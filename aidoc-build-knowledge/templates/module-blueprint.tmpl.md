# {{MODULE_NAME}}

> **所属系统**：[{{SYSTEM_NAME}}](../README.md) | **类型**：{{MODULE_TYPE}} | **技术栈**：{{TECH_STACK}}

## 职责

{{RESPONSIBILITY}}

{{#BUSINESS_DOMAIN}}
业务域：**{{BUSINESS_DOMAIN}}**
{{/BUSINESS_DOMAIN}}

## 内部架构（C4 Level 3: Component）

```mermaid
C4_Component
    title {{MODULE_NAME}} — 内部组件图

    Container_Boundary({{BOUNDARY_KEY}}, "{{MODULE_NAME}}") {
        {{#COMPONENTS}}
        Component({{COMP_KEY}}, "{{COMP_NAME}}", "{{COMP_TECH}}", "{{COMP_DESC}}")
        {{/COMPONENTS}}
    }

    {{#EXTERNAL_DEPS}}
    {{EXT_DECL}}
    {{/EXTERNAL_DEPS}}

    {{#COMPONENT_RELATIONS}}
    Rel({{FROM}}, {{TO}}, "{{REL_DESC}}")
    {{/COMPONENT_RELATIONS}}
```

## 对外接口

### 入站接口（我提供的）

| 接口 | 协议 | 调用方 | 所属流程 |
|------|------|--------|----------|
{{#INBOUND_APIS}}
| `{{API}}` | {{PROTOCOL}} | {{CALLER}} | [{{FLOW}}](../flows/{{FLOW_FILE}}.md) |
{{/INBOUND_APIS}}

### 出站依赖（我调用的）

| 接口/中间件 | 提供方 | 用途 | 所属流程 |
|------------|--------|------|----------|
{{#OUTBOUND_DEPS}}
| `{{API}}` | [{{PROVIDER}}](../modules/{{PROVIDER_FILE}}.md) | {{PURPOSE}} | [{{FLOW}}](../flows/{{FLOW_FILE}}.md) |
{{/OUTBOUND_DEPS}}

## 关联流程

| 流程 | 角色 | 步骤 |
|------|------|------|
{{#RELATED_FLOWS}}
| [{{FLOW_NAME}}](../flows/{{FLOW_FILE}}.md) | {{ROLE}} | {{STEPS}} |
{{/RELATED_FLOWS}}

## 关键设计决策

{{#DECISIONS}}
- [ADR-{{NUMBER}}：{{TITLE}}](../decisions/adr-{{NUMBER}}-{{SLUG}}.md)
{{/DECISIONS}}
{{^DECISIONS}}
暂无该模块特有的架构决策记录。
{{/DECISIONS}}

---

> 返回：[模块总览](_index.md) | [蓝图首页](../README.md)
