# AI 时代 Harness 工程实践手册

*生成日期：2026-06-06 | 配套理论报告：report.md*

---

## 实践一：搭建 AI 代码的 CI/CD 质量门禁（30 分钟可落地）

### GitHub Actions 完整配置

```yaml
# .github/workflows/ai-code-quality.yml
name: AI Code Quality Gates

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  hard-gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # === Layer 1: Lint（不可协商，失败阻断合并）===
      - name: Lint
        run: npm run lint

      # === Layer 2: 静态分析（AI 强化规则）===
      - name: SonarQube Scan (AI-hardened profile)
        uses: SonarSource/sonarqube-scan-action@v4
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        with:
          args: >
            -Dsonar.qualitygate.wait=true
            -Dsonar.projectKey=myproject

      # === Layer 3: 安全扫描（SAST + 密钥检测）===
      - name: Semgrep SAST
        run: |
          semgrep scan --config=auto --error --metrics=off .

      - name: Secret Detection
        uses: gitleaks/gitleaks-action@v2

      # === Layer 4: 测试 + 覆盖率门槛 ===
      - name: Test with coverage
        run: npm test -- --coverage

      - name: Coverage Gate（AI 代码 90%）
        uses: infracost/coverage-gate@v1
        with:
          threshold: 90
          scope: new-code

      # === Layer 5: 依赖安全 ===
      - name: Dependency Audit
        run: |
          npm audit --audit-level=high
          # 🚨 关键：检测幻觉包
          npx can-i-ignore-scripts || echo "::warning::New install scripts detected"
```

### SonarQube AI 强化质量配置文件

```properties
# sonar-project.properties
sonar.projectKey=myproject
sonar.qualitygate.wait=true
sonar.coverage.exclusions=**/*.test.*,**/*.spec.*
sonar.coverage.minCoverage=90
sonar.python.cognitiveComplexity.threshold=8
```

---

## 实践二：CLAUDE.md —— 最轻量的 Harness 层（5 分钟见效）

### 关键原则（Anthropic 官方指南）

- ~200 行以内：模型能可靠遵循约 150-200 条指令
- `IMPORTANT:` / `YOU MUST NOT:` 前缀显著提高遵循率
- CLAUDE.md 是建议，Hook 是强制执行
- 每次纠正 Claude 后让它更新 CLAUDE.md

### 生产级模板

```markdown
# CLAUDE.md

## 重启规则
- 后端（Go）：每次修改后必须重启。`go run cmd/server/main.go`
- 前端（Vue/TS）：Vite HMR 自动热更新，无需重启

## 命令
- 全栈：`make dev`
- 构建：`make build`
- 测试：`make test`

## 关键架构规则
- 后端：手动 DI 在 cmd/server/main.go
- Repository 构造函数返回 interface；mock 使用内存 map[string]*Model
- 前端类型统一在 src/types/index.ts
- Pinia stores 测试：setActivePinia(createPinia()) in beforeEach

## YOU MUST NOT
- 测试中连接生产数据库
- 提交 config.yaml 中的 API key
- 直接修改 node_modules
```

---

## 实践三：Spec-First 开发流 —— 从 Vibe 到生产

### 标准 4 阶段工作流

```
PLAN → IMPLEMENT → TEST → REVIEW
/create-plan  /execute-plan  /writing-test  /code-review
```

### Spec 模板

```markdown
# Feature: [功能名]

## 输入
- [明确列出输入数据格式]

## 期望输出
- [明确列出输出格式和约束]

## 验收条件
- [ ] 条件 1
- [ ] 条件 2

## 技术约束
- [语言/框架/依赖限制]
```

关键洞察（NearForm 实战）：500-token 聚焦 Spec 优于 3000-token 文档。Chunking 比全面性重要。

---

## 实践四：多 Agent 验证流水线

### agent-validator

```bash
npm install -g agent-validator
agent-validator init
```

```yaml
# .validator/config.yml
entry_points:
  - path: "src/"
    checks:
      - build: { command: "npm run build" }
      - lint: { command: "npx biome check src" }
      - test: { command: "npm test" }
      - security: { command: "semgrep scan --config auto --error src" }
    reviews:
      - code-quality:
          builtin: code-quality
          model: claude-sonnet-4-6
      - security:
          builtin: security-and-errors
          model: gpt-5.3-codex  # 跨模型交叉审查
```

### code-review-graph

```bash
pip install code-review-graph
code-review-graph install
code-review-graph build
```

38x-528x token 缩减，100% recall 影响分析。

### Code Scalpel

```bash
uvx codescalpel mcp
```

语法感知守门人——AI 代码写入磁盘前解析拦截。

---

## 实践五：生产级 Phase-Gate 模式

```
Phase 1: 安装依赖 → 验证构建 → git commit
Phase 2: 创建模型 → 验证测试 → git commit
Phase 3: 实现逻辑 → 验证集成 → git commit
Phase 4: 代码审查 → 修复问题 → git commit
```

### 上下文退化警告信号

- 重复读取同一文件 3 次以上
- 与之前决策矛盾
- 忘记初始需求
- 循环检查同一代码无进展

### 两错原则

同一问题纠正超过两次 → /clear + 重启会话。

---

## 实践六：Hook —— 确定性强制执行

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "command": "npx biome check --fix \"$CLAUDE_FILE_PATH\" 2>/dev/null || true"
    }],
    "PreToolUse": [{
      "matcher": "Bash",
      "command": "if echo \"$CLAUDE_BASH_COMMAND\" | grep -qE 'rm -rf|DROP TABLE'; then echo '🚨 危险操作需确认'; exit 1; fi"
    }]
  }
}
```

---

## 实践七：Ratchet 原则的日常落地

每次 AI 犯错，不在聊天里修，而在 Harness 层永久修复。

渐进升级路径：
```
CLAUDE.md 规则 → Hook → CI 检查 → 全局规则
```

---

## 实践八：风险分层的 AI 使用策略

### 🟢 低风险 — 自由使用
- 脚手架代码、文档生成、单元测试补充、代码格式化/重构

### 🟡 中风险 — Spec + 审查
- 业务逻辑、API 端点、数据库迁移、第三方库集成

### 🔴 高风险 — 设计文档 + 多 Agent 验证 + 人工审批
- 认证/授权、支付/计费、数据删除、生产基础设施

---

## 最小可行实践路线图

| 时间 | 投入 | 产出 |
|------|------|------|
| 今天 | 30 分钟写 CLAUDE.md | AI 不再犯同样错误 |
| 本周 | 1 小时配 CI 门禁 | PR 自动阻断明显问题 |
| 本月 | 2 小时引入交叉验证 | 多 Agent 验证上线 |
| 本季度 | 为高风险模块写 Spec→Contract→验证 | Vibe → 生产级 |

---

## 参考工具索引

| 工具 | 安装 | 用途 |
|------|------|------|
| agent-validator | `npm i -g agent-validator` | 多 Agent 交叉验证 |
| code-review-graph | `pip install code-review-graph` | 结构化代码审查 |
| Code Scalpel | `uvx codescalpel mcp` | 语法守门人 |
| Athena | GitHub: bencrooks-dev/Athena | 规范化 AI 工作流 |
| ai-workflow-init | `npx ai-workflow-init` | 标准化 Plan/Implement/Test/Review |

---

## 参考来源

- [Anthropic: CLAUDE.md 官方指南](https://support.claude.com/en/articles/14553240-give-claude-context-claude-md-and-better-prompts)
- [Faros: Harness Engineering 2026](https://www.faros.ai/blog/harness-engineering)
- [Datadog: Harness-First Agents](https://www.datadoghq.com/blog/ai/harness-first-agents/)
- [NearForm: Spec-Driven Development 实战](https://nearform.com/digital-community/why-ill-never-go-back-to-vibe-coding-a-developers-case-for-spec-driven-development/)
- [Loiane: Vibe Coding Production-Ready](https://loiane.com/2026/03/vibe-coding-with-specs-driven-feedback-loops/)
- [SitePoint: Production Vibe Coding Workflow](https://www.sitepoint.com/production-vibe-coding-workflow/)
- [SitePoint: Claude Code in Production](https://www.sitepoint.com/claude-code-in-production-how-to-keep-long-runs-stable/)
- [Athena Workflow Orchestrator](https://github.com/bencrooks-dev/Athena)
- [agent-validator](https://github.com/Codagent-AI/agent-validator)
- [Code Scalpel](https://github.com/3D-Tech-Solutions/code-scalpel)
