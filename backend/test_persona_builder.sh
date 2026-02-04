#!/bin/bash
# 测试Persona构建功能

cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)"

echo "🧠 测试Persona构建功能"
echo "======================"
echo ""

python3 << 'PYTHON_SCRIPT'
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.document_parser import get_document_parser
from app.services.persona_builder import get_persona_builder, build_host_persona

async def test():
    print("📖 步骤1: 解析《理想国》")
    print("-" * 60)

    parser = get_document_parser()

    # 解析理想国
    book = await parser.parse_book(
        file_path='../books/理想国.txt',
        title='理想国',
        author='柏拉图'
    )

    print(f"✅ 书籍解析完成!")
    print(f"   标题: {book.title}")
    print(f"   作者: {book.author}")
    print(f"   章节数: {len(book.chapters)}")
    print(f"   核心观点: {len(book.core_viewpoints)}")
    print()

    print("🧠 步骤2: 构建柏拉图Persona")
    print("-" * 60)

    builder = get_persona_builder()

    try:
        # 构建Persona（会调用真实OpenAI API）
        persona = await builder.build_persona(
            book=book,
            era="古希腊（约公元前427-前347年）",
            identity="著名哲学家、思想家"
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
        for concept, definition in persona.key_concepts.items():
            print(f"  • {concept}: {definition}")

        print("\n3️⃣  叙事风格 (Narrative Style)")
        print("-" * 60)
        print(f"风格: {persona.narrative_style}")
        print(f"语言节奏: {persona.language_rhythm}")
        print(f"句式结构: {persona.sentence_structure}")
        print(f"修辞手法: {', '.join(persona.rhetorical_devices)}")

        print("\n4️⃣  价值观 (Values)")
        print("-" * 60)
        print(f"价值取向: {persona.value_orientation}")
        print(f"判断框架: {persona.value_judgment_framework}")
        print(f"核心立场:")
        for position in persona.core_positions:
            print(f"  ✓ {position}")
        print(f"反对立场:")
        for position in persona.opposed_positions:
            print(f"  ✗ {position}")

        print("\n5️⃣  语气 (Tone)")
        print("-" * 60)
        print(f"语气: {persona.tone}")
        print(f"情感倾向: {persona.emotion_tendency}")
        print(f"表达方式: {persona.expressiveness}")

        print("\n6️⃣  性格 (Personality)")
        print("-" * 60)
        print(f"性格特质: {', '.join(persona.personality_traits)}")
        print(f"沟通风格: {persona.communication_style}")
        print(f"受众态度: {persona.attitude_toward_audience}")

        print("\n" + "=" * 60)
        print()

        # 生成System Prompt
        print("📝 步骤3: 生成System Prompt")
        print("-" * 60)

        system_prompt = await builder.generate_system_prompt(
            persona=persona,
            era="古希腊（约公元前427-前347年）",
            identity="著名哲学家、思想家"
        )

        print(f"✅ System Prompt生成成功!")
        print(f"   长度: {len(system_prompt)} 字符")
        print()
        print("📄 System Prompt内容:")
        print("=" * 60)
        print(system_prompt)
        print("=" * 60)
        print()

        # 构建主持人Persona
        print("🎙️  步骤4: 构建主持人Persona")
        print("-" * 60)

        host = build_host_persona()
        print(f"✅ 主持人Persona构建完成!")
        print()
        print("📊 主持人特质:")
        print("-" * 60)
        print(f"角色定位: {host.role_positioning}")
        print(f"性格特质: {', '.join(host.traits)}")
        print(f"语言风格: {host.language_style}")
        print(f"发言比例: {host.speaking_ratio}%")
        print()
        print("知识库:")
        for knowledge in host.knowledge_base:
            print(f"  • {knowledge}")
        print()
        print("功能:")
        for func in host.functions:
            print(f"  • {func}")
        print()

        # 总结
        print("=" * 60)
        print("🎉 测试完成!")
        print("=" * 60)
        print()
        print("✅ 所有功能测试通过:")
        print("  ✓ 书籍解析")
        print("  ✓ Persona 6维度分析（使用真实GPT-4）")
        print("  ✓ System Prompt生成")
        print("  ✓ 主持人Persona构建")
        print()

    except Exception as e:
        print(f"❌ Persona构建失败: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
PYTHON_SCRIPT
