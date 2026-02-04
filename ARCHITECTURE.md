# 系统架构设计文档

## 一、架构总览

### 1.1 系统定位

**AI著作跨时空对话播客 - 内容生成系统**

这是一个跨平台桌面应用的内容生成部分，通过AI技术复刻经典作家人格，生成"虚拟作者+主持人"跨时空对话播客内容。

### 1.2 架构风格

**混合架构：Rust前端 + Python后端**

```
┌──────────────────────────────────────────────────────────┐
│                    用户桌面应用                           │
├──────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐    │
│  │        Rust + Tauri 前端层                       │    │
│  │  ┌──────────────┐  ┌──────────────────────┐    │    │
│  │  │  React UI    │  │  Rust Core (Tauri)   │    │    │
│  │  │  - 文件上传  │  │  - 窗口管理           │    │    │
│  │  │  - 进度展示  │  │  - 本地文件系统       │    │    │
│  │  │  - 内容预览  │  │  - SQLite本地存储     │    │    │
│  │  │  - 可视化    │  │  - 后台服务管理       │    │    │
│  │  └──────────────┘  └──────────────────────┘    │    │
│  └─────────────────────────────────────────────────┘    │
│                        ↕ IPC/HTTP (localhost)           │
├──────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐    │
│  │        Python 后端服务层                         │    │
│  │  ┌──────────────────────────────────────────┐  │    │
│  │  │  FastAPI REST API                        │  │    │
│  │  │  - 著作管理 API                          │  │    │
│  │  │  - Persona构建 API                       │  │    │
│  │  │  - 内容生成 API                          │  │    │
│  │  │  - 热点匹配 API                          │  │    │
│  │  └──────────────────────────────────────────┘  │    │
│  │                                                  │    │
│  │  ┌──────────────────────────────────────────┐  │    │
│  │  │  业务逻辑层 (Services)                    │  │    │
│  │  │  ┌──────────────┐  ┌──────────────────┐ │  │    │
│  │  │  │ 文档解析服务  │  │ Persona建模服务  │ │  │    │
│  │  │  │ - PDF解析    │  │ - 6维度分析      │ │  │    │
│  │  │  │ - EPUB解析   │  │ - System Prompt  │ │  │    │
│  │  │  │ - 清洗提取   │  │ - 观点边界       │ │  │    │
│  │  │  └──────────────┘  └──────────────────┘ │  │    │
│  │  │  ┌──────────────┐  ┌──────────────────┐ │  │    │
│  │  │  │ 提纲生成服务  │  │ 对话生成服务     │ │  │    │
│  │  │  │ - 10集规划   │  │ - 脚本生成       │ │  │    │
│  │  │  │ - 热点匹配   │  │ - 多轮优化       │ │  │    │
│  │  │  │ - 章节分配   │  │ - 质量审核       │ │  │    │
│  │  │  └──────────────┘  └──────────────────┘ │  │    │
│  │  └──────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
                          ↕ API调用
┌──────────────────────────────────────────────────────────┐
│              外部服务                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ OpenAI API   │  │ 本地文件系统  │  │ SQLite数据库  │  │
│  │ - GPT-4      │  │ - 著作存储    │  │ - 结构化数据  │  │
│  │ - 文本生成    │  │ - 生成内容    │  │ - 用户配置    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## 二、技术栈详解

### 2.1 前端技术栈

#### 2.1.1 Rust层 (Tauri Core)
```toml
[dependencies]
tauri = "2.0"              # 桌面应用框架
serde = "1.0"              # 序列化/反序列化
tokio = "1.0"              # 异步运行时
reqwest = "0.11"           # HTTP客户端
sqlx = "0.7"               # 数据库ORM
dirs = "5.0"               # 系统目录路径
```

**职责**：
- 窗口管理和系统交互
- 本地文件系统访问（著作文件、生成内容）
- SQLite数据库操作
- Python后端服务管理（启动/停止/监控）
- 与React层的IPC通信

#### 2.1.2 React UI层
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.0.0",
    "vite": "^5.0.0",
    "zustand": "^4.4.0",    // 状态管理
    "react-router-dom": "^6.20.0",  // 路由
    "@tanstack/react-query": "^5.0.0",  // 数据请求
    "shadcn/ui": "^1.0.0",   // UI组件库
    "tailwindcss": "^3.4.0"  // CSS框架
  }
}
```

**UI页面结构**：
```
/src
  /pages
    - Dashboard.tsx          # 总览仪表板
    - BookUpload.tsx         # 著作上传
    - BookList.tsx           # 著作列表
    - PersonaBuilder.tsx     # Persona构建
    - OutlineEditor.tsx      # 提纲编辑器
    - ScriptGenerator.tsx    # 脚本生成器
    - ScriptViewer.tsx       # 内容预览
    - Settings.tsx           # 设置
  /components
    - FileUploader.tsx
    - ProgressBar.tsx
    - DialogueEditor.tsx
    - HotTopicMatcher.tsx
```

### 2.2 后端技术栈

#### 2.2.1 核心依赖
```txt
fastapi==0.109.0            # Web框架
uvicorn==0.27.0             # ASGI服务器
pydantic==2.5.3             # 数据验证
sqlalchemy==2.0.25          # ORM
openai==1.12.0              # OpenAI API客户端

# 文档解析
PyPDF2==3.0.1
pdfplumber==0.10.3
ebooklib==0.18
python-docx==1.1.0

# NLP处理
jieba==0.42.1
spacy==3.7.2
nltk==3.8.1

# 数据处理
pandas==2.1.4
numpy==1.26.3

# 工具
python-dotenv==1.0.0
loguru==0.7.2
httpx==0.26.0
```

#### 2.2.2 后端项目结构
```
backend/
├── app/
│   ├── main.py                 # FastAPI入口
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库连接
│   │
│   ├── api/                    # API路由层
│   │   ├── __init__.py
│   │   ├── books.py            # 著作管理API
│   │   ├── personas.py         # Persona API
│   │   ├── outlines.py         # 提纲API
│   │   ├── scripts.py          # 脚本API
│   │   └── health.py           # 健康检查
│   │
│   ├── models/                 # 数据模型层
│   │   ├── __init__.py
│   │   ├── book.py             # 著作模型
│   │   ├── persona.py          # Persona模型
│   │   ├── dialogue.py         # 对话模型
│   │   └── schemas.py          # Pydantic schemas
│   │
│   ├── services/               # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── document_parser.py  # 文档解析服务
│   │   ├── persona_builder.py  # Persona构建服务
│   │   ├── outline_generator.py # 提纲生成服务
│   │   ├── dialogue_generator.py # 对话生成服务
│   │   ├── hot_topic_matcher.py  # 热点匹配服务
│   │   └── content_reviewer.py  # 内容审核服务
│   │
│   ├── utils/                  # 工具函数
│   │   ├── __init__.py
│   │   ├── openai_client.py    # OpenAI客户端封装
│   │   ├── text_processor.py   # 文本处理工具
│   │   ├── logger.py           # 日志工具
│   │   └── file_handler.py     # 文件处理工具
│   │
│   └── prompts/                # Prompt模板
│       ├── persona_analysis.txt
│       ├── system_context.txt
│       └── dialogue_generation.txt
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## 三、核心数据流设计

### 3.1 著作解析流程

```
┌────────────┐
│ 文件上传   │ (PDF/EPUB/TXT)
└─────┬──────┘
      ↓
┌──────────────────────────────────┐
│ 文档解析服务                      │
│ 1. 格式识别                       │
│ 2. 文本提取                       │
│ 3. 清洗（去版权、页码）           │
│ 4. 章节拆分                       │
└─────┬────────────────────────────┘
      ↓
┌──────────────────────────────────┐
│ NLP分析                          │
│ 1. 分词、词性标注                 │
│ 2. 核心观点提取                   │
│ 3. 关键词提取                     │
│ 4. 建立索引                       │
└─────┬────────────────────────────┘
      ↓
┌────────────┐
│ 存入SQLite │
└────────────┘
```

### 3.2 Persona构建流程

```
┌────────────┐
│ 著作数据    │
└─────┬──────┘
      ↓
┌──────────────────────────────────┐
│ 6维度分析（调用GPT-4）            │
│ 1. 思维方式：归纳/演绎/辩证       │
│ 2. 思想体系：核心哲学/理论框架    │
│ 3. 叙事风格：语言节奏/修辞        │
│ 4. 价值观：价值立场/判断框架      │
│ 5. 语气：温和/激烈/谦逊           │
│ 6. 性格：特质/沟通风格            │
└─────┬────────────────────────────┘
      ↓
┌──────────────────────────────────┐
│ 生成System Prompt                │
│ - 角色定义                       │
│ - 行为约束                       │
│ - 观点边界                       │
└─────┬────────────────────────────┘
      ↓
┌────────────┐
│ 存入数据库  │
└────────────┘
```

### 3.3 内容生成流程

```
┌──────────────┐
│ 选择著作+Persona│
└──────┬───────┘
       ↓
┌──────────────────────────────────┐
│ 生成10集提纲（GPT-4）             │
│ 1. 分析著作结构                  │
│ 2. 分配章节到各集                │
│ 3. 匹配热点话题                  │
│ 4. 定义讨论重点                  │
└──────┬───────────────────────────┘
       ↓
┌──────────────────────────────────┐
│ 用户审核/调整提纲                 │
└──────┬───────────────────────────┘
       ↓
┌──────────────────────────────────┐
│ 生成对话脚本（逐集）              │
│ 1. 加载System Context            │
│ 2. 加载作者/主持人System Prompt  │
│ 3. 多轮对话生成                  │
│ 4. 观点校验                      │
│ 5. 语言优化                      │
└──────┬───────────────────────────┘
       ↓
┌────────────┐
│ 输出脚本    │
└────────────┘
```

---

## 四、API接口设计

### 4.1 著作管理API

```python
# 著作上传
POST /api/books/upload
Request: multipart/form-data (file)
Response: {book_id, title, author, status}

# 获取著作列表
GET /api/books
Response: [{book_id, title, author, status, created_at}]

# 获取著作详情
GET /api/books/{book_id}
Response: {book_id, chapters, core_viewpoints, analysis}

# 删除著作
DELETE /api/books/{book_id}
```

### 4.2 Persona构建API

```python
# 创建Persona
POST /api/personas
Request: {book_id, persona_name}
Response: {persona_id, status}

# 获取Persona详情
GET /api/personas/{persona_id}
Response: {6维度特征, system_prompt}

# 更新Persona
PUT /api/personas/{persona_id}
Request: {dimension_updates}

# 生成System Prompt
POST /api/personas/{persona_id}/generate-prompt
Response: {system_prompt}
```

### 4.3 提纲生成API

```python
# 生成10集提纲
POST /api/outlines/generate
Request: {book_id, persona_id}
Response: {outline_id, episodes: [{episode_number, theme, chapters, hot_topics}]}

# 更新单集提纲
PUT /api/outlines/{outline_id}/episodes/{episode_number}
Request: {theme, hot_topics, discussion_points}

# 获取完整提纲
GET /api/outlines/{outline_id}
Response: {outline_id, book_id, all_episodes}
```

### 4.4 对话生成API

```python
# 生成单集脚本
POST /api/scripts/generate
Request: {outline_id, episode_number}
Response: {script_id, status}

# 查询生成进度
GET /api/scripts/{script_id}/progress
Response: {percentage, current_step, eta}

# 获取生成的脚本
GET /api/scripts/{script_id}
Response: {dialogue_turns, quality_metrics, duration}

# 导出脚本
GET /api/scripts/{script_id}/export
Response: File (TXT/MD/JSON)
```

### 4.5 热点匹配API

```python
# 获取推荐热点
GET /api/hot-topics/recommend
Query: viewpoint_id
Response: [{title, relevance_score, connection_point}]

# 手动添加热点
POST /api/hot-topics/add
Request: {title, description, url}
```

---

## 五、数据库设计

### 5.1 表结构

#### books (著作表)
```sql
CREATE TABLE books (
    book_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    language TEXT DEFAULT 'zh',
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL,
    total_words INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending',  -- pending/analyzing/completed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### chapters (章节表)
```sql
CREATE TABLE chapters (
    chapter_id TEXT PRIMARY KEY,
    book_id TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    page_range TEXT,
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);
```

#### core_viewpoints (核心观点表)
```sql
CREATE TABLE core_viewpoints (
    viewpoint_id TEXT PRIMARY KEY,
    book_id TEXT NOT NULL,
    chapter_id TEXT NOT NULL,
    content TEXT NOT NULL,
    original_text TEXT NOT NULL,
    context TEXT,
    keywords TEXT,  -- JSON array
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (chapter_id) REFERENCES chapters(chapter_id)
);
```

#### personas (作者Persona表)
```sql
CREATE TABLE personas (
    persona_id TEXT PRIMARY KEY,
    author_name TEXT NOT NULL,
    book_id TEXT NOT NULL,
    thinking_style TEXT,
    core_philosophy TEXT,
    narrative_style TEXT,
    value_system TEXT,  -- JSON
    tone TEXT,
    personality_traits TEXT,  -- JSON array
    viewpoint_boundaries TEXT,  -- JSON
    system_prompt TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);
```

#### outlines (提纲表)
```sql
CREATE TABLE outlines (
    outline_id TEXT PRIMARY KEY,
    book_id TEXT NOT NULL,
    persona_id TEXT NOT NULL,
    total_episodes INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (persona_id) REFERENCES personas(persona_id)
);
```

#### episodes (单集提纲表)
```sql
CREATE TABLE episodes (
    episode_id TEXT PRIMARY KEY,
    outline_id TEXT NOT NULL,
    episode_number INTEGER NOT NULL,
    theme TEXT NOT NULL,
    target_chapters TEXT,  -- JSON array
    target_viewpoints TEXT,  -- JSON array
    hot_topics TEXT,  -- JSON array
    discussion_points TEXT,  -- JSON array
    estimated_duration INTEGER DEFAULT 30,
    FOREIGN KEY (outline_id) REFERENCES outlines(outline_id)
);
```

#### scripts (对话脚本表)
```sql
CREATE TABLE scripts (
    script_id TEXT PRIMARY KEY,
    episode_id TEXT NOT NULL,
    dialogue_turns TEXT NOT NULL,  -- JSON array
    total_duration INTEGER NOT NULL,
    total_word_count INTEGER NOT NULL,
    quality_metrics TEXT,  -- JSON
    status TEXT DEFAULT 'pending',  -- pending/generating/completed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (episode_id) REFERENCES episodes(episode_id)
);
```

---

## 六、安全与性能

### 6.1 安全措施

1. **API密钥管理**
   - OpenAI API密钥存储在环境变量
   - 不在代码中硬编码敏感信息

2. **输入验证**
   - 所有API请求使用Pydantic验证
   - 文件上传限制大小和类型

3. **内容审核**
   - 生成内容经过敏感词过滤
   - 价值观合规检查

4. **本地数据保护**
   - SQLite数据库加密（可选）
   - 用户数据不主动上传云端

### 6.2 性能优化

1. **异步处理**
   - FastAPI使用async/await
   - 长时间任务（如文档解析）后台处理

2. **缓存策略**
   - OpenAI响应缓存（避免重复调用）
   - 著作分析结果缓存

3. **流式生成**
   - 对话脚本采用流式生成
   - 实时展示生成进度

4. **并发控制**
   - 限制同时处理的著作数量
   - API请求速率限制

---

## 七、部署方案

### 7.1 开发环境

```bash
# 前端（Rust + Tauri）
cd frontend
npm install
npm run tauri dev

# 后端（Python）
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 7.2 生产打包

#### 前端打包（Tauri）
```bash
cd frontend
npm run tauri build
# 输出：frontend/src-tauri/target/release/bundle/
```

#### 后端打包（PyInstaller）
```bash
cd backend
pip install pyinstaller
pyinstaller --onefile --name dialogue-backend app/main.py
```

#### 集成打包
- 方案A：Python后端内嵌到Tauri应用
- 方案B：首次运行自动安装Python环境
- 方案C：提供独立安装器

### 7.3 更新机制

- Tauri内置更新器
- 版本检查：`GET /api/version`
- 增量更新支持

---

## 八、监控与日志

### 8.1 日志系统

```python
from loguru import logger

logger.add("logs/app_{time}.log", rotation="10 MB", retention="30 days")
```

### 8.2 性能监控

- API响应时间
- OpenAI调用次数和成本
- 生成任务成功率
- 系统资源使用

### 8.3 错误追踪

- 完整错误堆栈
- 用户操作路径
- 自动上报（可选）

---

## 九、扩展性设计

### 9.1 未来扩展功能

1. **云端同步**（可选）
   - 用户账号系统
   - 内容云端备份
   - 多设备同步

2. **本地AI模型**（可选）
   - 集成轻量级模型（如llama.cpp）
   - 离线推理能力
   - 向量检索（RAG）

3. **多语言支持**
   - i18n国际化
   - 多语言著作解析

4. **协作功能**
   - 多人协同编辑
   - 评论批注系统

### 9.2 插件系统

- Prompt模板插件
- 自定义解析器
- 第三方服务集成

---

## 十、技术风险与应对

| 风险 | 影响 | 应对 |
|------|------|------|
| Rust学习曲线陡峭 | 开发周期长 | Tauri主要写React，Rust代码少 |
| OpenAI API限流 | 生成失败 | 实现重试机制、队列管理 |
| 文档解析失败 | 内容缺失 | 多种解析工具组合、人工校验 |
| 生成内容质量差 | 用户体验差 | 多轮优化、人工审核、反馈改进 |
| 打包体积过大 | 下载困难 | 精简依赖、延迟加载 |

---

**文档版本**: v1.0
**最后更新**: 2025-01-25
