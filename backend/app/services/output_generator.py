"""
输出内容生成服务
根据说者Persona与受众Persona生成 canonical/plan/final
"""
import json
from typing import Dict, Any, Optional
from loguru import logger

from app.utils.openai_client import get_openai_client


class OutputGenerator:
    """输出内容生成器"""

    def __init__(self):
        self.openai_client = get_openai_client()
        logger.info("✅ 输出内容生成服务初始化成功")

    async def generate_outputs(
        self,
        source_text: str,
        task_type: str,
        speaker_profile: Optional[Dict[str, Any]] = None,
        audience_profile: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None,
        locked_facts: Optional[list[str]] = None,
        style_config: Optional[Dict[str, Any]] = None,
        max_tokens: int = 1200
    ) -> Dict[str, str]:
        """生成 canonical/plan/final 三阶段输出"""
        prompt = self._build_prompt(
            source_text=source_text,
            task_type=task_type,
            speaker_profile=speaker_profile,
            audience_profile=audience_profile,
            constraints=constraints,
            locked_facts=locked_facts,
            style_config=style_config
        )

        messages = [
            {"role": "system", "content": "你是严谨的内容改写与适配引擎。"},
            {"role": "user", "content": prompt}
        ]

        logger.info("🤖 正在生成输出内容...")
        response = await self.openai_client.chat_completion(
            messages=messages,
            max_tokens=max_tokens
        )

        outputs = self._parse_json_response(response.get("content", ""))
        if outputs:
            return outputs

        # 兜底输出
        logger.warning("⚠️ JSON解析失败，使用兜底策略")
        return self._fallback_outputs(source_text)

    def _build_prompt(
        self,
        source_text: str,
        task_type: str,
        speaker_profile: Optional[Dict[str, Any]],
        audience_profile: Optional[Dict[str, Any]],
        constraints: Optional[Dict[str, Any]],
        locked_facts: Optional[list[str]],
        style_config: Optional[Dict[str, Any]]
    ) -> str:
        speaker_block = json.dumps(speaker_profile or {}, ensure_ascii=False, indent=2)
        audience_block = json.dumps(audience_profile or {}, ensure_ascii=False, indent=2)
        constraint_block = json.dumps(constraints or {}, ensure_ascii=False, indent=2)
        locked_block = json.dumps(locked_facts or [], ensure_ascii=False, indent=2)
        style_block = json.dumps(style_config or {}, ensure_ascii=False, indent=2)

        return f"""
你将基于给定文本，输出三阶段内容：canonical/plan/final。

【任务类型】{task_type}

【说者Persona】
{speaker_block}

【受众Persona】
{audience_block}

【表达约束】
{constraint_block}

【风格参数】
{style_block}

【锁定概念/事实（必须原样保留，不可改写/替换/删除）】
{locked_block}

【源文本】
{source_text}

要求：
1. canonical：提取事实/观点，不加入新信息
2. plan：给出结构化要点（条目）
3. final：在不引入新事实的前提下进行受众适配表达
4. 锁定概念/事实必须原样出现在 final 中
5. 输出JSON格式：
{{
  "canonical": "...",
  "plan": "...",
  "final": "..."
}}
6. 不要输出除JSON以外的任何内容。
"""

    def _parse_json_response(self, content: str) -> Optional[Dict[str, str]]:
        if not content:
            return None
        try:
            start = content.find("{")
            end = content.rfind("}")
            if start == -1 or end == -1 or end <= start:
                return None
            payload = content[start:end + 1]
            data = json.loads(payload)
            if not all(key in data for key in ("canonical", "plan", "final")):
                return None
            return {
                "canonical": str(data.get("canonical", "")),
                "plan": str(data.get("plan", "")),
                "final": str(data.get("final", ""))
            }
        except Exception:
            return None

    def _fallback_outputs(self, source_text: str) -> Dict[str, str]:
        preview = source_text.strip()
        if len(preview) > 600:
            preview = preview[:600] + "..."

        sentences = [s for s in preview.replace("\n", " ").split("。") if s.strip()]
        plan_lines = [f"- {s.strip()}" for s in sentences[:5]]
        plan = "\n".join(plan_lines) if plan_lines else "- 提炼要点"

        return {
            "canonical": preview,
            "plan": plan,
            "final": preview
        }


_generator: OutputGenerator | None = None


def get_output_generator() -> OutputGenerator:
    """获取输出内容生成器单例"""
    global _generator
    if _generator is None:
        _generator = OutputGenerator()
    return _generator
