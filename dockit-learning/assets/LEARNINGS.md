# 学习记录

开发过程中捕获的纠正、洞察和知识盲区。

**分类**：correction | insight | knowledge_gap | best_practice
**区域**：frontend | backend | infra | tests | docs | config
**状态**：pending | in_progress | resolved | wont_fix | promoted | promoted_to_skill

## 状态定义

| 状态 | 含义 |
|--------|---------|
| `pending` | 尚未处理 |
| `in_progress` | 正在积极处理中 |
| `resolved` | 问题已修复或知识已整合 |
| `wont_fix` | 决定不处理（原因见 Resolution） |
| `promoted` | 已升级到 CLAUDE.md、AGENTS.md 或 copilot-instructions.md |
| `promoted_to_skill` | 已提取为可复用技能 |

## 技能提取字段

当学习经验升级为技能时，添加以下字段：

```markdown
**Status**：promoted_to_skill
**Skill-Path**：skills/skill-name
```

示例：
```markdown
## [LRN-20250115-001] best_practice

**Logged**：2025-01-15T10:00:00Z
**Priority**：high
**Status**：promoted_to_skill
**Skill-Path**：skills/docker-m1-fixes
**Area**：infra

### Summary
由于平台不匹配，Docker 构建在 Apple Silicon 上失败
...
```

---

