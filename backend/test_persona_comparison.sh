#!/bin/bash
# 优化前后对比测试

cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)"

echo "📊 优化前后对比测试"
echo "==================="
echo ""
echo "测试作者：柏拉图（理想国）"
echo ""

python3 << 'PYTHON_SCRIPT'
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.document_parser import get_document_parser
from app.services.persona_builder import get_persona_builder

async def test_plato():
    parser = get_document_parser()
    builder = get_persona_builder()

    print("📖 解析《理想国》...")
    book = await parser.parse_book(
        file_path='../books/理想国.txt',
        title='理想国',
        author='柏拉图'
    )
    print(f"✅ 解析完成: {len(book.chapters)} 章节")

    print("\n🧠 构建柏拉图Persona（优化后）...")
    persona = await builder.build_persona(
        book=book,
        era="古希腊（约公元前427-前347年）",
        identity="著名哲学家、思想家"
    )

    print(f"\n✅ 构建完成!")
    print("\n📊 统计信息:")
    print("-" * 60)
    print(f"✓ 核心概念: {len(persona.key_concepts)} 个")
    print(f"✓ 核心立场: {len(persona.core_positions)} 个")
    print(f"✓ 反对立场: {len(persona.opposed_positions)} 个")
    print(f"✓ 性格特质: {len(persona.personality_traits)} 个")

    print(f"\n💡 关键概念:")
    for i, (concept, definition) in enumerate(persona.key_concepts.items(), 1):
        print(f"  {i}. {concept}: {definition[:60]}...")

    print(f"\n📝 核心立场（前3个）:")
    for i, position in enumerate(persona.core_positions[:3], 1):
        print(f"  {i}. {position}")

    print(f"\n⚠️  反对立场（前3个）:")
    for i, position in enumerate(persona.opposed_positions[:3], 1):
        print(f"  {i}. {position}")

    print("\n" + "=" * 60)
    print("✅ 优化评估:")
    print("-" * 60)

    all_good = all([
        len(persona.key_concepts) >= 5,
        len(persona.core_positions) >= 5,
        len(persona.opposed_positions) >= 4,
        len(persona.personality_traits) >= 5
    ])

    if all_good:
        print("🎉 所有指标达标！优化成功！")
    else:
        print("⚠️  部分指标未达标")

    # 显示详细对比
    print("\n📈 优化前后对比（柏拉图）:")
    print("-" * 60)
    print(f"核心概念: 优化前 2个 → 优化后 {len(persona.key_concepts)}个 (提升{len(persona.key_concepts)-2}个)")
    print(f"核心立场: 优化前 2个 → 优化后 {len(persona.core_positions)}个 (提升{len(persona.core_positions)-2}个)")
    print(f"反对立场: 优化前 2个 → 优化后 {len(persona.opposed_positions)}个 (提升{len(persona.opposed_positions)-2}个)")
    print(f"性格特质: 优化前 2个 → 优化后 {len(persona.personality_traits)}个 (提升{len(persona.personality_traits)-2}个)")

asyncio.run(test_plato())
PYTHON_SCRIPT
