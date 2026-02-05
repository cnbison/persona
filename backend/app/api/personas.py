"""
Persona管理API
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from loguru import logger
from typing import Dict, Any, Optional
import uuid

from app.database import get_db
from app.models.orm import AuthorPersonaORM, BookORM
from app.crud.crud_series import create_persona, get_persona as get_persona_by_id
from app.services.persona_builder import get_persona_builder
from app.services.evidence_linker import get_evidence_linker
from app.services.persona_card import build_persona_card

router = APIRouter()


def _bump_version(version: Optional[str]) -> str:
    if not version:
        return "1.1"
    parts = version.split(".")
    if len(parts) == 1 and parts[0].isdigit():
        return f"{parts[0]}.1"
    if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
        major = int(parts[0])
        minor = int(parts[1]) + 1
        return f"{major}.{minor}"
    return f"{version}.1"


def _build_persona_from_payload(payload: Dict[str, Any], persona_id: str, version: str) -> AuthorPersonaORM:
    return AuthorPersonaORM(
        persona_id=persona_id,
        book_id=payload.get("book_id") or "",
        author_name=payload.get("author_name") or "",
        thinking_style=payload.get("thinking_style") or "analytical",
        logic_pattern=payload.get("logic_pattern") or "",
        reasoning_framework=payload.get("reasoning_framework") or "",
        core_philosophy=payload.get("core_philosophy") or "",
        theoretical_framework=payload.get("theoretical_framework") or "",
        key_concepts=payload.get("key_concepts") or {},
        narrative_style=payload.get("narrative_style") or "",
        language_rhythm=payload.get("language_rhythm") or "",
        sentence_structure=payload.get("sentence_structure") or "",
        rhetorical_devices=payload.get("rhetorical_devices") or [],
        value_orientation=payload.get("value_orientation") or "",
        value_judgment_framework=payload.get("value_judgment_framework") or "",
        core_positions=payload.get("core_positions") or [],
        opposed_positions=payload.get("opposed_positions") or [],
        tone=payload.get("tone") or "",
        emotion_tendency=payload.get("emotion_tendency") or "",
        expressiveness=payload.get("expressiveness") or "",
        personality_traits=payload.get("personality_traits") or [],
        communication_style=payload.get("communication_style") or "",
        attitude_toward_audience=payload.get("attitude_toward_audience") or "",
        system_prompt=payload.get("system_prompt"),
        era=payload.get("era"),
        identity=payload.get("identity"),
        version=version,
        evidence_links=payload.get("evidence_links") or []
    )


class CreatePersonaRequest(BaseModel):
    """创建Persona请求"""
    book_id: str = Field(..., description="著作ID")


class CreatePersonaResponse(BaseModel):
    """创建Persona响应"""
    persona_id: str
    book_id: str
    author_name: str
    status: str


class PersonaDiffRequest(BaseModel):
    """Persona对比请求"""
    source_id: str = Field(..., description="基准Persona ID")
    target_id: str = Field(..., description="对比Persona ID")


class ImportPersonaRequest(BaseModel):
    """导入Persona请求"""
    mode: str = Field(default="new_version", description="导入模式: new/new_version/overwrite")
    persona: Dict[str, Any] = Field(..., description="Persona JSON内容")


class CreatePersonaVersionRequest(BaseModel):
    """创建Persona新版本请求"""
    version: Optional[str] = Field(default=None, description="指定版本号（可选）")


@router.post("/", summary="创建Persona")
async def create_persona(
    request: CreatePersonaRequest,
    db: Session = Depends(get_db)
):
    """
    创建作者Persona

    基于著作分析生成6维度人格特征
    """
    try:
        logger.info(f"🎭 开始构建Persona: book_id={request.book_id}")

        # 1. 检查著作是否存在
        book = db.query(BookORM).filter(
            BookORM.book_id == request.book_id
        ).first()

        if not book:
            raise HTTPException(status_code=404, detail="著作不存在")

        logger.info(f"  找到著作: {book.title} by {book.author}")

        # 2. 检查是否已存在Persona
        existing = db.query(AuthorPersonaORM).filter(
            AuthorPersonaORM.book_id == request.book_id
        ).first()

        if existing:
            logger.info(f"  Persona已存在: {existing.persona_id}")
            return {
                "code": 200,
                "message": "Persona已存在",
                "data": {
                    "persona_id": existing.persona_id,
                    "book_id": existing.book_id,
                    "author_name": existing.author_name,
                    "status": "exists"
                }
            }

        # 3. 调用Persona构建服务
        persona_builder = get_persona_builder()

        # 构建临时的Book对象（用于persona_builder）
        from app.models.book import Book
        temp_book = Book(
            book_id=book.book_id,
            title=book.title,
            author=book.author,
            language=book.language or "zh",
            file_path=book.file_path or "",
            file_type=book.file_type or "unknown",
            total_words=book.total_words or 0,
            total_chapters=book.total_chapters or 0,
            total_viewpoints=book.total_viewpoints or 0
        )

        # 构建Persona
        author_persona = await persona_builder.build_persona(
            book=temp_book,
            era="根据著作背景推断",
            identity="作者"
        )

        logger.info(f"  Persona构建完成: {author_persona.persona_id}")

        # 4. 保存到数据库 - 直接使用ORM
        # 处理thinking_style枚举
        thinking_style_str = str(author_persona.thinking_style.value) if hasattr(author_persona.thinking_style, 'value') else str(author_persona.thinking_style)

        db_persona = AuthorPersonaORM(
            persona_id=author_persona.persona_id,
            book_id=author_persona.book_id,
            author_name=author_persona.author_name,

            # 思维方式
            thinking_style=thinking_style_str,
            logic_pattern=author_persona.logic_pattern or "",
            reasoning_framework=author_persona.reasoning_framework or "",

            # 哲学体系
            core_philosophy=author_persona.core_philosophy or "",
            theoretical_framework=author_persona.theoretical_framework or "",
            key_concepts=author_persona.key_concepts or {},

            # 叙事风格
            narrative_style=author_persona.narrative_style or "",
            language_rhythm=author_persona.language_rhythm or "",
            sentence_structure=author_persona.sentence_structure or "",
            rhetorical_devices=author_persona.rhetorical_devices or [],

            # 价值观
            value_orientation=author_persona.value_orientation or "",
            value_judgment_framework=author_persona.value_judgment_framework or "",
            core_positions=author_persona.core_positions or [],
            opposed_positions=author_persona.opposed_positions or [],

            # 语气和性格
            tone=author_persona.tone or "",
            emotion_tendency=author_persona.emotion_tendency or "",
            expressiveness=author_persona.expressiveness or "",
            personality_traits=author_persona.personality_traits or [],
            communication_style=author_persona.communication_style or "",
            attitude_toward_audience=author_persona.attitude_toward_audience or "",

            # System Prompt（可选）
            system_prompt=None,  # 稍后生成

            # 元数据
            era="根据著作背景推断",
            identity="作者"
        )

        db.add(db_persona)
        db.commit()
        db.refresh(db_persona)

        logger.info(f"  Persona已保存到数据库: {db_persona.persona_id}")

        return {
            "code": 200,
            "message": "Persona构建成功",
            "data": {
                "persona_id": db_persona.persona_id,
                "book_id": db_persona.book_id,
                "author_name": db_persona.author_name,
                "status": "created"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 创建Persona失败: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", summary="获取Persona列表")
async def list_personas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取Persona列表

    返回所有已创建的作者人格
    """
    try:
        # 查询列表
        personas = db.query(AuthorPersonaORM).offset(skip).limit(limit).all()
        total = db.query(AuthorPersonaORM).count()

        # 转换为响应格式
        persona_list = []
        for db_persona in personas:
            persona_list.append({
                "persona_id": db_persona.persona_id,
                "book_id": db_persona.book_id,
                "author_name": db_persona.author_name or "",
                "thinking_style": db_persona.thinking_style or "analytical",
                "tone": db_persona.tone or "",
                "version": db_persona.version or "1.0",
                "created_at": db_persona.created_at.isoformat() if db_persona.created_at else None
            })

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "items": persona_list,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        }

    except Exception as e:
        logger.error(f"❌ 获取Persona列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{persona_id}", summary="获取Persona详情")
async def get_persona(persona_id: str, db: Session = Depends(get_db)):
    """
    获取Persona详细信息

    包含6维度特征和System Prompt
    """
    try:
        # 从数据库查询
        db_persona = get_persona_by_id(db, persona_id)

        if not db_persona:
            raise HTTPException(status_code=404, detail="Persona不存在")

        # 自动补齐证据链接（若为空）
        if not db_persona.evidence_links:
            linker = get_evidence_linker()
            db_persona.evidence_links = linker.build_links(db, db_persona)
            db.commit()

        # 转换为响应格式
        persona_data = {
            "persona_id": db_persona.persona_id,
            "book_id": db_persona.book_id,
            "author_name": db_persona.author_name or "",
            "thinking_style": db_persona.thinking_style or "analytical",
            "logic_pattern": db_persona.logic_pattern or "",
            "reasoning_framework": db_persona.reasoning_framework or "",
            "core_philosophy": db_persona.core_philosophy or "",
            "theoretical_framework": db_persona.theoretical_framework or "",
            "key_concepts": db_persona.key_concepts or {},
            "narrative_style": db_persona.narrative_style or "",
            "language_rhythm": db_persona.language_rhythm or "",
            "sentence_structure": db_persona.sentence_structure or "",
            "rhetorical_devices": db_persona.rhetorical_devices or [],
            "value_orientation": db_persona.value_orientation or "",
            "value_judgment_framework": db_persona.value_judgment_framework or "",
            "core_positions": db_persona.core_positions or [],
            "opposed_positions": db_persona.opposed_positions or [],
            "tone": db_persona.tone or "",
            "emotion_tendency": db_persona.emotion_tendency or "",
            "expressiveness": db_persona.expressiveness or "",
            "personality_traits": db_persona.personality_traits or [],
            "communication_style": db_persona.communication_style or "",
            "attitude_toward_audience": db_persona.attitude_toward_audience or "",
            "system_prompt": db_persona.system_prompt,
            "version": db_persona.version or "1.0",
            "evidence_links": db_persona.evidence_links or []
        }

        return {
            "code": 200,
            "message": "获取成功",
            "data": persona_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取Persona失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{persona_id}/card", summary="生成Persona卡片摘要")
async def get_persona_card(persona_id: str, db: Session = Depends(get_db)):
    """生成Persona卡片摘要（不落库）"""
    try:
        db_persona = get_persona_by_id(db, persona_id)
        if not db_persona:
            raise HTTPException(status_code=404, detail="Persona不存在")

        # 自动补齐证据链接（若为空）
        if not db_persona.evidence_links:
            linker = get_evidence_linker()
            db_persona.evidence_links = linker.build_links(db, db_persona)
            db.commit()

        card = build_persona_card(db_persona)

        return {
            "code": 200,
            "message": "生成成功",
            "data": card
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Persona卡片生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import", summary="导入Persona")
async def import_persona(
    request: ImportPersonaRequest,
    db: Session = Depends(get_db)
):
    """导入Persona配置"""
    try:
        payload = request.persona or {}
        if not payload.get("book_id"):
            raise HTTPException(status_code=400, detail="book_id缺失")
        if not payload.get("author_name"):
            raise HTTPException(status_code=400, detail="author_name缺失")

        book = db.query(BookORM).filter(BookORM.book_id == payload.get("book_id")).first()
        if not book:
            raise HTTPException(status_code=404, detail="关联著作不存在")

        incoming_id = payload.get("persona_id")
        incoming_version = payload.get("version") or "1.0"

        if request.mode == "overwrite" and incoming_id:
            existing = db.query(AuthorPersonaORM).filter(AuthorPersonaORM.persona_id == incoming_id).first()
            if not existing:
                raise HTTPException(status_code=404, detail="待覆盖Persona不存在")

            version = incoming_version
            updated = _build_persona_from_payload(payload, incoming_id, version)
            for field in updated.__dict__:
                if field.startswith("_"):
                    continue
                setattr(existing, field, getattr(updated, field))
            db.commit()
            return {
                "code": 200,
                "message": "覆盖导入成功",
                "data": {
                    "persona_id": existing.persona_id,
                    "version": existing.version
                }
            }

        new_persona_id = uuid.uuid4().hex
        version = incoming_version
        if request.mode == "new_version":
            version = _bump_version(incoming_version)

        db_persona = _build_persona_from_payload(payload, new_persona_id, version)
        db.add(db_persona)
        db.commit()
        db.refresh(db_persona)

        return {
            "code": 200,
            "message": "导入成功",
            "data": {
                "persona_id": db_persona.persona_id,
                "version": db_persona.version
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 导入Persona失败: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{persona_id}/versions", summary="创建Persona新版本")
async def create_persona_version(
    persona_id: str,
    request: CreatePersonaVersionRequest,
    db: Session = Depends(get_db)
):
    """基于现有Persona创建新版本"""
    try:
        source = get_persona_by_id(db, persona_id)
        if not source:
            raise HTTPException(status_code=404, detail="Persona不存在")

        new_id = uuid.uuid4().hex
        version = request.version or _bump_version(source.version or "1.0")

        payload = {
            "book_id": source.book_id,
            "author_name": source.author_name,
            "thinking_style": source.thinking_style,
            "logic_pattern": source.logic_pattern,
            "reasoning_framework": source.reasoning_framework,
            "core_philosophy": source.core_philosophy,
            "theoretical_framework": source.theoretical_framework,
            "key_concepts": source.key_concepts,
            "narrative_style": source.narrative_style,
            "language_rhythm": source.language_rhythm,
            "sentence_structure": source.sentence_structure,
            "rhetorical_devices": source.rhetorical_devices,
            "value_orientation": source.value_orientation,
            "value_judgment_framework": source.value_judgment_framework,
            "core_positions": source.core_positions,
            "opposed_positions": source.opposed_positions,
            "tone": source.tone,
            "emotion_tendency": source.emotion_tendency,
            "expressiveness": source.expressiveness,
            "personality_traits": source.personality_traits,
            "communication_style": source.communication_style,
            "attitude_toward_audience": source.attitude_toward_audience,
            "system_prompt": source.system_prompt,
            "era": source.era,
            "identity": source.identity,
            "evidence_links": source.evidence_links
        }

        db_persona = _build_persona_from_payload(payload, new_id, version)
        db.add(db_persona)
        db.commit()
        db.refresh(db_persona)

        return {
            "code": 200,
            "message": "新版本创建成功",
            "data": {
                "persona_id": db_persona.persona_id,
                "version": db_persona.version
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 创建Persona新版本失败: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/diff", summary="Persona版本对比")
async def diff_persona(
    request: PersonaDiffRequest,
    db: Session = Depends(get_db)
):
    """对比两个Persona的字段差异"""
    try:
        source = get_persona_by_id(db, request.source_id)
        target = get_persona_by_id(db, request.target_id)
        if not source or not target:
            raise HTTPException(status_code=404, detail="Persona不存在")

        diff_fields = [
            "thinking_style",
            "logic_pattern",
            "reasoning_framework",
            "core_philosophy",
            "theoretical_framework",
            "key_concepts",
            "narrative_style",
            "language_rhythm",
            "sentence_structure",
            "rhetorical_devices",
            "value_orientation",
            "value_judgment_framework",
            "core_positions",
            "opposed_positions",
            "tone",
            "emotion_tendency",
            "expressiveness",
            "personality_traits",
            "communication_style",
            "attitude_toward_audience",
            "version"
        ]

        changes = []
        for field in diff_fields:
            a_value = getattr(source, field, None)
            b_value = getattr(target, field, None)
            if a_value != b_value:
                changes.append({
                    "field": field,
                    "source": a_value,
                    "target": b_value
                })

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "source_id": source.persona_id,
                "target_id": target.persona_id,
                "changes": changes,
                "total_changes": len(changes)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Persona对比失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{persona_id}/generate-prompt", summary="生成System Prompt")
async def generate_system_prompt(
    persona_id: str,
    force: bool = False,
    db: Session = Depends(get_db)
):
    """
    为Persona生成System Prompt

    用于对话生成时的角色指令
    """
    try:
        # 从数据库查询Persona
        db_persona = get_persona_by_id(db, persona_id)

        if not db_persona:
            raise HTTPException(status_code=404, detail="Persona不存在")

        # 如果已有system_prompt，且不强制刷新，直接返回
        if db_persona.system_prompt and not force:
            return {
                "code": 200,
                "message": "System Prompt已存在",
                "data": {
                    "system_prompt": db_persona.system_prompt
                }
            }

        # 生成新的System Prompt
        persona_builder = get_persona_builder()

        # 构建AuthorPersona对象
        from app.models.persona import AuthorPersona, ThinkingStyle
        author_persona = AuthorPersona(
            persona_id=db_persona.persona_id,
            book_id=db_persona.book_id,
            author_name=db_persona.author_name,
            thinking_style=ThinkingStyle(db_persona.thinking_style) if db_persona.thinking_style else ThinkingStyle.ANALYTICAL,
            logic_pattern=db_persona.logic_pattern or "",
            reasoning_framework=db_persona.reasoning_framework or "",
            core_philosophy=db_persona.core_philosophy or "",
            theoretical_framework=db_persona.theoretical_framework or "",
            key_concepts=db_persona.key_concepts or {},
            narrative_style=db_persona.narrative_style or "",
            language_rhythm=db_persona.language_rhythm or "",
            sentence_structure=db_persona.sentence_structure or "",
            rhetorical_devices=db_persona.rhetorical_devices or [],
            value_orientation=db_persona.value_orientation or "",
            value_judgment_framework=db_persona.value_judgment_framework or "",
            core_positions=db_persona.core_positions or [],
            opposed_positions=db_persona.opposed_positions or [],
            tone=db_persona.tone or "",
            emotion_tendency=db_persona.emotion_tendency or "",
            expressiveness=db_persona.expressiveness or "",
            personality_traits=db_persona.personality_traits or [],
            communication_style=db_persona.communication_style or "",
            attitude_toward_audience=db_persona.attitude_toward_audience or "",
            viewpoint_boundaries={
                "core_positions": db_persona.core_positions or [],
                "opposed_positions": db_persona.opposed_positions or [],
                "unmentioned_areas": []
            },
            evidence_links=db_persona.evidence_links or []
        )

        system_prompt = await persona_builder.generate_system_prompt(
            author_persona,
            era="根据著作背景推断",
            identity="作者"
        )

        # 保存到数据库
        db_persona.system_prompt = system_prompt
        db.commit()

        logger.info(f"✅ System Prompt生成完成: {persona_id}")

        return {
            "code": 200,
            "message": "System Prompt生成成功",
            "data": {
                "system_prompt": system_prompt
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 生成System Prompt失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{persona_id}/export", summary="导出Persona JSON")
async def export_persona(persona_id: str, db: Session = Depends(get_db)):
    """
    导出Persona配置（JSON）
    """
    try:
        db_persona = get_persona_by_id(db, persona_id)
        if not db_persona:
            raise HTTPException(status_code=404, detail="Persona不存在")

        export_data = {
            "persona_id": db_persona.persona_id,
            "book_id": db_persona.book_id,
            "author_name": db_persona.author_name or "",
            "thinking_style": db_persona.thinking_style or "analytical",
            "logic_pattern": db_persona.logic_pattern or "",
            "reasoning_framework": db_persona.reasoning_framework or "",
            "core_philosophy": db_persona.core_philosophy or "",
            "theoretical_framework": db_persona.theoretical_framework or "",
            "key_concepts": db_persona.key_concepts or {},
            "narrative_style": db_persona.narrative_style or "",
            "language_rhythm": db_persona.language_rhythm or "",
            "sentence_structure": db_persona.sentence_structure or "",
            "rhetorical_devices": db_persona.rhetorical_devices or [],
            "value_orientation": db_persona.value_orientation or "",
            "value_judgment_framework": db_persona.value_judgment_framework or "",
            "core_positions": db_persona.core_positions or [],
            "opposed_positions": db_persona.opposed_positions or [],
            "tone": db_persona.tone or "",
            "emotion_tendency": db_persona.emotion_tendency or "",
            "expressiveness": db_persona.expressiveness or "",
            "personality_traits": db_persona.personality_traits or [],
            "communication_style": db_persona.communication_style or "",
            "attitude_toward_audience": db_persona.attitude_toward_audience or "",
            "system_prompt": db_persona.system_prompt,
            "version": db_persona.version or "1.0",
            "evidence_links": db_persona.evidence_links or []
        }

        return {
            "code": 200,
            "message": "导出成功",
            "data": export_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 导出Persona失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
