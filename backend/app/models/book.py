"""
著作数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Chapter(BaseModel):
    """章节模型"""
    chapter_id: str = Field(..., description="章节ID")
    chapter_number: int = Field(..., description="章节编号")
    title: str = Field(..., description="章节标题")
    content: str = Field(..., description="章节内容")
    page_range: Optional[str] = Field(None, description="页码范围")


class CoreViewpoint(BaseModel):
    """核心观点模型"""
    viewpoint_id: str = Field(..., description="观点ID")
    content: str = Field(..., description="观点内容")
    original_text: str = Field(..., description="原文片段")
    chapter_id: str = Field(..., description="所属章节ID")
    context: str = Field(..., description="上下文")
    keywords: List[str] = Field(default_factory=list, description="关键词")


class Book(BaseModel):
    """著作模型"""
    book_id: str = Field(..., description="著作ID")
    title: str = Field(..., description="著作标题")
    author: str = Field(..., description="作者")
    language: str = Field(default="zh", description="语言")
    file_path: str = Field(..., description="文件路径")
    file_type: str = Field(..., description="文件类型：pdf/epub/txt")

    # 结构化内容
    chapters: List[Chapter] = Field(default_factory=list, description="章节列表")
    core_viewpoints: List[CoreViewpoint] = Field(default_factory=list, description="核心观点列表")

    # 元数据
    total_words: int = Field(default=0, description="总字数")
    parse_stats: dict = Field(default_factory=dict, description="解析统计")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # 版本信息
    version: Optional[str] = Field(None, description="版本信息")
    publisher: Optional[str] = Field(None, description="出版社")
    publish_year: Optional[int] = Field(None, description="出版年份")


class BookAnalysis(BaseModel):
    """著作分析结果"""
    book_id: str
    mind_map: str = Field(..., description="思维导图（JSON或文本格式）")
    summary: str = Field(..., description="著作摘要")
    main_themes: List[str] = Field(default_factory=list, description="主要主题")
    writing_style: str = Field(..., description="写作风格分析")
