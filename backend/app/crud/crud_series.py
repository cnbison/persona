"""
Persona和Series的CRUD操作
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from loguru import logger

from app.models.orm import AuthorPersonaORM, BookSeriesORM, EpisodeOutlineORM, EpisodeScriptORM
from app.models.persona import AuthorPersona
from app.models.dialogue import BookSeries, EpisodeOutline, HotTopicMatch, EpisodeScript, DialogueTurn, DialogueRole


def create_persona(db: Session, persona: AuthorPersona, era: str = "", identity: str = "") -> AuthorPersonaORM:
    """
    创建Persona记录

    参数:
        db: 数据库会话
        persona: Pydantic Persona对象
        era: 时代
        identity: 身份

    返回:
        AuthorPersonaORM对象
    """
    db_persona = AuthorPersonaORM(
        persona_id=persona.persona_id,
        book_id=persona.book_id,
        author_name=persona.author_name,

        # 思维方式
        thinking_style=persona.thinking_style.value if hasattr(persona.thinking_style, 'value') else str(persona.thinking_style),
        logic_pattern=persona.logic_pattern,
        reasoning_framework=persona.reasoning_framework,

        # 哲学体系
        core_philosophy=persona.core_philosophy,
        theoretical_framework=persona.theoretical_framework,
        key_concepts=persona.key_concepts,

        # 叙事风格
        narrative_style=persona.narrative_style,
        language_rhythm=persona.language_rhythm,
        sentence_structure=persona.sentence_structure,
        rhetorical_devices=persona.rhetorical_devices,

        # 价值观
        value_orientation=persona.value_orientation,
        value_judgment_framework=persona.value_judgment_framework,
        core_positions=persona.core_positions,
        opposed_positions=persona.opposed_positions,

        # 语气和性格
        tone=persona.tone,
        emotion_tendency=persona.emotion_tendency,
        expressiveness=persona.expressiveness,
        personality_traits=persona.personality_traits,
        communication_style=persona.communication_style,
        attitude_toward_audience=persona.attitude_toward_audience,

        # 元数据
        era=era,
        identity=identity
    )

    db.add(db_persona)
    db.commit()
    db.refresh(db_persona)

    logger.info(f"✅ 创建Persona成功: {persona.author_name}")

    return db_persona


def get_persona(db: Session, persona_id: str) -> Optional[AuthorPersonaORM]:
    """获取Persona"""
    return db.query(AuthorPersonaORM).filter(AuthorPersonaORM.persona_id == persona_id).first()


def create_book_series(db: Session, series: BookSeries, persona_id: Optional[str] = None) -> BookSeriesORM:
    """
    创建著作合集记录

    参数:
        db: 数据库会话
        series: Pydantic BookSeries对象
        persona_id: Persona ID（可选）

    返回:
        BookSeriesORM对象
    """
    db_series = BookSeriesORM(
        series_id=series.series_id,
        book_id=series.book_id,
        persona_id=persona_id,
        book_title=series.book_title,
        author_name=series.author_name,
        total_episodes=series.total_episodes,
        total_duration=series.total_duration,
        completion_status=series.completion_status
    )

    db.add(db_series)
    db.commit()
    db.refresh(db_series)

    # 创建各集提纲记录
    for outline in series.outlines:
        # 转换HotTopicMatch对象为字典
        hot_topics_dict = [
            {
                "topic_title": ht.topic_title,
                "topic_description": ht.topic_description,
                "relevance_score": ht.relevance_score,
                "connection_point": ht.connection_point
            }
            for ht in outline.hot_topics
        ]

        db_outline = EpisodeOutlineORM(
            outline_id=outline.outline_id,
            series_id=series.series_id,
            book_id=series.book_id,
            episode_number=outline.episode_number,
            theme=outline.theme,
            target_chapters=outline.target_chapters,
            target_viewpoints=outline.target_viewpoints,
            discussion_points=outline.discussion_points,
            hot_topics=hot_topics_dict,
            flow_design=outline.flow_design,
            estimated_duration=outline.estimated_duration
        )

        db.add(db_outline)

    db.commit()
    logger.info(f"✅ 创建著作合集成功: {series.book_title} ({len(series.outlines)}集)")

    return db_series


def get_book_series(db: Session, series_id: str) -> Optional[BookSeriesORM]:
    """获取著作合集"""
    return db.query(BookSeriesORM).filter(BookSeriesORM.series_id == series_id).first()


def get_all_series(db: Session, skip: int = 0, limit: int = 10) -> List[BookSeriesORM]:
    """获取所有著作合集"""
    return db.query(BookSeriesORM).offset(skip).limit(limit).all()


def update_series_status(db: Session, series_id: str, status: str) -> Optional[BookSeriesORM]:
    """更新合集状态"""
    db_series = db.query(BookSeriesORM).filter(BookSeriesORM.series_id == series_id).first()
    if db_series:
        db_series.completion_status = status
        db.commit()
        db.refresh(db_series)
        logger.info(f"✅ 更新合集状态: {series_id} -> {status}")
        return db_series
    return None


# ==================== 脚本CRUD操作 ====================

def create_episode_script(db: Session, script: EpisodeScript) -> EpisodeScriptORM:
    """
    创建单集脚本记录

    参数:
        db: 数据库会话
        script: Pydantic EpisodeScript对象

    返回:
        EpisodeScriptORM对象
    """
    # 转换DialogueTurn对象为字典
    dialogue_turns_dict = [
        {
            "turn_id": turn.turn_id,
            "role": turn.role.value if hasattr(turn.role, 'value') else str(turn.role),
            "content": turn.content,
            "original_text_ref": turn.original_text_ref,
            "viewpoint_ref": turn.viewpoint_ref,
            "hot_topic_ref": turn.hot_topic_ref,
            "duration_seconds": turn.duration_seconds,
            "word_count": turn.word_count,
            "quality_score": turn.quality_score
        }
        for turn in script.dialogue_turns
    ]

    db_script = EpisodeScriptORM(
        script_id=script.script_id,
        outline_id=script.outline_id,
        book_id=script.book_id,
        episode_number=script.episode_number,
        title=script.title,
        theme=script.theme,
        dialogue_turns=dialogue_turns_dict,
        total_duration=script.total_duration,
        total_word_count=script.total_word_count,
        author_speaking_ratio=script.author_speaking_ratio,
        host_speaking_ratio=script.host_speaking_ratio,
        quality_metrics=script.quality_metrics,
        generation_time=script.generation_time,
        version=script.version
    )

    db.add(db_script)
    db.commit()
    db.refresh(db_script)

    logger.info(f"✅ 创建脚本成功: {script.title} (集数{script.episode_number})")

    return db_script


def get_episode_script(db: Session, script_id: str) -> Optional[EpisodeScriptORM]:
    """获取单集脚本"""
    return db.query(EpisodeScriptORM).filter(EpisodeScriptORM.script_id == script_id).first()


def get_scripts_by_outline(db: Session, outline_id: str) -> List[EpisodeScriptORM]:
    """根据提纲ID获取所有脚本"""
    return db.query(EpisodeScriptORM).filter(EpisodeScriptORM.outline_id == outline_id).all()


def get_scripts_by_book(db: Session, book_id: str) -> List[EpisodeScriptORM]:
    """根据著作ID获取所有脚本"""
    return db.query(EpisodeScriptORM).filter(EpisodeScriptORM.book_id == book_id).all()


def get_all_scripts(db: Session, skip: int = 0, limit: int = 10) -> List[EpisodeScriptORM]:
    """获取所有脚本（分页）"""
    return db.query(EpisodeScriptORM).offset(skip).limit(limit).all()


def update_script_quality_metrics(
    db: Session,
    script_id: str,
    quality_metrics: dict
) -> Optional[EpisodeScriptORM]:
    """更新脚本质量评估"""
    db_script = db.query(EpisodeScriptORM).filter(EpisodeScriptORM.script_id == script_id).first()
    if db_script:
        db_script.quality_metrics = quality_metrics
        db.commit()
        db.refresh(db_script)
        logger.info(f"✅ 更新脚本质量评估: {script_id}")
        return db_script
    return None


def delete_script(db: Session, script_id: str) -> bool:
    """删除脚本"""
    db_script = db.query(EpisodeScriptORM).filter(EpisodeScriptORM.script_id == script_id).first()
    if db_script:
        db.delete(db_script)
        db.commit()
        logger.info(f"✅ 删除脚本: {script_id}")
        return True
    return False

