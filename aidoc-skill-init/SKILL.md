---
name: aidoc-skill-init
description: 扫描代码仓中可封装为 skill 的自动化能力，生成领域能力目录（docs/skills/）。依赖阶段 0-3 产出的 AGENTS.md 和 ARCHITECTURE.md。由 aidoc-build 阶段 4 触发，也可独立使用。
---

# 领域能力目录初始化

## 概览

在阶段 0-3 产出的结构文档基础上，构建领域能力目录（`docs/skills/`），将代码仓中可复用的自动化操作封装为 skill。

## 前置条件

- `.aidoc/phase0/repo-profile.md` 必须存在
- 根目录 AGENTS.md 和各模块 AGENTS.md 应已生成
- `docs/ARCHITECTURE.md` 应已生成

## 工作流程

### 步骤 1：候选检测

扫描 repo 中可封装为 skill 的自动化能力：

1. **从 `scripts/` 检测**：
   - 列出所有脚本文件（`.sh`、`.py`、`.ts` 等）
   - 单脚本 + 独立用途 → 一个 skill
   - 多脚本 + 共同主题 → 一个 skill + `scripts/` 目录引用多个脚本
2. **从 AGENTS.md 检测**：搜索"自动"、"生成"、"触发"、"skill"等关键词，识别已有的工作流描述
3. **从 Makefile / package.json scripts 检测**：`make deploy`、`npm run migrate` 等非构建命令

### 步骤 2：生成

- 有明确候选 → 创建 `docs/skills/<skill-name>/SKILL.md`，使用 `templates/skill.tmpl.md`
- 无明确候选 → 仅创建 `docs/skills/AGENTS.md`（使用 `templates/skills-readme.tmpl.md`），说明 skill 概念和封装时机
- 每个 skill 的 YAML frontmatter 中 `description` 是触发关键：写明"用户说什么话时触发"

### 步骤 3：回写入口文件

领域能力目录的索引必须可被发现——Agent 不会主动探索未知目录。用户确认后，将索引引用**写回根 AGENTS.md**（若已存在则更新）：

```markdown
## 领域能力 [~ 推断]

- **领域能力**：`docs/skills/AGENTS.md` — 可复用自动化操作（{N} 个 skill）

> 遇到"执行 X 操作"→ 查 docs/skills/。
```

## 生成后

1. 展示完整的目录结构概览供审阅：
   ```
   📦 领域能力目录已生成：

   docs/skills/
   └── ...（{N} 个 skill）
   ```
2. 确认重点：
   - "检测到的 skill 候选是否遗漏？"
3. 用户确认后，将完成报告写入 `.aidoc/phase4a/report.md`：

```markdown
# 阶段 4a 完成报告

## 生成结果
- docs/skills/：{N} 个 skill 目录 / 占位说明
- 生成时间：{时间戳}

## 目录骨架清单
| 路径 | 类型 | 状态 |
|------|------|------|
| docs/skills/xxx/SKILL.md | skill | ✓ |

## 待人工补充
{汇总所有 HUMAN_REVIEW 标记}
```

## 幂等性

如果目标路径已存在文件：
- 不要静默覆盖
- 展示现有文件与生成内容的差异
- 让用户选择：保留现有、合并或替换
