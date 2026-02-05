"""
著作管理API
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from loguru import logger
import uuid

from app.database import get_db
from app.models.book import Book
from app.services.document_parser import get_document_parser
from app.services.persona_builder import get_persona_builder
from app.services.outline_generator import get_outline_generator
from app.crud.crud_book import create_book, get_book, get_books, delete_book
from app.crud.crud_series import create_persona, create_book_series
from app.models.orm import BookORM

router = APIRouter()


@router.post("/upload", summary="上传并解析著作")
async def upload_book(
    file: UploadFile = File(...),
    title: str = None,
    author: str = None,
    db: Session = Depends(get_db)
):
    """
    上传著作文件并解析

    参数:
    - file: 著作文件（PDF/EPUB/TXT）
    - title: 著作标题（可选）
    - author: 作者（可选）
    """
    try:
        # 保存文件
        import os
        from pathlib import Path

        upload_dir = Path("./data/books")
        upload_dir.mkdir(exist_ok=True)

        file_path = upload_dir / file.filename

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        logger.info(f"✅ 文件保存成功: {file_path}")

        # 解析著作
        parser = get_document_parser()
        book = await parser.parse_book(
            file_path=str(file_path),
            title=title or file.filename,
            author=author or "未知作者"
        )

        # 保存到数据库
        db_book = create_book(db=db, book=book)

        return {
            "code": 200,
            "message": "著作上传并解析成功",
            "data": {
                "book_id": db_book.book_id,
                "title": db_book.title,
                "author": db_book.author,
                "total_chapters": db_book.total_chapters,
                "total_viewpoints": db_book.total_viewpoints
            }
        }

    except Exception as e:
        logger.error(f"❌ 上传著作失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", summary="获取著作列表")
async def get_books_list(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    获取著作列表

    参数:
    - skip: 跳过数量（分页）
    - limit: 返回数量限制
    """
    try:
        books = get_books(db, skip=skip, limit=limit)

        # 获取总数（用于分页）
        from app.models.orm import BookORM
        total_count = db.query(BookORM).count()

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "books": [
                    {
                        "book_id": b.book_id,
                        "title": b.title,
                        "author": b.author,
                        "language": b.language,
                "file_type": b.file_type,
                "total_chapters": b.total_chapters,
                "total_viewpoints": b.total_viewpoints,
                "parse_stats": b.parse_stats or {},
                "created_at": b.created_at.isoformat()
            }
            for b in books
                ],
                "total": total_count
            }
        }

    except Exception as e:
        logger.error(f"❌ 获取著作列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{book_id}", summary="获取著作详情")
async def get_book_detail(book_id: str, db: Session = Depends(get_db)):
    """
    获取著作详细信息

    参数:
    - book_id: 著作ID
    """
    try:
        db_book = get_book(db, book_id)

        if not db_book:
            raise HTTPException(status_code=404, detail="著作不存在")

        # 获取章节
        chapters = [
            {
                "chapter_id": c.chapter_id,
                "chapter_number": c.chapter_number,
                "title": c.title,
                "word_count": c.word_count
            }
            for c in db_book.chapters
        ]

        # 获取所有核心观点
        viewpoints = [
            {
                "viewpoint_id": v.viewpoint_id,
                "content": v.content[:100] + "..." if len(v.content) > 100 else v.content,
                "keywords": v.keywords[:5] if v.keywords else []
            }
            for v in db_book.viewpoints
        ]

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "book_id": db_book.book_id,
                "title": db_book.title,
                "author": db_book.author,
                "language": db_book.language,
                "file_type": db_book.file_type,
                "total_words": db_book.total_words,
                "total_chapters": db_book.total_chapters,
                "total_viewpoints": db_book.total_viewpoints,
                "parse_stats": db_book.parse_stats or {},
                "chapters": chapters,
                "viewpoints": viewpoints,
                "created_at": db_book.created_at.isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取著作详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{book_id}/parse-stats", summary="获取解析统计")
async def get_parse_stats(book_id: str, db: Session = Depends(get_db)):
    """获取著作解析统计信息"""
    try:
        db_book = get_book(db, book_id)
        if not db_book:
            raise HTTPException(status_code=404, detail="著作不存在")

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "book_id": db_book.book_id,
                "title": db_book.title,
                "author": db_book.author,
                "parse_stats": db_book.parse_stats or {}
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取解析统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{book_id}", summary="删除著作")
async def delete_book_endpoint(book_id: str, db: Session = Depends(get_db)):
    """
    删除著作

    参数:
    - book_id: 著作ID
    """
    try:
        success = delete_book(db, book_id)

        if not success:
            raise HTTPException(status_code=404, detail="著作不存在")

        return {
            "code": 200,
            "message": "删除成功",
            "data": {"book_id": book_id}
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 删除著作失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
