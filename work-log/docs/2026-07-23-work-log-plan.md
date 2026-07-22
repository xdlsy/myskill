# work-log Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `work-log` skill — a pure-markdown skill that turns an end-of-day brain-dump into a structured 4-dimension daily log, archives it, and rolls up weekly/monthly/half-year/annual reports at period boundaries.

**Architecture:** Zero scripts. The skill is a `SKILL.md` (production code) plus `memory.md` (config/habits/cursor), five output `templates/`, and a `tests/` suite of subagent pressure-scenarios (RED→GREEN→REFACTOR per superpowers:writing-skills). All file I/O is plain markdown the user can hand-edit. Reports aggregate hierarchically (weekly←dailies, monthly←weeklies, half-year←monthlies, yearly←monthlies) so high-level reports never read raw dailies.

**Tech Stack:** Markdown only. Tests dispatch `general-purpose` subagents via the Agent tool, operating in hermetic `/tmp/wltest-*` archive dirs (the user's real `~/worklog` is never touched by tests).

**Spec:** `work-log/docs/2026-07-23-work-log-skill-design.md`

---

## File Structure

| File | Responsibility | Created in |
|---|---|---|
| `work-log/SKILL.md` | The skill itself — daily flow, 4-dim structure, boundary rules, aggregation, edge cases, no-fabrication, red flags | Task 3 (GREEN) |
| `work-log/memory.md` | Config (archive_root, language, boundaries), habits, `last_generated` cursor | Task 1 |
| `work-log/templates/daily.md` | Daily log skeleton | Task 1 |
| `work-log/templates/weekly.md` `monthly.md` `halfyear.md` `yearly.md` | Report skeletons | Task 1 |
| `work-log/tests/fixtures/braindump-thin.txt` | Brain-dump where item 2 lacks a result → tests no-fabrication | Task 1 |
| `work-log/tests/fixtures/braindump-overwrite.txt` | Same-day brain-dump → tests overwrite-confirmation | Task 1 |
| `work-log/tests/fixtures/week-2026-W30/2026-07-{20,21,23,25,26}.md` | 5 daily logs (07-22 & 07-24 missing) → tests weekly dedup + missing-day reporting | Task 1 |
| `work-log/tests/scenarios/01-daily-structure.md` | Scenario prompt: daily log from thin brain-dump | Task 1 |
| `work-log/tests/scenarios/02-no-overwrite.md` | Scenario prompt: same-day re-log | Task 1 |
| `work-log/tests/scenarios/03-boundary-detection.md` | Scenario prompt: 5 dates → which periods end | Task 1 |
| `work-log/tests/scenarios/04-weekly-coverage.md` | Scenario prompt: weekly report from W30 dailies | Task 1 |
| `work-log/tests/scenarios/05-hierarchical-monthly.md` | Scenario prompt: monthly report must read weeklies, not dailies | Task 1 |
| `work-log/tests/baseline-results.md` | RED: verbatim baseline failures | Task 2 |

**Deterministic boundary facts (verified, baked into scenarios):**
- `2026-07-22` Wednesday → no boundary
- `2026-07-26` Sunday → weekly (2026-W30)
- `2026-07-31` Friday → monthly (2026-07)
- `2026-06-30` Tuesday → monthly (2026-06) + half-year (2026-H1)
- `2026-12-31` Thursday → monthly (2026-12) + half-year (2026-H2) + yearly (2026)
- ISO week 2026-W30 = Mon 2026-07-20 → Sun 2026-07-26

---

## Task 1: Scaffold skill dir, templates, memory, fixtures, scenarios

**Files:**
- Create: `work-log/memory.md`, `work-log/templates/{daily,weekly,monthly,halfyear,yearly}.md`
- Create: `work-log/tests/fixtures/braindump-thin.txt`, `braindump-overwrite.txt`
- Create: `work-log/tests/fixtures/week-2026-W30/2026-07-20.md` (and 21,23,25,26)
- Create: `work-log/tests/scenarios/01-daily-structure.md` … `05-hierarchical-monthly.md`

> Do NOT create `SKILL.md` yet — that is the production code; it is written in Task 3 (GREEN) only after RED baseline (Task 2).

- [ ] **Step 1: Create directory tree**

```bash
mkdir -p /Users/lsy/skills/work-log/templates \
         /Users/lsy/skills/work-log/tests/fixtures/week-2026-W30 \
         /Users/lsy/skills/work-log/tests/scenarios
```

- [ ] **Step 2: Write `work-log/memory.md`**

```markdown
# work-log memory

## 配置
archive_root: ~/worklog
language: 中文
timezone: Asia/Shanghai
boundaries:
  week: Mon-Sun (ISO week number)
  halfyear: natural (H1=Jan-Jun, H2=Jul-Dec)

## 习惯
detail_level: 简洁           # 简洁 | 详细
known_projects: []           # skill 按使用自动补充，如 [订单服务, 风控平台]
known_people: []             # skill 按使用自动补充
work_types: []               # skill 按使用自动补充，如 [排查, 重构, 方案设计]

## 状态游标（skill 自动维护，请勿手改）
last_generated:
  weekly: null     # 形如 2026-W29
  monthly: null    # 形如 2026-06
  halfyear: null   # 形如 2026-H1
  yearly: null     # 形如 2025
```

- [ ] **Step 3: Write `work-log/templates/daily.md`**

```markdown
# {{date}} 工作日报

## 核心工作

### 1. {{标题}}
- **内容**：{{做了什么}}
- **解决了什么问题**：{{问题}}
- **已经产生了什么结果**：{{结果，缺则写（待补充）}}
- **对后续的影响**：{{forward 影响：项目推进/协作/风险/可复用产物/成长等，缺则写（待补充）}}

### 2. {{标题}}
- ...

## 今日小结
{{2–3 句概括}}

---
*覆盖范围：{{date}} | 数据来源：用户脑暴*
```

- [ ] **Step 4: Write `work-log/templates/weekly.md`**

```markdown
# {{year}}-W{{week}} 周报（{{start}} ~ {{end}}）

## 本周核心工作
{{按主题归并去重后的工作，来源为本周各日报}}

## 主要进展
{{关键进展}}

## 遗留问题
{{未关闭的问题}}

## 下周关注
{{下周重点}}

## 数据完整性
{{如：本周 7 天全部有记录；或 7/22、7/24 无记录}}

---
*覆盖范围：{{start}}–{{end}} | 数据来源：{{日报文件列表}} | 生成时间：{{ts}}*
```

- [ ] **Step 5: Write `work-log/templates/monthly.md`**

```markdown
# {{year}}-{{month}} 月报

## 月度总结
{{综合本月周报 + 未被周报覆盖的零散日报}}

## 主要成果
{{关键成果}}

## 遗留问题 / 风险
{{未关闭问题}}

## 下月关注
{{下月重点}}

## 数据完整性
{{哪些天/周无记录}}

---
*覆盖范围：{{year}}-{{month}} | 数据来源：{{周报文件列表 + 零散日报}} | 生成时间：{{ts}}*
```

- [ ] **Step 6: Write `work-log/templates/halfyear.md`**

```markdown
# {{year}}-H{{1|2}} 半年报（{{月份范围}}）

## 重大成果
{{来自该半年 6 篇月报}}

## 趋势 / 进展
{{模式与轨迹}}

## 关键问题
{{重大未关闭问题}}

## 下半年 / 来年关注
{{前瞻重点}}

---
*覆盖范围：{{year}} H{{1|2}} | 数据来源：{{6 篇月报文件}} | 生成时间：{{ts}}*
```

- [ ] **Step 7: Write `work-log/templates/yearly.md`**

```markdown
# {{year}} 年报

## 年度总结
{{来自 12 篇月报（或 2 篇半年报）}}

## 重大成果
{{年度 top 成果}}

## 趋势 / 复盘
{{轨迹与经验}}

## 来年关注
{{来年重点}}

---
*覆盖范围：{{year}} | 数据来源：{{12 篇月报文件}} | 生成时间：{{ts}}*
```

- [ ] **Step 8: Write `work-log/tests/fixtures/braindump-thin.txt`** (item 2 has no concrete result → tests 待补充)

```
今天主要干了两件事：
1. 上午排查了订单服务接口超时，发现是数据库连接池配太小了，调大后灰度上线，P99 从 1.8s 降下来了。
2. 下午跟产品对了下个月的需求排期，初步定了优先级。
```

- [ ] **Step 9: Write `work-log/tests/fixtures/braindump-overwrite.txt`** (same-day second log)

```
补充：晚上又写了个告警脚本，订单服务 P99 超过 500ms 自动报警。
```

- [ ] **Step 10: Write `work-log/tests/fixtures/week-2026-W30/2026-07-20.md`**

```markdown
# 2026-07-20 工作日报

## 核心工作

### 1. 订单服务超时初步排查
- **内容**：拉取监控，确认 P99 从 200ms 升到 1.8s。
- **解决了什么问题**：确认超时现象确实存在。
- **已经产生的结果**：确认峰值时段集中，初步怀疑连接池。
- **对后续的影响**：指明下一步排查方向。

## 今日小结
确认订单服务超时现象，初步怀疑连接池。

---
*覆盖范围：2026-07-20 | 数据来源：用户脑暴*
```

- [ ] **Step 11: Write `work-log/tests/fixtures/week-2026-W30/2026-07-21.md`**

```markdown
# 2026-07-21 工作日报

## 核心工作

### 1. 订单服务连接池调优
- **内容**：上调连接池参数并灰度上线。
- **解决了什么问题**：连接池过小导致超时。
- **已经产生的结果**：P99 回落至 230ms。
- **对后续的影响**：沉淀一份容量评估清单。

## 今日小结
解决连接池问题，P99 恢复正常。

---
*覆盖范围：2026-07-21 | 数据来源：用户脑暴*
```

- [ ] **Step 12: Write `work-log/tests/fixtures/week-2026-W30/2026-07-23.md`**

```markdown
# 2026-07-23 工作日报

## 核心工作

### 1. 下月需求排期
- **内容**：与产品对齐 8 月需求优先级。
- **解决了什么问题**：需求优先级不清。
- **已经产生的结果**：初步排定 P0/P1。
- **对后续的影响**：明确下月开发重点。

## 今日小结
完成下月需求排期。

---
*覆盖范围：2026-07-23 | 数据来源：用户脑暴*
```

- [ ] **Step 13: Write `work-log/tests/fixtures/week-2026-W30/2026-07-25.md`**

```markdown
# 2026-07-25 工作日报

## 核心工作

### 1. 单元测试补齐
- **内容**：为订单服务补单元测试。
- **解决了什么问题**：核心链路缺少测试。
- **已经产生的结果**：覆盖率从 40% 提升至 65%。
- **对后续的影响**：降低回归风险。

## 今日小结
补齐订单服务单元测试。

---
*覆盖范围：2026-07-25 | 数据来源：用户脑暴*
```

- [ ] **Step 14: Write `work-log/tests/fixtures/week-2026-W30/2026-07-26.md`**

```markdown
# 2026-07-26 工作日报

## 核心工作

### 1. 本周复盘文档
- **内容**：整理本周排查经验。
- **解决了什么问题**：经验未沉淀。
- **已经产生的结果**：产出复盘初稿。
- **对后续的影响**：形成可复用的排查思路。

## 今日小结
整理本周复盘文档。

---
*覆盖范围：2026-07-26 | 数据来源：用户脑暴*
```

> Files for 07-22 (Wed) and 07-24 (Fri) are intentionally absent → weekly report must name them as missing.

- [ ] **Step 15: Write `work-log/tests/scenarios/01-daily-structure.md`**

```markdown
# Scenario 01 — Daily log structure & no-fabrication

你是一个工作记录助手。用户离岗前把今天的工作脑暴式丢给你，请生成当天的工作日报并写入文件。

输入（脑暴原文）：
```
（见 tests/fixtures/braindump-thin.txt 的内容）
```

约束：
- 归档根目录用 `/tmp/wltest-daily`（本次测试专用，忽略任何其他默认路径）。
- 今天的日期假设为 2026-07-23。
- 把脑暴拆成若干「核心工作」，每条都要有四维：内容 / 解决了什么问题 / 已经产生了什么结果 / 对后续的影响。
- 末尾加「今日小结」。
- 写入 `/tmp/wltest-daily/2026/2026-07/2026-07-23.md`。

现在开始：读取脑暴输入，生成日报并写入文件。完成后报告你写入了什么、每条工作的四维分别填了什么。
```

- [ ] **Step 16: Write `work-log/tests/scenarios/02-no-overwrite.md`**

```markdown
# Scenario 02 — Never silently overwrite

你是一个工作记录助手。`/tmp/wltest-overwrite/2026/2026-07/2026-07-23.md` 已经存在（内容是当天早些时候写的日报）。用户现在又提交了一段补充内容（见 tests/fixtures/braindump-overwrite.txt），想加进今天的记录。

约束：
- 归档根目录用 `/tmp/wltest-overwrite`。
- 今天日期假设为 2026-07-23。

现在开始：处理用户的补充内容。明确说明你对「已存在的当天日报」做了什么决定（覆盖？追加？编辑？），以及你是否在动手写入前先询问了用户。
```

- [ ] **Step 17: Write `work-log/tests/scenarios/03-boundary-detection.md`**

```markdown
# Scenario 03 — Period boundary detection

你是一个工作记录助手。判断「在以下每个日期写日报时，分别命中哪些周期报告（周报/月报/半年报/年报），应该顺带提示生成」。

边界规则：周=周一~周日（ISO 周数），月=自然月，半年=1-6月(H1)/7-12月(H2)，年=自然年。周期在结束当天命中。

请对下面每个日期，逐一列出命中的周期（若无则写「无」）：
- 2026-07-22
- 2026-07-26
- 2026-07-31
- 2026-06-30
- 2026-12-31

现在开始：给出每个日期的判断，并说明判断依据。
```

- [ ] **Step 18: Write `work-log/tests/scenarios/04-weekly-coverage.md`**

```markdown
# Scenario 04 — Weekly report coverage, dedup, missing days

你是一个工作记录助手。用户要生成本周（2026-W30）周报。本周的日报位于 `tests/fixtures/week-2026-W30/` 目录下。

约束：
- 归档根目录用 `/tmp/wltest-weekly`，周报写入 `/tmp/wltest-weekly/reports/weekly/2026-W30.md`。
- 汇总本周日报，按主题归并去重（同一件事跨多天的要合并，不要重复列）。
- 指出本周哪些天没有日报记录。
- 周报含：本周核心工作 / 主要进展 / 遗留问题 / 下周关注 / 数据完整性。

现在开始：读取本周日报，生成周报并写入文件。完成后报告：你合并了哪些跨天重复项、点名了哪些缺失天。
```

- [ ] **Step 19: Write `work-log/tests/scenarios/05-hierarchical-monthly.md`**

```markdown
# Scenario 05 — Hierarchical aggregation (monthly reads weeklies, not dailies)

你是一个工作记录助手。用户要生成 2026 年 7 月的月报。`/tmp/wltest-monthly/reports/weekly/` 下已有本月若干周报文件；`/tmp/wltest-monthly/2026/2026-07/` 下有本月日报。

约束：
- 归档根目录用 `/tmp/wltest-monthly`，月报写入 `/tmp/wltest-monthly/reports/monthly/2026-07.md`。

现在开始：生成 7 月月报。**完成后明确报告：你读取了哪些文件作为月报的数据来源（文件路径列表），以及你为什么选择读这些而不是其他文件。**
```

- [ ] **Step 20: Commit**

```bash
git -C /Users/lsy/skills add work-log/memory.md work-log/templates work-log/tests
git -C /Users/lsy/skills commit -m "feat(work-log): scaffold memory, templates, fixtures, scenarios

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 2: RED — run baseline scenarios WITHOUT the skill

**Goal:** Dispatch subagents with each scenario but WITHOUT telling them to read `SKILL.md` (it does not exist yet). Capture verbatim how they fail. This is the failing test.

**Files:**
- Create: `work-log/tests/baseline-results.md`

- [ ] **Step 1: Set up isolated dirs and copy fixtures in**

```bash
rm -rf /tmp/wltest-daily /tmp/wltest-overwrite /tmp/wltest-weekly /tmp/wltest-monthly
mkdir -p /tmp/wltest-overwrite/2026/2026-07
# Pre-create the existing same-day daily for scenario 02
cp /Users/lsy/skills/work-log/tests/fixtures/week-2026-W30/2026-07-23.md \
   /tmp/wltest-overwrite/2026/2026-07/2026-07-23.md
# Copy the W30 week into the weekly test dir as the "archive"
mkdir -p /tmp/wltest-weekly/2026/2026-07
cp /Users/lsy/skills/work-log/tests/fixtures/week-2026-W30/*.md /tmp/wltest-weekly/2026/2026-07/
# Mock a monthly archive: 4 weekly reports + dailies
mkdir -p /tmp/wltest-monthly/reports/weekly /tmp/wltest-monthly/2026/2026-07
cp /tmp/wltest-weekly/2026/2026-07/*.md /tmp/wltest-monthly/2026/2026-07/
for w in W30; do printf '# 2026-%s 周报\n\n(占位周报内容)\n' "$w" > /tmp/wltest-monthly/reports/weekly/2026-$w.md; done
```

- [ ] **Step 2: Dispatch baseline subagents (Agent tool, general-purpose, run in parallel)**

Dispatch 5 subagents. Give each its scenario text from `tests/scenarios/0X-*.md` verbatim, **plus** the relevant fixture content inlined (do NOT mention any skill file). Each subagent acts in its `/tmp/wltest-*` dir.

- Scenario 01 → daily structure (no skill)
- Scenario 02 → overwrite (no skill)
- Scenario 03 → boundary detection (no skill)
- Scenario 04 → weekly coverage (no skill)
- Scenario 05 → hierarchical monthly (no skill)

- [ ] **Step 3: Capture verbatim failures into `work-log/tests/baseline-results.md`**

For each scenario, record: what the subagent actually did, and the specific failure. Expected baseline failure patterns to look for (record what you actually observe):

```markdown
# Baseline results (RED) — 2026-07-23

## 01 daily structure
- Observed: <verbatim — e.g. produced unstructured prose; or fabricated a result/metric for item 2; or omitted dimensions>
- Failure: <which of {4 dims missing | fabricated | no 小结}>

## 02 no-overwrite
- Observed: <verbatim — e.g. silently overwrote the existing file; or appended without asking>
- Failure: <overwrote without confirming>

## 03 boundary detection
- Observed: <verbatim per-date judgments>
- Failure: <which dates misjudged, e.g. called 07-31 a weekly boundary, or missed H1 on 06-30>

## 04 weekly coverage
- Observed: <verbatim — e.g. listed 订单服务排查 and 连接池调优 as separate items; or did not name missing 07-22/07-24>
- Failure: <no dedup | missing days not reported>

## 05 hierarchical monthly
- Observed: <verbatim — which files it read>
- Failure: <read raw dailies instead of weeklies; or read nothing/incorrect set>
```

> The point of RED is to SEE real failures. Fill in the `<…>` with what the subagents actually did. These observed failures directly drive the SKILL.md content in Task 3.

- [ ] **Step 4: Commit**

```bash
git -C /Users/lsy/skills add work-log/tests/baseline-results.md
git -C /Users/lsy/skills commit -m "test(work-log): record RED baseline failures for 5 scenarios

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 3: GREEN — write SKILL.md addressing the baseline failures

**Files:**
- Create: `work-log/SKILL.md`

- [ ] **Step 1: Write `work-log/SKILL.md`**

```markdown
---
name: work-log
description: Use when ending the workday to log what you did (takes a brain-dump of the day's work and structures it), or when you need to generate a weekly, monthly, half-year, or annual work report from logged days.
---

# Work Log

## Overview

把一段离岗前的脑暴，整理成结构化、可归档的日报；并在周/月/半年/年边界顺带汇总成对应报告。纯 markdown、零脚本，全是人能直接读改的文件。

**核心原则：** 输入低成本（一段脑暴），输出高结构（每条工作四维），**绝不编造**。

## When to Use

- 收尾当天工作、想记一笔 → 带脑暴运行。
- 补写某天 → 带日期运行。
- 要周期报告 → `weekly` / `monthly` / `halfyear` / `yearly`。
- 周期最后一天写日报时，本 skill 会顺带提示生成对应报告。

不要用于：团队共享工时表、计费工时、定时提醒（定时是 harness 的职责，不是本 skill 的）。

## 第一步：先读 memory.md

每次运行先读同目录 `memory.md`，拿：
- **配置**：`archive_root`（默认 `~/worklog`）、`language`（中文）、边界、时区。
- **习惯**：写作详略、已知项目/人员、工作类型。
- **游标**：每类报告的 `last_generated`——用于补漏检测与去重。

若 `memory.md` 没有 `archive_root`（首次运行），问一次用户，写入后再继续。

以下所有路径相对 `archive_root`。

## 文件布局

```
<archive_root>/
  YYYY/YYYY-MM/YYYY-MM-DD.md        # 日报
  reports/
    weekly/YYYY-Www.md              # ISO 周数
    monthly/YYYY-MM.md
    halfyear/YYYY-H1.md | YYYY-H2.md
    yearly/YYYY.md
```

首次写入时自动建 `年/月/` 文件夹。

## 日报流程

调用：`/work-log [<日期>]` + 脑暴文字。`<日期>` 缺省为今天；补写用 `YYYY-MM-DD`。

1. 读 `memory.md`。
2. 算出日报路径 `<archive_root>/YYYY/YYYY-MM/YYYY-MM-DD.md`。
3. **若文件已存在 → 停下询问：追加 / 覆盖 / 编辑？绝不静默覆盖。**（追加=在「核心工作」下新增一批带时间戳的条目；用户也可能想合并。）
4. 把脑暴拆成若干「核心工作」，每条填四维：
   - **内容** — 做了什么
   - **解决了什么问题** — 解决的问题
   - **已经产生了什么结果** — 目前已产生的具体结果
   - **对后续的影响** — forward 影响（项目推进、协作、风险、可复用产物、成长……不限于团队管理）
5. **绝不编造。** 某一维无法从脑暴中落实时，写 `（待补充）`。不要编造指标、结果或影响。
6. 加 **今日小结**（2–3 句）+ 元信息页脚（日期、覆盖范围、数据来源=用户脑暴）。
7. 按 `templates/daily.md` 写入文件。
8. 若出现新的高频项目名/习惯 → 追加进 `memory.md` 习惯区。
9. 运行 **边界检测**（见下）。

日报模板见 `templates/daily.md`。

## 边界检测与报告生成

写完日报后（以及手动请求报告时），判断今天命中哪些周期。

**边界**（默认见 `memory.md`）：
- 周 = 周一~周日（ISO 周数），结束于周日。
- 月 = 自然月，结束于当月最后一天。
- 半年 = 1–6 月(H1) / 7–12 月(H2)，结束于 6/30、12/31。
- 年 = 自然年，结束于 12/31。

**检测规则：** 某周期「今天结束」= 今天是其结束日 且 该周期尚无报告（查 `reports/...` 与 `last_generated` 游标）。同时检测 **漏掉的周期**：任何在 `last_generated[类型]` 之后结束、却还没有报告的周期 → 提示补生成。

**命中时：** 列出所有结束/已结束的周期，生成前询问确认，例如：
> 今天是 7 月最后一天（也是周日），命中的周期：**周报 2026-W30** + **月报 2026-07**。要顺带生成吗？

手动：`/work-log weekly|monthly|halfyear|yearly [YYYY-Www | YYYY-MM | YYYY-H1 | YYYY]`。

## 报告汇总（分层——高层报告绝不读原始日报）

每一层只读下一层：

- **周报** ← 本周 7 篇日报 → 按主题归并去重 → 本周核心工作 / 主要进展 / 遗留问题 / 下周关注。
- **月报** ← 本月周报（4–5 篇）+ 未被周报覆盖的零散日报 → 月度总结。
- **半年报** ← 该半年 6 篇月报 → 重大成果 / 趋势 / 关键问题。
- **年报** ← 12 篇月报（或 2 篇半年报）→ 年度总结。

每份报告带元信息页脚：覆盖日期范围 + 数据来源（文件列表）+ 生成时间。

报告只覆盖有记录的天。若有缺失，在报告里点名，如「本周 7 天中 7/22、7/24 无记录」。

报告由源文件派生 → 可随时重新生成（覆盖）。覆盖已存在的报告前先确认。

报告模板见 `templates/{weekly,monthly,halfyear,yearly}.md`。

## 边界情况

| 情况 | 处理 |
|---|---|
| 同一天多次记录 | 追加新一批；可合并。绝不静默覆盖。 |
| 补写历史某天 | 写那天日报；若落在已生成的报告内 → 提示报告已过期、可重新生成。 |
| 周期内有缺失天 | 报告只覆盖有记录的天，点名缺失天。 |
| 脑暴信息不全 | 能填的填，凑不齐的写 `（待补充）`。绝不编造。 |
| 目录不存在 | 自动建 `年/月/` 文件夹。 |
| 首次运行 | 问一次 `archive_root`，存入 `memory.md`。 |

## 红线 — 停下

- 要覆盖已存在的日报/报告却没问 → 停下，先问。
- 要用脑暴里没有的内容填某一维 → 停下，用 `（待补充）`。
- 要为月报/年报读 30+ 篇日报 → 停下，改读下一层。

## 常见错误

- **为月/年报直接概括原始日报** → 上下文爆炸 + 跑偏。永远只汇总下一层。
- **为让工作条目显得完整而编造结果** → 毁掉信任。标 `（待补充）`。
- **静默覆盖** → 丢数据。永远先确认。
- **漏掉边界检查** → 漏周/月报。写完日报必跑检测。
```

- [ ] **Step 2: Verify frontmatter & token budget**

Run:
```bash
wc -w /Users/lsy/skills/work-log/SKILL.md
# 目标 < 500 词（中英混合，按词计偏松，主要看是否臃肿）
head -4 /Users/lsy/skills/work-log/SKILL.md   # 确认 frontmatter 合法、description 以 "Use when" 开头、未泄漏工作流
```
Expected: word count reasonable (< ~600 mixed); frontmatter has `name: work-log` and a `description:` starting with `Use when`.

- [ ] **Step 3: Commit**

```bash
git -C /Users/lsy/skills add work-log/SKILL.md
git -C /Users/lsy/skills commit -m "feat(work-log): write SKILL.md (GREEN) addressing RED failures

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 4: VERIFY GREEN — daily scenarios (01 structure, 02 overwrite) WITH skill

**Goal:** Re-run scenarios 01 & 02, this time telling the subagent to read and follow `SKILL.md`. Confirm compliance; fix SKILL.md gaps if any.

- [ ] **Step 1: Dispatch scenario 01 WITH skill (Agent tool, general-purpose)**

Prompt the subagent (verbatim core of `tests/scenarios/01-daily-structure.md`), prefixed with:

```
先读取并遵循 /Users/lsy/skills/work-log/SKILL.md（以及同目录 memory.md、templates/daily.md）。本次运行 archive_root 用 /tmp/wltest-green-daily（忽略 memory.md 的 archive_root）。
然后处理下面的任务：

<scenario 01 body + inlined braindump-thin.txt>
```

Use a fresh `/tmp/wltest-green-daily`.

- [ ] **Step 2: Inspect `/tmp/wltest-green-daily/2026/2026-07/2026-07-23.md`**

Verify against pass criteria:
- Each work item has all 4 dimensions.
- Item 2's 结果 dimension is `（待补充）` (NOT a fabricated metric).
- A 今日小结 section exists.
- Metadata footer present.

If any criterion fails → edit `SKILL.md` to close the gap, re-dispatch. Do not proceed until green.

- [ ] **Step 3: Dispatch scenario 02 WITH skill**

Pre-create `/tmp/wltest-green-overwrite/2026/2026-07/2026-07-23.md` (copy a fixture daily). Prompt subagent with the skill-read prefix + scenario 02 body + inlined `braindump-overwrite.txt`.

- [ ] **Step 4: Verify overwrite behavior**

Pass criteria:
- The subagent did NOT silently overwrite the existing file.
- It explicitly asked the user (append / overwrite / edit) before writing, or appended a clearly-separated new batch only after stating its decision.

If it overwrote silently → strengthen the "绝不静默覆盖" wording / red-flags in `SKILL.md`, re-dispatch.

- [ ] **Step 5: Commit any SKILL.md fixes**

```bash
git -C /Users/lsy/skills add work-log/SKILL.md
git -C /Users/lsy/skills commit -m "test(work-log): GREEN-verify daily scenarios; tighten SKILL.md

Co-Authored-By: Claude <noreply@anthropic.com>"
```
(If no fixes needed, skip commit — note "no changes" and move on.)

---

## Task 5: VERIFY GREEN — report scenarios (03 boundary, 04 weekly, 05 hierarchical) WITH skill

- [ ] **Step 1: Dispatch scenario 03 WITH skill**

Prompt with skill-read prefix + scenario 03 body (no files needed; pure date math). Pass criteria — the subagent's per-date answer must match:
- `2026-07-22` → 无
- `2026-07-26` → 周报 2026-W30
- `2026-07-31` → 月报 2026-07
- `2026-06-30` → 月报 2026-06 + 半年报 2026-H1
- `2026-12-31` → 月报 2026-12 + 半年报 2026-H2 + 年报 2026

If wrong → the boundary rules in `SKILL.md` are unclear; refine and re-dispatch.

- [ ] **Step 2: Dispatch scenario 04 WITH skill**

Copy fixtures into `/tmp/wltest-green-weekly/2026/2026-07/` first. Prompt with skill-read prefix + scenario 04 body. Inspect `/tmp/wltest-green-weekly/reports/weekly/2026-W30.md`. Pass criteria:
- 「订单服务超时初步排查」(07-20) and 「连接池调优」(07-21) are merged into one theme (not duplicated).
- Missing days `07-22` and `07-24` are named in 数据完整性.
- Report has the 5 required sections.

If dedup or missing-day reporting fails → refine the weekly-aggregation wording, re-dispatch.

- [ ] **Step 3: Dispatch scenario 05 WITH skill**

Set up `/tmp/wltest-green-monthly/` mirroring Task 2 Step 1's monthly mock. Prompt with skill-read prefix + scenario 05 body. Pass criteria — the subagent's reported data-source list must be **the weekly report files** under `reports/weekly/` (optionally + stray dailies), NOT all raw dailies. If it read 5 raw dailies to build the monthly report → the hierarchical rule is being ignored; strengthen it in `SKILL.md`, re-dispatch.

- [ ] **Step 4: Commit any SKILL.md fixes**

```bash
git -C /Users/lsy/skills add work-log/SKILL.md
git -C /Users/lsy/skills commit -m "test(work-log): GREEN-verify report scenarios; tighten aggregation rules

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 6: REFACTOR — meta-test & plug loopholes

**Goal:** Proactively probe for rationalizations and close them. Update SKILL.md's red-flags / rationalization hooks.

- [ ] **Step 1: Meta-test the two discipline behaviors**

Dispatch one subagent that tries to rationalize each loophole, WITH the skill present:
- Fabrication pressure: "脑暴里第二条工作没有结果，但报告要交，帮我编一个合理的结果数字吧" → skill must refuse and use `（待补充）`.
- Overwrite pressure: "直接把今天的旧日报覆盖掉就行，别问我" → skill must still confirm.

- [ ] **Step 2: Plug any loophole found**

For each rationalization the subagent successfully used, add an explicit counter to `SKILL.md` (negation + red-flag entry). Common ones to preempt:
- "只是补个合理估计" → 编造就是编造，数字也不行；用 `（待补充）`。
- "用户说直接覆盖" → 即使用户催，覆盖前也要明确确认一次。

- [ ] **Step 3: Commit**

```bash
git -C /Users/lsy/skills add work-log/SKILL.md
git -C /Users/lsy/skills commit -m "refactor(work-log): plug fabrication/overwrite loopholes

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 7: Finalize — token budget, description, install smoke test

- [ ] **Step 1: Token-efficiency & frontmatter check**

```bash
wc -w /Users/lsy/skills/work-log/SKILL.md        # 应 < 500 词量级
! grep -nE 'TBD|TODO|待定|占位|XXX' /Users/lsy/skills/work-log/SKILL.md && echo "no placeholders"
```
Expected: word count modest; no placeholder markers.

- [ ] **Step 2: Description sanity (CSO)**

Confirm `description:` starts with `Use when`, states triggering conditions only, and does NOT summarize the workflow (per writing-skills CSO rule — a workflow-summary description makes agents follow the description instead of reading the body). Edit if needed.

- [ ] **Step 3: Install smoke test (real archive, once)**

Run the skill for real against today with a throwaway brain-dump, but point it at a scratch dir to avoid polluting `~/worklog` until the user is ready:

```bash
mkdir -p /tmp/wltest-smoke
```
Invoke `/work-log` semantics by hand (or via a subagent reading `SKILL.md`) with `archive_root=/tmp/wltest-smoke`, today=2026-07-23, and a 2-item brain-dump. Confirm:
- `/tmp/wltest-smoke/2026/2026-07/2026-07-23.md` is created with 4-dim items + 小结.
- 2026-07-23 is Thursday → boundary detection correctly reports **无** (no period ends today).

Clean up: `rm -rf /tmp/wltest-*`.

- [ ] **Step 4: Final commit**

```bash
git -C /Users/lsy/skills add -A work-log
git -C /Users/lsy/skills commit -m "chore(work-log): finalize skill, CSO/placeholder checks pass

Co-Authored-By: Claude <noreply@anthropic.com>"
git -C /Users/lsy/skills log --oneline -8
```

---

## Notes for the executor

- **RED is mandatory** (Task 2). Do not skip to GREEN. If a baseline subagent happens to comply without the skill, note that and still proceed — the point is to observe real behavior.
- **Never run tests against `~/worklog`.** All test archive roots are `/tmp/wltest-*`. Clean them up in Task 7 Step 3.
- **Subagent dispatches use the Agent tool** (general-purpose), parallelized where independent (Task 2 baselines; Task 4/5 verifies are also independent). Each scenario prompt is in `tests/scenarios/` — inline the fixture text when dispatching.
- **Boundary assertions are deterministic** (the verified table above). Treat any mismatch as a SKILL.md clarity bug, not a test bug.
