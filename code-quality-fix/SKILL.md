---
name: code-quality-fix
version: "1.1.0"
description: 代码质量扫描与AI自动修复。触发短语："代码扫描"、"扫描修复"、"code scan"、"code quality"、"安全扫描"、"质量修复"
---

# Code Quality Fix

扫描项目的安全与质量问题，然后修复。修复由你（Claude）直接完成 —— 不要调任何外部 LLM API。

## 何时使用
- 提交前检查安全/质量问题
- 清理积累的质量债
- 修复安全评审发现的问题

## 入参
`/code-quality-fix [选项]`。选项：
- `--scan-only` : 只扫描展示报告，不修复（修复是默认行为）
- `--no-commit` : 修复但只留在工作区，不提交
- `--category <security|quality|style>` : 只修一类
- `--severity <HIGH|MEDIUM|LOW>` : 只修该级别及以上
- `--lang <go|java|python>` : 只扫描一种语言
- `--max-issues <n>` : 本次最多修复的问题数（可选；默认**不限制=修全部**）。仅当想限定规模时传入，按严重度降序取前 n 个；超过分发阈值（15）的修复仍走子代理并行，见步骤 5/6
- `--dry-run` : 只提建议不写文件
- `--skip-test` : 跳过测试验证步骤
- `--install-tools` : 安装缺失扫描器

若用户未带任何选项，用 AskUserQuestion 询问意图：
1. 仅扫描（== --scan-only）
2. 扫描并全部修复（默认）
3. 只修安全（== --category security）
4. 只修高危（== --severity HIGH）

## 前置条件
- Python 3.8+ 运行 scan.py（路径：~/.claude/skills/code-quality-fix/scripts/scan.py）
- 目标项目最好有测试（否则用 --skip-test）

## 步骤

### 1. 解析意图
若未给选项，用 AskUserQuestion 询问（见入参）。把答案映射为对应选项。确定项目根（当前工作目录，除非用户指明）。

### 2. 检查并安装工具
运行：
```bash
python3 ~/.claude/skills/code-quality-fix/scripts/scan.py --check-tools
```
若检测到的语言所需的某工具 `"installed": false`，列出并用 AskUserQuestion 询问是否安装。若同意：
```bash
python3 ~/.claude/skills/code-quality-fix/scripts/scan.py --install-tools
```
即使部分工具仍缺失也继续 —— scan.py 会跑已装的那些。

### 3. 扫描
确保 `.tmp/code-quality-fix/` 存在（创建之），并把 `.tmp/` 加入项目 `.gitignore`（若未加）。运行：
```bash
python3 ~/.claude/skills/code-quality-fix/scripts/scan.py \
  --project <project_root> \
  --output <project_root>/.tmp/code-quality-fix/report.json \
  [--lang L] [--category C] [--severity S]
```
读取 `.tmp/code-quality-fix/report.json`。

### 4. 展示扫描摘要
打印精简摘要：总问题数，按严重度/类别/语言拆分（用 `summary` 块）。若 `--scan-only`，到此为止。

### 5. 准备修复
- 读 issues 列表，过滤掉 `fixable: false` 的（标记 `needs_manual`，不进入修复）。
- **跳过已知误报**（这些 `fixable:true` 但自动改会破坏代码，必须排除并记入「需人工」）：
  - bandit **B101**（`assert` 用法）出现在测试文件（`test_*.py` / `*_test.py`）里 —— pytest 以 `assert` 为惯用断言，**不要改写**。
- 统计可修问题数 `N`，按分发阈值 **15** 决定修复路径（**不要逐条问用户**）：
  - **`N ≤ 15`：** 本对话直接修全部 `N` 个（步骤 6「路径 A」）。
  - **`N > 15`：** **不截断**，按文件分区并行派子代理修全部（步骤 6「路径 B」）。分区规则：同一文件的所有问题 = 一批；单批超过 15 再按行号均分，每批 ≤ 15 个。
- 若用户**显式**传了 `--max-issues <n>`：先按严重度降序把可修问题截到前 `n` 个，再套用上面的路径选择（`n ≤ 15` 走 A，否则走 B）。
- 收集「实际要改的文件集合」（分区后所有批次涉及的文件，或被 `--max-issues` 截断后的子集）。
- 编辑前先建备份快照（只备份实际要改的文件 —— 若 report.json 含未修问题，先把「实际要修的 issues」写到一个临时 report 再传给 `--backup`）：
```bash
TS=$(date +%Y%m%d-%H%M%S)
python3 ~/.claude/skills/code-quality-fix/scripts/scan.py \
  --backup <project_root>/.tmp/code-quality-fix/report.json \
  --backup-root <project_root>/.tmp/code-quality-fix/backups \
  --backup-id "$TS"
```
记住 `$TS` 以便回滚。

### 6. 修复
按步骤 5 选定的路径执行（**不要逐条问用户**）：

- **路径 A：本对话直接修（`N ≤ 15`）。** 按严重度降序，单文件内从最后一行往第一行改（保证较早的行号仍然有效）：
  1. 读 `prompts/{category}.md` 作为指导（Read 工具）。
  2. 读 `{line}` 附近的源码（Read 工具）。
  3. 用 Edit 工具应用修复。diff 对用户可见。
  若修复引入可见的语法错误，换思路重试一次；仍失败则跳过并标 `needs_manual`。

- **路径 B：分发子代理并行修（`N > 15`，不截断）。** 按步骤 5 的分区，每批派一个子代理（Agent 工具，general-purpose）。**在一条消息里并行派发所有批次**（多个 Agent 调用），不要串行等待。每个子代理的 prompt 至少包含：
  - 该批问题清单：`{id, file, line, rule_id, message, category, severity}`，
  - 「读 `~/.claude/skills/code-quality-fix/prompts/{category}.md` 作指导；跳过 `fixable:false` 与已知误报（如测试文件里的 bandit B101）」，
  - 「用 Edit 修复，同一文件内从最后一行往第一行改，保证行号有效」，
  - 「不要跑测试，不要提交，不要碰本批之外的文件」，
  - 「只返回精简摘要：`{id, status: fixed|needs_manual|failed, 一句话描述}` 列表」。
  收集所有子代理的摘要，合并成总结果。**测试由你在步骤 7 统一跑一次**，子代理不跑测试。

### 7. 验证（所有修复完成后统一跑一次测试）
检测适用测试命令：
```bash
python3 ~/.claude/skills/code-quality-fix/scripts/scan.py --detect-tests --project <project_root>
```
运行列出的每条测试命令（Bash）。若 `--skip-test`，跳到步骤 8。

- **全部通过：** 进步骤 8。
- **任一失败：** 做正向定位：
  1. 还原干净快照：`scan.py --restore --backup-root ... --backup-id "$TS" --project <root>`。
  2. 正向重新应用修复（按严重度顺序），每应用一组后跑测试，二分定位罪魁：
     - 路径 B（多批次）先按**批次（文件）**二分：先应用一半批次跑测试，缩小到出问题的批次；再在该批次内**逐条**二分。
     - 路径 A 直接逐条二分。
     第一条让套件变红的即罪魁。
  3. 回滚该罪魁。重修一次，附加失败上下文："上次修复导致测试失败：<错误>。请换种方法修复。"
  4. 重跑测试。若仍红，标 `needs_manual`，保持回滚，继续重新应用其余修复。
  记录哪些修复最终应用、哪些跳过。

### 8. 生成临时报告
写 `<project_root>/.tmp/code-quality-fix/fix-report-{TS}.md`，包含：
- 扫描摘要，
- 每条修复结果（已修复 / 重试后修复 / 需人工 / 失败），各带一行描述和 文件:行号，
- 测试结果（命令 + 通过/失败 + 耗时），
- 剩余未修复问题（`needs_manual` / 失败 / 被 `--max-issues` 截断的），各带原因。

### 9. 确认并提交
向用户展示报告。用 AskUserQuestion：接受全部修复，或拒绝。

- **接受：** 删除临时报告文件，然后提交：
```bash
cd <project_root>
git add -A
git commit -m "fix(code-quality): auto-fix N issues (security/quality)

<每类别一行摘要>"
```
  （若 `--no-commit`，跳过提交，改动留在工作区。）
- **拒绝：** 还原干净快照（`scan.py --restore ...`），删除临时报告，不提交。告知用户树已还原。

### 10. 报告剩余
告知用户剩余问题（默认已修全部可修项，剩余多为 `needs_manual` 误报或业务逻辑相关）。建议：误报可在报告里加 `# noqa`/注释说明后忽略；业务逻辑相关项交人工。仅当用户**显式**用了 `--max-issues <n>` 截断时，才提示「再运行 `/code-quality-fix` 继续」。

## 常见问题
- **没装工具：** 先运行 `/code-quality-fix --install-tools`。
- **某语言测试慢（mvn）：** 属正常；那一次测试是验证的成本。
- **修复反复导致测试失败：** 问题可能涉及工具推断不出的业务逻辑 —— 会标 `needs_manual` 交人工。
- **项目无测试：** 用 `--skip-test`；修复不经验证直接应用。
- **问题很多（>15）会怎样：** 自动按文件分区、并行派子代理修复**全部**可修项（不在本对话逐条改、也不截断）；子代理只改文件、不跑测试，测试由主流程在步骤 7 统一验证。
