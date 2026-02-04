# 竞品分析与可借鉴方向（整理版）

> 本文件汇总多轮竞品扫描结果，按能力类型归类，并给出可借鉴点与差异化空间。内容用于内部对标与PRD支撑。

## 一、竞品分组与定位

### 1) 说者风格/品牌声音类（偏“说者Persona”）
**目标**：把“说者风格”资产化、可复用、可导出。  
**典型能力**：风格规则化、样例驱动、可编辑、可导出、多Persona并存与切换。

**可借鉴点**
- 形成“风格规则集 + 示例对照”的可执行规范
- 把风格沉淀为配置/模板，用于多场景复用
- 支持版本化与多人协作调整

### 2) 受众适配/分级改写类（偏“受众Persona”）
**目标**：同一内容输出多版本，适配不同阅读水平或年级。  
**典型能力**：多阅读等级输出、保持核心意义不变、可编辑与教学场景可控。

**可借鉴点**
- 多版本输出是分级场景的核心交付形态
- 输出必须可编辑与可追溯
- 能输出“难度/可读性”评估或提示

### 3) 教学内容生成/教材适配类（偏“内容工程化”）
**目标**：支持教学材料生成、结构化、删改与适配。  
**典型能力**：内容结构可变、版本化、可定制。

**可借鉴点**
- 结构可变 + 版本化，方便不同教学情境复用
- 输出可视化，让教师/运营更快校准

### 4) 音频/听读类（偏“多模态扩展”）
**目标**：将文本转为音频，提供多音色/语言。  
**可借鉴点**
- 作为未来“多音色播客生成”的落地参考

## 二、能力矩阵（对照PRD模块）

| PRD模块 | 可借鉴能力 | 可借鉴来源类型 |
|---|---|---|
| Persona画像/风格执行 | 风格规则化、可导出配置、样例驱动 | 说者风格/品牌声音类 |
| 受众Persona适配 | 多版本输出、分级可控、可编辑校准 | 受众适配/分级改写类 |
| 一致性与可追溯 | 输出可编辑与可追溯、难度提示 | 受众适配/教学内容类 |
| 多模态扩展 | 文本到音频、多音色 | 音频/听读类 |

## 三、可借鉴的交互流程（UX Patterns）

- **样例/原文输入 → 生成风格/等级描述 → 输出多版本 → 编辑与导出**
- **多版本对比与回写**：允许用户校准参数并沉淀为模板
- **适配可解释**：展示“为什么这样改”的提示与可视化

## 四、与本项目的差异化空间

- **作者Persona证据锚定**：输出需可追溯至原文证据库
- **双Persona耦合**：作者Persona + 受众Persona同时驱动输出
- **经典/教材活化**：不仅改写难度，还要保留作者思想与风格一致性

## 五、建议落地策略（摘要）

- 以“证据库 + 边界规则”为底层约束，避免参数化带来人格漂移
- 以“受众Persona参数化”为表层控制，增强可调试与可视化
- 输出多版本并提供适配评估，形成可复用资产

## 附录：具体竞品清单与来源链接

### 说者风格/品牌声音类
- [AIStyleGuide](https://aistyleguide.com/)
- [Junia Brand Voice](https://www.junia.ai/brand-voice)
- [Neotype Brand Voice](https://neotype.ai/product/brand-voice/)
- [Enji Brand Voice Generator](https://www.enji.co/brand-voice-generator)

### 受众适配/分级改写与教育类
- [Gale AI Leveler（Cengage 新闻稿）](https://www.cengagegroup.com/news/press-releases/2025/gale-part-of-cengage-group-introduces-ai-leveler-tool-in-beta-to-personalize-learning-and-support-student-reading-comprehension/)
- [SchoolAI Text Leveler（帮助文档）](https://help.schoolai.com/en/articles/11526208-use-the-text-leveler-tool)
- [Varsity Tutors Text Leveler](https://ai.varsitytutors.com/tools/text-leveler)
- [Kira Text Leveler](https://www.kira-learning.com/tools/text-leveler)
- [Newsela Leveler（阅读等级说明）](https://support.newsela.com/article/article-actions/)
- [Adaptive Books](https://adaptivebooks.org/)
- [ReadEasy](https://readeasy.org/)

### 多模态/音频（参考）
- [ElevenReader（ElevenLabs 朗读应用）](https://elevenreader.io/)
- [Google App Simplify（iOS 功能报道）](https://www.macrumors.com/2025/05/06/google-search-ios-app-simplify/)
