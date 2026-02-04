# 开发任务分解文档

> **最新更新**: 2025-01-25
> **当前状态**: Phase 2 (Week 2-3) 进行中
> **已完成**: 选项A (Persona优化) ✅ | 选项B (提纲生成) ✅ | 选项C (数据库集成) ✅
> **进行中**: 选项D (前端开发)
> **总体进度**: 60%

---

## 一、开发阶段总览

```
Phase 1: 环境搭建与基础架构 (Week 1)
  ├─ Day 1-2: 项目初始化
  ├─ Day 3-4: 数据库设计与实现
  └─ Day 5-7: 基础服务搭建

Phase 2: 后端核心功能开发 (Week 2-3)
  ├─ Week 2: 文档解析 + Persona构建
  └─ Week 3: 提纲生成 + 对话生成

Phase 3: 前端UI开发 (Week 4)
  ├─ Day 1-3: Tauri项目搭建
  ├─ Day 4-5: 核心页面开发
  └─ Day 6-7: API对接

Phase 4: 集成测试与优化 (Week 5)
  ├─ Day 1-3: 端到端测试
  ├─ Day 4-5: 性能优化
  └─ Day 6-7: Bug修复

Phase 5: 打包与部署 (Week 6)
  ├─ Day 1-2: 应用打包
  ├─ Day 3-4: 安装器制作
  └─ Day 5-7: 文档与上线
```

---

## 二、Phase 1: 环境搭建与基础架构 (Week 1)

### 2.1 Day 1-2: 项目初始化

#### 任务1.1: 创建项目结构
- [ ] 创建根目录结构
  ```bash
  discrimination/
  ├── frontend/          # Tauri + React前端
  ├── backend/           # Python后端
  ├── books/            # 著作文件存储
  ├── data/             # 数据存储
  ├── logs/             # 日志
  └── docs/             # 文档
  ```
- [ ] 初始化Git仓库
- [ ] 创建.gitignore文件
- [ ] 创建README.md（项目说明）

#### 任务1.2: 后端环境搭建
- [ ] 创建Python虚拟环境
  ```bash
  cd backend
  python3 -m venv venv
  source venv/bin/activate
  ```
- [ ] 创建requirements.txt
- [ ] 安装核心依赖
  - FastAPI
  - SQLAlchemy
  - OpenAI
  - PyPDF2, pdfplumber, ebooklib
  - jieba, spacy
- [ ] 创建.env配置文件
- [ ] 测试依赖安装是否成功

#### 任务1.3: 数据库设计实现
- [ ] 设计数据库Schema（参考ARCHITECTURE.md）
- [ ] 创建SQLAlchemy模型
  - models/book.py
  - models/persona.py
  - models/dialogue.py
- [ ] 创建数据库连接管理
  - database.py
  - 初始化脚本
- [ ] 创建数据库迁移系统（可选：Alembic）
- [ ] 测试数据库连接和基本CRUD

#### 任务1.4: FastAPI基础框架
- [ ] 创建FastAPI应用入口
  ```python
  # app/main.py
  from fastapi import FastAPI
  app = FastAPI(title="AI对话播客后端")
  ```
- [ ] 配置CORS中间件（允许前端访问）
- [ ] 创建基础路由结构
  - api/books.py
  - api/personas.py
  - api/outlines.py
  - api/scripts.py
- [ ] 实现健康检查API: `GET /api/health`
- [ ] 添加API文档（Swagger UI自动生成）
- [ ] 测试API可访问性

#### 任务1.5: 日志与错误处理
- [ ] 配置loguru日志系统
  - 日志文件按日期分割
  - 控制台输出格式化
- [ ] 创建全局异常处理器
- [ ] 实现统一响应格式
  ```python
  {"code": 200, "message": "success", "data": {...}}
  ```
- [ ] 测试日志记录和异常处理

**验收标准**:
- ✅ 后端服务可以启动（`uvicorn app.main:app`）
- ✅ 访问 http://localhost:8000/docs 能看到API文档
- ✅ 数据库表创建成功
- ✅ 健康检查API返回正常

---

### 2.2 Day 3-4: 工具层开发

#### 任务2.1: OpenAI客户端封装
- [ ] 创建utils/openai_client.py
  - 封装GPT-4调用
  - 实现重试机制（3次重试，指数退避）
  - 实现流式响应支持
  - 添加Token使用统计
- [ ] 创建Prompt模板管理
  - prompts/目录
  - 模板加载函数
  - 变量替换功能
- [ ] 测试OpenAI API调用
- [ ] 记录API调用成本（日志）

#### 任务2.2: 文本处理工具
- [ ] 创建utils/text_processor.py
  - 中文分词（jieba）
  - 文本清洗函数（去空白、去特殊字符）
  - 文本截断与分段
  - 关键词提取（TF-IDF或jieba.extract_tags）
- [ ] 创建utils/file_handler.py
  - 文件上传处理
  - 文件类型验证
  - 文件大小限制（max: 50MB）
- [ ] 单元测试

**验收标准**:
- ✅ OpenAI调用成功，能获取响应
- ✅ 文本处理函数无报错
- ✅ 单元测试通过

---

### 2.3 Day 5-7: 核心服务框架（骨架）

#### 任务3.1: 文档解析服务骨架
- [ ] 创建services/document_parser.py
  - 定义接口: `parse_book(file_path) -> Book`
  - 定义抽象基类
  - 创建占位实现（返回假数据）
- [ ] 创建API路由
  - POST /api/books/upload
  - GET /api/books
  - GET /api/books/{book_id}
- [ ] 测试API（用假数据）

#### 任务3.2: Persona构建服务骨架
- [ ] 创建services/persona_builder.py
  - 定义接口: `build_persona(book) -> Persona`
  - 创建占位实现
- [ ] 创建API路由
  - POST /api/personas
  - GET /api/personas/{persona_id}
- [ ] 测试API

#### 任务3.3: 提纲生成服务骨架
- [ ] 创建services/outline_generator.py
  - 定义接口: `generate_outline(book, persona) -> Outline`
  - 创建占位实现
- [ ] 创建API路由
  - POST /api/outlines/generate
- [ ] 测试API

#### 任务3.4: 对话生成服务骨架
- [ ] 创建services/dialogue_generator.py
  - 定义接口: `generate_script(episode) -> Script`
  - 创建占位实现
- [ ] 创建API路由
  - POST /api/scripts/generate
  - GET /api/scripts/{script_id}/progress
- [ ] 测试API

**验收标准**:
- ✅ 所有核心服务的API可调用
- ✅ 返回符合数据结构的假数据
- ✅ API文档完整

---

## 三、Phase 2: 后端核心功能开发 (Week 2-3)

### 3.1 Week 2: 文档解析 + Persona构建

#### Day 8-10: 文档解析实现

**任务4.1: PDF解析器**
- [ ] 实现PDF文本提取（pdfplumber）
  - 处理多栏布局
  - 处理页眉页脚
  - 识别章节标题
- [ ] 实现OCR支持（如果需要扫描版）
  - 集成pytesseract
  - 图像预处理
- [ ] 测试解析准确性
  - 用《理想国》、《乡土中国》测试
  - 目标准确率≥95%

**任务4.2: EPUB/TXT解析器**
- [ ] 实现EPUB解析（ebooklib）
  - 提取章节结构
  - 提取元数据
- [ ] 实现TXT解析
  - 识别章节标题（正则匹配）
- [ ] 测试各种格式

**任务4.3: 内容清洗与结构化**
- [ ] 实现冗余信息过滤
  - 去除版权声明
  - 去除页码
  - 去除无关批注
- [ ] 实现章节拆分
  - 自动识别章节边界
  - 手动调整支持
- [ ] 实现核心观点提取（NLP）
  - 使用jieba分词
  - 提取关键句子（TextRank算法）
  - 关联原文片段
- [ ] 存储到数据库

**验收标准**:
- ✅ 能解析PDF、EPUB、TXT格式
- ✅ 解析准确率≥95%
- ✅ 章节拆分正确率≥90%
- ✅ 核心观点提取完整度≥80%

---

#### Day 11-14: Persona构建实现

**任务5.1: 6维度分析实现**
- [ ] 创建Prompt模板（prompts/persona_analysis.txt）
  - 思维方式分析Prompt
  - 思想体系分析Prompt
  - 叙事风格分析Prompt
  - 价值观分析Prompt
  - 语气分析Prompt
  - 性格分析Prompt
- [ ] 实现6维度分析函数
  ```python
  def analyze_persona_dimensions(book: Book) -> Persona:
      # 逐维度调用GPT-4
      # 组合结果
  ```
- [ ] 实现观点边界提取
  - 核心立场
  - 反对观点
  - 未表态领域
- [ ] 测试分析准确性（用《理想国》测试柏拉图人格）

**任务5.2: System Prompt生成**
- [ ] 设计System Prompt模板
  - 角色定义部分
  - 约束条件部分
  - 示例对话部分
- [ ] 实现自动生成函数
  ```python
  def generate_system_prompt(persona: Persona) -> str:
      # 根据Persona生成
  ```
- [ ] 实现主持人Persona
  - 固定模板 + 动态调整
- [ ] 测试Prompt效果

**任务5.3: 观点校验机制**
- [ ] 实现原文锚定校验
  ```python
  def validate_viewpoint(viewpoint: str, original_text: str) -> bool:
      # 调用GPT-4校验一致性
  ```
- [ ] 实现观点边界检查
  - 检查是否违背核心主张
  - 检查是否涉及反对观点
- [ ] 实现动态修正
  - 自动修正轻微偏差
  - 严重偏差触发人工审核

**验收标准**:
- ✅ 6维度分析完整
- ✅ System Prompt生成成功
- ✅ 观点校验准确率≥95%
- ✅ 生成的人格与历史认知一致性≥85%（专家评审）

---

### 3.2 Week 3: 提纲生成 + 对话生成

#### Day 15-17: 提纲生成实现

**任务6.1: 10集提纲生成**
- [ ] 创建提纲生成Prompt
  - 分析著作章节结构
  - 规划10集主题
  - 分配章节到各集
  - 定义讨论重点
- [ ] 实现生成逻辑
  ```python
  def generate_10_episode_outline(book: Book, persona: Persona) -> Outline:
      # 调用GPT-4生成完整提纲
      # 验证覆盖度≥90%
  ```
- [ ] 实现手动调整API
  - 修改主题
  - 重新分配章节
  - 调整讨论重点
- [ ] 测试提纲质量

**任务6.2: 热点匹配功能**
- [ ] 创建热点数据源
  - 方案A: 爬虫爬取热点（微博、知乎）
  - 方案B: 手动维护热点库
  - 方案C: 调用第三方API
- [ ] 实现智能匹配算法
  ```python
  def match_hot_topics(viewpoint: str) -> List[HotTopic]:
      # 向量化检索或关键词匹配
      # 计算相关性评分
  ```
- [ ] 实现推荐与筛选
  - 相关性阈值≥0.8
  - 适配性评分
  - 手动添加/删除
- [ ] 测试匹配准确性

**验收标准**:
- ✅ 10集提纲覆盖著作核心内容≥90%
- ✅ 热点匹配相关性≥85%
- ✅ 手动调整功能正常

---

#### Day 18-21: 对话生成实现

**任务7.1: System Context设计**
- [ ] 设计对话流程模板
  - 开场引入（3分钟）
  - 著作探讨（10分钟）
  - 热点连接（8分钟）
  - 深度思辨（10分钟）
  - 总结升华（4分钟）
- [ ] 创建System Context Prompt
  - 定义角色互动规则
  - 定义发言时长比例（作者60%、主持人40%）
  - 定义热点融合方式
- [ ] 测试Context效果

**任务7.2: 多轮对话生成**
- [ ] 实现对话生成逻辑
  ```python
  def generate_dialogue_episode(episode: Episode) -> Script:
      # 加载System Context
      # 加载作者/主持人System Prompt
      # 多轮对话生成（GPT-4）
      # 实时观点校验
  ```
- [ ] 实现流式生成
  - 实时返回生成进度
  - WebSocket推送进度
- [ ] 实现发言时长控制
  - 根据字数估算时长
  - 动态调整发言比例

**任务7.3: 内容优化**
- [ ] 实现语言润色
  - 优化连贯性
  - 统一角色风格
  - 去除重复
- [ ] 实现质量评估
  ```python
  def evaluate_script_quality(script: Script) -> Dict[str, float]:
      # 观点准确性
      # 人格一致性
      # 热点融合自然度
      # 内容连贯性
  ```
- [ ] 实现内容审核
  - 敏感词过滤
  - 价值观检查
  - 合规性校验

**任务7.4: 导出功能**
- [ ] 实现多格式导出
  - TXT（纯文本）
  - Markdown（格式化）
  - JSON（结构化）
- [ ] 添加元数据导出
  - 原文引用索引
  - 热点关联
  - 时长标记

**验收标准**:
- ✅ 单集生成时间≤10分钟
- ✅ 作者风格还原度≥88%
- ✅ 热点融合自然度≥90%
- ✅ 质量评估4项指标均≥85分

---

## 四、Phase 3: 前端UI开发 (Week 4)

### 4.1 Day 22-24: Tauri项目搭建

#### 任务8.1: 初始化Tauri项目
- [ ] 安装Rust工具链
  ```bash
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
  ```
- [ ] 创建Tauri + React项目
  ```bash
  npm create tauri-app@latest
  cd frontend
  npm install
  ```
- [ ] 配置package.json
  - 添加UI框架依赖
  - 配置TypeScript
  - 配置Vite

#### 任务8.2: React基础框架
- [ ] 安装UI组件库
  - shadcn/ui 或 Ant Design
  - TailwindCSS
- [ ] 配置路由（React Router）
  - /dashboard
  - /books
  - /personas
  - /outlines
  - /scripts
  - /settings
- [ ] 配置状态管理（Zustand）
  - 全局状态：books, personas, outlines
  - API请求状态
- [ ] 创建布局组件
  - 侧边栏导航
  - 顶部栏
  - 内容区域

#### 任务8.3: Tauri后端（Rust）
- [ ] 实现Tauri Command
  ```rust
  #[tauri::command]
  async fn start_backend_service() -> Result<String, String> {
      // 启动Python后端
  }
  ```
- [ ] 实现文件系统访问
  - 读取著作文件
  - 保存生成内容
- [ ] 实现SQLite操作（可选）
  - 如果前端直接操作数据库
- [ ] 测试Rust-React通信

**验收标准**:
- ✅ Tauri应用可启动
- ✅ React页面可访问
- ✅ Rust Command可调用
- ✅ 窗口基本操作（最小化、关闭）正常

---

### 4.2 Day 25-27: 核心页面开发

#### 任务9.1: Dashboard仪表板
- [ ] 创建Dashboard页面
  - 统计卡片：著作数、生成中、已完成
  - 最近任务列表
  - 快速操作按钮
- [ ] 实现数据可视化
  - 生成进度图表
  - Token使用统计
- [ ] 响应式布局

#### 任务9.2: 著作管理页面
- [ ] 创建BookList页面
  - 著作列表展示（表格/卡片）
  - 搜索/筛选功能
  - 删除操作
- [ ] 创建BookUpload页面
  - 文件上传组件（拖拽支持）
  - 上传进度条
  - 文件信息展示
- [ ] 创建BookDetail页面
  - 著作基本信息
  - 章节列表
  - 核心观点列表
- [ ] 对接后端API

#### 任务9.3: Persona构建页面
- [ ] 创建PersonaList页面
  - Persona卡片展示
  - 6维度可视化（雷达图）
- [ ] 创建PersonaBuilder页面
  - 选择著作
  - 6维度展示（可编辑）
  - System Prompt预览
  - 生成按钮
- [ ] 实时进度展示
- [ ] 对接后端API

**验收标准**:
- ✅ 所有页面可访问
- ✅ UI组件渲染正常
- ✅ 响应式布局适配

---

### 4.3 Day 28-30: API对接与功能完善

#### 任务10.1: API请求封装
- [ ] 创建API客户端
  ```typescript
  // api/client.ts
  const apiClient = axios.create({
    baseURL: 'http://localhost:8000/api',
    timeout: 30000,
  })
  ```
- [ ] 实现请求拦截器
  - 自动添加认证头（未来）
  - 错误处理
- [ ] 实现响应拦截器
  - 统一格式化
  - 自动Toast提示
- [ ] 实现所有API调用函数
  - books API
  - personas API
  - outlines API
  - scripts API

#### 任务10.2: 提纲编辑页面
- [ ] 创建OutlineEditor页面
  - 10集提纲展示（Timeline/列表）
  - 单集详情编辑
  - 热点匹配组件
  - 拖拽调整集数顺序
- [ ] 实现保存/更新功能
- [ ] 实时预览

#### 任务10.3: 脚本生成页面
- [ ] 创建ScriptGenerator页面
  - 选择提纲
  - 选择生成集数
  - 生成控制（开始/暂停/停止）
  - 进度条 + 实时日志
- [ ] 创建ScriptViewer页面
  - 对话脚本展示（对话气泡）
  - 高亮原文引用
  - 高亮热点关联
  - 导出按钮（TXT/MD/JSON）
- [ ] 实现WebSocket连接
  - 接收生成进度
  - 实时更新UI

#### 任务10.4: 设置页面
- [ ] 创建Settings页面
  - OpenAI API配置
  - 文件路径配置
  - 日志级别配置
  - 关于信息
- [ ] 实现配置持久化（localStorage）

**验收标准**:
- ✅ 所有API调用成功
- ✅ 错误处理完善
- ✅ WebSocket实时通信正常
- ✅ 生成进度实时展示

---

## 五、Phase 4: 集成测试与优化 (Week 5)

### 5.1 Day 31-33: 端到端测试

#### 任务11.1: 完整流程测试
- [ ] 测试著作上传流程
  - 上传《理想国》
  - 检查解析结果
- [ ] 测试Persona构建
  - 为《理想国》构建柏拉图人格
  - 检查6维度准确性
- [ ] 测试提纲生成
  - 生成10集提纲
  - 检查覆盖度和逻辑性
- [ ] 测试脚本生成
  - 生成第1集脚本
  - 检查质量和时长
- [ ] 测试导出功能
  - 导出为各种格式
  - 验证文件内容

#### 任务11.2: 边界测试
- [ ] 大文件测试（>50MB）
- [ ] 特殊字符测试
- [ ] 网络异常测试（断网、超时）
- [ ] 并发请求测试
- [ ] 错误输入测试

#### 任务11.3: 性能测试
- [ ] 测试解析速度
  - 10MB PDF解析时间
- [ ] 测试生成速度
  - 单集脚本生成时间
  - 10集批量生成时间
- [ ] 测试内存占用
- [ ] 测试CPU占用

**验收标准**:
- ✅ 完整流程无报错
- ✅ 边界情况有友好提示
- ✅ 性能指标达到要求

---

### 5.2 Day 34-35: 性能优化

#### 任务12.1: 后端优化
- [ ] 实现异步任务队列
  - 使用Celery或BackgroundTasks
  - 长时间任务后台处理
- [ ] 实现缓存机制
  - OpenAI响应缓存
  - 著作分析结果缓存
- [ ] 优化数据库查询
  - 添加索引
  - 使用join减少查询次数
- [ ] 优化日志输出
  - 减少冗余日志
  - 异步写入

#### 任务12.2: 前端优化
- [ ] 实现虚拟滚动（长列表）
- [ ] 实现懒加载
- [ ] 优化大文件上传
  - 分片上传
  - 进度展示
- [ ] 优化渲染性能
  - React.memo
  - useMemo/useCallback

**验收标准**:
- ✅ 单集生成时间≤10分钟
- ✅ UI响应时间<500ms
- ✅ 内存占用<1GB

---

### 5.3 Day 36-37: Bug修复与完善

#### 任务13.1: Bug修复
- [ ] 修复测试中发现的Bug
- [ ] 完善错误提示
- [ ] 添加操作确认（删除等危险操作）
- [ ] 优化用户体验细节

#### 任务13.2: 功能完善
- [ ] 添加快捷键支持
- [ ] 添加操作引导（首次使用）
- [ ] 添加帮助文档
- [ ] 实现配置导入/导出

---

## 六、Phase 5: 打包与部署 (Week 6)

### 6.1 Day 38-39: 应用打包

#### 任务14.1: 后端打包
- [ ] 使用PyInstaller打包Python后端
  ```bash
  pyinstaller --onefile --windowless backend/app/main.py
  ```
- [ ] 测试打包后的可执行文件
- [ ] 解决依赖问题

#### 任务14.2: 前端打包
- [ ] 使用Tauri打包
  ```bash
  cd frontend
  npm run tauri build
  ```
- [ ] 生成多平台安装包
  - Windows: .exe
  - macOS: .dmg
  - Linux: .AppImage
- [ ] 测试安装包
- [ ] 检查应用签名（macOS/Windows）

#### 任务14.3: 集成打包
- [ ] 将Python后端嵌入Tauri应用
- [ ] 实现首次启动自动安装后端
- [ ] 配置自动更新
- [ ] 测试完整安装流程

**验收标准**:
- ✅ 安装包可正常安装
- ✅ 应用可独立运行（无需额外安装Python）
- ✅ 跨平台打包成功

---

### 6.2 Day 40-41: 文档与发布

#### 任务15.1: 用户文档
- [ ] 编写用户手册
  - 快速开始指南
  - 功能说明
  - 常见问题
- [ ] 录制演示视频
- [ ] 创建截图教程

#### 任务15.2: 开发文档
- [ ] 完善README.md
- [ ] 编写API文档
- [ ] 编写架构文档
- [ ] 编写部署文档

#### 任务15.3: 发布准备
- [ ] 准备发布说明（CHANGELOG）
- [ ] 创建GitHub Release
- [ ] 上传安装包
- [ ] 配置下载页面

---

## 七、持续改进任务（后续迭代）

### 7.1 功能增强
- [ ] 添加更多著作格式支持（DOCX、MOBI）
- [ ] 实现批量生成（多部著作并行）
- [ ] 添加内容版本管理
- [ ] 实现协作编辑功能

### 7.2 质量提升
- [ ] 收集用户反馈
- [ ] 优化Prompt模板
- [ ] 提升人格复刻准确率
- [ ] 提升热点匹配相关性

### 7.3 性能优化
- [ ] 实现增量生成（只重新生成变化部分）
- [ ] 优化模型调用（使用更便宜的模型组合）
- [ ] 实现本地缓存策略

---

## 八、任务优先级说明

### P0 (最高优先级 - 必须完成)
- 环境搭建与基础架构
- 文档解析功能
- Persona构建功能
- 提纲生成功能
- 对话生成功能
- 前端核心页面
- 端到端测试
- 应用打包

### P1 (高优先级 - 尽快完成)
- 热点匹配优化
- 性能优化
- 错误处理完善
- 用户文档

### P2 (中优先级 - 后续迭代)
- 批量生成
- 协作功能
- 高级可视化
- 数据分析

---

**文档版本**: v1.0
**最后更新**: 2025-01-25
**预计总工期**: 6周（42天）
