#!/bin/bash
# 测试《乡土中国》PDF解析

cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)"

echo "📖 测试《乡土中国》PDF解析"
echo "=========================="
echo ""

python3 << 'PYTHON_SCRIPT'
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.document_parser import get_document_parser

async def test():
    print("📚 解析《乡土中国》...")
    print("=" * 60)
    print()

    parser = get_document_parser()

    try:
        book = await parser.parse_book(
            file_path='../books/乡土中国.pdf',
            title='乡土中国',
            author='费孝通'
        )

        print(f"✅ 解析成功!")
        print()
        print(f"📚 标题: {book.title}")
        print(f"✍️  作者: {book.author}")
        print(f"🌐 语言: {book.language}")
        print(f"📁 文件类型: {book.file_type}")
        print(f"📏 总字数: {book.total_words:,}")
        print(f"📖 章节数: {len(book.chapters)}")
        print(f"💡 核心观点: {len(book.core_viewpoints)}")
        print()

        # 显示所有章节
        print("📋 章节列表:")
        print("-" * 60)
        for ch in book.chapters:
            content_preview = ch.content[:80].replace('\n', ' ')
            print(f"{ch.chapter_number}. {ch.title}")
            print(f"   内容: {content_preview}... ({len(ch.content):,} 字)")
            print()

        # 显示核心观点
        print("💡 核心观点示例（前5个）:")
        print("-" * 60)
        for i, vp in enumerate(book.core_viewpoints[:5], 1):
            print(f"{i}. {vp.content[:100]}...")
            print(f"   关键词: {', '.join(vp.keywords[:5])}")
            print()

        # 统计信息
        avg_chapter_words = sum(len(c.content) for c in book.chapters) // len(book.chapters) if book.chapters else 0
        print("=" * 60)
        print(f"📊 统计信息:")
        print(f"   总章节数: {len(book.chapters)}")
        print(f"   平均字数: {avg_chapter_words:,} 字/章")
        print(f"   总字数: {book.total_words:,} 字")
        print(f"   核心观点数: {len(book.core_viewpoints)}")

    except Exception as e:
        print(f"❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
PYTHON_SCRIPT
