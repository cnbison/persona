# Persona生成与应用平台 - 前端

**技术栈**: Tauri + React + TypeScript + Vite + TailwindCSS
**当前状态**: ✅ 基础框架完成（页面以结构与占位为主）
**最后更新**: 2025-01-25

---

## 快速开始

### 前置要求
- Node.js >= 18
- Rust >= 1.70 (用于Tauri)
- npm >= 9

### 安装依赖
```bash
npm install --cache .npm-cache
```

### 启动开发服务器
```bash
# 仅前端开发（Web模式）
npm run dev

# Tauri桌面应用（包含Rust后端）
npm run tauri:dev
```

### 构建生产版本
```bash
# Web构建
npm run build

# Tauri桌面应用
npm run tauri:build
```

---

## 项目结构

```
frontend/
├── src/
│   ├── pages/              # 页面组件
│   │   ├── Dashboard.tsx           # 仪表板
│   │   ├── books/                  # 文档管理模块
│   │   │   ├── BookList.tsx
│   │   │   ├── BookUpload.tsx
│   │   │   └── BookDetail.tsx
│   │   ├── personas/               # Persona模块
│   │   │   ├── PersonaList.tsx
│   │   │   └── PersonaDetail.tsx
│   │   ├── outlines/               # 提纲模块
│   │   │   ├── OutlineList.tsx
│   │   │   └── OutlineDetail.tsx
│   │   ├── scripts/                # 生成模块
│   │   │   ├── ScriptGenerator.tsx
│   │   │   └── ScriptViewer.tsx
│   │   └── Settings.tsx            # 设置页面
│   │
│   ├── components/         # 可复用组件
│   │   └── layout/
│   │       ├── Sidebar.tsx
│   │       ├── Header.tsx
│   │       └── MainLayout.tsx
│   │
│   ├── services/           # API服务层
│   │   ├── api.ts
│   │   ├── books.ts
│   │   ├── personas.ts
│   │   ├── outlines.ts
│   │   └── scripts.ts
│   │
│   ├── types/              # TypeScript类型
│   │   ├── book.ts
│   │   ├── persona.ts
│   │   ├── outline.ts
│   │   └── script.ts
│   │
│   └── utils/              # 工具函数
│       └── cn.ts
│
├── src-tauri/               # Tauri Rust后端
├── public/                  # 公共资源
├── index.html               # HTML入口
├── package.json             # 前端依赖与脚本
└── vite.config.ts           # Vite配置
```

