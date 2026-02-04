# 快速测试指南

## 问题：ModuleNotFoundError: No module named 'app'

这个问题是因为Python找不到app模块。以下是解决方案：

---

## ✅ 方案1：使用统一的测试脚本（推荐）

```bash
cd backend
./test.sh
```

然后选择要测试的模块（1-8）。

---

## ✅ 方案2：手动设置PYTHONPATH

```bash
cd backend
export PYTHONPATH=$(pwd)
python app/utils/openai_client.py
```

或者使用`-m`参数：

```bash
cd backend
python -m app.utils.openai_client
```

---

## ✅ 方案3：使用启动脚本

```bash
cd backend
./start.sh
```

这会自动设置PYTHONPATH并启动FastAPI服务。

---

## 🧪 快速测试命令

### 测试工具层（不需要真实API）

```bash
cd backend
export PYTHONPATH=$(pwd)

# 测试文本处理
python app/utils/text_processor.py

# 测试文件处理
python app/utils/file_handler.py
```

### 测试服务层（当前使用Mock模式）

```bash
cd backend
export PYTHONPATH=$(pwd)

# 测试文档解析
python app/services/document_parser.py

# 测试Persona构建
python app/services/persona_builder.py

# 测试提纲生成
python app/services/outline_generator.py

# 测试对话生成
python app/services/dialogue_generator.py
```

### 测试OpenAI客户端（需要真实API密钥）

```bash
cd backend
export PYTHONPATH=$(pwd)

# 这会调用真实的GPT-4 API
python app/utils/openai_client.py
```

**注意**：你已经配置了真实API密钥，所以这个测试会实际调用OpenAI API并产生费用。

---

## 🚀 启动FastAPI服务

```bash
cd backend
./start.sh
```

或手动启动：

```bash
cd backend
export PYTHONPATH=$(pwd)
python -m uvicorn app.main:app --reload --port 8000
```

启动后访问：
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/api/health

---

## 💡 建议的测试顺序

### 1. 先测试不需要API的部分

```bash
cd backend
./test.sh
# 选择 2 - 文本处理工具
# 选择 3 - 文件处理工具
```

### 2. 测试文档解析（使用本地文件）

```bash
./test.sh
# 选择 4 - 文档解析服务
```

这会解析`../../books/理想国.txt`文件。

### 3. 测试OpenAI客户端（可选）

```bash
./test.sh
# 选择 1 - OpenAI客户端
```

**注意**：这会调用真实的GPT-4 API并产生费用。

### 4. 启动服务

```bash
./test.sh
# 选择 8 - 启动FastAPI服务
```

然后访问 http://localhost:8000/docs 测试API。

---

## ⚙️ 永久修复（可选）

如果你不想每次都设置PYTHONPATH，可以创建一个初始化脚本：

```bash
# 在backend目录下创建
cat > init_env.sh << 'EOF'
#!/bin/bash
export PYTHONPATH=$(pwd)
export PATH="$(pwd)/venv/bin:$PATH"
echo "✅ 环境已初始化"
echo "   PYTHONPATH: $PYTHONPATH"
EOF

chmod +x init_env.sh
```

然后每次打开终端时：

```bash
cd backend
source init_env.sh
# 之后就可以直接运行 python app/...
```

---

## 📝 常见问题

### Q: 为什么会有这个错误？

A: Python模块导入需要模块所在的目录在PYTHONPATH中。当前目录是`backend/`，但app模块在`backend/app/`，所以需要将`backend/`添加到PYTHONPATH。

### Q: 我已经配置了真实API密钥，会自动使用吗？

A: 是的！系统会检测到真实API密钥并自动调用OpenAI API。但如果在测试中出现错误，可以暂时切换回Mock模式。

### Q: 如何查看API调用日志？

A: 启动服务后，日志会显示在终端和`logs/`目录下。OpenAI调用会记录token使用和成本。

---

**更新时间**: 2025-01-25
**状态**: 环境配置完成 ✅
