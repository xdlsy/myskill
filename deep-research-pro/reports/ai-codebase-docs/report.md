# AI 辅助研发的代码仓结构化文档：体系、维护与防腐

*Generated: 2026-04-26 | Sources: 40+ | Confidence: High*

---

## Executive Summary

AI 辅助研发要求文档既是**给人看的**，更是**给 agent 看的"上下文契约"**。业界 2024–2026 年已形成稳定共识：

- **入口层**：以 `AGENTS.md` / `CLAUDE.md` 为统一入口（已被 60000+ 项目采用，OpenAI、Cursor、Aider、Copilot 等 30+ 工具兼容）。AGENTS.md 规范于 2025-08-19 由 OpenAI 首次公开提交，现由 Linux Foundation 旗下 Agentic AI Foundation 接管。
- **分层加载**：文档分**入口层 / 路径规则层 / 技能工作流层 / 个人本地层**四层加载；Claude Code 根级 CLAUDE.md 完整加载，MEMORY.md 硬截断 200 行/25KB。
- **存量代码**：用 **C4/arc42 架构图 + ADR + 代码地图 + 术语表 + Runbook** 描述；matklad 的 ARCHITECTURE.md 范式（Bird's-eye → Code map → Cross-cutting concerns）是事实标准。
- **增量开发**：用 **conventions + spec + plan + tasks** 驱动；GitHub Spec-Kit 提供 constitution/spec/plan/tasks 四件套，BMAD-METHOD 提供角色驱动 Agile 框架。
- **维护机制**：按 **docs-as-code** 范式（PR 门禁、CI 校验、CODEOWNERS、自动化 hook）；Vale + markdownlint-cli2 + lychee 是工具链最优组合。
- **防腐策略**：靠 **just-in-time 检索 + 定期剪枝 + 失效检测** 三件套；Anthropic 官方总结 5 大失败模式与社区补充 8 种反模式。
- **方法论选型**：轻量项目用 vanilla AGENTS.md 单文件起步；中大型项目可上 Spec-Kit 或 BMAD，但 brownfield 需慎用；模型能力提升会压缩重型 SDD 工具的边际价值。

---

## 主题 1：AI Agent 项目入口文件与分层规范

### 1.1 AGENTS.md 规范的演化历史

**起源时间线**（通过 GitHub Commits API 抓取 [agentsmd/agents.md](https://github.com/agentsmd/agents.md)）：

| 时间 (UTC) | 事件 |
|---|---|
| **2025-08-19 21:49:01** | "Initial commit" — 公开仓首次推送 |
| 2025-08-21 17:28:13 | 首次扩展兼容工具列表：Aider / Gemini / Kilo Code / OpenCode / Phoenix / Zed |
| 2025-08-28 22:01:01 | 最近一次实质提交（更新 OpenCode 大小写） |

OpenAI Codex 的研究预览发布于 **2025-05-16**，CLI 形态发布于 **2025 年 4 月**。AGENTS.md 先于规范站点出现约三个月，2025 年 8 月才被推到独立站点做"行业化"包装。参与方明确点名：**OpenAI Codex、Sourcegraph Amp、Google Jules、Cursor、Factory**。

agents.md FAQ 中给出迁移指引："`mv AGENT.md AGENTS.md && ln -s AGENTS.md AGENT.md`" — 揭示了 v1 之前业界存在 `AGENT.md`（单数）前身。当前兼容工具已扩张到 23+。

**治理结构**：从 OpenAI 个人仓库 → **Linux Foundation 旗下 Agentic AI Foundation 接管**。规范本身没有版本号、release 或 RFC，仅以 markdown spec 加 FAQ 形式存在。

### 1.2 真实大型项目的入口文件长什么样

采样 20+ 开源项目的结果：

| 项目 | 文件 | 行数 | 类型 |
|---|---|---|---|
| openai/codex | AGENTS.md | 213 | 重型 |
| vercel/ai | AGENTS.md | 306 | 重型 |
| langchain-ai/langchain | AGENTS.md = CLAUDE.md | 291 | 重型，双工具同步 |
| openai/openai-cookbook | AGENTS.md | 47 | 骨架型 |
| withastro/astro | AGENTS.md | 89 | 中型 |
| microsoft/vscode | AGENTS.md | 5 | 路由型（see copilot-instructions.md） |
| cline/cline | CLAUDE.md | 3 | 路由型（纯 @-import） |
| modelcontextprotocol/servers | CLAUDE.md | 103 | 标准型 |
| mendableai/firecrawl | CLAUDE.md | 18 | 极简型 |

**长度分布**：
- **重型（200+ 行）**：仅框架/SDK 类项目（codex / vercel-ai / langchain）
- **标准型（50–150 行）**：公认的"舒适区"，覆盖 Anthropic 200 行硬约束
- **极简型（≤30 行）**：只列步骤式工作流
- **路由型（≤5 行）**：把入口当重定向，内容下沉到 `.claude/`、`.clinerules/`、`.ai/` 等目录

**高频 H2 七件套**（基于 8 个非路由型样本）：Project Overview / Project Structure、Build & Test Commands、Coding Style、Testing Guidelines、Commit & PR Guidelines、Do Not / Gotchas、Repository Structure。

### 1.3 monorepo 嵌套实战

官方规则：
- **AGENTS.md**：覆盖语义（"The closest AGENTS.md to the edited file wins"）
- **CLAUDE.md**：合并语义（"All discovered files are concatenated"）

实战上两套语义**收敛到同一个建议：子文件不要复制父级**，只写本子树独有内容。

**"OpenAI 主仓 88 个 AGENTS.md"考据**：agents.md 官方文案指的并非公开仓 `openai/codex`（该仓只有少量嵌套文件），而是 OpenAI 内部主 monorepo，没有公开证据可验证。

公开样本：
- openai/codex 的 213 行根 AGENTS.md 内部用 H1/H2 切分子模块（Rust/codex-rs、TUI conventions、Tests），属"扁平多区段"风格
- vercel/ai 的 306 行 AGENTS.md 同样是单根平铺，15 个 H2 覆盖多子包

### 1.4 让所有工具吃同一份指令的统一方案

业界已分化成三种方案：

| 方案 | 示例 | 优缺点 |
|---|---|---|
| **(A) 短重定向** | vscode AGENTS.md 写 "see .github/copilot-instructions.md" | 靠 LLM 自觉跳转，不保证加载第二份 |
| **(B) @-import 路由（推荐）** | vercel/ai 的 CLAUDE.md 仅 9 字节，内容是 "AGENTS.md"；cline 的 CLAUDE.md 三行 `@.clinerules/...` | Anthropic 官方推荐；Claude `@-import` 支持递归 5 跳；跨平台稳 |
| **(C) 物理冗余 / CI 同步** | langchain 的 CLAUDE.md 与 AGENTS.md 字节级一致（同 SHA） | 不依赖任何工具 import 能力；必须配 CI 同步校验 |

**工具兼容矩阵**：

| 工具 | 入口文件 | 支持 @-import | 支持 path frontmatter | 支持 symlink |
|---|---|---|---|---|
| Claude Code | `CLAUDE.md` + `.claude/rules/*.md` | ✓ 5 跳 | ✓ `paths:` | ✓ |
| Cursor | `.cursor/rules/*.mdc` + AGENTS.md | ✓ `@filename.ts` | ✓ `globs:` | 未明确 |
| Aider | `CONVENTIONS.md`（任意名） | 通过 `read:` 配置数组 | ✗ | 未明确 |
| GitHub Copilot | `.github/copilot-instructions.md` + `.github/instructions/*.instructions.md` | ✗ | ✓ `applyTo:` | 未明确 |
| OpenAI Codex / Jules / Amp | `AGENTS.md`（嵌套） | 部分 | ✗ | 未明确 |

**结论**：Claude / Cursor 双栈环境选 B；要兼容 Copilot 必须搭配 A 或 C。

### 1.5 入口文件长度的硬上限对比

| 工具 | 长度建议 | 超长后果 |
|---|---|---|
| Claude Code CLAUDE.md | **≤200 行** | 进 context，不截断；adherence 下降 |
| Claude Code MEMORY.md | **≤200 行 / 25KB（取小）** | **硬截断**：超出部分启动时不加载 |
| Cursor | **≤500 行 / 单 .mdc** | 软建议，无截断 |
| GitHub Copilot（agent 自动生成） | ≤2 页 | 仅约束生成器 |
| Aider | 无明确数字 | — |

**关键发现**：`MEMORY.md` 是 Claude Code 体系内唯一会被硬截断的文件；CLAUDE.md 不截断，只是"越长 → context 越胖 → 遵循度越差"。

### 1.6 路径作用域规则三家工具对比

| 字段 | Claude Code | Cursor | GitHub Copilot |
|---|---|---|---|
| 文件位置 | `.claude/rules/*.md` | `.cursor/rules/*.mdc` | `.github/instructions/*.instructions.md` |
| 路径字段名 | `paths:` | `globs:` | `applyTo:` |
| 字段类型 | YAML 数组 | YAML 标量或数组 | **逗号分隔字符串** |
| 旁路开关 | 无 | `alwaysApply: true` 跳过 globs | `excludeAgent: "code-review"` 或 `"cloud-agent"` |
| 智能描述 | 无 | `description:` 触发"Apply Intelligently" | 无 |
| 触发时机 | "读到匹配文件时"加载 | 同 / 也支持 alwaysApply | "if the path matches a file Copilot is working on" |

**优先级合并差异**（极易踩坑）：
- **Claude Code**：local > project > user > policy（项目规则后加载、优先级更高）
- **Cursor**：Team Rules → Project Rules → User Rules（earlier sources take precedence）
- **GitHub Copilot**：Personal > Repository > Organization

**限制与陷阱**：
- Claude `paths:` 只在"读到匹配文件时"加载；用户聊天还没 Read 文件时不会进上下文
- Cursor `globs:` 与 `alwaysApply: true` 互斥；`Apply Intelligently` 必须填 `description:`
- **Copilot `applyTo:` 在 GitHub.com 仅 cloud-agent + code-review 生效**，IDE 端 Copilot Chat 完全不读！

### 1.7 综合对照表（单页可查）

| 维度 | AGENTS.md（通用） | Claude Code | Cursor | Copilot | Aider |
|---|---|---|---|---|---|
| 入口文件 | `AGENTS.md` | `CLAUDE.md` + `.claude/CLAUDE.md` | `.cursor/rules/*.mdc` + AGENTS.md | `.github/copilot-instructions.md` | 任意 markdown，惯用 `CONVENTIONS.md` |
| 嵌套语义 | 最近者覆盖 | 全部追加合并 | 嵌套合并、更具体优先 | 仓库级 + path-specific 同时使用 | 通过 `read:` 数组手动指定 |
| 路径作用域字段 | 无 | `paths:` 数组 | `globs:` + `alwaysApply` + `description` | `applyTo:` 字符串 + `excludeAgent` | 无 |
| 长度建议 | 无 | ≤200 行（MEMORY.md 硬截断） | ≤500 行 / .mdc | ≤2 页（仅自动生成） | 无 |
| 优先级顺序 | path closest wins | local > project > user > policy | Team > Project > User | Personal > Repo > Org | 配置文件顺序 |
| @-import / 文件引用 | ✗ | ✓ `@path`（5 跳） | ✓ `@filename.ts` 引用文件入上下文 | ✗ | `read:` 数组 |
| 工具间共享方案 | — | 推荐：`@AGENTS.md` 一行 import | 直接读 AGENTS.md 嵌套 | 单独维护或 redirect | 单独维护 |

---

## 主题 2：用结构化文档描述存量代码

存量代码描述的核心矛盾是 **"高信息密度 vs. 低维护成本"**。matklad（rust-analyzer 作者）总结：

> "Patches take ~2× longer without project familiarity, but locating where to change code takes ~10×."
> —— [matklad, ARCHITECTURE.md (2021)](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html)

**"在哪里改" 比 "怎么改" 重要 5 倍**。存量代码文档的第一公民不是 UML 类图，而是 **代码地图（Code Map） + 架构不变量（Invariants）**。

### 2.1 架构图标准对比：C4 / arc42 / 4+1 / 自由 Mermaid

| 标准 | 抽象层级 | 产物形态 | 适合谁 | agent 可解析性 |
|---|---|---|---|---|
| **C4 model** | Context → Container → Component → Code 四级 | 4 张层级嵌套图 + dynamic/deployment | 中小型系统、微服务 | **高**（DSL/JSON 可程序化读取） |
| **arc42** | 12 章模板 | 完整"架构手册" | 大型企业、合规/审计 | 中（自由文） |
| **4+1 view** | 5 个视图（Logical / Process / Development / Physical / Scenarios） | 5 套 UML 图 | 重度 UML 团队 | 低（图为主） |
| **自由 Mermaid** | 无规范 | repo 里散落的 .md + mermaid 块 | 小项目、原型 | 中（Mermaid 文本） |

**推荐**：
- **首选 C4 + Structurizr DSL**：DSL 是文本，Mermaid/PlantUML 都能渲染，agent 可直接解析，已有 Structurizr MCP server
- **大型企业补 arc42 章节**：把 C4 图嵌入 arc42 模板第 5、6、7 章
- **不建议 4+1**：5 视图同步成本高，UML 图不利于 LLM 阅读
- **小项目用自由 Mermaid**：但要在 README 里指明"这就是唯一的架构图"

### 2.2 ADR 三大模板对比

| 模板 | 字段 | 典型长度 | 标志特征 | 推荐场景 |
|---|---|---|---|---|
| **Nygard** | Title · Status · Context · Decision · Consequences | 半页～1 页 | 散文风、5 个固定段 | 个人/小团队 |
| **MADR** | YAML frontmatter + Title · Context · Decision Drivers · Considered Options · Decision Outcome · Consequences · Confirmation · Pros/Cons | 1～2 页 | 显式选项对比、结构化 frontmatter | 中大团队、需要 traceability |
| **Y-statement** | 单段六部分：In the context of … facing … we decided for … and against … | 1 张幻灯片 | 一句话决定 | 高管决策、咨询/教学 |

**AI agent 主导维护 → 推荐 MADR + frontmatter**：YAML 字段可被 agent 程序化检索（如"列出所有 superseded 的 ADR"）。

**实战要点**：文件名编号化（`0001-…`）；Status 严格枚举（proposed / accepted / deprecated / superseded by 0042）；ADR 不可改、只能追加新 ADR 取代；每条 ADR ≤ 2 页。

### 2.3 代码地图（Code Map）实战

**matklad 的 ARCHITECTURE.md 范式**（被 rust-analyzer、ripgrep 等采用）三段式：

1. **Bird's-eye view** — 项目解决什么问题，一段话
2. **Code map** — 主要目录/模块，每段 2-5 句，回答"X 在哪里？"和"这个东西是干啥的？"
3. **Cross-cutting concerns** — 不属于任何模块的横切关注点（性能、错误处理、可观测性）

关键约束（matklad）：
> "Do name important files, modules, and types. **Do not directly link them (links go stale)**. Explicitly call-out architectural invariants. Point out boundaries between layers and systems."

**rust-analyzer 的 architecture.md** 是模范范本：约 18 个 crate 的两三句描述，每个都说明"是 API boundary 还是 internal"；Cross-Cutting Concerns 覆盖 Stability、Cancellation、Testing、Error Handling、Observability 等。

**自动生成工具**：

| 工具 | 语言/生态 | 输出 | 适用 |
|---|---|---|---|
| dependency-cruiser | JS/TS | dot / mermaid / json / html | 前端/Node |
| go-callvis | Go | call graph | Go |
| pydeps | Python | import graph | Python |
| Structurizr DSL | 多语言 | C4 多图 | 架构层 |

dependency-cruiser 还能"validate against your own rules"——例如"core 模块不能 import ui 模块"，违反时 CI 失败。这是 **agent 友好的活文档**。

### 2.4 领域术语表（Glossary）

组织方式：
- **小项目（单 bounded context）**：字母序
- **中大型 / 多子域**：先按子域分组、子域内字母序（`# Billing` / `# Inventory` / `# Auth`）

单条术语字段建议：
```markdown
### Order (订单)
- **English**: Order
- **中文**: 订单
- **Bounded Context**: Sales
- **Definition**: 客户提交并已经付款的购买请求；未付款时叫 Cart
- **Code mapping**: `app/models/order.rb`，状态机见 `OrderStateMachine`
- **Don't confuse with**: PurchaseOrder（采购方向），Invoice（账务方向）
- **Last reviewed**: 2026-03
```

**"Don't confuse with"** 是反漂移核心——每次新人/agent 误用，把它加进来。

防止术语漂移：Glossary 也是 docs-as-code，PR 修改要 review；CI 用 `grep` 或 Vale 禁用废弃术语；每季度 review。

### 2.5 Runbook / 操作手册

**Tom Limoncelli 的 7 段**（PagerDuty 引用前 Google SRE）：
1. Service Overview
2. Service Build Information
3. Instructions for Deploying
4. Instructions for Common Tasks
5. **Pager Playbook** — 每个 monitoring alert 的 step-by-step
6. Disaster Recovery Plans
7. Service Level Agreement

**可直接抄的骨架模板**：
```markdown
# Runbook: <Service Name>
## 1. Metadata
- **Service**: <name>
- **Owner team**: <slack-channel>
- **Severity**: SEV1 / SEV2 / SEV3
- **Last reviewed**: 2026-MM-DD
## 2. Symptoms
## 3. Quick mitigation (5 分钟内)
## 4. Diagnosis
## 5. Escalation
## 6. Post-incident
## 7. Related
```

### 2.6 让 agent / 新人 30 分钟动手的 Onboarding 文档

**优秀样本**：
- **OpenAI Codex AGENTS.md**（213 行）：有最近一次必跑命令、有"不要碰的文件"清单、有"目标行数上限"
- **Grafana developer-guide.md**（432 行）：troubleshooting 最长——新人/agent 最容易卡的地方
- **Kubernetes contributors/devel**：按 SIG 拆分，每个 SIG 给出自己的 code hierarchy + design conventions

**30 分钟动手的最小骨架**（前 200 行决定一切）：

```markdown
# <Project> — Onboarding (30 min to first commit)
## 1. What this project does (1 段，3 句以内)
## 2. Quickstart (照抄能跑)
## 3. Repo layout (matklad code map 风格)
## 4. How to make a change
## 5. Where to look first
## 6. Common tasks
## 7. Troubleshooting
## 8. Where to go next
```

### 2.7 全套 docs/ 目录建议

```
<repo>/
├── README.md                        # 5 分钟看懂干什么
├── ARCHITECTURE.md                  # matklad 三段式
├── AGENTS.md / CLAUDE.md            # agent 入口
├── CONTRIBUTING.md                  # PR 流程
├── docs/
│   ├── onboarding.md                # 30 分钟动手骨架
│   ├── glossary.md                  # 按子域分组
│   ├── architecture/
│   │   ├── workspace.dsl            # Structurizr / C4 DSL
│   │   └── context.svg              # 自动生成
│   ├── decisions/                   # MADR ADR
│   ├── runbooks/                    # 操作手册
│   └── howto/                       # 任务级 how-to
└── .dependency-cruiser.cjs          # 依赖规则 → CI 强制
```

---

## 主题 3：AI Agent 增量开发的 Spec / Plan / Tasks 文档体系

### 3.1 GitHub Spec-Kit 四件套：真实模板字段

来源：GitHub Spec-Kit raw templates（2026-04 抓取）。

**spec-template.md**：
- 无 YAML frontmatter，markdown header 元数据
- 章节：User Scenarios & Testing（mandatory）→ Requirements（mandatory，FR-001 起编）→ Success Criteria（mandatory）→ Assumptions
- 硬约束："Each user story/journey must be **INDEPENDENTLY TESTABLE**"

**plan-template.md**：
- Summary（一句话需求 + 一句话技术路线）
- Technical Context（9 个 advisory 字段，缺省都是 `NEEDS CLARIFICATION`）
- Constitution Check — *GATE: Must pass before Phase 0 research*
- Project Structure — 文档输出 + 源码三选一
- Complexity Tracking — 仅当违反 Constitution 才填表

**tasks-template.md**：
- 格式：`[ID] [P?] [Story] Description`
- 依赖原文："Setup → Foundational（blocks all stories）→ User Stories（depend only on Foundational, can parallel）"

### 3.2 BMAD-METHOD：PRD / Story 模板与 AC 格式

**Epic + Story（Gherkin 严格 AC）**：
```
## Epic {{N}}: {{epic_title_N}}
### Story {{N}}.{{M}}: {{story_title}}
As a {{user_type}}, I want {{capability}}, So that {{value_benefit}}.
**Acceptance Criteria:**
- Given {{precondition}}
- When {{action}}
- Then {{expected_outcome}}
```

**单 Story 实现模板**（核心创新：task→AC 反追踪）：
```
## Tasks / Subtasks
- [ ] Task 1 (AC: 1, 3)        # 任务 (AC: #) 标注覆盖哪条 AC
- [ ] Task 2 (AC: 2)
## Dev Notes
### References
- [Source: docs/architecture.md#auth-flow]   # 必须给出 path#anchor
```

**AC 数量经验**：每个 story 3–7 条；超 7 条说明 story 太大，拆分。

### 3.3 Plan-mode 决策树

Anthropic 原文："**If you could describe the diff in one sentence, skip the plan.**"

| 任务类型 | 一句话能描述 diff？ | 跨文件？ | 不熟悉？ | 决策 | 文档产物 |
|---|---|---|---|---|---|
| 改 typo / 注释 | ✅ | ❌ | ❌ | **跳过 plan** | 无 |
| 修小 bug（已定位） | ✅ | 1–2 文件 | ❌ | **轻 plan**：口头列 2–3 步 | inline TODO |
| 加新接口/端点 | ❌ | 3+ 文件 | ❌ | **Plan Mode + plan.md** | spec.md + plan.md |
| 跨模块重构 | ❌ | 5+ 文件 | ✅ | **完整三件套** | 全套 |
| 新功能（含数据模型） | ❌ | ✅ | ✅ | **完整三件套 + research** | 全套 |

口诀："**diff 一句话 → 直接做；多文件或不熟悉 → plan；新功能或重构 → 全套**"。

### 3.4 任务粒度与 `[P]` 并行规则

| 层级 | 大小 | AC/任务数 | 完成时长 | 谁产出 |
|---|---|---|---|---|
| **Epic** | 一个用户旅程 | 含 3–8 个 story | 1–4 周 | PM/Architect |
| **Story** | 独立可测可发的切片 | 3–7 条 AC | 0.5–3 天 | PM+Tech Lead |
| **Task** | 单文件改动 + 验证 | 单一动作 | 15 min – 2 小时 | Tech Lead / agent |

**`[P]` 允许条件**（必须全部满足）：不同文件、无依赖、同一 phase 内。

### 3.5 TDD × AI Agent 工作流

**顺序铁律：spec → test → code**

权威依据：
- Spec-Kit tasks-template.md："Write these tests FIRST, ensure they FAIL before implementation"
- Anthropic："Include tests, screenshots, or expected outputs so Claude can check itself. **This is the single highest-leverage thing you can do.**"

逻辑链：spec 给"做什么"，test 把"做什么"编码成可执行契约，AI agent 拿 test 当 reward signal。**没有 test 等于没有验证回路**。

**检查点**：
1. spec.md 完成后人类 review，**禁止 agent 一口气从 idea 到代码**
2. test 必须先 FAIL 再 PASS（防占位 / mock 自欺）
3. tasks.md 里 test 编号 < 实现编号

### 3.6 可直接抄的骨架

见主题 3 子报告 §6.1–6.3 的完整 spec.md / plan.md / tasks.md 模板。

---

## 主题 4：Docs-as-Code 范式下 AI 项目文档的维护机制与自动化工具链

### 4.1 TL;DR

| 维度 | 关键结论 | 工具 |
|---|---|---|
| 散文风格检查 | Vale，覆盖术语/拼写/句法/可读性 | **Vale** + Google/write-good/proselint 包 |
| Markdown 结构 lint | markdownlint-cli2，规则成熟 | **markdownlint-cli2** |
| 链接失效 | 大仓只用 lychee，速度+缓存压倒性 | **lychee** |
| PR 必带文档守卫 | dorny/paths-filter 双 filter + required check | **dorny/paths-filter@v4** |
| 文档审批权 | CODEOWNERS 给 docs/ 指定 tech writer team | **CODEOWNERS + branch protection** |
| Agent 端强制 | Claude Code hooks（PostToolUse/SessionStart） | **`.claude/settings.json` hooks** |
| API 文档自动化 | 接口签名/类型文档全部自动生成；只手写"为什么" | OpenAPI / TypeDoc / Sphinx autodoc |
| 可度量的 docs 覆盖率 | 业界无统一指标，可自建"src 行变 / docs 行变"比 + agent 引用率 | 自建 dashboard |

### 4.2 文档静态检查工具横向对比

| 工具 | 语言 | 主检查类型 | 自定义规则 | 适用场景 |
|---|---|---|---|---|
| **Vale** | Go | 拼写、大小写、术语替换、禁用词、可读性、句法序列 | YAML 规则文件，社区有 Google/Microsoft/RedHat 现成包 | **首选**，最全面 |
| **markdownlint-cli2** | Node.js | Markdown 结构（标题层级、列表样式、代码围栏语言、行长） | 自定义规则插件 | 与 Vale 互补，结构层 |
| **textlint** | Node.js | 100+ 插件（中日韩语义检查强） | 极度可插拔 | 多语言（中文/日文）强需求 |

**结论**：Vale + markdownlint-cli2 是 90% 项目最佳组合。write-good 与 proselint 不必单独跑——Vale 通过 `Packages = write-good, proselint` 一行接管。

**`.vale.ini` 实战配置**、**`.markdownlint.json` 实战配置**、**GitHub Actions: docs-lint.yml** 详见主题 4 子报告 §1.2–1.4。

### 4.3 链接失效检查：lychee 一锤定音

| 项 | lychee | markdown-link-check | awesome_bot |
|---|---|---|---|
| 实现 | Rust，单二进制 | Node.js | Ruby |
| 速度 | 异步并发，**大仓快 5-30×** | 串行 | 中 |
| 缓存 | `--cache --max-cache-age 1d` | 无 | 无 |
| GitHub Action | 官方 `lycheeverse/lychee-action` | 第三方 | 已停止维护 |

**双层策略**：
- **增量（PR 守门）**：仅 PR 改动文件，阻塞合并
- **全量（定期巡检）**：每日凌晨 cron，失败开 issue，不阻塞代码流

### 4.4 文档 PR 门禁实战

**CODEOWNERS**：区分大小写；`/docs/` 包含全部子目录；在 Branch Protection 启用 "Require review from Code Owners"。

**阻止"代码改了但 docs 没改"**：dorny/paths-filter 双 filter 检测 `src/**` 改而 `docs/**` 未改时失败；允许 `skip-docs` 或 `chore` label 跳过。

**进阶：要求 ADR 联动**：代码动核心目录（`src/auth/`、`src/db/`）必须新增或更新 ADR。

### 4.5 从代码生成文档：手写 vs 自动生成

| 内容 | 手写 / 自动 | 工具 | 给 agent 的价值 |
|---|---|---|---|
| 公共 API 签名 | **自动** | OpenAPI/Swagger、TypeDoc、godoc | 高（结构化、不会过期） |
| 接口字段语义 | **手写** docstring，工具抽出 | 同上 + 注释 | 高（"为什么这字段必需"） |
| 架构图 | **手写** | Mermaid、PlantUML、structurizr | 极高（agent 看流向） |
| 决策原因（why） | **手写** ADR | adr-tools、log4brains | 极高（避免 agent 推翻已决策） |
| 部署 runbook | **手写** | — | 高（异常路径必须人写） |

**核心原则**：what/where 自动生成，why/when 手写。

**引用关系四要素**（让 agent 顺藤摸瓜）：
1. 路径+行号（`src/auth/token.ts:42-89`）
2. 测试文件路径
3. ADR 链接
4. `Last verified` 时间戳 + git sha

### 4.6 Claude Code hooks 实战配置

Anthropic 有 25+ 事件，docs-as-code 场景最有用的 8 个 hook：

| 事件 | 是否值得配置 | 用途 |
|---|---|---|
| `SessionStart` | ✅ | 注入项目入口、最近 ADR |
| `UserPromptSubmit` | ✅ | 注入 staleness/约束 |
| `PreToolUse` | ✅ | 阻止危险/不合规操作（rm、create docs/notes.md） |
| `PostToolUse` | ✅ | 自动跑 vale/eslint，给反馈让 agent 自纠 |
| `Stop` | ✅ | 收尾时提醒"是否要更新文档" |
| `PreCompact` | ✅ | 关键决策落盘提醒 |

**关键 hook 脚本**：
- `block-docs-write.sh`：阻止 agent "好心"创建 docs/progress.md / docs/notes.md 等噪音文档
- `remind-docs.sh`：改了 `src/auth/`、`src/db/`、`src/api/` 后提醒检查架构文档 / ADR / OpenAPI
- `inject-stale-warning.sh`：AGENTS.md `last_verified` 过 30 天，开头警告 agent

### 4.7 文档覆盖率怎么度量

**业界现状：没有统一指标**。三个可落地的自建指标：

**指标 A：src 行变 / docs 行变 比**
```bash
RATIO=$(echo "scale=2; ${DOC_LINES:-0} / ${SRC_LINES:-1}" | bc)
```
健康值：**0.05 – 0.30**（每 100 行代码改 5-30 行文档）。

**指标 B：staleness 度量**
- 过期率：`last_verified < now - 90d` 的文档比例
- 漂移率：`verified_against` 的 git sha 之后该文件夹有 N 次 commit

**指标 C：agent 引用率**
在 hooks 里记录 agent Read 了哪些文档；0 引用文档要么是僵尸（删除），要么入口没正确链到（修链接）。

### 4.8 文档 review 文化：他山之石

**GitLab Handbook（最详细公开 SOP）**：
- 铁律 1：文档与代码同 MR 提交；功能 MR 不带文档不能合并
- 铁律 2：四角色协作（Developer 主笔 / PM 定义 requirements / Tech Writer non-blocking review / Maintainer 合并权）
- 铁律 3：Tech Writer 非阻塞——maintainer 可提前合并，必须创建 post-merge follow-up issue
- 铁律 4：AI 生成文档必须人工 review + 跑 Vale

**Stripe**：工程师写 first draft，专职 docs engineer 改写；API reference 100% 从 OpenAPI 自动生成。

**Vercel**：强调"快速删比写慢"——过期文档优先删除，不容忍"待修复"。

### 4.9 工具链组合推荐：三档配方

**配方 1：轻量（个人 / 小团队 / 原型）**
- `markdownlint-cli2` 本地跑
- `lychee` 周末手动跑全量
- pre-commit hook 防止提交 broken link

**配方 2：标准（5-30 人团队，主推）**
- GitHub Actions：`docs-lint.yml` + `links.yml` + `docs-required.yml`
- CODEOWNERS：tech writer team + architects
- `.vale.ini` 用 Google + write-good + proselint
- Claude Code hooks：SessionStart 注入 + PostToolUse 跑 vale + Stop 提醒
- 自建指标 A（src/docs 比）入库

**配方 3：重型（企业 / 多团队 / monorepo）**
- 在配方 2 基础上加：OpenAPI/TypeDoc 自动生成 API 区、ADR-required 守卫、指标 A+B+C 仪表盘、专职 Docs Engineer、textlint 中文规则双轨

---

## 主题 5：AI Agent 项目文档防腐化策略

### 5.1 Just-in-time retrieval：从原则到命令级落地

Anthropic 上下文工程文章原话：
> "Rather than preloading data, agents keep lightweight identifiers (file paths, stored queries, web links, etc.) and fetch data dynamically at runtime via tools."
> "Claude Code uses a hybrid: CLAUDE.md dropped in upfront + glob/grep primitives for navigating filesystem just-in-time."

**Claude Code 具体使用模式**：

| 模式 | 反模式（preload） | 推荐（JIT） |
|---|---|---|
| 找接口实现 | 把整个 `src/api/` 塞进 CLAUDE.md | `Grep(pattern="export.*Handler", path="src/api/")` 按需 |
| 大数据库分析 | `cat dump.sql` 进上下文 | 写 SQL 查询 → 落 CSV → `head/tail` 查看 |
| 多文件改造 | 一次 Read 30 个文件 | 派 subagent，回 1-2k 字摘要 |
| 文档参考 | 把 README/ADR 全 import 到 CLAUDE.md | 只在 CLAUDE.md 写 `See @docs/adr/` 路径 |
| 接口约定 | 把 200 行 API 规范写进 CLAUDE.md | 拆 `.claude/skills/api-conventions/SKILL.md`，按需加载 |

**命令最小集合**：`Grep` → 找符号；`Glob` → 找文件路径；`Read` → 路径确定后调用（尽量 offset/limit）；`Bash` → head/tail/wc/git log 取元信息。

**上下文窗口压力的根因**（Anthropic 官方）：
1. **n² attention**：n token 形成 n² 配对关系，注意力被稀释 → "context rot"
2. **训练分布**：长序列在训练数据里少，位置编码插值带来 degradation

### 5.2 Auto memory 机制详解（v2.1.59+）

**存储位置**（实测路径）：
```
~/.claude/projects/<project>/memory/
├── MEMORY.md          ← 索引；每会话首 200 行 / 25KB 自动加载
├── debugging.md       ← 主题文件，按需读
└── ...
```

**写入触发**：
- 显式：用户说 "remember that X" / "always use pnpm not npm" → 直接写 auto memory
- 隐式（agent 自决）：Build/test 命令、调试方法论、风格偏好、项目历史

**与 CLAUDE.md 的边界**：

|  | CLAUDE.md | Auto memory |
|---|---|---|
| 谁写 | 人 | Agent |
| 内容 | Instructions / rules | Learnings / patterns |
| 作用域 | project / user / org | per working tree（机器本地） |
| 加载量 | 完整加载 | MEMORY.md 首 200 行 / 25KB |
| 团队共享 | 是（git） | 否（机器本地，不上传） |

关键差异：CLAUDE.md 完整加载；MEMORY.md **截断加载**——超出部分要靠 agent 用 file tool 主动读。Auto memory 是 *per working tree*，同事不会读到你的。

### 5.3 失效信号的检测方法

**唯一原生 hook：`InstructionsLoaded`**
事件载荷含 `file_path`、`memory_type`（User|Project|Local|Managed）、`load_reason`（session_start|nested_traversal|path_glob_match|include|compact）。

**重要限制**：hook 不阻塞、不能改变加载内容；只用于审计。它告诉你"哪条规则进了上下文"，不告诉你"agent 是否照做"。

**最小可用的审计日志**：
```jsonc
{
  "hooks": {
    "InstructionsLoaded": [{
      "hooks": [{
        "type": "command",
        "command": "jq -c '{ts:now,file:.file_path,type:.memory_type,reason:.load_reason}' >> ~/.claude/instruction-audit.log"
      }]
    }]
  }
}
```

**规则失效的三个间接信号**：
| 信号 | 含义 |
|---|---|
| 用户在同一会话内**两次以上**纠正同一行为 | 规则要么没写，要么写得太弱 / 太长被忽略 |
| `/memory` 列出某 rule 文件，但近 2 周 audit log 里 0 次加载 | 路径作用域写错了 |
| compaction 之后 agent 又开始犯之前纠正过的错 | 规则只在 conversation 里出现过，没进 CLAUDE.md |

### 5.4 `/memory` 周审计 SOP

**每周 30 分钟 checklist**（15 项）：

1. CLAUDE.md 是否 > 200 行？→ 拆成 path-scoped rule 或 skill
2. 是否有相互矛盾的规则？→ 留更具体的，删另一个
3. 是否有"agent 不写也能做对"的规则？→ 删（"If Claude already does without it, delete"）
4. 是否有"应该是 hook 而不是 prompt"的规则？→ 转 hook
5. audit log 里 0 次命中的 rule 文件 → 改 glob 或删
6. MEMORY.md 是否超 200 行？→ split 到主题文件
7. auto memory 里是否有该升进 CLAUDE.md 的事实？→ 升
8. auto memory 里是否有过期的"调试历史"？→ 删
9. CLAUDE.md / rules 引用的文件路径是否还存在？→ 跑 `claude-rules-doctor` 或 grep
10. ADR / 长说明是否被抄进了 CLAUDE.md？→ 改成 `@docs/adr/...` 引用
11. "IMPORTANT/YOU MUST" 是否泛滥？→ 强调超过 5 条 = 没强调；保留最关键 2-3 条
12. 是否有 nested CLAUDE.md 在已废弃目录里？→ 直接删
13. 团队成员有没有人改了 CLAUDE.md 没说？→ git log + diff
14. CLAUDE.local.md 里有没有该上升团队级的事实？→ 升 CLAUDE.md
15. 是否还需要某 skill / rule 的存在？→ 不再需要的归档

**剪枝决策树**：
```
看一条规则 →
├─ agent 没它也做对  →  删
├─ agent 偶尔忘     →
│   ├─ 内容是事实  →  留 CLAUDE.md，加"YOU MUST"
│   └─ 内容是流程  →  下沉 skill，CLAUDE.md 留一句"对 X 用 /skill"
├─ agent 经常违反   →
│   ├─ 可机检       →  转 hook（PreToolUse / PostToolUse）
│   └─ 不可机检     →  改写得更具体（带例子、反例）
└─ 多个规则讲同一事 → 合并到最具体那一处
```

### 5.5 上下文窗口压力的实证数据

**官方硬约束**：
- CLAUDE.md：建议 < 200 行；超过会 "consume more context and reduce adherence"
- MEMORY.md：硬截断 200 行 / 25KB
- Skill description 总预算：context window 的 1%（fallback 8000 字符），单条 description+when_to_use 1536 字符封顶
- Skill 内容 compaction 预算：每条 skill 重新注入首 5000 token，全部 skills 共享 25000 token；溢出时**最旧的 skill 整条丢弃**

### 5.6 失败模式表（含早期信号 / 根因 / 对策）

**Anthropic 官方 5 模式**：

| 失败模式 | 早期信号 | 根因 | 对策 |
|---|---|---|---|
| **Kitchen sink session** | 用户切话题 ≥ 2 次仍同一会话 | 上下文混入无关信息 | 不同任务必 `/clear`；用 `/btw` 处理一次性问答 |
| **Correcting over and over** | 同一缺陷纠正 ≥ 2 次 | 失败尝试堆积 | 第二次纠错后立即 `/clear`，重写含"刚学到的事"的 prompt |
| **Over-specified CLAUDE.md** | 用户重复 CLAUDE.md 已写过的事 | 长 CLAUDE.md 重要规则被淹没 | 周审计删冗余；可机检的转 hook |
| **Trust-then-verify gap** | PR review 才发现边界没处理 | 没给 agent 验证手段 | 强制 tests/screenshots/lint；agent 自我验证 |
| **Infinite exploration** | agent 读上百文件 | 范围不明 + 主上下文承担探索成本 | 用 subagent 做调研；prompt 限定文件/步骤数 |

**社区补充 8 种反模式**：

| 失败模式 | 早期信号 | 对策 |
|---|---|---|
| **Silent dead rule** | rule 文件还在 git，但 audit log 永不命中 | `claude-rules-doctor`；CI 跑命中率检查 |
| **Compaction-induced amnesia** | compact 后又犯之前纠正过的错 | 核心规则上项目根 CLAUDE.md；用 `SessionStart(matcher:"compact")` 重注入 |
| **Memory leak（auto memory 膨胀）** | MEMORY.md 超 200 行 | 周审计 SOP 第 6/7/8 项 |
| **Conflicting CLAUDE.md（monorepo）** | 跨子目录行为不一致 | `claudeMdExcludes` 排除别人的；或合并到 path-scoped rule |
| **All-caps fatigue** | "IMPORTANT/YOU MUST" 满篇还是不听 | 每个 CLAUDE.md 至多 2-3 条 caps |
| **AGENTS.md / CLAUDE.md drift** | 两个文件说法不一致 | CLAUDE.md 第一行 `@AGENTS.md` 单一信源 |
| **Skill 触发不到** | `/skill-name` 工作，但 agent 自己从不调用 | description 里前置 "Use when ..." 触发短语 |
| **Skill 内容失活** | 调用过的 skill 在长会话里似乎"被忘" | compaction 后关键 skill 主动 `/skill-name` 刷新 |

### 5.7 "进哪个层"的决策树

```
新知识 ────────────────────────────
│
├─ 是机器可强制的吗（lint / test / 路径限制）？
│   └─ 是 → HOOK（.claude/settings.json）
│
├─ 是组织级合规 / 安全？
│   └─ 是 → MANAGED CLAUDE.md
│
├─ 每会话都需要、且全队该知道？
│   ├─ 是事实（命令、约定、架构）→ ./CLAUDE.md（< 200 行）
│   └─ 是流程（多步、按需）  → .claude/skills/<name>/SKILL.md
│
├─ 仅在某些路径触发？
│   └─ .claude/rules/<name>.md + paths frontmatter
│
├─ 仅自己用，不入 git？
│   └─ ./CLAUDE.local.md（gitignore）或 ~/.claude/CLAUDE.md
│
├─ Agent 自己学到的？
│   └─ AUTO MEMORY（让 agent 写，人定期审计）
│
├─ 长参考材料？
│   └─ 留在 docs/，CLAUDE.md 只放路径引用 @docs/...
│
└─ 一次性问答 / 短期上下文？
    └─ 不要沉淀；必要时用 /btw 让结果不进历史
```

**反例（压根不该沉淀）**：单次 bug 调试历史、文件级描述（让 agent grep）、标准语言/框架知识、频繁变化的信息、长篇大论的"为什么"（除非进 ADR）。

### 5.8 文档防腐 SOP（人 + agent 各自职责）

**人的职责**：
| 频率 | 任务 |
|---|---|
| 每会话 | 同一缺陷纠正 ≥ 2 次 → `/clear` 并写更具体的 prompt |
| 每 PR | review 改了哪些代码/接口 → 同步 CLAUDE.md / rules / skill |
| 每周 | 跑 15 项 checklist；看 instruction-audit.log；剪 auto memory |
| 每月 | 走一遍决策树；把"该上升 team"的 auto memory 升进 CLAUDE.md |
| 每季 | 检查 hooks 是否还匹配实际工作流；CLAUDE.md size 趋势 |

**Agent 的职责**：
| 触发 | 行为 |
|---|---|
| 用户说 "remember X" | 写 auto memory；不要直接改 CLAUDE.md |
| 同一次会话内学到 build/test 命令 | 候选写入 auto memory |
| 用户纠正一次同一行为 | 候选写入 auto memory |
| compaction 后 | 自动重读项目根 CLAUDE.md（官方机制）；nested 不会自动重注入 |

### 5.9 五条最反直觉的发现

1. **Auto memory 是"agent 自写、人后审"**——很多人把 `/memory` 当成 CLAUDE.md 的别名，结果两个文件被同步污染。正确分工：用户记结论、规范、约定（CLAUDE.md），agent 记构建命令、调试洞见、风格偏好（auto memory）。
2. **InstructionsLoaded hook 只告诉你"加载"，不告诉你"遵守"**——当前唯一的原生 telemetry，只能审计死规则，不能审计被忽略的规则。
3. **"YOU MUST / IMPORTANT" 用多了等于没用**——best-practices 把"过载强调"列为 bloat 信号；社区被表扬的 CLAUDE.md 特点是"thorough but not shouting in all-caps"。
4. **Skills 在长会话里会被默默驱逐**——compaction 后所有 skill 共享 25000 token 预算，超出时**最旧的 skill 整条消失**。关键 skill 要主动 `/skill-name` 重新注入。
5. **Project-root CLAUDE.md 在 compact 时会自动重注入，但 nested CLAUDE.md 不会**——深目录里的规则只在 agent 下次读那个目录时才回来，意味着 compaction 之后行为可能"突然变"。关键规则要么放项目根，要么用 `SessionStart(matcher:"compact")` hook 强制重注入。

---

## 主题 6：AI 辅助研发的文档方法论选型与迁移

### 6.1 四套方法论对比表（10+ 维度）

| 维度 | vanilla AGENTS.md | Aider CONVENTIONS | GitHub Spec-Kit | BMAD-METHOD |
|---|---|---|---|---|
| **核心范式** | 单文件人类规约 | 单文件 read-only 风格指南 | Spec-Driven Development（SDD）流水线 | 角色驱动 Agile 框架 |
| **核心产物** | `AGENTS.md`（≤200 行） | `CONVENTIONS.md`（短小，bullet 风） | `constitution.md` + `spec.md` + `plan.md` + `tasks.md` | PRD + Architecture + Story 文档 + 12+ agent persona |
| **流程僵化度** | 极低 | 极低 | 高（9 个有序 slash 命令） | 极高（Agile 全生命周期 + 34+ workflow） |
| **上手成本** | < 30 分钟 | < 30 分钟 | 0.5–1 天 | 1–3 天 |
| **AI 工具兼容性** | 30+ 工具开箱 | 仅 Aider 原生；其他需 `--read` | 30+ agent 集成 | 多工具支持但安装时绑定具体 agent |
| **企业治理友好度** | 弱 | 弱 | 中–高 | 高 |
| **brownfield 适配** | 优 | 优 | 中（greenfield 强，brownfield 需纠偏） | 中（v6 引入 brownfield workflow，但 issue 报告"表面修复"多） |
| **退化路径** | N/A | N/A | 中（停用 slash 命令，constitution 留作 ADR） | 难（角色/workflow 与 prompt 深度耦合） |
| **Prompt cache 友好度** | 优 | 优 | 中 | 差 |
| **典型 star 数** | 60k+ 项目使用 | Aider 生态内置 | 90.8k★ / 7.8k fork | 45.7k★ / 5.4k fork |

> 横向定位：vanilla / CONVENTIONS 是**约定**层；Spec-Kit 是**流程**层；BMAD 是**组织 + 流程 + 角色**层。三层叠加重量呈阶梯。

### 6.2 真实采用案例

**Spec-Kit**：
- 自身 90.8k★，136 release，136 个第三方扩展
- 社区扩展 `spec-kit-verify` 补 spec→test 验证回路；`spec-kit-verify-tasks` 补 task 完成度
- 公开 brownfield 案例：Shoubhik Ghosh 的 legacy ASP.NET 现代化；IBM Bob × SpecKit 企业向评估

**BMAD**：
- 33 仓库 + 16 package 真实采用
- **最受关注下游**：`BMAD-AT-CLAUDE`（229★）——专门把 BMAD "ported to Claude Code"，说明 vanilla BMAD 在 Claude Code 上 not turn-key
- 模式观察：多数下游是 BMAD 的 fork，定制化（裁剪/适配特定 agent）是采用前置

**OpenSpec（值得关注）**：
ThoughtWorks Tech Radar Vol 34 "Assess" blip：
> "We particularly like OpenSpec's focus on spec deltas rather than defining a complete specification upfront."
> "continue to monitor and revisit native capabilities and re-evaluate the need for SDD tooling **as models grow more powerful**."

### 6.3 决策树：什么阶段用什么

```
项目规模 × 多人协作 × 治理强度
    │
    ├── 个人 / 1 人 / 原型探索
    │       └── vanilla AGENTS.md（≤200 行）
    │
    ├── 1–3 人 / 单仓库 / 6 个月内
    │       └── AGENTS.md + CONVENTIONS.md + 1–3 ADR
    │              ↑ 触发升级：CLAUDE.md 超 200 行 或 单仓库 ≥3 子域
    │
    ├── 4–10 人 / 单仓库或浅层多包 / 长期
    │       └── + .claude/rules/ 路径作用域 + .claude/skills/
    │              ↑ 触发升级：feature 跨 PR 数 ≥5
    │
    ├── 跨团队 / monorepo / greenfield 0→1 重要
    │       └── GitHub Spec-Kit（constitution + spec + plan + tasks）
    │              ↑ 警告：brownfield 慎用；先用 OpenSpec spec-delta 试水
    │
    └── 企业级 / 多 stakeholder / 强治理 / Agile 全流程
            └── BMAD-METHOD（PM + Architect + SM + Dev 角色驱动）
                   ↑ 警告：先评估"小 MVP 慢 10×"是否可接受
```

### 6.4 迁移路径：轻 → 重（5 个触发点）

| # | 触发信号 | 升级动作 |
|---|---|---|
| 1 | 入口文件 > 200 行且仍在加新规则 | 拆分到路径作用域：`.claude/rules/api.md`（paths: `src/api/**`） |
| 2 | Agent 频繁忽略某条规则 / 多个 CLAUDE.md 互相矛盾 | 引入 ADR + glossary，把"为什么"和"术语"从入口分离 |
| 3 | 同一 feature 跨 5+ PR / 多人改一处易冲突 | 上 spec/plan/tasks 三件套（先用 markdown 手写，不必立刻装 Spec-Kit） |
| 4 | 新成员上手 > 1 周 / agent 出"看起来对实则错"的代码频次高 | 装 Spec-Kit（或 OpenSpec，brownfield 优先），强制 constitution + clarify + analyze |
| 5 | 跨团队 / 跨产品 / 合规审计要求 | 上 BMAD；先跑 1 个 feature 当 pilot，验证团队接受度再扩散 |

> 反信号（不要升级）：项目即将 sunset / 团队 ≤2 人 / 业务节奏比"流程僵化度"敏感。

### 6.5 迁移路径：重 → 轻（精简实战）

**何时该精简**：
- Spec/PRD 数量 > 已实现 feature 数 ×2
- 团队抱怨"写 spec 比写代码慢"
- agent 频繁绕过流程直接动代码
- prompt cache miss 率高

**实战剪枝策略**：

| 类别 | 处理 |
|---|---|
| 历史 spec / 已实现的 feature spec | 移到 `specs/archive/<date>-<feature>/`，保留 `spec.md` 作为"为什么" |
| 过期 PRD | 折叠到 ADR 单文件，删除原 PRD |
| 从未触发的 agent persona | 删除（"删了 agent 会犯错吗"测试） |
| 跨 feature 重复的 architecture | 抽到 `docs/architecture/` 一份，feature 文档只引路径 |
| constitution.md 中"非约束"的内容 | 降级到 AGENTS.md 或 README |

**BMAD → vanilla 实战经验**（issue #2003 作者公开方案）：
1. 保留 BMAD 的 **planning 阶段**（PM/Architect 跑出 PRD + Architecture）
2. 实施阶段切到 vanilla：把 PRD/Architecture 的产物**抽要点**注入 `CLAUDE.md` + 一份 `tasks.md`
3. 抛弃 SM/Dev agent 的 prompt 编排，用裸 Claude Code + 短任务列表

实质是把 BMAD 当"重型规划工具"用，而不是"端到端框架"用。

### 6.6 多种方法论混搭

**Spec-Kit + .claude/skills（可行，已是官方建议）**：
Spec-Kit 维护者 mnriem 在 discussion #2268 明确：
> "Constitution 是直接进 spec-kit 命令流的；AGENTS.md 角色较小；SKILLS 在 spec-kit 命令视野之外，**仅 implement 命令例外**。"

最佳实践：
- Constitution = 不可变原则（governance）
- AGENTS.md = 跨工具入口（只读引用 constitution）
- `.claude/skills/` = 可执行 procedure（fix-issue / create-pr 等具体 how-to）
- 三者解耦：constitution 改动需要 PR review；AGENTS.md 改动随手即可；skills 由 agent 自更新

**反模式**：
- ❌ 同时跑 Spec-Kit 和 BMAD 完整流程（两套 PM/Architect/Dev 心智，agent 来回切换 context 即崩）
- ❌ vanilla AGENTS.md 之外又加 BMAD（小项目体感"装了个交响乐团演四重奏"）

### 6.7 AI 工具切换的兼容性

**多 agent 中立化三种实战手段**：

| 方案 | 实现 | 优势 | 缺点 |
|---|---|---|---|
| **符号链接** | `ln -s AGENTS.md AGENT.md` | agents.md 官方推荐 | Windows 行为不一致；某些 agent 不解析 symlink |
| **@-import（推荐）** | `CLAUDE.md` 单行 `@AGENTS.md` | 跨平台稳；Claude Code 原生支持递归 import（5 层） | Aider 不支持，需 `--read` |
| **中央 git submodule** | 把 `docs/` 与 `AGENTS.md` 抽成独立仓库 | 多产品共享一份治理 | submodule 心智成本；agent 拉不到时静默失败 |

**优先级**：单仓单产品 → @-import；多产品同治理 → submodule；遗留兼容 → symlink。

**中立化原则**：
- 入口文件名用 `AGENTS.md`（最广兼容），其他工具用 1 行引用
- 路径作用域规则用工具原生格式，但**内容只放工具特性相关**部分；通用规约一律回归 AGENTS.md

### 6.8 失败案例 / 反方观点

**Spec-Kit 反方**：
- 官方 README 自承："Claude Code might be over-eager and add components you did not ask for"；"over-engineering risk"
- 社区扩展 TinySpec 明确"skip the heavy multi-step SDD process"
- Discussion #2315（IDP 团队评估）列 7 个不够的地方：spec→contract test 缺、依赖排序模型缺、governance 不是 first-class 等
- ThoughtWorks Tech Radar："better suited to greenfield projects than brownfield ones"

**BMAD 反方**：
- Issue #2003（自称 BMAD fan）实测："a small MVP could take 10 to 15 times the time with BMAD compared to a normal traditional development process"。截至调研时维护者**无回应**
- Issue #1930：`bmad-bmm-correct-course` workflow 会**重写已完成的 story**
- ThoughtWorks Tech Radar："BMAD … enforce more rigid workflows"

**共同反方**（ThoughtWorks 在 OpenSpec blip 末尾）：
> "Continue to monitor and revisit native capabilities and re-evaluate the need for SDD tooling **as models grow more powerful**."

翻译：当模型推理能力进一步提升，重型 SDD 工具的边际价值会下降。**这是对所有重型方法论的长期看空信号**。

### 6.9 Key Takeaways

1. **vanilla / Aider / Spec-Kit / BMAD 是约定→流程→组织三阶梯**。不要跨阶梯升级。
2. **Spec-Kit 自身警示 over-engineering**；BMAD issue #2003 实测"小 MVP 慢 10–15×"。官方与活跃用户都承认的现实成本。
3. **brownfield 慎用 Spec-Kit / BMAD**——greenfield 优，brownfield 优先 OpenSpec（spec deltas）或自写 spec/plan/tasks。
4. **重型方法论的真实退化路径已经被走通**：BMAD 用作"规划工具"，实施阶段切回 vanilla CLAUDE.md。Spec-Kit 退化只需停用命令、归档 `.specify/`。
5. **多工具中立化首选 @-import + AGENTS.md**：单 source-of-truth，跨平台。
6. **混搭优先级**：constitution 不可变 governance + AGENTS.md 跨工具入口 + skills 可执行 procedure，三层解耦。
7. **长期看空重型 SDD**：模型推理能力提升时，spec-kit / BMAD 的边际价值会被压缩。把方法论选型当成"当下能力补丁"，不是"永久基础设施"。

---

## 综合建议与仓库骨架

### 信息密度排序（按"agent 30 分钟内最需要的"）

1. **Quickstart 命令**（必跑、能跑） → 占 30% 篇幅
2. **Repo layout + 不变量** → 25%
3. **How to make a change**（PR 流程） → 15%
4. **Where to look first**（任务 → 路径映射） → 15%
5. **Troubleshooting top 3** → 10%
6. **指针到深度文档** → 5%

避免：背景故事、产品愿景、架构演进史——这些放 ARCHITECTURE.md。

### 推荐仓库骨架

```
your-project/
├── AGENTS.md                  # 跨工具入口（≤200 行）
├── CLAUDE.md                  # @AGENTS.md + Claude 特有补充
├── .github/
│   ├── copilot-instructions.md
│   ├── instructions/
│   │   └── api.instructions.md   # applyTo: "src/api/**"
│   ├── CODEOWNERS
│   └── workflows/
│       ├── docs-lint.yml
│       ├── links.yml
│       └── docs-required.yml
├── .cursor/
│   └── rules/
│       └── frontend.mdc
├── .claude/
│   ├── rules/
│   │   ├── api.md            # paths: ["src/api/**/*.ts"]
│   │   ├── testing.md
│   │   └── security.md
│   ├── skills/
│   │   ├── fix-issue/SKILL.md
│   │   └── create-pr/SKILL.md
│   ├── hooks/
│   │   ├── block-docs-write.sh
│   │   ├── remind-docs.sh
│   │   └── inject-stale-warning.sh
│   └── settings.json
├── docs/
│   ├── onboarding.md         # 30 分钟动手骨架
│   ├── glossary.md           # 按子域分组
│   ├── architecture/
│   │   ├── workspace.dsl     # Structurizr / C4 DSL
│   │   └── context.svg       # 自动生成
│   ├── decisions/            # MADR ADR
│   │   ├── 0001-use-postgres.md
│   │   └── 0002-auth-strategy.md
│   ├── runbooks/             # 操作手册
│   └── howto/                # 任务级 how-to
├── ARCHITECTURE.md           # matklad 三段式
├── CONTRIBUTING.md           # PR 流程
├── README.md                 # 5 分钟看懂干什么
├── .vale.ini
├── .markdownlint.json
├── .lycheeignore
└── CLAUDE.local.md           # gitignored
```

---

## Sources

1. [agents.md — Open spec for coding agent docs](https://agents.md) — 60k+ 项目使用，跨工具事实标准
2. [GitHub agentsmd/agents.md commits API](https://api.github.com/repos/agentsmd/agents.md/commits) — AGENTS.md 规范演化时间线
3. [Anthropic — Claude Code Memory & CLAUDE.md](https://code.claude.com/docs/en/memory) — 200 行约束、四层加载、auto memory、@-import
4. [Anthropic — Best Practices for Claude Code](https://code.claude.com/docs/en/best-practices) — `/init`、hooks、context 管理、5 大失败模式
5. [Anthropic — Effective Context Engineering for AI Agents (2025-09-29)](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — just-in-time、progressive disclosure、context rot 根因
6. [Anthropic — Hooks reference](https://code.claude.com/docs/en/hooks) — InstructionsLoaded 事件载荷、SessionStart(compact) 重注入
7. [Anthropic — Skills](https://code.claude.com/docs/en/skills) — SKILL.md 结构、25000 token compaction 预算
8. [GitHub — awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) — agnix、claude-rules-doctor、pre-commit-hooks、Ralph 系列
9. [GitHub — Spec-Kit](https://github.com/github/spec-kit) — constitution/spec/plan/tasks 四件套、官方 over-engineering 警告
10. [GitHub — BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) — 角色驱动文档、issue #2003 #1930
11. [BMAD-AT-CLAUDE](https://github.com/24601/BMAD-AT-CLAUDE) — 229★ 的 Claude Code 移植
12. [adr.github.io — Architecture Decision Records](https://adr.github.io/) — Nygard / Y-statement / MADR 三种模板
13. [Aider — Coding Conventions Guide](https://aider.chat/docs/usage/conventions.html) — `CONVENTIONS.md` 单文件 + read-only + prompt caching
14. [Cursor Docs — Rules](https://cursor.com/docs/context/rules) — 4 种应用模式 + `.mdc` frontmatter + 嵌套 AGENTS.md
15. [GitHub Docs — Copilot Custom Instructions](https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot) — `.github/copilot-instructions.md` + `.instructions.md`
16. [Write The Docs — Docs as Code](https://www.writethedocs.org/guide/docs-as-code/) — PR 门禁、共享所有权、自动化测试
17. [matklad — ARCHITECTURE.md (2021)](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html) — 代码地图范式
18. [rust-analyzer architecture.md](https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/architecture.md) — 模范范本
19. [C4 model](https://c4model.com/) — 四级架构抽象
20. [arc42.org](https://arc42.org/overview) — 12 章模板
21. [Structurizr](https://structurizr.com/) — C4 DSL 工具，含 MCP server
22. [MADR 4.0](https://adr.github.io/madr/) — Markdown Architecture Decision Records
23. [Vale 官方文档](https://vale.sh/docs/install) — 安装、规则类型、StylesPath
24. [lycheeverse/lychee](https://github.com/lycheeverse/lychee) — 链接检查
25. [dorny/paths-filter](https://github.com/dorny/paths-filter) — PR 路径过滤守卫
26. [GitLab Documentation Workflow](https://docs.gitlab.com/development/documentation/workflow/) — 同 MR、四角色 SOP
27. [Google SRE Book](https://sre.google/sre-book/service-best-practices/) — Service Best Practices、On-Call
28. [PagerDuty — What is a Runbook](https://www.pagerduty.com/resources/learn/what-is-a-runbook/) — Runbook 定义与结构
29. [ThoughtWorks Technology Radar Vol 34](https://www.thoughtworks.com/radar/tools) — OpenSpec / Spec-Kit / BMAD 对比
30. [openai/codex AGENTS.md](https://github.com/openai/codex/blob/main/AGENTS.md) — 213 行实战范本
31. [vercel/ai AGENTS.md](https://github.com/vercel/ai/blob/main/AGENTS.md) — 306 行重型范本
32. [Microsoft/vscode AGENTS.md](https://github.com/microsoft/vscode/blob/main/AGENTS.md) — 5 行路由型范本
33. [cline/cline CLAUDE.md](https://github.com/cline/cline/blob/main/CLAUDE.md) — 3 行 @-import 范本
34. [Martin Fowler — Ubiquitous Language](https://martinfowler.com/bliki/UbiquitousLanguage.html) — DDD 术语表
35. [dependency-cruiser](https://github.com/sverweij/dependency-cruiser) — JS/TS 依赖图 + CI 规则验证

---

## Methodology

- **Sub-questions investigated**: 6 大主题下 30+ 子问题（入口演化 / 真实采样 / monorepo / 多工具统一 / 长度上限 / 路径作用域 / 架构图标准 / ADR 模板 / 代码地图 / 术语表 / Runbook / Onboarding / Spec-Kit 字段 / BMAD AC 格式 / plan-mode 决策树 / 任务粒度 / TDD×AI / docs lint 工具 / 链接检查 / PR 门禁 / hooks / 覆盖率度量 / JIT 检索 / auto memory / 失效检测 / 周审计 / 上下文压力 / 失败模式 / 方法论对比 / 采用案例 / 迁移路径 / 混搭 / 工具中立化）
- **Sources analyzed**: 35+ 个独立来源（Anthropic 官方 6 份、agents.md 官方、GitHub 仓库 8+、Cursor/Aider/Copilot 官方文档、Write The Docs/GitLab SRE/ThoughtWorks Radar 等行业基准、matklad/rust-analyzer 等开源范本、Vale/lychee/markdownlint 等工具文档）
- **Search strategy**: WebFetch 直抓已知权威源原文 + GitHub API 抓取 commits/raw files + DuckDuckGo/Bing 补充检索；每个来源 prompt 引导深读 + 引述原文；搜不到则跳过不编
- **Confidence**: High（核心结论在 ≥3 个独立来源交叉验证：入口标准 = agents.md + Anthropic + Copilot；防腐策略 = Anthropic 上下文工程 + Write The Docs + Cursor；分层结构 = Anthropic + Cursor + Copilot；方法论成本 = 官方自承 + 用户 issue + ThoughtWorks 行业评估）
- **Caveats**: 
  - "200 行 adherence 下降"是文档定性表述，没有公开 benchmark 数字；建议团队用 InstructionsLoaded hook 自采
  - WebSearch 部分时段被 API 拒绝，Reddit / HN 一手贴未直接抓取；社区证据通过 awesome-claude-code 二手汇总间接获得
  - GitHub code search 受登录墙限制，部分采用者数量用 dependents 与扩展数量做替代信号
  - BMAD/Spec-Kit 类重型框架在中小型项目可能过度设计；Cursor / Copilot 路径规则的精确语义会随版本演进
