# 主题 3 深挖：AI agent 增量开发的 spec / plan / tasks 文档体系

*Generated: 2026-04-26 | Sources: 5 (Spec-Kit raw templates, BMAD-METHOD, Anthropic best-practices) | Confidence: High*

> 回答父研究 §3 留下的 5 个开放问题：Spec-Kit 真实字段、BMAD AC 格式、plan-mode 决策树、任务粒度、TDD×AI 工作流。所有片段从 GitHub raw 或 Anthropic 官方文档原文摘录。

---

## 1. GitHub Spec-Kit 四件套：真实模板字段

来源：`https://raw.githubusercontent.com/github/spec-kit/main/templates/{spec,plan,tasks}-template.md`（2026-04 抓取）。

### 1.1 spec-template.md（无 YAML frontmatter，markdown header 元数据）

```markdown
# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`
**Created**: [DATE]
**Status**: Draft
**Input**: User description: "$ARGUMENTS"
```

章节顺序：

1. `## User Scenarios & Testing *(mandatory)*`
   - `### User Story 1 - [Brief Title] (Priority: P1)`，子字段 `Why this priority` / `Independent Test` / `Acceptance Scenarios`（Given/When/Then 编号列表）
   - 重复 P2、P3…，再加 `### Edge Cases`
2. `## Requirements *(mandatory)*` — `FR-001` 起编，句式 `System MUST …` / `Users MUST be able to …`；不确定项写 `[NEEDS CLARIFICATION: <q>]`；`### Key Entities` 仅当涉及数据
3. `## Success Criteria *(mandatory)*` — `SC-001`，要求 measurable + technology-agnostic
4. `## Assumptions`

硬约束原文："Each user story/journey must be **INDEPENDENTLY TESTABLE** — if you implement just ONE of them, you should still have a viable MVP."

### 1.2 plan-template.md

```markdown
# Implementation Plan: [FEATURE]
**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
```

章节：
1. `## Summary`（一句话需求 + 一句话技术路线）
2. `## Technical Context`（9 个 advisory 字段，缺省都是字面量 `NEEDS CLARIFICATION`）：Language/Version、Primary Dependencies、Storage、Testing、Target Platform、Project Type、Performance Goals、Constraints、Scale/Scope
3. `## Constitution Check` — *GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*
4. `## Project Structure` — 文档输出 `plan.md/research.md/data-model.md/quickstart.md/contracts/`；源码三选一（single project / web app / mobile+API），删除未选项
5. `## Complexity Tracking` — 仅当违反 Constitution 才填表（Violation / Why Needed / Simpler Alternative Rejected）

### 1.3 tasks-template.md

```yaml
---
description: "Task list template for feature implementation"
---
```

Format：`[ID] [P?] [Story] Description`，`[P]`= different files & no dependencies；`[Story]`= US1/US2/US3。

依赖原文："Setup → Foundational（blocks all stories）→ User Stories（depend only on Foundational, can parallel）。Within a story: tests → models → services → endpoints → integration."

---

## 2. BMAD-METHOD：PRD / Story 模板与 AC 格式

仓库 2026-04 已重构到 `src/bmm-skills/`：
- 史诗+故事：`3-solutioning/bmad-create-epics-and-stories/templates/epics-template.md`
- 单故事：`4-implementation/bmad-create-story/template.md`

### 2.1 Epic + Story（Gherkin 严格 AC）

```
## Epic {{N}}: {{epic_title_N}}
**Goal:** {{epic_goal_N}}

### Story {{N}}.{{M}}: {{story_title}}
As a {{user_type}}, I want {{capability}}, So that {{value_benefit}}.

**Acceptance Criteria:**
- Given {{precondition}}
- When {{action}}
- Then {{expected_outcome}}
- And {{additional_criteria}}
```

### 2.2 单 Story 实现模板（核心创新：task→AC 反追踪）

```
# Story {{epic_num}}.{{story_num}}: {{story_title}}
Status: ready-for-dev

## Story
As a {{role}}, I want {{action}}, so that {{benefit}}.

## Acceptance Criteria
1. <从 epic 拷贝>
2. ...

## Tasks / Subtasks
- [ ] Task 1 (AC: 1, 3)        # 任务 (AC: #) 标注覆盖哪条 AC
  - [ ] Subtask 1.1
- [ ] Task 2 (AC: 2)

## Dev Notes
### References
- [Source: docs/architecture.md#auth-flow]   # 必须给出 path#anchor

## Dev Agent Record
- Agent Model Used: {{agent_model_name_version}}
- File List:                   # 实现完成后填的所有改动文件
```

**AC 数量经验**：每个 story 3–7 条；超 7 条说明 story 太大，拆分。**关键差异**：BMAD 用 `(AC: #)` 反追踪、Spec-Kit 用 `[US1]` 标签——两者可混用。

---

## 3. Plan-mode 决策树

Anthropic 原文 ([best-practices](https://code.claude.com/docs/en/best-practices))：

> "Plan Mode is useful, but also adds overhead. For tasks where the scope is clear and the fix is small (typo, log line, rename) ask Claude to do it directly. Planning is most useful when uncertain about approach, when modifying multiple files, or unfamiliar code. **If you could describe the diff in one sentence, skip the plan.**"

四阶段官方工作流：**Explore → Plan → Implement → Commit**（前两步在 Plan Mode）。

### 决策树

| 任务类型 | 一句话能描述 diff？ | 跨文件？ | 不熟悉的代码？ | 决策 | 文档产物 |
|---|---|---|---|---|---|
| 改 typo / 注释 | ✅ | ❌ | ❌ | **跳过 plan** | 无（PR description） |
| 加 log / rename 变量 | ✅ | 单文件 | ❌ | **跳过 plan** | 无 |
| 修小 bug（已定位） | ✅ | 1–2 文件 | ❌ | **轻 plan**：口头列 2–3 步 | inline TODO |
| 修小 bug（未定位） | ❌ | 未知 | 可能 | **Plan Mode** explore | 短 spec or PR |
| 加新接口/端点 | ❌ | 3+ 文件 | ❌ | **Plan Mode + plan.md** | spec.md + plan.md |
| 跨模块重构 | ❌ | 5+ 文件 | ✅ | **完整三件套** | 全套 |
| 新功能（含数据模型） | ❌ | ✅ | ✅ | **完整三件套 + research** | 全套 |
| 性能优化（无明确瓶颈） | ❌ | 未知 | ✅ | **Plan Mode + research.md** | research + plan |

口诀："**diff 一句话 → 直接做；多文件或不熟悉 → plan；新功能或重构 → 全套**"。

---

## 4. 任务粒度与 `[P]` 并行规则

| 层级 | 大小 | AC/任务数 | 完成时长 | 谁产出 |
|---|---|---|---|---|
| **Epic** | 一个用户旅程 | 含 3–8 个 story | 1–4 周 | PM/Architect |
| **Story** | 独立可测可发的切片 | 3–7 条 AC | 0.5–3 天 | PM+Tech Lead |
| **Task** | 单文件改动 + 验证 | 单一动作 | 15 min – 2 小时 | Tech Lead / agent |

**`[P]` 允许条件**（必须全部满足）：
1. 不同文件
2. 无依赖（不读其他未完成 task 的产物）
3. 同一 phase 内（不能跨 Foundational→Story 边界）

实战例（取自 tasks-template.md）：

```
# 可并行：两个不同 model 文件
- [ ] T012 [P] [US1] Create User model in src/models/user.py
- [ ] T013 [P] [US1] Create Order model in src/models/order.py

# 不可并行：service 依赖上面两个
- [ ] T014 [US1] Implement OrderService in src/services/order.py (depends on T012, T013)
```

**反模式**：同文件多 edit 不能并行（即使逻辑无关，避免 git 冲突）；跨 phase 不能并行。

---

## 5. TDD × AI agent 工作流

### 5.1 顺序铁律：spec → test → code

权威依据：

- **Spec-Kit tasks-template.md**："Write these tests FIRST, ensure they FAIL before implementation"
- **Anthropic 验证原则**："Include tests, screenshots, or expected outputs so Claude can check itself. **This is the single highest-leverage thing you can do.**"
- **Anthropic 官方 implement 步示例 prompt**：`"implement the OAuth flow from your plan. write tests for the callback handler, run the test suite and fix any failures."`

逻辑链：spec 给"做什么"，test 把"做什么"编码成可执行契约，AI agent 拿 test 当 reward signal。**没有 test 等于没有验证回路，agent 易产 plausible-but-wrong 代码**。

### 5.2 工作流图

```
┌──────────────────────────────────────────────────────────────────┐
│  人类         Plan Mode                  Normal Mode              │
├──────────────────────────────────────────────────────────────────┤
│  一句话 ──► /specify (Explore) ──► spec.md (P1/P2 + AC)           │
│  审批 + Ctrl+G 编辑 ──► /plan ──► plan.md + research + contracts/ │
│                       ──► /tasks ──► tasks.md ([P], test 在前)    │
│           ── 切到 Normal Mode ──                                  │
│  T010 写测试 ──► 跑 → 确认 FAIL                       (Red)       │
│  T012-T015 写实现 ──► 跑测试 → PASS                   (Green)     │
│  重构 / lint / typecheck ──► 全测试 PASS              (Refactor)  │
│  /commit + open PR ──► 归档到 specs/archive/<date>-<feature>/     │
└──────────────────────────────────────────────────────────────────┘
```

**检查点**：
1. spec.md 完成后人类 review，**禁止 agent 一口气从 idea 到代码**。
2. test 必须先 FAIL 再 PASS（防占位 / mock 自欺）。
3. tasks.md 里 test 编号 < 实现编号（如 T010-test < T012-impl）。

---

## 6. 可直接抄的骨架

### 6.1 spec.md

```markdown
# Feature Specification: <name>
**Feature Branch**: `001-<slug>`
**Created**: 2026-04-26
**Status**: Draft
**Input**: User description: "<原始需求>"

## User Scenarios & Testing *(mandatory)*
### User Story 1 — <核心切片> (Priority: P1)
**Why this priority**: <为什么是 MVP>
**Independent Test**: <怎么单独验证>
**Acceptance Scenarios**:
1. **Given** <前置>, **When** <动作>, **Then** <结果>

### User Story 2 — <次要> (Priority: P2)
...

### Edge Cases
- 当 <边界> 时如何处理？
- [NEEDS CLARIFICATION: <尚未确认的点>]

## Requirements *(mandatory)*
### Functional Requirements
- **FR-001**: System MUST <能力>。
- **FR-002**: Users MUST be able to <动作>。

### Key Entities *(if data involved)*
- **<实体>**: <定义>; 属性: <列>; 关系: <列>

## Success Criteria *(mandatory)*
- **SC-001**: 95% 请求 < 200ms
- **SC-002**: 注册成功率首次尝试 > 90%

## Assumptions
- <默认值 1> / <默认值 2>
```

### 6.2 plan.md

```markdown
# Implementation Plan: <name>
**Branch**: `001-<slug>` | **Date**: 2026-04-26 | **Spec**: ./spec.md

## Summary
<1 句话需求 + 1 句话技术路线>

## Technical Context
**Language/Version**: TypeScript 5.4
**Primary Dependencies**: Hono, Drizzle, Zod
**Storage**: PostgreSQL 16
**Testing**: Vitest + Playwright
**Target Platform**: Cloudflare Workers
**Project Type**: web-service
**Performance Goals**: p95 < 150ms @ 500 RPS
**Constraints**: 单 worker 内存 < 128MB
**Scale/Scope**: 1 万 DAU, 3 endpoints

## Constitution Check
- [x] 代码质量：lint + typecheck CI
- [x] 测试标准：所有 P1 story 有 contract + integration test
- [x] 性能：基准 < SC-001 阈值

## Project Structure
specs/001-<slug>/{spec,plan,research,data-model,quickstart,tasks}.md + contracts/
src/{routes,services,models,lib}/  +  tests/{contract,integration,unit}/

## Complexity Tracking
| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| 引入 Redis 限流 | 跨 worker 共享计数 | 单机方案在多实例下失效 |
```

### 6.3 tasks.md（含 `[P]` 示例）

```markdown
---
description: "Task list for <feature-name>"
---
# Tasks: <feature-name>

## Phase 1: Setup
- [ ] T001 Create project structure per plan.md
- [ ] T002 Init TypeScript project + deps (hono drizzle zod vitest)
- [ ] T003 [P] Configure ESLint, Prettier, tsconfig strict

## Phase 2: Foundational  ⚠️ blocks all stories
- [ ] T004 Setup Drizzle migrations in src/db/
- [ ] T005 [P] Auth middleware in src/lib/auth.ts
- [ ] T006 [P] Hono router skeleton in src/routes/index.ts
- [ ] T007 Base User entity migration (depends on T004)

## Phase 3: User Story 1 — 用户注册 (P1)  🎯 MVP
### Tests (write FIRST, must FAIL)
- [ ] T010 [P] [US1] Contract test POST /register in tests/contract/register.test.ts
- [ ] T011 [P] [US1] Integration test 注册→登录 in tests/integration/signup.test.ts

### Implementation
- [ ] T012 [P] [US1] User model in src/models/user.ts
- [ ] T013 [P] [US1] Password hash util in src/lib/hash.ts
- [ ] T014 [US1] RegisterService in src/services/register.ts (depends on T012, T013)
- [ ] T015 [US1] POST /register endpoint in src/routes/auth.ts (depends on T014)

**Checkpoint**: US1 通过 T010/T011 即可独立发版

## Phase 4: User Story 2 — 邮箱验证 (P2)
- [ ] T020 [P] [US2] Contract test POST /verify
- [ ] T021 [P] [US2] EmailToken model
- [ ] T022 [US2] EmailService (depends on T021)
- [ ] T023 [US2] POST /verify endpoint

## Phase 5: Polish
- [ ] T030 [P] 更新 OpenAPI 文档
- [ ] T031 [P] 性能基准 验证 SC-001
- [ ] T032 归档到 specs/archive/2026-04-<feature>/
```

---

## 7. 关键 takeaways

1. **Spec-Kit 用 `[P]` + `[US#]` 双标签**做并行 + 故事追踪；**BMAD 用 `(AC: #)`** 做 task→AC 反追踪。两套不冲突，可混用。
2. **"一句话能描述 diff 就跳过 plan"** 是 Anthropic 铁律——避免每个改动都拉全套文档。
3. **Story 必须 INDEPENDENTLY TESTABLE**：拆分粒度由"独立可发"决定（不是"独立可写"）。3–7 AC、0.5–3 天工时是阈值。
4. **TDD 顺序固定 spec → test → code**：tasks.md 里 test 编号 < impl 编号，模板原文要求 "Write tests FIRST, ensure they FAIL"。
5. **完整三件套适用范围窄**：仅当跨模块、不熟悉、新数据模型才上；80% 日常改动只要轻 plan 即可，否则文档反而拖速度。

---

## Sources

1. [Spec-Kit spec-template.md (raw)](https://raw.githubusercontent.com/github/spec-kit/main/templates/spec-template.md)
2. [Spec-Kit plan-template.md (raw)](https://raw.githubusercontent.com/github/spec-kit/main/templates/plan-template.md)
3. [Spec-Kit tasks-template.md (raw)](https://raw.githubusercontent.com/github/spec-kit/main/templates/tasks-template.md)
4. [BMAD-METHOD epics-template.md](https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/src/bmm-skills/3-solutioning/bmad-create-epics-and-stories/templates/epics-template.md)
5. [BMAD-METHOD story template.md](https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/src/bmm-skills/4-implementation/bmad-create-story/template.md)
6. [Anthropic — Claude Code Best Practices](https://code.claude.com/docs/en/best-practices)
