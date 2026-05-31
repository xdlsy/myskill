---
name: aidoc-module-init
description: 为代码仓中所有叶子模块生成 AGENTS.md（每个 30-50 行）。依赖 .aidoc/phase0/repo-profile.md 中的画像数据。使用子代理并行生成。由 aidoc-create 阶段 2 触发，也可独立使用。
---

# 子模块 AGENTS.md 批量生成

## 概览

基于 `.aidoc/phase0/repo-profile.md` 中的叶子模块信息，通过子代理并行为每个模块生成 `AGENTS.md`。

**核心策略：使用子代理（subagent）为每个模块独立生成**，避免主上下文膨胀。

## 前置条件

- `.aidoc/phase0/repo-profile.md` 必须存在且内容完整
- 根目录 `AGENTS.md` 应已生成（模块 AGENTS.md 不重复根文档内容）

## 约束

- 每个模块 AGENTS.md 30-50 行
- 只写模块特定的补充内容 — 不重复根 AGENTS.md（遵循 AGENTS.md "最近优先"的嵌套语义）
- 每个章节标注置信度：`[✓ 自动]` / `[~ 推断]` / `[? 待审核]`

## 步骤 1：批量确认模块职责

从 `.aidoc/phase0/repo-profile.md` 中的画像数据提取所有叶子模块，一次性展示给用户确认：

```
📦 待处理的子模块（共 N 个）：

| # | 模块路径 | 语言 | 文件数 | 类型 | 推断职责 |
|---|---------|------|--------|------|---------|
| 1 | internal/order/ | Java | 42 | domain | 订单领域模型和状态机 |
| 2 | internal/payment/ | Java | 18 | service | 支付处理与网关集成 |
| ... |

→ 全部确认 / 跳过特定模块（输入编号） / 编辑特定模块描述（输入 "e1: 新描述"）
```

**重复模式检测：** 若超过 3 个模块共享相同的内部结构（如 controller/service/repository），标注并提示批量生成。

## 步骤 2：子代理并行生成

对每个确认的模块，使用 `Agent` 工具派发子代理。子代理 prompt 必须包含：

### 模块上下文（从画像数据中提取）
- 模块路径、语言、文件数、代码行数
- 依赖关系（依赖哪些模块、被哪些模块依赖）
- 用户确认的职责描述

### 输出模板

```markdown
# {{MODULE_NAME}}

## 职责 [~ 推断]
{{USER_CONFIRMED_RESPONSIBILITY}}

## 约定 [~ 推断]
{{AUTO_EXTRACTED_PATTERNS}}
<!-- HUMAN_REVIEW: 请补充本模块特有的编码约定和注意事项 -->

## 依赖 [✓ 自动]
- 依赖：{{DEPS}}
- 被依赖：{{REVERSE_DEPS}}
```

### 探索指令

```
你需要：
1. 列出 {module_path} 下的文件
2. 读取 2-3 个代表性文件：最大的源文件、主要导出/接口文件、有文档注释的文件
3. 从包名、文件注释、导出符号推断模块职责
4. 检测约定：错误处理模式、命名约定、架构分层（controller→service→repository）
5. 不确定的内容标记为 <!-- HUMAN_REVIEW -->
6. 将生成的 AGENTS.md 写入 {module_path}/AGENTS.md
```

### 并行策略

- 所有子代理可同时派发（相互独立）
- 对于共享相同内部结构的 3+ 个模块，可合并为一个子代理批量处理
- 若 `.aidoc/phase0/repo-profile.md` 中的画像数据已包含足够详细的模块信息，可跳过文件读取直接生成

## 步骤 3：汇总审阅

所有子代理完成后展示摘要：

```
| # | 模块 | 职责 | 状态 |
|---|--------|---------------|--------|
| 1 | internal/order/ | 订单领域模型 | ✓ 已生成 |
| 2 | internal/payment/ | 支付处理 | ✓ 已生成 |
| ... |
```

询问："请审阅各模块的 AGENTS.md。是否需要重新检查某些模块？"

用户确认后，将完成报告写入 `.aidoc/phase2/report.md`：

```markdown
# 阶段 2 完成报告

## 生成结果
- 总模块数：{N}
- 成功生成：{N}
- 生成时间：{时间戳}

## 模块清单
| # | 模块路径 | 文件路径 | 行数 | 状态 |
|---|---------|---------|------|------|
| 1 | api/ | .../api/AGENTS.md | 33 | ✓ |
| 2 | adapter/ | .../adapter/AGENTS.md | 36 | ✓ |
| ... |

## 超限模块
{列出超过 50 行的模块及原因}

## 待人工补充
{汇总所有模块中 HUMAN_REVIEW 标记的数量和位置}
```
