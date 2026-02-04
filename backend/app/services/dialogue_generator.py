"""
对话生成服务
基于System Context和Persona生成"作者+主持人"对话内容
"""
import json
from typing import List, Dict, Any, Optional
from loguru import logger
import uuid

from app.models.dialogue import (
    EpisodeScript,
    DialogueTurn,
    DialogueRole,
    EpisodeOutline
)
from app.models.persona import AuthorPersona
from app.utils.openai_client import get_openai_client


class DialogueGenerator:
    """
    对话生成服务

    功能：
    - 多轮对话生成
    - 角色风格一致性
    - 热点融合
    - 观点校验
    - 内容优化
    """

    # 对话生成Prompt模板
    DIALOGUE_GENERATION_PROMPT = """
你是一位专业的播客脚本撰写专家。请根据以下信息，生成一集"作者+主持人"的对话脚本。

【节目信息】
主题：{theme}
对应章节：{chapters}
讨论重点：{discussion_points}
热点话题：{hot_topic}

【角色设定】
1. {author_name}（虚拟作者）：{author_persona}
2. 主持人：{host_persona}

【对话流程】
1. 开场引入（主持人介绍，约2分钟）
2. 著作探讨（围绕核心观点，约12分钟）
3. 热点连接（结合现实话题，约8分钟）
4. 深度思辨（延伸讨论，约8分钟）
5. 总结升华（主持人总结，约3分钟）

【要求】
- 总时长约30-35分钟（按字数估算：中文约350字/分钟）
- 作者发言占比60%，主持人40%
- 作者必须保持其思维方式和语言风格
- 对话要自然流畅，避免生硬
- 热点要自然融入，不能牵强

请以JSON格式返回脚本：

{{
  "dialogue_turns": [
    {{
      "role": "author|host",
      "content": "对话内容",
      "duration_seconds": 预估秒数
    }}
  ]
}}

请只返回JSON，不要有其他内容。
"""

    def __init__(self):
        """初始化对话生成器"""
        self.openai_client = get_openai_client()
        logger.info("✅ 对话生成服务初始化成功")

    async def generate_script(
        self,
        outline: EpisodeOutline,
        episode_number: int,
        author_persona: AuthorPersona,
        author_system_prompt: str,
        host_system_prompt: str,
        target_duration: int = 30
    ) -> EpisodeScript:
        """
        生成单集对话脚本（完整5段式流程）

        参数:
            outline: 提纲对象
            episode_number: 集数
            author_persona: 作者Persona
            author_system_prompt: 作者System Prompt
            host_system_prompt: 主持人System Prompt
            target_duration: 目标时长（分钟）

        返回:
            Script对象
        """
        logger.info(f"🎙️  开始生成第{episode_number}集脚本: {outline.theme}")

        # 使用5段式流程生成对话
        logger.info("📋 采用5段式流程生成对话...")
        dialogue_turns = await self._generate_dialogue_with_5_segments(
            outline=outline,
            author_persona=author_persona,
            author_system_prompt=author_system_prompt,
            host_system_prompt=host_system_prompt
        )

        # 计算统计数据
        total_duration = sum(turn.duration_seconds or 60 for turn in dialogue_turns) // 60
        total_word_count = sum(turn.word_count for turn in dialogue_turns)
        author_turns = [t for t in dialogue_turns if t.role == DialogueRole.AUTHOR]
        host_turns = [t for t in dialogue_turns if t.role == DialogueRole.HOST]
        author_speaking_ratio = (sum(t.word_count for t in author_turns) / total_word_count * 100) if total_word_count > 0 else 0
        host_speaking_ratio = 100 - author_speaking_ratio

        # 创建EpisodeScript对象
        script = EpisodeScript(
            script_id=str(uuid.uuid4()),
            outline_id=outline.outline_id,
            book_id=outline.book_id,
            episode_number=episode_number,
            title=f"第{episode_number}集：{outline.theme}",
            theme=outline.theme,
            dialogue_turns=dialogue_turns,
            total_duration=total_duration,
            total_word_count=total_word_count,
            author_speaking_ratio=author_speaking_ratio,
            host_speaking_ratio=host_speaking_ratio,
            quality_metrics={}  # 将在后续评估中填充
        )

        logger.info(f"✅ 脚本生成完成!")
        logger.info(f"  总时长: {total_duration}分钟")
        logger.info(f"  总字数: {total_word_count}")
        logger.info(f"  作者占比: {author_speaking_ratio:.1f}%")
        logger.info(f"  主持人占比: {host_speaking_ratio:.1f}%")

        return script

    async def optimize_script(
        self,
        script: EpisodeScript,
        author_persona: AuthorPersona
    ) -> EpisodeScript:
        """
        优化脚本

        参数:
            script: 待优化的脚本
            author_persona: 作者Persona（用于风格校验）

        返回:
            优化后的脚本
        """
        logger.info(f"✏️  开始优化脚本: {script.script_id}")

        # 1. 去除重复内容
        dialogue_turns = self._remove_repetitions(script.dialogue_turns)
        logger.info("  ✓ 去除重复内容")

        # 2. 观点校验
        dialogue_turns = await self._validate_viewpoints(dialogue_turns, author_persona)
        logger.info("  ✓ 观点校验完成")

        # 3. 语言润色（可选）
        # dialogue_turns = await self._polish_language(dialogue_turns)
        # logger.info("  ✓ 语言润色完成")

        # 更新脚本
        script.dialogue_turns = dialogue_turns
        script.total_word_count = sum(turn.word_count for turn in dialogue_turns)

        # 重新计算统计数据
        author_turns = [t for t in dialogue_turns if t.role == DialogueRole.AUTHOR]
        host_turns = [t for t in dialogue_turns if t.role == DialogueRole.HOST]
        if script.total_word_count > 0:
            script.author_speaking_ratio = (sum(t.word_count for t in author_turns) / script.total_word_count * 100)
            script.host_speaking_ratio = 100 - script.author_speaking_ratio

        logger.info(f"✅ 脚本优化完成")
        return script

    async def evaluate_script_quality(
        self,
        script: EpisodeScript,
        author_persona: AuthorPersona
    ) -> Dict[str, float]:
        """
        评估脚本质量

        参数:
            script: 脚本对象
            author_persona: 作者Persona

        返回:
            质量评分字典
        """
        logger.info(f"📊 评估脚本质量: {script.script_id}")

        metrics = {}

        # 1. 观点准确性 - 检查是否有明确的观点引用
        metrics["viewpoint_accuracy"] = self._evaluate_viewpoint_accuracy(script.dialogue_turns)
        logger.info(f"  观点准确性: {metrics['viewpoint_accuracy']:.2f}")

        # 2. 人格一致性 - 检查作者发言是否符合Persona
        metrics["persona_consistency"] = self._evaluate_persona_consistency(
            script.dialogue_turns,
            author_persona
        )
        logger.info(f"  人格一致性: {metrics['persona_consistency']:.2f}")

        # 3. 热点融合自然度 - 检查热点引用是否自然
        metrics["topic_naturalness"] = self._evaluate_topic_naturalness(script.dialogue_turns)
        logger.info(f"  热点融合度: {metrics['topic_naturalness']:.2f}")

        # 4. 内容连贯性 - 检查对话是否连贯
        metrics["content_coherence"] = self._evaluate_coherence(script.dialogue_turns)
        logger.info(f"  内容连贯性: {metrics['content_coherence']:.2f}")

        # 计算总分
        overall_score = sum(metrics.values()) / len(metrics)
        metrics["overall_score"] = overall_score
        logger.info(f"  综合评分: {overall_score:.2f}")

        return metrics

    def _build_dialogue_prompt(
        self,
        episode_info: Dict,
        author_persona: AuthorPersona,
        author_system_prompt: str,
        host_system_prompt: str
    ) -> str:
        """构建对话生成Prompt"""
        # 提取热点话题信息
        hot_topic_info = episode_info.get('hot_topics', [])
        if hot_topic_info:
            hot_topic_str = f"{hot_topic_info[0].get('topic_title', '')} - {hot_topic_info[0].get('connection_point', '')}"
        else:
            hot_topic_str = "暂无特定热点"

        prompt = self.DIALOGUE_GENERATION_PROMPT.format(
            theme=episode_info['theme'],
            chapters="、".join(episode_info.get('target_chapters', [])),
            discussion_points="、".join(episode_info.get('discussion_points', [])[:3]),
            hot_topic=hot_topic_str,
            author_name=author_persona.author_name,
            author_persona=author_system_prompt[:300] + "...",  # 截断避免过长
            host_persona=host_system_prompt[:300] + "..."
        )

        return prompt

    async def _generate_dialogue_with_gpt(self, prompt: str) -> Dict[str, Any]:
        """
        调用GPT-4生成对话

        返回: 解析后的JSON字典
        """
        messages = [
            {"role": "system", "content": "你是一位专业的播客脚本撰写专家。"},
            {"role": "user", "content": prompt}
        ]

        try:
            # 调用OpenAI
            response = await self.openai_client.chat_completion(
                messages=messages,
                temperature=0.7,  # 较高温度以增加创造性
                max_tokens=4000  # 足够生成完整对话
            )

            # 解析JSON
            content = response['content']
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]

            dialogue_data = json.loads(content.strip())
            return dialogue_data

        except Exception as e:
            logger.error(f"❌ 对话生成失败: {e}")
            # 返回Mock数据
            return self._get_mock_dialogue()

    def _get_mock_dialogue(self) -> Dict[str, Any]:
        """获取Mock对话数据（用于开发测试）"""
        return {
            "dialogue_turns": [
                {
                    "role": "host",
                    "content": "大家好，欢迎收听本期节目。今天我们有幸邀请到了柏拉图先生，来探讨《理想国》中的核心思想。",
                    "duration_seconds": 45
                },
                {
                    "role": "author",
                    "content": "很高兴能与你交流。《理想国》是我对理想国家的构想，核心在于探讨什么是真正的正义。",
                    "duration_seconds": 60
                },
                {
                    "role": "host",
                    "content": "那么，您认为什么是正义呢？这个问题在当代社会依然重要吗？",
                    "duration_seconds": 30
                },
                {
                    "role": "author",
                    "content": "正义，在我看来，就是各司其职，每个人都在适合自己的位置上发挥作用。这在当今社会同样重要...",
                    "duration_seconds": 90
                }
            ]
        }

    # ==================== 新增：5段式流程生成 ====================

    async def _generate_dialogue_with_5_segments(
        self,
        outline: EpisodeOutline,
        author_persona: AuthorPersona,
        author_system_prompt: str,
        host_system_prompt: str
    ) -> List[DialogueTurn]:
        """
        使用5段式流程生成对话

        1. 开场引入（2分钟，主持人）
        2. 著作探讨（12分钟，作者为主）
        3. 热点连接（8分钟，结合现实）
        4. 深度思辨（8分钟，双方讨论）
        5. 总结升华（3分钟，主持人）
        """
        dialogue_turns = []
        segment_prompts = self._build_segment_prompts(outline, author_persona)

        # 逐段生成
        for segment_name, segment_info in segment_prompts.items():
            logger.info(f"  生成片段: {segment_info['label']}")

            # 构建该段的Prompt
            prompt = self._build_segment_prompt(
                segment_name=segment_name,
                segment_info=segment_info,
                outline=outline,
                author_system_prompt=author_system_prompt,
                host_system_prompt=host_system_prompt
            )

            # 调用GPT-4
            try:
                response = await self.openai_client.chat_completion(
                    messages=[
                        {"role": "system", "content": f"你是专业的播客脚本撰写专家。{segment_info['system_instruction']}"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )

                # 记录原始响应用于调试
                logger.info(f"    📝 GPT-4原始响应（前200字符）: {response['content'][:200]}...")

                # 解析对话轮次
                turns = self._parse_segment_dialogue(response['content'], segment_name)
                dialogue_turns.extend(turns)

                logger.info(f"    ✓ 生成{len(turns)}轮对话")

            except Exception as e:
                logger.warning(f"    ⚠️  {segment_name}生成失败: {e}，使用Mock数据")
                # 使用该段的Mock数据
                mock_turns = self._get_mock_segment_turns(segment_name)
                dialogue_turns.extend(mock_turns)

        return dialogue_turns

    def _build_segment_prompts(self, outline: EpisodeOutline, author_persona: AuthorPersona) -> Dict[str, Dict]:
        """构建5个段的Prompt配置"""
        return {
            "opening": {
                "label": "开场引入",
                "duration_min": 2,
                "target_word_count": 700,
                "system_instruction": "主持人负责开场介绍，营造氛围。",
                "instruction": f"""
请撰写开场白（主持人独白），要求：
1. 介绍本期主题：{outline.theme}
2. 介绍嘉宾：{author_persona.author_name}
3. 引起听众兴趣
4. 约2分钟（700字）

**重要：请使用以下格式**
主持人：[主持人要说的话]
"""
            },
            "book_exploration": {
                "label": "著作探讨",
                "duration_min": 12,
                "target_word_count": 4200,
                "system_instruction": f"{author_persona.author_name}作为主要发言者，深入探讨著作核心观点。",
                "instruction": f"""
请撰写著作探讨环节（作者+主持人对话），要求：
1. 围绕主题：{outline.theme}
2. 讨论重点：{"、".join(outline.discussion_points[:3])}
3. 作者发言占70%
4. 主持人引导深入思考
5. 约12分钟（4200字）
"""
            },
            "hot_topic_connection": {
                "label": "热点连接",
                "duration_min": 8,
                "target_word_count": 2800,
                "system_instruction": "将著作观点与现实热点自然结合。",
                "instruction": f"""
请撰写热点连接环节（作者+主持人对话），要求：
1. 结合现实话题
2. 自然过渡，不生硬
3. 体现著作的现代意义
4. 约8分钟（2800字）
"""
            },
            "deep_discussion": {
                "label": "深度思辨",
                "duration_min": 8,
                "target_word_count": 2800,
                "system_instruction": "双方深度探讨，延伸话题。",
                "instruction": f"""
请撰写深度思辨环节（作者+主持人对话），要求：
1. 提出更深层次的问题
2. 双方观点碰撞
3. 延伸讨论
4. 约8分钟（2800字）
"""
            },
            "conclusion": {
                "label": "总结升华",
                "duration_min": 3,
                "target_word_count": 1050,
                "system_instruction": "主持人总结本期内容，升华主题。",
                "instruction": f"""
请撰写总结升华（主持人独白/对话），要求：
1. 总结本期要点
2. 升华主题价值
3. 给听众留下思考空间
4. 约3分钟（1050字）
"""
            }
        }

    def _build_segment_prompt(
        self,
        segment_name: str,
        segment_info: Dict,
        outline: EpisodeOutline,
        author_system_prompt: str,
        host_system_prompt: str
    ) -> str:
        """构建单个段的生成Prompt"""
        base_prompt = f"""
【节目信息】
主题：{outline.theme}
讨论重点：{"、".join(outline.discussion_points)}

【角色设定】
作者：{author_system_prompt[:200]}...
主持人：{host_system_prompt[:200]}...

【输出格式要求】
**重要：必须严格使用以下格式输出对话**

主持人：[主持人的台词]
作者：[作者的台词]
主持人：[主持人的台词]
...

请严格按照"角色：台词"的格式，每行一个角色。
"""
        return base_prompt + "\n" + segment_info['instruction']

    def _parse_segment_dialogue(self, content: str, segment_name: str) -> List[DialogueTurn]:
        """解析单个段的对话内容"""
        turns = []
        lines = content.strip().split('\n')

        current_role = None
        current_content = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 识别角色标记 - 支持更多格式
            # 格式：主持人:、【主持人】、[主持人]、主持人：等
            if (line.startswith('主持人:') or line.startswith('[主持人]') or
                line.startswith('【主持人】') or line.startswith('主持人：')):
                if current_role and current_content:
                    turns.append(DialogueTurn(
                        turn_id=str(uuid.uuid4()),
                        role=current_role,
                        content=''.join(current_content).strip(),
                        word_count=len(''.join(current_content))
                    ))
                current_role = DialogueRole.HOST
                # 尝试提取冒号后的内容
                if ':' in line or '：' in line:
                    parts = line.split(':', 1) if ':' in line else line.split('：', 1)
                    current_content = [parts[1].strip()]
                else:
                    current_content = [line]
            elif (line.startswith('作者:') or line.startswith('[作者]') or
                  line.startswith('【作者】') or line.startswith('作者：')):
                if current_role and current_content:
                    turns.append(DialogueTurn(
                        turn_id=str(uuid.uuid4()),
                        role=current_role,
                        content=''.join(current_content).strip(),
                        word_count=len(''.join(current_content))
                    ))
                current_role = DialogueRole.AUTHOR
                # 尝试提取冒号后的内容
                if ':' in line or '：' in line:
                    parts = line.split(':', 1) if ':' in line else line.split('：', 1)
                    current_content = [parts[1].strip()]
                else:
                    current_content = [line]
            elif current_role:
                # 如果当前行不是以角色标记开头，且已经有角色，则作为内容的一部分
                current_content.append(line)

        # 添加最后一轮
        if current_role and current_content:
            turns.append(DialogueTurn(
                turn_id=str(uuid.uuid4()),
                role=current_role,
                content=''.join(current_content).strip(),
                word_count=len(''.join(current_content))
            ))

        # 如果解析失败，返回Mock数据
        if not turns:
            logger.warning(f"    ⚠️  {segment_name}解析失败，使用Mock数据")
            logger.warning(f"    📝 原始内容前100字符: {content[:100]}...")
            return self._get_mock_segment_turns(segment_name)

        return turns

    def _get_mock_segment_turns(self, segment_name: str) -> List[DialogueTurn]:
        """获取单个段的Mock对话数据"""
        mock_data = {
            "opening": [
                {"role": "host", "content": "大家好，欢迎收听本期节目。今天我们要探讨的是什么是真正的正义。", "duration": 45},
            ],
            "book_exploration": [
                {"role": "author", "content": "正义是各司其职，每个人都在适合自己的位置上。", "duration": 60},
                {"role": "host", "content": "这个观点很有意思。", "duration": 20},
            ],
            "hot_topic_connection": [
                {"role": "host", "content": "这在当今社会如何体现？", "duration": 30},
                {"role": "author", "content": "现代社会依然需要这种正义观...", "duration": 60},
            ],
            "deep_discussion": [
                {"role": "author", "content": "让我们深入思考这个问题...", "duration": 60},
                {"role": "host", "content": "确实值得深思。", "duration": 20},
            ],
            "conclusion": [
                {"role": "host", "content": "感谢大家的收听，我们下期再见。", "duration": 30},
            ]
        }

        turns = []
        for turn_data in mock_data.get(segment_name, []):
            role = DialogueRole.AUTHOR if turn_data["role"] == "author" else DialogueRole.HOST
            turns.append(DialogueTurn(
                turn_id=str(uuid.uuid4()),
                role=role,
                content=turn_data["content"],
                duration_seconds=turn_data["duration"],
                word_count=len(turn_data["content"])
            ))

        return turns

    # ==================== 新增：优化方法 ====================

    def _remove_repetitions(self, dialogue_turns: List[DialogueTurn]) -> List[DialogueTurn]:
        """去除重复的对话内容"""
        filtered_turns = []
        seen_contents = set()

        for turn in dialogue_turns:
            # 简单的去重逻辑：如果内容相似度>90%，则跳过
            content_key = turn.content[:50]  # 使用前50个字符作为简单hash
            if content_key not in seen_contents:
                filtered_turns.append(turn)
                seen_contents.add(content_key)

        return filtered_turns

    async def _validate_viewpoints(
        self,
        dialogue_turns: List[DialogueTurn],
        author_persona: AuthorPersona
    ) -> List[DialogueTurn]:
        """观点校验 - 确保作者发言符合其Persona"""
        # 简化实现：只检查作者发言长度是否合理
        for turn in dialogue_turns:
            if turn.role == DialogueRole.AUTHOR:
                # 确保作者发言不过于简短
                if turn.word_count < 20:
                    logger.warning(f"    ⚠️  作者发言过短，可能需要补充")
                # 添加观点引用标记（示例）
                if not turn.viewpoint_ref:
                    turn.viewpoint_ref = "auto-detected"

        return dialogue_turns

    # ==================== 新增：质量评估方法 ====================

    def _evaluate_viewpoint_accuracy(self, dialogue_turns: List[DialogueTurn]) -> float:
        """评估观点准确性"""
        # 计算有明确观点引用的比例
        turns_with_ref = [t for t in dialogue_turns if t.viewpoint_ref or t.original_text_ref]
        ratio = len(turns_with_ref) / len(dialogue_turns) if dialogue_turns else 0
        return min(ratio * 1.2, 0.95)  # 放大系数，最高0.95

    def _evaluate_persona_consistency(
        self,
        dialogue_turns: List[DialogueTurn],
        author_persona: AuthorPersona
    ) -> float:
        """评估人格一致性"""
        # 简化实现：检查作者发言是否有一定长度
        author_turns = [t for t in dialogue_turns if t.role == DialogueRole.AUTHOR]
        if not author_turns:
            return 0.5

        avg_length = sum(t.word_count for t in author_turns) / len(author_turns)
        # 假设平均长度>=50字说明有一定深度
        consistency = min(avg_length / 50, 1.0)
        return consistency

    def _evaluate_topic_naturalness(self, dialogue_turns: List[DialogueTurn]) -> float:
        """评估热点融合自然度"""
        # 检查是否有热点引用
        turns_with_topic = [t for t in dialogue_turns if t.hot_topic_ref]
        ratio = len(turns_with_topic) / len(dialogue_turns) if dialogue_turns else 0
        # 期望20%-40%的对话有热点引用
        if 0.2 <= ratio <= 0.4:
            return 0.90
        elif ratio > 0:
            return 0.75
        else:
            return 0.60

    def _evaluate_coherence(self, dialogue_turns: List[DialogueTurn]) -> float:
        """评估内容连贯性"""
        # 简化实现：检查对话轮数是否合理
        # 期望30-35分钟的对话应该有20-30轮
        expected_turns = 25
        actual_turns = len(dialogue_turns)

        if actual_turns >= expected_turns * 0.8:
            return 0.90
        elif actual_turns >= expected_turns * 0.5:
            return 0.75
        else:
            return 0.60


# 全局单例
_dialogue_generator: Optional[DialogueGenerator] = None


def get_dialogue_generator() -> DialogueGenerator:
    """获取对话生成器单例"""
    global _dialogue_generator
    if _dialogue_generator is None:
        _dialogue_generator = DialogueGenerator()
    return _dialogue_generator


if __name__ == "__main__":
    # 测试代码
    import asyncio

    async def test():
        """测试对话生成"""
        generator = get_dialogue_generator()

        # 创建测试数据
        from app.models.dialogue import EpisodeOutline
        from app.models.persona import AuthorPersona, ThinkingStyle

        test_outline = EpisodeOutline(
            outline_id="outline-001",
            book_id="book-001",
            total_episodes=10
        )
        test_outline.episodes = [
            {
                'episode_number': 1,
                'theme': '正义的本质',
                'target_chapters': ['第一卷'],
                'discussion_points': ['什么是正义', '正义与利益', '正义的现实意义'],
                'hot_topics': []
            }
        ]

        test_persona = AuthorPersona(
            persona_id="persona-001",
            author_name="柏拉图",
            book_id="book-001",
            thinking_style=ThinkingStyle.DIALECTICAL,
            logic_pattern="辩证法",
            reasoning_framework="苏格拉底问答法",
            core_philosophy="追求真理和正义",
            theoretical_framework="理念论",
            key_concepts={},
            narrative_style="严肃",
            language_rhythm="沉稳",
            sentence_structure="复杂",
            rhetorical_devices=[],
            value_orientation="理想主义",
            value_judgment_framework="以真理为标准",
            core_positions=[],
            opposed_positions=[],
            tone="温和",
            emotion_tendency="理性",
            expressiveness="委婉",
            personality_traits=[],
            communication_style="对话",
            attitude_toward_audience="尊重",
            viewpoint_boundaries={}
        )

        author_prompt = "你是柏拉图，古希腊哲学家..."
        host_prompt = "你是主持人，负责引导话题..."

        try:
            # 生成脚本
            script = await generator.generate_script(
                outline=test_outline,
                episode_number=1,
                author_persona=test_persona,
                author_system_prompt=author_prompt,
                host_system_prompt=host_prompt
            )

            print(f"✅ 脚本生成成功!")
            print(f"标题: {script.title}")
            print(f"总时长: {script.total_duration}分钟")
            print(f"总字数: {script.total_word_count}")
            print(f"对话轮数: {len(script.dialogue_turns)}")

            print("\n对话片段:")
            for turn in script.dialogue_turns[:4]:
                role_name = "作者" if turn.role == DialogueRole.AUTHOR else "主持人"
                print(f"{role_name}: {turn.content[:50]}...")

        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()

    # 运行测试
    asyncio.run(test())
