"""
输出内容与诊断CRUD操作
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from loguru import logger

from app.models.orm import OutputArtifactORM, DiagnosticReportORM
from app.models.output import OutputArtifact, DiagnosticReport


def create_output_artifact(db: Session, artifact: OutputArtifact) -> OutputArtifactORM:
    """创建输出内容记录"""
    db_artifact = OutputArtifactORM(
        artifact_id=artifact.artifact_id,
        book_id=artifact.book_id,
        speaker_persona_id=artifact.speaker_persona_id,
        audience_persona_id=artifact.audience_persona_id,
        task_type=artifact.task_type,
        title=artifact.title,
        style_config=artifact.style_config,
        locked_facts=artifact.locked_facts,
        stage_outputs=artifact.stage_outputs,
        final_text=artifact.final_text,
        content_format=artifact.content_format,
        metrics=artifact.metrics
    )

    db.add(db_artifact)
    db.commit()
    db.refresh(db_artifact)

    logger.info(f"✅ 创建输出内容成功: {artifact.task_type} ({artifact.artifact_id})")

    return db_artifact


def get_output_artifact(db: Session, artifact_id: str) -> Optional[OutputArtifactORM]:
    """获取输出内容"""
    return db.query(OutputArtifactORM).filter(OutputArtifactORM.artifact_id == artifact_id).first()


def get_output_artifacts(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    book_id: Optional[str] = None,
    speaker_persona_id: Optional[str] = None,
    audience_persona_id: Optional[str] = None,
    task_type: Optional[str] = None
) -> List[OutputArtifactORM]:
    """获取输出内容列表"""
    query = db.query(OutputArtifactORM)
    if book_id:
        query = query.filter(OutputArtifactORM.book_id == book_id)
    if speaker_persona_id:
        query = query.filter(OutputArtifactORM.speaker_persona_id == speaker_persona_id)
    if audience_persona_id:
        query = query.filter(OutputArtifactORM.audience_persona_id == audience_persona_id)
    if task_type:
        query = query.filter(OutputArtifactORM.task_type == task_type)
    return query.offset(skip).limit(limit).all()


def delete_output_artifact(db: Session, artifact_id: str) -> bool:
    """删除输出内容"""
    db_artifact = db.query(OutputArtifactORM).filter(OutputArtifactORM.artifact_id == artifact_id).first()
    if db_artifact:
        db.delete(db_artifact)
        db.commit()
        logger.info(f"✅ 删除输出内容: {artifact_id}")
        return True
    return False


# ==================== 诊断报告 ====================

def create_diagnostic_report(db: Session, report: DiagnosticReport) -> DiagnosticReportORM:
    """创建诊断报告"""
    db_report = DiagnosticReportORM(
        report_id=report.report_id,
        artifact_id=report.artifact_id,
        book_id=report.book_id,
        speaker_persona_id=report.speaker_persona_id,
        audience_persona_id=report.audience_persona_id,
        metrics=report.metrics,
        issues=report.issues,
        suggestions=report.suggestions
    )

    db.add(db_report)
    db.commit()
    db.refresh(db_report)

    logger.info(f"✅ 创建诊断报告成功: {report.report_id}")

    return db_report


def get_diagnostic_report(db: Session, report_id: str) -> Optional[DiagnosticReportORM]:
    """获取诊断报告"""
    return db.query(DiagnosticReportORM).filter(DiagnosticReportORM.report_id == report_id).first()


def get_reports_by_artifact(db: Session, artifact_id: str) -> List[DiagnosticReportORM]:
    """根据输出内容获取诊断报告"""
    return db.query(DiagnosticReportORM).filter(DiagnosticReportORM.artifact_id == artifact_id).all()
