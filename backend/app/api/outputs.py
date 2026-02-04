"""
输出内容与诊断API
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from loguru import logger
import uuid

from app.database import get_db
from app.models.orm import BookORM, AuthorPersonaORM, AudiencePersonaORM
from app.models.output import OutputArtifact, DiagnosticReport
from app.models.persona import AudiencePersona
from app.services.audience_adapter import get_audience_adapter
from app.services.output_generator import get_output_generator
from app.services.diagnostic_evaluator import get_diagnostic_evaluator
from app.crud.crud_output import (
    create_output_artifact,
    get_output_artifact,
    get_output_artifacts,
    delete_output_artifact,
    create_diagnostic_report,
    get_diagnostic_report,
    get_reports_by_artifact
)

router = APIRouter()


class CreateOutputArtifactRequest(BaseModel):
    """创建输出内容请求"""
    book_id: str = Field(..., description="著作ID")
    speaker_persona_id: Optional[str] = Field(None, description="说者Persona ID")
    audience_persona_id: Optional[str] = Field(None, description="受众Persona ID")

    task_type: str = Field(..., description="任务类型")
    title: Optional[str] = Field(None, description="标题")

    locked_facts: List[str] = Field(default_factory=list, description="锁定概念/事实")
    stage_outputs: Dict[str, str] = Field(default_factory=dict, description="阶段输出")
    final_text: Optional[str] = Field(None, description="最终文本")
    content_format: str = Field(default="text", description="内容格式")
    metrics: Dict[str, float] = Field(default_factory=dict, description="评估指标")


class CreateDiagnosticReportRequest(BaseModel):
    """创建诊断报告请求"""
    speaker_persona_id: Optional[str] = Field(None, description="说者Persona ID")
    audience_persona_id: Optional[str] = Field(None, description="受众Persona ID")
    metrics: Dict[str, float] = Field(default_factory=dict, description="诊断指标")
    issues: List[str] = Field(default_factory=list, description="问题列表")
    suggestions: Optional[str] = Field(None, description="优化建议")


class GenerateOutputRequest(BaseModel):
    """生成输出内容请求"""
    book_id: str = Field(..., description="著作ID")
    source_text: str = Field(..., description="源文本")
    task_type: str = Field(..., description="任务类型")
    title: Optional[str] = Field(None, description="标题")
    content_format: str = Field(default="text", description="内容格式")

    speaker_persona_id: Optional[str] = Field(None, description="说者Persona ID")
    audience_persona_id: Optional[str] = Field(None, description="受众Persona ID")
    locked_facts: List[str] = Field(default_factory=list, description="锁定概念/事实")

    create_report: bool = Field(default=True, description="是否生成诊断报告")


@router.post("/", summary="创建输出内容")
async def create_output(
    request: CreateOutputArtifactRequest,
    db: Session = Depends(get_db)
):
    """创建输出内容"""
    try:
        # 检查著作存在
        book = db.query(BookORM).filter(BookORM.book_id == request.book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="著作不存在")

        # 可选检查Persona
        if request.speaker_persona_id:
            speaker = db.query(AuthorPersonaORM).filter(AuthorPersonaORM.persona_id == request.speaker_persona_id).first()
            if not speaker:
                raise HTTPException(status_code=404, detail="说者Persona不存在")

        if request.audience_persona_id:
            audience = db.query(AudiencePersonaORM).filter(AudiencePersonaORM.audience_id == request.audience_persona_id).first()
            if not audience:
                raise HTTPException(status_code=404, detail="受众Persona不存在")

        artifact_id = uuid.uuid4().hex
        artifact = OutputArtifact(
            artifact_id=artifact_id,
            book_id=request.book_id,
            speaker_persona_id=request.speaker_persona_id,
            audience_persona_id=request.audience_persona_id,
            task_type=request.task_type,
            title=request.title,
            locked_facts=request.locked_facts,
            stage_outputs=request.stage_outputs,
            final_text=request.final_text,
            content_format=request.content_format,
            metrics=request.metrics
        )

        db_artifact = create_output_artifact(db=db, artifact=artifact)

        return {
            "code": 200,
            "message": "输出内容创建成功",
            "data": {
                "artifact_id": db_artifact.artifact_id,
                "book_id": db_artifact.book_id,
                "task_type": db_artifact.task_type
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 创建输出内容失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", summary="生成输出内容并保存")
async def generate_output(
    request: GenerateOutputRequest,
    db: Session = Depends(get_db)
):
    """生成输出内容并保存"""
    try:
        book = db.query(BookORM).filter(BookORM.book_id == request.book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="著作不存在")

        speaker_profile = None
        if request.speaker_persona_id:
            speaker = db.query(AuthorPersonaORM).filter(
                AuthorPersonaORM.persona_id == request.speaker_persona_id
            ).first()
            if not speaker:
                raise HTTPException(status_code=404, detail="说者Persona不存在")
            speaker_profile = {
                "author_name": speaker.author_name,
                "thinking_style": speaker.thinking_style,
                "narrative_style": speaker.narrative_style,
                "tone": speaker.tone,
                "core_philosophy": speaker.core_philosophy,
                "value_orientation": speaker.value_orientation
            }

        audience_profile = None
        audience_pydantic = None
        constraints = None
        if request.audience_persona_id:
            audience = db.query(AudiencePersonaORM).filter(
                AudiencePersonaORM.audience_id == request.audience_persona_id
            ).first()
            if not audience:
                raise HTTPException(status_code=404, detail="受众Persona不存在")

            audience_profile = {
                "label": audience.label,
                "education_stage": audience.education_stage,
                "prior_knowledge": audience.prior_knowledge,
                "cognitive_preference": audience.cognitive_preference,
                "language_preference": audience.language_preference,
                "tone_preference": audience.tone_preference
            }

            audience_pydantic = AudiencePersona(
                audience_id=audience.audience_id,
                label=audience.label,
                book_id=audience.book_id,
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
                constraints=audience.constraints or []
            )

            adapter = get_audience_adapter()
            constraints = adapter.build_constraints(audience_pydantic)

        generator = get_output_generator()
        outputs = await generator.generate_outputs(
            source_text=request.source_text,
            task_type=request.task_type,
            speaker_profile=speaker_profile,
            audience_profile=audience_profile,
            constraints=constraints,
            locked_facts=request.locked_facts
        )

        artifact_id = uuid.uuid4().hex
        artifact = OutputArtifact(
            artifact_id=artifact_id,
            book_id=request.book_id,
            speaker_persona_id=request.speaker_persona_id,
            audience_persona_id=request.audience_persona_id,
            task_type=request.task_type,
            title=request.title,
            locked_facts=request.locked_facts,
            stage_outputs=outputs,
            final_text=outputs.get("final"),
            content_format=request.content_format,
            metrics={}
        )

        db_artifact = create_output_artifact(db, artifact)

        report_id = None
        if request.create_report:
            evaluator = get_diagnostic_evaluator()
            report_data = evaluator.evaluate(
                outputs.get("final", ""),
                audience_pydantic,
                request.locked_facts
            )

            report = DiagnosticReport(
                report_id=uuid.uuid4().hex,
                artifact_id=db_artifact.artifact_id,
                book_id=db_artifact.book_id,
                speaker_persona_id=db_artifact.speaker_persona_id,
                audience_persona_id=db_artifact.audience_persona_id,
                metrics=report_data.get("metrics", {}),
                issues=report_data.get("issues", []),
                suggestions=None
            )
            db_report = create_diagnostic_report(db, report)
            report_id = db_report.report_id

        return {
            "code": 200,
            "message": "输出内容生成成功",
            "data": {
                "artifact_id": db_artifact.artifact_id,
                "report_id": report_id
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 生成输出内容失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", summary="获取输出内容列表")
async def list_outputs(
    skip: int = 0,
    limit: int = 50,
    book_id: Optional[str] = None,
    speaker_persona_id: Optional[str] = None,
    audience_persona_id: Optional[str] = None,
    task_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取输出内容列表"""
    try:
        artifacts = get_output_artifacts(
            db,
            skip=skip,
            limit=limit,
            book_id=book_id,
            speaker_persona_id=speaker_persona_id,
            audience_persona_id=audience_persona_id,
            task_type=task_type
        )

        total_query = db.query(OutputArtifactORM)
        if book_id:
            total_query = total_query.filter(OutputArtifactORM.book_id == book_id)
        if speaker_persona_id:
            total_query = total_query.filter(OutputArtifactORM.speaker_persona_id == speaker_persona_id)
        if audience_persona_id:
            total_query = total_query.filter(OutputArtifactORM.audience_persona_id == audience_persona_id)
        if task_type:
            total_query = total_query.filter(OutputArtifactORM.task_type == task_type)
        total = total_query.count()

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "artifacts": [
                    {
                        "artifact_id": a.artifact_id,
                        "book_id": a.book_id,
                        "speaker_persona_id": a.speaker_persona_id,
                        "audience_persona_id": a.audience_persona_id,
                        "task_type": a.task_type,
                        "title": a.title,
                        "locked_facts": a.locked_facts,
                        "content_format": a.content_format,
                        "created_at": a.created_at.isoformat() if a.created_at else None
                    }
                    for a in artifacts
                ],
                "total": total
            }
        }

    except Exception as e:
        logger.error(f"❌ 获取输出内容列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{artifact_id}", summary="获取输出内容详情")
async def get_output_detail(artifact_id: str, db: Session = Depends(get_db)):
    """获取输出内容详情"""
    try:
        artifact = get_output_artifact(db, artifact_id)
        if not artifact:
            raise HTTPException(status_code=404, detail="输出内容不存在")

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "artifact_id": artifact.artifact_id,
                "book_id": artifact.book_id,
                "speaker_persona_id": artifact.speaker_persona_id,
                "audience_persona_id": artifact.audience_persona_id,
                "task_type": artifact.task_type,
                "title": artifact.title,
                "locked_facts": artifact.locked_facts,
                "stage_outputs": artifact.stage_outputs,
                "final_text": artifact.final_text,
                "content_format": artifact.content_format,
                "metrics": artifact.metrics,
                "created_at": artifact.created_at.isoformat() if artifact.created_at else None
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取输出内容详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{artifact_id}", summary="删除输出内容")
async def delete_output(artifact_id: str, db: Session = Depends(get_db)):
    """删除输出内容"""
    try:
        success = delete_output_artifact(db, artifact_id)
        if not success:
            raise HTTPException(status_code=404, detail="输出内容不存在")

        return {
            "code": 200,
            "message": "删除成功",
            "data": {
                "artifact_id": artifact_id
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 删除输出内容失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{artifact_id}/diagnostics", summary="创建诊断报告")
async def create_report(
    artifact_id: str,
    request: CreateDiagnosticReportRequest,
    db: Session = Depends(get_db)
):
    """创建诊断报告"""
    try:
        artifact = get_output_artifact(db, artifact_id)
        if not artifact:
            raise HTTPException(status_code=404, detail="输出内容不存在")

        report_id = uuid.uuid4().hex
        report = DiagnosticReport(
            report_id=report_id,
            artifact_id=artifact_id,
            book_id=artifact.book_id,
            speaker_persona_id=request.speaker_persona_id or artifact.speaker_persona_id,
            audience_persona_id=request.audience_persona_id or artifact.audience_persona_id,
            metrics=request.metrics,
            issues=request.issues,
            suggestions=request.suggestions
        )

        db_report = create_diagnostic_report(db, report)

        return {
            "code": 200,
            "message": "诊断报告创建成功",
            "data": {
                "report_id": db_report.report_id,
                "artifact_id": db_report.artifact_id
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 创建诊断报告失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{artifact_id}/diagnostics", summary="获取诊断报告列表")
async def list_reports(artifact_id: str, db: Session = Depends(get_db)):
    """获取输出内容对应的诊断报告"""
    try:
        reports = get_reports_by_artifact(db, artifact_id)

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "reports": [
                    {
                        "report_id": r.report_id,
                        "artifact_id": r.artifact_id,
                        "book_id": r.book_id,
                        "speaker_persona_id": r.speaker_persona_id,
                        "audience_persona_id": r.audience_persona_id,
                        "metrics": r.metrics,
                        "issues": r.issues,
                        "suggestions": r.suggestions,
                        "created_at": r.created_at.isoformat() if r.created_at else None
                    }
                    for r in reports
                ]
            }
        }

    except Exception as e:
        logger.error(f"❌ 获取诊断报告列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/diagnostics/{report_id}", summary="获取诊断报告详情")
async def get_report_detail(report_id: str, db: Session = Depends(get_db)):
    """获取诊断报告详情"""
    try:
        report = get_diagnostic_report(db, report_id)
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
        logger.error(f"❌ 获取诊断报告详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
