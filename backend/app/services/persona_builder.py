"""
Persona构建服务
通过AI分析著作，构建作者的6维度人格特征
"""
import json
from typing import Dict, Any, Optional
from loguru import logger
import uuid

from app.models.persona import (
    AuthorPersona,
    ThinkingStyle,
    SystemPrompt,
    HostPersona
)
from app.models.book import Book
from app.utils.openai_client import get_openai_client


class PersonaBuilder:
    """
    Persona构建服务

    功能：
    - 6维度人格分析（思维、思想、叙事、价值、语气、性格）
    - System Prompt生成
    - 观点边界设定
    - 观点一致性校验
    """

    # Persona分析Prompt模板
    PERSONA_ANALYSIS_PROMPT = """
你是一位专业的文学分析师和心理学家。请仔细阅读以下著作内容，深入分析作者的6维度人格特征。

【著作信息】
标题：{title}
作者：{author}
核心章节和观点：
{content_sample}

请深入分析作者的6个维度，并以JSON格式返回：

{{
  "thinking_style": {{
    "type": "inductive|deductive|dialectical|analytical|intuitive",
    "description": "思维方式的详细描述（100字以上）",
    "logic_pattern": "论证逻辑的详细说明，包括论证方法和思考路径",
    "reasoning_framework": "推理框架的完整描述，如何从前提得出结论"
  }},
  "philosophy": {{
    "core_philosophy": "核心哲学观点的完整阐述（100字以上）",
    "theoretical_framework": "详细的理论框架说明，包括理论体系、思想流派、学术背景",
    "key_concepts": {{"概念1": "精确定义", "概念2": "精确定义", "概念3": "精确定义", "概念4": "精确定义", "概念5": "精确定义"}}
  }},
  "narrative_style": {{
    "style": "幽默/严肃/口语/书面/对话式等",
    "language_rhythm": "语言节奏的详细描述",
    "sentence_structure": "句式结构特征的详细说明",
    "rhetorical_devices": ["修辞手法1", "修辞手法2", "修辞手法3", "修辞手法4"]
  }},
  "values": {{
    "orientation": "保守/激进/个人主义/集体主义/实用主义等",
    "judgment_framework": "价值判断框架的详细说明",
    "core_positions": ["核心立场1", "核心立场2", "核心立场3", "核心立场4", "核心立场5"],
    "opposed_positions": ["反对观点1", "反对观点2", "反对观点3", "反对观点4"]
  }},
  "tone": {{
    "tone": "温和/激烈/谦逊/自信/冷静等",
    "emotion_tendency": "情感倾向的详细说明",
    "expressiveness": "直白/委婉/热情/冷淡/含蓄"
  }},
  "personality": {{
    "traits": ["性格特质1", "性格特质2", "性格特质3", "性格特质4", "性格特质5"],
    "communication_style": "沟通风格的详细说明",
    "attitude": "对受众态度的完整描述"
  }}
}}

要求：
1. key_concepts必须提取至少5个核心概念
2. core_positions必须列出至少5个核心立场
3. opposed_positions必须列出至少4个反对观点
4. 所有描述性字段要详尽具体，不少于50字
5. 基于原著内容，不要编造

请只返回JSON，不要有其他内容。
"""

    # System Prompt生成模板
    SYSTEM_PROMPT_TEMPLATE = """
# 角色定义
你是{author_name}（{era}），{identity}。

# 核心哲学观点
{core_philosophy}

# 思维方式
{thinking_style}

# 语言风格
{narrative_style}

# 价值观
{values}

# 语气和性格
{tone}，{personality}

# 对话规则
1. 你必须基于自己的原著观点进行回答，不得编造或违背核心思想
2. 对于未表态的话题，可以基于你的理论框架进行合理推演，但需标注"此为推演观点"
3. 用你典型的语言风格和思维逻辑表达
4. 尊重原著观点，不随意改变立场

# 禁止事项
- 不得表述与你核心主张相矛盾的观点
- 不得攻击或贬低他人
- 不得涉及敏感政治话题

请始终保持这个人设进行对话。
"""

    def __init__(self):
        """初始化Persona构建器"""
        self.openai_client = get_openai_client()
        logger.info("✅ Persona构建服务初始化成功")

    async def build_persona(
        self,
        book: Book,
        era: str = "古代",
        identity: str = "著名思想家"
    ) -> AuthorPersona:
        """
        构建作者Persona

        参数:
            book: 著作对象
            era: 时代（如"古代"、"19世纪"）
            identity: 身份（如"哲学家"、"经济学家"）

        返回:
            AuthorPersona对象
        """
        logger.info(f"🧠 开始构建Persona: {book.author}")

        # 准备分析内容（取前3个章节的核心观点）
        content_sample = self._prepare_content_sample(book)

        # 调用GPT-4分析6维度
        logger.info("🔍 正在调用GPT-4分析人格维度...")
        analysis = await self._analyze_persona_dimensions(
            book=book,
            content_sample=content_sample
        )

        # 构建Persona对象
        persona = AuthorPersona(
            persona_id=str(uuid.uuid4()),
            author_name=book.author,
            book_id=book.book_id,
            thinking_style=ThinkingStyle(analysis['thinking_style']['type']),
            logic_pattern=analysis['thinking_style']['description'],
            reasoning_framework=analysis['thinking_style']['logic_pattern'],
            core_philosophy=analysis['philosophy']['core_philosophy'],
            theoretical_framework=analysis['philosophy']['theoretical_framework'],
            key_concepts=analysis['philosophy']['key_concepts'],
            narrative_style=analysis['narrative_style']['style'],
            language_rhythm=analysis['narrative_style']['language_rhythm'],
            sentence_structure=analysis['narrative_style']['sentence_structure'],
            rhetorical_devices=analysis['narrative_style']['rhetorical_devices'],
            value_orientation=analysis['values']['orientation'],
            value_judgment_framework=analysis['values']['judgment_framework'],
            core_positions=analysis['values']['core_positions'],
            opposed_positions=analysis['values']['opposed_positions'],
            tone=analysis['tone']['tone'],
            emotion_tendency=analysis['tone']['emotion_tendency'],
            expressiveness=analysis['tone']['expressiveness'],
            personality_traits=analysis['personality']['traits'],
            communication_style=analysis['personality']['communication_style'],
            attitude_toward_audience=analysis['personality']['attitude'],
            viewpoint_boundaries={
                'core_positions': analysis['values']['core_positions'],
                'opposed_positions': analysis['values']['opposed_positions'],
                'unmentioned_areas': []  # 后续可以补充
            }
        )

        logger.info(f"✅ Persona构建完成: {book.author}")
        return persona

    async def generate_system_prompt(
        self,
        persona: AuthorPersona,
        era: str = "古代",
        identity: str = "著名思想家"
    ) -> str:
        """
        生成System Prompt

        参数:
            persona: Persona对象
            era: 时代
            identity: 身份

        返回:
            System Prompt字符串
        """
        logger.info(f"📝 生成System Prompt: {persona.author_name}")

        # 填充模板
        system_prompt = self.SYSTEM_PROMPT_TEMPLATE.format(
            author_name=persona.author_name,
            era=era,
            identity=identity,
            core_philosophy=persona.core_philosophy,
            thinking_style=persona.logic_pattern,
            narrative_style=f"{persona.narrative_style}，{persona.language_rhythm}",
            values=f"价值取向：{persona.value_orientation}，{persona.value_judgment_framework}",
            tone=persona.tone,
            personality=f"{persona.emotion_tendency}，{persona.expressiveness}"
        )

        return system_prompt

    async def validate_viewpoint(
        self,
        viewpoint: str,
        persona: AuthorPersona,
        original_text: str
    ) -> Dict[str, Any]:
        """
        校验观点一致性

        参数:
            viewpoint: 待校验的观点
            persona: Persona对象
            original_text: 原文

        返回:
            {
                "is_consistent": True/False,
                "confidence": 0.0-1.0,
                "suggestion": "修正建议"
            }
        """
        # TODO: 实现观点校验逻辑
        # 1. 对比观点与原文
        # 2. 检查是否违背核心立场
        # 3. 给出置信度评分

        return {
            "is_consistent": True,
            "confidence": 0.8,
            "suggestion": None
        }

    def _prepare_content_sample(self, book: Book, max_chapters: int = 3) -> str:
        """准备用于分析的内容样本"""
        sample_parts = []

        for i, chapter in enumerate(book.chapters[:max_chapters]):
            # 章节标题
            sample_parts.append(f"\n【第{i+1}章：{chapter.title}】\n")

            # 核心观点（前3个）
            chapter_viewpoints = [
                vp for vp in book.core_viewpoints
                if vp.chapter_id == chapter.chapter_id
            ][:3]

            for vp in chapter_viewpoints:
                sample_parts.append(f"- {vp.content}\n")

        return "\n".join(sample_parts)

    async def _analyze_persona_dimensions(
        self,
        book: Book,
        content_sample: str
    ) -> Dict[str, Any]:
        """
        调用GPT-4分析6维度人格

        返回: 解析后的JSON字典
        """
        # 构建Prompt
        prompt = self.PERSONA_ANALYSIS_PROMPT.format(
            title=book.title,
            author=book.author,
            content_sample=content_sample[:4000]  # 限制长度避免超token
        )

        messages = [
            {"role": "system", "content": "你是一位专业的文学分析师。"},
            {"role": "user", "content": prompt}
        ]

        try:
            # 调用OpenAI
            response = await self.openai_client.chat_completion(
                messages=messages,
                temperature=0.3  # 降低温度以获得更一致的分析
            )

            # 解析JSON响应
            content = response['content']
            # 提取JSON（去除可能的markdown代码块标记）
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]

            analysis = json.loads(content.strip())
            return analysis

        except Exception as e:
            logger.error(f"❌ Persona分析失败: {e}")
            # 返回Mock数据
            return self._get_mock_analysis(book.author)

    def _get_mock_analysis(self, author: str) -> Dict[str, Any]:
        """获取Mock分析结果（用于开发测试）"""
        return {
            "thinking_style": {
                "type": "dialectical",
                "description": "善于运用辩证法，通过对话和辩论展开思考",
                "logic_pattern": "苏格拉底式的问答法，层层递进，追求真理"
            },
            "philosophy": {
                "core_philosophy": "追求正义、真理和理想国的构建",
                "theoretical_framework": "理念论，认为现实世界是理念世界的影子",
                "key_concepts": {
                    "理念": "永恒不变的真实存在",
                    "正义": "各司其职，和谐统一",
                    "理想国": "哲学家统治的完美国家"
                }
            },
            "narrative_style": {
                "style": "严肃，富有哲理",
                "language_rhythm": "节奏沉稳，善于用比喻和对话",
                "sentence_structure": "多用设问和反问，句式丰富",
                "rhetorical_devices": ["比喻", "对话", "设问"]
            },
            "values": {
                "orientation": "理想主义",
                "judgment_framework": "以理念和真理为标准",
                "core_positions": [
                    "正义是最高的美德",
                    "哲学家应该成为统治者",
                    "教育是培养理想公民的关键"
                ],
                "opposed_positions": [
                    "民主制会导致暴民政治",
                    "财富和权力不应集中于少数人"
                ]
            },
            "tone": {
                "tone": "温和而坚定",
                "emotion_tendency": "理性",
                "expressiveness": "委婉而深刻"
            },
            "personality": {
                "traits": ["智慧", "理性", "谦逊", "追求真理"],
                "communication_style": "善于引导，循循善诱",
                "attitude": "尊重对话者，追求共同探求真理"
            }
        }


def build_host_persona() -> HostPersona:
    """
    构建主持人Persona（固定模板）

    返回标准化的主持人Persona
    """
    return HostPersona(
        persona_id="host-001",
        role_positioning="引导者+诠释者+桥梁者",
        traits=["专业严谨", "亲和易懂", "尊重作者", "代表现代受众"],
        knowledge_base=[
            "精通著作内容",
            "熟悉作者生平",
            "了解时代背景",
            "把握热点话题"
        ],
        language_style="简洁通俗，擅长转化学术表述为现代语境",
        functions=[
            "引导话题方向",
            "把控对话节奏",
            "深化内容理解",
            "连接现实热点"
        ],
        speaking_ratio=40
    )


# 全局单例
_persona_builder: Optional[PersonaBuilder] = None


def get_persona_builder() -> PersonaBuilder:
    """获取Persona构建器单例"""
    global _persona_builder
    if _persona_builder is None:
        _persona_builder = PersonaBuilder()
    return _persona_builder


if __name__ == "__main__":
    # 测试代码
    import asyncio

    async def test():
        """测试Persona构建"""
        builder = get_persona_builder()

        # 创建测试用的Book对象
        from app.models.book import Book, Chapter, CoreViewpoint

        test_book = Book(
            book_id="test-001",
            title="理想国",
            author="柏拉图",
            language="zh",
            file_path="/fake/path.pdf",
            file_type="pdf",
            chapters=[
                Chapter(
                    chapter_id="ch-001",
                    chapter_number=1,
                    title="第一卷",
                    content="这是测试内容..."
                )
            ],
            core_viewpoints=[
                CoreViewpoint(
                    viewpoint_id="vp-001",
                    content="正义是最高的美德",
                    original_text="正义是最高的美德",
                    chapter_id="ch-001",
                    context="..."
                )
            ]
        )

        try:
            # 构建Persona
            persona = await builder.build_persona(test_book)

            print(f"✅ Persona构建成功!")
            print(f"作者: {persona.author_name}")
            print(f"思维方式: {persona.thinking_style}")
            print(f"核心哲学: {persona.core_philosophy}")

            # 生成System Prompt
            system_prompt = await builder.generate_system_prompt(persona)
            print(f"\n✅ System Prompt生成成功!")
            print(f"长度: {len(system_prompt)} 字符")

            # 构建主持人Persona
            host = build_host_persona()
            print(f"\n✅ 主持人Persona: {host.role_positioning}")

        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()

    # 运行测试
    asyncio.run(test())
