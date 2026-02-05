"""
模型提供方CRUD操作
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from loguru import logger

from app.models.orm import ModelProviderORM


def create_provider(db: Session, provider: ModelProviderORM) -> ModelProviderORM:
    if provider.is_active:
        db.query(ModelProviderORM).update({ModelProviderORM.is_active: 0})
    db.add(provider)
    db.commit()
    db.refresh(provider)
    logger.info(f"✅ 创建模型提供方: {provider.name}")
    return provider


def get_provider(db: Session, provider_id: str) -> Optional[ModelProviderORM]:
    return db.query(ModelProviderORM).filter(ModelProviderORM.provider_id == provider_id).first()


def get_providers(db: Session) -> List[ModelProviderORM]:
    return db.query(ModelProviderORM).order_by(ModelProviderORM.created_at.desc()).all()


def get_active_provider(db: Session) -> Optional[ModelProviderORM]:
    return db.query(ModelProviderORM).filter(ModelProviderORM.is_active == 1).first()


def update_provider(db: Session, provider_id: str, **kwargs) -> Optional[ModelProviderORM]:
    provider = get_provider(db, provider_id)
    if not provider:
        return None

    if "is_active" in kwargs and kwargs["is_active"]:
        db.query(ModelProviderORM).update({ModelProviderORM.is_active: 0})

    for key, value in kwargs.items():
        if hasattr(provider, key):
            setattr(provider, key, value)

    db.commit()
    db.refresh(provider)
    logger.info(f"✅ 更新模型提供方: {provider_id}")
    return provider


def delete_provider(db: Session, provider_id: str) -> bool:
    provider = get_provider(db, provider_id)
    if not provider:
        return False
    db.delete(provider)
    db.commit()
    logger.info(f"✅ 删除模型提供方: {provider_id}")
    return True
