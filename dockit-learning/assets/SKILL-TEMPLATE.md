# 技能模板

从学习经验中提取技能时使用的模板。复制后自定义使用。

---

## SKILL.md 模板

```markdown
---
name: skill-name-here
description: "简洁地描述此技能的功能和使用时机。包含触发条件。"
---

# 技能名称

简要介绍此技能解决的问题及其来源。

## 快速参考

| 场景 | 操作 |
|-----------|--------|
| [触发条件 1] | [操作 1] |
| [触发条件 2] | [操作 2] |

## 背景

为什么这些知识很重要。它可以防止什么问题。来自原始学习经验的上下文。

## 解决方案

### 分步说明

1. 第一步，附带代码或命令
2. 第二步
3. 验证步骤

### 代码示例

\`\`\`language
// 演示解决方案的示例代码
\`\`\`

## 常见变体

- **变体 A**：描述及处理方法
- **变体 B**：描述及处理方法

## 注意事项

- 警告或常见错误 #1
- 警告或常见错误 #2

## 相关资源

- 链接到相关文档
- 链接到相关技能

## 来源

从学习条目提取。
- **学习 ID**：LRN-YYYYMMDD-XXX
- **原始分类**：correction | insight | knowledge_gap | best_practice
- **提取日期**：YYYY-MM-DD
```

---

## 最小模板

适用于不需要所有部分的简单技能：

```markdown
---
name: skill-name-here
description: "此技能的功能和使用时机。"
---

# 技能名称

[一句话描述问题]

## 解决方案

[附代码/命令的直接解决方案]

## 来源

- 学习 ID：LRN-YYYYMMDD-XXX
```

---

## 带脚本的模板

适用于包含可执行辅助脚本的技能：

```markdown
---
name: skill-name-here
description: "此技能的功能和使用时机。"
---

# 技能名称

[介绍]

## 快速参考

| 命令 | 用途 |
|---------|---------|
| `./scripts/helper.sh` | [功能描述] |
| `./scripts/validate.sh` | [功能描述] |

## 使用说明

### 自动化（推荐）

\`\`\`bash
./skills/skill-name/scripts/helper.sh [args]
\`\`\`

### 手动步骤

1. 第一步
2. 第二步

## 脚本

| 脚本 | 描述 |
|--------|-------------|
| `scripts/helper.sh` | 主要工具 |
| `scripts/validate.sh` | 验证检查器 |

## 来源

- 学习 ID：LRN-YYYYMMDD-XXX
```

---

## 命名约定

- **技能名称**：小写，连字符分隔
  - 好的：`docker-m1-fixes`、`api-timeout-patterns`
  - 差的：`Docker_M1_Fixes`、`APITimeoutPatterns`

- **描述**：以动作动词开头，提及触发条件
  - 好的："处理 Apple Silicon 上的 Docker 构建失败。当构建失败并出现平台不匹配时使用。"
  - 差的："Docker 相关的东西"

- **文件**：
  - `SKILL.md` - 必需，主要文档
  - `scripts/` - 可选，可执行代码
  - `references/` - 可选，详细文档
  - `assets/` - 可选，模板

---

## 提取检查清单

从学习经验创建技能之前：

- [ ] 学习经验已验证（状态：resolved）
- [ ] 解决方案广泛适用（非一次性）
- [ ] 内容完整（具有所有需要的上下文）
- [ ] 名称遵循约定
- [ ] 描述简洁但信息丰富
- [ ] 快速参考表格可操作
- [ ] 代码示例已测试
- [ ] 已记录来源学习 ID

创建之后：

- [ ] 使用 `promoted_to_skill` 状态更新原始学习记录
- [ ] 在学习元数据中添加 `Skill-Path：skills/skill-name`
- [ ] 通过在新会话中阅读来测试技能
