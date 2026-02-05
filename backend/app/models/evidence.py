"""
证据数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Paragraph(BaseModel):
    paragraph_id: str = Field(..., description="段落ID")
    chapter_id: str = Field(..., description="章节ID")
    paragraph_number: int = Field(..., description="段落序号")
    content: str = Field(..., description="段落内容")
    word_count: int = Field(default=0, description="段落字数")


class Evidence(BaseModel):
    evidence_id: str = Field(..., description="证据ID")
    book_id: str = Field(..., description="著作ID")
    chapter_id: str = Field(..., description="章节ID")
    paragraph_id: Optional[str] = Field(None, description="段落ID")
    viewpoint_id: Optional[str] = Field(None, description="观点ID")

    evidence_text: str = Field(..., description="证据原文")
    context_before: Optional[str] = Field(None, description="前文")
    context_after: Optional[str] = Field(None, description="后文")
    keywords: List[str] = Field(default_factory=list, description="关键词")
    score: float = Field(default=1.0, description="证据评分")

    created_at: datetime = Field(default_factory=datetime.now)
