---
name: aidoc-learnings-init
description: 为代码仓初始化经验库（docs/learnings/），包含 LEARNINGS.md、ERRORS.md、FEATURE_REQUESTS.md。从已有文档中提取可沉淀的经验，初始化后启用持续记录工作流（配套 aidoc-learning）。依赖阶段 0-3 产出的 AGENTS.md。由 aidoc-create 阶段 4 触发，也可独立使用。
---

# 经验库初始化

## 概览

在阶段 0-3 产出的结构文档基础上，构建经验库（`docs/learnings/`），承载开发与运维中的教训，支持持续记录。

## 前置条件

- `.aidoc/phase0/repo-profile.md` 必须存在
- 根目录 AGENTS.md 和各模块 AGENTS.md 应已生成

## 工作流程

### 步骤 1：初始化

在项目根目录创建经验库的三文件结构：

```bash
mkdir -p docs/learnings
[ -f docs/learnings/LEARNINGS.md ] || printf "# 学习记录\n\n开发过程中捕获的纠正、洞察和知识盲区。\n\n**分类**：correction | insight | knowledge_gap | best_practice\n\n---\n" > docs/learnings/LEARNINGS.md
[ -f docs/learnings/ERRORS.md ] || printf "# 错误日志\n\n命令失败和集成错误。\n\n---\n" > docs/learnings/ERRORS.md
[ -f docs/learnings/FEATURE_REQUESTS.md ] || printf "# 功能请求\n\n用户请求的功能。\n\n---\n" > docs/learnings/FEATURE_REQUESTS.md
```

切勿覆盖已有文件。如果 `docs/learnings/` 已经初始化，此操作不会产生任何效果。

### 步骤 2：经验提取

从已有文档中提取可沉淀的经验，写入 `docs/learnings/LEARNINGS.md`：

1. **从 CLAUDE.md** 提取：搜索"避坑"、"重启规则"、"已知问题"、"关键经验"、"千万不要"、"不要"等段落
2. **从根 AGENTS.md** 提取："禁止事项 / 常见陷阱"章节；"Do Not / Gotchas" 章节
3. **从模块 AGENTS.md** 提取：`<!-- HUMAN_REVIEW -->` 中已回填的经验性内容

### 步骤 3：生成

- 提取的经验以 `[LRN-YYYYMMDD-XXX]` 格式追加到 `docs/learnings/LEARNINGS.md`（格式详见 `aidoc-learning` 技能）
- 创建 `docs/learnings/AGENTS.md`（使用 `templates/learnings-index.tmpl.md`）
- 若未检测到可提取的经验，创建 `docs/learnings/AGENTS.md` 骨架（预留模板条目），并注明"尚未检测到可自动提取的经验"
- `<!-- HUMAN_REVIEW -->` 标记所有 AI 推断的现象/根因/教训

### 步骤 4：回写入口文件

经验库的索引必须可被发现——Agent 不会主动探索未知目录。用户确认后，将索引引用**写回根 AGENTS.md**（若已存在则更新）：

```markdown
## 经验库 [~ 推断]

- **经验库**：`docs/learnings/AGENTS.md` — 开发与运维踩坑教训（{N} 条）

> 遇到"之前怎么解决"→ 查经验库。
> 持续记录：开发中遇到错误、纠正、新发现，按 `aidoc-learning` 格式记录到 `docs/learnings/`。
```

## 生成后

1. 展示完整的目录结构概览供审阅：
   ```
   📦 经验库已生成：

   docs/learnings/
   ├── LEARNINGS.md
   ├── ERRORS.md
   ├── FEATURE_REQUESTS.md
   ├── AGENTS.md
   └── ...（{N} 条初始经验）
   ```
2. 确认重点：
   - "还有哪些踩坑经验应该沉淀到此？"
3. 用户确认后，将完成报告写入 `.aidoc/phase4b/report.md`：

```markdown
# 阶段 4b 完成报告

## 生成结果
- docs/learnings/：{N} 条初始经验，已启用持续记录
- 生成时间：{时间戳}

## 目录骨架清单
| 路径 | 类型 | 状态 |
|------|------|------|
| docs/learnings/LEARNINGS.md | 学习记录 | ✓ |
| docs/learnings/ERRORS.md | 错误日志 | ✓ |
| docs/learnings/FEATURE_REQUESTS.md | 功能请求 | ✓ |
| docs/learnings/AGENTS.md | 经验索引 | ✓ |

## 待人工补充
{汇总所有 HUMAN_REVIEW 标记}
```

## 幂等性

如果目标路径已存在文件：
- 不要静默覆盖
- 展示现有文件与生成内容的差异
- 让用户选择：保留现有、合并或替换
