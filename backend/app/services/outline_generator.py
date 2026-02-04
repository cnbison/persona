"""
提纲生成服务
基于著作和Persona生成10集节目提纲
"""
import json
from typing import List, Dict, Any, Optional
from loguru import logger
import uuid

from app.models.persona import AuthorPersona
from app.models.book import Book
from app.models.dialogue import EpisodeOutline, HotTopicMatch, BookSeries
from app.utils.openai_client import get_openai_client


class OutlineGenerator:
    """
    提纲生成服务

    功能：
    - 分析著作结构
    - 生成10集提纲
    - 每集分配章节
    - 匹配热点话题
    - 定义讨论重点
    """

    # 提纲生成Prompt模板
    OUTLINE_GENERATION_PROMPT = """
你是一位经验丰富的播客制作人。请基于以下著作信息，设计一个10集的深度对话节目提纲。

【著作信息】
标题：{title}
作者：{author}
总章节数：{total_chapters}
核心主题：{main_themes}

【章节概览】
{chapters_overview}

【核心观点示例】
{viewpoints_sample}

请设计10集节目，要求：
1. 每集聚焦特定主题/章节，主题明确且有吸引力
2. 10集内容覆盖著作核心内容90%以上，避免遗漏重要章节
3. 逻辑递进，由浅入深：从背景介绍 → 核心概念 → 深度探讨 → 现代意义
4. 每集包含明确的讨论重点，至少5个
5. 每集主题要能让听众产生共鸣和好奇

请以JSON格式返回：

{{
  "episodes": [
    {{
      "episode_number": 1,
      "theme": "本集主题（20字以内，吸引人）",
      "target_chapters": ["章节1", "章节2"],
      "discussion_points": [
        "具体讨论点1（明确要探讨的问题）",
        "具体讨论点2",
        "具体讨论点3",
        "具体讨论点4",
        "具体讨论点5"
      ]
    }}
  ]
}}

要求：
- target_chapters必须基于实际章节标题
- discussion_points至少5个，要具体、深入、可讨论
- 主题要通俗易懂，适合大众听众
- 10集之间要有逻辑递进关系

请只返回JSON，不要有其他内容。
"""

    def __init__(self):
        """初始化提纲生成器"""
        self.openai_client = get_openai_client()
        logger.info("✅ 提纲生成服务初始化成功")

    async def generate_outline(
        self,
        book: Book,
        persona: AuthorPersona,
        episodes_count: int = 10
    ) -> BookSeries:
        """
        生成10集提纲

        参数:
            book: 著作对象
            persona: 作者Persona
            episodes_count: 集数（默认10）

        返回:
            BookSeries对象（包含10集EpisodeOutline）
        """
        logger.info(f"📝 开始生成提纲: {book.title} ({episodes_count}集)")

        # 准备输入数据
        chapters_overview = self._prepare_chapters_overview(book)
        viewpoints_sample = self._prepare_viewpoints_sample(book)
        main_themes = self._extract_main_themes(book)

        # 调用GPT-4生成提纲
        logger.info("🤖 正在调用GPT-4生成提纲...")
        episodes_data = await self._generate_episodes_with_gpt(
            book=book,
            chapters_overview=chapters_overview,
            viewpoints_sample=viewpoints_sample,
            main_themes=main_themes
        )

        # 创建BookSeries对象
        series = BookSeries(
            series_id=str(uuid.uuid4()),
            book_id=book.book_id,
            book_title=book.title,
            author_name=book.author,
            total_episodes=episodes_count
        )

        # 为每集创建EpisodeOutline
        for episode_data in episodes_data['episodes']:
            # 查找对应的章节ID
            target_chapter_ids = self._match_chapters_by_title(
                book,
                episode_data['target_chapters']
            )

            # 匹配热点话题
            hot_topics = await self._match_hot_topics(
                episode_data['theme'],
                episode_data['discussion_points']
            )

            # 创建EpisodeOutline
            # 生成基本流程设计
            flow_design = {
                "opening": f"主持人开场，引入本集主题：{episode_data['theme']}",
                "book_exploration": f"作者主讲，探讨{episode_data['target_chapters'][0] if episode_data['target_chapters'] else '相关章节'}的核心观点",
                "hot_topic_connection": f"结合现代热点话题，探讨{episode_data['theme']}的现实意义",
                "deep_discussion": "主持人与作者深度思辨，展开多层次讨论",
                "conclusion": "总结升华，提出启发性思考"
            }

            episode_outline = EpisodeOutline(
                outline_id=str(uuid.uuid4()),
                book_id=book.book_id,
                episode_number=episode_data['episode_number'],
                theme=episode_data['theme'],
                target_chapters=episode_data['target_chapters'],
                discussion_points=episode_data['discussion_points'],
                hot_topics=hot_topics,
                flow_design=flow_design,
                estimated_duration=30
            )

            series.outlines.append(episode_outline)

        logger.info(f"✅ 提纲生成完成: {len(series.outlines)}集")
        return series

    async def update_episode(
        self,
        outline_id: str,
        episode_number: int,
        updates: Dict[str, Any]
    ) -> bool:
        """
        更新单集提纲

        参数:
            outline_id: 提纲ID
            episode_number: 集数
            updates: 更新内容

        返回:
            是否更新成功
        """
        # TODO: 实现更新逻辑
        # 1. 从数据库加载outline
        # 2. 找到对应episode
        # 3. 应用更新
        # 4. 保存到数据库

        logger.info(f"✏️  更新第{episode_number}集提纲")
        return True

    def _prepare_chapters_overview(self, book: Book) -> str:
        """准备章节概览"""
        overview_parts = []

        for chapter in book.chapters:
            # 取前200字作为概览
            preview = chapter.content[:200] + "..." if len(chapter.content) > 200 else chapter.content
            overview_parts.append(f"- {chapter.title}: {preview}")

        return "\n".join(overview_parts[:10])  # 最多10章

    def _prepare_viewpoints_sample(self, book: Book) -> str:
        """准备核心观点样本"""
        sample_parts = []

        for vp in book.core_viewpoints[:10]:  # 取前10个
            sample_parts.append(f"- {vp.content}")

        return "\n".join(sample_parts)

    def _extract_main_themes(self, book: Book) -> List[str]:
        """提取主要主题"""
        # 基于关键词提取主题
        all_keywords = []
        for vp in book.core_viewpoints:
            all_keywords.extend(vp.keywords)

        # 统计高频词
        from collections import Counter
        keyword_freq = Counter(all_keywords)

        # 取前5个作为主要主题
        main_themes = [kw for kw, _ in keyword_freq.most_common(5)]
        return main_themes

    async def _generate_episodes_with_gpt(
        self,
        book: Book,
        chapters_overview: str,
        viewpoints_sample: str,
        main_themes: List[str]
    ) -> Dict[str, Any]:
        """
        调用GPT-4生成集数规划

        返回: 解析后的JSON字典
        """
        # 构建Prompt
        prompt = self.OUTLINE_GENERATION_PROMPT.format(
            title=book.title,
            author=book.author,
            total_chapters=len(book.chapters),
            main_themes="、".join(main_themes),
            chapters_overview=chapters_overview[:3000],  # 限制长度
            viewpoints_sample=viewpoints_sample
        )

        messages = [
            {"role": "system", "content": "你是一位经验丰富的播客制作人。"},
            {"role": "user", "content": prompt}
        ]

        try:
            # 调用OpenAI
            response = await self.openai_client.chat_completion(
                messages=messages,
                temperature=0.5
            )

            # 解析JSON
            content = response['content']
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]

            episodes_data = json.loads(content.strip())
            return episodes_data

        except Exception as e:
            logger.error(f"❌ 提纲生成失败: {e}")
            # 返回Mock数据
            return self._get_mock_episodes(book)

    async def _match_hot_topics(
        self,
        theme: str,
        discussion_points: List[str]
    ) -> List[HotTopicMatch]:
        """
        匹配热点话题

        参数:
            theme: 集数主题
            discussion_points: 讨论重点

        返回:
            匹配的热点话题列表
        """
        # TODO: 实现热点匹配逻辑
        # 1. 调用热点API或查询热点数据库
        # 2. 计算相关性评分
        # 3. 筛选高相关性话题

        # 基于主题关键词生成不同的热点话题
        hot_topic_map = {
            "学习": "现代教育体系与终身学习",
            "实践": "理论与实践的结合",
            "治国": "现代治理与社会责任",
            "德政": "道德领导力与企业管理",
            "礼乐": "文化传承与现代礼仪",
            "仁爱": "人际关系与心理健康",
            "道德": "职业操守与社会道德",
            "君子": "人格塑造与自我提升",
            "智慧": "批判性思维与决策",
            "言辞": "沟通技巧与表达",
            "行为": "行为规范与职场礼仪",
            "社会": "公民参与和社会责任"
        }

        # 找到匹配的热点话题
        matched_topic = "当代社会热点话题"
        for keyword, topic in hot_topic_map.items():
            if keyword in theme or keyword in str(discussion_points):
                matched_topic = topic
                break

        mock_topics = [
            HotTopicMatch(
                topic_title=matched_topic,
                topic_description=f"与《{theme}》主题相关的现代社会讨论",
                relevance_score=0.85,
                connection_point=f"从{theme}的角度思考现代{matched_topic.split('与')[-1] if '与' in matched_topic else matched_topic}"
            )
        ]

        return mock_topics

    def _match_chapters_by_title(
        self,
        book: Book,
        chapter_titles: List[str]
    ) -> List[str]:
        """根据章节标题匹配章节ID"""
        matched_ids = []

        for title in chapter_titles:
            # 模糊匹配
            for chapter in book.chapters:
                if title in chapter.title or chapter.title in title:
                    matched_ids.append(chapter.chapter_id)
                    break

        return matched_ids

    def _get_mock_episodes(self, book: Book) -> Dict[str, Any]:
        """获取Mock提纲数据（用于开发测试）"""
        return {
            "episodes": [
                {
                    "episode_number": 1,
                    "theme": f"《{book.title}》的写作背景",
                    "target_chapters": ["序言", "第一章"],
                    "discussion_points": [
                        "作者写作的历史背景",
                        "著作的核心问题意识",
                        "在当代的现实意义"
                    ]
                },
                {
                    "episode_number": 2,
                    "theme": "核心概念解析",
                    "target_chapters": ["第二章", "第三章"],
                    "discussion_points": [
                        "关键术语的定义",
                        "概念之间的逻辑关系",
                        "常见误解辨析"
                    ]
                }
            ]
        }


# 全局单例
_outline_generator: Optional[OutlineGenerator] = None


def get_outline_generator() -> OutlineGenerator:
    """获取提纲生成器单例"""
    global _outline_generator
    if _outline_generator is None:
        _outline_generator = OutlineGenerator()
    return _outline_generator


if __name__ == "__main__":
    # 测试代码
    import asyncio

    async def test():
        """测试提纲生成"""
        generator = get_outline_generator()

        # 创建测试数据
        from app.models.book import Book, Chapter, CoreViewpoint
        from app.models.persona import AuthorPersona, ThinkingStyle

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
                    content="正义是什么？这是本卷的核心问题..."
                ),
                Chapter(
                    chapter_id="ch-002",
                    chapter_number=2,
                    title="第二卷",
                    content="关于理想国家的构想..."
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

        test_persona = AuthorPersona(
            persona_id="persona-001",
            author_name="柏拉图",
            book_id="test-001",
            thinking_style=ThinkingStyle.DIALECTICAL,
            logic_pattern="辩证法",
            reasoning_framework="苏格拉底问答法",
            core_philosophy="追求真理和正义",
            theoretical_framework="理念论",
            key_concepts={"理念": "永恒真实"},
            narrative_style="严肃",
            language_rhythm="沉稳",
            sentence_structure="复杂",
            rhetorical_devices=["比喻"],
            value_orientation="理想主义",
            value_judgment_framework="以真理为标准",
            core_positions=["正义至上"],
            opposed_positions=[" relativism"],
            tone="温和",
            emotion_tendency="理性",
            expressiveness="委婉",
            personality_traits=["智慧"],
            communication_style="对话",
            attitude_toward_audience="尊重"
        )

        try:
            # 生成提纲
            outline = await generator.generate_outline(test_book, test_persona)

            print(f"✅ 提纲生成成功!")
            print(f"提纲ID: {outline.outline_id}")
            print(f"总集数: {outline.total_episodes}")

            print("\n集数列表:")
            for episode in outline.episodes:
                print(f"  第{episode['episode_number']}集: {episode['theme']}")
                print(f"    讨论: {', '.join(episode['discussion_points'][:2])}")

        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()

    # 运行测试
    asyncio.run(test())
