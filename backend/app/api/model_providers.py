"""
模型提供方管理API
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from loguru import logger
import uuid

from app.database import get_db
from app.models.orm import ModelProviderORM
from app.crud.crud_providers import (
    create_provider,
    get_provider,
    get_providers,
    get_active_provider,
    update_provider,
    delete_provider
)

router = APIRouter()


class ProviderRequest(BaseModel):
    name: str = Field(..., description="名称")
    provider_type: str = Field(..., description="类型")
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    api_version: Optional[str] = None
    model: str = Field(..., description="模型或部署名")
    extra_headers: Dict[str, str] = Field(default_factory=dict)
    is_active: bool = False


class ProviderUpdateRequest(BaseModel):
    name: Optional[str] = None
    provider_type: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    api_version: Optional[str] = None
    model: Optional[str] = None
    extra_headers: Optional[Dict[str, str]] = None
    is_active: Optional[bool] = None


@router.get("/", summary="获取模型提供方列表")
async def list_providers(db: Session = Depends(get_db)):
    providers = get_providers(db)
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "items": [
                {
                    "provider_id": p.provider_id,
                    "name": p.name,
                    "provider_type": p.provider_type,
                    "base_url": p.base_url,
                    "api_version": p.api_version,
                    "model": p.model,
                    "extra_headers": p.extra_headers or {},
                    "is_active": bool(p.is_active),
                    "created_at": p.created_at.isoformat() if p.created_at else None
                }
                for p in providers
            ]
        }
    }


@router.get("/active", summary="获取当前激活模型")
async def get_active(db: Session = Depends(get_db)):
    provider = get_active_provider(db)
    if not provider:
        raise HTTPException(status_code=404, detail="未设置激活模型")
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "provider_id": provider.provider_id,
            "name": provider.name,
            "provider_type": provider.provider_type,
            "base_url": provider.base_url,
            "api_version": provider.api_version,
            "model": provider.model,
            "extra_headers": provider.extra_headers or {},
            "is_active": bool(provider.is_active)
        }
    }


@router.post("/", summary="创建模型提供方")
async def create_provider_api(request: ProviderRequest, db: Session = Depends(get_db)):
    try:
        provider = ModelProviderORM(
            provider_id=uuid.uuid4().hex,
            name=request.name,
            provider_type=request.provider_type,
            base_url=request.base_url,
            api_key=request.api_key,
            api_version=request.api_version,
            model=request.model,
            extra_headers=request.extra_headers,
            is_active=1 if request.is_active else 0
        )
        db_provider = create_provider(db, provider)
        return {
            "code": 200,
            "message": "创建成功",
            "data": {"provider_id": db_provider.provider_id}
        }
    except Exception as e:
        logger.error(f"❌ 创建模型提供方失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{provider_id}", summary="更新模型提供方")
async def update_provider_api(
    provider_id: str,
    request: ProviderUpdateRequest,
    db: Session = Depends(get_db)
):
    update_data = request.model_dump(exclude_unset=True)
    provider = update_provider(db, provider_id, **update_data)
    if not provider:
        raise HTTPException(status_code=404, detail="模型提供方不存在")
    return {
        "code": 200,
        "message": "更新成功",
        "data": {"provider_id": provider.provider_id}
    }


@router.delete("/{provider_id}", summary="删除模型提供方")
async def delete_provider_api(provider_id: str, db: Session = Depends(get_db)):
    success = delete_provider(db, provider_id)
    if not success:
        raise HTTPException(status_code=404, detail="模型提供方不存在")
    return {
        "code": 200,
        "message": "删除成功",
        "data": {"provider_id": provider_id}
    }
