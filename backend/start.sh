#!/bin/bash
# 后端服务启动脚本

echo "🚀 启动AI著作跨时空对话播客后端服务..."

# 进入backend目录
cd "$(dirname "$0")"

# 设置PYTHONPATH
export PYTHONPATH="$(pwd)"

echo "📍 当前目录: $(pwd)"
echo "🐍 PYTHONPATH: $PYTHONPATH"

# 检查是否在虚拟环境中
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo "⚠️  建议在虚拟环境中运行"
    echo "   创建虚拟环境: python3 -m venv venv"
    echo "   激活虚拟环境: source venv/bin/activate"
fi

# 启动服务
echo "📡 启动FastAPI服务 (http://localhost:8000)"
echo "📚 API文档: http://localhost:8000/docs"
echo ""

python3 -m uvicorn app.main:app --reload --port 8000
