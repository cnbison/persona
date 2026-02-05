"""
证据库API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from loguru import logger

from app.database import get_db
from app.models.orm import EvidenceORM, ParagraphORM, ChapterORM
from app.services.evidence_builder import get_evidence_builder

router = APIRouter()


@router.post("/build/{book_id}", summary="构建证据库")
async def build_evidence(book_id: str, db: Session = Depends(get_db)):
    try:
        builder = get_evidence_builder()
        builder.build_for_book(db, book_id)
        return {
            "code": 200,
            "message": "证据库构建完成",
            "data": {"book_id": book_id}
        }
    except Exception as e:
        logger.error(f"❌ 证据库构建失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", summary="证据检索")
async def search_evidence(
    keyword: Optional[str] = None,
    book_id: Optional[str] = None,
    chapter_id: Optional[str] = None,
    viewpoint_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(EvidenceORM)
        if book_id:
            query = query.filter(EvidenceORM.book_id == book_id)
        if chapter_id:
            query = query.filter(EvidenceORM.chapter_id == chapter_id)
        if viewpoint_id:
            query = query.filter(EvidenceORM.viewpoint_id == viewpoint_id)
        if keyword:
            query = query.filter(EvidenceORM.evidence_text.contains(keyword))

        evidences = query.limit(50).all()
        chapter_map = {}
        paragraph_map = {}
        for e in evidences:
            if e.chapter_id and e.chapter_id not in chapter_map:
                chapter = db.query(ChapterORM).filter(ChapterORM.chapter_id == e.chapter_id).first()
                chapter_map[e.chapter_id] = chapter.title if chapter else None
            if e.paragraph_id and e.paragraph_id not in paragraph_map:
                paragraph = db.query(ParagraphORM).filter(ParagraphORM.paragraph_id == e.paragraph_id).first()
                paragraph_map[e.paragraph_id] = paragraph.paragraph_number if paragraph else None

        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "items": [
                    {
                        "evidence_id": e.evidence_id,
                        "book_id": e.book_id,
                        "chapter_id": e.chapter_id,
                        "chapter_title": chapter_map.get(e.chapter_id),
                        "paragraph_id": e.paragraph_id,
                        "paragraph_number": paragraph_map.get(e.paragraph_id),
                        "viewpoint_id": e.viewpoint_id,
                        "evidence_text": e.evidence_text,
                        "context_before": e.context_before,
                        "context_after": e.context_after,
                        "keywords": e.keywords,
                        "score": e.score
                    }
                    for e in evidences
                ]
            }
        }
    except Exception as e:
        logger.error(f"❌ 证据检索失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paragraphs", summary="按章节获取段落")
async def list_paragraphs(
    chapter_id: str,
    db: Session = Depends(get_db)
):
    try:
        paragraphs = db.query(ParagraphORM).filter(ParagraphORM.chapter_id == chapter_id).all()
        return {
            "code": 200,
            "message": "获取成功",
            "data": {
                "items": [
                    {
                        "paragraph_id": p.paragraph_id,
                        "chapter_id": p.chapter_id,
                        "paragraph_number": p.paragraph_number,
                        "content": p.content,
                        "word_count": p.word_count
                    }
                    for p in paragraphs
                ]
            }
        }
    except Exception as e:
        logger.error(f"❌ 段落获取失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
