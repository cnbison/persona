"""
输出内容与诊断模型
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


class OutputArtifact(BaseModel):
    """输出内容模型（提纲/对话/改写等）"""

    artifact_id: str = Field(..., description="输出内容ID")
    book_id: str = Field(..., description="著作ID")
    speaker_persona_id: Optional[str] = Field(None, description="说者Persona ID")
    audience_persona_id: Optional[str] = Field(None, description="受众Persona ID")

    task_type: str = Field(..., description="任务类型：outline/dialogue/rewrite/explain")
    title: Optional[str] = Field(None, description="标题")

    stage_outputs: Dict[str, str] = Field(
        default_factory=dict,
        description="阶段输出：canonical/plan/final"
    )
    final_text: Optional[str] = Field(None, description="最终文本")
    content_format: str = Field(default="text", description="内容格式")
    metrics: Dict[str, float] = Field(default_factory=dict, description="评估指标")

    created_at: datetime = Field(default_factory=datetime.now)


class DiagnosticReport(BaseModel):
    """诊断报告模型"""

    report_id: str = Field(..., description="诊断报告ID")
    artifact_id: str = Field(..., description="输出内容ID")
    book_id: str = Field(..., description="著作ID")
    speaker_persona_id: Optional[str] = Field(None, description="说者Persona ID")
    audience_persona_id: Optional[str] = Field(None, description="受众Persona ID")

    metrics: Dict[str, float] = Field(default_factory=dict, description="诊断指标")
    issues: List[str] = Field(default_factory=list, description="问题列表")
    suggestions: Optional[str] = Field(None, description="优化建议")

    created_at: datetime = Field(default_factory=datetime.now)
