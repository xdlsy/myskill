# 流程总览

> 按流程浏览系统行为。每条核心流程有独立的蓝图文档，包含 Mermaid 时序图、参与模块和异常路径。

## 核心流程清单

| 流程 | 类型 | 触发条件 | 涉及模块 | 步骤数 | 蓝图 |
|------|------|----------|----------|--------|------|
{{#FLOWS}}
| **{{NAME}}** | {{TYPE}} | {{TRIGGER}} | {{MODULE_COUNT}} 个 | {{STEP_COUNT}} | [查看]({{FILE}}.md) |
{{/FLOWS}}

## 流程-模块矩阵

| | {{#MODULE_NAMES}} {{NAME}} |{{/MODULE_NAMES}}
|------|{{#MODULE_NAMES}}------|{{/MODULE_NAMES}}
{{#MATRIX}}
| **{{FLOW_NAME}}** | {{#MODULES}} {{INVOLVED}} |{{/MODULES}}
{{/MATRIX}}

> 图例：**✓** 参与 | **—** 不参与
>
> 点击流程名查看详情。
