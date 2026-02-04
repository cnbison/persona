"""
对话脚本模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class DialogueRole(str, Enum):
    """对话角色"""
    AUTHOR = "author"  # 虚拟作者
    HOST = "host"  # 主持人


class DialogueTurn(BaseModel):
    """对话轮次"""
    turn_id: str = Field(..., description="轮次ID")
    role: DialogueRole = Field(..., description="角色")
    content: str = Field(..., description="对话内容")

    # 引用信息
    original_text_ref: Optional[str] = Field(None, description="引用的原文")
    viewpoint_ref: Optional[str] = Field(None, description="引用的观点ID")
    hot_topic_ref: Optional[str] = Field(None, description="关联的热点话题")

    # 元数据
    duration_seconds: Optional[int] = Field(None, description="预估时长（秒）")
    word_count: int = Field(..., description="字数")

    # 质量标注
    quality_score: Optional[float] = Field(None, description="质量评分")


class HotTopicMatch(BaseModel):
    """热点匹配"""
    topic_title: str = Field(..., description="热点标题")
    topic_description: str = Field(..., description="热点描述")
    relevance_score: float = Field(..., ge=0, le=1, description="相关性评分")
    connection_point: str = Field(..., description="连接点说明")


class EpisodeOutline(BaseModel):
    """单集提纲"""
    outline_id: str = Field(..., description="提纲ID")
    book_id: str = Field(..., description="著作ID")
    episode_number: int = Field(..., description="集数（1-10）")

    # 主题信息
    theme: str = Field(..., description="本集主题")
    target_chapters: List[str] = Field(default_factory=list, description="对应章节")
    target_viewpoints: List[str] = Field(default_factory=list, description="对应观点ID列表")

    # 热点匹配
    hot_topics: List[HotTopicMatch] = Field(default_factory=list, description="推荐热点")

    # 讨论重点
    discussion_points: List[str] = Field(default_factory=list, description="讨论重点列表")

    # 流程设计
    flow_design: Dict[str, str] = Field(
        default_factory=dict,
        description={
            "opening": "开场引入",
            "book_exploration": "著作探讨要点",
            "hot_topic_connection": "热点连接方式",
            "deep_discussion": "深度思辨方向",
            "conclusion": "总结升华"
        }
    )

    # 元数据
    estimated_duration: int = Field(default=30, description="预估时长（分钟）")
    created_at: datetime = Field(default_factory=datetime.now)


class EpisodeScript(BaseModel):
    """单集对话脚本"""
    script_id: str = Field(..., description="脚本ID")
    outline_id: str = Field(..., description="关联的提纲ID")
    book_id: str = Field(..., description="著作ID")
    episode_number: int = Field(..., description="集数")

    # 基本信息
    title: str = Field(..., description="本集标题")
    theme: str = Field(..., description="本集主题")

    # 对话内容
    dialogue_turns: List[DialogueTurn] = Field(default_factory=list, description="对话轮次列表")

    # 统计信息
    total_duration: int = Field(..., description="总时长（分钟）")
    total_word_count: int = Field(..., description="总字数")
    author_speaking_ratio: float = Field(..., description="作者发言占比")
    host_speaking_ratio: float = Field(..., description="主持人发言占比")

    # 质量评估
    quality_metrics: Dict[str, float] = Field(
        default_factory=dict,
        description={
            "viewpoint_accuracy": 0.0,  # 观点准确性
            "persona_consistency": 0.0,  # 人格一致性
            "topic_naturalness": 0.0,  # 热点融合自然度
            "content_coherence": 0.0,  # 内容连贯性
        }
    )

    # 元数据
    generation_time: datetime = Field(default_factory=datetime.now)
    version: str = "1.0"


class BookSeries(BaseModel):
    """著作合集（10集）"""
    series_id: str = Field(..., description="合集ID")
    book_id: str = Field(..., description="著作ID")
    book_title: str = Field(..., description="著作标题")
    author_name: str = Field(..., description="作者姓名")

    # 合集内容
    outlines: List[EpisodeOutline] = Field(default_factory=list, description="10集提纲")
    scripts: List[EpisodeScript] = Field(default_factory=list, description="10集脚本")

    # 统计信息
    total_episodes: int = Field(default=10, description="总集数")
    total_duration: int = Field(default=0, description="总时长（分钟）")
    completion_status: str = Field(default="pending", description="完成状态")

    # 元数据
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class SystemContext(BaseModel):
    """System Context模板"""
    context_id: str = Field(..., description="Context ID")
    name: str = Field(..., description="模板名称")

    # 对话框架
    dialogue_flow: List[str] = Field(
        default_factory=lambda: [
            "opening",  # 开场引入
            "book_exploration",  # 著作探讨
            "hot_topic_connection",  # 热点连接
            "deep_discussion",  # 深度思辨
            "conclusion"  # 总结升华
        ],
        description="对话流程"
    )

    # 各环节详细说明
    flow_descriptions: Dict[str, str] = Field(
        default_factory=dict,
        description="各环节详细说明"
    )

    # 角色指令
    author_instructions: str = Field(..., description="作者角色指令")
    host_instructions: str = Field(..., description="主持人角色指令")

    # 全局规则
    global_rules: List[str] = Field(default_factory=list, description="全局规则")

    # 版本
    version: str = "1.0"
