---
name: aidoc-create
description: 用于为存量代码仓生成面向AI的结构化文档框架，包含入口文件、架构文档和代码地图等。由"帮我为代码仓生成结构化文档"、"帮我分析整个代码仓并输出文档"等明确指明需要生成系统化、结构化文档的指令触发。
---

# 代码库文档生成

## 概览

为存量代码仓生成结构化的文档。全程由 LLM 自主探索，通过交互式阶段合成。

## 工作流程

### 阶段 0：采集与确认

调用 `aidoc-repo-explore` 探索代码仓画像 → `.aidoc/phase0/repo-profile.md`。若该文件已存在且内容完整则跳过。

### 阶段 1：根目录 AGENTS.md

调用 `aidoc-repo-init` 生成根目录 `AGENTS.md`（80-150 行），含置信度标注 `[✓ 自动]` / `[~ 推断]` / `[? 待审核]`。

### 阶段 2：子模块 AGENTS.md

调用 `aidoc-module-init` 为每个叶子模块生成 `AGENTS.md`（每个 30-50 行）。

### 阶段 3：ARCHITECTURE.md

调用 `aidoc-architecture` 生成 `docs/ARCHITECTURE.md`（≤300 行），使用 matklad 三段式格式：鸟瞰视图 → 代码地图 → 横切关注点。

### 阶段 4：知识架构构建

调用 `aidoc-knowledge-init` 构建专家库知识骨架，包含四个目录：
- `skills/` — 领域能力目录（可复用操作的 SKILL.md 封装）
- `docs/adr/` — 决策记录目录（MADR 格式的架构决策记录）
- `docs/learnings/` — 经验库（开发与运维踩坑教训）
- `docs/knowledge/` — 知识库（跨模块深层知识文章）

### 阶段 5：Claude Code 适配

使用子 Agent 调用 `aidoc-adapt-claude`，将 aidoc 文档体系接通 Claude Code 原生加载链：

- 生成 `CLAUDE.md` 入口桥接（`@AGENTS.md`）
- 生成 `.claude/rules/` 路径作用域规则（全局 + 模块索引）
- 部署 `activator.sh` 并注册为 `UserPromptSubmit` Hook

```bash
# 以子 Agent 方式调用
aidoc-adapt-claude
```

## 完成之后

1. 检查所有生成的 AGENTS.md 文件
2. 检查 CLAUDE.md 和 .claude/rules/ 是否正确生成
3. 填写所有 `<!-- HUMAN_REVIEW -->` 占位符
4. 提交所有生成的文件

## 幂等性

如果目标路径已存在文件：
- 不要静默覆盖
- 展示现有文件与生成内容的差异
- 让用户选择：保留现有、合并或替换
