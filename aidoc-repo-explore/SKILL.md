---
name: aidoc-repo-explore
description: 用于探索和采集代码仓画像信息，生成诊断摘要供用户确认。适用于代码仓文档化、新人上手、架构评审等场景。结果写入 .aidoc/phase0/repo-profile.md 供下游 skill（如 aidoc-create）消费。由"帮我分析代码仓"、"采集代码仓信息"、"探索项目结构"等指令触发。
---

# 代码仓探索与画像采集

## 概览

LLM 自主探索代码仓，采集代码规模、语言分布、模块结构、构建系统、测试框架、CI/CD 等关键信息，汇总为诊断摘要供用户确认。结果记入内存，供下游 skill 消费。

**纯 LLM 驱动，不依赖外部脚本。** 用 `tokei`、`ls`、`git log`、文件读取等原生工具完成所有采集。

## 适用场景

- 为代码仓文档化提供基础数据
- 新人快速了解陌生代码仓的全貌
- 架构评审前的信息采集
- CI/CD 迁移前的现状摸排

## 前置条件

- 推荐安装 `tokei`（代码行数统计）：`brew install tokei`；若不可用则用 `cloc` 或 `find` + `wc -l` 代替
- 从目标仓库根目录运行

## 工作流程

### 步骤 1：代码规模与语言分布

运行 `tokei`（首选）获取按语言分类的文件数、代码行数、注释行数。

若 tokei 不可用，降级方案：
- `cloc .` 
- 或按主要扩展名分别统计：`find . -name "*.py" | xargs wc -l` 等

输出要点：
- 识别 **primary_language**（代码行数最多的那门语言）
- 列出所有检测到的语言及其代码行数、文件数、占比
- 注意区分真正的源代码和 Markdown/JSON/YAML 等配置/文档文件

### 步骤 2：目录结构与模块划分

扫描仓库顶层目录，区分以下内容并归类：

| 目录类型 | 判定标准 | 示例 |
|---------|---------|------|
| **根模块** | 含独立构建文件（pom.xml, go.mod, pyproject.toml, package.json, Cargo.toml 等）或独立 src 目录 | `services/order/`, `frontend/` |
| **配置/部署** | 仅含 CI 配置、Dockerfile、K8s yaml 等 | `deploy/`, `.github/` |
| **文档** | 仅含 .md, .rst 等 | `docs/`, `wiki/` |
| **脚本/工具** | 辅助脚本，非主体代码 | `scripts/`, `tools/` |

对每个根模块，深入 2-3 层识别子模块结构：
- 寻找是否有 `src/main/java/com/...`（Java）、`internal/`、`pkg/`（Go）等标准布局
- 识别包/命名空间的第一级分组

**判定模块类型：**
- `service` — 有 main/入口类的独立可运行服务
- `library` — 被其他模块依赖的公共库（无独立入口）
- `extension` — 浏览器扩展、IDE 插件等
- `adapter` — 适配器/桥接层（如多平台适配）
- `config` — 纯配置文件集合
- `test` — 独立的测试模块

**识别叶子模块：** 不再包含独立子模块的最细粒度功能单元。一个根模块下可有多个叶子模块。

### 步骤 3：构建系统检测

扫描以下构建文件并推断构建命令：

| 构建文件 | 语言/生态 | 推断命令 |
|---------|----------|---------|
| `pom.xml` | Java/Maven | `mvn clean package` |
| `build.gradle*` | Java/Kotlin/Gradle | `gradle build` |
| `Makefile` | C/C++/通用 | `make` / `make all` |
| `package.json` | Node.js | `npm run build` / `yarn build` |
| `pyproject.toml` / `setup.py` | Python | `pip install -e .` |
| `go.mod` | Go | `go build ./...` |
| `Cargo.toml` | Rust | `cargo build` |

若存在多模块（monorepo），分别列出各模块的构建命令。

### 步骤 4：测试框架与命令

检测测试目录和配置文件：

- 测试目录：`src/test/java/`（Java）、`tests/`、`__tests__/`、`spec/`（Ruby）、`*_test.go`（Go）、`*.spec.ts` 等
- 测试配置：`pytest.ini`/`pyproject.toml[tool.pytest]`、`jest.config.*`、`.phpunit.xml`、`karma.conf.js` 等
- 从构建文件中提取测试依赖（如 pom.xml 中的 junit、pom.xml 中的 testng）

推断测试命令：
- Java/Maven：`mvn test`
- Python/pytest：`pytest --cov -n auto`
- Node.js：`npm test` / `jest`
- Go：`go test ./...`

### 步骤 5：代码风格与检查工具

检测以下配置文件的存在性：

| 配置类型 | 文件示例 |
|---------|---------|
| Lint | `.eslintrc*`, `.pylintrc`, `checkstyle.xml`, `.golangci.yml`, `.rubocop.yml`, `.clang-format` |
| Formatter | `.prettierrc*`, `.editorconfig`, `pyproject.toml` 中的 `[tool.black]` / `[tool.ruff]` |
| 类型检查 | `mypy.ini`, `tsconfig.json` (strict), `pyrightconfig.json` |
| 拼写检查 | `.cspell.json`, `.codespellrc` |

### 步骤 6：CI/CD 流水线

检测 CI 配置文件：
- `.github/workflows/` — 列出所有 workflow 文件，提取 job 名称
- `.gitlab-ci.yml` — 列出 stage 和 job
- `Jenkinsfile` — 检测 pipeline 结构
- `azure-pipelines.yml` — 列出 stage
- `.circleci/config.yml` — 列出 job
- `bitbucket-pipelines.yml` — 列出 step

对于检测到的 CI 配置，读取内容并提取关键阶段（如 build、test、lint、deploy）。

### 步骤 7：提交规范

运行 `git log --oneline -20` 分析提交信息格式。

判定标准：
- **Conventional Commits** — 大部分提交以 `feat:` / `fix:` / `chore:` / `docs:` / `refactor:` 等开头
- **自定义规范** — 有规律性的前缀模式但不符合 Conventional Commits（如 `[JIRA-123]`）
- **无规范** — 提交信息格式不一，无固定模式

提取 3-5 条典型提交作为示例。

### 步骤 8：展示诊断摘要并确认

将以上所有采集结果汇总为以下格式展示：

```
🔍 代码仓画像

语言分布：
  Java      12,541 行  219 文件  57.5%
  Python     1,264 行   13 文件   5.8%
  ...

根模块（N 个）：
  path/to/module1/     service     276 文件  ~12,500 行  <一句话描述>
  path/to/module2/     service      18 文件  ~1,300 行  <一句话描述>

叶子模块（M 个）：
  path/to/leaf1/       adapter       6 文件  ~500 行  <一句话描述>
  path/to/leaf2/       test          4 文件  ~200 行  <一句话描述>

构建：
  module1 → mvn clean package -f module1/pom.xml
  module2 → pip install -e module2/

测试：
  module2 → pytest --cov -n auto
  （module1 未检测到测试框架）

代码检查：<检测到的工具列表，或"未检测到">

CI/CD：
  <流水线摘要，或"未检测到 CI 配置">

提交规范：
  Conventional Commits（示例：feat: add xxx, fix: correct yyy）
```

然后向用户提问：
1. "各模块的类型判定和描述是否准确？是否有需要跳过或重新归类的模块？"
2. "主构建命令和测试命令是否正确？"
3. "是否有未检测到的 CI 流水线或代码检查工具？"

## 输出与持久化

用户确认（并完成修正）后：
1. **将最终确认的画像写入项目仓库**：创建 `.aidoc/phase0/` 目录，将画像数据写入 `.aidoc/phase0/repo-profile.md`
2. 文件格式为 Markdown，包含以下内容：
   - 语言分布（表格：语言、代码行数、文件数、占比）
   - 根模块列表（表格：路径、类型、文件数、代码行数、描述）
   - 叶子模块列表（表格：路径、类型、文件数、代码行数、描述）
   - 构建命令（每个模块的构建命令）
   - 测试命令（每个模块的测试命令）
   - 代码检查工具列表（或"未检测到"）
   - CI/CD 流水线摘要（或"未检测到 CI 配置"）
   - 提交规范判定及示例
3. 告知用户："画像已写入 `.aidoc/phase0/repo-profile.md`，下游 skill（如 aidoc-create）可直接读取使用。"
4. 在使用 `aidoc-create` 或类似下游 skill 时，先检查 `.aidoc/phase0/repo-profile.md` 是否存在，避免重复采集

## 注意事项

- 优先并行执行独立的探索步骤（如 tokei 可以和 ls 并发）
- 对不确定的判定（如模块类型），标注为 `[? 待确认]` 而非猜测后直接确认
- 如果仓库特别大（> 50 万行），先做顶层探索，在确认阶段让用户指定需要深入分析的范围
- 不要在仓库中生成任何中间文件（JSON、YAML 等），所有结果直接在对话中展示
