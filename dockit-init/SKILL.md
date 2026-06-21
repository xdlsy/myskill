---
name: dockit-init
description: 为存量代码仓生成面向 AI 的结构化文档框架，包含 AGENTS.md、ARCHITECTURE.md、知识骨架、Claude Code 适配和知识库。由"帮我生成代码仓文档"等指令触发。
---

# 代码库文档生成

## 概览

为存量代码仓生成结构化文档。每个阶段派发一个子 Agent 独立执行，主 Agent 负责编排：派发 → 审核 → 用户确认 → 下一阶段。

## 编排原则

- **一阶段一 Agent**：用 `Agent` 工具派发，避免主上下文膨胀
- **串行执行**：下游依赖上游产物，按 0→1→2→3→4→5a→5b→6 顺序
- **逐阶段确认**：子 Agent 完成后，主 Agent 审核输出呈现给用户，确认后再推进
- **幂等跳过**：阶段产物已存在且完整则跳过

---

## 工作流程

### 阶段 0：代码仓画像

派发子 Agent 调用 `dockit-repo-profile`。

```
调用 skill `dockit-repo-profile` 探索代码仓。

1. 采集语言分布、模块结构、构建系统、测试框架、CI/CD
2. 汇总诊断摘要，展示给用户确认
3. 确认后写入 .dockit/phase0/repo-profile.md
4. 返回摘要供主 Agent 审核

约束：
- 不确定的判定标注 [? 待确认]
- 若 .dockit/phase0/repo-profile.md 已存在且完整，告知主 Agent 跳过
```

→ 主 Agent 审核画像摘要，确认后进入阶段 1。

### 阶段 1：根目录 AGENTS.md

派发子 Agent 调用 `dockit-root-agents`。

```
调用 skill `dockit-root-agents` 生成根 AGENTS.md。

1. 读取 .dockit/phase0/repo-profile.md
2. 生成根 AGENTS.md（80-150 行），标注置信度：[✓ 自动] / [~ 推断] / [? 待审核]
3. 展示全文供审阅
4. 确认后写入，报告写入 .dockit/phase1/report.md

约束：
- 有冲突时展示 diff，让用户选择保留/合并/替换
- 坑点章节含 <!-- HUMAN_REVIEW --> 占位符
```

→ 主 Agent 审核 AGENTS.md 摘要，确认后进入阶段 2。

### 阶段 2：子模块 AGENTS.md

派发子 Agent 调用 `dockit-module-agents`。

```
调用 skill `dockit-module-agents` 为每个叶子模块生成 AGENTS.md。

1. 提取模块清单并确认
2. 并行派发子代理生成各模块 AGENTS.md
3. 汇总审阅，确认后写入
4. 回查根 AGENTS.md 准确性并修正不一致项
5. 报告写入 .dockit/phase2/report.md
```

→ 主 Agent 审核模块清单和回查报告，确认后进入阶段 3。

### 阶段 3：ARCHITECTURE.md

派发子 Agent 调用 `dockit-architecture`。

```
调用 skill `dockit-architecture` 生成 docs/ARCHITECTURE.md。

1. 读取 .dockit/phase0/repo-profile.md、根 AGENTS.md 和各模块 AGENTS.md
2. 按 matklad 三段式生成（≤300 行）：
   - 鸟瞰视图（2-3 句）
   - 代码地图（每模块 2-5 句，命名但不链接）
   - 横切关注点（错误处理、可观测性、测试策略、构建部署）
3. 展示全文供审阅
4. 确认后回写根 AGENTS.md 索引，报告写入 .dockit/phase3/report.md

约束：
- 不确定标注 [? 待审核]，缺失添加 <!-- HUMAN_REVIEW -->
```

→ 主 Agent 审核架构摘要，确认后进入阶段 4。

### 阶段 4：知识骨架

分两个子阶段串行执行。

#### 阶段 4a：领域能力目录

派发子 Agent 调用 `dockit-skills`。

```
调用 skill `dockit-skills` 初始化 docs/skills/。

1. 从 scripts/、AGENTS.md、Makefile 等检测可封装的自动化能力
2. 有候选 → 创建 docs/skills/<name>/SKILL.md；无候选 → 创建占位 AGENTS.md
3. 展示概览供审阅
4. 确认后回写根 AGENTS.md 索引，报告写入 .dockit/phase4a/report.md

约束：
- description 写明触发短语
```

→ 主 Agent 审核 skill 清单，确认后进入阶段 4b。

#### 阶段 4b：经验库

派发子 Agent 调用 `dockit-experience`。

```
调用 skill `dockit-experience` 初始化 docs/learnings/。

1. 初始化 LEARNINGS.md、ERRORS.md、FEATURE_REQUESTS.md（勿覆盖）
2. 从 CLAUDE.md、AGENTS.md 提取可沉淀经验
3. 展示概览供审阅
4. 确认后回写根 AGENTS.md 索引，报告写入 .dockit/phase4b/report.md

约束：
- 经验以 [LRN-YYYYMMDD-XXX] 格式追加
- AI 推断标注 <!-- HUMAN_REVIEW -->
```

→ 主 Agent 审核经验库摘要，确认后进入阶段 5。

### 阶段 5：工具链适配

分两个子阶段串行执行。

#### 阶段 5a：Claude Code 适配

派发子 Agent 调用 `dockit-claude`。

```
调用 skill `dockit-claude` 接通 Claude Code 原生加载链。

1. 生成 CLAUDE.md 桥接（@AGENTS.md，不覆盖已有内容）
2. 生成 .claude/rules/ 规则：
   - 全局规则 ×3（global-style / global-testing / architecture）
   - 模块规则 ×N（≤15 行，仅 frontmatter + @-import）
3. 创建 .claude/skills → ../docs/skills 软链接
4. 配置 dockit-learning Hook（部署 activator.sh + 注册 UserPromptSubmit）

完成后交叉验证 → 展示产物树 → 确认后写入 .dockit/phase5/report.md

约束：
- CLAUDE.md 仅做指针，不复制内容
- 规则文件只做 @-import，不复制 AGENTS.md
- settings.json 合并时保留现有配置
```

→ 主 Agent 审核 Claude Code 适配结果，确认后进入阶段 5b。

#### 阶段 5b：OpenCode 适配

派发子 Agent 调用 `dockit-opencode`。

```
调用 skill `dockit-opencode` 接通 OpenCode 原生加载链。

1. 验证 AGENTS.md 入口（OpenCode 原生读取，无需桥接）
2. 配置 dockit-learning 为 OpenCode TypeScript 插件（.opencode/plugins/）
3. 交叉验证：AGENTS.md 存在、.claude/skills/ 软链接可发现、插件已配置
4. 展示产物树，确认后写入 .dockit/phase5/opencode-report.md

前置条件：
- 已运行 dockit-claude（创建 .claude/skills/ 软链接，OpenCode 通过 ~/.claude/skills/ 路径发现 skills）

约束：
- OpenCode 原生读取 AGENTS.md，无需生成桥接文件
- TypeScript 插件机制（tui.prompt.append），不依赖 shell hook
- .claude/ 和 .opencode/ 双工具链可共存
- 报告文件与 Claude 版分开存放（opencode-report.md），避免覆盖
```

→ 主 Agent 审核 OpenCode 适配结果，确认后进入阶段 6。

### 阶段 6：知识库

派发子 Agent 调用 `dockit-knowledge`。

```
调用 skill `dockit-knowledge` 构建知识库。

1. 采集系统信息（独立模式）或从已有产物推断（管道模式）
2. 生成系统全景图（C4 Context）→ 容器架构图（C4 Container）
3. 为核心模块生成 Component 蓝图 → docs/knowledge/modules/
4. 为核心流程生成时序图 → docs/knowledge/flows/
5. 为关键决策创建 ADR → docs/knowledge/decisions/
6. 生成导航索引 → docs/knowledge/README.md
7. 展示目录树供审阅，确认后回写根 AGENTS.md，报告写入 .dockit/knowledge/report.md

约束：
- 模块蓝图 ≤150 行，流程蓝图 ≤120 行
- 交叉引用用相对路径
- 模块数 >10 时仅核心模块生成 Component 图
```

---

## 完成之后

1. 检查所有 AGENTS.md、ARCHITECTURE.md、CLAUDE.md、.claude/rules/、.opencode/plugins/ 和 docs/knowledge/
2. 填写所有 `<!-- HUMAN_REVIEW -->` 占位符
3. 提交所有生成的文件

## 幂等性

已有文件不静默覆盖。展示 diff，让用户选择保留、合并或替换。
