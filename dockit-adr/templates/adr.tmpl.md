---
title: "ADR-{{ADR_NUMBER}}: {{TITLE}}"
status: "{{STATUS}}"
date: "{{DATE}}"
tags: [{{TAGS}}]
---

# ADR-{{ADR_NUMBER}}: {{TITLE}}

## 状态

**{{STATUS}}** | 已采纳 | 已拒绝 | 已替代 | 已废弃

## 背景上下文

{{CONTEXT}}

## 决策

{{DECISION}}

## 后果

### 正面

{{#POSITIVE_CONSEQUENCES}}
- **POS-{{NUMBER}}**：{{DESCRIPTION}}
{{/POSITIVE_CONSEQUENCES}}
{{^POSITIVE_CONSEQUENCES}}
- **POS-001**：[待补充：有益成果与优势]
{{/POSITIVE_CONSEQUENCES}}

### 负面

{{#NEGATIVE_CONSEQUENCES}}
- **NEG-{{NUMBER}}**：{{DESCRIPTION}}
{{/NEGATIVE_CONSEQUENCES}}
{{^NEGATIVE_CONSEQUENCES}}
- **NEG-001**：[待补充：权衡、限制与风险]
{{/NEGATIVE_CONSEQUENCES}}

## 备选方案

{{#ALTERNATIVES}}
### {{NAME}}

- **ALT-{{ALT_NUMBER}}**：**描述**：{{DESCRIPTION}}
- **ALT-{{REJECT_NUMBER}}**：**拒绝理由**：{{REJECTION_REASON}}
{{/ALTERNATIVES}}
{{^ALTERNATIVES}}
<!-- HUMAN_REVIEW: 请补充被考虑的备选方案及拒绝理由 -->
{{/ALTERNATIVES}}

## 实施注意事项

{{#IMPLEMENTATION_NOTES}}
- **IMP-{{NUMBER}}**：{{NOTE}}
{{/IMPLEMENTATION_NOTES}}
{{^IMPLEMENTATION_NOTES}}
- **IMP-001**：[待补充：关键实施考量]
{{/IMPLEMENTATION_NOTES}}

## 参考资料

{{#REFERENCES}}
- **REF-{{NUMBER}}**：{{DESCRIPTION}}
{{/REFERENCES}}
{{^REFERENCES}}
<!-- 无外部参考资料 -->
{{/REFERENCES}}

## 关联

- **模块**：{{RELATED_MODULES}}
- **流程**：{{RELATED_FLOWS}}
