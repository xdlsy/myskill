---
name: aidoc-learning
description: "捕获学习经验、错误和纠正以实现持续改进。适用场景：(1) 命令或操作意外失败，(2) 用户纠正 Agent（'不对，应该是...'、'实际上...'），(3) 用户请求不存在的功能，(4) 外部 API 或工具失败，(5) Agent 发现自己的知识已过时或错误，(6) 为重复性任务发现了更好的方法。同时在开始重要任务前回顾学习记录。"
---

# 学习改进技能

将学习经验和错误记录到 markdown 文件中，实现持续改进。编码助手后续可将这些记录处理为修复，重要的学习经验会升级为项目记忆。

## 首次使用初始化

在记录任何内容之前，确保项目或工作区根目录中存在 `docs/learnings/` 目录和文件。如有缺失，请创建：

```bash
mkdir -p docs/learnings
[ -f docs/learnings/LEARNINGS.md ] || printf "# 学习记录\n\n开发过程中捕获的纠正、洞察和知识盲区。\n\n**分类**：correction | insight | knowledge_gap | best_practice\n\n---\n" > docs/learnings/LEARNINGS.md
[ -f docs/learnings/ERRORS.md ] || printf "# 错误日志\n\n命令失败和集成错误。\n\n---\n" > docs/learnings/ERRORS.md
[ -f docs/learnings/FEATURE_REQUESTS.md ] || printf "# 功能请求\n\n用户请求的功能。\n\n---\n" > docs/learnings/FEATURE_REQUESTS.md
```

切勿覆盖已有文件。如果 `docs/learnings/` 已经初始化，此操作不会产生任何效果。

除非用户明确要求提供详细信息，否则不要记录密钥、令牌、私钥、环境变量或完整的源/配置文件。优先使用简洁的摘要或脱敏摘录，而非原始命令输出或完整对话记录。

如需自动提醒或设置辅助，请使用 [Hook 集成](#hook-集成) 中描述的可选 hook 工作流。

## 快速参考

| 场景 | 操作 |
|-----------|--------|
| 命令/操作失败 | 记录到 `docs/learnings/ERRORS.md` |
| 用户纠正你 | 记录到 `docs/learnings/LEARNINGS.md`，分类为 `correction` |
| 用户想要缺失的功能 | 记录到 `docs/learnings/FEATURE_REQUESTS.md` |
| API/外部工具失败 | 记录到 `docs/learnings/ERRORS.md`，附带集成细节 |
| 知识已过时 | 记录到 `docs/learnings/LEARNINGS.md`，分类为 `knowledge_gap` |
| 发现更好的方法 | 记录到 `docs/learnings/LEARNINGS.md`，分类为 `best_practice` |
| 简化/强化重复出现的模式 | 记录/更新 `docs/learnings/LEARNINGS.md`，标注 `Source: simplify-and-harden` 和稳定的 `Pattern-Key` |
| 与已有条目类似 | 使用 `**See Also**` 链接，考虑提升优先级 |
| 广泛适用的学习经验 | 升级到 `CLAUDE.md`、`AGENTS.md` 和/或 `.github/copilot-instructions.md` |
| 工作流改进 | 升级到 `AGENTS.md` |
| 工具陷阱 | 升级到 `TOOLS.md` |
| 行为模式 | 升级到 `SOUL.md` |

## 项目设置

对于 Claude Code、Codex、Copilot 或其他助手，在项目或工作区根目录中创建 `docs/learnings/`：

```bash
mkdir -p docs/learnings
```

使用上述标头内联创建文件。除非你明确信任该路径，否则应避免从当前仓库或工作区读取模板。

### 在助手文件 AGENTS.md、CLAUDE.md 或 .github/copilot-instructions.md 中添加引用，提醒自己记录学习经验（

#### 自我改进工作流

当发生错误或纠正时：
1. 记录到 `docs/learnings/ERRORS.md`、`LEARNINGS.md` 或 `FEATURE_REQUESTS.md`
2. 回顾并将广泛适用的学习经验升级到：
   - `CLAUDE.md` - 项目事实和约定
   - `AGENTS.md` - 工作流和自动化
   - `.github/copilot-instructions.md` - Copilot 上下文

## 日志格式

### 学习条目

追加到 `docs/learnings/LEARNINGS.md`：

```markdown
## [LRN-YYYYMMDD-XXX] 分类

**Logged**：ISO-8601 时间戳
**Priority**：low | medium | high | critical
**Status**：pending
**Area**：frontend | backend | infra | tests | docs | config

### Summary
所学内容的单行描述

### Details
完整上下文：发生了什么、哪里错了、正确的是什么

### Suggested Action
需要做出的具体修复或改进

### Metadata
- Source：conversation | error | user_feedback
- Related Files：path/to/file.ext
- Tags：tag1, tag2
- See Also：LRN-20250110-001（如果与已有条目相关）
- Pattern-Key：simplify.dead_code | harden.input_validation（可选，用于追踪重复模式）
- Recurrence-Count：1（可选）
- First-Seen：2025-01-15（可选）
- Last-Seen：2025-01-15（可选）

---
```

### 错误条目

追加到 `docs/learnings/ERRORS.md`：

```markdown
## [ERR-YYYYMMDD-XXX] 技能或命令名称

**Logged**：ISO-8601 时间戳
**Priority**：high
**Status**：pending
**Area**：frontend | backend | infra | tests | docs | config

### Summary
失败内容的简要描述

### Error
```
实际的错误消息或输出
```

### Context
- 尝试的命令/操作
- 使用的输入或参数
- 相关的环境细节
- 相关输出的摘要或脱敏摘录（默认避免完整记录和包含敏感数据的内容）

### Suggested Fix
如果可识别，可能解决问题的方案

### Metadata
- Reproducible：yes | no | unknown
- Related Files：path/to/file.ext
- See Also：ERR-20250110-001（如果反复出现）

---
```

### 功能请求条目

追加到 `docs/learnings/FEATURE_REQUESTS.md`：

```markdown
## [FEAT-YYYYMMDD-XXX] 功能名称

**Logged**：ISO-8601 时间戳
**Priority**：medium
**Status**：pending
**Area**：frontend | backend | infra | tests | docs | config

### Requested Capability
用户想要做什么

### User Context
为什么需要、正在解决什么问题

### Complexity Estimate
simple | medium | complex

### Suggested Implementation
如何实现、可能扩展什么

### Metadata
- Frequency：first_time | recurring
- Related Features：existing_feature_name

---
```

## ID 生成

格式：`TYPE-YYYYMMDD-XXX`
- TYPE：`LRN`（学习）、`ERR`（错误）、`FEAT`（功能）
- YYYYMMDD：当前日期
- XXX：顺序编号或随机3字符（例如 `001`、`A7B`）

示例：`LRN-20250115-001`、`ERR-20250115-A3F`、`FEAT-20250115-002`

## 解决条目

当问题被修复后，更新条目：

1. 将 `**Status**：pending` 改为 `**Status**：resolved`
2. 在 Metadata 之后添加解决块：

```markdown
### Resolution
- **Resolved**：2025-01-16T09:00:00Z
- **Commit/PR**：abc123 或 #42
- **Notes**：所做操作的简要描述
```

其他状态值：
- `in_progress` - 正在积极处理中
- `wont_fix` - 决定不处理（在 Resolution 备注中添加原因）
- `promoted` - 已升级到 CLAUDE.md、AGENTS.md 或 .github/copilot-instructions.md

## 升级到项目记忆

当学习经验广泛适用（而非一次性修复）时，将其升级为永久项目记忆。

### 何时升级

- 学习经验适用于多个文件/功能
- 任何贡献者（人类或 AI）都应知道的知识
- 防止重复性错误
- 记录项目特定的约定

### 升级目标

| 目标 | 应包含的内容 |
|--------|-------------------|
| `CLAUDE.md` | 项目事实、约定、适用于所有 Claude 交互的陷阱 |
| `AGENTS.md` | 助手特定的工作流、工具使用模式、自动化规则 |
| `.github/copilot-instructions.md` | GitHub Copilot 的项目上下文和约定 |
| `SOUL.md` | 行为准则、沟通风格、原则 |
| `TOOLS.md` | 工具功能、使用模式、集成陷阱 |

### 如何升级

1. **提炼**学习经验为简洁的规则或事实
2. **添加**到目标文件的适当部分（如需要则创建文件）
3. **更新**原始条目：
   - 将 `**Status**：pending` 改为 `**Status**：promoted`
   - 添加 `**Promoted**：CLAUDE.md`、`AGENTS.md` 或 `.github/copilot-instructions.md`

### 升级示例

**学习经验**（详细版本）：
> 项目使用 pnpm workspaces。尝试 `npm install` 但失败了。
> 锁定文件是 `pnpm-lock.yaml`。必须使用 `pnpm install`。

**在 CLAUDE.md 中**（简洁版本）：
```markdown
## 构建与依赖
- 包管理器：pnpm（非 npm） - 使用 `pnpm install`
```

**学习经验**（详细版本）：
> 修改 API 端点后，必须重新生成 TypeScript 客户端。
> 忘记这一步会导致运行时类型不匹配。

**在 AGENTS.md 中**（可操作版本）：
```markdown
## API 变更后
1. 重新生成客户端：`pnpm run generate:api`
2. 检查类型错误：`pnpm tsc --noEmit`
```

## 重复模式检测

如果记录的内容与已有条目类似：

1. **先搜索**：`grep -r "关键词" docs/learnings/`
2. **链接条目**：在 Metadata 中添加 `**See Also**：ERR-20250110-001`
3. **提升优先级**：如果问题持续出现
4. **考虑系统性修复**：重复性问题通常表明：
   - 缺少文档（→ 升级到 CLAUDE.md 或 .github/copilot-instructions.md）
   - 缺少自动化（→ 添加到 AGENTS.md）
   - 架构问题（→ 创建技术债务工单）

## 定期回顾

在自然的断点处回顾 `docs/learnings/`：

### 何时回顾
- 开始新的重要任务之前
- 完成一个功能之后
- 在有过往学习记录的区域工作时
- 活跃开发期间每周一次

### 快速状态检查
```bash
# 统计待处理条目
grep -h "Status\*\*：pending" docs/learnings/*.md | wc -l

# 列出待处理的高优先级条目
grep -B5 "Priority\*\*：high" docs/learnings/*.md | grep "^## \["

# 查找特定区域的学习记录
grep -l "Area\*\*：backend" docs/learnings/*.md
```

### 回顾操作
- 解决已修复的条目
- 升级适用的学习经验
- 链接相关条目
- 升级重复性问题

## 检测触发器

在注意到以下情况时自动记录：

**纠正**（→ 分类为 `correction` 的学习记录）：
- "不对，应该是..."
- "实际上，应该是..."
- "你搞错了..."
- "这已经过时了..."

**功能请求**（→ 功能请求）：
- "你能不能也..."
- "我希望你能..."
- "有没有办法..."
- "为什么你不能..."

**知识盲区**（→ 分类为 `knowledge_gap` 的学习记录）：
- 用户提供了你不知道的信息
- 你引用的文档已过时
- API 行为与你的理解不同

**错误**（→ 错误条目）：
- 命令返回非零退出码
- 异常或堆栈跟踪
- 意外的输出或行为
- 超时或连接失败

## 优先级指南

| 优先级 | 何时使用 |
|----------|-------------|
| `critical` | 阻塞核心功能、数据丢失风险、安全问题 |
| `high` | 重大影响、影响常见工作流、重复性问题 |
| `medium` | 中等影响、存在变通方案 |
| `low` | 轻微不便、边缘情况、锦上添花 |

## 区域标签

用于按代码库区域筛选学习记录：

| 区域 | 范围 |
|------|-------|
| `frontend` | UI、组件、客户端代码 |
| `backend` | API、服务、服务端代码 |
| `infra` | CI/CD、部署、Docker、云 |
| `tests` | 测试文件、测试工具、覆盖率 |
| `docs` | 文档、注释、README |
| `config` | 配置文件、环境、设置 |

## 最佳实践

1. **立即记录** - 问题刚发生后上下文最清晰
2. **具体明确** - 未来的助手需要快速理解
3. **包含复现步骤** - 尤其是错误
4. **链接相关文件** - 使修复更容易
5. **建议具体修复方案** - 而不只是"调查一下"
6. **使用一致的分类** - 便于筛选
7. **积极升级** - 如有疑问，添加到 CLAUDE.md 或 .github/copilot-instructions.md
8. **定期回顾** - 陈旧的学习记录会失去价值

## Gitignore 选项

**保持学习记录本地化**（每个开发者独立）：
```gitignore
docs/learnings/
```

本仓库使用此默认设置，以避免意外提交敏感或嘈杂的本地日志。

**在仓库中追踪学习记录**（团队共享）：
不要添加到 .gitignore - 学习记录将成为共享知识。

**混合模式**（追踪模板，忽略条目）：
```gitignore
docs/learnings/*.md
!docs/learnings/.gitkeep
```

## Hook 集成

通过助手 hook 启用自动提醒。这是**可选的** - 你必须显式配置 hook。

### 快速设置（Claude Code / Codex）

在项目中创建 `.claude/settings.json`：

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "./skills/aidoc-learning/scripts/activator.sh"
      }]
    }]
  }
}
```

这将在每次提示后注入学习评估提醒（约 50-100 tokens 开销）。

### 高级设置（含错误检测）

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "./skills/aidoc-learning/scripts/activator.sh"
      }]
    }],
    "PostToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "./skills/aidoc-learning/scripts/error-detector.sh"
      }]
    }]
  }
}
```

这是可选的。推荐默认仅使用 activator 设置；只有在你接受 hook 脚本检查命令输出中的错误模式时，才启用 `PostToolUse`。

### 可用的 Hook 脚本

| 脚本 | Hook 类型 | 用途 |
|--------|-----------|---------|
| `scripts/activator.sh` | UserPromptSubmit | 提醒在任务后评估学习记录 |
| `scripts/error-detector.sh` | PostToolUse (Bash) | 在命令错误时触发 |

详细的配置和故障排除请参见 `references/hooks-setup.md`。

## 自动技能提取

当学习经验有价值成为可复用的技能时，使用提供的辅助工具提取它。

### 技能提取标准

学习经验符合技能提取的条件是满足以下任一条件：

| 标准 | 描述 |
|-----------|-------------|
| **重复出现** | 有 `See Also` 链接指向 2 个以上类似问题 |
| **已验证** | 状态为 `resolved`，修复方案有效 |
| **非显而易见** | 需要实际调试/调查才能发现 |
| **广泛适用** | 非项目特定；跨代码库有用 |
| **用户标记** | 用户说"保存为技能"或类似表达 |

### 提取工作流

1. **识别候选项**：学习经验符合提取标准
2. **运行辅助工具**（或手动创建）：
   ```bash
   ./skills/aidoc-learning/scripts/extract-skill.sh skill-name --dry-run
   ./skills/aidoc-learning/scripts/extract-skill.sh skill-name
   ```
3. **自定义 SKILL.md**：用学习内容填充模板
4. **更新学习记录**：将状态设置为 `promoted_to_skill`，添加 `Skill-Path`
5. **验证**：在新的会话中阅读技能，确保其自包含

### 手动提取

如果你偏好手动创建：

1. 创建 `skills/<skill-name>/SKILL.md`
2. 使用 `assets/SKILL-TEMPLATE.md` 中的模板
3. 遵循 [Agent Skills 规范](https://agentskills.io/specification)：
   - YAML 前置元数据包含 `name` 和 `description`
   - 名称必须与文件夹名称匹配
   - 技能文件夹内不得有 README.md

### 提取检测触发器

注意以下表明学习经验应成为技能的信号：

**对话中：**
- "保存为技能"
- "我总是遇到这个"
- "这对其他项目也有用"
- "记住这个模式"

**学习条目中：**
- 多个 `See Also` 链接（重复问题）
- 高优先级 + 已解决状态
- 分类为 `best_practice` 且广泛适用
- 用户反馈称赞解决方案

### 技能质量门禁

提取前验证：

- [ ] 解决方案已测试并有效
- [ ] 描述在没有原始上下文的情况下也清晰明了
- [ ] 代码示例是自包含的
- [ ] 没有项目特定的硬编码值
- [ ] 遵循技能命名约定（小写、连字符）

## 多助手支持

本技能适用于不同 AI 编码助手，具有助手特定的激活方式。

### Claude Code

**激活**：Hook（UserPromptSubmit、PostToolUse）
**设置**：`.claude/settings.json` 配置 hook
**检测**：通过 hook 脚本自动检测

### Codex CLI

**激活**：Hook（与 Claude Code 相同模式）
**设置**：`.codex/settings.json` 配置 hook
**检测**：通过 hook 脚本自动检测

### GitHub Copilot

**激活**：手动（不支持 hook）
**设置**：添加到 `.github/copilot-instructions.md`：

```markdown
## 自我改进

解决非显而易见的问题后，考虑记录到 `docs/learnings/`：
1. 使用自改进技能中的格式
2. 使用 See Also 链接相关条目
3. 将高价值学习经验升级为技能

在聊天中询问："我应该把这个记录为学习经验吗？"
```

**检测**：会话结束时手动回顾
