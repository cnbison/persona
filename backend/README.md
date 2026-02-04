# Persona生成与应用平台 - 后端服务

本服务负责文档解析、证据库构建、Persona建模与适配输出等能力的API层。

## 快速开始

### 1. 配置环境变量

编辑 `.env` 文件，填入你的 OpenAI API 密钥：

```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 2. 安装依赖

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 初始化数据库

```bash
# 数据库会在首次启动时自动创建
# 或手动运行：
python -m app.database
```

### 4. 启动服务

```bash
# 开发模式（自动重载）
uvicorn app.main:app --reload --port 8000

# 或直接运行
python -m app.main
```

### 5. 访问API文档

启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/api/health

## 项目结构

```
backend/
├── app/
│   ├── main.py              # FastAPI应用入口
│   ├── database.py          # 数据库连接管理
│   ├── api/                 # API路由层
│   │   ├── health.py        # 健康检查
│   │   ├── books.py         # 文档/著作管理
│   │   ├── personas.py      # Persona管理
│   │   ├── outlines.py      # 提纲管理
│   │   └── scripts.py       # 脚本/对话管理
│   ├── models/              # 数据模型层
│   │   ├── book.py          # 文档模型
│   │   ├── persona.py       # Persona模型
│   │   └── dialogue.py      # 对话模型
│   ├── services/            # 业务逻辑层（待完善）
│   ├── utils/               # 工具函数
│   │   └── config.py        # 配置管理
│   └── prompts/             # Prompt模板（待完善）
├── requirements.txt         # Python依赖
├── .env                     # 环境变量配置
└── logs/                    # 日志目录
```

## 开发状态

- ✅ 基础框架搭建完成
- ✅ API路由结构建立
- ✅ 数据模型定义完成 (Pydantic)
- ✅ ORM模型定义完成 (7张表)
