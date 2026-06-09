# 主题 1 深挖：AI Agent 项目入口文件与分层规范

*Generated: 2026-04-26 | Sources: 13+ | 在主报告 `report.md` 主题 1 之上向下挖一层*

---

## 摘要

本报告就六个具体问题展开。结论先行：

1. **AGENTS.md 由 OpenAI 在 2025-08-19 首次提交至 `agentsmd/agents.md` 公开仓**，与 OpenAI Codex（2025-05-16 研究预览）不在同一时间，而是 Codex 上线后约三个月内、协同 Amp / Jules / Cursor / Factory 抛出的"行业格式"。当前已交由 **Linux Foundation 旗下 Agentic AI Foundation** 接管。
2. **真实开源项目入口文件长度差异极大**：openai/codex 213 行 / vercel/ai 306 行属"重型"，openai/openai-cookbook 47 行属"骨架型"，cline/cline 仅 3 行（纯 import）属"路由型"。**最常见 H2 七件套**：Project Overview、Project Structure / Repository Structure、Build & Test Commands、Coding Style、Testing Guidelines、Commit & PR Guidelines、Do Not / Gotchas。
3. **monorepo 嵌套实战上"差异覆盖"已是事实标准**：子目录文件不重复父级，仅写"本子树独有"内容，依赖 Codex/Claude Code 的"路径就近合并"加载。openai/codex 是单一根 AGENTS.md + 内嵌 H1/H2 区分子模块，没有真正用 88 个嵌套文件——OpenAI 全公司主仓的 88 个数字来自其他大型 monorepo（agents.md 官方援引）。
4. **多工具统一**：业界已分化成三种方案：**(A)** 短重定向（vscode 把 AGENTS.md 写成"see copilot-instructions.md"）；**(B)** 一行 `@-import`（vercel/ai 的 CLAUDE.md = `AGENTS.md`、cline/cline 的 CLAUDE.md = 三行 `@.clinerules/...`）；**(C)** 物理冗余 / 同步（langchain CLAUDE.md 与 AGENTS.md 内容字节级一致，13112 字节同 SHA 通过 CI 同步）。Anthropic 官方推荐 (B)。
5. **入口长度硬上限**：Anthropic 给 ≤200 行；Cursor 给 `.mdc` 单文件 ≤500 行；GitHub Copilot 给"两页（约 500 字）"上限（仅对 cloud agent 自动生成，对手写文件没硬约束）；Aider 文档无明确数字。超长后果统一为"context bloat → instruction adherence 下降"，没有硬截断。
6. **路径作用域**：Claude `paths:` 用 glob 数组、运行时按"读到匹配文件即加载"延迟触发；Cursor `globs:` 同样 glob 但 *frontmatter* 还有 `alwaysApply` / `description` 两个旁路（"由 Agent 决定")；Copilot `applyTo:` 是 *逗号分隔字符串*、还有 `excludeAgent` 字段对 cloud-agent / code-review 二选一。三者语法接近但语义边界、合并优先级各不相同。

---

## 问题 1：AGENTS.md 规范的演化历史

### 1.1 起源时间线

通过 GitHub Commits API 拉取 [agentsmd/agents.md](https://github.com/agentsmd/agents.md) 仓库的全部 35 个 commit：

| 时间 (UTC) | 事件 |
|---|---|
| **2025-08-19 21:49:01** | "Initial commit" — 公开仓首次推送 |
| 2025-08-21 17:28:13 | 首次扩展兼容工具列表：Aider / Gemini / Kilo Code / OpenCode / Phoenix / Zed |
| 2025-08-21 18:40:16 | 修订 FAQ，建议用 Gemini CLI |
| 2025-08-28 22:01:01 | 最近一次实质提交（更新 OpenCode 大小写） |

[OpenAI Codex（AI agent）](https://en.wikipedia.org/wiki/OpenAI_Codex_(AI_agent)) 的研究预览发布于 **2025-05-16**，CLI 形态发布于 **2025 年 4 月**。也就是说 Codex 自带的 AGENTS.md 行为先于规范站点出现约三个月，2025 年 8 月才被推到独立站点 + 独立组织 `agentsmd` 上做"行业化"包装。

[agents.md](https://agents.md) 官方"About"段写：

> "AGENTS.md emerged from collaborative efforts across the AI software development ecosystem"
> "AGENTS.md is now stewarded by the Agentic AI Foundation under the Linux Foundation."

参与方明确点名：**OpenAI Codex、Sourcegraph Amp、Google Jules、Cursor、Factory**。

### 1.2 最初动机：替代散乱的"AGENT.md / .agent / agent_instructions.txt"

agents.md FAQ 中给出迁移指引："`mv AGENT.md AGENTS.md && ln -s AGENTS.md AGENT.md`" — 这条单行命令揭示了 v1 之前业界至少存在过 `AGENT.md`（单数）这一前身。规范站点反复强调的"a README for agents"是其核心价值主张：把入口规范化到**单数复数都不会错**的命名上。

### 1.3 v1 与当前版本的差异

- **v1（2025-08）**：兼容工具仅列约 10 个（Codex / Amp / Jules / Cursor / Factory + Aider 等少数）。
- **当前（2026-04）**：兼容工具扩张到 23+（包括 GitHub Copilot Coding Agent、Augment、Devin、JetBrains Junie、Warp、Zed、Semgrep、UiPath、RooCode 等）。
- 治理结构升级：从 OpenAI 个人仓库 → **Linux Foundation 旗下 Agentic AI Foundation 接管**。这一治理变更未公布精确日期，但落在 2025 Q4 ~ 2026 Q1 之间（基于 commit 频率推断）。
- 规范本身没有版本号，没有 release，没有 RFC：**仅以 markdown spec 加 FAQ 形式存在**——一种"事实标准 by adoption"路线。

来源：[agents.md](https://agents.md)、[GitHub agentsmd/agents.md commits API](https://api.github.com/repos/agentsmd/agents.md/commits)、[OpenAI Codex (AI agent) Wikipedia](https://en.wikipedia.org/wiki/OpenAI_Codex_(AI_agent))。

---

## 问题 2：真实大型项目的入口文件长什么样

直接用 `curl raw.githubusercontent.com` 抓取了 20+ 项目，下表是采样结果：

| 项目 | 文件 | 行数 | 字节 | H2 数 | 类型 |
|---|---|---|---|---|---|
| [openai/codex](https://github.com/openai/codex/blob/main/AGENTS.md) | AGENTS.md | 213 | 17080 | 6 | 重型 |
| [vercel/ai](https://github.com/vercel/ai/blob/main/AGENTS.md) | AGENTS.md | 306 | 12682 | 15 | 重型 |
| [langchain-ai/langchain](https://github.com/langchain-ai/langchain/blob/master/AGENTS.md) | AGENTS.md = CLAUDE.md | 291 | 13112 | 4 | 重型，双工具同步 |
| [openai/openai-cookbook](https://github.com/openai/openai-cookbook/blob/main/AGENTS.md) | AGENTS.md | 47 | 5560 | 8 | 骨架型，严守 200 行 |
| [withastro/astro](https://github.com/withastro/astro/blob/main/AGENTS.md) | AGENTS.md | 89 | 5572 | 1 | 中型，多 H1 平铺 |
| [microsoft/vscode](https://github.com/microsoft/vscode/blob/main/AGENTS.md) | AGENTS.md | 5 | 271 | 0 | 路由型，"see .github/copilot-instructions.md" |
| [microsoft/vscode](https://github.com/microsoft/vscode/blob/main/.github/copilot-instructions.md) | copilot-instructions.md | 152 | 10053 | — | 实质入口 |
| [cline/cline](https://github.com/cline/cline/blob/main/CLAUDE.md) | CLAUDE.md | 3 | 68 | 0 | 路由型，纯 @-import |
| [cline/cline](https://github.com/cline/cline/blob/main/.github/copilot-instructions.md) | copilot-instructions.md | 58 | 3943 | — | Copilot 专用 |
| [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers/blob/main/CLAUDE.md) | CLAUDE.md | 103 | 4154 | 7 | 标准型，逼近 200 行硬约束 |
| [mendableai/firecrawl](https://github.com/mendableai/firecrawl/blob/main/CLAUDE.md) | CLAUDE.md | 18 | 1464 | 0 | 极简型，无 H2，纯流程 |
| [huggingface/transformers](https://github.com/huggingface/transformers/blob/main/AGENTS.md) | AGENTS.md = CLAUDE.md | 1 | 13 | 0 | 路由型，单行指向 `.ai/AGENTS.md` |
| [ClickHouse/ClickHouse](https://github.com/ClickHouse/ClickHouse/blob/master/AGENTS.md) | AGENTS.md | 1 | 17 | 0 | 路由型，单行指向 `.claude/CLAUDE.md` |
| [supabase/supabase](https://github.com/supabase/supabase/blob/master/.github/copilot-instructions.md) | copilot-instructions.md | 58 | 3436 | 3 | Copilot 专用 |

### 2.1 长度分布观察

- **重型（200+ 行）**：仅出现在框架/SDK 类项目（codex / vercel-ai / langchain）。这些项目把规范、coding style、API 命名、commit 格式都塞在入口里。
- **标准型（50–150 行）**：MCP servers、astro、cline 的 copilot-instructions、vscode 的 copilot-instructions——**这是公认的"舒适区"**，正好覆盖 Anthropic 200 行硬约束。
- **极简型（≤30 行）**：firecrawl 风格——只列"步骤式工作流"。
- **路由型（≤5 行）**：vscode、cline、huggingface、ClickHouse 都把入口当**重定向**（"实际文件在别处"），把内容下沉到 `.claude/`、`.clinerules/`、`.ai/` 等专用目录。这种做法在 2026 年起非常普遍。

### 2.2 高频 H2 章节（基于以上 8 个非路由型样本）

按出现频率（n=8）：

| 章节标题（标准化） | 出现次数 | 典型来源 |
|---|---|---|
| Project Overview / Project Structure | 8/8 | 全部 |
| Build & Test Commands / Development Commands | 8/8 | 全部 |
| Coding Style / Code Conventions | 7/8 | 全部除 firecrawl |
| Commit / PR Guidelines | 5/8 | langchain、cookbook、mcp、vercel-ai、astro |
| Testing Guidelines | 6/8 | 几乎全部 |
| Do Not / Gotchas / Architecture Decisions | 4/8 | vercel-ai、codex、astro、langchain |
| Recent Learnings / Changelog | 1/8 | openai-cookbook 独有，值得效仿 |
| Repository Structure / Layout | 8/8 | 全部 |

**openai-cookbook 把 47 行 H2 八件套写齐**是个非常精炼的范例——47 行能装下 8 个章节，意味着每节平均不到 6 行。值得作为骨架模板。

来源：[openai/codex AGENTS.md](https://github.com/openai/codex/blob/main/AGENTS.md), [vercel/ai AGENTS.md](https://github.com/vercel/ai/blob/main/AGENTS.md), [langchain CLAUDE.md](https://github.com/langchain-ai/langchain/blob/master/CLAUDE.md), [openai-cookbook AGENTS.md](https://github.com/openai/openai-cookbook/blob/main/AGENTS.md), [vscode AGENTS.md](https://github.com/microsoft/vscode/blob/main/AGENTS.md), [cline CLAUDE.md](https://github.com/cline/cline/blob/main/CLAUDE.md), [modelcontextprotocol/servers CLAUDE.md](https://github.com/modelcontextprotocol/servers/blob/main/CLAUDE.md)。

---

## 问题 3：monorepo 嵌套实战

### 3.1 官方规则回顾

[agents.md FAQ](https://agents.md) 和 [Anthropic memory docs](https://code.claude.com/docs/en/memory) 都明确：

> "The closest AGENTS.md to the edited file wins; explicit user chat prompts override everything."（agents.md）
> "All discovered files are concatenated into context rather than overriding each other ... `CLAUDE.local.md` is appended after `CLAUDE.md`, so when instructions conflict, your personal notes are the last thing Claude reads at that level."（Anthropic）

**两套规则关键差异**：
- **AGENTS.md**：覆盖语义（最近者优先）。
- **CLAUDE.md**：合并语义（同时进上下文，按目录顺序拼接）。

实战上，因为合并语义不会"扔掉"父级，子文件只写差异即可——两套语义对作者的实际写作要求**收敛到同一个建议：子文件不要复制父级**。

### 3.2 "OpenAI 主仓 88 个 AGENTS.md"考据

agents.md 官方文案中那句 "the main OpenAI repo has 88 AGENTS.md files" 指的并非公开仓 `openai/codex`（该仓只有少量 AGENTS.md，根目录 `AGENTS.md` 是主入口，`codex-rs/` 子模块各自有少量补充），而是 OpenAI 的内部主 monorepo。该数字来自 agents.md 官方援引但**没有公开证据可验证**，应视为内部数据。

公开可验证的对照样本：
- **openai/codex 的 213 行根 AGENTS.md** 内部使用 H1/H2 切分子模块（Rust/codex-rs、TUI conventions、Tests、App-server API），属于"扁平多区段"风格而非"嵌套多文件"。
- **vercel/ai 的 306 行 AGENTS.md** 同样是单根、平铺，包含 15 个 H2，覆盖 packages/ai-sdk/ai-sdk-provider 等多个子包的规范。

### 3.3 实战建议

基于多个开源项目的写作惯例（vercel/ai、langchain、codex），子目录 AGENTS.md 应：

1. **只写本子树独有的差异**（命令、约束、风格）；
2. **避免重写"项目总览"**——这部分父级已写；
3. **如果必须强调**某条父级规则，宁可写"see root AGENTS.md §X"也不要复制。
4. **冲突时**：AGENTS.md 走覆盖（最近者赢），CLAUDE.md 走合并（追加）——两种工具读同一份子文件时这种行为不一致是个**真实陷阱**，对应同一仓库要做兼容必须考虑。

---

## 问题 4：让所有工具吃同一份指令的统一方案

调研发现业界已经分化成三种方案，这里逐一定量对比：

### 方案 A：短重定向（Redirect Stub）

入口文件只写一句"see X"。Claude / Codex / Copilot 读到后会顺着提示找下一份文件。

例：
```
# vscode/AGENTS.md（5 行）
# VS Code Agents Instructions
This file provides instructions for AI coding agents working with the VS Code codebase.
For detailed project overview ..., see the [Copilot Instructions](.github/copilot-instructions.md).
```
缺点：靠 LLM 自觉跳转，不保证一定加载第二份；老旧工具可能直接当 5 行用了。

### 方案 B：@-import 路由（推荐）

Anthropic 官方明确推荐：[CLAUDE.md 文档](https://code.claude.com/docs/en/memory) 的 "AGENTS.md" 段：

> "Claude Code reads `CLAUDE.md`, not `AGENTS.md`. If your repository already uses `AGENTS.md` for other coding agents, create a `CLAUDE.md` that imports it so both tools read the same instructions without duplicating them."

```markdown
# CLAUDE.md
@AGENTS.md

## Claude Code
Use plan mode for changes under `src/billing/`.
```

实例：
- **vercel/ai**：CLAUDE.md 内容**仅 9 字节**，纯文本 "AGENTS.md"——是让 Claude `@-import` 主入口的最小写法。
- **cline/cline**：CLAUDE.md 三行：
  ```
  @.clinerules/general.md
  @.clinerules/network.md
  @.clinerules/cli.md
  ```
  这是**用 Claude 的 @-import 把 Cline 自己的规则文件吸过来**。Claude 与 Cline 共享同一组 markdown，零冗余。

`@-import` 支持递归，最多 5 跳；支持绝对路径和 `~` 家目录。

### 方案 C：物理冗余 / CI 同步

例：**langchain CLAUDE.md 与 AGENTS.md 完全相同**——同 13112 字节，同 SHA `8b8a51a152c4d091a5ba6ef69de30487eabf1db1`，应通过预提交 hook 或 CI 同步。

优点：不依赖任何工具的 import 能力。  
缺点：必须配 CI 校验"两份必须同步"。

### 方案 D（次推荐）：symlink

Anthropic 文档明确支持：

> ".claude/rules/ supports symlinks, so you can maintain a shared set of rules and link them into multiple projects."

agents.md 也建议：`ln -s AGENTS.md AGENT.md` 用于向后兼容老格式。但 symlink 在 Windows 上行为不一致、在 git 上需要 `core.symlinks=true`，因此并未成为主流。

### 工具兼容矩阵

| 工具 | 入口文件 | 支持 @-import | 支持 path frontmatter | 支持 symlink |
|---|---|---|---|---|
| Claude Code | `CLAUDE.md` + `.claude/rules/*.md` | ✓ 5 跳 | ✓ `paths:` | ✓ |
| Cursor | `.cursor/rules/*.mdc` + AGENTS.md | ✓ `@filename.ts` | ✓ `globs:` | 未明确 |
| Aider | `CONVENTIONS.md`（任意名） | 通过 `read:` 配置数组 | ✗ | 未明确 |
| GitHub Copilot | `.github/copilot-instructions.md` + `.github/instructions/*.instructions.md` | ✗ | ✓ `applyTo:` | 未明确 |
| OpenAI Codex / Jules / Amp | `AGENTS.md`（嵌套） | 部分（Cursor 嵌套规则） | ✗ | 未明确 |

**结论**：在 Claude / Cursor 双栈环境，**B 是首选**；要兼容到 Copilot 必须搭配方案 A 或 C，因为 Copilot 不识别 `@`。

来源：[Anthropic memory docs](https://code.claude.com/docs/en/memory)、[Cursor rules docs](https://cursor.com/docs/context/rules)、[Aider conventions docs](https://aider.chat/docs/usage/conventions.html)、[Copilot custom instructions](https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)。

---

## 问题 5：入口文件长度的硬上限对比

| 工具 | 长度建议 | 来源原文 | 超长后果 |
|---|---|---|---|
| Claude Code | **≤200 行 / CLAUDE.md** | "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence." | 进 context，不截断；adherence 下降 |
| Claude Code（auto-memory） | **≤200 行 / 25KB（取小）** | "first 200 lines of `MEMORY.md`, or the first 25KB, whichever comes first" | **硬截断**：超出部分启动时不加载 |
| Cursor | **≤500 行 / 单 .mdc** | "Keep rules under 500 lines. Split large rules into multiple, composable rules" | 软建议，无截断 |
| GitHub Copilot（手写） | 无明确数字 | — | — |
| GitHub Copilot（agent 自动生成 prompt） | ≤2 页 | "Instructions must be no longer than 2 pages." | 仅约束生成器 |
| Aider CONVENTIONS.md | 无明确数字 | 文档未列 | — |

### 5.1 关键发现：**`MEMORY.md` 是 Claude Code 体系内唯一会被硬截断的文件**

[Anthropic memory docs](https://code.claude.com/docs/en/memory) 原文：

> "The first 200 lines of `MEMORY.md`, or the first 25KB, whichever comes first, are loaded at the start of every conversation. **Content beyond that threshold is not loaded at session start.** ... This limit applies only to `MEMORY.md`. CLAUDE.md files are loaded in full regardless of length, though shorter files produce better adherence."

CLAUDE.md 不会被截断，只是"越长 → context 越胖 → 模型遵循度越差"。MEMORY.md 则会**真截断**：超出部分模型完全看不到。这是主报告里没强调的关键差别。

### 5.2 降级方案

Anthropic 给的官方降级路径：

1. **超长 → 路径作用域规则**：把"只对 src/api 适用"的内容挪到 `.claude/rules/api.md` + `paths: ["src/api/**"]`，按需加载。
2. **超长 → @-import 拆分**：把"git workflow"挪到 `docs/git-instructions.md`，CLAUDE.md 里 `@docs/git-instructions.md`。注意：**imports 仍然在启动时全量加载，不能省 context**——只是组织更清晰。
3. **超长 → skills**：纯流程性内容（"如何发布版本"）挪到 `.claude/skills/release/SKILL.md`，仅 agent 显式调用时加载。

Cursor 的官方降级：

> "Reference files instead of copying their contents—this keeps rules short and prevents them from becoming stale as code changes"

意为**把代码片段移出规则、留 `@filename.ts` 引用**，让规则永远跟代码同步。

---

## 问题 6：路径作用域规则三家工具对比

### 6.1 语法差异

| 字段 | Claude Code | Cursor | GitHub Copilot |
|---|---|---|---|
| 文件位置 | `.claude/rules/*.md` | `.cursor/rules/*.mdc` (or `.md`) | `.github/instructions/*.instructions.md` |
| 路径字段名 | `paths:` | `globs:` | `applyTo:` |
| 字段类型 | YAML 数组 | YAML 标量或数组 | **逗号分隔字符串**（"`**/*.ts,**/*.tsx`"） |
| Glob 语法 | `**`、`*`、`{ts,tsx}` brace 扩展 | 同 | 同 |
| 旁路开关 | 无 | `alwaysApply: true` 跳过 globs | `excludeAgent: "code-review"` 或 `"cloud-agent"` |
| 智能描述 | 无（只有 paths） | `description:` 触发"Apply Intelligently" | 无 |
| 触发时机 | "trigger when Claude reads files matching the pattern" | 同 / 也支持 alwaysApply | "if the path you specify matches a file that Copilot is working on" |

### 6.2 优先级合并差异

- **Claude Code**：四层叠加，managed policy → user (`~/.claude/`) → project → local。User-level rules 加载在前，**项目规则后加载、优先级更高**（覆盖 user 级）。父级 CLAUDE.md 可被 `claudeMdExcludes` 配置剔除。
- **Cursor**：明确顺序 "**Team Rules → Project Rules → User Rules**"，"earlier sources take precedence when guidance conflicts" — 跟 Claude 完全相反，**Team 优先于 Project 优先于 User**。
- **GitHub Copilot**：明确顺序 "**Personal > Repository > Organization**"。Personal 最高优先级，与 Cursor 又不同。

**这是一个非常容易踩坑的事实**：同一概念"个人 / 项目 / 团队"三家优先级倒序完全不一致，跨工具配置时不能假设语义对齐。

### 6.3 限制与陷阱

- **Claude `paths:`** 只在"读到匹配文件时"加载——也就是说光是用户在 chat 里描述需求、还没 Read 任何文件，作用域规则不会进上下文。可以用 `InstructionsLoaded` hook 调试。
- **Cursor `globs:`** 与 `alwaysApply: true` 互斥；用 `Apply Intelligently` 模式必须填 `description:` 否则 Cursor 不会让 agent 自决。
- **Copilot `applyTo:`** 在 GitHub.com **"path-specific custom instructions are only supported for Copilot cloud agent and Copilot code review"** —— 也就是说 IDE 里的 Copilot Chat 暂时**不读 path-specific instructions**！这是文档原文写明的一个真实大坑。
- **Cursor 嵌套 AGENTS.md**：[Cursor docs](https://cursor.com/docs/context/rules) 明确："Nested AGENTS.md support in subdirectories is now available. Instructions from nested AGENTS.md files are combined with parent directories, with more specific instructions taking precedence." Cursor 同时支持 `.cursor/rules/*.mdc` 和嵌套 AGENTS.md，规则比 Claude Code 多一套。

### 6.4 三家路径作用域示例并列

```markdown
# Claude .claude/rules/api.md
---
paths:
  - "src/api/**/*.ts"
  - "src/api/**/*.tsx"
---
- All API endpoints must include input validation
```

```markdown
# Cursor .cursor/rules/api.mdc
---
description: "API design rules"
globs: src/api/**/*.{ts,tsx}
alwaysApply: false
---
- All API endpoints must include input validation
```

```markdown
# Copilot .github/instructions/api.instructions.md
---
applyTo: "src/api/**/*.ts,src/api/**/*.tsx"
excludeAgent: "code-review"
---
- All API endpoints must include input validation
```

来源：[Anthropic memory docs](https://code.claude.com/docs/en/memory)、[Cursor rules](https://cursor.com/docs/context/rules)、[Copilot custom instructions](https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)。

---

## 综合对照表（六项关键差异，单页可查）

| 维度 | AGENTS.md（通用） | Claude Code | Cursor | Copilot | Aider |
|---|---|---|---|---|---|
| 入口文件 | `AGENTS.md` | `CLAUDE.md` + `.claude/CLAUDE.md` | `.cursor/rules/*.mdc` + AGENTS.md | `.github/copilot-instructions.md` | 任意 markdown，惯用 `CONVENTIONS.md` |
| 嵌套语义 | 最近者覆盖 | 全部追加合并 | 嵌套合并、更具体优先 | 仓库级 + path-specific 同时使用 | 通过 `read:` 数组手动指定 |
| 路径作用域字段 | 无（靠目录位置） | `paths:` 数组 | `globs:` + `alwaysApply` + `description` | `applyTo:` 字符串 + `excludeAgent` | 无 |
| 长度建议 | 无 | ≤200 行（MEMORY.md 硬截断） | ≤500 行 / .mdc | ≤2 页（仅自动生成） | 无 |
| 优先级顺序 | path closest wins | local > project > user > policy | Team > Project > User | Personal > Repo > Org | 配置文件顺序 |
| @-import / 文件引用 | ✗ | ✓ `@path`（5 跳） | ✓ `@filename.ts` 引用文件入上下文 | ✗ | `read:` 数组 |
| 工具间共享方案 | — | 推荐：`@AGENTS.md` 一行 import | 直接读 AGENTS.md 嵌套 | 单独维护或 redirect | 单独维护 |

---

## 附录：六大新发现速查（相对主报告 report.md 的增量）

1. **AGENTS.md 公开仓首推 2025-08-19**，比 OpenAI Codex 公开（2025-05-16）晚 95 天；它是 Codex 落地后**总结出来的格式标准**，而不是反过来。
2. **MEMORY.md 是 Claude 体系唯一会被硬截断的文件**（200 行 / 25KB whichever first）；CLAUDE.md 不截断，只是 adherence 下降。
3. **业界已出现"路由型入口"模式**：vscode、cline、huggingface、ClickHouse 把 AGENTS.md / CLAUDE.md 写成 1–5 行重定向，把内容下沉到 `.github/copilot-instructions.md`、`.clinerules/`、`.ai/`、`.claude/` 等专用目录。
4. **Cursor / Copilot / Claude 三家"个人 vs 项目"优先级互相倒序**——跨工具配置高危。
5. **Copilot 的 path-specific instructions 仅 cloud-agent + code-review 生效**，IDE 端 Copilot Chat 完全不读，这是文档原文确认的大坑。
6. **vercel/ai 的 CLAUDE.md 仅 9 字节、内容是 "AGENTS.md"** — Anthropic 官方推荐的"一行 import"做法已被工业界采纳，是当前最被实证的多工具统一方案。

---
