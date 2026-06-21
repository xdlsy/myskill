# 条目示例

格式良好、包含所有字段的具体示例。

## 学习记录：纠正

```markdown
## [LRN-20250115-001] correction

**Logged**：2025-01-15T10:30:00Z
**Priority**：high
**Status**：pending
**Area**：tests

### Summary
错误地认为默认情况下 pytest fixture 的作用域是函数级别

### Details
在编写测试 fixture 时，我假设所有 fixture 都是函数作用域。
用户纠正说虽然函数作用域是默认的，但代码库的约定是
为数据库连接使用模块作用域的 fixture，以提高测试性能。

### Suggested Action
在创建涉及昂贵设置（数据库、网络）的 fixture 时，
在默认使用函数作用域之前，先检查现有 fixture 的作用域模式。

### Metadata
- Source：user_feedback
- Related Files：tests/conftest.py
- Tags：pytest, testing, fixtures

---
```

## 学习记录：知识盲区（已解决）

```markdown
## [LRN-20250115-002] knowledge_gap

**Logged**：2025-01-15T14:22:00Z
**Priority**：medium
**Status**：resolved
**Area**：config

### Summary
项目使用 pnpm 而非 npm 进行包管理

### Details
尝试运行 `npm install`，但项目使用 pnpm workspaces。
锁定文件是 `pnpm-lock.yaml`，而非 `package-lock.json`。

### Suggested Action
在假定使用 npm 之前，先检查是否有 `pnpm-lock.yaml` 或 `pnpm-workspace.yaml`。
对此项目使用 `pnpm install`。

### Metadata
- Source：error
- Related Files：pnpm-lock.yaml, pnpm-workspace.yaml
- Tags：package-manager, pnpm, setup

### Resolution
- **Resolved**：2025-01-15T14:30:00Z
- **Commit/PR**：N/A - 知识更新
- **Notes**：已添加到 CLAUDE.md 供将来参考

---
```

## 学习记录：升级到 CLAUDE.md

```markdown
## [LRN-20250115-003] best_practice

**Logged**：2025-01-15T16:00:00Z
**Priority**：high
**Status**：promoted
**Promoted**：CLAUDE.md
**Area**：backend

### Summary
API 响应必须包含请求头中的关联 ID

### Details
所有 API 响应应回传请求中的 X-Correlation-ID 头。
这是分布式追踪所必需的。没有此头的响应会
破坏可观测性管道。

### Suggested Action
始终在 API 处理程序中包含关联 ID 直通传递。

### Metadata
- Source：user_feedback
- Related Files：src/middleware/correlation.ts
- Tags：api, observability, tracing

---
```

## 学习记录：升级到 AGENTS.md

```markdown
## [LRN-20250116-001] best_practice

**Logged**：2025-01-16T09:00:00Z
**Priority**：high
**Status**：promoted
**Promoted**：AGENTS.md
**Area**：backend

### Summary
OpenAPI 规范更改后必须重新生成 API 客户端

### Details
修改 API 端点后，必须重新生成 TypeScript 客户端。
忘记这一步会导致类型不匹配，仅在运行时才会显现。
生成脚本还会运行验证。

### Suggested Action
添加到助手工作流：任何 API 更改后，运行 `pnpm run generate:api`。

### Metadata
- Source：error
- Related Files：openapi.yaml, src/client/api.ts
- Tags：api, codegen, typescript

---
```

## 错误条目

```markdown
## [ERR-20250115-A3F] docker_build

**Logged**：2025-01-15T09:15:00Z
**Priority**：high
**Status**：pending
**Area**：infra

### Summary
由于平台不匹配，Docker 构建在 M1 Mac 上失败

### Error
```
error: failed to solve: python:3.11-slim: no match for platform linux/arm64
```

### Context
- 命令：`docker build -t myapp .`
- Dockerfile 使用 `FROM python:3.11-slim`
- 在 Apple Silicon（M1/M2）上运行

### Suggested Fix
添加平台标志：`docker build --platform linux/amd64 -t myapp .`
或更新 Dockerfile：`FROM --platform=linux/amd64 python:3.11-slim`

### Metadata
- Reproducible：yes
- Related Files：Dockerfile

---
```

## 错误条目：重复性问题

```markdown
## [ERR-20250120-B2C] api_timeout

**Logged**：2025-01-20T11:30:00Z
**Priority**：critical
**Status**：pending
**Area**：backend

### Summary
请求处理期间第三方 API 超时

### Error
```
TimeoutError: Request to api.example.com timed out after 30000ms
```

### Context
- 命令：POST /api/process
- 超时设置为 30 秒
- 在高峰时段（午餐时间、晚间）发生

### Suggested Fix
实现指数退避重试。考虑使用熔断器模式。

### Metadata
- Reproducible：yes（高峰时段）
- Related Files：src/services/api-client.ts
- See Also：ERR-20250115-X1Y, ERR-20250118-Z3W

---
```

## 功能请求

```markdown
## [FEAT-20250115-001] export_to_csv

**Logged**：2025-01-15T16:45:00Z
**Priority**：medium
**Status**：pending
**Area**：backend

### Requested Capability
将分析结果导出为 CSV 格式

### User Context
用户每周运行报告，需要与非技术利益相关者
在 Excel 中分享结果。目前手动复制输出。

### Complexity Estimate
simple

### Suggested Implementation
为 analyze 命令添加 `--output csv` 标志。使用标准 csv 模块。
可扩展现有的 `--output json` 模式。

### Metadata
- Frequency：recurring
- Related Features：analyze command, json output

---
```

## 功能请求：已解决

```markdown
## [FEAT-20250110-002] dark_mode

**Logged**：2025-01-10T14:00:00Z
**Priority**：low
**Status**：resolved
**Area**：frontend

### Requested Capability
仪表板的暗色模式支持

### User Context
用户工作到深夜，发现明亮的界面很疲劳。
其他几位用户也非正式地提到过这一点。

### Complexity Estimate
medium

### Suggested Implementation
为颜色使用 CSS 变量。在用户设置中添加切换开关。
考虑系统偏好检测。

### Metadata
- Frequency：recurring
- Related Features：user settings, theme system

### Resolution
- **Resolved**：2025-01-18T16:00:00Z
- **Commit/PR**：#142
- **Notes**：实现了系统偏好检测和手动切换

---
```

## 学习记录：升级为技能

```markdown
## [LRN-20250118-001] best_practice

**Logged**：2025-01-18T11:00:00Z
**Priority**：high
**Status**：promoted_to_skill
**Skill-Path**：skills/docker-m1-fixes
**Area**：infra

### Summary
由于平台不匹配，Docker 构建在 Apple Silicon 上失败

### Details
在 M1/M2 Mac 上构建 Docker 镜像时，因为基础镜像
没有 ARM64 变体而导致构建失败。这是一个影响
许多开发者的常见问题。

### Suggested Action
为 docker build 命令添加 `--platform linux/amd64`，或在 Dockerfile 中
使用 `FROM --platform=linux/amd64`。

### Metadata
- Source：error
- Related Files：Dockerfile
- Tags：docker, arm64, m1, apple-silicon
- See Also：ERR-20250115-A3F, ERR-20250117-B2D

---
```

## 提取的技能示例

当上述学习记录被提取为技能时，变为：

**文件**：`skills/docker-m1-fixes/SKILL.md`

```markdown
---
name: docker-m1-fixes
description: "修复 Apple Silicon（M1/M2）上的 Docker 构建失败。当 docker build 失败并出现平台不匹配错误时使用。"
---

# Docker M1 修复

解决 Apple Silicon Mac 上 Docker 构建问题的解决方案。

## 快速参考

| 错误 | 修复 |
|-------|-----|
| `no match for platform linux/arm64` | 在构建时添加 `--platform linux/amd64` |
| 镜像运行但崩溃 | 使用模拟或查找 ARM 兼容的基础镜像 |

## 问题

许多 Docker 基础镜像没有 ARM64 变体。在 Apple Silicon
（M1/M2/M3）上构建时，Docker 默认尝试拉取 ARM64 镜像，
导致平台不匹配错误。

## 解决方案

### 选项 1：构建标志（推荐）

为构建命令添加平台标志：

\`\`\`bash
docker build --platform linux/amd64 -t myapp .
\`\`\`

### 选项 2：Dockerfile 修改

在 FROM 指令中指定平台：

\`\`\`dockerfile
FROM --platform=linux/amd64 python:3.11-slim
\`\`\`

### 选项 3：Docker Compose

为服务添加平台：

\`\`\`yaml
services:
  app:
    platform: linux/amd64
    build: .
\`\`\`

## 权衡

| 方法 | 优点 | 缺点 |
|----------|------|------|
| 构建标志 | 无需文件更改 | 必须记住使用标志 |
| Dockerfile | 显式、版本化 | 影响所有构建 |
| Compose | 开发方便 | 需要 compose |

## 性能说明

在 ARM64 上运行 AMD64 镜像使用 Rosetta 2 模拟。这在开发中
可以工作但可能较慢。对于生产环境，尽可能寻找
ARM 原生替代方案。

## 来源

- 学习 ID：LRN-20250118-001
- 分类：best_practice
- 提取日期：2025-01-18
```
