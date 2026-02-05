"""
Persona管理API
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from loguru import logger
from typing import Dict, Any
import uuid

from app.database import get_db
from app.models.orm import AuthorPersonaORM, BookORM
from app.crud.crud_series import create_persona, get_persona as get_persona_by_id
from app.services.persona_builder import get_persona_builder
from app.services.evidence_linker import get_evidence_linker

router = APIRouter()


class CreatePersonaRequest(BaseModel):
    """创建Persona请求"""
    book_id: str = Field(..., description="著作ID")


class CreatePersonaResponse(BaseModel):
    """创建Persona响应"""
    persona_id: str
    book_id: str
    author_name: str
    status: str


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


@router.post("/{persona_id}/generate-prompt", summary="生成System Prompt")
async def generate_system_prompt(persona_id: str, db: Session = Depends(get_db)):
    """
    为Persona生成System Prompt

    用于对话生成时的角色指令
    """
    try:
        # 从数据库查询Persona
        db_persona = get_persona_by_id(db, persona_id)

        if not db_persona:
            raise HTTPException(status_code=404, detail="Persona不存在")

        # 如果已有system_prompt，直接返回
        if db_persona.system_prompt:
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
            attitude_toward_audience=db_persona.attitude_toward_audience or ""
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
