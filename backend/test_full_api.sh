#!/bin/bash
# 测试完整API流程：解析 -> Persona -> 提纲 -> 数据库

cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)"

echo "🔄 测试完整API流程"
echo "=================="
echo ""

python3 << 'PYTHON_SCRIPT'
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.document_parser import get_document_parser
from app.services.persona_builder import get_persona_builder
from app.services.outline_generator import get_outline_generator
from app.database import SessionLocal
from app.crud import create_book, create_persona, create_book_series, get_book, get_book_series

async def test():
    db = SessionLocal()

    try:
        print("📖 步骤1: 解析《论语》")
        print("-" * 60)

        parser = get_document_parser()
        book = await parser.parse_book(
            file_path='../books/论语.txt',
            title='论语',
            author='孔子'
        )

        print(f"✅ 解析完成: {book.title}")
        print(f"   章节数: {len(book.chapters)}")
        print(f"   核心观点: {len(book.core_viewpoints)}")
        print()

        # 保存到数据库
        print("💾 步骤2: 保存到数据库")
        print("-" * 60)

        db_book = create_book(db, book)
        print(f"✅ 保存著作成功: {db_book.title} (ID: {db_book.book_id})")
        print()

        print("🧠 步骤3: 构建Persona")
        print("-" * 60)

        persona_builder = get_persona_builder()
        persona = await persona_builder.build_persona(
            book=book,
            era="春秋时期（公元前551-前479年）",
            identity="伟大的思想家、教育家、儒家学派创始人"
        )

        # 保存Persona
        db_persona = create_persona(db, persona, era="春秋时期", identity="思想家")
        print(f"✅ 保存Persona成功: {db_persona.author_name} (ID: {db_persona.persona_id})")
        print()

        print("📝 步骤4: 生成提纲")
        print("-" * 60)

        outline_generator = get_outline_generator()
        series = await outline_generator.generate_outline(
            book=book,
            persona=persona,
            episodes_count=10
        )

        # 保存BookSeries
        db_series = create_book_series(db, series, persona_id=db_persona.persona_id)
        print(f"✅ 保存提纲成功: {db_series.book_title} (ID: {db_series.series_id})")
        print(f"   集数: {len(db_series.outlines)}")
        print()

        print("🔍 步骤5: 验证数据读取")
        print("-" * 60)

        # 从数据库读取著作
        retrieved_book = get_book(db, db_book.book_id)
        print(f"✅ 读取著作: {retrieved_book.title}")
        print(f"   章节数: {retrieved_book.total_chapters}")
        print(f"   观点数: {retrieved_book.total_viewpoints}")
        print()

        # 从数据库读取合集
        retrieved_series = get_book_series(db, db_series.series_id)
        print(f"✅ 读取合集: {retrieved_series.book_title}")
        print(f"   集数: {retrieved_series.total_episodes}")
        print(f"   状态: {retrieved_series.completion_status}")
        print()

        # 显示前3集
        print("📋 提纲预览（前3集）:")
        print("-" * 60)
        for outline in retrieved_series.outlines[:3]:
            print(f"{outline.episode_number}. {outline.theme}")
            print(f"   章节: {', '.join(outline.target_chapters)}")
            print(f"   讨论: {len(outline.discussion_points)}个")
            print()

        print("=" * 60)
        print("🎉 完整流程测试成功！")
        print("=" * 60)
        print()
        print("✅ 验证项:")
        print("  ✓ 书籍解析")
        print("  ✓ Persona构建")
        print("  ✓ 提纲生成")
        print("  ✓ 数据库保存（Book + Chapters + Viewpoints）")
        print("  ✓ 数据库保存（Persona）")
        print("  ✓ 数据库保存（BookSeries + EpisodeOutlines）")
        print("  ✓ 数据库读取")
        print()

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()

asyncio.run(test())
PYTHON_SCRIPT
