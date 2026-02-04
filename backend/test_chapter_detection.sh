#!/bin/bash
# 测试优化后的章节识别

cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)"

echo "📚 测试优化后的章节识别"
echo "====================="
echo ""

python3 << 'PYTHON_SCRIPT'
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.document_parser import get_document_parser

async def test():
    parser = get_document_parser()
    
    # 读取文件
    with open('../books/理想国.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"📖 文件: 理想国.txt")
    print(f"📏 总字数: {len(text):,}")
    print("")
    
    # 测试章节识别
    print("🔍 识别章节结构...")
    print("")
    
    chapters = parser._identify_chapters(text, 'txt')
    
    print(f"✅ 识别到 {len(chapters)} 个章节")
    print("")
    
    # 显示前15个章节
    print("📋 章节列表（前15个）:")
    print("-" * 60)
    for i, chapter in enumerate(chapters[:15], 1):
        content_preview = chapter.content[:100].replace('\n', ' ')
        print(f"{i}. {chapter.title}")
        print(f"   内容: {content_preview}... ({len(chapter.content):,} 字)")
        print()
    
    # 统计信息
    total_words = sum(len(c.content) for c in chapters)
    avg_words = total_words // len(chapters) if chapters else 0
    
    print("=" * 60)
    print(f"📊 统计信息:")
    print(f"   总章节数: {len(chapters)}")
    print(f"   平均字数: {avg_words:,} 字/章")
    print(f"   总字数: {total_words:,} 字")

asyncio.run(test())
PYTHON_SCRIPT
