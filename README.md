# Persona生成与应用平台

> 以说者Persona（默认作者，可扩展讲解者）+ 受众Persona为核心资产，活化经典著作与教学内容，支持证据可追溯、分级表达与可解释输出。

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-green)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 项目简介

本项目聚焦 Persona 的生成、验证与应用，核心能力包括：

- 文档解析与证据库（观点-原文-上下文证据链）
- 说者Persona构建（可解释画像与边界约束）
- 受众Persona适配（多版本分级讲解/改写）
- 验证输出（提纲/对话/重述）
- 可解释性与诊断（canonical/plan/final + Diff + 诊断提示）
- 资产化管理（Persona卡片、版本化、导出/导入）

`style-generator/` 为独立参考工程，用于借鉴参数化与可视化交互思路，不改动其代码。

---

## 应用场景

- 教育辅助：同一知识点按小学/初中/高中/大学分级讲解
- 经典活化：保留作者思想与风格一致性，同时提升可理解性
- 内容生产：稳定的说者Persona输出多场景内容
- 研究辅助：以证据库保证观点可追溯

---

## 技术栈

- 后端：FastAPI + SQLAlchemy + SQLite
- 前端：Tauri + React + TailwindCSS + Zustand
- NLP：jieba / TextRank
- 文档解析：pdfplumber / ebooklib
- 日志：loguru

---

## 项目结构

```
persona/
├── backend/                # Python 后端
├── frontend/               # Tauri + React 前端
├── books/                  # 示例著作/教材
├── data/                   # 数据存储
├── logs/                   # 日志
├── style-generator/        # 独立参考工程（不入库）
├── PRD-Persona.md          # 产品需求文档
├── COMPETITIVE_ANALYSIS.md # 竞品分析
├── ARCHITECTURE.md         # 架构设计
├── TASKS.md                # 任务分解
├── CHECKLIST.md            # 开发检查清单
└── README.md               # 项目说明
```

---

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- OpenAI API 密钥

### 1. 克隆项目
```bash
git clone <repository-url>
cd persona
```

### 2. 后端设置
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY

python -m app.database
uvicorn app.main:app --reload --port 8000
```

### 3. 前端设置
```bash
cd frontend
npm install --cache .npm-cache
npm run dev
# 或启动 Tauri 桌面模式
npm run tauri:dev
```

---

## API接口（当前）

- `POST /api/books/upload` - 上传并解析文档
- `GET /api/books` - 获取文档列表（分页）
- `GET /api/books/{book_id}` - 获取文档详情
- `DELETE /api/books/{book_id}` - 删除文档

---

## 相关文档

- `PRD-Persona.md`
- `COMPETITIVE_ANALYSIS.md`
- `ARCHITECTURE.md`
- `TASKS.md`
- `CHECKLIST.md`
- `backend/README.md`
- `frontend/README.md`

---

## 许可证

本项目采用 MIT 许可证 - 详见 `LICENSE`

---

**最后更新**: 2026-02-04
