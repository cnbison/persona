"""
著作CRUD操作
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from loguru import logger

from app.models.orm import BookORM, ChapterORM, CoreViewpointORM
from app.models.book import Book, Chapter, CoreViewpoint


def create_book(db: Session, book: Book) -> BookORM:
    """
    创建著作记录

    参数:
        db: 数据库会话
        book: Pydantic Book对象

    返回:
        BookORM对象
    """
    db_book = BookORM(
        book_id=book.book_id,
        title=book.title,
        author=book.author,
        language=book.language,
        file_path=book.file_path,
        file_type=book.file_type,
        total_words=book.total_words,
        total_chapters=len(book.chapters),
        total_viewpoints=len(book.core_viewpoints),
        parse_stats=book.parse_stats or {}
    )

    db.add(db_book)
    db.commit()
    db.refresh(db_book)

    # 创建章节记录
    for chapter in book.chapters:
        db_chapter = ChapterORM(
            chapter_id=chapter.chapter_id,
            book_id=book.book_id,
            chapter_number=chapter.chapter_number,
            title=chapter.title,
            content=chapter.content,
            page_range=chapter.page_range,
            word_count=len(chapter.content)
        )
        db.add(db_chapter)

    # 创建核心观点记录
    for viewpoint in book.core_viewpoints:
        db_viewpoint = CoreViewpointORM(
            viewpoint_id=viewpoint.viewpoint_id,
            book_id=book.book_id,
            chapter_id=viewpoint.chapter_id,
            content=viewpoint.content,
            original_text=viewpoint.original_text,
            context=viewpoint.context,
            keywords=viewpoint.keywords
        )
        db.add(db_viewpoint)

    db.commit()
    logger.info(f"✅ 创建著作成功: {book.title} ({len(book.chapters)}章, {len(book.core_viewpoints)}观点)")

    return db_book


def get_book(db: Session, book_id: str) -> Optional[BookORM]:
    """获取著作"""
    return db.query(BookORM).filter(BookORM.book_id == book_id).first()


def get_books(db: Session, skip: int = 0, limit: int = 10) -> List[BookORM]:
    """获取著作列表"""
    return db.query(BookORM).offset(skip).limit(limit).all()


def delete_book(db: Session, book_id: str) -> bool:
    """删除著作"""
    db_book = db.query(BookORM).filter(BookORM.book_id == book_id).first()
    if db_book:
        db.delete(db_book)
        db.commit()
        logger.info(f"✅ 删除著作成功: {book_id}")
        return True
    return False


def update_book(db: Session, book_id: str, **kwargs) -> Optional[BookORM]:
    """更新著作"""
    db_book = db.query(BookORM).filter(BookORM.book_id == book_id).first()
    if db_book:
        for key, value in kwargs.items():
            if hasattr(db_book, key):
                setattr(db_book, key, value)
        db.commit()
        db.refresh(db_book)
        logger.info(f"✅ 更新著作成功: {book_id}")
        return db_book
    return None
