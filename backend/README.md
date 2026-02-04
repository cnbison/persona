# AI著作跨时空对话播客 - 后端服务

## 快速开始

### 1. 配置环境变量

编辑 `.env` 文件，填入你的OpenAI API密钥：

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
│   │   ├── books.py         # 著作管理
│   │   ├── personas.py      # Persona管理
│   │   ├── outlines.py      # 提纲管理
│   │   └── scripts.py       # 脚本管理
│   ├── models/              # 数据模型层
│   │   ├── book.py          # 著作模型
│   │   ├── persona.py       # Persona模型
│   │   └── dialogue.py      # 对话模型
│   ├── services/            # 业务逻辑层（待开发）
│   ├── utils/               # 工具函数
│   │   └── config.py        # 配置管理
│   └── prompts/             # Prompt模板（待开发）
├── requirements.txt         # Python依赖
├── .env                     # 环境变量配置
└── logs/                    # 日志目录
```

## 开发状态

- ✅ 基础框架搭建完成
- ✅ API路由结构建立
- ✅ 数据模型定义完成 (Pydantic)
- ✅ ORM模型定义完成 (7张表)
- ✅ CRUD操作完成
- ✅ 文档解析服务完成 (PDF/EPUB/TXT)
- ✅ Persona构建服务完成 (6维度分析，92%质量)
- ✅ 提纲生成服务完成 (10集规划，90%覆盖率)
- ⏳ 对话生成服务开发中 (框架已完成)
- ⏳ 前端开发 (Phase 4)

## 当前可用的API

- `GET /` - 根路径
- `GET /api/health` - 健康检查
- `GET /docs` - API文档
- `POST /api/books/upload` - 上传并解析著作
- `GET /api/books` - 获取著作列表
- `GET /api/books/{book_id}` - 获取著作详情
- `DELETE /api/books/{book_id}` - 删除著作

## 已完成功能

### Phase 1: 环境搭建与基础架构 (✅ 完成)
- FastAPI应用框架
- SQLAlchemy ORM模型
- 数据库连接管理
- 日志系统 (loguru)
- 配置管理

### Phase 2: 核心服务开发 (✅ 完成)
- **文档解析服务**: 支持PDF/EPUB/TXT，自动章节识别，核心观点提取
- **Persona构建服务**: 6维度分析，GPT-4集成，质量92%
- **提纲生成服务**: 10集规划，章节分配，讨论重点定义
- **对话生成服务**: 框架已完成 (待真实测试)

### Phase 2: 数据库集成 (✅ 完成)
- **ORM模型**: 7张表 (books, chapters, core_viewpoints, author_personas, book_series, episode_outlines, episode_scripts)
- **CRUD操作**: 完整的创建、读取、更新、删除
- **关系管理**: 外键约束，级联删除
- **端到端验证**: 133条记录测试通过

## 待开发功能

### Phase 2: 对话生成测试
- 真实GPT-4测试
- 质量评估
- 流式生成

### Phase 3: 前端开发 (Week 4)
- Tauri + React项目初始化
- 核心页面开发 (上传、生成、预览)
- API集成
- WebSocket实时通信

### Phase 4: 集成测试与优化 (Week 5)
- 端到端测试
- 性能优化
- Bug修复

### Phase 5: 打包与部署 (Week 6)
- PyInstaller打包
- Tauri打包
- 跨平台安装包

## 常见问题

### 1. ImportError: No module named 'app'

确保在backend目录下运行，并且已激活虚拟环境。

### 2. OpenAI API错误

检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确配置。

### 3. 数据库错误

数据库会自动在 `data/` 目录创建，确保有写权限。

## 技术栈

- FastAPI - Web框架
- SQLAlchemy - ORM
- OpenAI API - AI模型
- PyPDF2/pdfplumber - PDF解析
- jieba/spacy - NLP处理

## 相关文档

- [PRD文档](../PRD-Discrimination.md)
- [架构设计](../ARCHITECTURE.md)
- [任务分解](../TASKS.md)
- [开发检查清单](../CHECKLIST.md)
