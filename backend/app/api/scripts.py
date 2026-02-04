"""
脚本管理API
"""
from fastapi import APIRouter, Depends, Query, HTTPException, BackgroundTasks, WebSocket
from sqlalchemy.orm import Session
from loguru import logger
from fastapi.responses import FileResponse
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import uuid
import asyncio
import json
from pathlib import Path

from app.database import get_db
from sqlalchemy.orm import sessionmaker
from app.models.dialogue import EpisodeScript, DialogueTurn, DialogueRole
from app.models.orm import EpisodeScriptORM, EpisodeOutlineORM, BookSeriesORM, AuthorPersonaORM, BookORM
from app.crud.crud_series import create_episode_script, get_episode_script
from app.services.dialogue_generator import get_dialogue_generator
from app.api.websocket import manager

router = APIRouter()

# ==================== 全局状态管理 ====================

# 脚本生成进度状态（内存存储）
# 生产环境应该使用Redis或数据库
script_generation_progress: Dict[str, dict] = {}


def update_progress(script_id: str, percentage: int, current_step: str, status: str = "generating", extra_data: dict = None):
    """
    更新生成进度

    参数:
        script_id: 脚本ID
        percentage: 进度百分比
        current_step: 当前步骤
        status: 状态
        extra_data: 额外数据
    """
    # 更新内存状态 - 包含extra_data
    progress_data = {
        "script_id": script_id,
        "percentage": percentage,
        "current_step": current_step,
        "status": status
    }

    # 如果有extra_data，添加到进度数据中
    if extra_data:
        progress_data["extra_data"] = extra_data

    script_generation_progress[script_id] = progress_data

    # 通过WebSocket推送实时进度
    asyncio.create_task(manager.send_progress(
        script_id=script_id,
        percentage=percentage,
        current_step=current_step,
        status=status,
        extra_data=extra_data
    ))

    logger.info(f"📊 脚本生成进度: {script_id} - {percentage}% - {current_step}")


# ==================== 后台任务 ====================

async def generate_script_task(
    script_id: str,
    series_id: str,
    episode_start: int,
    episode_end: int,
    db_session_factory
):
    """
    后台脚本生成任务

    参数:
        script_id: 脚本ID
        series_id: 提纲系列ID
        episode_start: 起始集数
        episode_end: 结束集数
        db_session_factory: 数据库会话工厂
    """
    db = db_session_factory()

    try:
        # 1. 获取系列信息
        logger.info(f"🎙️  开始生成脚本: {script_id}")

        series = db.query(BookSeriesORM).filter(
            BookSeriesORM.series_id == series_id
        ).first()

        if not series:
            raise ValueError(f"系列不存在: {series_id}")

        # 2. 获取Persona
        persona = db.query(AuthorPersonaORM).filter(
            AuthorPersonaORM.persona_id == series.persona_id
        ).first()

        if not persona:
            raise ValueError(f"Persona不存在: {series.persona_id}")

        # 3. 构建Pydantic对象
        from app.models.persona import AuthorPersona, ThinkingStyle
        from app.models.dialogue import EpisodeOutline, HotTopicMatch

        # 构建Persona对象
        author_persona = AuthorPersona(
            persona_id=persona.persona_id,
            book_id=persona.book_id,
            author_name=persona.author_name,
            thinking_style=ThinkingStyle(persona.thinking_style),
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

        # 生成System Prompt
        author_system_prompt = persona.system_prompt or f"你是{persona.author_name}，保持你的思维方式。"
        host_system_prompt = "你是一位专业的播客主持人，负责引导对话、总结观点。"

        # 4. 获取对话生成器
        dialogue_generator = get_dialogue_generator()

        # 5. 逐集生成
        episode_numbers = list(range(episode_start, episode_end + 1))
        total_episodes = len(episode_numbers)
        generated_scripts = []

        for idx, episode_number in enumerate(episode_numbers):
            progress_percentage = int((idx / total_episodes) * 100)
            update_progress(
                script_id,
                progress_percentage,
                f"正在生成第{episode_number}集..."
            )

            # 获取该集的outline
            episode_outline = db.query(EpisodeOutlineORM).filter(
                EpisodeOutlineORM.series_id == series.series_id,
                EpisodeOutlineORM.episode_number == episode_number
            ).first()

            if not episode_outline:
                logger.warning(f"⚠️  第{episode_number}集提纲不存在，跳过")
                continue

            # 构建EpisodeOutline对象
            pydantic_outline = EpisodeOutline(
                outline_id=episode_outline.outline_id,
                book_id=episode_outline.book_id,
                episode_number=episode_outline.episode_number,
                theme=episode_outline.theme,
                target_chapters=episode_outline.target_chapters or [],
                target_viewpoints=episode_outline.target_viewpoints or [],
                hot_topics=[
                    HotTopicMatch(**ht) for ht in (episode_outline.hot_topics or [])
                ],
                discussion_points=episode_outline.discussion_points or [],
                flow_design=episode_outline.flow_design or {},
                estimated_duration=episode_outline.estimated_duration
            )

            # 生成脚本
            script = await dialogue_generator.generate_script(
                outline=pydantic_outline,
                episode_number=episode_number,
                author_persona=author_persona,
                author_system_prompt=author_system_prompt,
                host_system_prompt=host_system_prompt,
                target_duration=30
            )

            # 保存到数据库
            script.outline_id = episode_outline.outline_id
            db_script = create_episode_script(db, script)
            generated_scripts.append(db_script.script_id)

            logger.info(f"✅ 第{episode_number}集脚本生成完成")

        # 6. 完成
        update_progress(
            script_id,
            100,
            f"成功生成{len(generated_scripts)}集脚本",
            status="completed",
            extra_data={"generated_script_ids": generated_scripts}
        )

        logger.info(f"🎉 脚本生成任务完成: {script_id}，共{len(generated_scripts)}集")
        logger.info(f"📝 生成的脚本IDs: {generated_scripts}")

    except Exception as e:
        logger.error(f"❌ 脚本生成失败: {e}")
        update_progress(
            script_id,
            0,
            f"生成失败: {str(e)}",
            status="failed"
        )

    finally:
        db.close()


# ==================== API接口 ====================

class GenerateScriptRequest(BaseModel):
    """生成脚本请求"""
    series_id: str = Field(..., description="提纲系列ID（series_id）")
    episode_start: int = Field(..., ge=1, le=10, description="起始集数")
    episode_end: int = Field(..., ge=1, le=10, description="结束集数")


@router.post("/generate", summary="生成对话脚本")
async def generate_script(
    request: GenerateScriptRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    生成对话脚本

    基于提纲生成"作者+主持人"对话内容

    参数:
    - outline_id: 提纲ID
    - episode_start: 起始集数（1-10）
    - episode_end: 结束集数（1-10）
    """
    try:
        # 1. 验证提纲系列存在
        series = db.query(BookSeriesORM).filter(
            BookSeriesORM.series_id == request.series_id
        ).first()

        if not series:
            raise HTTPException(status_code=404, detail="提纲系列不存在")

        # 2. 查询该系列下的所有集数
        all_episodes = db.query(EpisodeOutlineORM).filter(
            EpisodeOutlineORM.series_id == request.series_id
        ).order_by(EpisodeOutlineORM.episode_number).all()

        if not all_episodes:
            raise HTTPException(status_code=404, detail="该提纲下没有集数数据")

        # 3. 验证集数范围
        if request.episode_start > request.episode_end:
            raise HTTPException(
                status_code=400,
                detail="起始集数不能大于结束集数"
            )

        if request.episode_end > len(all_episodes):
            raise HTTPException(
                status_code=400,
                detail=f"该提纲只有{len(all_episodes)}集，结束集数不能超过{len(all_episodes)}"
            )

        # 4. 生成脚本ID
        script_id = str(uuid.uuid4())

        # 5. 初始化进度
        update_progress(script_id, 0, "任务已启动，正在准备...")

        # 6. 添加后台任务
        # 创建Session工厂用于后台任务
        session_factory = sessionmaker(bind=db.bind)
        background_tasks.add_task(
            generate_script_task,
            script_id,
            request.series_id,
            request.episode_start,
            request.episode_end,
            session_factory
        )

        logger.info(f"✅ 脚本生成任务已启动: {script_id}")

        episode_numbers = list(range(request.episode_start, request.episode_end + 1))

        return {
            "code": 200,
            "message": "脚本生成任务已启动",
            "data": {
                "script_id": script_id,
                "series_id": request.series_id,
                "episode_numbers": episode_numbers,
                "total_episodes": len(episode_numbers)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 启动脚本生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{script_id}/progress", summary="查询生成进度")
async def get_script_progress(script_id: str, db: Session = Depends(get_db)):
    """
    查询脚本生成进度

    实时返回生成百分比和当前步骤
    """
    try:
        # 从全局状态中获取进度
        progress = script_generation_progress.get(script_id)

        if not progress:
            # 检查是否已完成（数据库中存在）
            db_script = db.query(EpisodeScriptORM).filter(
                EpisodeScriptORM.script_id == script_id
            ).first()

            if db_script:
                return {
                    "code": 200,
                    "message": "获取成功",
                    "data": {
                        "script_id": script_id,
                        "percentage": 100,
                        "current_step": "生成完成",
                        "status": "completed"
                    }
                }
            else:
                return {
                    "code": 404,
                    "message": "脚本不存在或任务未启动",
                    "data": None
                }

        return {
            "code": 200,
            "message": "获取成功",
            "data": progress
        }

    except Exception as e:
        logger.error(f"❌ 获取进度失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{script_id}")
async def websocket_script_progress(websocket: WebSocket, script_id: str):
    """
    WebSocket实时进度推送

    连接格式: ws://localhost:8000/api/scripts/ws/{script_id}

    接收消息格式:
    {
        "type": "progress_update" | "log",
        "data": {
            "script_id": "...",
            "percentage": 50,
            "current_step": "正在生成第1集...",
            "status": "generating" | "completed" | "failed"
        }
    }
    """
    await manager.connect(websocket, script_id)

    try:
        # 保持连接活跃，接收客户端的心跳
        while True:
            data = await websocket.receive_text()

            # 处理客户端消息（例如心跳）
            if data == "ping":
                await websocket.send_json({"type": "pong", "data": {"timestamp": asyncio.get_event_loop().time()}})

    except WebSocketDisconnect:
        manager.disconnect(websocket, script_id)
        logger.info(f"🔌 WebSocket断开: script_id={script_id}")
    except Exception as e:
        logger.error(f"❌ WebSocket错误: {e}")
        manager.disconnect(websocket, script_id)


@router.get("", summary="获取脚本列表")
async def get_scripts(
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db)
):
    """
    获取脚本列表

    返回所有已生成的脚本
    """
    try:
        scripts = db.query(EpisodeScriptORM).order_by(
            EpisodeScriptORM.generation_time.desc()
        ).offset(offset).limit(limit).all()

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "scripts": [
                    {
                        "script_id": script.script_id,
                        "outline_id": script.outline_id,
                        "book_id": script.book_id,
                        "episode_number": script.episode_number,
                        "title": script.title,
                        "theme": script.theme,
                        "total_duration": script.total_duration,
                        "total_word_count": script.total_word_count,
                        "author_speaking_ratio": script.author_speaking_ratio,
                        "host_speaking_ratio": script.host_speaking_ratio,
                        "generation_time": script.generation_time.isoformat() if script.generation_time else None,
                        "dialogue_turns_count": len(script.dialogue_turns) if script.dialogue_turns else 0
                    }
                    for script in scripts
                ],
                "total": len(scripts)
            }
        }

    except Exception as e:
        logger.error(f"❌ 获取脚本列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{script_id}", summary="获取脚本内容")
async def get_script(script_id: str, db: Session = Depends(get_db)):
    """
    获取生成的对话脚本

    返回完整的对话内容
    """
    try:
        db_script = get_episode_script(db, script_id)

        if not db_script:
            raise HTTPException(status_code=404, detail="脚本不存在")

        # 转换DialogueTurn
        dialogue_turns = []
        for turn_data in db_script.dialogue_turns:
            turn = DialogueTurn(
                turn_id=turn_data["turn_id"],
                role=DialogueRole(turn_data["role"]),
                content=turn_data["content"],
                original_text_ref=turn_data.get("original_text_ref"),
                viewpoint_ref=turn_data.get("viewpoint_ref"),
                hot_topic_ref=turn_data.get("hot_topic_ref"),
                duration_seconds=turn_data.get("duration_seconds"),
                word_count=turn_data["word_count"],
                quality_score=turn_data.get("quality_score")
            )
            dialogue_turns.append(turn)

        # 构建响应
        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "script_id": db_script.script_id,
                "outline_id": db_script.outline_id,
                "book_id": db_script.book_id,
                "episode_number": db_script.episode_number,
                "title": db_script.title,
                "theme": db_script.theme,
                "dialogue_turns": [
                    {
                        "turn_id": turn.turn_id,
                        "speaker": turn.role.value,
                        "content": turn.content,
                        "original_text_reference": turn.original_text_ref,
                        "hot_topic_reference": turn.hot_topic_ref,
                        "duration_seconds": turn.duration_seconds
                    }
                    for turn in dialogue_turns
                ],
                "statistics": {
                    "total_duration": db_script.total_duration,
                    "total_word_count": db_script.total_word_count,
                    "author_speaking_ratio": db_script.author_speaking_ratio,
                    "host_speaking_ratio": db_script.host_speaking_ratio
                },
                "quality_metrics": db_script.quality_metrics,
                "generation_time": db_script.generation_time.isoformat() if db_script.generation_time else None,
                "version": db_script.version
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取脚本失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{script_id}/export", summary="导出脚本")
async def export_script(
    script_id: str,
    format: str = Query("txt", description="导出格式: txt/md/json"),
    db: Session = Depends(get_db)
):
    """
    导出脚本文件

    支持TXT、Markdown、JSON格式
    """
    try:
        db_script = get_episode_script(db, script_id)

        if not db_script:
            raise HTTPException(status_code=404, detail="脚本不存在")

        # 创建导出目录
        export_dir = Path("./data/exports")
        export_dir.mkdir(exist_ok=True)

        # 生成文件名
        filename = f"{db_script.episode_number:02d}_{db_script.title}.{format}"
        file_path = export_dir / filename

        # 根据格式生成内容
        if format == "txt":
            content = _export_txt(db_script)
        elif format == "md":
            content = _export_markdown(db_script)
        elif format == "json":
            content = _export_json(db_script)
        else:
            raise HTTPException(status_code=400, detail="不支持的导出格式")

        # 写入文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"✅ 脚本导出成功: {file_path}")

        # 返回文件下载链接
        return {
            "code": 200,
            "message": "导出成功",
            "data": {
                "script_id": script_id,
                "format": format,
                "filename": filename,
                "download_url": f"/api/scripts/{script_id}/download/{format}",
                "file_size": len(content.encode("utf-8"))
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 导出脚本失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 导出格式化函数 ====================

def _export_txt(script: EpisodeScriptORM) -> str:
    """导出为纯文本格式"""
    lines = [
        f"{'='*60}",
        f"{script.title}",
        f"{'='*60}",
        f"",
        f"集数: 第{script.episode_number}集",
        f"主题: {script.theme}",
        f"总时长: {script.total_duration}分钟",
        f"总字数: {script.total_word_count}",
        f"",
        f"{'='*60}",
        f"对话内容",
        f"{'='*60}",
        f""
    ]

    for turn in script.dialogue_turns:
        speaker = "作者" if turn["role"] == "author" else "主持人"
        lines.append(f"[{speaker}]")
        lines.append(turn["content"])

        if turn.get("original_text_ref"):
            lines.append(f"  ↳ 原文引用: {turn['original_text_ref']}")

        if turn.get("hot_topic_ref"):
            lines.append(f"  ↳ 热点关联: {turn['hot_topic_ref']}")

        lines.append("")

    lines.append(f"{'='*60}")
    lines.append(f"作者占比: {script.author_speaking_ratio:.1f}%")
    lines.append(f"主持人占比: {script.host_speaking_ratio:.1f}%")

    return "\n".join(lines)


def _export_markdown(script: EpisodeScriptORM) -> str:
    """导出为Markdown格式"""
    lines = [
        f"# {script.title}",
        f"",
        f"## 基本信息",
        f"",
        f"- **集数**: 第{script.episode_number}集",
        f"- **主题**: {script.theme}",
        f"- **总时长**: {script.total_duration}分钟",
        f"- **总字数**: {script.total_word_count}",
        f"",
        f"---",
        f"",
        f"## 对话内容",
        f""
    ]

    for idx, turn in enumerate(script.dialogue_turns, 1):
        speaker = "👤 作者" if turn["role"] == "author" else "🎙️ 主持人"

        lines.append(f"### {speaker} (第{idx}轮)")
        lines.append("")
        lines.append(turn["content"])
        lines.append("")

        if turn.get("original_text_ref"):
            lines.append(f"> 📖 原文引用: {turn['original_text_ref']}")
            lines.append("")

        if turn.get("hot_topic_ref"):
            lines.append(f"> 🔥 热点关联: {turn['hot_topic_ref']}")
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 统计信息")
    lines.append("")
    lines.append(f"- 作者占比: {script.author_speaking_ratio:.1f}%")
    lines.append(f"- 主持人占比: {script.host_speaking_ratio:.1f}%")

    return "\n".join(lines)


def _export_json(script: EpisodeScriptORM) -> str:
    """导出为JSON格式"""
    data = {
        "script_id": script.script_id,
        "outline_id": script.outline_id,
        "book_id": script.book_id,
        "episode_number": script.episode_number,
        "title": script.title,
        "theme": script.theme,
        "dialogue_turns": script.dialogue_turns,
        "statistics": {
            "total_duration": script.total_duration,
            "total_word_count": script.total_word_count,
            "author_speaking_ratio": script.author_speaking_ratio,
            "host_speaking_ratio": script.host_speaking_ratio
        },
        "quality_metrics": script.quality_metrics,
        "generation_time": script.generation_time.isoformat() if script.generation_time else None,
        "version": script.version
    }

    return json.dumps(data, ensure_ascii=False, indent=2)
