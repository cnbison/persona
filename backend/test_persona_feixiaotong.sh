#!/bin/bash
# 测试费孝通Persona构建

cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)"

echo "🧠 测试费孝通Persona构建"
echo "======================="
echo ""

python3 << 'PYTHON_SCRIPT'
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.document_parser import get_document_parser
from app.services.persona_builder import get_persona_builder

async def test():
    print("📖 步骤1: 解析《乡土中国》")
    print("-" * 60)

    parser = get_document_parser()

    # 解析乡土中国
    book = await parser.parse_book(
        file_path='../books/乡土中国.pdf',
        title='乡土中国',
        author='费孝通'
    )

    print(f"✅ 书籍解析完成!")
    print(f"   标题: {book.title}")
    print(f"   作者: {book.author}")
    print(f"   章节数: {len(book.chapters)}")
    print(f"   核心观点: {len(book.core_viewpoints)}")
    print()

    print("🧠 步骤2: 构建费孝通Persona")
    print("-" * 60)

    builder = get_persona_builder()

    try:
        # 构建Persona
        persona = await builder.build_persona(
            book=book,
            era="中国社会学家（1910-2005）",
            identity="著名社会学家、人类学家"
        )

        print(f"✅ Persona构建完成!")
        print()

        # 显示6维度分析结果
        print("📊 6维度人格分析:")
        print("=" * 60)

        print("\n1️⃣  思维方式 (Thinking Style)")
        print("-" * 60)
        print(f"类型: {persona.thinking_style}")
        print(f"逻辑模式: {persona.logic_pattern}")
        print(f"推理框架: {persona.reasoning_framework}")

        print("\n2️⃣  哲学体系 (Philosophy)")
        print("-" * 60)
        print(f"核心哲学: {persona.core_philosophy}")
        print(f"理论框架: {persona.theoretical_framework}")
        print(f"关键概念:")
        for concept, definition in list(persona.key_concepts.items())[:5]:
            print(f"  • {concept}: {definition}")
        if len(persona.key_concepts) > 5:
            print(f"  ... 还有 {len(persona.key_concepts) - 5} 个概念")

        print("\n3️⃣  叙事风格 (Narrative Style)")
        print("-" * 60)
        print(f"风格: {persona.narrative_style}")
        print(f"语言节奏: {persona.language_rhythm}")
        print(f"修辞手法: {', '.join(persona.rhetorical_devices[:5])}")

        print("\n4️⃣  价值观 (Values)")
        print("-" * 60)
        print(f"价值取向: {persona.value_orientation}")
        print(f"核心立场:")
        for position in persona.core_positions[:5]:
            print(f"  ✓ {position}")

        print("\n5️⃣  语气 (Tone)")
        print("-" * 60)
        print(f"语气: {persona.tone}")
        print(f"表达方式: {persona.expressiveness}")

        print("\n6️⃣  性格 (Personality)")
        print("-" * 60)
        print(f"性格特质: {', '.join(persona.personality_traits)}")

        print("\n" + "=" * 60)
        print()

        # 生成System Prompt
        print("📝 System Prompt预览:")
        print("-" * 60)

        system_prompt = await builder.generate_system_prompt(
            persona=persona,
            era="中国社会学家（1910-2005）",
            identity="著名社会学家、人类学家"
        )

        print(system_prompt[:500] + "...")
        print()

        # 总结
        print("=" * 60)
        print("🎉 测试完成!")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Persona构建失败: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
PYTHON_SCRIPT
