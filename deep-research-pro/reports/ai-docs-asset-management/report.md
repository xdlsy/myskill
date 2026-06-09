# 面向 AI 的文档资产管理：目录结构、经验、Spec、架构文档 — 深度调研报告

*生成日期: 2026-05-30 | 来源数: 25+ | 置信度: High*

---

## 执行摘要

2025-2026 年，围绕 "AI 编码助手如何理解项目" 这一核心问题，业界已经形成了一套高度趋同的实践模式。核心思路是：**用一个极简的入口文件（CLAUDE.md / AGENTS.md）作为"项目宪法"，通过渐进式披露（Progressive Disclosure）按需引导 AI 读取详细文档，而非把所有信息塞进上下文窗口。** 目录结构上，`docs/` 放详细文档、`.claude/rules/` 或 `.cursor/rules/` 放 AI 专属规则、`docs/adr/` 或 `docs/decisions/` 放架构决策记录，已成为主流共识。

---

## 1. 核心概念：AI 文档资产是什么？

面向 AI 的文档资产不同于传统给人看的文档。它的核心特征是：

| 维度 | 传统文档（给人看） | AI 文档（给模型看） |
|------|-------------------|---------------------|
| **受众** | 新入职工程师 | 每次新会话的 AI（无状态的"新人"） |
| **目标** | 全面覆盖、娓娓道来 | 极简、精准、可被检索 |
| **格式** | 长文、图示、Wiki | Markdown、结构化清单、文件指针 |
| **更新频率** | 大版本更新时 | 与代码同步（"AI 犯两次同样错误就加一条"）|
| **加载方式** | 人主动翻阅 | 自动注入系统提示 / 按需懒加载 |

**关键洞察**：把每次 AI 会话当成一个"刚入职、什么都不知道但学习能力极强的工程师"来对待。文档的目标不是讲清楚所有细节，而是告诉它**去哪找答案**。

---

## 2. 目录结构：业界共识模式

### 2.1 单一仓库的标准布局

综合 julep-ai、HumanLayer、danielrosehill/AI-Dev-Repo-Template、Cursor Rules 生态等 10+ 个来源，以下是**最主流的目录结构**：

```
project-root/
│
├── AGENTS.md                      # 🧭 主入口（框架无关的开放标准）
├── CLAUDE.md → AGENTS.md          # 🔗 符号链接（Claude Code 兼容）
├── GEMINI.md → AGENTS.md          # 🔗 符号链接（Gemini CLI 兼容）
├── README.md                      # 👤 人类可读的项目说明
│
├── .claude/                       # ⚙️ Claude Code 专属配置
│   ├── settings.json              #    权限、环境变量等
│   ├── rules/                     #    📋 路径作用域模块化规则
│   │   ├── api-conventions.md
│   │   ├── db-patterns.md
│   │   └── testing-standards.md
│   ├── skills/                    #    🔧 可复用的专家工作流
│   │   └── deploy/SKILL.md
│   ├── agents/                    #    🤖 自定义子代理定义
│   └── commands/                  #    ⌨️  自定义斜杠命令
│
├── .cursor/rules/                 # ⚙️ Cursor IDE 专属规则 (.mdc 格式)
│   ├── base.mdc                   #    alwaysApply: true
│   ├── react.mdc                  #    globs: **/*.tsx
│   └── testing.mdc                #    globs: **/*.test.ts
│
├── docs/                          # 📚 人 + AI 共读的详细文档
│   ├── architecture.md            #    系统架构总览
│   ├── adr/                       #    🏛️ 架构决策记录 (Architecture Decision Records)
│   │   ├── README.md              #       ADR 索引
│   │   ├── template.md            #       ADR 模板
│   │   ├── 0001-use-postgres.md
│   │   ├── 0002-choose-react.md
│   │   └── ...
│   ├── api/                       #    API 规范
│   │   └── overview.md
│   ├── sql/                       #    数据库 schema + 字段含义
│   ├── testing.md                 #    测试模式与约定
│   ├── code-conventions.md        #    代码规范
│   ├── build-process.md           #    构建链路
│   ├── deployment.md              #    部署流程
│   └── runbooks/                  #    操作手册
│
├── agent_docs/                    # 🤖 AI 专属详细文档（HumanLayer 模式）
│   ├── building_the_project.md
│   ├── running_tests.md
│   ├── code_conventions.md
│   ├── service_architecture.md
│   ├── database_schema.md
│   └── service_communication_patterns.md
│
├── src/                           # 源代码
│   ├── modules/
│   └── CLAUDE.md                  #    子目录作用域规则（懒加载）
│
├── tests/
└── scripts/
```

### 2.2 Monorepo 的扩展布局

```
monorepo-root/
├── AGENTS.md                      # 仓库级共享约定
├── docs/
│   └── adr/                       # 全局 ADR（跨包决策）
│       ├── 0001-use-kafka-for-messaging.md
│       └── ...
├── packages/
│   ├── frontend-app/
│   │   ├── AGENTS.md              # 前端特有规则
│   │   ├── docs/
│   │   │   ├── architecture.md
│   │   │   └── adr/               # 前端专属 ADR
│   │   └── src/
│   ├── api-service/
│   │   ├── AGENTS.md
│   │   ├── docs/
│   │   │   └── adr/
│   │   └── src/
│   └── shared-lib/
│       ├── AGENTS.md
│       └── src/
```

### 2.3 不同工具的文件映射

| AI 工具 | 入口文件 | 规则目录 | 备注 |
|---------|---------|---------|------|
| **Claude Code** | `CLAUDE.md` | `.claude/rules/` | 也支持 `AGENTS.md` |
| **Cursor** | `AGENTS.md` 或 `.cursorrules` | `.cursor/rules/*.mdc` | 旧单文件 `.cursorrules` 已弃用 |
| **GitHub Copilot** | `AGENTS.md` | `.github/copilot-instructions.md` | |
| **Gemini CLI** | `GEMINI.md` | 也读 `AGENTS.md` | |
| **OpenAI Codex** | `AGENTS.md` | | |
| **Aider / Zed / Windsurf** | `AGENTS.md` | | 开放标准广泛支持 |

> **趋势**：`AGENTS.md` 正在成为跨工具的开放标准。许多项目以 `AGENTS.md` 为规范文件，再用符号链接指向它来兼容各工具。截至 2025 年中，已有 20,000+ 开源仓库采用。

---

## 3. 经验放哪里？—— 知识与经验的存放策略

这是你问的核心问题之一。业界有以下几种分层模式：

### 3.1 三层知识架构（来自 LLMWiki / Second Brain 实践）

```
raw/                 # 原始资料（不可变，AI 只读）
  └── assets/        # 图片、附件
wiki/                # AI 生成维护的结构化知识
  ├── index.md       # 内容索引
  ├── log.md         # 操作日志
  ├── entities/      # 实体页（工具、产品、人物）
  ├── concepts/      # 概念页（方法论、模式）
  ├── sources/       # 资料摘要
  └── syntheses/     # 综合分析
```

### 3.2 "复合记忆"模式（来自 TheRealSeanDonahoe/agents-md）

在 AGENTS.md 中设 Section 11 "项目学习积累"——AI 在开发过程中自动记录错误和修正，形成**随着时间积累的复合记忆**。这是将"经验"固化为文档资产的核心机制。

### 3.3 社区共识：经验该放哪？

| 经验类型 | 放哪里 | 示例 |
|---------|--------|------|
| **项目级通用约定** | `AGENTS.md` / `CLAUDE.md`（根文件，< 200 行） | "我们用 pnpm，不是 npm"、"永远不要编辑 `generated/`" |
| **已知陷阱/踩坑记录** | `AGENTS.md` 中的 "Known Pitfalls" 区域，或 `docs/gotchas.md` | "每个新工程师都会在 X 处犯错" |
| **代码风格约定** | `docs/code-conventions.md`（模块化文件，按需加载） | 命名规范、错误处理范式 |
| **架构决策及理由** | `docs/adr/`（编号 + 时间戳 + 背景 + 选项对比） | 为什么选 Postgres 而不是 Mongo |
| **操作经验/跑脚本的方法** | `docs/runbooks/` | 如何部署、如何回滚 |
| **持续迭代的经验** | AGENTS.md Section 11 或 CLAUDE.md 的 memory 区域 | AI 犯两次同样错误后追加一行规则 |
| **模块级特有经验** | 子目录 `CLAUDE.md`（懒加载，仅在该目录被操作时注入） | 认证模块的特殊安全要求 |

### 3.4 关键原则：指针优于副本

```
❌ 错误做法：把所有经验塞进 AGENTS.md（上下文爆炸 → AI 选择性忽略）
✅ 正确做法：AGENTS.md 只放文件清单 + 一句话说明 → AI 按需读取
```

示例（来自 HumanLayer）：
```markdown
## Domain Guides
- `agent_docs/service_architecture.md` — system design & component communication
- `agent_docs/database_schema.md` — table structures & field meanings
- `agent_docs/code_conventions.md` — naming, error handling, file layout
```

---

## 4. Spec 放哪里？—— 规格文档的位置策略

### 4.1 不同 Spec 类型的存放位置

| Spec 类型 | 推荐位置 | 说明 |
|-----------|---------|------|
| **API 规范** | `docs/api/` 或 `src/typespec/`（若使用 TypeSpec 等规范驱动开发） | julep-ai 将 TypeSpec 作为 API 规范的"真源"放在 `src/typespec/` |
| **PRD / 产品需求文档** | `docs/planning/` 或 `planning/` | AI 友好仓库模板推荐 |
| **技术规格（Tech Spec）** | `docs/tech-specs/` 或 `docs/design/` | 功能级技术设计文档 |
| **数据库 Schema** | `docs/sql/` 或 `docs/data-schema.md` | 含字段含义说明，不止 DDL |
| **ADR（架构决策记录）** | `docs/adr/` 或 `docs/decisions/` | 编号前缀 + 模板化 |
| **测试规范** | `docs/testing.md` | 测试框架、模式、覆盖率要求 |
| **构建/部署规范** | `docs/build-process.md` + `docs/deployment.md` | CI/CD 链路说明 |

### 4.2 ADR 的详细模板

ADR 是社区中最为标准化的 Spec 类型之一，以下是共识模板：

```markdown
# ADR-0001: 标题

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-XXXX]

## Date
YYYY-MM-DD

## Context
什么背景/问题推动了这次决策？

## Decision
我们决定做什么？具体方案是什么？

## Consequences
### Positive（正面影响）
### Negative（负面影响）

## Alternatives Considered（备选方案及放弃原因）
### 方案 A
**优点:** ...
**缺点:** ...
**为何放弃:** ...

## References（关联代码 / Issue / 外部资料）
```

### 4.3 API Spec 的特殊处理

当使用 **规范驱动开发**（如 OpenAPI、TypeSpec、Protobuf）时：

```
src/typespec/          # ← API 规范的"真源"（julep-ai 模式）
  ├── main.tsp
  ├── models.tsp
  └── routes.tsp
docs/api/
  └── overview.md      # ← 人类可读的补充说明
```

**核心原则**：如果 Spec 是机器可执行的（能生成代码/文档），它应该放在源码树中靠近代码的位置。如果 Spec 是纯文档性质的，放在 `docs/` 下。

---

## 5. 代码架构文档放哪里？—— 架构文档的位置策略

### 5.1 两种主流模式

#### 模式 A：`docs/` 下集中管理（中小项目首选）

```
docs/
├── architecture.md          # 架构总览（3 句话 + 主要模块 + 通信方式）
├── diagrams/                # 架构图
│   ├── c4/                  #   C4 模型图
│   ├── sequence/            #   时序图
│   └── erd/                 #   ER 图
├── adr/                     # 架构决策记录
├── api/
└── sql/
```

**适用**：单一仓库、团队规模小-中、架构复杂度中等。

#### 模式 B：`architecture/` 顶层目录（大型系统）

```
architecture/
├── README.md                # 架构文档索引
├── 01-introduction-and-goals.md
├── 03-system-context.md
├── 05-building-block-view.md
├── 07-runtime-view.md
├── 09-architecture-decisions/   # ADR
│   ├── adr-0001.md
│   └── adr-000-template.md
├── diagrams/
│   ├── c4/
│   └── sequence/
└── glossary.md
```

**适用**：大型系统、独立架构团队、arc42 模板用户（Gradle、Spryker 等）。

### 5.2 架构文档的编写原则（面向 AI 的）

| 原则 | 说明 |
|------|------|
| **三句话架构** | AGENTS.md 中放 3 句话概括：主要模块有哪些、怎么通信、数据怎么流 |
| **指针优于副本** | 用 `docs/architecture.md:45-60` 格式指向权威源文件，而非复制内容 |
| **与代码同址** | 模块级架构说明放在对应子目录的 `CLAUDE.md` / `README.md` 中 |
| **图表用 Mermaid** | Markdown 内嵌 ` ```mermaid ` 代码块，AI 可直接解析和修改 |

### 5.3 Monorepo 中架构文档的放置

```
monorepo-root/
├── docs/
│   ├── architecture.md          # 全局架构（跨包）
│   └── adr/                     # 全局 ADR
├── packages/
│   ├── frontend-app/
│   │   ├── docs/
│   │   │   ├── architecture.md  # 前端架构
│   │   │   └── adr/             # 前端 ADR
│   │   └── src/
│   └── api-service/
│       ├── docs/
│       │   ├── architecture.md  # 后端架构
│       │   └── adr/
│       └── src/
```

**规则**：影响多个包的决策 → 根 `docs/adr/`；仅影响单个包的决策 → `packages/<name>/docs/adr/`。

---

## 6. 渐进式披露：一切的核心方法论

### 6.1 问题

一个 500 行的 AGENTS.md 塞满所有信息 → AI 会**选择性忽略**规则（Context Budget 溢出效应）。前沿模型的可靠指令遵循上限约 150-200 条，而 Claude Code 的系统提示已占约 50 条。

### 6.2 解决方案：四层渐进加载

```
Layer 1: AGENTS.md（~50-200 行）
    │   核心规则 + 文件索引 + 三句话架构
    │   "处理 XX 任务前，请先读取 docs/XX.md"
    ▼
Layer 2: docs/*.md（按需读取）
    │   详细规则和架构文档（可写得很详细，200-400 行）
    │   AI 根据任务自主判断是否需要读取
    ▼
Layer 3: 子目录 CLAUDE.md / AGENTS.md（懒加载）
    │   模块/子目录特有约定
    │   仅在 AI 操作该目录文件时自动注入
    ▼
Layer 4: @file:line 指针（精准引用）
        指向代码中的权威源文件，避免文档过期
```

### 6.3 实际的 AGENTS.md 极简示例（~30 行）

来自社区的"最小可行 AGENTS.md"：

```markdown
# AGENTS.md

## Onboarding
Before working, read:
1. All **/README.md files
2. All **/README.*.md files
3. docs/architecture.md

## Quality Gates
After code changes, run until all pass:
1. pnpm type-check
2. pnpm format
3. pnpm lint
4. pnpm test

## Domain Guides
- docs/architecture.md — system design & key decisions
- docs/testing.md — test framework & patterns
- docs/api/overview.md — API structure & conventions
- docs/sql/schema.md — database tables & field meanings
```

---

## 7. 关键反模式（避坑指南）

| ❌ 反模式 | ✅ 正确做法 |
|-----------|------------|
| 用 `/init` 自动生成然后不管了 | `/init` 只是草稿起点，必须手工打磨——这是"最高杠杆点" |
| 把所有信息塞进一个 AGENTS.md | 渐进式披露——入口极简，详情在 docs/ 中 |
| 写代码风格指南让 AI 遵守 | 质量门（lint/format/test）用确定性工具，不让 AI 做 linter |
| 硬编码文件路径 | 用 "search for X" 模式，路径会变 |
| 复制上游工具文档到 AGENTS.md | 外链到工具文档（pytest、ruff 等），不重复 |
| 把敏感信息写进去 | 这些文件会进系统提示——视为可能公开的数据 |
| "Set and forget" 不再更新 | 代码架构变 → AGENTS.md 同步变，就像更新其他文档一样 |

---

## 8. 维护节奏建议

| 时机 | 操作 |
|------|------|
| 项目初始化 | 运行 `/init` 生成草稿 → 人工审查、精简到 < 100 行 |
| AI 犯同样的错两次 | 追加一行规则到 AGENTS.md |
| 做重大架构决策时 | 写一篇 ADR 到 `docs/adr/` |
| 新增模块/子系统时 | 考虑是否需要子目录 CLAUDE.md |
| 约定发生变化 | 同步更新（新框架、新 lint 规则、新目录结构等） |
| 每季度 | 遍历清理过时内容，删除不再适用的规则 |

---

## 9. 针对你的项目（SBG/BrowserGateway）的建议

根据你的项目情况（Java/Gradle 项目），建议从以下结构起步：

```
BrowserGateway/
├── AGENTS.md                         # 主入口（也可以直接叫 CLAUDE.md）
│                                     # 内容：构建命令、三句话架构、docs/ 索引
├── docs/
│   ├── architecture.md               # 系统架构：模块、通信、数据流
│   ├── adr/                          # 架构决策记录
│   │   ├── template.md
│   │   └── 0001-xxx.md
│   ├── api/                          # API 规范（若有）
│   ├── testing.md                    # 测试策略：JUnit、集成测试、E2E
│   ├── build-process.md              # Gradle 构建链路说明
│   └── deployment.md                 # 部署流程
├── .claude/
│   ├── rules/                        # 模块化规则
│   │   ├── java-conventions.md       # Java 代码约定
│   │   └── gradle-patterns.md        # Gradle 约定
│   └── settings.json
└── src/
    └── main/java/...
```

**最小启动步骤**（今天就能做）：
1. 在项目根目录写一个 30-50 行的 `AGENTS.md`，包含构建命令、三句话架构、docs/ 索引
2. 把现有的架构文档迁移到 `docs/architecture.md`
3. 把团队积累的经验/踩坑记录写进 `docs/gotchas.md`，在 AGENTS.md 中加一行索引
4. 做下一个重要技术决策时，写第一篇 ADR

---

## 10. 关键信息来源

1. [Using CLAUDE.MD files: Customizing Claude Code for your codebase](https://claude.com/blog/using-claude-md-files) — Anthropic 官方指南
2. [Writing a good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md) — HumanLayer 的渐进式披露实践（根文件 < 60 行）
3. [第 3 篇：规则分层——用 docs/ 文档体系实现渐进披露](https://cloud.tencent.cn/developer/article/2649848) — 中文深度解析
4. [AGENTS.md Gains Traction as an Open Format](https://socket.dev/blog/agents-md-gains-traction-as-an-open-format-for-ai-coding-agents) — AGENTS.md 开放标准生态概述
5. [julep-ai/julep AGENTS.md](https://raw.githubusercontent.com/julep-ai/julep/refs/heads/dev/AGENTS.md) — 真实项目标杆案例
6. [danielrosehill/AI-Dev-Repo-Template-Oct-2025](https://github.com/danielrosehill/AI-Dev-Repo-Template-Oct-2025) — AI 友好仓库模板
7. [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) — Claude Code 最佳实践合集
8. [Factory.ai — AGENTS.md announcement](https://www.factory.ai/agents-md) — Monorepo 场景的 AGENTS.md 模板
9. [log4brains — ADR tool](https://github.com/barseghyanartur/log4brains) — ADR 工具与 Monorepo 模式
10. [从 0 到 1：用 CLAUDE.md 搭建永远懂你的项目环境](https://cloud.tencent.cn/developer/article/2596824) — 中文实践指南

---

## 研究方法说明

- **搜索查询数**：9 组关键词，覆盖中英文
- **分析来源数**：25+ 个独立来源
- **子问题覆盖**：AI 文档资产定义 ✓ | 目录结构模式 ✓ | 经验与知识存放 ✓ | Spec 文档位置 ✓ | 代码架构文档位置 ✓
- **置信度**：High — 多个独立来源得出高度一致的结论
