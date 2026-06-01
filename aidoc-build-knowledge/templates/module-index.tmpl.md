# 模块总览

> 按模块浏览系统架构。每个模块有独立的蓝图文档，包含 C4 Component 图、对外接口和关联流程。

## 模块清单

| 模块 | 技术栈 | 职责 | 内部组件数 | 参与流程数 | 蓝图 |
|------|--------|------|-----------|-----------|------|
{{#MODULES}}
| **{{NAME}}** | {{TECH}} | {{RESPONSIBILITY}} | {{COMPONENT_COUNT}} | {{FLOW_COUNT}} | [查看]({{FILE}}.md) |
{{/MODULES}}

## 模块依赖全景

```mermaid
graph LR
    {{#DEPENDENCY_GRAPH}}
    {{FROM}} --> {{TO}}
    {{/DEPENDENCY_GRAPH}}
```

> 箭头方向 = 调用方向（A → B 表示 A 调用 B）
>
> 如需查看某模块的内部组件详情，点击上表中的"查看"链接。
