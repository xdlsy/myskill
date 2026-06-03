# {{FLOW_NAME}}

> **流程类型**：{{FLOW_TYPE}} | **触发条件**：{{TRIGGER}} | **目标**：{{GOAL}}

## 参与模块

| 步骤 | 模块 | 动作 | 关键输入/输出 |
|------|------|------|--------------|
{{#STEPS}}
| {{STEP_NUMBER}} | [{{MODULE_NAME}}](../modules/{{MODULE_FILE}}.md) | {{ACTION}} | `{{KEY_DATA}}` |
{{/STEPS}}

## 时序图

```mermaid
sequenceDiagram
    autonumber
    {{#PARTICIPANTS}}
    participant {{ALIAS}} as {{DISPLAY_NAME}}
    {{/PARTICIPANTS}}

    {{#INTERACTIONS}}
    {{INTERACTION}}
    {{/INTERACTIONS}}
```

## 异常路径

| 异常点 | 触发条件 | 处理方式 | 影响范围 |
|--------|----------|----------|----------|
{{#ERROR_PATHS}}
| {{LOCATION}} | {{CONDITION}} | {{HANDLING}} | {{IMPACT}} |
{{/ERROR_PATHS}}

{{#SAGA_NOTE}}
> ⚠️ **分布式事务说明**：本流程涉及 {{SAGA_MODULE_COUNT}} 个模块的数据变更。{{SAGA_STRATEGY}}
{{/SAGA_NOTE}}

## 关联模块摘要

| 模块 | 在本流程中的职责 |
|------|-----------------|
{{#MODULE_SUMMARY}}
| [{{MODULE_NAME}}](../modules/{{MODULE_FILE}}.md) | {{ROLE_IN_FLOW}} |
{{/MODULE_SUMMARY}}

---

> 返回：[流程总览](INDEX.md) | [蓝图首页](../AGENTS.md)
