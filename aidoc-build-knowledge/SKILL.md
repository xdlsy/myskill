---
name: aidoc-build-knowledge
description: 为代码仓构建知识库（Knowledge Base），使用 Mermaid + C4 模型 + ADR 承载系统架构图、模块内部架构、跨模块流程图和架构决策记录。支持独立使用，也可作为 aidoc-build 阶段 3 的增强步骤。输出到 docs/knowledge/ 目录。
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

### 步骤 3：模块蓝图（C4 Level 3: Component）—— 派发子 Agent

为步骤 0 收集到的每个模块，**派发独立子 Agent** 并调用 `aidoc-document-module` skill 生成 `docs/knowledge/modules/<module-name>.md`。

**派发策略**：
- 所有模块子 Agent **并行派发**（互不依赖）
- 每个子 Agent 携带该模块的完整上下文（名称、技术栈、组件清单、接口表、关联流程、关联 ADR）
- 子 Agent 自动处理幂等性（若目标文件已存在则询问处理策略）

**子 Agent 调用示例**：
```
Agent prompt: "使用 aidoc-document-module skill 为模块 [{模块名}] 生成知识文档。
模块信息如下：
- 名称：{模块名}
- 技术栈：{技术栈}
- 职责：{一句话描述}
- 内部组件：{组件清单}
- 对外接口（入站/出站）：{接口表}
- 关联流程：{流程列表}
- 关联 ADR：{ADR 列表}"

子 Agent 会自动：
1. 调用 aidoc-document-module skill 执行发现→生成→更新索引→确认流程
2. 生成 C4 Component 图 + 对外接口表 + 关联流程表
3. 更新 docs/knowledge/modules/INDEX.md
```

**等待所有模块子 Agent 完成后**，主 Agent 汇总结果并生成 `docs/knowledge/modules/INDEX.md`（模板：`templates/module-index.tmpl.md`）。

> **并行安全**：子 Agent 仅生成各自的 `<module-name>.md` 文件，INDEX.md 由主 Agent 统一处理，避免竞态。
> 
> 模块蓝图的具体结构和模板由 `aidoc-document-module` skill 定义，详见该 skill 的步骤 1。

### 步骤 4：流程蓝图（Runtime View）—— 派发子 Agent

为步骤 0 收集到的每条核心流程，**派发独立子 Agent** 并调用 `aidoc-document-flow` skill 生成 `docs/knowledge/flows/<flow-name>.md`。

**派发策略**：
- 所有流程子 Agent **并行派发**（互不依赖）
- 每个子 Agent 携带该流程的完整上下文（名称、类型、触发条件、参与模块与步骤、异常路径）
- 子 Agent 自动处理幂等性（若目标文件已存在则询问处理策略）

**子 Agent 调用示例**：
```
Agent prompt: "使用 aidoc-document-flow skill 为流程 [{流程名}] 生成知识文档。
流程信息如下：
- 名称：{流程名}
- 类型：{同步请求/异步事件/定时任务/混合}
- 触发条件：{触发描述}
- 目标：{流程目标}
- 参与模块与步骤：{步骤表}
- 异常路径：{异常路径表}"

子 Agent 会自动：
1. 调用 aidoc-document-flow skill 执行发现→生成→更新索引→确认流程
2. 生成 Mermaid 时序图 + 参与模块表 + 异常路径表
3. 更新 docs/knowledge/flows/INDEX.md
```

**等待所有流程子 Agent 完成后**，主 Agent 汇总结果并生成 `docs/knowledge/flows/INDEX.md`（模板：`templates/flow-index.tmpl.md`）。

> **并行安全**：子 Agent 仅生成各自的 `<flow-name>.md` 文件，INDEX.md 由主 Agent 统一处理，避免竞态。
>
> 流程蓝图的具体结构和模板由 `aidoc-document-flow` skill 定义，详见该 skill 的步骤 1。

### 步骤 5：架构决策记录（ADR）

为步骤 0 收集到的关键技术决策创建独立的 ADR 文档，并生成决策索引。

#### 5a：创建单篇 ADR —— 派发子 Agent

为步骤 0 收集到的每个关键决策，**派发独立子 Agent** 并调用 `aidoc-writing-adr` skill 生成 `docs/knowledge/decisions/adr-NNNN-<slug>.md`。

**派发策略**：
- 所有 ADR 子 Agent **并行派发**（互不依赖）
- 每个子 Agent 携带该决策的完整上下文（标题、背景、决策内容、备选方案）
- 子 Agent 自动扫描目录取下一个 ADR 编号，处理幂等性

**子 Agent 调用示例**：
```
Agent prompt: "使用 aidoc-writing-adr skill 为决策 [{决策标题}] 创建 ADR 文档。
决策信息如下：
- 决策标题：{标题}
- 背景上下文：{背景}
- 决策内容：{决策}
- 备选方案：{备选方案列表}
- 关联模块：{模块列表}
- 关联流程：{流程列表}"

子 Agent 会自动：
1. 调用 aidoc-writing-adr skill 执行输入校验→生成 ADR→写入文件流程
2. 使用 MADR 格式 + 编码要点（POS/NEG/ALT/IMP/REF）
3. 关联相关模块和流程文档
```

**等待所有 ADR 子 Agent 完成后**，主 Agent 汇总结果。

**生成前先确认**：展示检测到的决策列表，询问用户：
- "以下决策是否需要记录？哪些需要补充或修改？"
- "每条决策有哪些备选方案？"

> ADR 的格式（MADR + 编码要点 POS/NEG/ALT/IMP/REF）、命名规范、输入校验由 `aidoc-writing-adr` skill 定义，详见该 skill。

#### 5b：生成决策索引和横切关注点索引

生成 `docs/knowledge/decisions/INDEX.md`：
- ADR 清单表（编号、决策、状态、日期、关联模块、关联流程）
- 按主题分类的热力图
- ADR 模板引用

模板：`templates/decisions-index.tmpl.md`

生成 `docs/knowledge/crosscutting/INDEX.md`：
- 列出跨模块的通用关注点：错误处理、认证鉴权、日志追踪、配置管理等
- 如果已有 `docs/ARCHITECTURE.md`，提取其横切关注点章节
- 暂不展开为完整文章（留给知识库的后续深度文章生成），仅提供索引和简要说明

### 步骤 6：知识库导航索引

生成 `docs/knowledge/AGENTS.md` 作为蓝图总入口。

包含：
1. **系统全景图**（嵌入 `system-context.md` 中的 C4 Context 图或引用）
2. **按模块查阅**：10 个模块的表格（模块名、职责、参与流程数）
3. **按流程查阅**：4 条核心流程的表格（流程名、描述、涉及模块数）
4. **按决策查阅**：关键 ADR 列表
5. **快速导航**：指向各子目录 `INDEX.md` 的链接

模板：`templates/blueprint-index.tmpl.md`

---

## 生成后

1. 展示完整的知识库目录结构概览：

```
📦 知识库已生成：

docs/knowledge/
├── AGENTS.md                       # 知识库导航索引
├── system-context.md               # C4 Level 1: 系统全景
├── container-architecture.md       # C4 Level 2: 容器架构
├── modules/
│   ├── INDEX.md                   # 模块总览（{N} 个模块）
│   ├── {module-a}.md               # C4 Level 3: Component 图
│   └── ...
├── flows/
│   ├── INDEX.md                   # 流程总览（{M} 条流程）
│   ├── {flow-1}.md                 # Mermaid 时序图
│   └── ...
├── decisions/
│   ├── INDEX.md                   # ADR 索引（{K} 篇）
│   └── adr-0001-xxx.md
└── crosscutting/
    └── INDEX.md                   # 横切关注点索引
```

2. 确认重点：
   - "模块的 Component 图是否准确？"
   - "流程时序图的调用链是否正确？"
   - "异常路径是否覆盖了主要的失败场景？"
   - "ADR 是否覆盖了所有关键架构决策？"

3. 用户确认后，询问是否需要**回写到根 AGENTS.md**（若存在），追加知识库索引链接：
   ```markdown
   ## 知识库 [~ 推断]
   详见 [Knowledge Base](docs/knowledge/AGENTS.md)
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
| docs/knowledge/AGENTS.md | 导航索引 | ✓ |
| docs/knowledge/system-context.md | C4 Context | ✓ |
| docs/knowledge/container-architecture.md | C4 Container | ✓ |
| docs/knowledge/modules/INDEX.md | 模块索引 | ✓ |
| docs/knowledge/modules/{name}.md | 模块蓝图 | ✓（×{N}） |
| docs/knowledge/flows/INDEX.md | 流程索引 | ✓ |
| docs/knowledge/flows/{name}.md | 流程蓝图 | ✓（×{M}） |
| docs/knowledge/decisions/INDEX.md | ADR 索引 | ✓ |
| docs/knowledge/crosscutting/INDEX.md | 横切索引 | ✓ |

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

- 所有 Mermaid 代码块正确标注语言（`mermaid`）
- 所有文档间的交叉引用使用相对路径链接
- 模块蓝图、流程蓝图、ADR 的具体约束详见各自子 skill（`aidoc-document-module`、`aidoc-document-flow`、`aidoc-writing-adr`）
