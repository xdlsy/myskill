---
name: aidoc-adapt-claude
description: 用于将 aidoc 文档体系适配为 Claude Code 原生加载结构。触发场景：(1) aidoc-build 完成后的收尾阶段，(2) 已有 AGENTS.md 需要接通 Claude Code 加载链，(3) 用户要求"适配 Claude Code"、"配置 Claude 规则"、(4) 需要将 aidoc-learning 的 activator.sh 注册为 Hook。
---

# Aidoc 适配 Claude Code

## 概览

将 aidoc 文档体系适配为 Claude Code 原生加载结构，做四件事：

1. 生成 `CLAUDE.md` 入口桥接文件（指向 `AGENTS.md`）
2. 生成 `.claude/rules/` 路径作用域规则（按模块引用对应的 `AGENTS.md`）
3. 创建 `.claude/skills/` 软链接（→ `docs/skills/`），使项目级 skills 可被 Claude Code 原生发现
4. 配置 `aidoc-learning` 的 `activator.sh` 为 `UserPromptSubmit` Hook

**前置条件：** 项目根目录已有 `AGENTS.md`（由 `aidoc-build` 生成或手动编写）。

## 工作流程

### 步骤 1：生成 CLAUDE.md 桥接

`CLAUDE.md` 是 Claude Code 在项目中的入口指令文件。这里不复制内容，只做一级指针：

| 现有状态 | 操作 |
|---|---|
| 无 `CLAUDE.md` | 创建单行文件，内容为 `@AGENTS.md` |
| `CLAUDE.md` 存在，但无 `@AGENTS.md` 引用 | 在末尾追加一行 `@AGENTS.md` |
| `CLAUDE.md` 已包含 `@AGENTS.md` | 跳过，无需变更 |

**铁律：绝不覆盖已有 CLAUDE.md** — 只做创建或追加。

### 步骤 2：生成 .claude/rules/ 规则

Claude Code 的 rules 机制通过 `paths:` frontmatter 实现路径作用域加载——只有当操作的文件匹配 glob 模式时，对应规则才会注入上下文。

#### 2.1 全局规则（3 个文件，内容自包含）

这些规则跨模块生效，因此直接展开内容，不做 @-import。

**global-style.md** — 路径作用域到源码文件：

```markdown
---
paths: ["**/*.java", "**/*.py"]
---

# 代码风格

{{从 codebase-profile.json 或根 AGENTS.md 展开的代码风格规则}}
```

`paths` 推导规则：Java → `**/*.java`，Python → `**/*.py`，Go → `**/*.go`，多语言则合并所有 pattern。

**global-testing.md** — 路径作用域到测试文件：

```markdown
---
paths: ["**/*Test.java", "**/test_*.py", "**/*_test.py", "tests/**"]
---

# 测试指南

- 框架：{{测试框架名称}}
- 运行命令：`{{测试命令}}`
- 测试目录：{{测试目录列表}}
```

`paths` 推导规则：Java → `**/*Test.java`，Python → `**/test_*.py` + `tests/**`，Go → `**/*_test.go`。

**architecture.md** — 全局不变式，始终加载（`paths: []`）：

```markdown
---
paths: []
---

# 架构不变式

{{从根 AGENTS.md "禁止事项/常见陷阱" 章节提取的约束}}

<!-- HUMAN_REVIEW: 补充代码仓特定的架构规则 -->
```

#### 2.2 模块索引规则

为每个包含 `AGENTS.md` 的子模块创建单行规则文件：

```markdown
---
paths: ["{{模块路径}}/**"]
---

@{{模块路径}}AGENTS.md
```

**约束：**
- 模块规则 ≤15 行（主要是 YAML frontmatter）
- 不复制 AGENTS.md 内容 — 仅用 `@` 语法导入
- 跳过没有 AGENTS.md 的模块
- 如果 `.claude/rules/<module>.md` 已存在，展示 diff 让用户选择保留/合并/替换

### 步骤 3：Skills 符号链接

`docs/skills/` 存放项目级可复用能力（由 `aidoc-skill-init` 生成）。Claude Code 原生从 `.claude/skills/` 加载 skills，因此创建软链接使其可被发现：

```bash
ln -s ../docs/skills .claude/skills
```

| 当前状态 | 操作 |
|---|---|
| `.claude/skills` 不存在 | 创建软链接 `ln -s ../docs/skills .claude/skills` |
| 已存在且指向 `docs/skills/` | 跳过 |
| 已存在但指向其他位置 | 展示当前目标，让用户选择替换/保留 |

**注意：** 使用相对路径 `../docs/skills`，确保链接在任意 clone 位置均有效。

### 步骤 4：配置 aidoc-learning Hook

让 `aidoc-learning` 的 `activator.sh` 在每次用户输入后自动触发，提醒 Claude 在任务完成后评估是否有可提取的知识。

#### 3.1 部署 activator.sh 到项目本地

```bash
mkdir -p .claude/scripts/aidoc-learning
cp ~/.claude/skills/aidoc-learning/scripts/activator.sh .claude/scripts/aidoc-learning/
chmod +x .claude/scripts/aidoc-learning/activator.sh
```

如果目标文件已存在且内容相同则跳过。

#### 3.2 注册 Hook 到 settings.json

目标配置：

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/scripts/aidoc-learning/activator.sh"
          }
        ]
      }
    ]
  }
}
```

合并策略（逐级判断，保留所有现有配置）：

| 当前状态 | 操作 |
|---|---|
| `settings.json` 不存在 | 创建新文件，仅含 hook 配置 |
| 存在但无 `hooks` 键 | 在顶层加入 `hooks` 配置 |
| 有 `hooks` 但无 `UserPromptSubmit` | 在 `hooks` 对象中追加 `UserPromptSubmit` 数组 |
| `UserPromptSubmit` 存在但无对应 matcher | 追加新的 matcher 条目 |
| 完全匹配 | 跳过 |

**注意：** `settings.json` 可能包含 `permissions`、`additionalDirectories` 等其他顶层键，合并时全部保留。

### 步骤 5：交叉验证

确认规则与 AGENTS.md 一一对应，无遗漏：

```bash
# 列出所有源码模块 AGENTS.md（排除 docs/ 和 .aidoc/）
find . -name "AGENTS.md" -not -path "./.git/*" -not -path "./.aidoc/*" -not -path "./docs/*" | sort

# 列出所有模块规则文件
ls .claude/rules/*.md | sort
```

验证要点：
- 每个源码模块 AGENTS.md 必须有对应的 `.claude/rules/<name>.md`
- `CLAUDE.md` 内容为 `@AGENTS.md` 且仅此一行
- `settings.json` 中 `UserPromptSubmit` hook 指向 `activator.sh`
- 全局规则 3 个文件齐全（global-style / global-testing / architecture）
- 所有模块规则 ≤15 行，仅含 frontmatter + 单行 @-import

### 步骤 6：写入完成报告

创建 `mkdir -p .aidoc/phase5 &&` 写入 `.aidoc/phase5/report.md`：

```markdown
# 阶段 5 完成报告

## 生成结果
- `CLAUDE.md`：[已创建 / 已追加 / 无变更]
- `.claude/rules/`：{N} 个规则文件（3 全局 + {M} 模块）
- `.claude/skills/`：软链接 → `docs/skills/` [已创建 / 已存在]
- `.claude/scripts/aidoc-learning/`：已部署 `activator.sh`
- `.claude/settings.json`：`UserPromptSubmit` Hook [已配置 / 已存在 / 无变更]
- 生成时间：{时间戳}

## 文件清单

| 路径 | 类型 | 状态 |
|------|------|------|
| `CLAUDE.md` | 入口桥接 | ✓ |
| `.claude/rules/architecture.md` | 全局规则（始终加载） | ✓ |
| `.claude/rules/global-style.md` | 全局规则（`paths` 含源码文件） | ✓ |
| `.claude/rules/global-testing.md` | 全局规则（`paths` 含测试文件） | ✓ |
| `.claude/rules/<module1>.md` | 模块规则 → `<path>/AGENTS.md` | ✓ |
| ... | ... | ... |
| `.claude/skills/` | 软链接 → `docs/skills/` | ✓ |
| `.claude/scripts/aidoc-learning/activator.sh` | Hook 脚本 | ✓ |
| `.claude/settings.json` | UserPromptSubmit Hook | ✓ |

## 交叉验证

- AGENTS.md 文件总数（源码模块）：{N}
- 模块规则覆盖率：{M}/{N}（{百分比}%）
- 全局规则：3（style / testing / architecture）
- Hook 配置：`UserPromptSubmit` → `activator.sh`

## 待人工补充

{汇总所有 HUMAN_REVIEW 标记所在的文件}
```

**注意：** 展示树形一览给用户确认后，再写入报告文件。若 `.aidoc/phase5/report.md` 已存在，展示 diff 让用户选择保留/合并/替换。

## 幂等性

| 产物 | 策略 |
|------|------|
| `CLAUDE.md` | 绝不覆盖；仅创建或追加 |
| `.claude/rules/global-*.md` | 存在则展示 diff，让用户选择保留/合并/替换 |
| `.claude/rules/<module>.md` | 同上 |
| `.claude/skills/` 软链接 | 已存在且指向正确则跳过；指向错误则展示当前目标让用户选择 |
| `activator.sh` | 内容相同则跳过 |
| `settings.json` hook | 已配置则跳过 |

## 文件约束

| 文件 | 最大行数 | 内容 |
|------|---------|------|
| CLAUDE.md | 1 | `@AGENTS.md` 仅此一行 |
| global-style.md | 30-50 | 自包含，来自 codebase profile |
| global-testing.md | 20-30 | 自包含，来自 codebase profile |
| architecture.md | 20-40 | 自包含不变式 |
| 模块规则 .md | ≤15 | Frontmatter + 单行 @-import |

## 设计原则

- **AGENTS.md 是唯一真相源。** 规则不复制内容 — 它们只做 `@-import`。
- **全局规则自包含** 因为它们跨模块适用，没有单一 AGENTS.md 可导入。
- **不做按模块的 CLAUDE.md** — 通过 `.claude/rules/` + `paths:` 达到相同效果，且更精准（只在操作对应模块文件时才加载）。
- **`paths: []` 表示"始终加载"** — 仅用于架构不变式这类全局约束。
- **Skills 通过软链接暴露** — `docs/skills/` 是版本控制真相源，`.claude/skills/` 通过相对软链接指向它，Claude Code 原生发现而无需 `additionalDirectories` 配置。
- **Hook 脚本部署到项目本地** — 确保团队成员共享相同配置，不依赖个人环境。
