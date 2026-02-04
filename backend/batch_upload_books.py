#!/usr/bin/env python3
"""
批量上传书籍脚本
将 books/ 目录下的所有书籍上传到系统中
"""
import asyncio
import sys
from pathlib import Path
from loguru import logger

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal, Base, engine
from app.services.document_parser import get_document_parser
from app.crud.crud_book import create_book


# 确保数据库表存在
Base.metadata.create_all(bind=engine)


async def upload_book_file(file_path: str, title: str, author: str):
    """上传单本书籍"""
    logger.info(f"📖 开始上传: {title}")

    try:
        # 1. 解析书籍
        parser = get_document_parser()
        book = await parser.parse_book(
            file_path=file_path,
            title=title,
            author=author
        )

        logger.info(f"  ✅ 解析成功:")
        logger.info(f"     - 章节数: {len(book.chapters)}")
        logger.info(f"     - 观点数: {len(book.core_viewpoints)}")
        logger.info(f"     - 字数: {book.total_words}")

        # 2. 保存到数据库
        db = SessionLocal()
        try:
            db_book = create_book(db=db, book=book)
            logger.info(f"  ✅ 已保存到数据库 (ID: {db_book.book_id})")
            return True
        finally:
            db.close()

    except Exception as e:
        logger.error(f"  ❌ 上传失败: {e}")
        return False


async def main():
    """批量上传所有书籍"""
    books_dir = Path(__file__).parent.parent / "books"

    # 定义要上传的书籍
    books_to_upload = [
        {
            "file_path": str(books_dir / "论语.txt"),
            "title": "论语",
            "author": "孔子"
        },
        {
            "file_path": str(books_dir / "理想国.txt"),
            "title": "理想国",
            "author": "柏拉图"
        },
        {
            "file_path": str(books_dir / "乡土中国.pdf"),
            "title": "乡土中国",
            "author": "费孝通"
        }
    ]

    logger.info("=" * 60)
    logger.info("开始批量上传书籍")
    logger.info("=" * 60)

    success_count = 0
    failed_count = 0

    for book_info in books_to_upload:
        file_path = book_info["file_path"]

        # 检查文件是否存在
        if not Path(file_path).exists():
            logger.warning(f"⚠️  文件不存在: {file_path}")
            failed_count += 1
            continue

        # 上传书籍
        success = await upload_book_file(
            file_path=file_path,
            title=book_info["title"],
            author=book_info["author"]
        )

        if success:
            success_count += 1
        else:
            failed_count += 1

        logger.info("")

    # 打印总结
    logger.info("=" * 60)
    logger.info(f"上传完成！成功: {success_count}, 失败: {failed_count}")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
