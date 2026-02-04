#!/bin/bash
# 快速测试脚本

# 进入backend目录
cd "$(dirname "$0")"

# 设置PYTHONPATH
export PYTHONPATH="$(pwd)"

echo "🧪 测试AI著作跨时空对话播客后端"
echo "=================================="
echo ""

# 检查虚拟环境
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo "⚠️  警告：未检测到虚拟环境"
    echo "   建议运行: source venv/bin/activate"
    echo ""
fi

# 显示测试菜单
echo "请选择要测试的模块："
echo "1) OpenAI客户端（需要真实API密钥）"
echo "2) 文本处理工具"
echo "3) 文件处理工具"
echo "4) 文档解析服务"
echo "5) Persona构建服务"
echo "6) 提纲生成服务"
echo "7) 对话生成服务"
echo "8) 启动FastAPI服务"
echo "9) 退出"
echo ""
read -p "请输入选项 (1-9): " choice

case $choice in
    1)
        echo ""
        echo "🤖 测试OpenAI客户端..."
        python app/utils/openai_client.py
        ;;
    2)
        echo ""
        echo "📝 测试文本处理工具..."
        python app/utils/text_processor.py
        ;;
    3)
        echo ""
        echo "📁 测试文件处理工具..."
        python app/utils/file_handler.py
        ;;
    4)
        echo ""
        echo "📖 测试文档解析服务..."
        python app/services/document_parser.py
        ;;
    5)
        echo ""
        echo "🧠 测试Persona构建服务..."
        python app/services/persona_builder.py
        ;;
    6)
        echo ""
        echo "📋 测试提纲生成服务..."
        python app/services/outline_generator.py
        ;;
    7)
        echo ""
        echo "💬 测试对话生成服务..."
        python app/services/dialogue_generator.py
        ;;
    8)
        echo ""
        echo "🚀 启动FastAPI服务..."
        echo "   访问: http://localhost:8000/docs"
        echo ""
        python -m uvicorn app.main:app --reload --port 8000
        ;;
    9)
        echo "👋 退出"
        exit 0
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac
