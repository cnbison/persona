"""
模型提供方配置模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime


class ModelProvider(BaseModel):
    provider_id: str
    name: str
    provider_type: str
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    api_version: Optional[str] = None
    model: str
    extra_headers: Dict[str, str] = Field(default_factory=dict)
    is_active: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
