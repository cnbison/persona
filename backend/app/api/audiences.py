"""
受众Persona管理API
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import List, Optional
from loguru import logger
import uuid

from app.database import get_db
from app.models.orm import AudiencePersonaORM, BookORM
from app.models.persona import AudiencePersona
from app.crud.crud_audience import (
    create_audience_persona,
    get_audience_persona,
    get_audience_personas,
    update_audience_persona,
    delete_audience_persona
)

router = APIRouter()


class CreateAudiencePersonaRequest(BaseModel):
    """创建受众Persona请求"""
    label: str = Field(..., description="受众名称")
    book_id: Optional[str] = Field(None, description="关联著作ID（可选）")

    education_stage: str = Field(..., description="教育阶段")
    prior_knowledge: str = Field(..., description="先验知识水平")
    cognitive_preference: str = Field(..., description="认知偏好")
    language_preference: str = Field(..., description="语言风格偏好")
    tone_preference: str = Field(..., description="语气偏好")

    term_density: int = Field(3, ge=1, le=5, description="术语密度")
    sentence_length: int = Field(3, ge=1, le=5, description="句长复杂度")
    abstraction_level: int = Field(3, ge=1, le=5, description="抽象程度")
    example_complexity: int = Field(3, ge=1, le=5, description="案例复杂度")
    proof_depth: int = Field(3, ge=1, le=5, description="论证深度")

    constraints: List[str] = Field(default_factory=list, description="硬性限制")


class UpdateAudiencePersonaRequest(BaseModel):
    """更新受众Persona请求"""
    label: Optional[str] = None
    book_id: Optional[str] = None

    education_stage: Optional[str] = None
    prior_knowledge: Optional[str] = None
    cognitive_preference: Optional[str] = None
    language_preference: Optional[str] = None
    tone_preference: Optional[str] = None

    term_density: Optional[int] = Field(None, ge=1, le=5)
    sentence_length: Optional[int] = Field(None, ge=1, le=5)
    abstraction_level: Optional[int] = Field(None, ge=1, le=5)
    example_complexity: Optional[int] = Field(None, ge=1, le=5)
    proof_depth: Optional[int] = Field(None, ge=1, le=5)

    constraints: Optional[List[str]] = None


@router.post("/", summary="创建受众Persona")
async def create_audience(
    request: CreateAudiencePersonaRequest,
    db: Session = Depends(get_db)
):
    """
    创建受众Persona
    """
    try:
        # 若关联著作，检查存在性
        if request.book_id:
            book = db.query(BookORM).filter(BookORM.book_id == request.book_id).first()
            if not book:
                raise HTTPException(status_code=404, detail="著作不存在")

        audience_id = uuid.uuid4().hex
        audience = AudiencePersona(
            audience_id=audience_id,
            label=request.label,
            book_id=request.book_id,
            education_stage=request.education_stage,
            prior_knowledge=request.prior_knowledge,
            cognitive_preference=request.cognitive_preference,
            language_preference=request.language_preference,
            tone_preference=request.tone_preference,
            term_density=request.term_density,
            sentence_length=request.sentence_length,
            abstraction_level=request.abstraction_level,
            example_complexity=request.example_complexity,
            proof_depth=request.proof_depth,
            constraints=request.constraints
        )

        db_audience = create_audience_persona(db=db, audience=audience)

        return {
            "code": 200,
            "message": "受众Persona创建成功",
            "data": {
                "audience_id": db_audience.audience_id,
                "label": db_audience.label,
                "book_id": db_audience.book_id
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 创建受众Persona失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", summary="获取受众Persona列表")
async def list_audiences(
    skip: int = 0,
    limit: int = 100,
    book_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取受众Persona列表"""
    try:
        audiences = get_audience_personas(db, skip=skip, limit=limit, book_id=book_id)
        query = db.query(AudiencePersonaORM)
        if book_id:
            query = query.filter(AudiencePersonaORM.book_id == book_id)
        total = query.count()

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "audiences": [
                    {
                        "audience_id": a.audience_id,
                        "label": a.label,
                        "book_id": a.book_id,
                        "education_stage": a.education_stage,
                        "prior_knowledge": a.prior_knowledge,
                        "cognitive_preference": a.cognitive_preference,
                        "language_preference": a.language_preference,
                        "tone_preference": a.tone_preference,
                        "created_at": a.created_at.isoformat() if a.created_at else None
                    }
                    for a in audiences
                ],
                "total": total
            }
        }

    except Exception as e:
        logger.error(f"❌ 获取受众Persona列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{audience_id}", summary="获取受众Persona详情")
async def get_audience_detail(audience_id: str, db: Session = Depends(get_db)):
    """获取受众Persona详情"""
    try:
        audience = get_audience_persona(db, audience_id)
        if not audience:
            raise HTTPException(status_code=404, detail="受众Persona不存在")

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "audience_id": audience.audience_id,
                "label": audience.label,
                "book_id": audience.book_id,
                "education_stage": audience.education_stage,
                "prior_knowledge": audience.prior_knowledge,
                "cognitive_preference": audience.cognitive_preference,
                "language_preference": audience.language_preference,
                "tone_preference": audience.tone_preference,
                "term_density": audience.term_density,
                "sentence_length": audience.sentence_length,
                "abstraction_level": audience.abstraction_level,
                "example_complexity": audience.example_complexity,
                "proof_depth": audience.proof_depth,
                "constraints": audience.constraints,
                "created_at": audience.created_at.isoformat() if audience.created_at else None
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取受众Persona详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{audience_id}", summary="更新受众Persona")
async def update_audience(
    audience_id: str,
    request: UpdateAudiencePersonaRequest,
    db: Session = Depends(get_db)
):
    """更新受众Persona"""
    try:
        if request.book_id:
            book = db.query(BookORM).filter(BookORM.book_id == request.book_id).first()
            if not book:
                raise HTTPException(status_code=404, detail="著作不存在")

        update_data = request.model_dump(exclude_unset=True)
        audience = update_audience_persona(db, audience_id, **update_data)

        if not audience:
            raise HTTPException(status_code=404, detail="受众Persona不存在")

        return {
            "code": 200,
            "message": "更新成功",
            "data": {
                "audience_id": audience.audience_id,
                "label": audience.label,
                "book_id": audience.book_id
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 更新受众Persona失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{audience_id}", summary="删除受众Persona")
async def delete_audience(audience_id: str, db: Session = Depends(get_db)):
    """删除受众Persona"""
    try:
        success = delete_audience_persona(db, audience_id)
        if not success:
            raise HTTPException(status_code=404, detail="受众Persona不存在")

        return {
            "code": 200,
            "message": "删除成功",
            "data": {
                "audience_id": audience_id
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 删除受众Persona失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
