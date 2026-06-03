---
name: aidoc-writing-adr
description: 创建单篇架构决策记录（ADR）文档，使用 MADR 格式 + 编码要点（POS/NEG/ALT/IMP/REF）。输出到 docs/knowledge/decisions/ 目录，与 aidoc-build-knowledge 的 ADR 索引和蓝图统一管理。
---

# 创建架构决策记录

为 `${input:DecisionTitle}` 创建单篇 ADR 文档，使用结构化格式，兼顾 AI 消费与人类可读性。

## 与其他技能的关系

- **`aidoc-build-knowledge`**：负责蓝图全貌（C4 图 + 流程图 + ADR 索引），批量生成时调用本技能创建单篇 ADR
- **本技能**：专注于单篇 ADR 的创建和编辑，可独立使用，也可被 `aidoc-build-knowledge` 调用

## 输入

- **决策标题**：`${input:DecisionTitle}`
- **背景上下文**：`${input:Context}`
- **决策内容**：`${input:Decision}`
- **备选方案**：`${input:Alternatives}`
- **相关人员**：`${input:Stakeholders}`

## 输入校验

若任一必填输入缺失且无法从对话历史中推断，请在生成 ADR 之前向用户索要缺失的信息。

## 要求

- 使用精确、无歧义的语言
- 遵循 MADR 格式，包含 YAML frontmatter 元数据
- 同时包含正面和负面后果
- 记录备选方案及其被拒绝的理由
- 多条目章节使用编码要点（3-4 字母前缀 + 3 位数字编号）
- 关联相关模块和流程（与蓝图双向链接）

## 输出路径

ADR 保存至 `docs/knowledge/decisions/` 目录（与 `aidoc-build-knowledge` 的输出目录一致）。

命名规范：`adr-NNNN-[标题缩写].md`，其中 NNNN 为下一位顺序 4 位数字编号。

- 扫描 `docs/knowledge/decisions/` 目录中已有的 ADR，取最大编号 +1
- 若目录不存在，从 `adr-0001` 开始
- 示例：`adr-0001-数据库选型.md`

## 必需的文档结构

```md
---
title: "ADR-NNNN: [决策标题]"
status: "Proposed"
date: "YYYY-MM-DD"
tags: ["架构", "决策"]
---

# ADR-NNNN: [决策标题]

## 状态

**提议** | 已采纳 | 已拒绝 | 已替代 | 已废弃

## 背景上下文

[问题陈述、技术约束、业务需求以及引发此决策的环境因素。]

## 决策

[所选方案及其明确的选型理由。]

## 后果

### 正面

- **POS-001**：[有益成果与优势]
- **POS-002**：[性能、可维护性、可扩展性方面的改善]

### 负面

- **NEG-001**：[权衡、限制、缺陷]
- **NEG-002**：[引入的技术债务或复杂性]

## 备选方案

### [备选方案 1 名称]

- **ALT-001**：**描述**：[简要技术说明]
- **ALT-002**：**拒绝理由**：[为何未选择此方案]

### [备选方案 2 名称]

- **ALT-003**：**描述**：[简要技术说明]
- **ALT-004**：**拒绝理由**：[为何未选择此方案]

## 实施注意事项

- **IMP-001**：[关键实施考量]
- **IMP-002**：[迁移或推出版本策略]

## 参考资料

- **REF-001**：[相关 ADR]
- **REF-002**：[外部文档]

## 关联

- **模块**：[关联的模块，链接到 docs/knowledge/modules/]
- **流程**：[关联的流程，链接到 docs/knowledge/flows/]
```

## 编码要点规范

| 前缀 | 含义 | 用途 |
|------|------|------|
| `POS-XXX` | Positive | 正面后果 |
| `NEG-XXX` | Negative | 负面后果与权衡 |
| `ALT-XXX` | Alternative | 备选方案描述及拒绝理由 |
| `IMP-XXX` | Implementation | 实施注意事项 |
| `REF-XXX` | Reference | 参考资料 |

每个 ADR 内独立编号，从 001 开始。

## 生成后

1. 展示 ADR 全文供审阅
2. 确认后写入 `docs/knowledge/decisions/adr-NNNN-<slug>.md`
3. 若 `docs/knowledge/decisions/_index.md` 已存在，提示用户更新索引表
4. 若该 ADR 关联了特定模块或流程，提示用户是否需要在模块/流程文档中添加反向链接

> 模板参考：`templates/adr.tmpl.md`
