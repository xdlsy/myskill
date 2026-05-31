---
name: aidoc-knowledge-init
description: 为代码仓构建知识架构骨架，包含领域能力目录（docs/skills/）、决策记录目录（docs/adr/）、经验库（docs/learnings/）、知识库（docs/knowledge/）。初始化后启用持续记录工作流（配套 aidoc-learning）。依赖阶段 0-3 产出的 AGENTS.md 和 ARCHITECTURE.md。由 aidoc-create 阶段 4 触发，也可独立使用。
---

# 知识架构构建

## 概览

在阶段 0-3 产出的结构文档基础上，构建专家库的知识骨架。四个目录分别承载：
- **领域能力**（`docs/skills/`）：可复用操作的封装
- **决策记录**（`docs/adr/`）：关键架构决策及理由
- **经验库**（`docs/learnings/`）：开发与运维中的教训，支持持续记录
- **知识库**（`docs/knowledge/`）：跨模块深层知识文章

## 前置条件

- `.aidoc/phase0/repo-profile.md` 必须存在
- 根目录 AGENTS.md 和各模块 AGENTS.md 应已生成
- `docs/ARCHITECTURE.md` 应已生成

## 步骤 1：领域能力目录 — `docs/skills/`

### 候选检测

扫描 repo 中可封装为 skill 的自动化能力：

1. **从 `scripts/` 检测**：
   - 列出所有脚本文件（`.sh`、`.py`、`.ts` 等）
   - 单脚本 + 独立用途 → 一个 skill
   - 多脚本 + 共同主题 → 一个 skill + `scripts/` 目录引用多个脚本
2. **从 AGENTS.md 检测**：搜索"自动"、"生成"、"触发"、"skill"等关键词，识别已有的工作流描述
3. **从 Makefile / package.json scripts 检测**：`make deploy`、`npm run migrate` 等非构建命令

### 生成规则

- 有明确候选 → 创建 `docs/skills/<skill-name>/SKILL.md`，使用 `templates/skill.tmpl.md`
- 无明确候选 → 仅创建 `docs/skills/AGENTS.md`（使用 `templates/skills-agents.tmpl.md`），说明 skill 概念和封装时机
- 每个 skill 的 YAML frontmatter 中 `description` 是触发关键：写明"用户说什么话时触发"

## 步骤 2：决策记录目录 — `docs/adr/`

### 决策检测

从阶段 0 画像和已有文档中搜索值得记录为 ADR 的关键技术选择：

| 检测信号 | 检测方式 | 示例 |
|---------|---------|------|
| 构建标签 / 条件编译 | `go.work.*`、`*.go` 中的 `//go:build`、Cargo features | "为什么用 build tag 解耦平台 SDK" |
| DI 框架 | 搜索 `wire`、`fx`、`inject`、手动 `New*` 构造函数 | "为什么手动 DI 而非用 wire" |
| 数据库选型 | `go.mod` / `pom.xml` 中的数据库驱动 | "为什么选择 SQLite 而非 Postgres" |
| 接口/实现分离 | repo 中 `I*` 接口 + `*Impl` 的命名模式 | "为什么 repository 用接口+私有结构体" |
| 插件架构 | `plugins/` 目录、SPI 配置、类加载器 | "为什么采用 plugin 模式" |

### 生成规则

- 为每个检测到的决策，调用 **`aidoc-create-adr`** 技能生成 `docs/adr/NNNN-title.md`，状态设为 `Proposed`
- 创建 `docs/adr/AGENTS.md` 作为索引（使用 `templates/adr-agents.tmpl.md`）
- 所有 ADR 草稿标记 `<!-- HUMAN_REVIEW: ... -->`
- 检测到 0 个候选 → 创建 README 骨架 + 1 个占位 ADR（如 "ADR-001 选择当前技术栈"），同样使用 `aidoc-create-adr` 生成

## 步骤 3：经验库 — `docs/learnings/`

### 初始化

在项目根目录创建经验库的三文件结构：

```bash
mkdir -p docs/learnings
[ -f docs/learnings/LEARNINGS.md ] || printf "# 学习记录\n\n开发过程中捕获的纠正、洞察和知识盲区。\n\n**分类**：correction | insight | knowledge_gap | best_practice\n\n---\n" > docs/learnings/LEARNINGS.md
[ -f docs/learnings/ERRORS.md ] || printf "# 错误日志\n\n命令失败和集成错误。\n\n---\n" > docs/learnings/ERRORS.md
[ -f docs/learnings/FEATURE_REQUESTS.md ] || printf "# 功能请求\n\n用户请求的功能。\n\n---\n" > docs/learnings/FEATURE_REQUESTS.md
```

切勿覆盖已有文件。如果 `docs/learnings/` 已经初始化，此操作不会产生任何效果。

### 经验提取

从已有文档中提取可沉淀的经验，写入 `docs/learnings/LEARNINGS.md`：

1. **从 CLAUDE.md** 提取：搜索"避坑"、"重启规则"、"已知问题"、"关键经验"、"千万不要"、"不要"等段落
2. **从根 AGENTS.md** 提取："禁止事项 / 常见陷阱"章节；"Do Not / Gotchas" 章节
3. **从模块 AGENTS.md** 提取：`<!-- HUMAN_REVIEW -->` 中已回填的经验性内容

### 生成规则

- 提取的经验以 `[LRN-YYYYMMDD-XXX]` 格式追加到 `docs/learnings/LEARNINGS.md`（格式详见 `aidoc-learning` 技能）
- 创建 `docs/learnings/AGENTS.md`（使用 `templates/learnings-agents.tmpl.md`）
- 若未检测到可提取的经验，创建 `docs/learnings/AGENTS.md` 骨架（预留模板条目），并注明"尚未检测到可自动提取的经验"
- `<!-- HUMAN_REVIEW -->` 标记所有 AI 推断的现象/根因/教训

## 步骤 4：知识库 — `docs/knowledge/`

### 文章生成

从 ARCHITECTURE.md 和 AGENTS.md 中提取跨模块知识：

1. **横切关注点**：将 ARCHITECTURE.md 第三部分的每个关注点生成独立文章
   - 错误处理模式 → `error-handling-patterns.md`
   - 测试策略 → `testing-strategy.md`
   - 可观测性 → `observability-patterns.md`
2. **多语言策略**（若检测到多语言 repo）：`multi-language-strategy.md`
3. **构建系统**：`build-system.md`

### 生成规则

- 创建 `docs/knowledge/AGENTS.md`（使用 `templates/knowledge-agents.tmpl.md`）
- 每篇文章 ≤300 行，包含代码示例
- 若 ARCHITECTURE.md 的某个横切关注点仅标注了 `<!-- HUMAN_REVIEW -->` 占位符，知识文章保留该占位符并注明"待人类补充"

---

## 回写入口文件

四个知识目录的索引必须可被发现——Agent 不会主动探索未知目录。用户确认后，将各目录的索引引用**写回根 AGENTS.md**（若已存在则更新）：

```markdown
## 知识库 [~ 推断]

本仓库的知识架构包含以下四个维度，Agent 应按需检索：

- **决策记录**：`docs/adr/AGENTS.md` — 关键架构决策及理由（{N} 篇）
- **经验库**：`docs/learnings/AGENTS.md` — 开发与运维踩坑教训（{N} 条）
- **知识库**：`docs/knowledge/AGENTS.md` — 跨模块深层知识文章（{N} 篇）
- **领域能力**：`docs/skills/AGENTS.md` — 可复用自动化操作（{N} 个 skill）

> 检索策略：遇到"为什么这么设计"→ 查 ADR；遇到"之前怎么解决"→ 查经验库；
> 遇到"这个模式怎么串起来"→ 查知识库；遇到"执行 X 操作"→ 查 docs/skills/。
> 持续记录：开发中遇到错误、纠正、新发现，按 `aidoc-learning` 格式记录到 `docs/learnings/`。
```

## 生成后

1. 展示完整的目录结构概览供审阅：
   ```
   📦 知识架构骨架已生成：
   
   docs/skills/
   └── ...（{N} 个 skill）
   
   docs/adr/
   ├── AGENTS.md
   └── ...（{N} 篇 ADR 草稿）
   
   docs/learnings/
   ├── LEARNINGS.md
   ├── ERRORS.md
   ├── FEATURE_REQUESTS.md
   ├── AGENTS.md
   └── ...（{N} 条初始经验）
   
   docs/knowledge/
   ├── AGENTS.md
   └── ...（{N} 篇知识文章）
   ```
2. 逐子阶段确认重点：
   - "检测到的 skill 候选是否遗漏？"
   - "ADR 覆盖了所有关键决策吗？"
   - "还有哪些踩坑经验应该沉淀到此？"
3. 用户确认后：
   a. **将知识库索引写回根 AGENTS.md**（按上述"回写入口文件"格式，若已有知识库章节则更新）
   b. 写入完成报告到 `.aidoc/phase4/report.md`：

```markdown
# 阶段 4 完成报告

## 生成结果
- docs/skills/：{N} 个 skill 目录 / 占位说明
- docs/adr/：{N} 篇 ADR 草稿
- docs/learnings/：{N} 条初始经验，已启用持续记录
- docs/knowledge/：{N} 篇知识文章
- 生成时间：{时间戳}

## 目录骨架清单
| 路径 | 类型 | 状态 |
|------|------|------|
| docs/skills/xxx/SKILL.md | skill | ✓ |
| docs/adr/AGENTS.md | ADR 索引 | ✓ |
| docs/adr/001-xxx.md | ADR 草稿 | proposed |
| docs/learnings/LEARNINGS.md | 学习记录 | ✓ |
| docs/learnings/ERRORS.md | 错误日志 | ✓ |
| docs/learnings/FEATURE_REQUESTS.md | 功能请求 | ✓ |
| docs/learnings/AGENTS.md | 经验索引 | ✓ |
| docs/knowledge/AGENTS.md | 知识索引 | ✓ |
| docs/knowledge/xxx.md | 知识文章 | ✓ |

## 待人工补充
{汇总所有 HUMAN_REVIEW 标记}
```

## 幂等性

如果目标路径已存在文件：
- 不要静默覆盖
- 展示现有文件与生成内容的差异
- 让用户选择：保留现有、合并或替换
