"""
数据库ORM模型
定义SQLAlchemy表结构
"""
from sqlalchemy import Column, String, Integer, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class BookORM(Base):
    """著作表"""
    __tablename__ = "books"

    book_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    language = Column(String, default="zh")
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)

    # 内容统计
    total_words = Column(Integer, default=0)
    total_chapters = Column(Integer, default=0)
    total_viewpoints = Column(Integer, default=0)

    # 元数据
    version = Column(String, nullable=True)
    publisher = Column(String, nullable=True)
    publish_year = Column(Integer, nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联关系
    chapters = relationship("ChapterORM", back_populates="book", cascade="all, delete-orphan")
    viewpoints = relationship("CoreViewpointORM", back_populates="book", cascade="all, delete-orphan")
    personas = relationship("AuthorPersonaORM", back_populates="book", cascade="all, delete-orphan")
    audience_personas = relationship("AudiencePersonaORM", back_populates="book", cascade="all, delete-orphan")
    series = relationship("BookSeriesORM", back_populates="book", cascade="all, delete-orphan")
    outputs = relationship("OutputArtifactORM", back_populates="book", cascade="all, delete-orphan")
    diagnostics = relationship("DiagnosticReportORM", back_populates="book", cascade="all, delete-orphan")


class ChapterORM(Base):
    """章节表"""
    __tablename__ = "chapters"

    chapter_id = Column(String, primary_key=True, index=True)
    book_id = Column(String, ForeignKey("books.book_id"), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    page_range = Column(String, nullable=True)
    word_count = Column(Integer, default=0)
    paragraph_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.now)

    # 关联关系
    book = relationship("BookORM", back_populates="chapters")
    viewpoints = relationship("CoreViewpointORM", back_populates="chapter", cascade="all, delete-orphan")
    paragraphs = relationship("ParagraphORM", back_populates="chapter", cascade="all, delete-orphan")


class CoreViewpointORM(Base):
    """核心观点表"""
    __tablename__ = "core_viewpoints"

    viewpoint_id = Column(String, primary_key=True, index=True)
    book_id = Column(String, ForeignKey("books.book_id"), nullable=False)
    chapter_id = Column(String, ForeignKey("chapters.chapter_id"), nullable=False)

    content = Column(Text, nullable=False)
    original_text = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    keywords = Column(JSON, default=list)  # 存储关键词列表

    created_at = Column(DateTime, default=datetime.now)

    # 关联关系
    book = relationship("BookORM", back_populates="viewpoints")
    chapter = relationship("ChapterORM", back_populates="viewpoints")
    evidences = relationship("EvidenceORM", back_populates="viewpoint", cascade="all, delete-orphan")


class ParagraphORM(Base):
    """段落表"""
    __tablename__ = "paragraphs"

    paragraph_id = Column(String, primary_key=True, index=True)
    book_id = Column(String, ForeignKey("books.book_id"), nullable=False)
    chapter_id = Column(String, ForeignKey("chapters.chapter_id"), nullable=False)
    paragraph_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    word_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

    # 关联关系
    chapter = relationship("ChapterORM", back_populates="paragraphs")
    evidences = relationship("EvidenceORM", back_populates="paragraph", cascade="all, delete-orphan")


class EvidenceORM(Base):
    """证据表（观点-原文-上下文绑定）"""
    __tablename__ = "evidences"

    evidence_id = Column(String, primary_key=True, index=True)
    book_id = Column(String, ForeignKey("books.book_id"), nullable=False)
    chapter_id = Column(String, ForeignKey("chapters.chapter_id"), nullable=False)
    paragraph_id = Column(String, ForeignKey("paragraphs.paragraph_id"), nullable=True)
    viewpoint_id = Column(String, ForeignKey("core_viewpoints.viewpoint_id"), nullable=True)

    evidence_text = Column(Text, nullable=False)
    context_before = Column(Text, nullable=True)
    context_after = Column(Text, nullable=True)
    keywords = Column(JSON, default=list)
    score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.now)

    # 关联关系
    viewpoint = relationship("CoreViewpointORM", back_populates="evidences")
    paragraph = relationship("ParagraphORM", back_populates="evidences")


class AuthorPersonaORM(Base):
    """作者Persona表"""
    __tablename__ = "author_personas"

    persona_id = Column(String, primary_key=True, index=True)
    book_id = Column(String, ForeignKey("books.book_id"), nullable=False)
    author_name = Column(String, nullable=False)

    # 思维方式
    thinking_style = Column(String, nullable=False)
    logic_pattern = Column(Text, nullable=True)
    reasoning_framework = Column(Text, nullable=True)

    # 哲学体系
    core_philosophy = Column(Text, nullable=True)
    theoretical_framework = Column(Text, nullable=True)
    key_concepts = Column(JSON, default=dict)

    # 叙事风格
    narrative_style = Column(String, nullable=True)
    language_rhythm = Column(String, nullable=True)
    sentence_structure = Column(String, nullable=True)
    rhetorical_devices = Column(JSON, default=list)

    # 价值观
    value_orientation = Column(String, nullable=True)
    value_judgment_framework = Column(Text, nullable=True)
    core_positions = Column(JSON, default=list)
    opposed_positions = Column(JSON, default=list)

    # 语气和性格
    tone = Column(String, nullable=True)
    emotion_tendency = Column(String, nullable=True)
    expressiveness = Column(String, nullable=True)
    personality_traits = Column(JSON, default=list)
    communication_style = Column(Text, nullable=True)
    attitude_toward_audience = Column(Text, nullable=True)

    # System Prompt
    system_prompt = Column(Text, nullable=True)

    # 元数据
    era = Column(String, nullable=True)
    identity = Column(String, nullable=True)
    version = Column(String, default="1.0")
    evidence_links = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.now)

    # 关联关系
    book = relationship("BookORM", back_populates="personas")
    series = relationship("BookSeriesORM", back_populates="persona")
    outputs = relationship("OutputArtifactORM", back_populates="speaker_persona")
    diagnostics = relationship("DiagnosticReportORM", back_populates="speaker_persona")


class AudiencePersonaORM(Base):
    """受众Persona表"""
    __tablename__ = "audience_personas"

    audience_id = Column(String, primary_key=True, index=True)
    book_id = Column(String, ForeignKey("books.book_id"), nullable=True)
    label = Column(String, nullable=False)

    education_stage = Column(String, nullable=False)
    prior_knowledge = Column(String, nullable=False)
    cognitive_preference = Column(String, nullable=False)
    language_preference = Column(String, nullable=False)
    tone_preference = Column(String, nullable=False)

    term_density = Column(Integer, default=3)
    sentence_length = Column(Integer, default=3)
    abstraction_level = Column(Integer, default=3)
    example_complexity = Column(Integer, default=3)
    proof_depth = Column(Integer, default=3)

    constraints = Column(JSON, default=list)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联关系
    book = relationship("BookORM", back_populates="audience_personas")
    outputs = relationship("OutputArtifactORM", back_populates="audience_persona")
    diagnostics = relationship("DiagnosticReportORM", back_populates="audience_persona")


class BookSeriesORM(Base):
    """著作合集（10集提纲）表"""
    __tablename__ = "book_series"

    series_id = Column(String, primary_key=True, index=True)
    book_id = Column(String, ForeignKey("books.book_id"), nullable=False)
    persona_id = Column(String, ForeignKey("author_personas.persona_id"), nullable=True)

    book_title = Column(String, nullable=False)
    author_name = Column(String, nullable=False)

    total_episodes = Column(Integer, default=10)
    total_duration = Column(Integer, default=0)
    completion_status = Column(String, default="pending")

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联关系
    book = relationship("BookORM", back_populates="series")
    persona = relationship("AuthorPersonaORM", back_populates="series")
    outlines = relationship("EpisodeOutlineORM", back_populates="series", cascade="all, delete-orphan")


class EpisodeOutlineORM(Base):
    """单集提纲表"""
    __tablename__ = "episode_outlines"

    outline_id = Column(String, primary_key=True, index=True)
    series_id = Column(String, ForeignKey("book_series.series_id"), nullable=False)
    book_id = Column(String, ForeignKey("books.book_id"), nullable=False)

    episode_number = Column(Integer, nullable=False)
    theme = Column(String, nullable=False)
    target_chapters = Column(JSON, default=list)  # 章节标题列表
    target_viewpoints = Column(JSON, default=list)  # 观点ID列表

    discussion_points = Column(JSON, default=list)
    hot_topics = Column(JSON, default=list)  # 热点匹配列表

    # 流程设计
    flow_design = Column(JSON, default=dict)

    estimated_duration = Column(Integer, default=30)  # 分钟
    created_at = Column(DateTime, default=datetime.now)

    # 关联关系
    series = relationship("BookSeriesORM", back_populates="outlines")


class EpisodeScriptORM(Base):
    """单集对话脚本表"""
    __tablename__ = "episode_scripts"

    script_id = Column(String, primary_key=True, index=True)
    outline_id = Column(String, ForeignKey("episode_outlines.outline_id"), nullable=False)
    book_id = Column(String, ForeignKey("books.book_id"), nullable=False)

    episode_number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    theme = Column(String, nullable=False)

    # 对话内容
    dialogue_turns = Column(JSON, default=list)  # 对话轮次列表

    # 统计信息
    total_duration = Column(Integer, default=0)
    total_word_count = Column(Integer, default=0)
    author_speaking_ratio = Column(Float, default=0.6)
    host_speaking_ratio = Column(Float, default=0.4)

    # 质量评估
    quality_metrics = Column(JSON, default=dict)

    generation_time = Column(DateTime, default=datetime.now)
    version = Column(String, default="1.0")


class OutputArtifactORM(Base):
    """输出内容表（提纲/对话/改写等）"""
    __tablename__ = "output_artifacts"

    artifact_id = Column(String, primary_key=True, index=True)
    book_id = Column(String, ForeignKey("books.book_id"), nullable=False)
    speaker_persona_id = Column(String, ForeignKey("author_personas.persona_id"), nullable=True)
    audience_persona_id = Column(String, ForeignKey("audience_personas.audience_id"), nullable=True)

    task_type = Column(String, nullable=False)  # outline/dialogue/rewrite/explain
    title = Column(String, nullable=True)

    style_config = Column(JSON, default=dict)
    locked_facts = Column(JSON, default=list)
    stage_outputs = Column(JSON, default=dict)  # canonical/plan/final
    final_text = Column(Text, nullable=True)
    content_format = Column(String, default="text")
    metrics = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.now)

    # 关联关系
    book = relationship("BookORM", back_populates="outputs")
    speaker_persona = relationship("AuthorPersonaORM", back_populates="outputs")
    audience_persona = relationship("AudiencePersonaORM", back_populates="outputs")
    diagnostics = relationship("DiagnosticReportORM", back_populates="artifact", cascade="all, delete-orphan")


class DiagnosticReportORM(Base):
    """诊断报告表"""
    __tablename__ = "diagnostic_reports"

    report_id = Column(String, primary_key=True, index=True)
    artifact_id = Column(String, ForeignKey("output_artifacts.artifact_id"), nullable=False)
    book_id = Column(String, ForeignKey("books.book_id"), nullable=False)
    speaker_persona_id = Column(String, ForeignKey("author_personas.persona_id"), nullable=True)
    audience_persona_id = Column(String, ForeignKey("audience_personas.audience_id"), nullable=True)

    metrics = Column(JSON, default=dict)
    issues = Column(JSON, default=list)
    suggestions = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.now)

    # 关联关系
    book = relationship("BookORM", back_populates="diagnostics")
    speaker_persona = relationship("AuthorPersonaORM", back_populates="diagnostics")
    audience_persona = relationship("AudiencePersonaORM", back_populates="diagnostics")
    artifact = relationship("OutputArtifactORM", back_populates="diagnostics")


class ModelProviderORM(Base):
    """模型提供方配置表"""
    __tablename__ = "model_providers"

    provider_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    provider_type = Column(String, nullable=False)  # openai/azure/anthropic/deepseek/qwen/ollama/custom
    base_url = Column(String, nullable=True)
    api_key = Column(String, nullable=True)
    api_version = Column(String, nullable=True)
    model = Column(String, nullable=False)
    extra_headers = Column(JSON, default=dict)
    is_active = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
