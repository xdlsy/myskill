# {{SYSTEM_NAME}} — 容器架构图（C4 Level 2: Container）

> C4 Container 图放大到系统内部，展示主要的容器（应用、服务、数据库等）及其交互关系。

## Container 图

```mermaid
C4_Container
    title {{SYSTEM_NAME}} 容器架构图

    {{#EXTERNAL_ACTORS}}
    Person({{ACTOR_KEY}}, "{{ACTOR_NAME}}", "{{ACTOR_DESC}}")
    {{/EXTERNAL_ACTORS}}

    System_Boundary({{BOUNDARY_KEY}}, "{{SYSTEM_NAME}}") {
        {{#CONTAINERS}}
        Container({{CONTAINER_KEY}}, "{{CONTAINER_NAME}}", "{{TECH_STACK}}", "{{DESCRIPTION}}")
        {{/CONTAINERS}}
        {{#DATA_STORES}}
        ContainerDb({{DB_KEY}}, "{{DB_NAME}}", "{{DB_TECH}}", "{{DB_DESC}}")
        {{/DATA_STORES}}
        {{#QUEUES}}
        ContainerQueue({{QUEUE_KEY}}, "{{QUEUE_NAME}}", "{{QUEUE_TECH}}", "{{QUEUE_DESC}}")
        {{/QUEUES}}
    }

    {{#EXTERNAL_SYSTEMS}}
    System_Ext({{EXT_KEY}}, "{{EXT_NAME}}", "{{EXT_DESC}}")
    {{/EXTERNAL_SYSTEMS}}

    {{#RELATIONS}}
    Rel({{FROM}}, {{TO}}, "{{REL_DESC}}")
    {{/RELATIONS}}
```

## 容器清单

| 容器 | 类型 | 技术栈 | 职责 | 所属模块 |
|------|------|--------|------|----------|
{{#CONTAINER_LIST}}
| **{{NAME}}** | {{TYPE}} | {{TECH}} | {{RESPONSIBILITY}} | [{{MODULE}}](modules/{{MODULE_FILE}}.md) |
{{/CONTAINER_LIST}}

## 模块间依赖矩阵

| | {{#MODULE_NAMES}} {{NAME}} |{{/MODULE_NAMES}}
|------|{{#MODULE_NAMES}}------|{{/MODULE_NAMES}}
{{#DEPENDENCY_MATRIX}}
| **{{FROM}}** | {{#TO}} {{DEP}} |{{/TO}}
{{/DEPENDENCY_MATRIX}}

> 图例：**→** 同步调用 | **⇢** 异步消息 | **—** 无直接依赖
>
> 各模块的内部组件架构见 [modules/](modules/INDEX.md)
