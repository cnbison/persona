"""
OpenAI客户端封装
提供统一的GPT-4调用接口，包含重试机制、流式响应、成本统计
"""
import asyncio
import time
from typing import Optional, Dict, Any, AsyncIterator
import httpx
from enum import Enum
from loguru import logger
import json

try:
    from openai import AsyncOpenAI, OpenAI
    from openai import Stream
    from openai.types import Completion
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("⚠️  OpenAI包未安装，将使用mock模式")

from app.utils.config import settings


class ModelType(str, Enum):
    """支持的模型类型"""
    GPT4_TURBO = "gpt-4-turbo-preview"
    GPT4 = "gpt-4"
    GPT35_TURBO = "gpt-3.5-turbo"


class OpenAIClient:
    """
    OpenAI客户端封装类

    功能：
    - 统一的调用接口
    - 自动重试机制（指数退避）
    - 流式响应支持
    - Token使用统计
    - 成本计算
    """

    # 模型定价（美元/1K tokens）- 2025年价格
    PRICING = {
        "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    }

    def __init__(self):
        """初始化客户端"""
        self.client = None
        self.async_client = None
        self.mock_mode = True
        self.active_provider_id = None
        self.active_provider = None
        self._init_from_provider()

    async def chat_completion(
        self,
        messages: list,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        聊天补全API（异步）

        参数:
            messages: 对话消息列表
                [{"role": "user", "content": "..."}, ...]
            model: 模型名称（默认使用配置的模型）
            temperature: 温度参数（0-1）
            max_tokens: 最大token数
            stream: 是否流式返回
            max_retries: 最大重试次数

        返回:
            {
                "content": "响应内容",
                "usage": {"prompt_tokens": 10, "completion_tokens": 20},
                "model": "gpt-4-turbo-preview",
                "cost": 0.0007
            }
        """
        self._init_from_provider()

        if self.mock_mode:
            return self._mock_response(messages)

        provider_type = (self.active_provider or {}).get("provider_type", "openai")
        model = model or (self.active_provider or {}).get("model") or settings.openai_model
        temperature = temperature or settings.openai_temperature

        for attempt in range(max_retries):
            try:
                logger.debug(f"🔄 调用OpenAI API (尝试 {attempt + 1}/{max_retries})")

                if provider_type in ("openai", "deepseek", "qwen", "ollama", "custom"):
                    response = await self.async_client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=stream
                    )

                    if stream:
                        content = ""
                        async for chunk in response:
                            if chunk.choices[0].delta.content:
                                content += chunk.choices[0].delta.content
                        completion_text = content
                        usage = None
                    else:
                        completion_text = response.choices[0].message.content
                        usage = response.usage
                elif provider_type == "azure":
                    completion_text, usage = await self._call_azure_chat(
                        messages=messages,
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                elif provider_type == "anthropic":
                    completion_text, usage = await self._call_anthropic(
                        messages=messages,
                        model=model,
                        max_tokens=max_tokens
                    )
                else:
                    raise RuntimeError(f"不支持的模型提供方: {provider_type}")

                # 计算成本
                cost = self._calculate_cost(model, usage) if usage else 0.0

                # 记录使用情况
                if usage:
                    logger.info(
                        f"✅ OpenAI调用成功 | "
                        f"输入: {usage.prompt_tokens} tokens | "
                        f"输出: {usage.completion_tokens} tokens | "
                        f"成本: ${cost:.4f}"
                    )

                return {
                    "content": completion_text,
                    "usage": {
                        "prompt_tokens": usage.prompt_tokens if usage else 0,
                        "completion_tokens": usage.completion_tokens if usage else 0,
                        "total_tokens": usage.total_tokens if usage else 0
                    } if usage else None,
                    "model": model,
                    "cost": cost
                }

            except Exception as e:
                logger.error(f"❌ OpenAI API调用失败 (尝试 {attempt + 1}/{max_retries}): {e}")

                if attempt == max_retries - 1:
                    # 最后一次尝试失败，抛出异常
                    raise

                # 指数退避
                wait_time = 2 ** attempt
                logger.info(f"⏳ 等待 {wait_time} 秒后重试...")
                await asyncio.sleep(wait_time)

    def chat_completion_sync(
        self,
        messages: list,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        聊天补全API（同步版本）

        参数和返回值与异步版本相同
        """
        self._init_from_provider()

        if self.mock_mode:
            return self._mock_response(messages)

        provider_type = (self.active_provider or {}).get("provider_type", "openai")
        model = model or (self.active_provider or {}).get("model") or settings.openai_model
        temperature = temperature or settings.openai_temperature

        for attempt in range(max_retries):
            try:
                logger.debug(f"🔄 调用OpenAI API (尝试 {attempt + 1}/{max_retries})")

                if provider_type in ("openai", "deepseek", "qwen", "ollama", "custom"):
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )

                    completion_text = response.choices[0].message.content
                    usage = response.usage
                elif provider_type == "azure":
                    completion_text, usage = asyncio.run(
                        self._call_azure_chat(messages, model, temperature, max_tokens)
                    )
                elif provider_type == "anthropic":
                    completion_text, usage = asyncio.run(
                        self._call_anthropic(messages, model, max_tokens)
                    )
                else:
                    raise RuntimeError(f"不支持的模型提供方: {provider_type}")

                cost = self._calculate_cost(model, usage) if usage else 0.0

                logger.info(
                    f"✅ OpenAI调用成功 | "
                    f"输入: {usage.prompt_tokens} tokens | "
                    f"输出: {usage.completion_tokens} tokens | "
                    f"成本: ${cost:.4f}"
                )

                return {
                    "content": completion_text,
                    "usage": {
                        "prompt_tokens": usage.prompt_tokens if usage else 0,
                        "completion_tokens": usage.completion_tokens if usage else 0,
                        "total_tokens": usage.total_tokens if usage else 0
                    } if usage else None,
                    "model": model,
                    "cost": cost
                }

            except Exception as e:
                logger.error(f"❌ OpenAI API调用失败 (尝试 {attempt + 1}/{max_retries}): {e}")

                if attempt == max_retries - 1:
                    raise

                wait_time = 2 ** attempt
                logger.info(f"⏳ 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)

    def _calculate_cost(self, model: str, usage) -> float:
        """计算API调用成本"""
        if not usage:
            return 0.0

        pricing = self.PRICING.get(model, {"input": 0.01, "output": 0.03})
        input_cost = (usage.prompt_tokens / 1000) * pricing["input"]
        output_cost = (usage.completion_tokens / 1000) * pricing["output"]

        return input_cost + output_cost

    def _init_from_provider(self):
        if not OPENAI_AVAILABLE:
            self.mock_mode = True
            return

        provider = self._load_active_provider()
        if not provider:
            if settings.openai_api_key == "sk-test-key":
                self.mock_mode = True
                return
            provider = {
                "provider_id": None,
                "provider_type": "openai",
                "api_key": settings.openai_api_key,
                "base_url": settings.openai_api_base,
                "model": settings.openai_model,
            }

        if provider.get("provider_id") == self.active_provider_id:
            return

        self.active_provider_id = provider.get("provider_id")
        self.active_provider = provider

        api_key = provider.get("api_key") or ""
        base_url = provider.get("base_url") or settings.openai_api_base

        if not api_key or api_key == "sk-test-key":
            self.mock_mode = True
            self.client = None
            self.async_client = None
            return

        try:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            self.async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)
            self.mock_mode = False
            logger.info(f"✅ 模型提供方加载成功: {provider.get('name', provider.get('provider_type'))}")
        except Exception as e:
            logger.error(f"❌ 模型提供方初始化失败: {e}")
            self.mock_mode = True
            self.client = None
            self.async_client = None

    def _load_active_provider(self) -> Optional[Dict[str, Any]]:
        try:
            from app.database import SessionLocal
            from app.models.orm import ModelProviderORM

            db = SessionLocal()
            provider = db.query(ModelProviderORM).filter(ModelProviderORM.is_active == 1).first()
            db.close()

            if not provider:
                return None

            return {
                "provider_id": provider.provider_id,
                "name": provider.name,
                "provider_type": provider.provider_type,
                "base_url": provider.base_url,
                "api_key": provider.api_key,
                "api_version": provider.api_version,
                "model": provider.model,
                "extra_headers": provider.extra_headers or {}
            }
        except Exception as e:
            logger.error(f"❌ 加载模型提供方失败: {e}")
            return None

    async def _call_azure_chat(self, messages, model, temperature, max_tokens):
        provider = self.active_provider or {}
        base_url = provider.get("base_url") or ""
        api_key = provider.get("api_key") or ""
        api_version = provider.get("api_version") or "2024-02-15-preview"

        if not base_url or not api_key:
            raise RuntimeError("Azure配置缺失 base_url 或 api_key")

        url = f"{base_url}/openai/deployments/{model}/chat/completions?api-version={api_version}"
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        headers = {"api-key": api_key, "Content-Type": "application/json"}
        headers.update(provider.get("extra_headers", {}))

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        completion_text = data["choices"][0]["message"]["content"]
        usage = data.get("usage")
        return completion_text, usage

    async def _call_anthropic(self, messages, model, max_tokens):
        provider = self.active_provider or {}
        base_url = provider.get("base_url") or "https://api.anthropic.com"
        api_key = provider.get("api_key") or ""
        api_version = provider.get("api_version") or "2023-06-01"

        if not api_key:
            raise RuntimeError("Anthropic配置缺失 api_key")

        system_parts = [m["content"] for m in messages if m["role"] == "system"]
        user_messages = [m for m in messages if m["role"] != "system"]
        if system_parts and user_messages:
            user_messages[0]["content"] = "System: " + " ".join(system_parts) + "\n" + user_messages[0]["content"]

        url = f"{base_url}/v1/messages"
        payload = {
            "model": model,
            "max_tokens": max_tokens or 1024,
            "messages": user_messages
        }
        headers = {
            "x-api-key": api_key,
            "anthropic-version": api_version,
            "content-type": "application/json"
        }
        headers.update(provider.get("extra_headers", {}))

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        content_blocks = data.get("content", [])
        completion_text = content_blocks[0].get("text", "") if content_blocks else ""
        usage = data.get("usage")
        return completion_text, usage

    def _mock_response(self, messages: list) -> Dict[str, Any]:
        """
        Mock响应（用于开发测试）
        """
        last_message = messages[-1]["content"] if messages else ""

        mock_content = f"[Mock响应] 这是一个模拟的OpenAI响应。\n\n你的输入是：{last_message[:100]}...\n\n配置真实API密钥后即可调用实际API。"

        return {
            "content": mock_content,
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            },
            "model": settings.openai_model,
            "cost": 0.0
        }


# 全局单例
_openai_client: Optional[OpenAIClient] = None


def get_openai_client() -> OpenAIClient:
    """
    获取OpenAI客户端单例

    使用方式:
        client = get_openai_client()
        response = await client.chat_completion(messages)
    """
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient()
    return _openai_client


# 便捷函数
async def call_openai(
    messages: list,
    model: Optional[str] = None,
    temperature: Optional[float] = None
) -> str:
    """
    便捷的OpenAI调用函数（只返回内容）

    使用方式:
        response = await call_openai([{"role": "user", "content": "你好"}])
    """
    client = get_openai_client()
    result = await client.chat_completion(
        messages=messages,
        model=model,
        temperature=temperature
    )
    return result["content"]


if __name__ == "__main__":
    # 测试代码
    import asyncio

    async def test():
        """测试OpenAI客户端"""
        client = get_openai_client()

        messages = [
            {"role": "system", "content": "你是一个有帮助的助手。"},
            {"role": "user", "content": "请简单介绍一下Python编程语言。"}
        ]

        try:
            response = await client.chat_completion(messages)
            print("响应内容:")
            print(response["content"])
            print(f"\n使用情况: {response['usage']}")
            print(f"成本: ${response['cost']:.4f}")
        except Exception as e:
            print(f"错误: {e}")

    # 运行测试
    asyncio.run(test())
