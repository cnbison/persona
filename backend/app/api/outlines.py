"""
提纲管理API
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from loguru import logger
from typing import List, Optional
import uuid

from app.database import get_db
from app.models.orm import BookSeriesORM, EpisodeOutlineORM, BookORM, AuthorPersonaORM
from app.services.outline_generator import OutlineGenerator

router = APIRouter()


class GenerateOutlineRequest(BaseModel):
    """生成提纲请求"""
    book_id: str = Field(..., description="著作ID")
    persona_id: Optional[str] = Field(None, description="Persona ID（可选）")


@router.get("/", summary="获取提纲列表")
async def get_outlines(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    获取所有提纲列表（分页）

    返回已生成的10集提纲
    """
    try:
        # 查询所有系列
        series_list = db.query(BookSeriesORM).offset(skip).limit(limit).all()

        # 获取总数
        total = db.query(BookSeriesORM).count()

        # 转换为响应格式
        outlines = []
        for series in series_list:
            # 获取该系列的10集提纲
            episodes = db.query(EpisodeOutlineORM).filter(
                EpisodeOutlineORM.series_id == series.series_id
            ).order_by(EpisodeOutlineORM.episode_number).all()

            outlines.append({
                "series_id": series.series_id,
                "book_id": series.book_id,
                "book_title": series.book_title or "",
                "author_name": series.author_name or "",
                "title": series.book_title or "未命名系列",  # 使用book_title作为title
                "description": f"基于《{series.book_title}》的{series.total_episodes}集对话节目",
                "total_episodes": series.total_episodes,
                "episodes_count": len(episodes),
                "created_at": series.created_at.isoformat() if series.created_at else None,
                "updated_at": series.updated_at.isoformat() if series.updated_at else None
            })

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "outlines": outlines,
                "total": total
            }
        }

    except Exception as e:
        logger.error(f"❌ 获取提纲列表失败: {e}")
        return {
            "code": 500,
            "message": str(e),
            "data": {"outlines": [], "total": 0}
        }


@router.post("/generate", summary="生成10集提纲")
async def generate_outline(
    request: GenerateOutlineRequest,
    db: Session = Depends(get_db)
):
    """
    生成10集节目提纲

    基于著作和Persona生成完整的10集结构
    """
    try:
        logger.info(f"📝 开始生成提纲: book_id={request.book_id}, persona_id={request.persona_id}")

        # 1. 查询著作
        book = db.query(BookORM).filter(BookORM.book_id == request.book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="著作不存在")

        logger.info(f"  找到著作: {book.title}")

        # 2. 查询Persona（如果提供）
        persona = None
        if request.persona_id:
            persona = db.query(AuthorPersonaORM).filter(
                AuthorPersonaORM.persona_id == request.persona_id
            ).first()
            if persona:
                logger.info(f"  找到Persona: {persona.author_name}")
            else:
                logger.warning(f"  Persona不存在: {request.persona_id}")

        # 3. 检查是否已有提纲
        existing = db.query(BookSeriesORM).filter(
            BookSeriesORM.book_id == request.book_id
        ).first()

        if existing:
            logger.info(f"  提纲已存在: {existing.series_id}")
            return {
                "code": 200,
                "message": "提纲已存在",
                "data": {
                    "outline_id": existing.series_id,
                    "series_id": existing.series_id,
                    "status": existing.completion_status
                }
            }

        # 4. 调用提纲生成服务
        outline_generator = OutlineGenerator()

        # 构建Book和AuthorPersona对象
        from app.models.book import Book, Chapter, CoreViewpoint
        from app.models.persona import AuthorPersona, ThinkingStyle

        # 加载章节和观点数据
        from app.models.orm import ChapterORM, CoreViewpointORM

        chapters_orm = db.query(ChapterORM).filter(
            ChapterORM.book_id == book.book_id
        ).order_by(ChapterORM.chapter_number).all()

        viewpoints_orm = db.query(CoreViewpointORM).filter(
            CoreViewpointORM.book_id == book.book_id
        ).limit(20).all()

        # 构建Chapter对象列表
        chapters = []
        for chapter_orm in chapters_orm:
            chapters.append(Chapter(
                chapter_id=chapter_orm.chapter_id,
                chapter_number=chapter_orm.chapter_number,
                title=chapter_orm.title,
                content=chapter_orm.content,
                page_range=chapter_orm.page_range
            ))

        # 构建CoreViewpoint对象列表
        viewpoints = []
        for vp_orm in viewpoints_orm:
            viewpoints.append(CoreViewpoint(
                viewpoint_id=vp_orm.viewpoint_id,
                content=vp_orm.content,
                original_text=vp_orm.original_text,
                chapter_id=vp_orm.chapter_id,
                context=vp_orm.context or "",
                keywords=vp_orm.keywords or []
            ))

        temp_book = Book(
            book_id=book.book_id,
            title=book.title,
            author=book.author,
            language=book.language or "zh",
            file_path=book.file_path,
            file_type=book.file_type,
            total_words=book.total_words or 0,
            chapters=chapters,
            core_viewpoints=viewpoints
        )

        temp_persona = None
        if persona:
            temp_persona = AuthorPersona(
                persona_id=persona.persona_id,
                book_id=persona.book_id,
                author_name=persona.author_name,
                thinking_style=ThinkingStyle(persona.thinking_style) if persona.thinking_style else ThinkingStyle.ANALYTICAL,
                logic_pattern=persona.logic_pattern or "",
                reasoning_framework=persona.reasoning_framework or "",
                core_philosophy=persona.core_philosophy or "",
                theoretical_framework=persona.theoretical_framework or "",
                key_concepts=persona.key_concepts or {},
                narrative_style=persona.narrative_style or "",
                language_rhythm=persona.language_rhythm or "",
                sentence_structure=persona.sentence_structure or "",
                rhetorical_devices=persona.rhetorical_devices or [],
                value_orientation=persona.value_orientation or "",
                value_judgment_framework=persona.value_judgment_framework or "",
                core_positions=persona.core_positions or [],
                opposed_positions=persona.opposed_positions or [],
                tone=persona.tone or "",
                emotion_tendency=persona.emotion_tendency or "",
                expressiveness=persona.expressiveness or "",
                personality_traits=persona.personality_traits or [],
                communication_style=persona.communication_style or "",
                attitude_toward_audience=persona.attitude_toward_audience or ""
            )

        # 生成提纲
        book_series = await outline_generator.generate_outline(
            book=temp_book,
            persona=temp_persona,
            episodes_count=10
        )

        logger.info(f"  提纲生成完成: {book_series.series_id}")

        # 5. 保存到数据库
        # 5.1 保存系列
        db_series = BookSeriesORM(
            series_id=book_series.series_id,
            book_id=book_series.book_id,
            persona_id=persona.persona_id if persona else None,
            book_title=book_series.book_title,
            author_name=book_series.author_name,
            total_episodes=book_series.total_episodes,
            completion_status="completed"
        )

        db.add(db_series)
        db.flush()  # 获取series_id但不提交

        # 5.2 保存每一集
        for episode in book_series.outlines:
            # 将hot_topics中的HotTopicMatch对象转换为字典
            hot_topics_dict = [
                {
                    "topic_title": ht.topic_title,
                    "topic_description": ht.topic_description,
                    "relevance_score": ht.relevance_score,
                    "connection_point": ht.connection_point
                }
                for ht in episode.hot_topics
            ]

            db_episode = EpisodeOutlineORM(
                outline_id=episode.outline_id,
                series_id=db_series.series_id,
                book_id=book.book_id,
                episode_number=episode.episode_number,
                theme=episode.theme,
                target_chapters=episode.target_chapters,
                target_viewpoints=[],  # TODO: 从episode.target_viewpoints映射
                discussion_points=episode.discussion_points,
                hot_topics=hot_topics_dict,
                flow_design=episode.flow_design,
                estimated_duration=episode.estimated_duration
            )
            db.add(db_episode)

        db.commit()

        logger.info(f"  ✅ 提纲已保存到数据库")
        logger.info(f"  保存了 {len(book_series.outlines)} 集提纲")

        return {
            "code": 200,
            "message": "提纲生成成功",
            "data": {
                "outline_id": db_series.series_id,
                "series_id": db_series.series_id,
                "status": "completed",
                "episodes_count": len(book_series.outlines)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 生成提纲失败: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{outline_id}", summary="获取完整提纲")
async def get_outline(outline_id: str, db: Session = Depends(get_db)):
    """
    获取完整的10集提纲

    包含每集的主题、章节分配、热点匹配
    """
    try:
        # 查询系列
        series = db.query(BookSeriesORM).filter(
            BookSeriesORM.series_id == outline_id
        ).first()

        if not series:
            return {
                "code": 404,
                "message": "提纲不存在",
                "data": None
            }

        # 查询所有集数
        episodes = db.query(EpisodeOutlineORM).filter(
            EpisodeOutlineORM.series_id == series.series_id
        ).order_by(EpisodeOutlineORM.episode_number).all()

        # 构建响应数据
        outline_data = {
            "series_id": series.series_id,
            "book_id": series.book_id,
            "book_title": series.book_title or "",
            "author_name": series.author_name or "",
            "title": series.book_title or "未命名系列",  # 使用book_title作为title
            "description": f"基于《{series.book_title}》的{series.total_episodes}集对话节目",
            "total_episodes": series.total_episodes,
            "episodes": []
        }

        for episode in episodes:
            outline_data["episodes"].append({
                "outline_id": episode.outline_id,
                "episode_number": episode.episode_number,
                "theme": episode.theme or "",
                "target_chapters": episode.target_chapters or [],
                "target_viewpoints": episode.target_viewpoints or [],
                "discussion_points": episode.discussion_points or [],
                "hot_topics": episode.hot_topics or [],
                "flow_design": episode.flow_design or {},
                "estimated_duration": episode.estimated_duration
            })

        return {
            "code": 200,
            "message": "获取成功",
            "data": outline_data
        }

    except Exception as e:
        logger.error(f"❌ 获取提纲详情失败: {e}")
        return {
            "code": 500,
            "message": str(e),
            "data": None
        }


@router.delete("/{outline_id}", summary="删除提纲")
async def delete_outline(
    outline_id: str,
    db: Session = Depends(get_db)
):
    """
    删除提纲（包括所有集数）

    参数:
        outline_id: 提纲ID（series_id）
    """
    try:
        # 查询系列
        series = db.query(BookSeriesORM).filter(
            BookSeriesORM.series_id == outline_id
        ).first()

        if not series:
            raise HTTPException(status_code=404, detail="提纲不存在")

        logger.info(f"🗑️  删除提纲: {outline_id}")

        # 先删除所有集数
        deleted_episodes = db.query(EpisodeOutlineORM).filter(
            EpisodeOutlineORM.series_id == outline_id
        ).delete()

        # 再删除系列
        db.delete(series)
        db.commit()

        logger.info(f"  ✅ 已删除 {deleted_episodes} 集提纲")

        return {
            "code": 200,
            "message": "删除成功",
            "data": {
                "deleted_episodes": deleted_episodes
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 删除提纲失败: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{outline_id}/episodes/{episode_number}", summary="更新单集提纲")
async def update_episode(
    outline_id: str,
    episode_number: int,
    db: Session = Depends(get_db)
):
    """
    更新单集提纲内容

    支持修改主题、热点、讨论重点
    """
    # TODO: 实现更新提纲逻辑
    return {
        "code": 200,
        "message": "功能开发中",
        "data": {}
    }
