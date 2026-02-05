"""
诊断指标API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from loguru import logger

from app.database import get_db
from app.models.orm import DiagnosticReportORM

router = APIRouter()


@router.get("/{report_id}", summary="获取诊断指标详情")
async def get_report(report_id: str, db: Session = Depends(get_db)):
    """获取诊断报告详情"""
    try:
        report = db.query(DiagnosticReportORM).filter(
            DiagnosticReportORM.report_id == report_id
        ).first()

        if not report:
            raise HTTPException(status_code=404, detail="诊断报告不存在")

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "report_id": report.report_id,
                "artifact_id": report.artifact_id,
                "book_id": report.book_id,
                "speaker_persona_id": report.speaker_persona_id,
                "audience_persona_id": report.audience_persona_id,
                "metrics": report.metrics,
                "issues": report.issues,
                "suggestions": report.suggestions,
                "created_at": report.created_at.isoformat() if report.created_at else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取诊断报告失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
