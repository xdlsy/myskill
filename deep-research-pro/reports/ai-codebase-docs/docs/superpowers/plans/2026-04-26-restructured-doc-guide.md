# 《结构化文档指南.md》实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 `report.md`（999 行考据型研究报告）重构为 `结构化文档指南.md`（24 000–30 000 字、面向所有读者的实战指南），满足"术语解释、段落感强、概念聚合、可跳转引用"四条原则。

**Architecture:** 单文件交付物 + 三段式工作流——先建术语库与骨架（保证术语链接全程可用），再分章填内容（每章独立 self-contained），最后通读自检。每章统一"概念盒 / 一页结论 / 正文 / 实战速查"四段布局，章内首次出现的术语链回附录 A，重要外部源链回附录 C。

**Tech Stack:** Markdown + 站内锚点 + 外部链接；写作工具：Read/Edit/Write；自检工具：Bash + grep + wc。

**Source of truth:** `/Users/lsy/clawd/research/ai-codebase-docs/report.md`（保持不变）
**Spec:** `/Users/lsy/clawd/research/ai-codebase-docs/docs/superpowers/specs/2026-04-26-restructured-doc-guide-design.md`
**Target:** `/Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md`

**重要约定**：
- 当前目录**不是 git 仓库**，所有"commit"步骤改为"保存并跑自检"
- 写作过程中如需查证外部链接（agents.md、Anthropic 文档等），使用 WebFetch 并设较长 timeout；不要重复抓取，结果摘要直接落入对应附录条目

---

## 总览：任务依赖图

```
  Task 1 (建骨架与文件) 
        │
        ▼
  Task 2 (引言)
        │
        ▼
  Task 3 (第 1 章)
        │
        ▼
  Task 4 (附录 A 术语表) ◄────── 关键依赖：所有场景章引用它
        │
        ▼
 ┌──────┴──────┬──────┬──────┬──────┬──────┐
 ▼             ▼      ▼      ▼      ▼      ▼
Task 5       Task 6 Task 7 Task 8 Task 9 Task 10
(第 2 章)     (第 3) (第 4) (第 5) (第 6) (第 7)
 │             │      │      │      │      │
 └─────────────┴──────┴──────┴──────┴──────┘
                       │
                       ▼
                  Task 11 (第 8 章)
                       │
                       ▼
                  Task 12 (附录 B 模板与脚本)
                       │
                       ▼
                  Task 13 (附录 C 参考资源)
                       │
                       ▼
                  Task 14 (全文通读 + 自检)
```

---

## Phase A — 基础阶段（任务 1-4）

目的：建好骨架与术语库，让后面 6 个场景章可以自由引用。

### Task 1: 创建文件骨架

**Files:**
- Create: `/Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md`

**目的**：先把全部章节标题、章节占位、附录占位一次性写好，后续每章只填内容、不动结构。这样万一中途打断也能从 grep 章节锚点判断进度。

- [ ] **Step 1: 用以下骨架创建文件**

```markdown
# 结构化文档指南：给 AI 编码代理的项目文档体系

> *Generated: 2026-04-26 | 重构自 [report.md](./report.md) | 阅读对象：所有需要为 AI 辅助研发搭建文档体系的工程师与团队*

---

## 引言

<!-- TASK 2 will fill -->

---

## 第 1 章 全景与术语速查

<!-- TASK 3 will fill -->

---

## 第 2 章 场景一：搭建 AI 友好的项目入口

<!-- TASK 5 will fill -->

---

## 第 3 章 场景二：让 AI 看懂存量代码

<!-- TASK 6 will fill -->

---

## 第 4 章 场景三：用 AI 做增量开发

<!-- TASK 7 will fill -->

---

## 第 5 章 场景四:把文档维护成代码

<!-- TASK 8 will fill -->

---

## 第 6 章 场景五:让文档与规则不腐烂

<!-- TASK 9 will fill -->

---

## 第 7 章 方法论选型与迁移

<!-- TASK 10 will fill -->

---

## 第 8 章 综合建议与仓库骨架

<!-- TASK 11 will fill -->

---

## 附录 A：术语表

<!-- TASK 4 will fill -->

---

## 附录 B：模板与脚本

<!-- TASK 12 will fill -->

---

## 附录 C：参考资源

<!-- TASK 13 will fill -->
```

- [ ] **Step 2: 验证文件创建成功**

```bash
ls -la /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md
```

预期输出：文件存在，大小约 1 KB，包含 13 个 H2 标题。

```bash
grep -c '^## ' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md
```

预期输出：`13`

- [ ] **Step 3: 保存并进入 Task 2**

无 git commit，仅 ls 确认文件存在。

---

### Task 2: 写引言

**Files:**
- Modify: `/Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md`（替换"## 引言"下方占位符）

**Source from `report.md`:**
- 第 7-19 行（Executive Summary 6 条 bullet → 改写为段落）

**目的**：让读者用 3 分钟读完后明白 "AI 辅助研发的文档为什么和传统文档不同"、"本指南怎么用"、"6 章如何串联"。**不要**用 bullet list，必须是有故事感的段落。

**关键叙事要素**（必须覆盖）：
1. **核心动机**："文档既是给人看的，更是给 agent 看的'上下文契约'"——把这句作为引言的论点抛出
2. **业界共识时间窗**：2024–2026 年形成稳定共识，AGENTS.md 规范 2025-08-19 公开
3. **本指南架构**：6 章对应 5 个使用场景 + 1 章方法论选型
4. **如何使用本指南**：
   - 赶时间：直接读每章的【一页结论】+ 附录 A 术语表
   - 完整读：按章节顺序（场景之间有连接句）
   - 当工具书：附录 B 抄模板、附录 C 跳外部源
5. **作者立场**：本文综合 35+ 来源，所有方法论建议都标明边界（轻/中/重型项目）

**长度预算**：约 600 字（不含 markdown 标记），分 3-4 段。

- [ ] **Step 1: 在文件中找到引言占位符**

```bash
grep -n "## 引言" /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md
```

- [ ] **Step 2: 用 Edit 工具替换占位符**

把 `<!-- TASK 2 will fill -->` 替换为完整引言。引言的写法要求：
- 第一段：核心动机（"上下文契约"）+ 当前时间节点（2024–2026 共识形成中）
- 第二段：本指南要解决什么问题（六个场景串联）
- 第三段：怎么用本指南（三种读法）
- 第四段：边界声明（适用 / 不适用人群、所有建议标注项目规模档）

每段约 150 字。

- [ ] **Step 3: 自检**

```bash
sed -n '/## 引言/,/^---/p' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | wc -m
```

预期：1 800–2 200 字符（中文加 markdown）

```bash
# 验证不是 bullet list
sed -n '/## 引言/,/^---/p' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | grep -c '^- '
```

预期：`0`（引言不该有 bullet）

- [ ] **Step 4: 保存**

无需 commit。

---

### Task 3: 写第 1 章 全景与术语速查

**Files:**
- Modify: `/Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md`（替换"## 第 1 章"下方占位符）

**Source from `report.md`:**
- 全文读一遍，第 1 章本质是"目录化导览"，不引用具体段落

**目的**：第 1 章是全文的"地图"——告诉读者每章解决什么问题、术语速查表怎么用、章节怎么跳读。

**章节结构**（不需要"概念盒/一页结论/正文/实战速查"四段，第 1 章特殊）：

```markdown
## 第 1 章 全景与术语速查

### 1.1 6 个使用场景与本指南章节映射

[一段话：本指南分为 5 个场景章（第 2-6 章）+ 1 个选型迁移章（第 7 章）+ 综合建议（第 8 章）]

| 你的处境 | 跳到 | 关键产物 |
|---|---|---|
| 想为新项目搭建 AI 入口 | 第 2 章 | AGENTS.md / CLAUDE.md / .claude/rules/ |
| 老项目要补 AI 友好文档 | 第 3 章 | ARCHITECTURE.md / ADR / Code Map / Glossary |
| 用 AI 做增量功能开发 | 第 4 章 | spec.md / plan.md / tasks.md |
| 想让文档不腐烂 | 第 5、6 章 | Vale / lychee / hooks / 周审计 SOP |
| 为团队选型方法论 | 第 7 章 | vanilla / Spec-Kit / BMAD 三档 |

### 1.2 术语速查表（按字母序）

[列出附录 A 全部 ~30 条术语的"全称 + 一句话定义"，每条形如：

- **`AGENTS.md`**（*Agent Markdown*）：AI 编码代理通用入口规范，2025-08 由 OpenAI 公开。详见 [附录 A](#术语-agentsmd)。
- **`@-import`**（*at-import*）：Claude Code 在 markdown 文件里用 `@path` 语法递归引入其他文件，最多 5 跳。详见 [附录 A](#术语-at-import)。
- ...

按字母序，不分类。每条约 50 字。]

### 1.3 阅读路径建议

[一段话：
- "搭车型读者"（30 分钟内拿走结论）：读引言 + 1.2 + 每章【一页结论】+ 第 8 章
- "全图型读者"（深度学习）：按 2→3→4→5→6→7 章顺序，期间随时跳附录 A 查术语
- "工具人型读者"（直接抄）：跳附录 B 抄模板，回正文找上下文
]
```

- [ ] **Step 1: 列出附录 A 术语（用于 1.2）**

参考 spec §4.2 的术语清单（约 30 条）。在写 1.2 时，**只写"短名+全称+一句话定义+附录跳转链接"**，详细解释留给附录 A。

- [ ] **Step 2: 用 Edit 替换占位符**

按上面三节结构填写。1.1 表格 5 行；1.2 列出 ~30 条术语短条目；1.3 三种阅读路径每段 50 字。

- [ ] **Step 3: 自检**

```bash
sed -n '/## 第 1 章/,/^## 第 2 章/p' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | wc -m
```

预期：3 000–4 500 字符

```bash
# 数术语条目数
sed -n '/### 1.2 术语速查表/,/### 1.3/p' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | grep -c '^- \*\*'
```

预期：≥ 25（少于 25 说明遗漏，对照 spec §4.2 补齐）

- [ ] **Step 4: 保存**

---

### Task 4: 写附录 A 术语表

**Files:**
- Modify: `/Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md`（替换"## 附录 A：术语表"下方占位符）

**Source from `report.md`**: 通读全文，每个术语找出 2-3 个出处提炼定义。

**目的**：给所有术语写完整定义，正文章节首次出现时只链回此处。**先写附录 A 再写场景章**——否则场景章里链接没目标。

**术语条目格式**（统一字段）：

```markdown
### 术语-{slug}

**全称 / 缩写解读**：…  
**一句话定义**：…  
**关键约束 / 边界**：…（长度上限、加载机制、与近似概念的差异）  
**何处用到 / 何时不用**：…  
**权威源**：[链接](https://...)
```

**slug 命名规则**：纯小写英文，特殊符号去掉。例：`AGENTS.md` → `agentsmd`；`@-import` → `at-import`；`Spec-Kit` → `spec-kit`；`Code Map` → `code-map`。

**完整术语清单**（必须全部写完）：

#### 入口体系（9 条）

1. `AGENTS.md` (slug: agentsmd)
2. `CLAUDE.md` (slug: claudemd)
3. `MEMORY.md` (slug: memorymd)
4. `CONVENTIONS.md` (slug: conventionsmd)
5. `@-import` (slug: at-import)
6. `path frontmatter` (slug: path-frontmatter)
7. `paths` 字段（Claude Code）(slug: paths-field)
8. `globs` 字段（Cursor）(slug: globs-field)
9. `applyTo` 字段（Copilot）(slug: applyto-field)

#### 架构与决策（11 条）

10. `C4 model` (slug: c4-model)
11. `arc42` (slug: arc42)
12. `4+1 view` (slug: four-plus-one)
13. `Structurizr DSL` (slug: structurizr-dsl)
14. `ADR` (slug: adr)
15. `MADR` (slug: madr)
16. `Nygard 模板` (slug: nygard)
17. `Y-statement` (slug: y-statement)
18. `Code Map` (slug: code-map)
19. `Bounded Context` (slug: bounded-context)
20. `Glossary` (slug: glossary)

#### 增量开发（8 条）

21. `SDD` (slug: sdd) — Spec-Driven Development
22. `Spec-Kit` (slug: spec-kit)
23. `BMAD-METHOD` (slug: bmad)
24. `OpenSpec` (slug: openspec)
25. `Constitution` (slug: constitution)
26. `Spec/Plan/Tasks 三件套` (slug: spec-plan-tasks)
27. `INDEPENDENTLY TESTABLE` (slug: independently-testable)
28. `Gherkin AC` (slug: gherkin-ac)

#### Docs-as-code（5 条）

29. `Vale` (slug: vale)
30. `markdownlint-cli2` (slug: markdownlint)
31. `lychee` (slug: lychee)
32. `CODEOWNERS` (slug: codeowners)
33. `dorny/paths-filter` (slug: paths-filter)

#### Claude Code 机制（10 条）

34. `Claude Code` (slug: claude-code)
35. `auto memory` (slug: auto-memory)
36. `skills` (slug: skills)
37. `hooks` (slug: hooks)
38. `InstructionsLoaded` (slug: instructionsloaded)
39. `PreToolUse` (slug: pretooluse)
40. `compaction` (slug: compaction)
41. `JIT 检索` (slug: jit-retrieval)
42. `context rot` (slug: context-rot)
43. `prompt cache` (slug: prompt-cache)

**总计**：43 条（实际编写时如有合并/拆分，最终数量在 ~40 条）。

- [ ] **Step 1: 准备权威源 URL 表**

从 `report.md` 末尾 Sources 章节（第 954-991 行）抽取，列入笔记。如果某术语对应的链接缺失，使用 WebSearch 补找。

主要权威源：
- agents.md, github.com/agentsmd/agents.md
- code.claude.com/docs/en/{memory, best-practices, hooks, skills}
- anthropic.com/engineering/effective-context-engineering-for-ai-agents
- adr.github.io, adr.github.io/madr/
- c4model.com, arc42.org, structurizr.com
- aider.chat/docs/usage/conventions.html
- cursor.com/docs/context/rules
- docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot
- vale.sh/docs/install
- github.com/lycheeverse/lychee
- github.com/dorny/paths-filter
- github.com/github/spec-kit
- github.com/bmad-code-org/BMAD-METHOD
- matklad.github.io/2021/02/06/ARCHITECTURE.md.html

- [ ] **Step 2: 写每条术语**

对每条 43 条术语：
1. 给出 slug 锚点 `### 术语-{slug}`
2. 4 个统一字段都填
3. "何处用到 / 何时不用"是关键差异化字段——必须写清"用它解决什么问题"和"在什么情况下别用"

**重点术语必须更详细**（150-250 字而不是 80 字）：
- `AGENTS.md`、`CLAUDE.md`、`@-import`、`auto memory`、`hooks`、`skills`、`compaction`、`Spec-Kit`、`BMAD-METHOD`、`MADR`、`Code Map`、`Vale`、`JIT 检索`

其余术语 60–100 字即可。

- [ ] **Step 3: 自检**

```bash
sed -n '/## 附录 A:术语表/,/## 附录 B/p' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | grep -c '^### 术语-'
```

预期：≥ 40

```bash
# 检查每条都有"全称""一句话定义""关键约束""何处用到""权威源"五字段
sed -n '/## 附录 A:术语表/,/## 附录 B/p' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | grep -c '权威源'
```

预期：与术语数一致

- [ ] **Step 4: 保存**

---

## Phase B — 6 个场景章节（任务 5-10）

每个场景章统一遵循"概念盒 / 一页结论 / 正文 / 实战速查"四段式。术语首次出现处必须 `[术语](#术语-slug)` 链接到附录 A。

### Task 5: 写第 2 章 场景一：搭建 AI 友好的项目入口

**Files:**
- Modify: `/Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md`（替换"## 第 2 章"占位符）

**Source from `report.md`：**
- 第 21-143 行（主题 1 全文，7 个子节）

**章节结构与必含内容：**

```markdown
## 第 2 章 场景一：搭建 AI 友好的项目入口

### 【核心概念盒】

- [`AGENTS.md`](#术语-agentsmd)：AI 编码代理通用入口规范
- [`CLAUDE.md`](#术语-claudemd)：Claude Code 专用入口
- [`MEMORY.md`](#术语-memorymd)：Auto memory 索引文件，硬截断 200 行/25KB
- [`@-import`](#术语-at-import)：递归引入其他 markdown，最多 5 跳
- [`paths` / `globs` / `applyTo`](#术语-paths-field)：三家工具的路径作用域字段

### 【一页结论】

[5-8 条最关键结论：
1. 入口文件用 `AGENTS.md` 命名最跨工具兼容；Claude 用户单独加一份 `CLAUDE.md` 用 `@AGENTS.md` import
2. `CLAUDE.md` 软建议 ≤ 200 行；`MEMORY.md` 硬截断 200 行 / 25 KB
3. 三种统一方案：短重定向 / @-import 路由（推荐）/ 物理冗余
4. monorepo 嵌套：`AGENTS.md` 是覆盖语义、`CLAUDE.md` 是合并语义；二者收敛到同一建议——子文件不要复制父级
5. Copilot 的 applyTo 只在 cloud-agent + code-review 生效，IDE Chat 不读
...]

### 2.1 AGENTS.md 是怎么变成事实标准的

[基于原报告 1.1 节改写。要点：
- AGENTS.md（必须解释全称：Agent Markdown）规范的演化时间线
- 治理结构：OpenAI 个人仓库 → Linux Foundation Agentic AI Foundation
- 兼容工具数量从 5 个起步、现已 23+
- 不要列原报告那张 4 列时间线表——改成段落叙述，关键节点点出"2025-08-19 公开"、"2025-08-21 扩展兼容工具"
长度：约 400 字
]

### 2.2 真实项目的入口文件长什么样

[基于 1.2 节改写。要点：
- 抽样 20+ 开源项目；按长度分四档：重型(200+) / 标准型(50-150) / 极简型(≤30) / 路由型(≤5)
- 给出代表性项目：codex / vercel-ai / langchain / vscode / cline 等
- 高频 H2 七件套：Project Overview / Build & Test / Style / Testing / Commit & PR / Do Not / Repo Structure
- 用一段话 + 一张精简表（4 列以内）展示分布
长度：约 500 字
]

### 2.3 monorepo 与多工具兼容

[整合 1.3、1.4 节。要点：
- monorepo 嵌套语义：AGENTS.md 覆盖、CLAUDE.md 合并；都收敛到"子文件不复制父级"
- "OpenAI 88 个 AGENTS.md 考据"用一句话带过（无公开证据可验）
- 多工具统一三方案对照（A 短重定向 / B @-import 路由 / C 物理冗余 + CI 同步）
- 工具兼容矩阵——关键提醒 Copilot applyTo 在 IDE Chat 不读
长度：约 600 字
]

### 2.4 长度上限与路径作用域

[整合 1.5、1.6 节。这一节是**用户最容易踩坑**的——必须详细。
- 长度对比：CLAUDE.md ≤200 行（不截断、降低遵循度）vs MEMORY.md ≤200 行/25KB（硬截断）vs Cursor ≤500 行
- 三家工具路径作用域字段：paths / globs / applyTo——格式、字段类型、旁路开关、智能描述
- 优先级合并差异（极易踩坑）三家不同：
  - Claude: local > project > user > policy
  - Cursor: Team > Project > User
  - Copilot: Personal > Repository > Organization
- 限制陷阱：Claude paths 只在读到匹配文件时加载；Cursor globs 与 alwaysApply 互斥；Copilot applyTo 在 IDE Chat 不读
长度：约 700 字
]

### 【实战速查】综合对照表

[保留原报告 1.7 节那张 7 列对照表。表前一段引子："以下表格作为单页速查，写入仓库 docs/ 即可作为团队字典使用。"]
```

- [ ] **Step 1: 通读 `report.md` 第 21-143 行**

```bash
sed -n '21,143p' /Users/lsy/clawd/research/ai-codebase-docs/report.md
```

- [ ] **Step 2: 写【核心概念盒】+【一页结论】**

按上面结构填充，每条结论一句话不超过 30 字。

- [ ] **Step 3: 依次写 2.1、2.2、2.3、2.4**

每节按指定长度。术语首次出现 → `[术语](#术语-slug)`。第一次出现 AGENTS.md / CLAUDE.md / 等术语时还要给一句话定义（即使已链到附录 A）。

例：
> [`AGENTS.md`](#术语-agentsmd)（*Agent Markdown*，AI 编码代理通用入口规范，2025-08-19 由 OpenAI 公开）已被 60 000+ 项目采用……

- [ ] **Step 4: 写【实战速查】+ 章末"下一步"指针**

下一步指针例：
> 入口文件搭好之后，下一个挑战是：怎么让 AI 看懂已经存在的几十万行代码？这是第 3 章要回答的问题。

- [ ] **Step 5: 自检**

```bash
sed -n '/## 第 2 章/,/## 第 3 章/p' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | wc -m
```

预期：8 000–12 000 字符（约 2 500–4 000 字）

```bash
# 检查必须四段都有
sed -n '/## 第 2 章/,/## 第 3 章/p' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | grep -E '^###' | head
```

预期看到：核心概念盒 / 一页结论 / 2.1 / 2.2 / 2.3 / 2.4 / 实战速查 至少 7 个 H3。

```bash
# 检查术语首次出现处都有链接
sed -n '/## 第 2 章/,/## 第 3 章/p' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | grep -oE '\[`[^`]+`\]\(#术语-' | head
```

预期至少看到 8-12 处术语链接。

- [ ] **Step 6: 保存**

---

### Task 6: 写第 3 章 场景二：让 AI 看懂存量代码

**Files:**
- Modify: `/Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md`（替换"## 第 3 章"占位符）

**Source from `report.md`：**
- 第 145-294 行（主题 2 全文，7 个子节）

**章节结构与必含内容：**

```markdown
## 第 3 章 场景二：让 AI 看懂存量代码

### 【核心概念盒】

- [`Code Map`](#术语-code-map)：matklad 范式的"目录/模块导览"
- [`ADR`](#术语-adr)：Architecture Decision Record，架构决策记录
- [`MADR`](#术语-madr)：基于 Markdown 的 ADR 规范
- [`C4 model`](#术语-c4-model) / [`arc42`](#术语-arc42)：架构图与架构手册标准
- [`Glossary`](#术语-glossary)：领域术语表
- [`Bounded Context`](#术语-bounded-context)：DDD 概念，限界上下文

### 【一页结论】

[5-8 条：
1. 存量代码文档第一公民是"Code Map + Invariants"（matklad 引用论证）
2. 架构图首选 C4 + Structurizr DSL，企业可补 arc42 第 5/6/7 章
3. ADR 模板首选 MADR（YAML frontmatter 可被 agent 程序化检索）
4. 术语表"Don't confuse with"字段是反漂移核心
5. Runbook 用 Limoncelli 7 段式骨架
6. Onboarding 30 分钟动手骨架前 200 行决定一切
]

### 3.1 找代码比改代码慢 5 倍：Code Map 为什么是第一公民

[这一节是本章**核心概念展开**——必须按"原则性描述"段落体写法（一句话总结 → 一段解释 → 例子）。
- 引 matklad 那句"Patches take 2× / locating take 10×"——给完整段落体改写，约 250 字
- 解释 Code Map 三段式：Bird's-eye view → Code map → Cross-cutting concerns
- 关键约束（matklad 原话）："Do name important files... Do not directly link them (links go stale). Explicitly call-out architectural invariants."——把这句话用段落展开，解释为什么"不放链接"反而是高维护成本下的最优选择
- 给 rust-analyzer 的 architecture.md 当样本说"模范长这样"
长度：约 600 字
]

### 3.2 架构图：C4、arc42、4+1 视图怎么选

[基于 2.1 节。要点：
- 4 个标准对照表（4 列：抽象层级 / 产物 / 适合谁 / agent 可解析性）
- 推荐 C4 + Structurizr DSL（DSL 是文本，可程序化读取，已有 MCP server）
- 大企业补 arc42 第 5/6/7 章把 C4 嵌入
- 不建议 4+1（5 视图同步成本高、UML 不利于 LLM 阅读）
- 小项目用自由 Mermaid，但 README 必须指明"这就是唯一的架构图"
- 表后必须有解读段落
长度：约 500 字
]

### 3.3 ADR：把"为什么"写下来

[基于 2.2 节。要点：
- 三模板对照：Nygard（散文）/ MADR（结构化 + frontmatter）/ Y-statement（一句话）
- AI agent 主导维护推荐 MADR——YAML 字段可程序化检索
- 实战要点：文件名 0001-xxx 编号、Status 严格枚举、不可改只能追加新 ADR、每条 ≤ 2 页
- 例子：Status 流程 proposed → accepted → deprecated → superseded by 0042
长度：约 450 字
]

### 3.4 术语表与领域语言

[基于 2.4 节 + Bounded Context 解释。要点：
- 引用 Martin Fowler 的 Ubiquitous Language 概念（必须解释全称）
- 单条术语 6 字段（English / 中文 / Bounded Context / Definition / Code mapping / Don't confuse with / Last reviewed）
- "Don't confuse with"为什么是反漂移核心——给一个 Order vs PurchaseOrder vs Invoice 的例子
- 组织方式：小项目字母序、中大型按子域分组
长度：约 400 字
]

### 3.5 Runbook 与 Onboarding 文档

[整合 2.5、2.6 节。要点：
- Runbook：Tom Limoncelli 7 段（Service Overview / Build / Deploy / Common Tasks / Pager Playbook / DR / SLA）
- Onboarding 30 分钟动手骨架：8 个 H2，前 200 行决定一切
- 优秀样本：openai/codex AGENTS.md（213 行）/ Grafana developer-guide / Kubernetes contributors/devel
长度：约 400 字
]

### 【实战速查】docs/ 目录全套骨架

[保留原报告 2.7 节那个目录树。表前一段引子。]
```

- [ ] **Step 1: 通读 `report.md` 第 145-294 行**

```bash
sed -n '145,294p' /Users/lsy/clawd/research/ai-codebase-docs/report.md
```

- [ ] **Step 2: 按上面结构依次写 3.1-3.5 + 一页结论**

特别注意 3.1 是本章核心：matklad 引用必须用"段落体"写法（设计 §3.2 的样本可参考）。

- [ ] **Step 3: 写【实战速查】+ 章末"下一步"指针**

下一步指针例：
> 存量代码描述清楚之后，新功能怎么写？这就到了第 4 章——用 AI 做增量开发。

- [ ] **Step 4: 自检**

```bash
sed -n '/## 第 3 章/,/## 第 4 章/p' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | wc -m
```

预期：8 000–12 000 字符

```bash
# 验证四段都齐
sed -n '/## 第 3 章/,/## 第 4 章/p' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | grep -E '^###' 
```

预期至少 8 个 H3 标题（包括 3.1-3.5 + 三个固定段）。

- [ ] **Step 5: 保存**

---

### Task 7: 写第 4 章 场景三：用 AI 做增量开发

**Files:**
- Modify: `/Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md`（替换"## 第 4 章"占位符）

**Source from `report.md`：**
- 第 296-386 行（主题 3 全文，6 个子节）
- 配合 `topic-3-incremental-specs.md` 子报告（如需更详细的 Spec-Kit 字段）

**章节结构与必含内容：**

```markdown
## 第 4 章 场景三：用 AI 做增量开发

### 【核心概念盒】

- [`SDD`](#术语-sdd)：Spec-Driven Development，规约驱动开发
- [`Spec-Kit`](#术语-spec-kit)：GitHub 出品的 SDD 流水线，constitution / spec / plan / tasks 四件套
- [`BMAD-METHOD`](#术语-bmad)：角色驱动的 Agile 框架
- [`Spec/Plan/Tasks 三件套`](#术语-spec-plan-tasks)：增量开发的三类核心文档
- [`Constitution`](#术语-constitution)：Spec-Kit 中不可变的项目原则
- [`INDEPENDENTLY TESTABLE`](#术语-independently-testable)：每个用户故事必须可独立测试
- [`Gherkin AC`](#术语-gherkin-ac)：Given/When/Then 验收标准格式

### 【一页结论】

[5-8 条：
1. 增量开发的统一心智模型：spec → plan → tasks，对应"做什么 / 怎么做 / 一步步做哪些"
2. spec 的硬约束：每个 user story 必须 INDEPENDENTLY TESTABLE
3. plan 的入口在 Constitution Check（Spec-Kit）——必须先过门禁才进 Phase 0
4. tasks 的并行规则 [P]：不同文件 + 无依赖 + 同一 phase 内
5. 任务粒度：Epic 1-4 周 / Story 0.5-3 天 / Task 15min-2h
6. TDD × AI 铁律：spec → test → code，test 必须先 FAIL 再 PASS
7. 决策树：diff 一句话能描述就跳过 plan；多文件或不熟悉就上 plan；新功能或重构上完整三件套
]

### 4.1 心智模型：spec → plan → tasks 解决什么问题

[这一节是本章**核心概念展开**——必须用段落体写：
- 引出问题：AI agent 容易"过度热心"——上来就改代码、不问需求
- 三件套对应"做什么 / 怎么做 / 一步步做哪些"
- 给一个具体例子：加新功能"用户头像上传"——
  - spec：用户故事、AC、成功指标
  - plan：技术选型、架构、风险
  - tasks：T001 写测试 / T002 加路由 / T003 加 storage 适配器 ...
长度：约 500 字
]

### 4.2 GitHub Spec-Kit 四件套

[基于 3.1 节。要点：
- spec-template.md 字段：User Scenarios & Testing → Requirements (FR-001) → Success Criteria → Assumptions
- plan-template.md 字段：Summary / Technical Context (9 个 advisory) / Constitution Check（GATE） / Project Structure / Complexity Tracking
- tasks-template.md 格式：[ID] [P?] [Story] Description；依赖关系 Setup → Foundational → User Stories
- "INDEPENDENTLY TESTABLE" 硬约束（一句话解释 + 例子）
长度：约 600 字
]

### 4.3 BMAD-METHOD：角色驱动的 Agile 框架

[基于 3.2 节。要点：
- Epic + Story 模板（用户故事 + Gherkin AC）
- 单 Story 模板的核心创新：task → AC 反追踪（`Task 1 (AC: 1, 3)`）
- 必须给出 path#anchor 引用源
- AC 数量经验：3-7 条；超 7 条说明 story 太大要拆
- 与 Spec-Kit 的差异：BMAD 重在"角色协作 + 全生命周期"，Spec-Kit 重在"流水线 + 严格门禁"
长度：约 400 字
]

### 4.4 决策树：什么情况下要写 plan？

[基于 3.3 节。要点：
- 引 Anthropic 原话："If you could describe the diff in one sentence, skip the plan."
- 给出 5 类场景的决策矩阵（typo/小bug/新接口/跨模块重构/新功能）
- 口诀："diff 一句话 → 直接做；多文件或不熟悉 → plan；新功能或重构 → 全套"
- 给具体例子：改 typo 跳；加新 API 端点上 plan + spec；跨模块重构上完整三件套
长度：约 450 字
]

### 4.5 任务粒度与并行规则

[基于 3.4 节。要点：
- Epic / Story / Task 三层级粒度（一个用户旅程 / 独立可测可发的切片 / 单文件改动）
- [P] 并行规则：不同文件 + 无依赖 + 同一 phase 内（必须三条都满足）
- 给一个反例：[P] 标错的情况
长度：约 350 字
]

### 4.6 TDD × AI Agent

[基于 3.5 节。**核心原则要重点展开**：
- 顺序铁律：spec → test → code（用段落体讲清为什么）
- Anthropic 原话："Include tests, screenshots, or expected outputs so Claude can check itself. This is the single highest-leverage thing you can do."——展开解释 reward signal
- 三个检查点：spec 完成后人 review / test 必须先 FAIL / tasks.md 里 test 编号 < 实现编号
- 反例：agent 一口气从 idea 到代码的失败模式
长度：约 500 字
]

### 【实战速查】Spec-Kit / BMAD 模板抄写指引

[告诉读者：完整 spec/plan/tasks 模板见 [附录 B.1](#b1-spec-plan-tasks-模板)；BMAD Epic+Story 模板见 [附录 B.2](#b2-bmad-epic-story-模板)。本节给精简骨架。]
```

- [ ] **Step 1: 通读 `report.md` 第 296-386 行**

```bash
sed -n '296,386p' /Users/lsy/clawd/research/ai-codebase-docs/report.md
```

也读一遍子报告 `topic-3-incremental-specs.md` 第 1-130 行获取细节。

- [ ] **Step 2: 写【核心概念盒】+【一页结论】**

- [ ] **Step 3: 依次写 4.1-4.6**

- [ ] **Step 4: 写【实战速查】+ 章末"下一步"指针**

> 把"做什么、怎么做、一步步做哪些"写下来还远远不够——这些文档**写完之后会腐烂**。第 5 章和第 6 章合在一起回答两个相关问题：怎么让文档与代码同步演化、以及怎么让规则不被时间侵蚀。

- [ ] **Step 5: 自检**

```bash
sed -n '/## 第 4 章/,/## 第 5 章/p' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | wc -m
sed -n '/## 第 4 章/,/## 第 5 章/p' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | grep -E '^###'
```

预期：≥ 8 000 字符；至少 9 个 H3。

- [ ] **Step 6: 保存**

---

### Task 8: 写第 5 章 场景四：把文档维护成代码

**Files:**
- Modify: `/Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md`（替换"## 第 5 章"占位符）

**Source from `report.md`：**
- 第 388-520 行（主题 4 全文，9 个子节）

**章节结构：**

```markdown
## 第 5 章 场景四：把文档维护成代码

### 【核心概念盒】

- [`Vale`](#术语-vale)：散文风格检查工具，覆盖术语/拼写/句法
- [`markdownlint-cli2`](#术语-markdownlint)：Markdown 结构 lint
- [`lychee`](#术语-lychee)：链接失效检查，Rust 编写、大仓快 5-30×
- [`CODEOWNERS`](#术语-codeowners)：GitHub 的文件归属机制
- [`dorny/paths-filter`](#术语-paths-filter)：PR 路径过滤守卫

### 【一页结论】

[6-8 条：
1. 文档静态检查 = Vale + markdownlint-cli2 双轨
2. 链接检查首选 lychee（速度+缓存压倒性）
3. 双层链接检查策略：增量 PR 守门 + 全量定期巡检
4. PR 门禁：dorny/paths-filter 防止"代码改了 docs 没改"
5. 文档审批：CODEOWNERS + Branch Protection 给 docs/ 指定 tech writer
6. 自动 vs 手写：API 签名/类型自动；架构/为什么/runbook 手写
7. 文档覆盖率：业界无统一指标，自建"src 行变 / docs 行变"比 (健康值 0.05-0.30)
8. Claude Code hooks 8 个最值的事件配置
]

### 5.1 docs-as-code 是什么、不是什么

[基于 4.1-4.2 节背景。要点：
- docs-as-code 范式四要素：文档与代码同仓 + PR 门禁 + CI 校验 + CODEOWNERS
- 反例：文档放 wiki（无 PR、无版本、无 review）→ 失败模式
- 给一个例子：文档跟代码同 PR vs 文档单独 PR 的差异
长度：约 400 字
]

### 5.2 静态检查工具组合：Vale + markdownlint + lychee

[整合 4.2、4.3 节。要点：
- Vale 用 Go 写、覆盖最广，社区有 Google/Microsoft/RedHat 现成包
- markdownlint-cli2 覆盖结构层（标题、列表、代码围栏）
- 二者互补：Vale 不查标题层级、markdownlint 不查术语
- lychee 用 Rust 写、异步并发、自带缓存
- 双层链接检查：增量 PR + 全量 cron
- 完整 .vale.ini / .markdownlint.json / lychee.toml 配置见 [附录 B.4](#b4-docs-as-code-工具配置)
长度：约 600 字
]

### 5.3 PR 门禁：让文档落后于代码不能合并

[基于 4.4 节。要点：
- CODEOWNERS：区分大小写、`/docs/` 含全部子目录、Branch Protection "Require review from Code Owners"
- dorny/paths-filter 双 filter 实战：检测 src/** 改而 docs/** 未改时失败
- 进阶：动核心目录（src/auth/、src/db/）必须新增/更新 ADR
- 给一个简化的 GitHub Actions 片段（5-10 行骨架），完整脚本见 [附录 B.5](#b5-pr-门禁配置)
长度：约 500 字
]

### 5.4 自动生成 vs 手写：what/where 自动；why/when 手写

[基于 4.5 节。**这是核心原则**——必须用段落体展开。
- 引一段话起头：什么内容必须自动生成（API 签名/类型）、什么必须手写（架构/为什么/runbook）
- 给具体例子：OpenAPI 自动生成接口签名 vs 手写"为什么这字段必需"
- 引用关系四要素：路径+行号 / 测试文件路径 / ADR 链接 / Last verified 时间戳 + git sha
长度：约 450 字
]

### 5.5 Claude Code hooks：让 agent 自动遵守

[基于 4.6 节。要点：
- 8 个最有用的 hook 事件：SessionStart / UserPromptSubmit / PreToolUse / PostToolUse / Stop / PreCompact ……
- 三个关键脚本（block-docs-write / remind-docs / inject-stale-warning）说明用途，完整脚本见 [附录 B.6](#b6-claude-code-hooks-脚本)
长度：约 400 字
]

### 5.6 文档覆盖率与 review 文化

[整合 4.7、4.8 节。要点：
- 三个自建指标：A 比例 / B 过期率 / C agent 引用率
- GitLab Handbook 四角色铁律（Developer / PM / Tech Writer non-blocking / Maintainer 合并权）
- Stripe / Vercel 的不同打法
长度：约 400 字
]

### 【实战速查】三档配方

[基于 4.9 节。
- 配方 1（个人/小团队）：markdownlint + lychee 周末手动
- 配方 2（5-30 人，主推）：完整 GitHub Actions + CODEOWNERS + Vale + Claude hooks + 自建指标 A
- 配方 3（企业）：配方 2 + OpenAPI 自动生成 + ADR-required + 全指标仪表盘
表前一段引子。]
```

- [ ] **Step 1: 通读 `report.md` 第 388-520 行**

- [ ] **Step 2-3: 按结构写各小节**

- [ ] **Step 4: 写章末"下一步"指针**

> 文档已经自动化校验了——但**规则本身**也会过期：去年写的"用 npm"今年要改成"用 pnpm"，CLAUDE.md 越长就越没人遵守。第 6 章把视角从"文档 vs 代码"切到"规则 vs 时间"。

- [ ] **Step 5: 自检 + 保存**

```bash
sed -n '/## 第 5 章/,/## 第 6 章/p' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | wc -m
```

预期：≥ 8 000 字符。

---

### Task 9: 写第 6 章 场景五：让文档与规则不腐烂

**Files:**
- Modify: `/Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md`（替换"## 第 6 章"占位符）

**Source from `report.md`：**
- 第 522-725 行（主题 5 全文，9 个子节）

**章节结构：**

```markdown
## 第 6 章 场景五：让文档与规则不腐烂

### 【核心概念盒】

- [`JIT 检索`](#术语-jit-retrieval)：Just-In-Time，按需加载
- [`auto memory`](#术语-auto-memory)：Claude Code v2.1.59+ 的自动记忆机制
- [`compaction`](#术语-compaction)：长会话上下文压缩
- [`context rot`](#术语-context-rot)：上下文过载导致的注意力稀释
- [`InstructionsLoaded`](#术语-instructionsloaded)：规则加载事件 hook
- [`PreToolUse`](#术语-pretooluse)：工具调用前 hook

### 【一页结论】

[8-10 条：
1. JIT 检索 vs preload：保留路径/查询，运行时再取数据
2. CLAUDE.md ≤ 200 行；MEMORY.md 硬截断 200 行/25KB
3. auto memory 是"agent 自写、人后审"，不是 CLAUDE.md 的别名
4. InstructionsLoaded hook 只能审计加载、不能审计遵守
5. 失效信号三种：同一会话纠正 ≥ 2 次 / audit log 0 命中 / compaction 后重犯
6. /memory 周审计 SOP 15 项 checklist
7. 上下文压力根因：n² attention + 训练分布偏差
8. compaction 后 nested CLAUDE.md 不会自动重注入
9. Skill 长会话被静默驱逐：25000 token 共享预算
10. "YOU MUST" 用多了等于没用
]

### 6.1 上下文工程的根问题：n² attention 与 context rot

[这一节核心概念展开——用段落体。要点：
- 引 Anthropic 原话：preload 是反模式，agent 应保留 lightweight identifiers + 运行时取
- "n² attention" 用一段话解释（必须给全称：每多一个 token 就多 n 个新关系）
- "context rot" 解释：长上下文降低对单条规则的遵循度
- 例子：把整个 src/api/ 塞进 CLAUDE.md vs 用 Grep 按需检索
长度：约 500 字
]

### 6.2 auto memory 是什么、和 CLAUDE.md 怎么分工

[基于 5.2 节。**这是用户最容易混淆的**——必须详细。
- 存储位置：~/.claude/projects/<project>/memory/
- 写入触发：显式（用户 "remember"）/ 隐式（agent 自决）
- auto memory vs CLAUDE.md 对照表（5 维：谁写 / 内容 / 作用域 / 加载量 / 团队共享）
- 关键差异：auto memory per working tree 不上传；MEMORY.md 截断加载
长度：约 500 字
]

### 6.3 失效信号检测

[基于 5.3 节。要点：
- InstructionsLoaded hook 的载荷字段
- 限制：hook 不阻塞、不能改加载内容
- 三个间接信号（同一会话两次纠正 / 0 命中 / compaction 后重犯）
长度：约 350 字
]

### 6.4 周审计 SOP 与剪枝决策树

[基于 5.4 节。要点：
- 15 项 checklist（精炼成段落体描述，不要原样列 15 个 bullet——分组讲）
- 剪枝决策树：agent 没它也对 → 删；agent 经常违反 → 转 hook ……
- 给一个具体例子：一条 "use pnpm" 规则的演化（CLAUDE.md → audit 0 命中 → 转 hook）
长度：约 600 字
]

### 6.5 失败模式：13 种反模式

[基于 5.5、5.6 节。要点：
- Anthropic 官方 5 模式 + 社区补充 8 种
- 不要原样抄表——按"短期 / 长期 / 工具类"分组讲，每种模式一段
- 关键提示：早期信号 + 根因 + 对策（每模式约 100 字）
长度：约 800 字
]

### 6.6 决策树：新知识进哪一层？

[基于 5.7 节。要点：
- 把原报告那张决策树用更连贯的段落讲一遍
- 强调"反例"：不该沉淀的内容（单次 bug 调试 / 文件级描述 / 标准库知识）
长度：约 450 字
]

### 【实战速查】五条最反直觉的发现

[基于 5.9 节。直接保留五条+稍作改写]
```

- [ ] **Step 1-3: 通读 + 写各小节**

- [ ] **Step 4: 章末"下一步"指针**

> 至此你已经具备搭建一套 AI 友好文档体系的全部"零件"。但具体到自己的项目应该用 vanilla AGENTS.md、Spec-Kit 还是 BMAD？第 7 章给出选型与迁移路径。

- [ ] **Step 5: 自检 + 保存**

```bash
sed -n '/## 第 6 章/,/## 第 7 章/p' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | wc -m
```

预期：≥ 10 000 字符（本章是最长之一）。

---

### Task 10: 写第 7 章 方法论选型与迁移

**Files:**
- Modify: `/Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md`（替换"## 第 7 章"占位符）

**Source from `report.md`：**
- 第 727-885 行（主题 6 全文，9 个子节）

**章节结构：**

```markdown
## 第 7 章 方法论选型与迁移

### 【核心概念盒】

- vanilla AGENTS.md：约定层
- [`Spec-Kit`](#术语-spec-kit)：流程层（SDD 流水线）
- [`BMAD-METHOD`](#术语-bmad)：组织+流程+角色层
- [`OpenSpec`](#术语-openspec)：以 spec deltas 为核心
- 三类项目阶梯：约定 → 流程 → 组织

### 【一页结论】

[5-8 条：
1. vanilla / Aider / Spec-Kit / BMAD 是约定→流程→组织三阶梯
2. Spec-Kit 自身警告 over-engineering；BMAD 实测小 MVP 慢 10-15×
3. brownfield 慎用 Spec-Kit / BMAD，优先 OpenSpec 或自写
4. 重型方法论的退化路径已被走通：BMAD 当规划工具，实施切回 vanilla
5. 多工具中立化：@-import + AGENTS.md
6. 模型推理能力提升 → 重型 SDD 边际价值下降（长期看空信号）
]

### 7.1 三阶梯心智模型

[基于 6.1 节核心。**用段落体展开**：
- 约定层：用一份 markdown 写规则；适合个人/小团队
- 流程层：用流水线（spec/plan/tasks）；适合中大团队、跨 PR feature
- 组织层：用角色驱动（PM/Architect/SM/Dev）；适合企业、强治理
- 跨阶梯升级是反模式：从约定直接跳组织，团队心智成本爆炸
- 给一个例子：3 人小团队上 BMAD 的失败模式
长度：约 500 字
]

### 7.2 四套方法论对照

[基于 6.1 节那张 10 列表格——但**不要原样抄表**，分维度讲：
- 核心范式（一句话定位每个）
- 上手成本（< 30 min / 0.5-1 天 / 1-3 天）
- brownfield 适配
- prompt cache 友好度
- 退化路径
配一张精简对照表（4-5 列），表前后必须有叙述
长度：约 600 字
]

### 7.3 选型决策树

[基于 6.3 节。要点：
- 按"项目规模 × 多人协作 × 治理强度"决策
- 5 档：个人 / 1-3 人 / 4-10 人 / 跨团队 / 企业
- 每档对应推荐与升级触发点
- 反信号（不要升级）：项目即将 sunset / 团队 ≤2 人 / 业务节奏比流程僵化敏感
长度：约 500 字
]

### 7.4 升级路径与精简实战

[整合 6.4、6.5 节。要点：
- 5 个升级触发点（入口 > 200 行 / agent 频繁忽略 / 跨 5+ PR / 上手 > 1 周 / 跨团队合规）
- 精简信号：spec 数 > 已实现 feature ×2 / 团队抱怨写 spec 慢 / agent 绕过流程 / cache miss 率高
- BMAD → vanilla 三步实战（保留 planning / 抽要点入 CLAUDE.md / 抛弃 SM/Dev 编排）
长度：约 600 字
]

### 7.5 方法论混搭与多工具中立化

[整合 6.6、6.7 节。要点：
- Spec-Kit + .claude/skills 是官方建议（discussion #2268 引用）
- 三层解耦：constitution（不可变）+ AGENTS.md（跨工具入口）+ skills（可执行 procedure）
- 反模式：同时跑 Spec-Kit 和 BMAD 完整流程
- 多工具中立化三方案：symlink / @-import（推荐）/ git submodule
长度：约 500 字
]

### 7.6 反方观点：为什么有人不用

[基于 6.8 节。要点：
- Spec-Kit 反方：官方自承 over-engineering / Discussion #2315 7 个不足 / ThoughtWorks 评估
- BMAD 反方：Issue #2003 实测 10-15× / Issue #1930 重写已完成 story
- 共同长期看空：模型能力提升后重型 SDD 边际价值下降
长度：约 400 字
]

### 【实战速查】Key Takeaways 清单
```

- [ ] **Step 1-4: 通读 + 写各小节 + 章末指针**

> 第 7 章给完了选型方法。最后一章把所有零件拼成一个完整的仓库骨架——从一开始就照搬即可。

- [ ] **Step 5: 自检 + 保存**

---
## Phase C — 收尾与附录（任务 11-14）

### Task 11: 写第 8 章 综合建议与仓库骨架

**Files:**
- Modify: `/Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md`（替换"## 第 8 章"占位符）

**Source from `report.md`：**
- 第 887-950 行（综合建议与仓库骨架）

**章节结构：**

```markdown
## 第 8 章 综合建议与仓库骨架

### 8.1 信息密度排序：agent 30 分钟内最需要什么

[基于 887-901 行。改写为段落体：
- 引出问题：入口文件篇幅有限，应该先放什么？
- 6 类内容按"agent 第一时间最需要"排序：
  1. Quickstart 命令（30%）
  2. Repo layout + 不变量（25%）
  3. How to make a change（15%）
  4. Where to look first（15%）
  5. Troubleshooting top 3（10%）
  6. 指针到深度文档（5%）
- 反例：背景故事 / 产品愿景 / 架构演进史不该进 AGENTS.md，应放 ARCHITECTURE.md
长度：约 400 字
]

### 8.2 推荐仓库骨架：从一开始照搬即可

[保留原报告 901-950 行那个目录树。表前一段引子：
"以下是一个综合本指南所有结论的中型项目仓库骨架（5–30 人团队、单 monorepo、Claude Code + Cursor + Copilot 三工具混用）。新项目可直接照搬，老项目可按需对号入座。"
表后必须加一段叙述：解释这个骨架的几个关键决策——为什么 AGENTS.md 在根、为什么 .claude/rules/ 而不是 .claude/CLAUDE.md/、为什么有 CLAUDE.local.md 等]
长度：约 600 字（含目录树）
```

- [ ] **Step 1-3**: 通读 + 写两节 + 章末"下一步"

下一步指针：
> 完整骨架已经放在你面前——现在该动手做一份属于你团队的 `AGENTS.md`、`docs/` 与 `.claude/`。需要的所有模板都在附录 B；权威源链接都在附录 C；遇到陌生术语随时跳附录 A。祝顺利。

- [ ] **Step 4: 保存**

---

### Task 12: 写附录 B 模板与脚本

**Files:**
- Modify: `/Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md`（替换"## 附录 B"占位符）

**Source from `report.md`** + **`topic-3-incremental-specs.md`** + **`topic-4-docs-as-code.md`**

**目的**：把所有"主体只放骨架"的完整模板/脚本/配置文件归到这里。读者在正文看到"完整模板见附录 B.X"时跳过来。

**附录 B 子节安排：**

```markdown
## 附录 B：模板与脚本

### B.1 spec.md / plan.md / tasks.md 完整模板

[抽取自 GitHub Spec-Kit 模板原文。每个模板放一个完整骨架（30-50 行）。一段简短引子说明 GitHub Spec-Kit 来源。]

### B.2 BMAD Epic + Story 模板

[抽取自 BMAD-METHOD 仓库 src/bmm-skills/。完整 Epic + 单 Story 骨架。]

### B.3 ADR (MADR) 模板

[抽取自 adr.github.io/madr/。一个完整 MADR 4.0 模板示例。]

### B.4 ARCHITECTURE.md (matklad 三段式) 模板

[3 个 H2: Bird's-eye view / Code map / Cross-cutting concerns，每段一段示例文字。]

### B.5 Runbook 模板（Limoncelli 7 段）

[抽取自 PagerDuty 文档。完整 7 段骨架。]

### B.6 docs-as-code 工具配置

#### B.6.1 .vale.ini
#### B.6.2 .markdownlint.json
#### B.6.3 lychee.toml
[每个完整配置 10-30 行]

### B.7 GitHub Actions 工作流

#### B.7.1 docs-lint.yml
#### B.7.2 links.yml
#### B.7.3 docs-required.yml
[每个完整 YAML 20-40 行]

### B.8 Claude Code hooks 实战脚本

#### B.8.1 settings.json hooks 配置
#### B.8.2 block-docs-write.sh
#### B.8.3 remind-docs.sh
#### B.8.4 inject-stale-warning.sh
[每个完整 bash 脚本 10-30 行]

### B.9 仓库骨架完整目录树

[把第 8.2 节那个目录树也复制到这里方便单独查阅]
```

- [ ] **Step 1: 从 report.md 与子报告抽取所有模板**

```bash
# 从 report.md 找出代码块
grep -n '```' /Users/lsy/clawd/research/ai-codebase-docs/report.md | head -40
```

```bash
sed -n '/```yaml/,/```/p' /Users/lsy/clawd/research/ai-codebase-docs/topic-3-incremental-specs.md
sed -n '/```yaml/,/```/p' /Users/lsy/clawd/research/ai-codebase-docs/topic-4-docs-as-code.md
```

- [ ] **Step 2: 按 B.1-B.9 顺序填充**

每节都要：
1. 一段简短说明（为什么这模板有用、来源是哪里）
2. 完整代码块
3. 关键字段或行的简短注释（如果不是显然）

- [ ] **Step 3: 验证锚点齐全**

```bash
sed -n '/## 附录 B/,/## 附录 C/p' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | grep -E '^### B\.'
```

预期至少 9 个 H3（B.1 - B.9）。

- [ ] **Step 4: 验证章正文引用都有对应附录锚点**

```bash
# 查所有正文里的 "附录 B.X" 引用
grep -E '附录 B\.[0-9]' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md
```

每条引用都应能在附录 B 找到对应小节。

- [ ] **Step 5: 保存**

---

### Task 13: 写附录 C 参考资源

**Files:**
- Modify: `/Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md`（替换"## 附录 C"占位符）

**Source from `report.md`：**
- 第 952-991 行（Sources 章节，35 条原始外链）

**目的**：把全部外部权威源整理成"按主题分组"的参考资源列表。每条必须指出"在本指南哪里被引用"。

**章节结构：**

```markdown
## 附录 C：参考资源

### C.1 入口规范与协议

- [agents.md — Open spec for coding agent docs](https://agents.md) — 60k+ 项目使用，跨工具事实标准。引用于：第 2 章、附录 A 术语-agentsmd。
- ...

### C.2 Anthropic 官方文档（Claude Code 体系）

[6 份 Anthropic 文档：Memory & CLAUDE.md / Best Practices / Effective Context Engineering / Hooks / Skills / etc.]

### C.3 工具类（Claude / Cursor / Copilot / Aider）

### C.4 架构与决策

[matklad / C4 / arc42 / MADR / Structurizr / dependency-cruiser]

### C.5 增量开发框架

[Spec-Kit / BMAD-METHOD / OpenSpec / BMAD-AT-CLAUDE]

### C.6 Docs-as-Code 工具

[Vale / lychee / markdownlint / dorny/paths-filter / Write The Docs / GitLab Workflow]

### C.7 行业基准与评估

[ThoughtWorks Tech Radar / Google SRE Book / PagerDuty Runbook / Stripe / Vercel / Martin Fowler]

### C.8 真实开源项目入口文件样本

[openai/codex AGENTS.md / vercel/ai AGENTS.md / Microsoft/vscode / cline/cline]
```

- [ ] **Step 1: 把 report.md 第 952-991 行的 35 条按上面 8 类分组**

- [ ] **Step 2: 每条加上"引用于：第 X 章 / 附录 A 术语-Y"**

需要全文 grep 找：
```bash
# 比如查 vale.sh 出现在哪
grep -n 'vale.sh\|Vale' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md
```

- [ ] **Step 3: 自检每条至少被正文引用一次**

```bash
# 提取附录 C 所有 URL
grep -oE 'https://[^ )]+' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | sort -u | wc -l
```

预期：≥ 35 条独立 URL。

- [ ] **Step 4: 保存**

---

### Task 14: 全文通读与最终自检

**Files:**
- Read & verify: `/Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md`

**目的**：按 spec §7 的 8 项验收标准逐项核查。

- [ ] **Step 1: 全文字数与篇幅**

```bash
wc -l /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md
wc -m /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md
```

预期：行数 1500-2500；字符数 60 000–90 000（约 24 000–30 000 中文字）。

- [ ] **Step 2: 章节齐全**

```bash
grep -c '^## ' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md
```

预期：13（引言 + 8 章 + 附录 A/B/C + 标题）。

- [ ] **Step 3: 每章四段式齐全**

```bash
for i in 2 3 4 5 6; do
  echo "=== 第 $i 章 ==="
  sed -n "/## 第 $i 章/,/^## 第/p" /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | grep -E '核心概念盒|一页结论|实战速查' | head -5
done
```

预期：每章都看到三个固定段标题。

- [ ] **Step 4: 术语首次出现处都有链接**

```bash
# 统计术语跳转链接总数
grep -oE '\[`[^`]+`\]\(#术语-' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | wc -l
```

预期：≥ 60 处（6 个场景章每章约 8-12 个术语链接）。

```bash
# 检查所有 #术语-xxx 锚点都在附录 A 存在
grep -oE '#术语-[a-z-]+' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | sort -u > /tmp/used-anchors.txt
sed -n '/## 附录 A/,/## 附录 B/p' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | grep -oE '术语-[a-z-]+' | sort -u > /tmp/defined-anchors.txt
diff <(sed 's/#//' /tmp/used-anchors.txt) /tmp/defined-anchors.txt
```

预期：diff 输出为空（所有引用的锚点都在附录 A 存在）。

- [ ] **Step 5: 缩写都给了全称**

人工抽查：随机挑 5 个缩写（SDD、ADR、MADR、JIT、AC）查找首次出现处，确认都有 *斜体英文全称*。

```bash
# 找 SDD 首次出现
grep -n 'SDD' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | head -3
```

第一处必须含 `*Spec-Driven Development*`。其它缩写同理。

- [ ] **Step 6: 没有连续两个对照表之间无引子**

人工通读检查：找到所有 `|---|---|` 对照表，前面一段必须是叙述（不能直接接前一个表）。

```bash
# 找连续表格的位置
grep -n '^|' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | head -20
```

- [ ] **Step 7: 章末"下一步"指针**

```bash
for i in 2 3 4 5 6 7; do
  echo "=== 第 $i 章末 ==="
  sed -n "/## 第 $i 章/,/^## 第 $((i+1)) 章/p" /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | tail -8
done
```

预期：每章末 5-8 行内出现"下一步"或对下一章/附录的引用。

- [ ] **Step 8: 附录 C 每条参考资源至少被正文引用一次**

```bash
# 提取附录 C 中所有 URL，逐个 grep 全文看出现 ≥ 2 次（一次在附录、≥ 一次在正文）
sed -n '/## 附录 C/,$p' /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md | grep -oE 'https://[^ )]+' | sort -u | while read url; do
  count=$(grep -c "$url" /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md)
  if [ "$count" -lt 2 ]; then
    echo "WARN: $url 仅出现 $count 次"
  fi
done
```

预期：无 WARN 输出（每条 URL 在正文 + 附录都出现，至少 2 次）。

- [ ] **Step 9: 段落感检查（不堆砌名词）**

抽查每章的"概念盒"和"一页结论"之外的小节：随机挑 3-5 个 H3 段，确认开头不是直接抛对照表，而是有引子段落。

- [ ] **Step 10: markdown lint**

```bash
# 如果系统装了 markdownlint-cli2 就跑一遍
which markdownlint-cli2 && markdownlint-cli2 /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md || echo "markdownlint-cli2 未安装，跳过"
```

如有问题修正；如未安装跳过此步。

- [ ] **Step 11: 修复发现的所有问题**

按上面 Step 1-10 的输出逐项修补。每修一个 → 重跑相应 step → 通过后继续下一个。

- [ ] **Step 12: 最终交付**

```bash
ls -la /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md
wc -m /Users/lsy/clawd/research/ai-codebase-docs/结构化文档指南.md
```

确认文件最终大小落在预算 60 000–90 000 字符内。如果偏离 ±20%，决定是否需要补/裁。

---

## Self-Review (writing-plans 自检结果)

**Spec coverage 检查**：

- ✅ 4 条原则（术语解释 / 段落体 / 概念聚合 / 引用跳转）→ 在 Task 4-10 都有对应自检步骤
- ✅ 章节大纲（引言 + 8 章 + 附录 A/B/C）→ Task 1 骨架 + Task 2-13 逐章实现
- ✅ "概念盒/一页结论/正文/实战速查"四段式→ Task 5-9 每章模板都列出
- ✅ 术语三跳引用（正文 → 附录 A → 外部源）→ Task 4 + Task 14 Step 4 验证
- ✅ ~30+ 条术语清单 → Task 4 列出 43 条具体目标
- ✅ 长度预算 24 000-30 000 字 → Task 14 Step 1 验证
- ✅ 8 项验收标准 → Task 14 逐项 Step 1-9
- ✅ 3 处主动叙事补充（每章为什么 / 章节连接 / 章末下一步）→ Task 5-10 每个都有"下一步"步骤
- ✅ 内容剔除（Methodology 章 / 考据元信息）→ 设计已声明，实施时自然不复制

**Placeholder 扫描**：无 TBD/TODO/"实现细节"留白；每个 task 都给出了 Source 行号 + 章节结构 + 自检命令。

**Type/锚点一致性**：术语 slug 命名规则在 Task 4 给出（小写 + 连字符），所有章正文引用使用 `[术语](#术语-slug)` 格式与 Task 4 锚点对齐；Task 14 Step 4 用 diff 自动验证。

**Scope 检查**：单文件交付物，scope 单一，不需要拆 sub-project。

---

## 执行交接（Execution Handoff）

Plan 完成并保存到 `/Users/lsy/clawd/research/ai-codebase-docs/docs/superpowers/plans/2026-04-26-restructured-doc-guide.md`。

**重要：当前目录不是 git 仓库**，所以 `subagent-driven-development` 会失去 commit-per-task 的隔离能力——每个 subagent 仍可以独立交付一个章节，但回滚要靠手工。

两种执行选项：

1. **Subagent-Driven（推荐）**——每个 task 派一个新的 subagent 处理，主对话只做评审；优点是 14 个 task 串行下来主上下文不会被填满，每章质量更稳定；缺点是无 git 时回滚要靠手工。

2. **Inline Execution**——本会话直接连续执行 14 个 task，每个里程碑（Phase A 末 / 每章末 / 全文末）暂停由你确认；优点是流程紧凑、即时反馈；缺点是 14 章下来上下文压力大、可能影响后段质量。

你想用哪种方式？
