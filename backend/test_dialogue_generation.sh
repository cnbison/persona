#!/bin/bash

# 对话生成服务测试脚本
# 测试完整的对话生成流程

echo "=========================================="
echo "🎙️  对话生成服务测试"
echo "=========================================="

cd /Users/loubicheng/project/discrimination/backend

# 激活虚拟环境
source venv/bin/activate

# 设置Python路径
export PYTHONPATH=/Users/loubicheng/project/discrimination/backend

echo ""
echo "📋 测试内容:"
echo "  1. 5段式流程生成"
echo "  2. 脚本优化功能"
echo "  3. 质量评估功能"
echo ""

# 运行测试
python3 -c "
import asyncio
import sys
from loguru import logger

sys.path.insert(0, '/Users/loubicheng/project/discrimination/backend')

from app.services.dialogue_generator import get_dialogue_generator
from app.models.dialogue import EpisodeOutline, HotTopicMatch
from app.models.persona import AuthorPersona, ThinkingStyle


async def test_dialogue_generation():
    '''测试完整的对话生成流程'''

    logger.info('🚀 开始测试对话生成服务')

    # 1. 创建测试数据
    logger.info('📦 创建测试数据...')

    test_outline = EpisodeOutline(
        outline_id='test-outline-001',
        book_id='test-book-001',
        episode_number=1,
        theme='正义的本质',
        target_chapters=['第一卷', '第二卷'],
        target_viewpoints=['viewpoint-1', 'viewpoint-2'],
        hot_topics=[
            HotTopicMatch(
                topic_title='社会公平',
                topic_description='当代社会对公平正义的讨论',
                relevance_score=0.85,
                connection_point='理想国中的正义观与现代公平理念'
            )
        ],
        discussion_points=[
            '什么是正义',
            '正义与利益的关系',
            '正义在个人和国家层面的体现'
        ],
        flow_design={
            'opening': '介绍正义这个核心概念',
            'book_exploration': '深入探讨理想国中的正义理论',
            'hot_topic_connection': '结合现代社会公平问题',
            'deep_discussion': '延伸思考正义的普适性',
            'conclusion': '总结正义的现代意义'
        }
    )

    test_persona = AuthorPersona(
        persona_id='test-persona-001',
        author_name='柏拉图',
        book_id='test-book-001',
        thinking_style=ThinkingStyle.DIALECTICAL,
        logic_pattern='辩证法',
        reasoning_framework='苏格拉底问答法',
        core_philosophy='追求真理和正义，构建理想国家',
        theoretical_framework='理念论',
        key_concepts={
            '正义': '各司其职，每个人都在适合自己的位置上',
            '理想国': '由哲学王统治的完美国家',
            '理念': '超越物质世界的永恒真理'
        },
        narrative_style='严肃、富有哲理',
        language_rhythm='沉稳、逻辑性强',
        sentence_structure='复杂句式，层层递进',
        rhetorical_devices=['比喻', '反问', '对话'],
        value_orientation='理想主义',
        value_judgment_framework='以真理和善为最高标准',
        core_positions=[
            '正义是最高的美德',
            '哲学家应该成为统治者',
            '理念世界高于现实世界'
        ],
        opposed_positions=[
            '相对主义',
            '权力至上',
            '物质享乐主义'
        ],
        tone='温和但坚定',
        emotion_tendency='理性',
        expressiveness='委婉',
        personality_traits=['睿智', '谦逊', '追求真理'],
        communication_style='对话式',
        attitude_toward_audience='尊重并引导思考'
    )

    author_system_prompt = '''你是柏拉图，古希腊伟大的哲学家。
你追求真理和正义，认为一个理想的国家应该由哲学王统治。
你的思维方式是辩证的，喜欢通过对话和问答来探求真理。
你的语言严肃而富有哲理，经常使用比喻来说明抽象概念。
你重视灵魂的修养，认为正义是个人和国家最高的美德。'''

    host_system_prompt = '''你是一位专业的播客主持人。
你的任务是引导对话，让嘉宾深入表达观点。
你的语言亲切自然，善于提出好问题。
你会在适当的时候总结和升华话题。'''

    # 2. 测试对话生成
    logger.info('')
    logger.info('🎙️  测试1: 5段式流程生成')
    logger.info('='*50)

    generator = get_dialogue_generator()

    script = await generator.generate_script(
        outline=test_outline,
        episode_number=1,
        author_persona=test_persona,
        author_system_prompt=author_system_prompt,
        host_system_prompt=host_system_prompt,
        target_duration=30
    )

    logger.info('')
    logger.info('✅ 生成结果:')
    logger.info(f'  标题: {script.title}')
    logger.info(f'  主题: {script.theme}')
    logger.info(f'  总时长: {script.total_duration}分钟')
    logger.info(f'  总字数: {script.total_word_count}')
    logger.info(f'  对话轮数: {len(script.dialogue_turns)}')
    logger.info(f'  作者占比: {script.author_speaking_ratio:.1f}%')
    logger.info(f'  主持人占比: {script.host_speaking_ratio:.1f}%')

    # 显示前几轮对话
    logger.info('')
    logger.info('💬 对话预览 (前3轮):')
    for i, turn in enumerate(script.dialogue_turns[:3], 1):
        speaker = '作者' if turn.role.value == 'author' else '主持人'
        logger.info(f'  第{i}轮 [{speaker}]:')
        logger.info(f'    {turn.content[:100]}...')

    # 3. 测试脚本优化
    logger.info('')
    logger.info('✏️  测试2: 脚本优化功能')
    logger.info('='*50)

    original_turns_count = len(script.dialogue_turns)
    optimized_script = await generator.optimize_script(script, test_persona)

    logger.info(f'✅ 优化完成:')
    logger.info(f'  优化前对话轮数: {original_turns_count}')
    logger.info(f'  优化后对话轮数: {len(optimized_script.dialogue_turns)}')
    logger.info(f'  优化后总字数: {optimized_script.total_word_count}')

    # 4. 测试质量评估
    logger.info('')
    logger.info('📊 测试3: 质量评估功能')
    logger.info('='*50)

    quality_metrics = await generator.evaluate_script_quality(optimized_script, test_persona)

    logger.info('✅ 质量评估结果:')
    for metric_name, score in quality_metrics.items():
        if metric_name != 'overall_score':
            logger.info(f'  {metric_name}: {score:.2f}')
    logger.info(f'  综合评分: {quality_metrics.get(\"overall_score\", 0):.2f}')

    # 5. 显示详细统计
    logger.info('')
    logger.info('📈 详细统计:')
    logger.info('='*50)

    # 统计各段对话轮数
    author_turns = [t for t in optimized_script.dialogue_turns if t.role.value == 'author']
    host_turns = [t for t in optimized_script.dialogue_turns if t.role.value == 'host']

    logger.info(f'  作者发言轮数: {len(author_turns)}')
    logger.info(f'  主持人发言轮数: {len(host_turns)}')

    # 统计发言时长
    author_duration = sum(t.duration_seconds or 0 for t in author_turns) // 60
    host_duration = sum(t.duration_seconds or 0 for t in host_turns) // 60
    logger.info(f'  作者发言时长: {author_duration}分钟')
    logger.info(f'  主持人发言时长: {host_duration}分钟')

    # 6. 测试总结
    logger.info('')
    logger.info('='*50)
    logger.info('🎉 测试总结')
    logger.info('='*50)
    logger.info('✅ 5段式流程生成: 通过')
    logger.info('✅ 脚本优化功能: 通过')
    logger.info('✅ 质量评估功能: 通过')
    logger.info('')
    logger.info('🎉 所有测试通过! 对话生成服务运行正常。')
    logger.info('')

    return True


# 运行测试
try:
    result = asyncio.run(test_dialogue_generation())
    sys.exit(0 if result else 1)
except Exception as e:
    logger.error(f'❌ 测试失败: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

# 检查结果
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ 对话生成服务测试通过"
    echo "=========================================="
    echo ""
    echo "📌 后续步骤:"
    echo "  1. 启动后端服务: ./start.sh"
    echo "  2. 访问API文档: http://localhost:8000/docs"
    echo "  3. 测试WebSocket: ws://localhost:8000/api/scripts/ws/{script_id}"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ 测试失败"
    echo "=========================================="
    echo ""
    exit 1
fi
