#!/bin/bash
# 测试提纲生成功能

cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)"

echo "📝 测试提纲生成功能"
echo "==================="
echo ""

python3 << 'PYTHON_SCRIPT'
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.document_parser import get_document_parser
from app.services.persona_builder import get_persona_builder
from app.services.outline_generator import get_outline_generator

async def test():
    print("📖 步骤1: 解析《乡土中国》")
    print("-" * 60)

    parser = get_document_parser()

    # 解析乡土中国（章节数适中，14章）
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

    persona_builder = get_persona_builder()
    persona = await persona_builder.build_persona(
        book=book,
        era="中国社会学家（1910-2005）",
        identity="著名社会学家、人类学家"
    )

    print(f"✅ Persona构建完成!")
    print(f"   作者: {persona.author_name}")
    print(f"   核心哲学: {persona.core_philosophy[:50]}...")
    print()

    print("📝 步骤3: 生成10集提纲")
    print("-" * 60)

    outline_generator = get_outline_generator()

    try:
        # 生成提纲
        series = await outline_generator.generate_outline(
            book=book,
            persona=persona,
            episodes_count=10
        )

        print(f"✅ 提纲生成完成!")
        print()

        # 统计信息
        print("📊 提纲统计:")
        print("=" * 60)
        print(f"合集ID: {series.series_id}")
        print(f"总集数: {series.total_episodes}")
        print(f"实际生成: {len(series.outlines)} 集")
        print()

        # 章节覆盖度分析
        covered_chapters = set()
        for outline in series.outlines:
            covered_chapters.update(outline.target_chapters)

        coverage_rate = len(covered_chapters) / len(book.chapters) * 100
        print(f"章节覆盖度: {len(covered_chapters)}/{len(book.chapters)} ({coverage_rate:.1f}%)")
        print()

        # 显示每集详情
        print("📋 10集提纲详情:")
        print("=" * 60)

        for outline in series.outlines:
            ep_num = outline.episode_number
            theme = outline.theme
            chapters = outline.target_chapters
            points = outline.discussion_points
            hot_topics = outline.hot_topics

            print(f"\n第{ep_num}集：{theme}")
            print("-" * 60)
            print(f"📚 对应章节: {', '.join(chapters)}")

            print(f"💡 讨论重点 ({len(points)}个):")
            for i, point in enumerate(points[:5], 1):  # 显示前5个
                print(f"   {i}. {point}")
            if len(points) > 5:
                print(f"   ... 还有 {len(points) - 5} 个讨论点")

            if hot_topics:
                print(f"\n🔥 匹配热点 ({len(hot_topics)}个):")
                for ht in hot_topics[:2]:  # 显示前2个
                    print(f"   • {ht.topic_title} (相关度: {ht.relevance_score:.2f})")

        print("\n" + "=" * 60)
        print()

        # 质量评估
        print("✅ 提纲质量评估:")
        print("-" * 60)

        # 计算各项指标
        avg_points = sum(len(outline.discussion_points) for outline in series.outlines) / len(series.outlines)
        all_have_chapters = all(len(outline.target_chapters) > 0 for outline in series.outlines)
        all_have_topics = all(len(outline.discussion_points) >= 5 for outline in series.outlines)

        print(f"1. 章节覆盖度: {'✓ 优秀' if coverage_rate >= 90 else '✗ 需改进'} ({coverage_rate:.1f}%)")
        print(f"2. 每集讨论点数: {'✓ 优秀' if avg_points >= 5 else '✗ 需改进'} (平均 {avg_points:.1f} 个)")
        print(f"3. 章节分配完整性: {'✓ 完整' if all_have_chapters else '✗ 有缺失'}")
        print(f"4. 讨论点充足性: {'✓ 充足' if all_have_topics else '✗ 不足'}")
        print()

        all_good = all([
            coverage_rate >= 90,
            avg_points >= 5,
            all_have_chapters,
            all_have_topics
        ])

        if all_good:
            print("🎉 提纲质量优秀！所有指标均达标！")
        else:
            print("⚠️  部分指标未达标，可能需要人工调整")

        print()

    except Exception as e:
        print(f"❌ 提纲生成失败: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
PYTHON_SCRIPT
