"""
Diff对比API
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional
from loguru import logger

from app.database import get_db
from app.models.orm import OutputArtifactORM
from app.utils.diff_utils import diff_text

router = APIRouter()


class DiffRequest(BaseModel):
    """Diff请求"""
    a_text: Optional[str] = Field(None, description="文本A")
    b_text: Optional[str] = Field(None, description="文本B")
    a_artifact_id: Optional[str] = Field(None, description="输出内容A ID")
    b_artifact_id: Optional[str] = Field(None, description="输出内容B ID")
    a_stage: Optional[str] = Field(None, description="A阶段: canonical/plan/final")
    b_stage: Optional[str] = Field(None, description="B阶段: canonical/plan/final")


@router.post("/text", summary="文本Diff")
async def diff_by_text(request: DiffRequest):
    """基于直接文本做Diff"""
    try:
        if not request.a_text or not request.b_text:
            raise HTTPException(status_code=400, detail="a_text 与 b_text 必填")

        result = diff_text(request.a_text, request.b_text)
        return {
            "code": 200,
            "message": "获取成功",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Diff失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/artifacts", summary="输出内容Diff")
async def diff_by_artifacts(
    request: DiffRequest,
    db: Session = Depends(get_db)
):
    """基于输出内容做Diff"""
    try:
        if not request.a_artifact_id or not request.b_artifact_id:
            raise HTTPException(status_code=400, detail="a_artifact_id 与 b_artifact_id 必填")

        a_artifact = db.query(OutputArtifactORM).filter(
            OutputArtifactORM.artifact_id == request.a_artifact_id
        ).first()
        b_artifact = db.query(OutputArtifactORM).filter(
            OutputArtifactORM.artifact_id == request.b_artifact_id
        ).first()

        if not a_artifact or not b_artifact:
            raise HTTPException(status_code=404, detail="输出内容不存在")

        a_text = _resolve_artifact_text(a_artifact, request.a_stage)
        b_text = _resolve_artifact_text(b_artifact, request.b_stage)

        result = diff_text(a_text, b_text)
        return {
            "code": 200,
            "message": "获取成功",
            "data": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Diff失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _resolve_artifact_text(artifact: OutputArtifactORM, stage: Optional[str]) -> str:
    if stage and stage in (artifact.stage_outputs or {}):
        return artifact.stage_outputs.get(stage, "") or ""
    if artifact.final_text:
        return artifact.final_text
    if artifact.stage_outputs:
        return artifact.stage_outputs.get("final", "") or ""
    return ""
