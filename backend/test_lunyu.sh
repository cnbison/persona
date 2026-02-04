#!/bin/bash
# 测试《论语》解析

cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)"

python3 << 'PYTHON_SCRIPT'
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.document_parser import get_document_parser

async def test():
    print("📖 解析《论语》...")
    print("=" * 50)
    
    parser = get_document_parser()
    
    try:
        book = await parser.parse_book(
            file_path='../books/论语.txt',
            title='论语',
            author='孔子'
        )
        
        print(f"✅ 解析成功!")
        print(f"📚 标题: {book.title}")
        print(f"✍️  作者: {book.author}")
        print(f"📏 总字数: {book.total_words:,}")
        print(f"📖 章节数: {len(book.chapters)}")
        print(f"💡 核心观点: {len(book.core_viewpoints)}")
        print()
        print("📋 章节列表（前15个）:")
        print("-" * 60)
        for ch in book.chapters[:15]:
            content_preview = ch.content[:80].replace('\n', ' ')
            print(f"{ch.chapter_number}. {ch.title}")
            print(f"   内容: {content_preview}... ({len(ch.content):,} 字)")
            print()
        
        if len(book.chapters) > 15:
            print(f"... 还有 {len(book.chapters) - 15} 个章节")
            print()
        
        print("💡 核心观点示例（前5个）:")
        print("-" * 60)
        for i, vp in enumerate(book.core_viewpoints[:5], 1):
            print(f"{i}. {vp.content[:80]}...")
            print(f"   关键词: {', '.join(vp.keywords[:5])}")
            print()
        
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
PYTHON_SCRIPT
