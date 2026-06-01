---
name: aidoc-build-knowledge
description: 为代码仓构建知识库（Knowledge Base），使用 Mermaid + C4 模型 + ADR 承载系统架构图、模块内部架构、跨模块流程图和架构决策记录。支持独立使用，也可作为 aidoc-create 阶段 3 的增强步骤。输出到 docs/knowledge/ 目录。
---

# 知识库构建

## 概览

为代码仓库生成可视化知识库，基于 **Mermaid（Diagram-as-Code）+ C4 模型（4 层结构图）+ ADR（架构决策记录）**，输出到 `docs/knowledge/` 目录。

蓝图采用 **"地图 + 路线"双轴组织**：

| 轴 | 目录 | 内容 | 对应 C4 层级 |
|---|------|------|-------------|
| **地图**（结构） | `modules/` | 每个模块的内部架构、对外接口、依赖关系 | C4 Level 3: Component |
| **路线**（流程） | `flows/` | 每条核心流程的时序图、参与模块、异常路径 | C4 Level 2 运行时视角 |

两者之间通过**超链接双向关联**，无论从模块还是流程入口都能导航到对方。

## 前置条件

- **独立模式**：无需任何前置文件，通过对话收集系统和模块信息
- **管道模式**（可选）：读取 `.aidoc/phase0/repo-profile.md` 和已有 `AGENTS.md` 自动推断模块结构

## 工作流

### 步骤 0：发现（Discovery）

首先了解待文档化的系统：

**独立模式**——向用户收集以下信息：
1. **系统名称**和一句话描述（这个系统解决什么问题？）
2. **外部角色**：哪些用户/外部系统与此系统交互？
3. **模块清单**：系统有哪些模块/服务？每个模块的一句话职责
4. **核心流程清单**：系统有哪些关键业务流程？每条流程经过哪些模块（按顺序）？
5. **关键技术决策**：有哪些值得记录的架构决策？（语言/框架选型、数据库选型、通信方式等）

**管道模式**——从已有产物中推断：
- 读取 `.aidoc/phase0/repo-profile.md` 获取模块结构、语言/框架信息
- 读取根 `AGENTS.md` 和各模块 `AGENTS.md` 获取模块职责和依赖
- 读取 `docs/ARCHITECTURE.md` 获取已有的架构描述
- 将推断结果展示给用户确认和补充（特别是跨模块流程，通常需要人工补充）

> **交互原则**：一次问清楚所有信息，不要一个问题一个问题地追问。如果用户一次性提供了完整信息，直接跳入生成步骤，不要为了"流程完整"而反复确认。

### 步骤 1：系统全景图（C4 Level 1: Context）

生成 `docs/knowledge/system-context.md`。

使用 Mermaid `C4_Context` 语法，展示：
- **1 个核心系统**（本仓库代表的系统）
- **外部角色**：用户角色、外部依赖系统（第三方服务、上游/下游系统）
- **交互关系**：谁使用系统？系统依赖哪些外部系统？

模板：`templates/system-context.tmpl.md`

生成后展示给用户确认：
- "外部角色和系统是否完整？"
- "交互关系是否准确？"

### 步骤 2：容器架构图（C4 Level 2: Container）

生成 `docs/knowledge/container-architecture.md`。

使用 Mermaid `C4_Container` 语法，展示系统内部容器（应用/服务/数据库/消息队列等）：
- **每个模块作为一个 Container**
- **模块间的调用/依赖关系**
- **数据存储**（数据库、缓存、文件系统等）

模板：`templates/container-architecture.tmpl.md`

生成后展示给用户确认：
- "模块划分是否准确？"
- "模块间的依赖关系是否正确？"

### 步骤 3：模块蓝图（C4 Level 3: Component）

为每个模块生成 `docs/knowledge/modules/<module-name>.md`。

每份模块蓝图包含：

1. **模块职责**：一句话描述 + 所属业务域
2. **C4 Component 图**（Mermaid `C4_Component`）：模块内部的组件及其交互
3. **对外接口表**：

| 接口 | 方向 | 调用方/被调用方 | 所属流程 |
|------|------|----------------|----------|
| `POST /orders` | 入站 | API 网关 | [流程1：下单](../flows/flow-1-xxx.md) |
| `OrderCreated` 事件 | 出站 | 支付服务 | [流程2：支付](../flows/flow-2-xxx.md) |

4. **关联流程**：该模块参与的核心流程列表（含链接）
5. **关键设计决策**：该模块特有的架构选择（链接到 ADR）

模板：`templates/module-blueprint.tmpl.md`

同时生成 `docs/knowledge/modules/_index.md`（模块总览表）。

模板：`templates/module-index.tmpl.md`

> **规模控制**：如果模块数 > 10，优先为核心/复杂模块生成 Component 图；简单模块（如纯 CRUD、配置模块）可跳过 Component 图，仅在 `_index.md` 中保留条目。

### 步骤 4：流程蓝图（Runtime View）

为每条核心流程生成 `docs/knowledge/flows/<flow-name>.md`。

每份流程蓝图包含：

1. **流程概述**：一句话描述流程目标和触发条件
2. **参与模块表**：

| 步骤 | 模块 | 动作 | 关键数据 |
|------|------|------|----------|
| 1 | [订单服务](../modules/order-service.md) | 创建订单 | `order_id`, `user_id` |
| 2 | [库存服务](../modules/inventory-service.md) | 锁定库存 | `sku_id`, `quantity` |

3. **Mermaid 时序图**（`sequenceDiagram`）：完整的跨模块调用序列
4. **异常路径**：

| 异常点 | 触发条件 | 处理方式 |
|--------|----------|----------|
| 步骤2：库存不足 | `available < requested` | 返回错误，订单不创建 |
| 步骤3：风控拒绝 | 评分 < 阈值 | 标记订单为待审核 |

5. **关联模块**：反向链接到参与的模块文档

模板：`templates/flow-blueprint.tmpl.md`

同时生成 `docs/knowledge/flows/_index.md`（流程总览表）。

模板：`templates/flow-index.tmpl.md`

> **时序图注意事项**：
> - 参与者名称使用中文（如 `订单服务`），与模块文档名保持一致
> - 标注关键的请求/响应数据
> - 异常分支用 `alt/else` 或 `opt` 块表示
> - 如果某步骤是异步的（消息队列/事件），用 `-->>` 虚线箭头 + Note 标注

### 步骤 5：架构决策记录（ADR）

为步骤 0 收集到的关键技术决策创建独立的 ADR 文档，并生成决策索引。

#### 5a：创建单篇 ADR

为每个关键决策生成 `docs/knowledge/decisions/adr-NNNN-<slug>.md`。

**生成前先确认**：展示检测到的决策列表，询问用户：
- "以下决策是否需要记录？哪些需要补充或修改？"
- "每条决策有哪些备选方案？"

**ADR 格式**（MADR + 编码要点）：

```markdown
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
[问题、约束、环境]

## 决策
[所选方案及理由]

## 后果
### 正面
- **POS-001**：[优势]
### 负面
- **NEG-001**：[权衡]

## 备选方案
### [方案名称]
- **ALT-001**：**描述**：[说明]
- **ALT-002**：**拒绝理由**：[原因]

## 实施注意事项
- **IMP-001**：[关键考量]

## 参考资料
- **REF-001**：[相关文档]

## 关联
- **模块**：[关联的模块]
- **流程**：[关联的流程]
```

模板：`templates/adr.tmpl.md`

**编码要点规范**：
- `POS-XXX`：正面后果（Positive）
- `NEG-XXX`：负面后果（Negative）
- `ALT-XXX`：备选方案描述及拒绝理由（Alternative）
- `IMP-XXX`：实施注意事项（Implementation）
- `REF-XXX`：参考资料（Reference）
- 编号从 001 开始，每个 ADR 独立编号

**命名规范**：`adr-NNNN-<slug>.md`，NNNN 为 4 位顺序编号（如 `adr-0001-数据库选型.md`）。扫描 `docs/knowledge/decisions/` 目录取下一个编号。

**输入校验**：若某条决策的背景、决策内容、备选方案缺失且无法从对话中推断，标记 `<!-- HUMAN_REVIEW: 请补充... -->` 而非编造内容。

#### 5b：生成决策索引和横切关注点索引

生成 `docs/knowledge/decisions/_index.md`：
- ADR 清单表（编号、决策、状态、日期、关联模块、关联流程）
- 按主题分类的热力图
- ADR 模板引用

模板：`templates/decisions-index.tmpl.md`

生成 `docs/knowledge/crosscutting/_index.md`：
- 列出跨模块的通用关注点：错误处理、认证鉴权、日志追踪、配置管理等
- 如果已有 `docs/ARCHITECTURE.md`，提取其横切关注点章节
- 暂不展开为完整文章（留给知识库的后续深度文章生成），仅提供索引和简要说明

### 步骤 6：知识库导航索引

生成 `docs/knowledge/README.md` 作为蓝图总入口。

包含：
1. **系统全景图**（嵌入 `system-context.md` 中的 C4 Context 图或引用）
2. **按模块查阅**：10 个模块的表格（模块名、职责、参与流程数）
3. **按流程查阅**：4 条核心流程的表格（流程名、描述、涉及模块数）
4. **按决策查阅**：关键 ADR 列表
5. **快速导航**：指向各子目录 `_index.md` 的链接

模板：`templates/blueprint-index.tmpl.md`

---

## 生成后

1. 展示完整的知识库目录结构概览：

```
📦 知识库已生成：

docs/knowledge/
├── README.md                       # 知识库导航索引
├── system-context.md               # C4 Level 1: 系统全景
├── container-architecture.md       # C4 Level 2: 容器架构
├── modules/
│   ├── _index.md                   # 模块总览（{N} 个模块）
│   ├── {module-a}.md               # C4 Level 3: Component 图
│   └── ...
├── flows/
│   ├── _index.md                   # 流程总览（{M} 条流程）
│   ├── {flow-1}.md                 # Mermaid 时序图
│   └── ...
├── decisions/
│   ├── _index.md                   # ADR 索引（{K} 篇）
│   └── adr-0001-xxx.md
└── crosscutting/
    └── _index.md                   # 横切关注点索引
```

2. 确认重点：
   - "模块的 Component 图是否准确？"
   - "流程时序图的调用链是否正确？"
   - "异常路径是否覆盖了主要的失败场景？"
   - "ADR 是否覆盖了所有关键架构决策？"

3. 用户确认后，询问是否需要**回写到根 AGENTS.md**（若存在），追加知识库索引链接：
   ```markdown
   ## 知识库 [~ 推断]
   详见 [Knowledge Base](docs/knowledge/README.md)
   ```

4. 写入完成报告到 `.aidoc/knowledge/report.md`：

```markdown
# 知识库完成报告

## 生成结果
- 系统全景图：1 张（C4 Context）
- 容器架构图：1 张（C4 Container）
- 模块蓝图：{N} 个（C4 Component）
- 流程蓝图：{M} 条（Mermaid 时序图）
- ADR 草稿：{K} 篇
- 生成时间：{时间戳}

## 清单
| 文件 | 类型 | 状态 |
|------|------|------|
| docs/knowledge/README.md | 导航索引 | ✓ |
| docs/knowledge/system-context.md | C4 Context | ✓ |
| docs/knowledge/container-architecture.md | C4 Container | ✓ |
| docs/knowledge/modules/_index.md | 模块索引 | ✓ |
| docs/knowledge/modules/{name}.md | 模块蓝图 | ✓（×{N}） |
| docs/knowledge/flows/_index.md | 流程索引 | ✓ |
| docs/knowledge/flows/{name}.md | 流程蓝图 | ✓（×{M}） |
| docs/knowledge/decisions/_index.md | ADR 索引 | ✓ |
| docs/knowledge/crosscutting/_index.md | 横切索引 | ✓ |

## 待人工补充
{汇总所有需要人工补充的内容}
```

## 幂等性

如果 `docs/knowledge/` 目录已存在：
- 不静默覆盖任何文件
- 列出已有文件，询问用户对每个文件的处理策略：
  - **跳过**：保留现有
  - **覆盖**：重新生成
  - **合并**：保留现有内容，仅更新指定的图/表格
- 支持增量更新：可以只重新生成某个模块的 Component 图或某条流程的时序图

## 文件约束

- 每份模块蓝图 ≤ 150 行
- 每份流程蓝图 ≤ 120 行
- 时序图 ≤ 30 个交互步骤（过多则考虑拆分流程）
- 所有 Mermaid 代码块正确标注语言（`mermaid`）
- 所有模块/流程文档间的交叉引用使用相对路径链接
