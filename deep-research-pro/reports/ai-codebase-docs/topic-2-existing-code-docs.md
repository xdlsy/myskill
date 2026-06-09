# 主题 2 深挖：用结构化文档描述存量代码

> 目标：让 AI agent（以及新人）能在 30 分钟内"看懂老仓库"。
> 范围：架构图标准、ADR 模板、代码地图、术语表、Runbook、快速 onboarding。
> 父报告：`/Users/lsy/clawd/research/ai-codebase-docs/report.md` 的"主题 2"。

---

## 总览

存量代码描述的核心矛盾是 **"高信息密度 vs. 低维护成本"**。文档写得越精细，代码漂移时越快失效；写得越抽象，agent 越不知道去哪里改。matklad（rust-analyzer 作者）把这个矛盾总结为：

> "Patches take ~2× longer without project familiarity, but locating where to change code takes ~10×."
> —— [matklad, ARCHITECTURE.md (2021)](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html)

也就是说，**"在哪里改" 比 "怎么改" 重要 5 倍**。所以存量代码文档的第一公民不是 UML 类图，而是 **代码地图（Code Map） + 架构不变量（Invariants）**。下面六个问题围绕这个原则展开。

---

## 1. 架构图标准对比：C4 / arc42 / 4+1 / 自由 Mermaid

### 1.1 四种标准简介

| 标准 | 抽象层级 | 产物形态 | 适合谁 |
|---|---|---|---|
| **C4 model** ([c4model.com](https://c4model.com/)) | Context → Container → Component → Code 四级缩放 | 4 张层级嵌套图 + 可选 dynamic/deployment | 中小型系统、微服务、想给非工程师看的 |
| **arc42** ([arc42.org](https://arc42.org/overview)) | 12 章模板，从 goals 到 glossary 全覆盖 | 一份完整的"架构手册" | 大型企业系统、合规/审计需求强 |
| **4+1 view** ([Wikipedia](https://en.wikipedia.org/wiki/4%2B1_architectural_view_model)) | 5 个视图：Logical / Process / Development / Physical / Scenarios | 5 套 UML 图 | 重度 UML 团队、嵌入式/电信 |
| **自由 Mermaid** | 无规范 | repo 里散落的 .md + ```mermaid``` 块 | 小项目、原型、README 即文档 |

### 1.2 各自要素

**C4** 的核心抽象出自官网：

> "A set of hierarchical abstractions — software systems, containers, components, and code... Notation independent. Tooling independent."

C4 不强制工具，但官方推荐 [Structurizr](https://structurizr.com/) DSL，能从一份模型自动生成 Context/Container/Component 多图。Structurizr 官网明确指出 C4 + DSL 对 LLM 友好：

> "Structurizr's model-based consistency and enforcement of the C4 model rules... enables AI summaries, queries, and detecting architectural drift."

**arc42** 的 12 个章节是固定的（[arc42.org/overview](https://arc42.org/overview)）：

1. Introduction & Goals · 2. Constraints · 3. Context & Scope · 4. Solution Strategy
5. Building Block View · 6. Runtime View · 7. Deployment View · 8. Crosscutting Concepts
9. Architectural Decisions · 10. Quality Requirements · 11. Risks & Technical Debt · 12. Glossary

**4+1** 的 5 个视图（[Kruchten 1995](https://en.wikipedia.org/wiki/4%2B1_architectural_view_model)）：

| 视图 | 关注 | 受众 | 典型 UML |
|---|---|---|---|
| Logical | 功能 | 终端用户 | Class / State |
| Process | 并发/分布/性能 | 集成工程师 | Sequence / Communication |
| Development | 代码组织 | 开发 | Package / Component |
| Physical | 部署 | 运维 | Deployment |
| Scenarios (+1) | 关键用例串起其他 4 个 | 全员 | Use Case |

### 1.3 AI agent 时代的对比

| 维度 | C4 | arc42 | 4+1 | 自由 Mermaid |
|---|---|---|---|---|
| **学习成本** | 低（4 个抽象） | 中（12 章） | 高（UML） | 极低 |
| **维护成本** | 中（DSL 抗漂移） | 高（章多） | 高（多视图同步） | 低但易过期 |
| **agent 可解析性** | **高**（DSL/JSON 可程序化读取） | 中（自由文）| 低（图为主） | 中（Mermaid 文本） |
| **支持工具** | Structurizr / Mermaid C4 / PlantUML | 所有 Markdown | UML 工具链 | 任意 |
| **MCP/LLM 工具链** | 已有 [Structurizr MCP server](https://structurizr.com/) | 无原生 | 无 | 无 |
| **适用场景** | 微服务、SaaS、AI agent 友好 | 大型/合规重 | 电信/嵌入式遗留 | 早期或单 repo |

**推荐结论**：

- **首选 C4 + Structurizr DSL**：DSL 是文本，Mermaid/PlantUML 都能渲染，agent 可直接解析。Container 层往往就是 agent 最需要的"代码地图入口"。
- **大型企业系统补 arc42 章节**：把 C4 图嵌入 arc42 模板第 5、6、7 章，得到双赢——agent 看 C4 抽象，审计看 arc42 完整性。
- **不建议 4+1**：5 视图同步成本高，UML 图不利于 LLM 阅读。
- **小项目用自由 Mermaid 即可**：但要在 README 里指明"这就是唯一的架构图"，避免 agent 去找别的。

---

## 2. ADR 三大模板对比

### 2.1 字段对比表

| 模板 | 字段 | 典型长度 | 维护成本 | 标志特征 |
|---|---|---|---|---|
| **Nygard** ([原文](https://github.com/joelparkerhenderson/architecture-decision-record/blob/main/locales/en/templates/decision-record-template-by-michael-nygard/index.md)) | Title · Status · Context · Decision · Consequences | 半页～1 页 | 极低 | 散文风、5 个固定段 |
| **MADR** ([adr.github.io/madr](https://adr.github.io/madr/)) | YAML frontmatter (status/date/decision-makers/consulted/informed) + Title · Context and Problem · Decision Drivers · Considered Options · Decision Outcome · Consequences · Confirmation · Pros and Cons of Options · More Information | 1～2 页 | 中 | 显式选项对比、结构化 frontmatter |
| **Y-statement** ([Zimmermann 2018](https://medium.com/olzzio/y-statements-10eb07b5a177)) | 单段六部分：In the context of … facing … we decided for … and against … to achieve … accepting that … | 1 张幻灯片 | 极低 | 一句话决定 |

### 2.2 三种模板的细节

**Nygard 模板** 来自 Michael Nygard 2011 年博文，最早被 [adr-tools](https://github.com/npryce/adr-tools) 推广。模板提示词：

> "What is the issue that we're seeing that is motivating this decision? ... What is the change that we're proposing? ... What becomes easier or more difficult to do because of this change?"

**MADR 4.0** 在 Nygard 上扩展（[adr.github.io/madr](https://adr.github.io/madr/)）：

- 加 **Decision Drivers**（决策力学/驱动因素）
- 加 **Considered Options + Pros and Cons of the Options**（显式选项分析）
- frontmatter 引入 RACI 风格的 `decision-makers / consulted / informed`
- 加 **Confirmation** 字段（"how compliance is verified — code review / ArchUnit"）
- 文件命名固定 `NNNN-title-with-dashes.md`，存于 `docs/decisions/`

短版只保留 Title / Context / Considered Options / Decision Outcome 四段，约 10–20 行。

**Y-statement** 是 Olaf Zimmermann 提出的一句话格式：

> "In the context of the Web shop service, facing the need to keep user session data consistent across instances, we decided for the Database Session State pattern and against Client Session State, to achieve consistency and elasticity, accepting that a session DB must be designed and built."

设计目标是"一张幻灯片装得下"，可与 MADR 互补——把 Y-statement 放进 MADR 的 Decision Outcome 段。

### 2.3 选型建议

| 项目类型 | 推荐 | 理由 |
|---|---|---|
| 个人/小团队、决策不多 | **Nygard** | 学习成本最低；adr-tools 自动生成模板 |
| 中大团队、需要 traceability | **MADR** | 显式选项+RACI，agent 容易抽取"为什么选 A 不选 B" |
| 高管决策、咨询/教学 | **Y-statement** | 一句话沟通，可塞 PPT |
| 已用 Spec-Kit / BMAD | 把 MADR 嵌入 plan.md | 决策记录与计划同源 |
| AI agent 主导维护 | **MADR + frontmatter** | YAML 字段可被 agent 程序化检索（如"列出所有 superseded 的 ADR"）|

**实战要点**（综合多个项目的经验）：

- 文件名编号化（`0001-…`、`0002-…`）→ agent 容易引用、不易误删
- Status 严格枚举（proposed / accepted / deprecated / superseded by 0042）→ 防止"决策僵尸"
- ADR 不可改，只能追加新 ADR 取代 → 保留历史
- 每条 ADR ≤ 2 页，否则塞回 design doc

---

## 3. 代码地图（Code Map）实战

### 3.1 三种主流形态

| 形态 | 适用 | 优缺点 |
|---|---|---|
| **ASCII tree + 注释** | 小到中型 repo | 易读易写；不能表达"模块 A 依赖 B" |
| **Mermaid/Graphviz 依赖图** | 中到大型 | 可视化清晰；要么手画易过期，要么自动生成噪音多 |
| **mkdocs / sphinx autodoc** | 大型 + 文档站 | 自动同步代码；只覆盖 API，不覆盖架构 |

### 3.2 matklad 的 ARCHITECTURE.md 范式

[matklad's 2021 文章](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html)是当下事实标准（被 rust-analyzer、ripgrep 等采用）。三段式：

1. **Bird's-eye view** — 项目解决什么问题，一段话
2. **Code map** — 主要目录/模块，每段 2-5 句，回答"X 在哪里？" 和 "我看的这个东西是干啥的？"
3. **Cross-cutting concerns** — 不属于任何模块的横切关注点（性能、错误处理、可观测性）

关键约束：

> "Do name important files, modules, and types. **Do not directly link them (links go stale)**. ... Explicitly call-out architectural invariants. ... Point out boundaries between layers and systems."
> — matklad

也就是说：**用名字而非链接，强调不变量和边界**。

### 3.3 真实示例：rust-analyzer

[rust-analyzer 的 architecture.md](https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/architecture.md) 是模范范本：

- **Bird's Eye View**：一段说明 rust-analyzer "takes source code input and produces a structured semantic model of the code"
- **Entry Points**：直接点名 `main.rs`（LSP spawn）、`handlers/request.rs`（LSP 处理）、`Analysis`/`AnalysisHost` 类型
- **Code Map**：约 18 个 crate 的两三句描述，每个都说明"是 API boundary 还是 internal"
- **Cross-Cutting Concerns**：Stability、Code generation、Cancellation、Testing、Error Handling、Observability、Configurability、Serialization

例如：

> "`crates/base-db` — Salsa-based incremental computation infrastructure; defines input queries. **Knows nothing about cargo or filesystem paths.**"

最后一句就是"架构不变量"——agent 看到 base-db 调用了 cargo 就知道 PR 不能 merge。

### 3.4 自动生成工具

| 工具 | 语言/生态 | 输出 | 适用 |
|---|---|---|---|
| [dependency-cruiser](https://github.com/sverweij/dependency-cruiser) | JS/TS | dot / mermaid / json / html | 前端/Node 项目 |
| [Madge](https://github.com/pahen/madge) | JS/TS | 圆形依赖图 | 同上轻量 |
| [go-callvis](https://github.com/ofabry/go-callvis) | Go | call graph | Go |
| [pydeps](https://github.com/thebjorn/pydeps) | Python | import graph | Python |
| [Sourcegraph](https://sourcegraph.com/) | 多语言 | 代码导航/语义图 | 大型 monorepo |
| [Structurizr DSL](https://structurizr.com/) | 多语言 | C4 多图 | 架构层 |
| [Doxygen / Sphinx autodoc] | C++/Python 等 | API ref | API 文档站 |

**dependency-cruiser** 的典型用法（来自其 README）：

```
npx depcruise src --include-only "^src" --output-type dot | dot -T svg > deps.svg
```

它还能"validate against your own rules"——例如"core 模块不能 import ui 模块"，违反时 CI 失败。这是 **agent 友好的活文档**：错误在 PR 阶段就被挡住，文档不会偏离现实。

### 3.5 推荐做法

1. **首选手写 ARCHITECTURE.md**（matklad 风格）— 描述"为什么"和"边界"，agent 读得最快
2. **配合 dependency-cruiser 类工具**生成依赖图，CI 强制规则 → 防腐
3. **大型项目再加 Structurizr DSL** → 同源生成 C4 各级图

---

## 4. 领域术语表（Glossary）的写法

### 4.1 组织方式：字母序 vs. 子域

DDD 社区（[Martin Fowler on Ubiquitous Language](https://martinfowler.com/bliki/UbiquitousLanguage.html)）强调"一个 bounded context 一种语言"，所以：

- **小项目（单 bounded context）**：字母序即可
- **中大型 / 多子域**：**先按子域分组、子域内字母序**。例如 `# Billing` / `# Inventory` / `# Auth` 三节
- **arc42 第 12 章**也是把 glossary 当作"ubiquitous language"载体

### 4.2 单条术语的字段

借鉴 arc42 和实践经验，建议每条至少包含：

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

**"Don't confuse with"** 字段是反漂移核心——每次新人/agent 误用，把它加进来。

### 4.3 中英对照对 AI agent 的价值

国内项目 90% 注释/PR 中英混用。给 agent 写中英对照能：

1. agent 写 commit message 时正确选词（"订单 → Order"，不是 OrderRecord）
2. 跨团队对接时减少歧义
3. RAG 检索时同义词扩展

### 4.4 防止术语漂移

- **Glossary 也是 docs-as-code**：放仓库里，PR 修改要 review
- **CI 检查**：用 `grep` 或 [Vale](https://vale.sh/) 规则禁用废弃术语（如 "User → Member, User 已废弃"）
- **每季度 review**：matklad 推荐 ARCHITECTURE.md "a couple of times a year" 的频率同样适用 glossary
- **术语必须出现在代码里**：否则就是"幽灵术语"，应该删除或重命名代码

### 4.5 真实示例

- [Kubernetes Glossary](https://kubernetes.io/docs/reference/glossary/) — 字母序 + 标签筛选 + 多语种
- [arc42 Glossary 章节模板](https://docs.arc42.org/section-12/) — 表格 `Term | Definition` 双列
- DDD 社区惯例：在 `docs/glossary.md` 用 H3 列每个术语

---

## 5. Runbook / 操作手册的结构

### 5.1 业界共识：Tom Limoncelli 的 7 段

[PagerDuty 引用前 Google SRE Tom Limoncelli](https://www.pagerduty.com/resources/learn/what-is-a-runbook/)，列出 7 个推荐段：

1. Service Overview
2. Service Build Information
3. Instructions for Deploying the Software
4. Instructions for Common Tasks
5. **Pager Playbook** — "An outline of every possible monitoring system alert and step-by-step instructions"
6. Disaster Recovery Plans
7. Service Level Agreement

### 5.2 Google SRE Book 的"Best Practices"

[SRE Book Appendix B](https://sre.google/sre-book/service-best-practices/) 给出更细的服务文档要素：

- **Fail Sanely** — 输入校验、bad input 行为
- **Progressive Rollouts** — 灰度策略、跨地域顺序、回滚优先
- **SLOs / Error Budgets** — 用户视角度量、冻结策略
- **Monitoring** — 三类输出：Pages / Tickets / Logging（不要 email 告警）
- **Postmortems** — 责备无关、产出 action items
- **Capacity Planning** — N+2、负载测试比率
- **Overloads** — 优雅降级、限流、客户端指数退避

### 5.3 Increment.com 的实战观察

[Increment "When the pager goes off"](https://increment.com/on-call/when-the-pager-goes-off/) 总结的好 runbook 特征：

> "Step-by-step actionability... focus on triage and mitigation, not root-cause analysis... predefined severity classification... tied to dashboards and diagnostics... support for escape hatches / rollbacks."
> — DigitalOcean 的 Phil Calçado: "the main goal is always to get the system back to stability instead of trying to investigate root causes during outages."

### 5.4 可直接抄的 Runbook 骨架模板

```markdown
# Runbook: <Service Name> — <Alert/Operation Name>

## 1. Metadata
- **Service**: <name>
- **Owner team**: <slack-channel / oncall-rotation>
- **Severity**: SEV1 / SEV2 / SEV3
- **Last reviewed**: 2026-MM-DD
- **Related dashboards**: <Grafana URL>
- **Related ADRs**: ADR-0023, ADR-0042

## 2. Symptoms (告警长什么样)
- 触发指标: `http_5xx_rate > 0.05 for 5m`
- 用户感知: <"登录页面 502"，etc.>
- 影响范围: <region / tenant>

## 3. Quick mitigation (5 分钟内能做的)
1. 检查 <dashboard 链接>，确认是否真实告警
2. 如果是部署引发：`kubectl rollout undo deploy/<name>`（回滚优先）
3. 如果是流量过载：`flagger pause` 切走 50% 流量
4. 升级：5 分钟未恢复 → @oncall-secondary

## 4. Diagnosis (找根因)
- 检查日志: `stern -n prod <service> --since 10m`
- 检查依赖: <依赖列表 + 健康端点>
- 常见根因 #1: <DB 连接池耗尽> → 解决: <…>
- 常见根因 #2: <下游 API 超时> → 解决: <…>

## 5. Escalation
- L1 (5 min): <oncall primary>
- L2 (15 min): <oncall secondary + tech lead>
- L3 (30 min): <SRE manager + service owner>

## 6. Post-incident
- 写 postmortem 模板: <link>
- 是否更新本 runbook? 是 → 提 PR

## 7. Related
- ADRs: …
- Past incidents: <link to postmortems>
- Architecture: <link to ARCHITECTURE.md>
```

### 5.5 公开优秀样板

- [GitLab Production Runbooks (公开 repo)](https://gitlab.com/gitlab-com/runbooks) — "Runbooks for the stressed on-call"
- [PagerDuty Incident Response Docs](https://response.pagerduty.com/) — 行业标杆的 on-call 实践
- [Atlassian Incident Handbook](https://www.atlassian.com/incident-management) — incident 全流程
- [SRE Book Appendix B](https://sre.google/sre-book/service-best-practices/) — 9 大类最佳实践

---

## 6. 让 agent / 新人 30 分钟动手的 Onboarding 文档

### 6.1 优秀样本 1：OpenAI Codex AGENTS.md

[openai/codex AGENTS.md](https://github.com/openai/codex/blob/main/AGENTS.md)（213 行 / 16.7 KB）的 6 大段：

1. **Rust/codex-rs**：crate 命名、formatter、Clippy 偏好、模块大小上限（"Target Rust modules under 500 LoC"）、改完就跑 `just fmt && cargo test -p && just fix -p <project>`
2. **codex-core**：明令"resist adding code to codex-core"
3. **TUI style conventions**：指向 `styles.md`
4. **TUI code conventions**：Stylize trait、`textwrap::wrap`、`prefix_lines`
5. **Tests**：snapshot tests / integration tests / 测试断言
6. **App-server API best practices**：v2-only、命名、`#[ts(export_to)]`、ID 用 string、时间戳 `*_at` Unix sec、`#[experimental]` gating

特征：**有最近一次必跑命令、有"不要碰的文件"清单、有"目标行数上限"**——agent 拿到就能动。

### 6.2 优秀样本 2：Grafana developer-guide.md

[Grafana developer-guide.md](https://github.com/grafana/grafana/blob/main/contribute/developer-guide.md)（432 行）的 8 段：

1. Dependencies（macOS/Windows 分别说）
2. Download Grafana（git clone、yarn 配置、precommit hook）
3. Build Grafana（前端 / 插件 / 后端 / CGO / Windows）
4. Test Grafana（jest / go test / Playwright e2e）
5. Configure Grafana for development（`custom.ini`、devenv）
6. Build a Docker image
7. **Troubleshooting**（最长）—— ulimit / inotify / Node heap / Playwright 调试器
8. Next steps（指向 architecture / style guides）

特征：**troubleshooting 最长**——这是新人/agent 最容易卡的地方。把 `ulimit -n` 写进去能省一晚上 onboarding。

### 6.3 优秀样本 3：Kubernetes contributors/devel

[k8s/community/contributors/devel](https://github.com/kubernetes/community/tree/master/contributors/devel) 按 SIG 拆分：sig-architecture / sig-api-machinery / sig-scheduling …。每个 SIG 给出**自己的 code hierarchy + design conventions**。适合超大规模项目。

### 6.4 优秀样本 4：Rust Compiler Dev Guide

[rustc-dev-guide.rust-lang.org](https://rustc-dev-guide.rust-lang.org/overview.html)：写给新贡献者的"编译器之书"，编译流程 → 模块组织 → 调试技巧。约 200+ 页 markdown，但前 30 分钟能读完 overview 章节。

### 6.5 30 分钟动手的最小骨架

> 经验法则：**前 200 行决定一切**。新人/agent 80% 的疑问应该在前 200 行解决。

```markdown
# <Project> — Onboarding (30 min to first commit)

## 1. What this project does (1 段，3 句以内)
解决什么问题、给谁用、不做什么。

## 2. Quickstart (照抄能跑)
```bash
git clone … && cd …
make setup        # 安装依赖
make dev          # 启动本地
```
访问 http://localhost:3000，admin/admin。

## 3. Repo layout (matklad code map 风格)
- `apps/web` — Next.js 前端，业务页面
- `apps/api` — NestJS 后端，REST + GraphQL
- `packages/core` — 领域模型，**不依赖任何框架**
- `infra/` — Terraform / k8s manifests
> 不变量：`packages/core` 不能 import `apps/*`

## 4. How to make a change
1. 创建分支 `feat/<jira-id>-<short>`
2. 写测试：`<test path 模式>`
3. `make test && make lint`
4. 开 PR，至少 1 个 reviewer
5. CI 绿后 squash-merge

## 5. Where to look first
- 业务规则 → `packages/core/src/<domain>`
- API endpoint → `apps/api/src/routes`
- UI 组件 → `apps/web/src/components`
- 配置 → `config/` （不是 env vars，是 ts 文件）

## 6. Common tasks
- 加新 API：见 `docs/howto/add-endpoint.md`
- 加新页面：见 `docs/howto/add-page.md`
- 改 DB schema：先写 migration 再改 model

## 7. Troubleshooting
| 现象 | 解决 |
|---|---|
| `EMFILE: too many open files` | `ulimit -n 10240` |
| frontend hot reload 失效 | `rm -rf .next && yarn dev` |
| port 3000 占用 | `lsof -i :3000` 然后 kill |

## 8. Where to go next
- 架构详情：[ARCHITECTURE.md](./ARCHITECTURE.md)
- 决策历史：[docs/decisions/](./docs/decisions/)
- 术语表：[docs/glossary.md](./docs/glossary.md)
- 故障手册：[docs/runbooks/](./docs/runbooks/)
- agent 规约：[AGENTS.md](./AGENTS.md) / [CLAUDE.md](./CLAUDE.md)
```

### 6.6 信息密度排序（按"agent 30 分钟内最需要的"）

1. **Quickstart 命令**（必跑、能跑） → 占 30% 篇幅
2. **Repo layout + 不变量** → 25%
3. **How to make a change**（PR 流程） → 15%
4. **Where to look first**（任务 → 路径映射） → 15%
5. **Troubleshooting top 3** → 10%
6. **指针到深度文档** → 5%

避免：背景故事、产品愿景、架构演进史——这些放 ARCHITECTURE.md 即可。

---

## 7. 实战示例汇总（4+ 个真实开源项目）

| 项目 | 文档资产 | 借鉴点 | 链接 |
|---|---|---|---|
| **rust-analyzer** | architecture.md (matklad 范式) | Code map + 架构不变量、API boundary 标注 | [docs/book/src/contributing/architecture.md](https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/architecture.md) |
| **OpenAI Codex** | AGENTS.md (213 行) | "改完就跑这三条命令"、"不要碰这些文件" | [github.com/openai/codex/blob/main/AGENTS.md](https://github.com/openai/codex/blob/main/AGENTS.md) |
| **Grafana** | contribute/developer-guide.md (432 行) | Troubleshooting 最长、跨平台兼顾、Docker/devenv 范式 | [github.com/grafana/grafana/tree/main/contribute](https://github.com/grafana/grafana/tree/main/contribute) |
| **Kubernetes community** | contributors/devel/ 按 SIG 分目录 | 大型项目按子团队拆 dev docs、code hierarchy 单文件 | [github.com/kubernetes/community/tree/master/contributors/devel](https://github.com/kubernetes/community/tree/master/contributors/devel) |
| **GitLab Production** | gitlab-com/runbooks | 生产 runbook 的真实样板 | [gitlab.com/gitlab-com/runbooks](https://gitlab.com/gitlab-com/runbooks) |
| **Kubernetes architecture** | design-proposals-archive 中的 architecture.md | 显式声明非关系（"there are no internal inter-component APIs"） | [archived architecture.md](https://github.com/kubernetes/design-proposals-archive/blob/main/architecture/architecture.md) |

---

## 8. 综合建议：一份"全套" docs/ 目录建议

```
<repo>/
├── README.md                        # 5 分钟看懂干什么
├── ARCHITECTURE.md                  # matklad 三段式
├── AGENTS.md / CLAUDE.md            # agent 入口
├── CONTRIBUTING.md                  # PR 流程
├── docs/
│   ├── onboarding.md                # 30 分钟动手骨架（§6.5）
│   ├── glossary.md                  # 按子域分组（§4）
│   ├── architecture/
│   │   ├── workspace.dsl            # Structurizr / C4 DSL
│   │   ├── context.svg              # 自动生成
│   │   └── container.svg
│   ├── decisions/                   # MADR ADR
│   │   ├── 0001-use-postgres.md
│   │   └── 0042-switch-to-grpc.md
│   ├── runbooks/                    # §5.4 模板
│   │   ├── service-down.md
│   │   └── db-failover.md
│   └── howto/                       # 任务级 how-to
│       ├── add-endpoint.md
│       └── add-migration.md
└── .dependency-cruiser.cjs          # 依赖规则 → CI 强制
```

每一份文档都对应"AI agent 的一种问题"：

| Agent 问题 | 文档 |
|---|---|
| "这个项目是干啥的？" | README |
| "代码大致怎么组织？X 在哪？" | ARCHITECTURE.md |
| "我能不能改这里？规约是啥？" | AGENTS.md / CLAUDE.md |
| "30 分钟内怎么跑起来？" | onboarding.md |
| "为什么当初选 Postgres？" | docs/decisions/ |
| "Order vs PurchaseOrder 区别？" | glossary.md |
| "线上 5xx 怎么排查？" | runbooks/ |
| "core 能不能 import ui？" | dependency-cruiser 规则 + ARCHITECTURE.md 不变量 |

---

## 参考资料汇总

- [c4model.com](https://c4model.com/) — C4 model 主页
- [arc42.org/overview](https://arc42.org/overview) — arc42 12 章模板
- [4+1 view (Wikipedia)](https://en.wikipedia.org/wiki/4%2B1_architectural_view_model)
- [Structurizr](https://structurizr.com/) — C4 DSL 工具，含 MCP server
- [adr.github.io](https://adr.github.io/) — ADR 总入口
- [Nygard ADR template](https://github.com/joelparkerhenderson/architecture-decision-record/blob/main/locales/en/templates/decision-record-template-by-michael-nygard/index.md)
- [MADR 4.0 (adr.github.io/madr)](https://adr.github.io/madr/)
- [Y-statements (Olaf Zimmermann)](https://medium.com/olzzio/y-statements-10eb07b5a177)
- [matklad — ARCHITECTURE.md (2021)](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html)
- [rust-analyzer architecture.md](https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/architecture.md)
- [dependency-cruiser](https://github.com/sverweij/dependency-cruiser)
- [SRE Book — Service Best Practices](https://sre.google/sre-book/service-best-practices/)
- [SRE Book — Being On-Call](https://sre.google/sre-book/being-on-call/)
- [PagerDuty — What is a Runbook](https://www.pagerduty.com/resources/learn/what-is-a-runbook/)
- [Increment — When the Pager Goes Off](https://increment.com/on-call/when-the-pager-goes-off/)
- [GitLab runbooks](https://gitlab.com/gitlab-com/runbooks)
- [Martin Fowler — Ubiquitous Language](https://martinfowler.com/bliki/UbiquitousLanguage.html)
- [openai/codex AGENTS.md](https://github.com/openai/codex/blob/main/AGENTS.md)
- [Grafana contribute/](https://github.com/grafana/grafana/tree/main/contribute)
- [Kubernetes contributors/devel](https://github.com/kubernetes/community/tree/master/contributors/devel)
- [Kubernetes architecture (archived)](https://github.com/kubernetes/design-proposals-archive/blob/main/architecture/architecture.md)
