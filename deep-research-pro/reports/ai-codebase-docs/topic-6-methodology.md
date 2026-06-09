# 主题 6 深挖：AI 辅助研发的文档方法论选型与迁移

> 父研究 `report.md` 第 6 节给出"按规模映射方案"的总表。本文把四套方法论的取舍、真实采用、迁移路径、混搭与失败案例讲清楚到可决策。

---

## 1. 四套方法论对比表（10+ 维度）

| 维度 | vanilla AGENTS.md | Aider CONVENTIONS | GitHub Spec-Kit | BMAD-METHOD |
|---|---|---|---|---|
| **核心范式** | 单文件人类规约 | 单文件 read-only 风格指南 | Spec-Driven Development（SDD）流水线 | 角色驱动 Agile 框架（PM/Architect/Dev/SM） |
| **核心产物** | `AGENTS.md`（≤200 行） | `CONVENTIONS.md`（短小，bullet 风） | `constitution.md` + `spec.md` + `plan.md` + `tasks.md` 四件套 | PRD + Architecture + Story 文档 + 12+ agent persona |
| **流程僵化度** | 极低（自由 markdown） | 极低（一份 bullet） | 高（9 个有序 slash 命令：constitution → specify → clarify → plan → tasks → analyze → checklist → implement → taskstoissues） | 极高（Agile 全生命周期 + 34+ workflow + 5 个扩展模块） |
| **上手成本** | < 30 分钟（写 markdown） | < 30 分钟 | 0.5–1 天（理解 SDD 心智 + `specify init` + 试跑一次完整循环） | 1–3 天（Node 20+ / Python 3.10+ / uv，多角色心智，完整 PRD/Architecture 流程） |
| **文档量级** | 1 文件 | 1 文件（+ 可选社区库） | 每 feature 6–7 文件 + 中央 constitution + skills/templates | 角色 × 产物矩阵：每个 feature 涉及 brainstorm/PRD/architecture/epic/story/QA 多份 |
| **AI 工具兼容性** | 30+ 工具开箱即读（Claude Code、Codex、Cursor、Copilot、Aider、Gemini CLI、Windsurf、Junie、Devin…） | 仅 Aider 原生；其他工具需手动 `--read` | 30+ agent 集成（init 时选 `--integration`：copilot / claude / gemini / codex / cursor / qwen / opencode / goose…） | 多工具支持但安装时绑定具体 agent；`BMAD-AT-CLAUDE` 这种"为 Claude Code 重新移植"的 fork 是常态 |
| **企业治理友好度** | 弱（无版本/审计/角色） | 弱 | 中–高（constitution 作为不可变 governance 锚；analyze 步骤跨产物一致性检查；taskstoissues 接 GitHub Issue） | 高（角色分离、Architecture / PRD 作为正式产物，强 Agile 节奏；适合多团队多 stakeholder） |
| **brownfield 适配** | 优（直接写约定即可） | 优 | 中（README 自承：greenfield 0→1 强；brownfield 需要 `clarify` + `analyze` 反复纠偏。ThoughtWorks Radar 评："better suited to greenfield projects than brownfield ones"） | 中（v6 引入 brownfield workflow，但 issue #2003 报告 brownfield 下 dev agent 频繁出"表面修复"——改 IPC 命令名而非真正实现 HTTP probe） |
| **Iteration / 演化** | 自然演化（开发者直接改） | 自然演化 | 弱：discussion 高赞贴 "Evolving specs"（118 评论）反映 spec 修改路径不清；多人改一份 spec 易冲突 | 弱：bmad-bmm-correct-course workflow 会改写已完成 story（issue #1930） |
| **退化路径** | N/A（已是底） | N/A | 中（停用 slash 命令即可，constitution.md 留作 ADR；archive `.specify/`） | 难（角色/workflow 与 prompt 深度耦合，大量产物文件需要剪枝） |
| **Prompt cache 友好度** | 优（稳定 markdown 全量加载） | 优（`/read` 显式 cache）  | 中（按需加载分散文件，多次轮换） | 差（多 persona 切换频繁，文件树大） |
| **典型 star 数 / 社区** | 60k+ 项目使用（agents.md 自报） | Aider 生态内置 | spec-kit 90.8k★ / 7.8k fork | BMAD 45.7k★ / 5.4k fork |
| **官方失败模式自承** | 无强制约束 → 容易膨胀 | 无 | README 直承"Claude Code might be over-eager"、"over-engineering risk"；社区扩展 TinySpec 专门"skip the heavy multi-step SDD process" | 高复杂度；issue #2003 用户实测"小 MVP 比传统流程慢 10–15×" |

> 横向定位：vanilla / CONVENTIONS 是**约定**层；Spec-Kit 是**流程**层；BMAD 是**组织 + 流程 + 角色**层。三层叠加重量呈阶梯。

---

## 2. 真实采用案例

### 2.1 Spec-Kit 采用者

GitHub `network/dependents` 在调研时显示 0（package 模式分发，依赖图捕获不到），但社区 ecosystem 真实活跃：

| 仓库/项目 | 简评 |
|---|---|
| `github/spec-kit` 自身 [URL](https://github.com/github/spec-kit) | 90.8k★，136 release，136 个第三方扩展登记在 README |
| `ismaelJimenez/spec-kit-verify` [URL](https://github.com/ismaelJimenez/spec-kit-verify) | 社区扩展。Discussion #2315 中被维护者 mnriem 引用，专门补 spec-kit 缺的 spec→test 验证回路 |
| `datastone-inc/spec-kit-verify-tasks` [URL](https://github.com/datastone-inc/spec-kit-verify-tasks) | 社区扩展，"continues to find/fix incomplete tasks"——开发者吐槽 task 默认完成度不够 |
| Shoubhik Ghosh, 《Spec-Driven Development with Spec-Kit: Transforming a Legacy ASP.NET》（Medium）| 公开 brownfield 案例：legacy ASP.NET 现代化 |
| IBM Bob × GitHub SpecKit（Renjith R Krishnan, Towards AI）| 企业向："from intuition-driven AI development to structured, enterprise-ready engineering" |

> 备注：GitHub code search `path:.specify/memory/constitution.md` 返回的真实仓库列表受 GitHub 登录墙限制无法直接抓取；grep.app 在调研时段 429。但 spec-kit 90.8k★ 与 136 第三方扩展是相对硬的"被使用"信号。

### 2.2 BMAD-METHOD 采用者

`network/dependents` 显示 33 仓库 + 16 package。可见的非 fork 真实采用：

| 仓库 | URL | 简评 |
|---|---|---|
| `24601/BMAD-AT-CLAUDE` | https://github.com/24601/BMAD-AT-CLAUDE | 229★。**最受关注的下游**——专门把 BMAD "ported to Claude Code"，新增 `bmad-claude-integration/` 目录。这本身说明 vanilla BMAD 在 Claude Code 上 not turn-key |
| `PabloLION/xterm-react` | https://github.com/PabloLION/xterm-react | 17★，React xterm 组件，正式工程项目 |
| `MauricioPerera/agent-tool-description-format` | https://github.com/MauricioPerera/agent-tool-description-format | 5★，agent 工具描述格式定义 |
| `nikhillinit/Updog_restore` | https://github.com/nikhillinit/Updog_restore | 真实业务恢复项目 |
| `twyr/twyr-backend-monorepo` | https://github.com/twyr/twyr-backend-monorepo | 1★，monorepo 后端工程 |
| `mateja176/simple-todo` | https://github.com/mateja176/simple-todo | 学习/教学项目 |
| Swan Software Solutions blog（Medium）| 《Taming the AI Chaos: Why I'm All-In on the BMAD Method》 | 第三方咨询公司公开背书 |

> 模式观察：（1）多数下游是 BMAD 的 fork，说明定制化（裁剪/适配特定 agent）是采用前置；（2）"为 Claude Code 重新移植"的 fork 拿到最高 star，反映出**框架 × agent harness 的耦合是 BMAD 的现实痛点**。

### 2.3 中间地带：OpenSpec（值得关注）

ThoughtWorks Tech Radar Vol 34 "Assess" blip 把 OpenSpec 作为 Spec-Kit / BMAD 的更轻量替代点名：

> "We particularly like OpenSpec's focus on spec deltas rather than defining a complete specification upfront."

> "Spec-Kit … better suited to greenfield projects than brownfield ones."

> "BMAD … enforce more rigid workflows."

> "OpenSpec is a developer-friendly framework worth assessing."

ThoughtWorks 同时给出底层判断："continue to monitor and revisit native capabilities and re-evaluate the need for SDD tooling **as models grow more powerful**." 暗示 SDD 工具的长期 ROI 取决于模型能力曲线。

---

## 3. 决策树：什么阶段用什么

```
项目规模 × 多人协作 × 治理强度
    │
    ├── 个人 / 1 人 / 原型探索
    │       └── vanilla AGENTS.md（≤200 行）
    │
    ├── 1–3 人 / 单仓库 / 6 个月内
    │       └── AGENTS.md + CONVENTIONS.md（Aider 风格）+ 1–3 ADR
    │              ↑ 触发升级当：CLAUDE.md 超 200 行 或 单仓库 ≥3 子域
    │
    ├── 4–10 人 / 单仓库或浅层多包 / 长期
    │       └── + .claude/rules/ 路径作用域 + .claude/skills/
    │              ↑ 触发升级当：feature 跨 PR 数 ≥5、agent 频繁产出"对一半"代码
    │
    ├── 跨团队 / monorepo / greenfield 0→1 重要
    │       └── GitHub Spec-Kit（constitution + spec + plan + tasks）
    │              ↑ 警告：brownfield 慎用；先用 OpenSpec spec-delta 试水
    │
    └── 企业级 / 多 stakeholder / 强治理 / Agile 全流程
            └── BMAD-METHOD（PM + Architect + SM + Dev 角色驱动）
                   ↑ 警告：先评估"小 MVP 慢 10×"是否可接受；
                   通常用 BMAD 做 brainstorm/PRD/architecture，
                   实施阶段切回 vanilla CLAUDE.md（issue #2003 用户实战路径）
```

---

## 4. 迁移路径：轻 → 重（5 个触发点）

| # | 触发信号 | 升级动作 |
|---|---|---|
| 1 | **入口文件 > 200 行**且仍在加新规则 | 拆分到路径作用域：`.claude/rules/api.md`（paths: `src/api/**`）/ `.cursor/*.mdc` / `.github/instructions/*.instructions.md` |
| 2 | **Agent 频繁忽略某条规则** / 多个 CLAUDE.md 互相矛盾 | 引入 ADR（仅追加）+ glossary，把"为什么"和"术语"从入口文件分离 |
| 3 | **同一 feature 跨 5+ PR** / 多人改一处易冲突 | 上 spec/plan/tasks 三件套（先用 markdown 手写，不必立刻装 Spec-Kit），让"先 spec 后实现"成为习惯 |
| 4 | **新成员上手 > 1 周** / agent 出"看起来对实则错"的代码频次高 | 装 GitHub Spec-Kit（或 OpenSpec，brownfield 优先），强制 constitution + clarify + analyze 三道闸 |
| 5 | **跨团队 / 跨产品 / 合规审计要求** | 上 BMAD（或自建 PM/Architect/Dev role 模板）。关键：先用 BMAD 跑 1 个 feature 当 pilot，验证团队接受度再扩散 |

> 反信号（**不要**升级）：项目即将 sunset / 团队 ≤2 人 / 业务节奏比"流程僵化度"敏感。

---

## 5. 迁移路径：重 → 轻（精简实战）

### 5.1 何时该精简

- Spec/PRD 数量 > 已实现 feature 数 ×2（说明很多 spec 没被吃透）
- 团队抱怨"写 spec 比写代码慢"
- agent 频繁绕过流程直接动代码（流程已被规避）
- prompt cache miss 率高（产物文件树过大，每次切换 persona 都重新加载）

### 5.2 实战剪枝策略（参考 issue #2003 + 父研究 §5.3）

| 类别 | 处理 |
|---|---|
| **历史 spec / 已实现的 feature spec** | 移到 `specs/archive/<date>-<feature>/`，**保留** `spec.md` 作为可搜索的"为什么"，删除 `plan.md`/`tasks.md` |
| **过期 PRD** | 折叠到 ADR 单文件（一个决策一条），删除原 PRD |
| **从未触发的 agent persona** | 删除（"删了 agent 会犯错吗" 测试） |
| **跨 feature 重复的 architecture 描述** | 抽到 `docs/architecture/` 一份，feature 文档只引路径 |
| **constitution.md 中"非约束"的内容** | 降级到 AGENTS.md 或 README |

### 5.3 BMAD → vanilla 实战经验

issue #2003 的作者（自称 BMAD fan）公开方案：

> "BMAD excels at brainstorming, research, deeper analysis, advanced planning, and multi-domain support … For execution, [I] recommend instead using a solid CLAUDE.md, prompt docs, and structured plans with claude-mem-style memory tools."

**翻译为可操作路径**：
1. 保留 BMAD 的 **planning 阶段**（PM/Architect 跑出 PRD + Architecture）
2. 实施阶段切到 vanilla：把 PRD/Architecture 的产物**抽要点**注入 `CLAUDE.md` + 一份 `tasks.md`
3. 抛弃 SM/Dev agent 的 prompt 编排，用裸 Claude Code + 短任务列表

实质是把 BMAD 当"重型规划工具"用，而不是"端到端框架"用。

### 5.4 Spec-Kit 退化

最低成本：停用 `/speckit.*` 命令，把 `.specify/memory/constitution.md` 重命名为 `docs/principles.md`（或合并入 AGENTS.md），归档 `.specify/`。constitution 内容本身就是好的 governance 文档，无需丢弃。

---

## 6. 多种方法论混搭

### 6.1 Spec-Kit + .claude/skills（可行，已是官方建议）

Spec-Kit 维护者 mnriem 在 discussion #2268 明确：

> "Constitution 是直接进 spec-kit 命令流的；AGENTS.md 角色较小，依赖具体 agent；SKILLS 在 spec-kit 命令视野之外，**仅 implement 命令例外**。"

**最佳实践**：
- Constitution = 不可变原则（governance）
- AGENTS.md = 跨工具入口（只读引用 constitution，不重复内容）
- `.claude/skills/` = 可执行 procedure（fix-issue / create-pr 等具体 how-to）
- 三者解耦：constitution 改动需要 PR review；AGENTS.md 改动随手即可；skills 由 agent 自更新

### 6.2 BMAD + Cursor rules（半可行）

BMAD 自带 agent persona，与 Cursor 的 `.cursor/rules/*.mdc` 概念有重叠：

- **不冲突的用法**：BMAD persona 走 prompt（动态），Cursor rules 走文件（静态作用域）。例如 BMAD 的 Architect persona 不重复 `.cursor/rules/security.mdc` 的内容，而是 import
- **冲突信号**：同一规则两份（`.bmad-core/agents/dev.md` 与 `.cursor/rules/coding.mdc` 都规定 lint），任何一处改动都要双向同步
- **解法**：单一 source of truth + 符号链接 / `@-import`（详见 §7）

### 6.3 反模式

- ❌ 同时跑 Spec-Kit 和 BMAD 完整流程（两套 PM/Architect/Dev 心智，agent 来回切换 context 即崩）
- ❌ vanilla AGENTS.md 之外又加 BMAD（小项目体感"装了个交响乐团演四重奏"）

---

## 7. AI 工具切换的兼容性（多 agent 中立化）

团队从 Cursor 换 Claude Code、或多人混用，文档保持中立的三种实战手段：

| 方案 | 实现 | 优势 | 缺点 |
|---|---|---|---|
| **符号链接** | `mv AGENT.md AGENTS.md && ln -s AGENTS.md AGENT.md` & 类似 `CLAUDE.md → AGENTS.md` | agents.md 官方推荐；旧工具仍可读 | git 跨平台（Windows）行为不一致；某些 agent 不解析 symlink |
| **@-import** | `CLAUDE.md` 单行 `@AGENTS.md`；Cursor `.cursor/rules/main.mdc` 用 frontmatter `globs:` 后正文 `@AGENTS.md` | 文件即配置，跨平台稳；Claude Code 原生支持递归 import（5 层） | 不同工具对 @-import 支持差异（Aider 不支持，需 `--read`） |
| **中央 git submodule** | 把 `docs/` 与 `AGENTS.md` 抽成独立仓库，多个产品仓 submodule 引入 | 多产品共享一份治理；版本可控 | submodule 心智成本；agent 拉不到 submodule 内容时静默失败 |

**优先级**：单仓单产品 → @-import；多产品同治理 → submodule；遗留兼容 → symlink。

**中立化原则（来自父研究 §3）**：
- 入口文件名用 `AGENTS.md`（最广兼容），其他工具用 1 行引用
- 路径作用域规则用工具原生格式（Cursor `.mdc` / Copilot `.instructions.md` / Claude `.claude/rules/`），但**内容只放工具特性相关**部分；通用规约一律回归 AGENTS.md

---

## 8. 失败案例 / 反方观点

### 8.1 Spec-Kit 反方

| 来源 | 观点 |
|---|---|
| **官方 README 自承** | "Claude Code might be over-eager and add components you did not ask for"；"over-engineering risk"；建议用户主动 prompt agent "cross-check for over-engineered pieces" |
| **TinySpec 扩展存在本身** | 社区扩展明确"skip the heavy multi-step SDD process"——隐性承认完整流程对小任务过重 |
| **Discussion #2315（IDP 团队评估）** | 列了 7 个 spec-kit 不够的地方：spec→contract test 缺、依赖排序模型缺、governance 不是 first-class、本地 dev 体验、AI agent 可靠性、progressive 渐进采用支持差 |
| **Discussion #1119（团队工作流）** | 标题即为 "Issues encountered when using spec-kit as the team's AI development workflow"——团队级采用产生真实摩擦，且 unanswered |
| **Discussion #1112** | VSCode + Copilot 用户发现 `tasks` 步骤的并行化设计实际不被 agent 利用，自己用 Sonnet 4.5 重写了顺序版 |
| **ThoughtWorks Tech Radar Vol 34** | 直接定调："better suited to greenfield projects than brownfield ones" |

### 8.2 BMAD 反方

| 来源 | 观点 |
|---|---|
| **Issue #2003（"Structural Gaps and Contradictions of the BMAD Method V.6 Stable"）** | 作者（自称 BMAD fan）实测："a small MVP could take 10 to 15 times the time with BMAD compared to a normal traditional development process"。指出"两条前提（非技术用户用得起 / 技术用户审计得过来 AI 产出）不能共存"。截至调研时维护者**无回应**（无 label / 无 milestone / 无 comment） |
| **Issue #1930** | `bmad-bmm-correct-course` workflow 会**重写已完成的 story**——流程对"已 done"状态没有保护 |
| **Issue #1958** | 在非 JS 项目里 agent 会跳过适用的 workflow 段落 |
| **Issue #2034** | story 与 epic 在 correct-course 后不自动同步 |
| **BMAD-AT-CLAUDE 高 star（229★）的存在** | 隐性反方信号：vanilla BMAD 在 Claude Code 上需要专门移植 |
| **ThoughtWorks Tech Radar** | "BMAD … enforce more rigid workflows"——把僵化作为劣势点名 |

### 8.3 共同反方观点

ThoughtWorks 在 OpenSpec blip 末尾的总判断值得记录：

> "Continue to monitor and revisit native capabilities and re-evaluate the need for SDD tooling **as models grow more powerful**."

翻译：当模型推理能力进一步提升，重型 SDD 工具的边际价值会下降。**这是对所有重型方法论的长期看空信号**。

---

## 9. Key Takeaways

1. **vanilla / Aider / Spec-Kit / BMAD 是约定→流程→组织三阶梯**。不要跨阶梯升级（小项目直接上 BMAD = 交响乐团演四重奏）。
2. **Spec-Kit 自身警示 over-engineering**；BMAD issue #2003 实测"小 MVP 慢 10–15×"。这不是黑材料，是**官方与活跃用户都承认的现实成本**。
3. **brownfield 慎用 Spec-Kit / BMAD**——ThoughtWorks Radar 与社区 issue 一致指向：greenfield 优。brownfield 优先 OpenSpec（spec deltas）或自写 spec/plan/tasks。
4. **重型方法论的真实退化路径已经被走通**：BMAD 用作"规划工具"（保留 PRD/Architecture），实施阶段切回 vanilla CLAUDE.md。Spec-Kit 退化只需停用命令、归档 `.specify/`。
5. **多工具中立化首选 @-import + AGENTS.md**：单 source-of-truth，跨平台；symlink 是历史兼容，不是首选。
6. **混搭优先级**：constitution 不可变 governance + AGENTS.md 跨工具入口 + skills 可执行 procedure，三层解耦（来自 spec-kit 维护者明确建议）。同时跑两套重型框架是反模式。
7. **长期看空重型 SDD**：模型推理能力提升时，spec-kit / BMAD 的边际价值会被压缩。把方法论选型当成"当下能力补丁"，不是"永久基础设施"。

---

## Sources

1. [GitHub Spec-Kit README](https://github.com/github/spec-kit) — 官方工作流、命令、扩展生态、自承的 over-engineering 警告
2. [GitHub Spec-Kit Discussion #2268](https://github.com/github/spec-kit/discussions/2268) — Constitution / AGENTS.md / SKILLS 三者关系，维护者 mnriem 答复
3. [GitHub Spec-Kit Discussion #2315](https://github.com/github/spec-kit/discussions/2315) — IDP 团队评估反馈，spec→test 验证缺失
4. [GitHub Spec-Kit Discussion #1112](https://github.com/github/spec-kit/discussions/1112) — VSCode + Copilot 下 tasks 并行化无效
5. [GitHub Spec-Kit Discussion overview](https://github.com/github/spec-kit/discussions) — "Evolving specs"（118 评论）等高赞痛点
6. [BMAD-METHOD README](https://github.com/bmad-code-org/BMAD-METHOD) — 角色、workflow、扩展模块
7. [BMAD-METHOD Issue #2003](https://github.com/bmad-code-org/BMAD-METHOD/issues/2003) — "Structural Gaps and Contradictions" 用户实测 10–15× 慢
8. [BMAD-METHOD Issues 列表（complaints）](https://github.com/bmad-code-org/BMAD-METHOD/issues?q=is%3Aissue+overhead+OR+complex) — #1930 / #1958 / #2034 等
9. [BMAD-METHOD Dependents](https://github.com/bmad-code-org/BMAD-METHOD/network/dependents) — 33 仓库 + 16 package 真实采用
10. [BMAD-AT-CLAUDE](https://github.com/24601/BMAD-AT-CLAUDE) — 229★ 的 Claude Code 移植，反映耦合问题
11. [agents.md spec](https://agents.md) — 60k+ 项目共识、迁移建议（symlink）
12. [Aider CONVENTIONS docs](https://aider.chat/docs/usage/conventions.html) — `/read` + prompt cache + 社区 conventions repo
13. [ThoughtWorks Technology Radar Vol 34（OpenSpec blip）](https://www.thoughtworks.com/radar/tools) — Spec-Kit/BMAD 对比与"等模型变强再评估 SDD 工具"判断
14. Medium 公开案例：Shoubhik Ghosh（ASP.NET 现代化）、Renjith R Krishnan（IBM Bob × SpecKit）、Swan Software Solutions（BMAD 全 in）、Trung Hiếu Trần（BMAD v6 token 节省 90%）
15. [Anthropic — Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — just-in-time、避免预加载快照（与重型方法论的 prompt cache 冲突点）

---

## Methodology

- **Sub-questions investigated**: 7（横向对比 / 真实采用 / 升级路径 / 退化路径 / 混搭 / 工具切换 / 失败案例）
- **Sources analyzed**: 15 个独立来源（4 个一手仓库 README、4 个 GitHub Discussion/Issue、ThoughtWorks Radar、Medium 实战 8 篇、agents.md spec、Aider 文档、Anthropic 上下文工程）
- **Search strategy**: 直抓 GitHub 仓库 + Discussion/Issue 真实用户语言 → ThoughtWorks 行业判断 → Medium tag 页扫第三方实战
- **Caveats**:
  - GitHub code search 受登录墙限制，无法直抓 ".specify/memory/constitution.md" 全量列表；用 dependents 与社区扩展数量做替代信号
  - grep.app 调研时段返回 429，部分采用者列表不全
  - Reddit / HN 搜索接口在调研时段不可用，未纳入直接引用（按"搜不到则跳过，别编"原则不补）
  - 部分 Medium 文章 URL 失效（404），仅引用 tag 页可见的标题与作者
- **Confidence**: High（核心结论"重型方法论有真实成本 + brownfield 慎用 + 退化路径可走"在 ≥3 个独立来源交叉验证：官方自承 + 用户 issue + ThoughtWorks 行业评估）
