# {{SYSTEM_NAME}} — 架构蓝图

> 本蓝图基于 **C4 模型 + Mermaid + ADR** 构建。按模块（结构）和流程（行为）双轴组织，通过超链接双向关联。

## 系统全景

```mermaid
C4_Context
    title {{SYSTEM_NAME}} — 系统全景

    Person(user, "{{PRIMARY_USER}}", "{{USER_DESCRIPTION}}")

    System(system, "{{SYSTEM_NAME}}", "{{SYSTEM_DESCRIPTION}}")

    {{#EXTERNAL_SYSTEMS}}
    System_Ext({{EXT_SYS_KEY}}, "{{EXT_SYS_NAME}}", "{{EXT_SYS_DESC}}")
    {{/EXTERNAL_SYSTEMS}}

    Rel(user, system, "{{USER_INTERACTION}}")
    {{#SYSTEM_RELATIONS}}
    Rel(system, {{EXT_SYS_KEY}}, "{{REL_DESC}}")
    {{/SYSTEM_RELATIONS}}
```

> 详细上下文图见 [system-context.md](system-context.md)

## 按模块查阅（{{MODULE_COUNT}} 个模块）

| 模块 | 职责 | 参与流程数 | 内部架构 |
|------|------|-----------|----------|
{{#MODULES}}
| **{{MODULE_NAME}}** | {{RESPONSIBILITY}} | {{FLOW_COUNT}} | [Component 图](modules/{{MODULE_FILE}}.md) |
{{/MODULES}}

> 模块总览见 [modules/_index.md](modules/_index.md)

## 按流程查阅（{{FLOW_COUNT}} 条核心流程）

| 流程 | 触发条件 | 涉及模块 | 关键步骤 |
|------|----------|----------|----------|
{{#FLOWS}}
| [{{FLOW_NAME}}](flows/{{FLOW_FILE}}.md) | {{TRIGGER}} | {{MODULE_COUNT}} 个模块 | {{KEY_STEPS}} |
{{/FLOWS}}

> 流程总览见 [flows/_index.md](flows/_index.md)

## 按决策查阅

| ADR | 决策 | 状态 | 日期 |
|-----|------|------|------|
{{#ADRS}}
| [ADR-{{NUMBER}}](decisions/adr-{{NUMBER}}-{{SLUG}}.md) | {{TITLE}} | {{STATUS}} | {{DATE}} |
{{/ADRS}}

> 决策索引见 [decisions/_index.md](decisions/_index.md)

## 快速导航

| 我想了解... | 看这里 |
|------------|--------|
| 系统整体架构 | [container-architecture.md](container-architecture.md) |
| 某个模块的内部设计 | [modules/_index.md](modules/_index.md) → 找到对应模块 |
| 某个业务流程怎么走的 | [flows/_index.md](flows/_index.md) → 找到对应流程 |
| 为什么做某个技术决策 | [decisions/_index.md](decisions/_index.md) |
| 跨模块的通用机制（认证、日志等） | [crosscutting/_index.md](crosscutting/_index.md) |
