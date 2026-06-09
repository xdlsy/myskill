# Spec: codebase-docs — 存量代码仓入口文件自动生成 Harness

> 状态: 设计已确认 | 日期: 2026-05-20 | 产物形态: Claude Code Skill

## 1. 目标

为百万级存量代码仓自动生成 AI 编码代理需要的结构化入口文件体系：
- 根 `AGENTS.md` / `CLAUDE.md`
- 各子模块 `AGENTS.md`
- `.claude/rules/` 路径作用域规则文件
- `ARCHITECTURE.md`（matklad 三段式 Code Map）

## 2. 形态

Claude Code Skill（`codebase-docs`），由 `SKILL.md` + 采集脚本 `collect.sh` 组成。用户 `cd` 到目标仓库后执行。

## 3. 架构

```
目标仓库 ──→ collect.sh ──→ codebase-profile.json ──→ codebase-docs ──→ AGENTS.md (根)
              (采集)         (结构化中间数据)        (本 skill)      {module}/AGENTS.md (子模块)
                                                                  ARCHITECTURE.md

                                                       claude-sync ──→ CLAUDE.md → @AGENTS.md
                                                       (独立 skill,   .claude/rules/*.md → @{module}/AGENTS.md
                                                        最后执行)
```

**三层分工**：
- **codebase-docs（本 skill）**：生成所有 AGENTS.md + ARCHITECTURE.md（工具无关的纯内容）
- **claude-sync（独立 skill，最后一步执行）**：为已存在的 AGENTS.md 体系搭建 Claude Code 加载桥——CLAUDE.md + `.claude/rules/`（含全局规则和模块 @-import 索引）

## 4. collect.sh（采集脚本）

### 4.1 七类采集

| # | 类别 | 输出 | 关键工具 |
|---|---|---|---|
| 1 | 目录拓扑 | directory_tree, 每个目录的 LOC/文件数/类型 | tokei |
| 2 | 构建系统 | build_commands[{scope, cmd, cwd}] | 解析构建文件 |
| 3 | 代码风格 | style_rules{language: {key: value}} | 解析 lint 配置 |
| 4 | CI/CD | ci_pipeline_summary | 解析 CI YAML |
| 5 | Git 元信息 | commit_convention, code_owners_map | git log, CODEOWNERS |
| 6 | 测试框架 | test.framework, test.commands, test_dirs | 文件模式 + 配置文件探测 |
| 7 | 依赖关系 | build_dependencies | 语言特化工具 |

### 4.2 四种语言特化

**C/C++**：CMakeLists.txt → cmake --graphviz 近似依赖；grep `#include "` 补内部依赖；.clang-format/.clang-tidy 提取风格规则。

**Go**：go.mod → `go mod graph`（标准格式）；`internal/` 语义天然标记私有模块边界；.golangci.yml 提取 linter 列表。

**Java**：pom.xml/build.gradle 多模块声明 → `mvn dependency:tree` 或 `./gradlew dependencies`；包路径 ↔ 文件路径严格对应；checkstyle/spotbugs 配置提取。

**Python**：pyproject.toml → poetry/pip/uv 探测；pydeps 生成依赖图；ruff/flake8/black/mypy 配置提取。

## 5. codebase-profile.json

```jsonc
{
  "meta": {
    "repo_root": "<path>",
    "primary_language": "go",              // go | python | java | cpp | mixed
    "languages": ["go", "python"],
    "total_loc": 1200000,
    "module_count": 12,
    "collected_at": "2026-05-20T..."
  },
  "directory_tree": {
    "root_modules": [
      { "path": "cmd/", "type": "app-entry", "loc": 3200, "files": 18 },
      { "path": "internal/", "type": "private-lib", "loc": 45000, "files": 230 }
    ],
    "leaf_modules": [
      {
        "path": "internal/order/",
        "language": "java",
        "type": "domain",                   // domain | service | adapter | infra | app-entry | unknown
        "loc": 8500,
        "files": 42,
        "inferred_responsibility": null      // Claude 合成时填写
      }
    ]
  },
  "build_commands": [
    { "scope": "root", "cmd": "make build", "cwd": "." },
    { "scope": "module", "cmd": "go build ./...", "cwd": "internal/order/" }
  ],
  "build_dependencies": {
    "internal/order": ["internal/common", "internal/payment"]
  },
  "style_rules": {
    "go": {
      "formatter": "go fmt",
      "linter": "golangci-lint",
      "rules": { "max_line_len": 120 }
    }
  },
  "test": {
    "framework": "pytest + pytest-cov",
    "commands": [{ "scope": "root", "cmd": "pytest --cov=src -n auto" }],
    "test_dirs": ["tests/", "src/**/test/"]
  },
  "ci_pipeline": [
    { "stage": "lint", "steps": ["golangci-lint run"] },
    { "stage": "test", "steps": ["go test -race ./..."] },
    { "stage": "build", "steps": ["go build -o app ./cmd/server"] }
  ],
  "commit_convention": {
    "style": "conventional-commits",
    "sample": ["feat(order): add refund workflow", "fix(auth): token expiry"]
  },
  "code_owners": {
    "internal/order/*": "@team-order",
    "internal/payment/*": "@team-payment"
  }
}
```

## 6. Claude 合成 — 4 个 Phase

### 6.1 Phase 0：采集与确认

1. 运行 collect.sh（或用户提供已有 profile.json）
2. Claude 读 profile，呈报诊断摘要
3. 用户确认或修正（标记废弃模块等）

### 6.2 Phase 1：根入口文件

按 H2 七件套生成 `AGENTS.md`（80-150 行）：

| H2 段 | 数据源 | 出现条件 |
|---|---|---|
| Project Overview | README 摘要 + 目录结构推断 | 始终 |
| Build & Test Commands | build_commands + test.commands | 始终 |
| Coding Style | style_rules | 有 lint 配置 |
| Testing Guidelines | test.framework + test_dirs | 始终 |
| Commit & PR Guidelines | commit_convention + CI | 探测到规范 |
| Do Not / Gotchas | — | 始终，但留 `<!-- HUMAN_REVIEW -->` 占位 |
| Repository Structure | directory_tree + build_dependencies | 始终 |

> 注意：`CLAUDE.md` 的生成不在此 skill 范围内，由独立的 `claude-sync` skill 在所有 AGENTS.md 就位后统一处理。详见 §8。

### 6.3 Phase 2：子模块入口文件

逐模块处理：
1. Claude 读该模块 2-3 个代表文件
2. 推断职责 → 用户确认 → 生成 30-50 行 `{module}/AGENTS.md`
3. 识别重复结构（如 20 个 Spring Boot 模块）自动套用，但每次展示结果供纠错

### 6.4 Phase 3：ARCHITECTURE.md

matklad 三段式：
- Bird's-eye view（2-3 句）
- Code map（每模块 2-5 句，命名不链接、标注不变量）
- Cross-cutting concerns（大多留 `<!-- HUMAN_REVIEW -->`）

### 6.5 合成约束

- 每段标注置信度：`[✓ auto]` / `[~ inferred]` / `[? review]`
- 长度硬约束：根 AGENTS.md ≤150 行，子模块 ≤50 行，rules ≤80 行，ARCHITECTURE.md ≤300 行
- 幂等：已有文件只展示 diff

## 7. 实施范围

| 阶段 | 内容 | 所属 Skill | 优先级 |
|---|---|---|---|
| **MVP** | collect.sh + Phase 0/1/2（根 AGENTS.md + 子模块 AGENTS.md） | codebase-docs | P0 |
| **二期** | Phase 3（ARCHITECTURE.md） | codebase-docs | P1 |
| **最后一步** | CLAUDE.md + .claude/rules/（全局规则 + 模块 @-import 索引） | claude-sync（独立 skill） | P0 |

## 8. claude-sync（独立 skill）

`claude-sync` 是独立 skill，在所有 AGENTS.md 文件生成完毕后执行。职责：为已存在的 AGENTS.md 体系搭建完整的 Claude Code 加载桥——CLAUDE.md + `.claude/rules/`。

### 8.1 CLAUDE.md 桥接

| 场景 | 操作 |
|---|---|
| 仓库无 `CLAUDE.md` | 根目录生成一行 `@AGENTS.md` |
| 已有 `CLAUDE.md` 且内容独立 | 检测是否已引用 AGENTS.md，若未引用则在末尾追加 `@AGENTS.md` |
| monorepo（存在 `.claude/CLAUDE.md`） | 检查 `.claude/CLAUDE.md` 与根 `AGENTS.md` 的一致性，给出合并/路由建议 |

### 8.2 .claude/rules/ 生成

**核心原则：不重复已有内容**。子模块 `AGENTS.md` 已在 codebase-docs Phase 2 中生成了模块职责、特有约定、依赖关系——rules 的职责是建索引指向已有内容。

**生成产物**：

```
.claude/rules/
├── global-style.md         # paths: ["**/*.go", "**/*.py"]  | 自包含，从 profile 数据展开
├── global-testing.md       # paths: ["**/*_test.*", "tests/**"] | 自包含
├── order.md                # paths: ["internal/order/**"]   | 只有一行：
│                              @internal/order/AGENTS.md
├── payment.md              # paths: ["internal/payment/**"] | @internal/payment/AGENTS.md
└── architecture.md         # paths: [] — 全局不变量，自包含
```

**两种 rules 文件**：

| 类型 | 内容来源 | 生成方式 |
|---|---|---|
| **全局规则**（style / testing / architecture） | 自包含，从 profile 数据展开 | Claude 直接写完整内容 |
| **模块规则**（每个子模块一个 .md） | **复用 Phase 2 的 AGENTS.md** | 只写 YAML frontmatter + 一行 `@<module>/AGENTS.md` |

**工作机制**：`paths:` 决定何时加载，`@-import` 决定加载什么。一份 AGENTS.md 同时服务两套加载路径：
- `AGENTS.md` 嵌套语义：Claude 读到匹配文件时自动发现最近的 AGENTS.md（覆盖语义）
- `.claude/rules/` 显式规则：通过 `paths:` + `@-import` 精确加载（合并语义）

**paths 字段规则**：仅当规则明确对应某类文件时才设 paths；架构不变量等全局规则设 `paths: []`（始终生效）。回顾第 2 章陷阱：全局风格指南不应放在带 `paths:` 的子规则里。

**子模块 CLAUDE.md**：不需要生成——子模块规则已通过 `.claude/rules/` 的 @-import 覆盖，无需单独的 CLAUDE.md。

### 8.3 为什么拆成独立 skill

1. **关注点分离**：`codebase-docs` 生成工具无关的"内容"（AGENTS.md、Code Map），`claude-sync` 生成 Claude Code 特化的"加载桥"（CLAUDE.md、.claude/rules/）
2. **独立演进**：Claude Code 的加载语义（合并/覆盖/@-import 跳数）可能随版本变化，独立 skill 便于单独更新
3. **可单独调用**：用户手动写完 AGENTS.md 后，也可以单独跑 `claude-sync` 来重建 Claude Code 加载基础设施
