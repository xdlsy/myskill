# {{SYSTEM_NAME}} — 系统全景图（C4 Level 1: Context）

> C4 Context 图展示系统的边界——系统本身、与之交互的用户和外部系统。

## 系统描述

**{{SYSTEM_NAME}}**：{{SYSTEM_DESCRIPTION}}

核心价值：{{CORE_VALUE}}

## Context 图

```mermaid
C4_Context
    title {{SYSTEM_NAME}} 系统全景图

    {{#ACTORS}}
    Person({{ACTOR_KEY}}, "{{ACTOR_NAME}}", "{{ACTOR_DESCRIPTION}}")
    {{/ACTORS}}

    {{#EXTERNAL_SYSTEMS}}
    System_Ext({{EXT_SYS_KEY}}, "{{EXT_SYS_NAME}}", "{{EXT_SYS_DESCRIPTION}}")
    {{/EXTERNAL_SYSTEMS}}

    System_Boundary({{BOUNDARY_KEY}}, "{{SYSTEM_NAME}}") {
        System({{SYSTEM_KEY}}, "{{SYSTEM_NAME}}", "{{SYSTEM_DESCRIPTION}}")
    }

    {{#USER_RELATIONS}}
    Rel({{ACTOR_KEY}}, {{SYSTEM_KEY}}, "{{REL_DESC}}")
    {{/USER_RELATIONS}}
    {{#EXT_RELATIONS}}
    Rel({{SYSTEM_KEY}}, {{EXT_SYS_KEY}}, "{{REL_DESC}}")
    {{/EXT_RELATIONS}}
    {{#INBOUND_RELATIONS}}
    Rel({{EXT_SYS_KEY}}, {{SYSTEM_KEY}}, "{{REL_DESC}}")
    {{/INBOUND_RELATIONS}}
```

## 外部依赖清单

| 外部系统 | 类型 | 交互方式 | 用途 |
|----------|------|----------|------|
{{#EXTERNAL_DEPS}}
| {{NAME}} | {{TYPE}} | {{PROTOCOL}} | {{PURPOSE}} |
{{/EXTERNAL_DEPS}}

## 用户角色

| 角色 | 描述 | 主要场景 |
|------|------|----------|
{{#USER_ROLES}}
| {{ROLE}} | {{DESCRIPTION}} | {{SCENARIOS}} |
{{/USER_ROLES}}
