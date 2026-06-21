---
name: dockit-opencode
description: 将 dockit 文档体系适配为 OpenCode 原生加载结构。触发场景：(1) dockit-init 完成后的收尾阶段，(2) 已有 AGENTS.md 需要接通 OpenCode 配置，(3) 用户要求"适配 OpenCode"、"配置 OpenCode"，(4) 需要将 dockit-learning 注册为 OpenCode 插件。
---

# Dockit 适配 OpenCode

将 dockit 文档体系适配为 OpenCode 原生加载结构，做两件事：

1. 验证 `AGENTS.md` 入口文件（OpenCode 原生读取，无需桥接）
2. 配置 `dockit-learning` 为 OpenCode TypeScript 插件（`.opencode/plugins/`）

**前置条件：** 项目根目录已有 `AGENTS.md`（由 `dockit-init` 生成或手动编写），且已运行 `dockit-claude`（创建 `.claude/skills/` 软链接，OpenCode 通过 `~/.claude/skills/` 路径发现 skills）。

## 工作流程

### 步骤 1：验证 AGENTS.md 入口

OpenCode 原生读取 `AGENTS.md` 作为最高优先级指令文件（优先级高于 `CLAUDE.md`），无需创建桥接文件。

| 现有状态 | 操作 |
|---|---|
| `AGENTS.md` 存在于项目根目录 | ✅ 无需操作 |
| `AGENTS.md` 不存在 | 报错终止：前置条件不满足，需先运行 `dockit-init` |

**与 Claude Code 版的区别：** Claude Code 需要生成 `CLAUDE.md` 桥接文件（`@AGENTS.md`），OpenCode 不需要这一步。

### 步骤 2：配置 dockit-learning 插件

使用 OpenCode 的 TypeScript 插件机制（`.opencode/plugins/`），通过 `tui.prompt.append` 事件钩子注入 learning 提醒。这是 Claude Code 的 `UserPromptSubmit` shell hook 的 OpenCode 等价方案。

#### 2.1 创建插件文件

文件：`.opencode/plugins/dockit-learning.ts`

```typescript
export const DockitLearningPlugin = async ({ project, client, $, directory, worktree }) => {
  return {
    "tui.prompt.append": async (input, output) => {
      output.content = `
<self-improving-reminder>
完成此任务后，评估是否出现了可提取的知识：
- 通过调查发现了非显而易见的解决方案？
- 为意外行为找到了变通方案？
- 学到了项目特定的模式？
- 错误需要通过调试才能解决？

如果有：按照学习改进技能的格式记录到 docs/learnings/。
如果价值高（重复出现、广泛适用）：考虑技能提取。
</self-improving-reminder>`
    },
  }
}
```

插件 API 参考（来自 OpenCode 官方文档 https://opencode.ai/docs/plugins/）：
- 插件目录：`.opencode/plugins/`（项目级）、`~/.config/opencode/plugins/`（全局）
- 导出：`async ({ project, client, $, directory, worktree }) => { return { /* hooks */ } }`
- 可用事件：`tui.prompt.append`、`session.created`、`tool.execute.before`、`tool.execute.after`、`file.edited` 等

合并策略：

| 当前状态 | 操作 |
|---|---|
| `.opencode/plugins/` 目录不存在 | 创建目录和插件文件 |
| 插件文件不存在 | 创建 |
| 内容相同 | 跳过 |
| 内容不同 | 展示 diff，让用户选择保留/合并/替换 |

### 步骤 3：交叉验证

确认所有产物正确生成：

```bash
# 1. 根 AGENTS.md 存在（前置条件）
test -f AGENTS.md && echo "OK" || echo "MISSING"

# 2. Skills 可发现（通过 ~/.claude/skills/ 路径）
for dir in docs/skills/*/; do
  name=$(basename "$dir")
  if [ -f "$dir/SKILL.md" ]; then
    head -5 "$dir/SKILL.md" | grep -q "^name:" && echo "OK: $name" || echo "NO FRONTMATTER: $name"
  fi
done

# 3. 插件文件存在
test -f .opencode/plugins/dockit-learning.ts && echo "OK" || echo "MISSING"
```

验证要点：
- `AGENTS.md` 存在于项目根目录
- `.claude/skills/` 软链接存在（由 `dockit-claude` 创建）
- 所有 `docs/skills/*/SKILL.md` 都有合规的 YAML frontmatter
- `.opencode/plugins/dockit-learning.ts` 存在
- 与 `.claude/` 目录下 Claude Code 配置无冲突（两套可共存）

### 步骤 4：写入完成报告

创建 `mkdir -p .dockit/phase5 &&` 写入 `.dockit/phase5/opencode-report.md`（与 Claude 版的 `report.md` 分开，避免覆盖）：

```markdown
# 阶段 5 完成报告 -- OpenCode 适配

## 生成结果
- `AGENTS.md` 入口：[原生读取 / N/A -- OpenCode 原生读取]
- Skills 发现路径：`~/.claude/skills/`（由 `dockit-claude` 配置，{N} 个 skills 可发现）
- Skills frontmatter 合规：{M}/{T}（{P} 已修复）
- `.opencode/plugins/dockit-learning.ts`：[已创建 / 已存在]
- 生成时间：{时间戳}

## 文件清单

| 路径 | 类型 | 状态 |
|------|------|------|
| `AGENTS.md` | 入口文件（原生读取） | ✓ |
| `.claude/skills/` | Skills 软链接（由 dockit-claude 创建） | ✓ |
| `.opencode/plugins/dockit-learning.ts` | Learning 插件 | [已创建/已存在] |

## 交叉验证
- `AGENTS.md` 文件存在：是/否
- `.claude/skills/` 软链接存在：是/否
- Skills frontmatter 合规：{M}/{T}
- 插件已配置：是/否
- 与 Claude Code 配置共存：是/否

## 待人工补充
{汇总所有 HUMAN_REVIEW 标记所在的文件}
```

**注意：** 展示树形一览给用户确认后，再写入报告文件。若 `.dockit/phase5/opencode-report.md` 已存在，展示 diff 让用户选择保留/合并/替换。

## 幂等性

| 产物 | 策略 |
|------|------|
| `AGENTS.md` 验证 | 只读，始终安全 |
| Skills frontmatter 校验 | 只读校验；修复时原地修复（不破坏正文） |
| `.opencode/plugins/dockit-learning.ts` | 内容相同跳过；不同展示 diff |
| 报告文件 | 存在则展示 diff，让用户选择 |

## 文件约束

| 文件 | 最大行数 | 内容 |
|------|---------|------|
| `.opencode/plugins/dockit-learning.ts` | ~20 | TypeScript 插件 |

## 设计原则

- **AGENTS.md 是唯一真相源。** OpenCode 原生读取 AGENTS.md，无需额外配置文件桥接。
- **Skills 复用 Claude Code 配置。** OpenCode 通过 `~/.claude/skills/` 路径发现 skills，与 `dockit-claude` 共享同一套软链接，无需重复配置。
- **TypeScript 插件。** 用 OpenCode 原生插件机制（`tui.prompt.append`），不依赖 shell hook。
- **双工具链共存。** `.claude/`（Claude Code）和 `.opencode/`（OpenCode）独立运行，报告文件分开存放。
