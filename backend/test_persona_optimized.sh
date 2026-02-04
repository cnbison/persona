#!/bin/bash
# 测试优化后的Persona构建

cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)"

echo "🧠 测试优化后的Persona构建质量"
echo "==============================="
echo ""

python3 << 'PYTHON_SCRIPT'
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.document_parser import get_document_parser
from app.services.persona_builder import get_persona_builder

async def test():
    print("📖 步骤1: 解析《论语》")
    print("-" * 60)

    parser = get_document_parser()

    # 解析论语
    book = await parser.parse_book(
        file_path='../books/论语.txt',
        title='论语',
        author='孔子'
    )

    print(f"✅ 书籍解析完成!")
    print(f"   标题: {book.title}")
    print(f"   作者: {book.author}")
    print(f"   章节数: {len(book.chapters)}")
    print()

    print("🧠 步骤2: 构建孔子Persona（优化后）")
    print("-" * 60)

    builder = get_persona_builder()

    try:
        # 构建Persona
        persona = await builder.build_persona(
            book=book,
            era="春秋时期（公元前551-前479年）",
            identity="伟大的思想家、教育家、儒家学派创始人"
        )

        print(f"✅ Persona构建完成!")
        print()

        # 统计信息
        print("📊 优化效果统计:")
        print("=" * 60)
        print(f"✓ 核心概念数量: {len(persona.key_concepts)} 个")
        print(f"✓ 核心立场数量: {len(persona.core_positions)} 个")
        print(f"✓ 反对立场数量: {len(persona.opposed_positions)} 个")
        print(f"✓ 性格特质数量: {len(persona.personality_traits)} 个")
        print(f"✓ 修辞手法数量: {len(persona.rhetorical_devices)} 个")
        print()

        # 显示6维度分析结果
        print("📊 6维度人格分析（优化后）:")
        print("=" * 60)

        print("\n1️⃣  思维方式 (Thinking Style)")
        print("-" * 60)
        print(f"类型: {persona.thinking_style}")
        print(f"描述: {persona.logic_pattern}")
        print(f"推理框架: {persona.reasoning_framework}")

        print("\n2️⃣  哲学体系 (Philosophy)")
        print("-" * 60)
        print(f"核心哲学: {persona.core_philosophy}")
        print(f"理论框架: {persona.theoretical_framework}")
        print(f"关键概念 ({len(persona.key_concepts)}个):")
        for i, (concept, definition) in enumerate(persona.key_concepts.items(), 1):
            print(f"  {i}. {concept}: {definition}")

        print("\n3️⃣  叙事风格 (Narrative Style)")
        print("-" * 60)
        print(f"风格: {persona.narrative_style}")
        print(f"语言节奏: {persona.language_rhythm}")
        print(f"修辞手法 ({len(persona.rhetorical_devices)}个): {', '.join(persona.rhetorical_devices)}")

        print("\n4️⃣  价值观 (Values)")
        print("-" * 60)
        print(f"价值取向: {persona.value_orientation}")
        print(f"判断框架: {persona.value_judgment_framework}")
        print(f"核心立场 ({len(persona.core_positions)}个):")
        for i, position in enumerate(persona.core_positions, 1):
            print(f"  {i}. ✓ {position}")
        print(f"反对立场 ({len(persona.opposed_positions)}个):")
        for i, position in enumerate(persona.opposed_positions, 1):
            print(f"  {i}. ✗ {position}")

        print("\n5️⃣  语气与性格 (Tone & Personality)")
        print("-" * 60)
        print(f"语气: {persona.tone}")
        print(f"情感倾向: {persona.emotion_tendency}")
        print(f"表达方式: {persona.expressiveness}")
        print(f"性格特质 ({len(persona.personality_traits)}个): {', '.join(persona.personality_traits)}")

        print("\n" + "=" * 60)
        print()

        # 生成System Prompt
        print("📝 System Prompt:")
        print("-" * 60)

        system_prompt = await builder.generate_system_prompt(
            persona=persona,
            era="春秋时期（公元前551-前479年）",
            identity="伟大的思想家、教育家、儒家学派创始人"
        )

        print(system_prompt)
        print()

        # 质量评估
        print("=" * 60)
        print("✅ 优化效果评估:")
        print("=" * 60)
        print()

        # 计算各项指标
        concept_score = "✓ 优秀" if len(persona.key_concepts) >= 5 else "✗ 需改进"
        position_score = "✓ 优秀" if len(persona.core_positions) >= 5 else "✗ 需改进"
        opposition_score = "✓ 优秀" if len(persona.opposed_positions) >= 4 else "✗ 需改进"
        trait_score = "✓ 优秀" if len(persona.personality_traits) >= 5 else "✗ 需改进"
        detail_score = "✓ 详细" if len(persona.core_philosophy) > 50 else "✗ 简略"

        print(f"1. 核心概念提取: {concept_score} ({len(persona.key_concepts)}/5+)")
        print(f"2. 核心立场提取: {position_score} ({len(persona.core_positions)}/5+)")
        print(f"3. 反对立场提取: {opposition_score} ({len(persona.opposed_positions)}/4+)")
        print(f"4. 性格特质提取: {trait_score} ({len(persona.personality_traits)}/5+)")
        print(f"5. 描述详细程度: {detail_score} ({len(persona.core_philosophy)} 字)")
        print()

        all_good = all([
            len(persona.key_concepts) >= 5,
            len(persona.core_positions) >= 5,
            len(persona.opposed_positions) >= 4,
            len(persona.personality_traits) >= 5,
            len(persona.core_philosophy) > 50
        ])

        if all_good:
            print("🎉 优化成功！所有指标均达标！")
        else:
            print("⚠️  部分指标未达标，可能需要进一步优化")

        print()

    except Exception as e:
        print(f"❌ Persona构建失败: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
PYTHON_SCRIPT
