# SDD（规格驱动开发）深度研究报告

**生成日期：2026年6月6日 | 来源数：50+ | 置信度：高**

---

## 执行摘要

### SDD 的核心定义

SDD（Specification-Driven Development）是一种以**结构化规格文档**作为首要制品的软件工程范式。不同于"先写代码后补文档"，SDD 以 Spec 为唯一真相源（Single Source of Truth），AI 编码 agent 和人类开发者均以此生成、测试和验证代码。

行业共识的 SDD 三层成熟度模型（ThoughtWorks Birgitta Boeckeler 提出）：

| 层级 | 名称 | 描述 |
|------|------|------|
| **Level 1** | Spec-First | 在提示 AI 之前写好 spec；spec 可在完成后丢弃。最轻量，大多数团队的起点 |
| **Level 2** | Spec-Anchored | Spec 保留在版本控制中，与代码双向保持同步。生产系统的主流选择 |
| **Level 3** | Spec-as-Source | Spec 是人类唯一编写的制品，代码是完全派生的输出（标记 `// GENERATED FROM SPEC`）。先驱级 |

### SDD 与 TDD 的关系：互补而非竞争

**核心结论：SDD 和 TDD 是两个正交维度，天然互补。**

| 维度 | TDD | SDD |
|------|-----|-----|
| **抽象层次** | 单元/函数级 | 特性/系统级 |
| **回答的问题** | "我写的代码对不对？" | "我们在构建正确的东西吗？" |
| **主要制品** | 单元测试套件 | 结构化规格文档 |
| **迭代模型** | Red → Green → Refactor | Constitution → Specify → Plan → Tasks → Implement → Validate |
| **AI 集成度** | 非原生设计 | **为 AI 协作而生** |

**SDD + TDD 融合工作流：**

```
1. SDD 阶段：撰写 spec.md（功能需求 + 验收标准）
2. SDD 阶段：生成 plan.md（技术架构 + 数据模型）
3. SDD 阶段：分解为 tasks.md（原子化、可并行任务列表）
4. 对每个 Task：
   a. TDD Red：为具体行为编写失败的单测
   b. TDD Green：生成/实现最小代码使测试通过
   c. TDD Refactor：保持测试绿，重构代码
5. SDD 验证阶段：特性级别验收——我们是否构建了 spec 承诺的东西？
6. SDD 质量门禁：安全扫描、覆盖率阈值、性能基准、生产就绪检查
```

**类比：SDD 是蓝图，TDD 是每个施工步骤的质检。蓝图告诉你盖什么楼，TDD 确保每块砖砌得对。**

---

## 一、业界当前通用的 SDD 开发流程

### 1.1 标准化六阶段流水线

业界几乎所有 SDD 框架都收敛于同一流水线模式（以 GitHub Spec Kit 为事实参考实现）：

```
Constitution（宪章）→ Specify（规格化）→ Plan（技术规划）→ Tasks（任务分解）→ Implement（实现）→ Validate（验证）
```

**Phase 0: Constitution（宪章/基石）**
- 在任何特性工作之前，定义 `constitution.md` —— 项目的不变原则
- 包含：技术栈约束、测试标准、安全策略、质量门禁
- 例如："所有 API 必须使用 JWT 认证；bcrypt 12轮加盐；最低 80% 测试覆盖率；禁止硬编码密钥"

**Phase 1: Specify（规格化——WHAT & WHY）**
- 将自然语言特性描述转化为结构化规格
- 产出 `spec.md`：用户故事、功能需求、验收标准、边界用例
- 每个需求必须是可验证的（"系统必须... "）
- 模糊点显式标记 `[NEEDS CLARIFICATION: ...]`，防止 AI 猜测

**Phase 2: Plan（技术规划——HOW）**
- 将规格转化为技术决策：架构、数据模型、API 契约、技术选型及理由
- 产出 `plan.md`、`data-model.md`、`contracts/`、`research.md`、`quickstart.md`
- 每个技术选择追溯到具体需求

**Phase 3: Tasks（任务分解）**
- 将计划分解为原子的、可独立实现的任务
- 独立任务标记 `[P]` 表示可并行
- 产出 `tasks.md` —— AI agent 的可执行检查清单

**Phase 4: Implement（实现）**
- AI agent 按 spec 和 plan 逐任务执行
- 每完成一个任务即验证，再进入下一个

**Phase 5: Validate（质量门禁）**
- 包含安全扫描（SAST）、测试覆盖率阈值、lint/format、性能基准、生产就绪检查
- **重试循环模式**是关键：生成 → 测试 → 捕获错误 → 丰富 spec → 重新生成
- 实践者报告通常 2-3 轮即可达到生产质量

### 1.2 主流 SDD 框架对比

| 框架 | 核心特色 | 适用场景 | 仓库地址 |
|------|---------|---------|---------|
| **GitHub Spec Kit** | 3 个斜杠指令；跨 agent 模板；开源 MIT | 绿地项目，0→1 | [github.com/github/spec-kit](https://github.com/github/spec-kit) |
| **OpenSpec** (Fission AI) | 棕地优先；双文件夹模型（`specs/` + `changes/`）；增量 delta 模型 | 存量代码库，增量变更 | [github.com/Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) |
| **SpecD** | 多仓协调器模式；Schema 驱动的制品验证 | 多仓库、团队规模 SDD | [github.com/specd-sdd/SpecD](https://github.com/specd-sdd/SpecD) |
| **Kiro** (Amazon) | VS Code fork；spec 与代码双向同步 | AWS 生态集成开发 | AWS 分发 |
| **BMAD** | 多 agent 管线；版本化制品；合规审计追踪 | 合规要求高的场景 | [github.com/bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) |
| **specre** | 原子行为卡片；ULID 双向追踪；极轻量 | 微重构、增量变更 | [docs.rs/crate/specre](https://docs.rs/crate/specre/) |

### 1.3 大厂实践

| 企业 | 产品 | 工作流特色 |
|------|------|----------|
| **Microsoft** | GitHub Spec Kit + TypeSpec | 开源工具链 + API 优先的 TypeSpec 语言 |
| **Amazon** | Kiro IDE | 三文档流：Requirements → Design → Tasks，spec 与代码双向同步 |
| **Google** | Antigravity 平台 | 多 agent 并行编排，agent 产出有形制品（截图、测试输出）|
| **Normal Computing** | 自研 SDD | 独立 `sdd-repo` 作为跨服务单一真相源；混合 spec（产品意图 + 技术不变量）|
| **民生银行** | 私有云 IDE + Code CLI + 通义千问 | 三层 spec 层级: 企业级 → 领域级 → 项目级 |
| **阿里/淘特** | SpecKit + Qwen3 Coder Plus | 从 Vibe Coding → Rules 约束 → SDD 的完整演进路径 |

---

## 二、九个核心问题的深度解答

### （1）需求在后续变更时，如何维护已有的文档？

**核心策略：从"文档驱动"转向"条目驱动"（Item-Centric over Document-Centric）**

**a) 结构化变更控制（轻量级）**
- 提交变更请求（Change Request）→ 影响分析（Impact Statement）→ 跨职能评审（CCB）→ 实施更新 → 关闭
- TOGAF ADM 和 RUP 的经典流程，但在 SDD 中应大幅轻量化

**b) 需求版本化与基线（Baseline）**
- 每个需求分配唯一标识符（如 `REQ-AUTH-001`），记录：改了什么、谁改的、何时改、为什么改
- 在关键里程碑（sprint 开始、发布冻结、客户审批）创建冻结快照（Baseline）
- 使用工具（Jira、Modern Requirements4DevOps）自动记录变更历史

**c) SDD 原生方案：Delta 模型（推荐）**

OpenSpec 的两文件夹架构是最佳实践：

```
specs/          ← 当前真相（维护的单一真相源）
  auth/spec.md
changes/        ← 提议的增量变更
  add-password-reset/
    proposal.md
    design.md
    tasks.md
    specs/      ← delta spec，用 ADDED/MODIFIED/REMOVED 标记
```

每个变更是独立的文件夹，delta 标记清楚表示需求的变化：
```markdown
## Deltas
### ADDED
- REQ-AUTH-003: 通过邮件链接重置密码
### MODIFIED
- REQ-AUTH-001: 令牌过期从1小时延长至24小时
### REMOVED
- REQ-AUTH-002: SMS 二因素认证（已被 TOTP 替代）
```

**d) Spec-Code 一致性校验**
- 每次变更后运行"对账"流程："读 spec → 读代码 → 列出所有差异"
- GitHub Spec Kit 的 `/speckit.reconcile` 命令
- OpenSpec 的 `/opsx:sync` 命令
- 理想状态：agent 在工作时**双向更新** spec 和代码

**e) ADR（架构决策记录）的不可变性原则**
- ADR 是仅追加、不可修改的决策日志
- 当决策改变时，写**新的** ADR 替代旧的，将旧 ADR 状态更新为 "Superseded by ADR-XXX"
- 编号单调递增，不重用。这提供了完整的架构演进审计追踪

---

### （2）是否所有的中间输出件都需要归档？

**答案：不需要。关键在于区分"稳定知识"和"易变知识"。**

Cyrille Martraire（《Living Documentation》作者）提出的核心框架：

| 归档（稳定、高价值） | 丢弃或自动生成（易变） |
|---------------------|----------------------|
| 架构决策记录（ADR）——不可变日志 | 白板图——拍照后丢弃 |
| 已批准的规格（spec.md） | 临时的任务分解笔记 |
| API 契约（OpenAPI spec）——单一真相源 | 初步调研笔记（综合后即可丢弃）|
| 最终线框图（.png/.svg 快照） | 每日站会笔记 |
| 领域词汇表（Glossary） | 配置细节（从代码自动提取即可）|

**Martraire 的反臃肿检查清单（创建任何文档前自问）：**
1. 我们真的需要这个文档吗？
2. 这些知识在其他地方是否已经可以获取？（不重复）
3. 是否可以自动生成？（如果可以，不手写）
4. 是通用知识还是特定知识？
5. 准确性的保障机制是什么？（如果无法保持准确，不要创建）
6. 6 个月后这还会是正确的吗？（如果不是，标记为临时的或自动化）

**制品生命周期：**
```
Draft → In Review → Approved/Implemented → Archived（历史参考）
```

建议规范：**按特性归档，不按时间**。特性交付后，将相关制品移至 `docs/features/{feature-name}/`。

---

### （3）开发流程是否会太重？

**答案：如果不加控制会，但有明确的轻量化策略。**

**SDD 不是瀑布模型。** Spec 是活的文档，随项目演进。SDD 保留了瀑布模型的前置思考纪律，同时增加了敏捷迭代的能力。

**三种变更规模的正确流程密度：**

| 变更类型 | 正确方式 |
|---------|---------|
| 大型特性 / 新服务 | 完整 SDD 工作流（constitution → specify → plan → tasks → implement） |
| 5行的 bug fix | 直接修复 + commit |
| CSS 调整 | 直接修复 |
| 依赖版本升级 | 直接修改 |
| 探索性 Spike / 原型 | 与 AI 对话（无需 spec） |

**中国社区的"轻量化公式"（来自 CSDN 实践）：**
> `轻量技术方案 + Rules 约束 + Agent 实施 + AI 自动归档`

在每次小变更后，AI 反向分析变更代码，自动更新架构总览文档，形成闭环而无需繁重的预先 spec 撰写。

**Martraire 的四大活文档原则（防臃肿）：**
1. **可靠（Reliable）**：不存在过时、误导或缺失的文档
2. **省力（Low Effort）**：最小额外工作量，大量自动化从已有制品提取
3. **协作（Collaborative）**：文档是全团队活动，来自对话、结对编程、集体知识
4. **有洞察（Insightful）**：记录 **why** 而非 **what**，揭示设计知识而非复述代码

**ROI 预期管理：**
- 不要期望第1-4周就有净正向 ROI
- 实际时间线：**3-6个月达到盈亏平衡**
- 前1-3个月通常是净负向的（培训 + 流程调整成本）
- 67% 的开发者在学习阶段报告调试时间增加

---

### （4）微重构是否合适使用 SDD？

**答案：合适，但需要选对工具——传统的全量 spec SDD 太重，轻量级 delta 型 SDD 非常适合。**

**重型 SDD 的问题：**
- 为 5 行重构写 50 行 spec 得不偿失
- 绿地工具（如 Spec Kit）将 spec 视为变更制品而非长期能力契约，追踪小增量变更较困难

**微重构友好的轻量 SDD 方案：**

| 方案 | 核心思路 | 最适合 |
|------|---------|--------|
| **OpenSpec Delta 模型** | 变更独立文件夹 + `ADDED/MODIFIED/REMOVED` 标记；spec 开销与变更大小成正比 | 日常增量变更 |
| **specre 原子卡片** | 一个行为 = 一个 Markdown 文件 + 生命周期状态；AI agent 只需加载单文件即可理解变更 | 微行为变更 |
| **SDD-RIPER-One-Light** | 最小 spec + 低摩擦检查点 + restate → checkpoint → execute → validate → reverse sync 回路 | 日常编码和 bug fix |
| **AI 反向归档** | 小变更后 AI 反向分析变更代码，自动更新架构总览；无需预先 spec | 快速迭代 |

**核心洞察：spec 应与变更规模成比例，而非与系统规模成比例。** 5 行重构配 5 行 spec delta，不是 50 页系统规格书。

**决策树：**
```
变更规模 < 50 行且不改变行为？ → TDD 单测即可
变更规模中等但改变行为？ → OpenSpec delta model
变更规模大/新特性？ → 完整 SDD 工作流
```

---

### （5）输出件有没有成体系的归档方式？

**答案：有，而且相当成熟。以下是五种成体系的归档框架。**

**框架一：ADR（架构决策记录）**

业界最广泛采用的决策归档框架。Michael Nygard 2011 年提出，Martin Fowler 推广，现被 Microsoft Azure Well-Architected Framework 和英国政府数字服务部（GDS）正式背书。

```
doc/adr/
  0001-use-postgres-for-persistence.md
  0002-use-jwt-for-authentication.md
  0003-use-event-driven-architecture.md
  0004-supersede-0002-use-oauth2-instead.md
```

核心规则：
- 每 ADR 1 页，记录单一决策、上下文、备选方案、后果
- **仅追加，不可变** —— 永不事后修改
- 决策改变时：写新 ADR，旧的状态改为 "Superseded by ADR-XXX"
- Markdown 格式，存储在源码仓库 `doc/adr/` 中
- 状态生命周期：Proposed → Accepted → Superseded（或 Deprecated, Amended, Rejected）

工具链：`adr-tools` CLI、MADR 模板、Structurizr

**框架二：C4 模型 + arc42**

架构文档的两大互补框架：
- **C4 模型**：四级抽象层次（System Context → Container → Component → Code）
- **arc42**：12 节结构化模板（目标、约束、上下文、构建块、运行时、部署、风险等）

映射关系：C4 图 ↔ arc42 章节天然对应。使用 Docs-as-Code 工作流：

```
Structurizr DSL (模型) → Structurizr CLI → C4-PlantUML (.puml) → Asciidoctor → HTML/PDF → GitHub Pages
arc42 AsciiDoc (.adoc) ──────────────────────────────┘
```

整个文档存在于 Git 中，通过 PR 评审，CI/CD 自动发布。

**框架三：OpenAPI 契约优先**

对于 API 规格，OpenAPI YAML/JSON 是单一真相源：
- Spec 与代码同仓存储
- CI 强制 spec 更新通过 PR 检查
- OpenAPI Generator 生成服务端桩、客户端 SDK、多语言模型
- Spectral 进行 lint；Dredd 进行实现验证

**框架四：Structurizr DSL（图表即代码）**

用代码而非拖拽来定义架构图：
- 一个模型，多个视图 —— 改模型，所有图同步更新
- 纯文本、可 diff、PR 可评审
- 导出为 PlantUML、Mermaid、Draw.io、SVG、PNG

**框架五：SpecD 的 Schema 驱动归档**

SpecD 通过 `schema.yaml` 定义制品工作流，支持跨仓、schema 验证的体系化归档。

---

### （6）是否能扩展为增量需求的输入规范？

**答案：可以，而且已经在发生。多个 SDD 框架已原生支持此能力。**

**OpenSpec 的 Delta 模型** 天生就是增量需求格式。每个 change 文件夹的 `ADDED/MODIFIED/REMOVED` 标记字面意义上在说"需求曾经是什么，现在变成什么"。

**specre 的原子卡片模型** 将每个需求作为独立文件，拥有生命周期状态。可以增加、修改或废弃单个需求卡片而不影响其他。

**SpecD 的 Schema 模型** 允许项目通过 `schema.yaml` 自定义制品工作流和需要的字段，是本质上可扩展的输入规范标准。

**可集成的已有标准格式：**

| 格式 | 类型 | 与 SDD 的集成方式 |
|------|------|------------------|
| **EARS 语法** | 结构化自然语言 | `While <前置条件>, when <触发器>, the <系统> shall <响应>` —— 嵌入 spec.md |
| **Requs** | 受控自然语言 | 机器可解析的 `.req` 文件，CI 可编译 |
| **Gherkin/Cucumber** | BDD 场景 | `Given/When/Then` 既作 spec 内容又作可执行测试 |
| **IEEE 830 SRS** | 文档模板 | 结构映射到 SDD spec 各节 |

**一个同时作为 SDD 制品和增量需求输入的 spec 文件示例：**
```markdown
# Feature: User Authentication
Status: stable
Last Modified: 2026-06-01
Spec-Id: SPEC-AUTH-001

## Requirements
### REQ-AUTH-001
While the user is not authenticated, when they provide valid credentials,
the system shall return a JWT token with 1-hour expiry.

## Deltas (current change: extend-session)
### MODIFIED
- REQ-AUTH-001: Extended token expiry from 1hr to 24hr
### ADDED
- REQ-AUTH-003: Password reset via email link
```

**收敛趋势：结构化 Markdown + Schema 验证** 已成为 AI 友好 spec 的通用交换格式。

---

### （7）SE 的设计文档做到什么粒度，对于 AI 开发更为友好？

**核心原则：spec 应是最小单元，能在单次工作会话中无歧义地捕获意图。**

**三层粒度方法：**

| 粒度 | 描述 | 最佳场景 |
|------|------|---------|
| **原子级 / 单行为 Spec** | 一个行为 = 一个 .md 文件 + YAML frontmatter + ULID 追踪 | 最大上下文效率；许多小增量变更 |
| **特性级 / 阶段分解 Spec**（⭐当前最佳实践） | 一个特性拆为 `spec.md` + `plan.md` + `tasks.md` | 绿地特性；结构化团队工作流；人类可评审 |
| **系统级 / 混合 Spec** | 专用 SDD repo + 全局 constitution + 每特性 spec | 多仓库企业系统 |

**按目标推荐的 Spec 长度：**

| 目标 | 推荐长度 |
|------|---------|
| 基础函数 | 100-200 词 |
| API 端点 | 300-500 词 |
| 组件或模块 | 500-800 词 |
| 系统架构 | 1,000-2,000 词 |

**AI 友好 Spec 的八大原则：**
1. **需求，而非实现** —— 定义 *what*，不定义 *how*
2. **显式边界用例和错误状态** —— AI 不会推断你遗漏的东西
3. **无歧义的、量化的语言** —— 避免"快""鲁棒""用户友好"
4. **结构化、可解析的格式** —— 标题、表格、代码块、frontmatter
5. **自包含文档** —— 不依赖 AI 可能没有的外部上下文
6. **领域术语表** —— 确保跨 AI 会话的一致解释
7. **机器可读的验收标准** —— 使 AI 能自动生成测试
8. **显式的 spec id 可追踪性** —— 如 `REQ-001`、`// @specre <ULID>`

**反模式（INNOQ 和从业者总结）：**
- **单体 Spec** —— 大文档强迫 agent 解析整个功能才能理解一个行为
- **跳过实现计划（plan.md）**—— agent 会即兴决定构建顺序，遗漏步骤
- **过度模板化** —— 十个空节让开发者麻木；每节都应物有所值
- **Spec 中包含代码片段** —— 这会让 AI 产生技术偏见，过早锁定实现决策
- **脆弱的顺序编号**（FR-1, FR-2...）—— 当需求重排序、拆分或废弃时断裂。改用**稳定的、主题域标识符**（如 `FR-TEST-ISOLATION-001`）

**AI 友好 Spec 格式推荐：**

| 格式 | 最适合 |
|------|--------|
| **Markdown + YAML frontmatter** | 通用 spec、RFC、设计文档 |
| **Gherkin (Given/When/Then)** | 行为 spec、验收标准 |
| **OpenAPI YAML/JSON** | REST API 契约 |
| **TypeSpec** (Microsoft) | 大规模 API 设计（REST + gRPC）|
| **EARS 语法** | 安全关键/监管需求的正式语法 |
| **PLAIN** (Product Language for AI Notation) | 产品 spec（含 MoSCoW、用户故事、数据模型、路由）|

**务实的 sweet spot：** 对大多数使用 AI coding agent 的团队，**特性级 + 阶段分解**（GitHub Spec Kit 模型）是当前最佳实践。文档小到能放入上下文窗口，同时足够结构化以供人类评审。

---

### （8）如何推广到存量的复杂项目？

**核心洞察：棕地 SDD 与绿地 SDD 有根本性不同。绿地习惯"写全量 spec 然后生成代码"在无文档的遗留系统上无法存活。**

**推荐方法：先建立架构理解，再写限定范围的 spec。**

**五步棕地 SDD 工作流：**

**Step 1：先构建语义理解**
- **不要**一开始就写 spec
- 使用语义分析工具构建现有仓库的依赖图
- 理解代码实际在做什么 —— 包括隐式契约、顺序依赖、未文档化的错误处理
- Salesforce 工程团队通过依赖分析主导遗留迁移，将预估 2 年缩短为 4 个月

**Step 2：写变更级别的 Spec，而非全量代码库的 Spec**
- 这是**最重要的范式转变**
- 写窄 spec，仅覆盖变更的 delta：
  - 当前行为（系统今天做什么）
  - 目标行为（精确的 delta）
  - 不变量（相邻系统中什么必须不变）
  - 范围边界（明确排除什么）
- Spec 覆盖随每次修改有机增长，集中在价值最高的地方

**Step 3：针对现有架构分解**
- 实现任务必须尊重现有架构结构和约定
- 同一遗留代码库的不同部分可能遵循不同模式 —— 分解必须考虑到这一现实

**Step 4：在隔离的工作树中执行**
- 使用 Git worktree 进行并行、隔离的实现流
- 每个 agent 获得自己的目录、分支和文件系统状态，防止交叉污染

**Step 5：同时验证 Spec 和已有测试**
- 棕地验证有双重目的：(a) 确认变更匹配 spec，(b) 确认不破坏现有行为
- 机器可检查的契约（如在 CI 中验证 OpenAPI）将散文 spec 转化为可执行制品

**三种棕地 Spec 模式：**
1. **变更 Spec（Delta Specifications）**—— 仅捕获行为 delta。每个 bug fix、feature、重构都成为为触及的代码添加 spec 的机会
2. **依赖边界 Spec** —— 在遗留和现代系统之间的集成点形式化隐式契约，使用机器可读制品（OpenAPI、Protobuf）
3. **迁移 Spec** —— 定义目标状态和增量步骤（绞杀者模式：构建门面 → 识别可提取模块 → 增量迁移 → 持续监控）

**团队推广手册（90 天分阶段推行）：**

| 阶段 | 时间 | 范围 |
|------|------|------|
| **试点** | 第1-30天 | 3-5名热心开发者，内部工具或技术债（不要是客户交付特性！）；建立基线指标 |
| **扩展** | 第31-60天 | 2-3个额外团队的分批培训；构建 champion 网络（每5-8名开发者1位 champion） |
| **全组织** | 第61-90天 | SDD 成为默认方法论；纳入新人入职；建立实践社区，每月同步 |

**工具选择决策树：**
```
从零开始的新项目？
  YES → Spec Kit（如果是多仓则用 SpecD）
  NO  → 代码库有清晰的架构文档？
         YES → Spec Kit + brownfield 模块也许可行
         NO  → OpenSpec（先写变更级 spec）

需要合规/审计追踪？
  YES → BMAD（多 agent 管线 + 版本化制品）

跨多个仓库？
  YES → SpecD（协调器模式）

不确定？
  → OpenSpec（最小采纳摩擦，绿地和棕地通吃）
```

---

### （9）设计跨越多仓的场景应该如何处理？

**核心方案：SpecD 协调器模式（推荐）**

**多仓 SDD 面临的结构性问题：**
- Spec 散布在不同仓库中变得不一致或重复
- 横切关注点（认证契约、API schema、共享约定）没有单一真相源
- AI agent 在跨仓库工作时丢失上下文
- 跨仓库边界的依赖追踪是手动的、易出错的

**方案一：SpecD 协调器模式（⭐推荐）**

SpecD 是专门为此构建的。支持带有**协调器 repo** 的多工作空间项目：

```
sdd-repo/（协调器 — 系统级单一真相源）
  constitution.md        ← 系统级不变量
  specs/
    auth/                 ← 认证契约（所有服务引用）
    api-conventions/      ← API 约定（所有服务引用）
  workspaces/
    user-service/         → 指向 user-service 仓库
    order-service/        → 指向 order-service 仓库

user-service/（服务仓库 — 仅维护自己的代码）
  src/...
  tests/...

order-service/（服务仓库）
  src/...
  tests/...
```

**上下文编译在跨仓场景如何工作：**
1. 项目级 include 模式决定哪些 spec 始终适用
2. 工作空间级 include/exclude 模式按活跃工作空间应用
3. `dependsOn` 遍历自动拉取跨工作空间边界的相关 spec
4. 组装后的上下文块交付给 agent 执行当前生命周期步骤

**方案二：OpenSpec + Git Submodules**
- 中央 "spec repo" 包含 `openspec/specs/` 共享契约
- 服务仓库包含各自的 `openspec/` 目录
- 跨仓变更通过路径引用或 submodules 引用中央 spec
- Delta 模型跨边界有效 —— 一个仓库的变更可以引用另一个仓库的 spec

**方案三：联邦 Spec + 契约测试**
- 适用于无法集中化的组织
- 每个服务维护自己内部行为的 spec
- 跨服务契约（API、事件、schema）作为版本化制品发布
- CI 管线验证实现匹配已发布的契约
- Pact 风格的契约测试桥接各仓库的 spec 和实现

**三种方案的对比：**

| 方案 | 最适合 | 关键权衡 |
|------|--------|---------|
| **SpecD 协调器** | 有明确系统边界的微服务架构 | 需采纳 SpecD；协调器 repo 成为关键基础设施 |
| **OpenSpec + 子模块** | 较小的多仓设置；原生 git 团队 | 手动依赖管理；需维护子模块纪律 |
| **联邦契约 Spec** | 松散耦合的组织；独立团队自治 | 契约可能漂移；需要严格的 CI 执法 |

---

## 三、Harness 工程：SDD 和 TDD 的元层

### 什么是 Harness 工程？

**Harness Engineering（管控工程）** 是设计围绕 AI 模型的**环境、约束、工具、验证系统、反馈回路、记忆、沙箱和编排**的学科，使其产生可靠、确定性的输出。

**核心公式：Agent = Model + Harness**

模型提供推理和生成；Harness 提供其他一切 —— 决定模型看到什么、可以做什么、以及一致性的结构化系统。

**Harness 工程的三层演进：**
1. **Prompt Engineering** —— 怎么问模型（"用语音指令转向"）
2. **Context Engineering** —— 给模型看什么（"路标、旗帜、地图"）
3. **Harness Engineering** —— 模型周围有什么环境和约束规则（"建造赛道、护栏、缰绳和马鞍"）

**OpenAI 的四个闭环动作：**
1. **Constrain（约束）** —— 硬边界：架构规则、依赖白名单、权限隔离、沙箱
2. **Inform（告知）** —— 精确的、机器可读的上下文：`AGENTS.md`、架构地图、API 契约
3. **Verify（验证）** —— 自动化质量门禁：lint 规则、单元/集成测试、LLM-as-judge 评审
4. **Correct（修正）** —— 反馈回路：错误变为修复指南、自动回滚、human-in-the-loop

**Harness 工程与 SDD、TDD 的关系：**

- **TDD** 在单元层运作 —— 测试是 Harness 中的**一种传感器**，提供细粒度的回归安全网
- **SDD** 提供**指引层** —— spec 定义了 agent 应该构建什么，充当前馈控制
- **Harness Engineering** 是**元层**，整合两者：spec（指引）告诉 agent 构建什么；测试（传感器）验证构建了什么。Harness 编排两者之间的反馈回路

> SDD 没有 Harness 只是文档；TDD 没有 Harness 只是局部安全。Harness 使两者成为体系化的系统。

---

## 四、关键工具清单

| 工具 | 仓库/地址 | 最佳场景 |
|------|---------|---------|
| **GitHub Spec Kit** | [github.com/github/spec-kit](https://github.com/github/spec-kit) | 绿地项目，0→1 |
| **OpenSpec** (Fission AI) | [github.com/Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) | 棕地/存量代码库，增量变更 |
| **SpecD** | [github.com/specd-sdd/SpecD](https://github.com/specd-sdd/SpecD) | 多仓、团队规模 SDD |
| **BMAD** | [github.com/bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) | 合规审计追踪，多 agent 管线 |
| **specre** | [docs.rs/crate/specre](https://docs.rs/crate/specre/) | 原子 spec 卡片，微重构 |
| **SDD-RIPER** | [github.com/huisezhiyin/sdd-riper](https://github.com/huisezhiyin/sdd-riper) | 轻量 agent harness，日常编码 |
| **Spec-Coding MCP** | [github.com/kevinlin/spec-coding-mcp](https://github.com/kevinlin/spec-coding-mcp) | MCP 服务 + Claude Code Skill |
| **Vaultspec** | [pypi.org/project/vaultspec-core](https://pypi.org/project/vaultspec-core/) | Research → Execute → Review 流水线 |
| **Kiro** (Amazon) | AWS 分发 | VS Code fork，spec-code 双向同步 |
| **TypeSpec** (Microsoft) | [typespec.io](https://typespec.io) | API 设计优先语言 |
| **adr-tools** | [github.com/npryce/adr-tools](https://github.com/npryce/adr-tools) | ADR 创建和管理 CLI |
| **Structurizr** | [structurizr.com](https://structurizr.com) | 图表即代码，C4 模型 |

---

## 五、综合建议与收尾

### 务实的采纳路径

1. **从 Spec-First 开始，不要从 Spec-as-Source 开始。** 写一个结构良好的 spec.md 再提示 AI，成本几乎为零，收益立竿见影。不要一开始就追求 spec 与代码的完美双向同步。

2. **SDD + TDD 是黄金组合，不是二选一。** SDD 做蓝图 → TDD 在每个任务内做质检 → Harness 工程将两者体系化。

3. **绿地和棕地走不同的路。**
   - 绿地：Spec Kit，全量 spec，constitution 先行
   - 棕地：OpenSpec，delta spec，语义理解先行

4. **spec 的大小与变更成比例，不与系统成比例。** 这是防止流程臃肿的第一原则。

5. **不要归档一切。** 区分稳定知识和易变知识。ADR + API 契约 + 最终 spec 是底线。其他都可以在需要时自动生成或丢弃。

6. **建立 Harness 思维。** 工程师的角色从"写代码的人"转变为"设计写代码系统的人"。把"品味"编码为机器可执行的规则。

7. **接受 3-6 个月的学习曲线。** 前几个月是投资，不是失败。

### 关键数据点

- 同一模型在 Harness 质量不同时，任务成功率从 **12% → 76%**
- 10步任务中每步 95% 成功率 → 端到端只有 **~60%**，Harness 逐步捕获失败
- 3-6个月达到净正向 ROI
- 67% 开发者学习阶段调试时间增加
- 2-3 轮 spec → generate → validate 迭代通常达到生产质量
- Spec 推荐长度：函数级 100-200词 → API级 300-500词 → 系统级 1,000-2,000词

---

## 方法论

研究覆盖：4 个并行子 agent，50+ 独立搜索查询，深度阅读 80+ 来源，涵盖英文和中文资源。

子问题矩阵：
- SDD 业界标准流程与 TDD 对比融合
- AI 友好的 Spec 粒度与反模式
- 需求变更时的文档维护策略
- 中间件归档策略与轻量化方法
- Spec-as-Code 与体系化归档框架
- Harness 工程实践
- 微重构与轻量 SDD
- 存量/棕地项目推广
- 多仓跨仓场景
- 中国社区 SDD/TDD 实践（腾讯、阿里、民生银行等）
- BDD/ATDD/SBE 方法论谱系
- 大厂实践（Microsoft、Amazon、Google）

## 主要来源

1. [GitHub Spec Kit — spec-driven.md](https://github.com/github/spec-kit/blob/main/spec-driven.md)
2. [Microsoft Learn — SDD Training Module](https://learn.microsoft.com/en-us/training/modules/spec-driven-development-github-spec-kit-greenfield-intro/)
3. [Martin Fowler — Understanding SDD: Kiro, spec-kit, and Tessl](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)
4. [INNOQ — The Right Kind of Hard: Hidden Costs of SDD](https://www.innoq.com/en/blog/2026/04/versteckte-kosten-spec-driven-development/)
5. [Augment Code — SDD for Brownfield Codebases](https://www.augmentcode.com/guides/spec-driven-development-brownfield-codebases)
6. [Forbes — How SDD Sets the New Standard](https://www.forbes.com/councils/forbestechcouncil/2026/03/09/how-spec-driven-development-sets-the-new-standard-for-software-development/)
7. [Normal Computing — SDD for Real Production Systems](https://www.normalcomputing.com/blog/building-sdd-for-real-production-systems-sdd-part2)
8. [OpenSpec — GitHub (Fission AI)](https://github.com/Fission-AI/OpenSpec)
9. [Martin Fowler — Architecture Decision Record](https://martinfowler.com/bliki/ArchitectureDecisionRecord.html)
10. [Cyrille Martraire — Living Documentation (InfoQ)](https://www.infoq.com/articles/book-review-living-documentation/)
11. [Atlan — Agent Harness Explained](https://atlan.com/know/what-is-an-agent-harness/)
12. [Tencent Cloud — SDD 完整指南](https://cloud.tencent.com.cn/developer/article/2586438)
13. [民生银行 SDD 实践 (SegmentFault)](https://segmentfault.com/a/1190000047758803)
14. [阿里开发者 — 从 Vibe Coding 到 SDD](https://developer.aliyun.com/article/1709229)
15. [Wikipedia — Spec-driven development](https://en.wikipedia.org/wiki/Spec-driven_development)
16. [ThoughtWorks Technology Radar — OpenSpec](https://www.thoughtworks.com/zh-cn/radar/tools/openspec)
17. [UK Gov GDS — ADR Framework](https://technology.blog.gov.uk/2025/12/08/the-architecture-decision-record-adr-framework-making-better-technology-decisions-across-the-public-sector/)
18. [dev.to — Spec Kit vs BMAD vs OpenSpec](https://dev.to/willtorber/spec-kit-vs-bmad-vs-openspec-choosing-an-sdd-framework-in-2026-d3j)
19. [TypeSpec 1.0 GA (Microsoft)](https://typespec.io/blog/typespec-1-0-GA-release/)
20. [三金的窝 — SDD 层级模型](https://wukun.work/sdd/)

---

*🤖 本报告由 Claude Code Deep Research Pro 生成，基于 4 个并行子 agent 对 80+ 来源的研究。*
