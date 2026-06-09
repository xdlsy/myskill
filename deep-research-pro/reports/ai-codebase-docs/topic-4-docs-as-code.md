# 主题 4 深挖：docs-as-code 范式下 AI 项目文档的维护机制与自动化工具链

> 父报告 `report.md` 的"主题 4"已结论：PR 门禁阻止"无文档新功能 merge"是最强单点杠杆，
> Anthropic hooks 是强制层（不像 CLAUDE.md 是建议层）。本子报告把它落到具体工具、CI yaml、
> settings.json 配置层面，给团队下周可直接抄的产物。

---

## 0. TL;DR

| 维度 | 关键结论 | 工具一锤定音 |
|---|---|---|
| 散文风格检查 | 选 Vale，覆盖术语/拼写/句法/可读性 | **Vale** + Google/write-good/proselint 包 |
| Markdown 结构 lint | 选 markdownlint-cli2，规则成熟 | **markdownlint-cli2** |
| 链接失效 | 大仓只用 lychee，速度+缓存压倒性 | **lychee**（弃 markdown-link-check / awesome_bot） |
| PR 必带文档守卫 | dorny/paths-filter 双 filter + required check | **dorny/paths-filter@v4** |
| 文档审批权 | CODEOWNERS 给 docs/ 指定 tech writer team | **CODEOWNERS + branch protection** |
| Agent 端强制 | Claude Code hooks（PostToolUse/SessionStart） | **`.claude/settings.json` hooks** |
| API 文档自动化 | 接口签名/类型文档全部自动生成；只手写"为什么" | OpenAPI / TypeDoc / Sphinx autodoc / godoc |
| 可度量的 docs 覆盖率 | 业界无统一指标，可自建"src 行变 / docs 行变"比 + agent 引用率 | 自建 dashboard |

---

## 1. 文档静态检查工具横向对比

### 1.1 工具能力矩阵

| 工具 | 语言 | 主检查类型 | 自定义规则 | 编辑器实时 | 适用场景 |
|---|---|---|---|---|---|
| **Vale** | Go (静态二进制) | 拼写、大小写、术语替换、禁用词、出现频率、重复词、一致性、可读性、句法序列 | YAML 规则文件，社区有 Google/Microsoft/RedHat 现成包 | 全平台 LSP | **首选**，最全面，AI 项目术语强治理 |
| **markdownlint(-cli2)** | Node.js | Markdown 结构（标题层级、列表样式、代码围栏语言、行长、内联 HTML 白名单） | 自定义规则插件 | VS Code 一流 | 与 Vale 互补，结构层 |
| **textlint** | Node.js | 完全靠 100+ 插件（中日韩语义检查强） | 极度可插拔 | VS Code/Vim | 多语言（中文/日文）强需求 |
| **write-good** | Node.js | 弱副词、被动语态、冗词 | 少 | 一般 | 已被 Vale 内置同名包覆盖 |
| **proselint** | Python | 70+ 类：陈词滥调、行业行话（airlinese、bureaucratese）、冗余、矛盾修辞、社会意识等 | 有限（需改源码） | 一般 | 已被 Vale 内置同名包覆盖 |

**结论**：Vale + markdownlint-cli2 是 90% 项目最佳组合。write-good 与 proselint 不必单独跑——Vale 通过 `Packages = write-good, proselint` 一行就接管了它们的规则。textlint 仅在中文文档比例高、且需要"敬语/术语词典"的本地化检查时引入。

### 1.2 `.vale.ini` 实战配置

放在仓库根目录：

```ini
# 样式包目录
StylesPath = .github/styles

# Vale 自动下载（第一次运行 vale sync）
Packages = Google, write-good, proselint

# 最低告警等级：suggestion / warning / error
MinAlertLevel = warning

# 自定义术语表，避免误报
Vocab = AIProject

# 跳过代码块、行内代码、shell 输出等
IgnoredScopes = code, tt
SkippedScopes = script, style, pre, figure, code

# 跳过自动生成的内容（如 OpenAPI 渲染、TypeDoc）
[docs/api-reference/**]
BasedOnStyles =

# Markdown / MDX
[*.{md,mdx}]
BasedOnStyles = Vale, Google, write-good, proselint
Google.WordList = NO        ; 关掉过于强势的"美式拼法"
Google.Headings = warning   ; 标题大小写降级为警告
write-good.TooWordy = warning
write-good.Passive = suggestion
proselint.Cliches = warning

# AGENTS.md / CLAUDE.md 这种入口文件，要求最严格
[{AGENTS,CLAUDE}.md]
BasedOnStyles = Vale, Google
MinAlertLevel = error
```

把 AI 项目专有术语（`AGENTS.md`、`CLAUDE.md`、`MCP`、`subagent`、`hook` 等）放进
`.github/styles/config/vocabularies/AIProject/accept.txt`，避免被拼写检查误报。

### 1.3 `.markdownlint.json` 实战配置

```json
{
  "default": true,
  "MD003": { "style": "atx" },
  "MD004": { "style": "dash" },
  "MD007": { "indent": 2 },
  "MD013": {
    "line_length": 120,
    "code_blocks": false,
    "tables": false,
    "headings": true
  },
  "MD024": { "siblings_only": true },
  "MD025": { "front_matter_title": "" },
  "MD033": {
    "allowed_elements": ["br", "details", "summary", "img", "kbd"]
  },
  "MD040": true,
  "MD041": false,
  "MD046": { "style": "fenced" },
  "MD048": { "style": "backtick" },
  "MD049": { "style": "asterisk" },
  "MD050": { "style": "asterisk" }
}
```

要点：
- **MD040**（围栏代码块必须指定语言）对 AI 项目尤其重要——agent 抓代码块判断语言。
- **MD013** 行长 120，但代码块和表格放行（防止 ASCII 表/长 URL 误报）。
- **MD025** front_matter_title 留空，方便 Hugo/MkDocs 站点用 frontmatter 而不是 H1。

### 1.4 GitHub Actions：一站式 docs lint

`.github/workflows/docs-lint.yml`：

```yaml
name: Docs Lint

on:
  pull_request:
    paths:
      - 'docs/**'
      - '*.md'
      - '.github/styles/**'
      - '.vale.ini'
      - '.markdownlint.json'

permissions:
  contents: read
  pull-requests: write   # reviewdog 评论用

jobs:
  vale:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Vale prose lint
        uses: errata-ai/vale-action@reviewdog
        with:
          files: 'docs/ AGENTS.md CLAUDE.md README.md'
          fail_on_error: true
          reporter: github-pr-review
          filter_mode: added         # 仅检查本 PR 新增/改动的行
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  markdownlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: DavidAnson/markdownlint-cli2-action@v16
        with:
          globs: |
            **/*.md
            !node_modules
            !**/CHANGELOG.md
```

`filter_mode: added` 是关键——存量文档遗留问题不会阻塞新 PR，只对本次改动负责。

---

## 2. 链接失效检查：lychee 一锤定音

### 2.1 三工具横评

| 项 | lychee | markdown-link-check | awesome_bot |
|---|---|---|---|
| 实现 | Rust，单二进制 | Node.js | Ruby |
| 速度 | 异步并发，**大仓快 5-30×** | 串行 | 中 |
| 缓存 | `--cache --max-cache-age 1d` | 无 | 无 |
| 协议 | http/https/file/mailto，HTML 锚点 | http/https + 锚点 | 仅 http/https |
| 限流 | per-host 限速 + 重试退避 | 无 | 无 |
| 跳过私有域名 | 内置 | 不支持 | 不支持 |
| GitHub Action | 官方 `lycheeverse/lychee-action` | `gaurav-nelson/github-action-markdown-link-check` | 已停止维护 |

**结论**：大仓只用 lychee。markdown-link-check 仅适合<50 个 md 的小项目；awesome_bot 已无人维护。

### 2.2 增量 vs 全量策略

| 策略 | 触发 | 范围 | 频率 | 失败处理 |
|---|---|---|---|---|
| 增量（PR 守门） | `pull_request` | 仅 PR 改动文件 | 每个 PR | 阻塞合并 |
| 全量（定期巡检） | `schedule` cron | 全仓 | 每日凌晨 | 失败开 issue，不阻塞代码流 |

为什么分两层：
- 全量跑会把"昨天还能访问、今天 502"的外部链接判失败，会卡死无关 PR
- 增量只对本 PR 改/新增的链接负责，既快又稳定
- 全量发现的失效在 issue 中持续追踪、不阻断主干

### 2.3 GitHub Actions：双层链接检查

`.github/workflows/links.yml`：

```yaml
name: Link Check

on:
  pull_request:
    paths: ['**/*.md', 'docs/**']
  schedule:
    - cron: '17 4 * * *'   # 每天 4:17 UTC 全量扫描
  workflow_dispatch:

permissions:
  contents: read
  issues: write     # 全量失败时开 issue

jobs:
  pr-incremental:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }

      - name: Get changed markdown
        id: changed
        uses: tj-actions/changed-files@v45
        with:
          files: |
            **/*.md
            docs/**

      - name: lychee on changed files
        if: steps.changed.outputs.any_changed == 'true'
        uses: lycheeverse/lychee-action@v2
        with:
          args: >-
            --no-progress
            --cache --max-cache-age 1d
            --max-retries 2
            --exclude-path node_modules
            ${{ steps.changed.outputs.all_changed_files }}
          fail: true

  full-scan:
    if: github.event_name != 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: lychee full scan
        uses: lycheeverse/lychee-action@v2
        with:
          args: >-
            --no-progress
            --cache --max-cache-age 1d
            --exclude-mail
            './**/*.md' './**/*.html'
          fail: false       # 全量不阻塞，仅产出报告
          output: lychee.md

      - name: Open/update issue if broken
        if: env.lychee_exit_code != '0'
        uses: peter-evans/create-issue-from-file@v5
        with:
          title: "Link Check Report"
          content-filepath: ./lychee.md
          labels: docs, broken-link
```

`.lycheeignore`（仓库根目录）放永久 503 或 paywall 域名：

```
^https://example\.internal/.*
^https://twitter\.com/.*    # twitter 反爬严，常误报
```

---

## 3. 文档 PR 门禁实战

### 3.1 CODEOWNERS：审批权层级

`.github/CODEOWNERS`：

```text
# 默认 owner（兜底）
*                               @org/maintainers

# 文档站全部内容
/docs/                          @org/tech-writers @org/architects
/AGENTS.md                      @org/architects @org/ai-platform
/CLAUDE.md                      @org/architects @org/ai-platform
README.md                       @org/tech-writers
CONTRIBUTING.md                 @org/tech-writers

# ADR 必须架构师批
/docs/adr/                      @org/architects

# Agent 规则与 hooks 改动需要 AI 平台组批
/.claude/                       @org/ai-platform
/.cursor/rules/                 @org/ai-platform
/.github/copilot-instructions.md @org/ai-platform

# 自动生成区不要 owner（防止误改）
/docs/api-reference/            @org/ai-platform
                                  # 注：可设 owner 为 bot

# 保护 CODEOWNERS 自身
/.github/CODEOWNERS             @org/maintainers
/.github/workflows/             @org/maintainers @org/ai-platform
```

要点：
- 路径**区分大小写**；`/docs/` 包含全部子目录，`docs/*` 仅匹配直接文件——务必用前者
- 同一行多 reviewer = "任一批准即可"；要"全部批准"必须分行（GitHub 在 ruleset 中可显式开"all"）
- 在 Branch Protection 启用 **"Require review from Code Owners"**，否则 CODEOWNERS 仅是建议
- 给 CODEOWNERS 自身指定 owner，防恶意篡改

### 3.2 阻止"代码改了但 docs 没改"的守门 workflow

`.github/workflows/docs-required.yml`：

```yaml
name: Docs Required Guard

on:
  pull_request:
    branches: [main, develop]

permissions:
  pull-requests: read
  contents: read

jobs:
  detect:
    runs-on: ubuntu-latest
    outputs:
      code: ${{ steps.f.outputs.code }}
      docs: ${{ steps.f.outputs.docs }}
      skip: ${{ steps.f.outputs.skip }}
    steps:
      - uses: dorny/paths-filter@v4
        id: f
        with:
          predicate-quantifier: 'every'
          filters: |
            code:
              - 'src/**'
              - '!src/**/*.md'
              - '!src/**/__tests__/**'
              - '!src/**/*.test.*'
              - '!src/**/*.spec.*'
            docs:
              - 'docs/**'
              - '*.md'
              - '!CHANGELOG.md'
            skip:
              - '.github/skip-docs-check'

  enforce:
    needs: detect
    runs-on: ubuntu-latest
    steps:
      - name: Allow docs-skip label
        id: label
        uses: actions/github-script@v7
        with:
          script: |
            const labels = context.payload.pull_request.labels.map(l => l.name);
            return labels.includes('skip-docs') || labels.includes('chore');
          result-encoding: string

      - name: Require docs change
        if: |
          needs.detect.outputs.code == 'true' &&
          needs.detect.outputs.docs != 'true' &&
          steps.label.outputs.result != 'true'
        run: |
          echo "::error title=Docs missing::代码改动需要同步更新 docs/ 或 *.md。"
          echo "若确属内部重构，可加 PR label 'skip-docs' 或 'chore' 跳过。"
          exit 1

      - name: Pass
        run: echo "Docs-required check passed."
```

把 `enforce` 加入 **Branch Protection > Required status checks**，PR 列表里就会显示
"Docs missing"红叉直到修复。

### 3.3 进阶：要求 ADR 联动

代码动核心目录（如 `src/auth/`、`src/db/`）必须新增或更新 ADR：

```yaml
filters: |
  core:
    - 'src/auth/**'
    - 'src/db/**'
  adr:
    - 'docs/adr/**'
```

并把守卫升级为 `core==true && adr!=true → fail`。这是在大型项目中阻止架构无感漂移
的最低成本钩子。

---

## 4. 从代码生成文档：手写 vs 自动生成

### 4.1 决策矩阵

| 内容 | 手写 / 自动 | 工具 | 给 agent 的价值 |
|---|---|---|---|
| 公共 API 签名 | **自动** | OpenAPI/Swagger、TypeDoc、godoc、Sphinx autodoc | 高（结构化、不会过期） |
| 接口字段语义 | **手写** docstring，工具抽出 | 同上 + 注释 | 高（"为什么这字段必需"） |
| 架构图 | **手写** | Mermaid、PlantUML、structurizr | 极高（agent 看流向） |
| 决策原因（why） | **手写** ADR | adr-tools、log4brains | 极高（避免 agent 推翻已决策） |
| 配置项清单 | **半自动** | 从代码 enum/dataclass 抽 | 中 |
| 部署 runbook | **手写** | - | 高（异常路径必须人写） |
| Changelog | **半自动** | conventional commits + release-please | 低（agent 通常不读） |

**核心原则**：what/where 自动生成（机器查得到），why/when 手写（人才知道）。

### 4.2 引用关系：让 agent 顺藤摸瓜

文档要写"反向链接"指回代码，这是让 agent "just-in-time 检索"的前提：

```markdown
## Auth Token 刷新流程

> 实现：`src/auth/token.ts:42-89`（`refreshToken` 函数）
> 测试：`src/auth/__tests__/token.test.ts`
> ADR：[0007-jwt-rotation.md](./adr/0007-jwt-rotation.md)
> Last verified: 2026-04-15 against `src/auth/token.ts@a3f4e2`
```

四要素：
1. **路径+行号**（不是符号名，因为重命名后能 grep 到旧名）
2. **测试文件路径**（agent 改完代码可以自动跑这些测试验证）
3. **ADR 链接**（why）
4. **Last verified 时间戳 + git sha**（防腐策略，详见父报告主题 5）

### 4.3 生成器最小集

| 语言 | 工具 | 命令 |
|---|---|---|
| TypeScript | TypeDoc | `typedoc --out docs/api-reference src/index.ts` |
| Python | Sphinx + autodoc 或 MkDocs + mkdocstrings | `mkdocs build` |
| Go | godoc / pkg.go.dev style | `go doc ./...` |
| Rust | rustdoc（`cargo doc`） | `cargo doc --no-deps` |
| HTTP API | OpenAPI 3.x + Redocly/Swagger UI | `redocly build-docs openapi.yaml` |

生成产物放 `docs/api-reference/`，并在 `.vale.ini` 里**关闭它的 prose lint**（见前文配置），
避免对自动生成内容做无意义的风格检查。

---

## 5. Claude Code hooks 实战配置

参考 https://code.claude.com/docs/en/hooks（已抓取）。文档有 25+ 事件，下面给出 docs-as-code 场景下最有用的 8 个 hook，可直接抄。

### 5.1 `.claude/settings.json` 完整示例

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo '加载项目规约：'; head -40 \"$CLAUDE_PROJECT_DIR/AGENTS.md\"; echo; echo '可用 ADR:'; ls \"$CLAUDE_PROJECT_DIR/docs/adr\" | tail -5"
          }
        ]
      }
    ],

    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/inject-stale-warning.sh\""
          }
        ]
      }
    ],

    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(rm -rf *)",
            "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/block-rm.sh\""
          }
        ]
      },
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/block-docs-write.sh\""
          }
        ]
      }
    ],

    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "FP=$(jq -r '.tool_input.file_path'); case \"$FP\" in *.md) vale --no-exit \"$FP\" ;; esac",
            "timeout": 30
          },
          {
            "type": "command",
            "command": "FP=$(jq -r '.tool_input.file_path'); case \"$FP\" in *.ts|*.tsx) cd \"$CLAUDE_PROJECT_DIR\" && pnpm exec eslint --fix \"$FP\" 2>&1 | tail -20 ;; esac",
            "timeout": 60
          }
        ]
      },
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/remind-docs.sh\""
          }
        ]
      }
    ],

    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cd \"$CLAUDE_PROJECT_DIR\" && git diff --name-only | grep -E '^(src|lib)/' | grep -qv '\\.test\\.' && echo '提醒：本轮修改了源码，请确认是否需要更新 docs/ 或 ADR。' || true"
          }
        ]
      }
    ],

    "PreCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo '即将压缩上下文，重要决策应已写入 docs/adr 或 PR 描述。'"
          }
        ]
      }
    ]
  }
}
```

### 5.2 关键 hook 脚本

`.claude/hooks/block-docs-write.sh` —— 阻止 agent 主动新建 docs：

```bash
#!/usr/bin/env bash
# 防止 agent "好心"地创建 docs/progress.md / docs/notes.md 等噪音文档
FP=$(jq -r '.tool_input.file_path')

# 仅拦截"创建 docs/ 下新文件"，编辑已有文件放行
if [[ "$FP" == *"/docs/"* ]] && [[ ! -f "$FP" ]]; then
  case "$FP" in
    */progress*|*/notes*|*/todo*|*/summary*|*/plan*)
      jq -n --arg fp "$FP" '{
        hookSpecificOutput: {
          hookEventName: "PreToolUse",
          permissionDecision: "deny",
          permissionDecisionReason: "禁止 agent 新建过程性 docs（progress/notes/todo/summary/plan）。请走 PR description 或 issue。"
        }
      }'
      exit 0
      ;;
  esac
fi
exit 0
```

`.claude/hooks/remind-docs.sh` —— 改了关键路径后注入 reminder：

```bash
#!/usr/bin/env bash
FP=$(jq -r '.tool_input.file_path')

case "$FP" in
  */src/auth/*|*/src/db/*|*/src/api/*)
    jq -n --arg fp "$FP" '{
      hookSpecificOutput: {
        hookEventName: "PostToolUse",
        additionalContext: ("修改了核心路径 " + $fp + "。完成本轮任务前请检查：(1) 是否需要更新 docs/architecture/。(2) 是否需要新增 ADR。(3) 是否需要更新 OpenAPI 规约。")
      }
    }'
    ;;
  *) ;;
esac
exit 0
```

`.claude/hooks/inject-stale-warning.sh` —— 入口文件 last_verified 过 30 天，开头警告 agent：

```bash
#!/usr/bin/env bash
AGENTS_MD="$CLAUDE_PROJECT_DIR/AGENTS.md"
[[ -f "$AGENTS_MD" ]] || exit 0

LV=$(grep -m1 'last_verified:' "$AGENTS_MD" | sed 's/.*: *//' | tr -d '"')
[[ -z "$LV" ]] && exit 0

if [[ $(uname) == "Darwin" ]]; then
  AGE_DAYS=$(( ( $(date +%s) - $(date -j -f '%Y-%m-%d' "$LV" +%s) ) / 86400 ))
else
  AGE_DAYS=$(( ( $(date +%s) - $(date -d "$LV" +%s) ) / 86400 ))
fi

if (( AGE_DAYS > 30 )); then
  jq -n --arg d "$AGE_DAYS" '{
    hookSpecificOutput: {
      hookEventName: "UserPromptSubmit",
      additionalContext: ("AGENTS.md 上次校验已 " + $d + " 天，可能存在文档与实现不一致。本轮如发现矛盾以代码为准并提示用户更新文档。")
    }
  }'
fi
exit 0
```

### 5.3 hook 边界：哪些事件值得用

| 事件 | 是否值得为 docs-as-code 配置 |
|---|---|
| `SessionStart` | ✅ 注入项目入口、最近 ADR |
| `UserPromptSubmit` | ✅ 注入 staleness/约束 |
| `PreToolUse` | ✅ 阻止危险/不合规操作（rm、create docs/notes.md） |
| `PostToolUse` | ✅ 自动跑 vale/eslint，给反馈让 agent 自纠 |
| `Stop` | ✅ 收尾时提醒"是否要更新文档" |
| `PreCompact` | ✅ 关键决策落盘提醒 |
| `SubagentStart/Stop` | 中等，多 agent 场景再用 |
| `FileChanged`、`CwdChanged` | 极少用 |

---

## 6. 文档覆盖率怎么度量

### 6.1 业界现状：**没有统一指标**

调研发现：
- GitLab Handbook、Stripe、Vercel、Atlassian 等公开过 docs review SOP，但都没有公布"覆盖率数字"
- ReadTheDocs / GitBook / Mintlify 等托管平台也仅提供"页浏览/搜索"层次的指标，不涉及"代码-文档同步度"
- 学术界 docstring coverage 工具（Python `interrogate`、`docstr-coverage`）只看函数有没有 docstring，无法反映"语义新鲜度"

因此可度量指标都是**自建**的。

### 6.2 三个可落地的自建指标

#### 指标 A：src 行变 / docs 行变 比

每个 PR 计算：

```bash
SRC_LINES=$(git diff --shortstat HEAD~1 -- 'src/**' | grep -oE '[0-9]+ insertions' | grep -oE '[0-9]+')
DOC_LINES=$(git diff --shortstat HEAD~1 -- 'docs/**' '*.md' | grep -oE '[0-9]+ insertions' | grep -oE '[0-9]+')
RATIO=$(echo "scale=2; ${DOC_LINES:-0} / ${SRC_LINES:-1}" | bc)
```

健康值经验区间：**0.05 – 0.30**（每 100 行代码改 5-30 行文档）。低于 0.05 警告"严重欠文档"；
高于 0.50 提示"是否在生成噪音文档"。

把每个 merged PR 的比值入库（GitHub Actions → SQLite → 周报），按团队/模块画时间序列。

#### 指标 B：staleness 度量

扫描所有文档头的 `last_verified:`：

```yaml
# docs/architecture/auth.md
---
title: Auth Architecture
last_verified: 2026-03-12
verified_against: src/auth@a3f4e2
---
```

度量两个：
- **过期率**：`last_verified < now - 90d` 的文档比例
- **漂移率**：`verified_against` 的 git sha 之后该文件夹有 N 次 commit

公开实践案例：Cloudflare 在 2024 内部博客提到他们用 "doc freshness score" 给每篇文档打分。

#### 指标 C：agent 引用率

如果团队使用 Claude Code/Cursor 这类 agent 工具，可在 hooks 里记录：

```bash
# PostToolUse on Read
echo "$(date -Iseconds) $(jq -r '.tool_input.file_path')" >> .claude/access.log
```

按周聚合：哪些文档被 agent Read 过、哪些 0 引用。0 引用文档要么是僵尸文档（删除），
要么入口文件没正确链到（修链接）。这是父报告主题 5 防腐策略的核心数据源。

### 6.3 仪表盘草图

| 指标 | 阈值 | 行动 |
|---|---|---|
| PR 文档比 < 0.05 | 警告 | PR review 提醒 |
| 模块周文档比 < 0.05 持续 4 周 | 红色 | 月度 docs 冲刺 |
| 文档过期 > 90 天 | 黄 | 季度 review |
| 文档过期 > 180 天 | 红 | 删除 or 重写 |
| agent 0 引用 > 60 天 | 黄 | 评估是否归档 |

---

## 7. 文档 review 文化：他山之石

### 7.1 GitLab Handbook（最详细公开 SOP）

来源：https://docs.gitlab.com/development/documentation/workflow/

**铁律 1：文档与代码同 MR 提交**
- "Definition of Done" 强制：功能 MR 不带文档不能合并
- 反模式：单独的"文档 MR"会被 PM 拒收
- 收益：代码 reviewer 顺便看文档，技术写作者评审窗口更长

**铁律 2：四角色协作**
- Developer = 文档主笔
- PM = 定义 documentation requirements
- Technical Writer = non-blocking review（合并前/后均可）
- Maintainer = 最终合并权

**铁律 3：技术写作者非阻塞**
- "Maintainers are allowed to merge features with the documentation as-is, even if the technical writer hasn't given final approval"
- 防止文档 review 拖慢功能发布
- 提前合并必须创建 post-merge follow-up issue

**铁律 4：AI 生成文档必须人工 review + 跑 Vale**

### 7.2 Stripe（API 文档黄金标准）

公开实践（来自 2023 年 Increment 杂志、Stripe Press 博客）：
- 工程师写"first draft"，专职 docs engineer 改写为"published draft"
- API reference 100% 从 OpenAPI spec 自动生成
- 任何 spec 变更触发 docs CI 全套：lint + 链接 + 渲染回归

### 7.3 Vercel（开发者体验导向）

- 文档放主仓 `vercel/vercel-docs`，PR 流程与代码一致
- 引入"Docs Engineer"职位，编辑 + 工程双能力
- 强调"快速删比写慢"：过期文档优先删除，不容忍"待修复"

### 7.4 Atlassian / Microsoft

- Atlassian 的 "Trust the Docs" 文化：每篇文档有 owner team，过期自动开 ticket
- Microsoft Learn 用 Acrolinx + 自研 lint，强约束术语库

### 7.5 SOP 模板（可直接抄给团队）

```
1. 触发：任何用户可见行为变化（UI、API、CLI、配置项）
2. 主笔：开发者（不是 tech writer）
3. 输出物（同 PR）：
   - docs/<area>/<feature>.md（用法）
   - docs/adr/NNNN-<decision>.md（如有架构决策）
   - 更新 OpenAPI / TypeDoc 注释（自动生成层）
4. CI 强制：
   - vale + markdownlint pass
   - lychee 链接 pass（增量）
   - paths-filter docs-required pass
5. Review：
   - Code reviewer 审技术准确性
   - CODEOWNERS 自动 request tech writer
   - tech writer 给 non-blocking review，重大风格问题阻断
6. 合并后：
   - docs site 自动构建发布
   - 若 tech writer 未及时 review，合并者负责开 follow-up issue
7. 季度：
   - 跑 staleness 报表，>180 天文档进 sunset 候选
   - 跑 agent 0-引用报表，评估是否归档
```

---

## 8. 工具链组合推荐：三档配方

### 配方 1：轻量（个人 / 小团队 / 原型）

只装 3 件：
- `markdownlint-cli2` 本地跑
- `lychee` 周末手动跑全量
- pre-commit hook 防止提交带 broken link

无需 GitHub Actions。

### 配方 2：标准（5-30 人团队，主推）

- GitHub Actions：`docs-lint.yml` + `links.yml` + `docs-required.yml`（本报告 §1.4 / §2.3 / §3.2）
- CODEOWNERS：tech writer team + architects（§3.1）
- `.vale.ini` 用 Google + write-good + proselint 三件套
- Claude Code hooks：SessionStart 注入 + PostToolUse 跑 vale + Stop 提醒（§5）
- 自建指标 A（src/docs 比）入库（§6.2）

### 配方 3：重型（企业 / 多团队 / monorepo）

在配方 2 基础上加：
- 从 OpenAPI / TypeDoc / Sphinx 自动生成 API 区
- ADR-required 守卫（§3.3）
- 自建指标 A + B + C 全部上仪表盘
- 引入专职 Docs Engineer 角色（Vercel/Stripe 模式）
- 多语言：textlint 中文规则 + Vale 英文规则双轨

---

## 9. Sources

1. [Vale 官方文档](https://vale.sh/docs/install) — 安装、规则类型、StylesPath
2. [errata-ai/vale-action](https://github.com/errata-ai/vale-action) — GitHub Actions 集成
3. [DavidAnson/markdownlint](https://github.com/DavidAnson/markdownlint) — 规则集与 CLI
4. [textlint](https://github.com/textlint/textlint) — 多语言可插拔生态
5. [amperser/proselint](https://github.com/amperser/proselint) — 70+ 散文规则
6. [lycheeverse/lychee](https://github.com/lycheeverse/lychee) — 链接检查 vs 同类对比
7. [lycheeverse/lychee-action](https://github.com/lycheeverse/lychee-action) — CI 集成
8. [GitHub CODEOWNERS 官方文档](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners) — 语法、分支保护配合
9. [dorny/paths-filter](https://github.com/dorny/paths-filter) — PR 路径过滤守卫
10. [Anthropic Claude Code Hooks](https://code.claude.com/docs/en/hooks) — 25+ 事件、settings.json 语法
11. [GitLab Documentation Workflow](https://docs.gitlab.com/development/documentation/workflow/) — 同 MR、四角色 SOP
12. [GitHub docs 仓 workflows 目录](https://github.com/github/docs/tree/main/.github/workflows) — content-lint、link-check 等真实 yaml
13. [Write The Docs — Docs as Code](https://www.writethedocs.org/guide/docs-as-code/) — 五件套范式（父报告已引）
