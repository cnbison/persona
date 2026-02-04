"""
健康检查API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from loguru import logger

from app.database import get_db
from app.utils.config import settings

router = APIRouter()


@router.get("/health", summary="健康检查")
async def health_check(db: Session = Depends(get_db)):
    """
    健康检查端点

    返回系统状态信息
    """
    # 检查数据库连接
    try:
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        db_status = "disconnected"

    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "service": settings.project_name,
        "version": settings.project_version,
        "database": db_status,
        "openai_model": settings.openai_model,
        "debug": settings.debug
    }
