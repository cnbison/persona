"""
受众Persona CRUD操作
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from loguru import logger

from app.models.orm import AudiencePersonaORM
from app.models.persona import AudiencePersona


def create_audience_persona(db: Session, audience: AudiencePersona) -> AudiencePersonaORM:
    """创建受众Persona记录"""
    db_audience = AudiencePersonaORM(
        audience_id=audience.audience_id,
        book_id=audience.book_id,
        label=audience.label,
        education_stage=audience.education_stage,
        prior_knowledge=audience.prior_knowledge,
        cognitive_preference=audience.cognitive_preference,
        language_preference=audience.language_preference,
        tone_preference=audience.tone_preference,
        term_density=audience.term_density,
        sentence_length=audience.sentence_length,
        abstraction_level=audience.abstraction_level,
        example_complexity=audience.example_complexity,
        proof_depth=audience.proof_depth,
        constraints=audience.constraints
    )

    db.add(db_audience)
    db.commit()
    db.refresh(db_audience)

    logger.info(f"✅ 创建受众Persona成功: {audience.label} ({audience.audience_id})")

    return db_audience


def get_audience_persona(db: Session, audience_id: str) -> Optional[AudiencePersonaORM]:
    """获取受众Persona"""
    return db.query(AudiencePersonaORM).filter(AudiencePersonaORM.audience_id == audience_id).first()


def get_audience_personas(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    book_id: Optional[str] = None
) -> List[AudiencePersonaORM]:
    """获取受众Persona列表"""
    query = db.query(AudiencePersonaORM)
    if book_id:
        query = query.filter(AudiencePersonaORM.book_id == book_id)
    return query.offset(skip).limit(limit).all()


def update_audience_persona(db: Session, audience_id: str, **kwargs) -> Optional[AudiencePersonaORM]:
    """更新受众Persona"""
    db_audience = db.query(AudiencePersonaORM).filter(AudiencePersonaORM.audience_id == audience_id).first()
    if db_audience:
        for key, value in kwargs.items():
            if hasattr(db_audience, key):
                setattr(db_audience, key, value)
        db.commit()
        db.refresh(db_audience)
        logger.info(f"✅ 更新受众Persona成功: {audience_id}")
        return db_audience
    return None


def delete_audience_persona(db: Session, audience_id: str) -> bool:
    """删除受众Persona"""
    db_audience = db.query(AudiencePersonaORM).filter(AudiencePersonaORM.audience_id == audience_id).first()
    if db_audience:
        db.delete(db_audience)
        db.commit()
        logger.info(f"✅ 删除受众Persona成功: {audience_id}")
        return True
    return False
