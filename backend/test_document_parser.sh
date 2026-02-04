#!/bin/bash
# 文档解析快速测试

cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)"

echo "📖 测试文档解析服务"
echo "==================="
echo ""
echo "测试文件: ../books/理想国.txt"
echo ""

python3 -c "
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.document_parser import get_document_parser

async def test():
    parser = get_document_parser()
    test_file = '../books/理想国.txt'
    
    print(f'📁 文件路径: {test_file}')
    
    import os
    if not os.path.exists(test_file):
        print(f'❌ 文件不存在: {test_file}')
        print(f'   当前目录: {os.getcwd()}')
        return
    
    try:
        book = await parser.parse_book(
            file_path=test_file,
            title='理想国',
            author='柏拉图'
        )
        
        print(f'✅ 解析成功!')
        print(f'   标题: {book.title}')
        print(f'   作者: {book.author}')
        print(f'   总字数: {book.total_words}')
        print(f'   章节数: {len(book.chapters)}')
        print(f'   核心观点数: {len(book.core_viewpoints)}')
        
        print(f'\n📚 章节列表（前5章）:')
        for chapter in book.chapters[:5]:
            print(f'   {chapter.chapter_number}. {chapter.title} ({len(chapter.content)} 字)')
        
        print(f'\n💡 核心观点示例（前3个）:')
        for vp in book.core_viewpoints[:3]:
            print(f'   - {vp.content[:60]}...')
            
    except Exception as e:
        print(f'❌ 解析失败: {e}')
        import traceback
        traceback.print_exc()

asyncio.run(test())
"
