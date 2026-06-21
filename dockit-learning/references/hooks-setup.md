# Hook 设置指南

为 AI 编码助手配置自动自我改进触发器。

## 概述

Hook 通过在关键时刻注入提醒来实现主动的学习捕获：
- **UserPromptSubmit**：每次提示后提醒评估学习记录
- **PostToolUse (Bash)**：命令失败时的错误检测

## Claude Code 设置

### 选项 1：项目级配置

在项目根目录中创建 `.claude/settings.json`：

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "./skills/dockit-learning/scripts/activator.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "./skills/dockit-learning/scripts/error-detector.sh"
          }
        ]
      }
    ]
  }
}
```

### 选项 2：用户级配置

添加到 `~/.claude/settings.json` 实现全局激活：

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/skills/dockit-learning/scripts/activator.sh"
          }
        ]
      }
    ]
  }
}
```

### 最小设置（仅 Activator）

为了更低的开销，仅使用 UserPromptSubmit hook：

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "./skills/dockit-learning/scripts/activator.sh"
          }
        ]
      }
    ]
  }
}
```

## Codex CLI 设置

Codex 使用与 Claude Code 相同的 hook 系统。创建 `.codex/settings.json`：

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "./skills/dockit-learning/scripts/activator.sh"
          }
        ]
      }
    ]
  }
}
```

## GitHub Copilot 设置

Copilot 不直接支持 hook。改为在 `.github/copilot-instructions.md` 中添加指导：

```markdown
## 自我改进

完成以下任务后：
- 调试非显而易见的问题
- 发现变通方案
- 学习项目特定的模式
- 解决意外错误

考虑将学习经验记录到 `docs/learnings/`，使用自我改进技能的格式。

对于有助于其他会话的高价值学习经验，考虑技能提取。
```

## 验证

### 测试 Activator Hook

1. 启用 hook 配置
2. 启动新的 Claude Code 会话
3. 发送任意提示
4. 验证在上下文中是否看到 `<self-improvement-reminder>`

### 测试错误检测器 Hook

1. 为 Bash 启用 PostToolUse hook
2. 运行一个会失败的命令：`ls /nonexistent/path`
3. 验证是否看到 `<error-detected>` 提醒

### 干运行提取脚本

```bash
./skills/dockit-learning/scripts/extract-skill.sh test-skill --dry-run
```

预期输出显示将要创建的技能骨架。

## 故障排除

### Hook 未触发

1. **检查脚本权限**：`chmod +x scripts/*.sh`
2. **验证路径**：使用绝对路径或相对于项目根目录的路径
3. **检查设置位置**：项目级 vs 用户级设置
4. **重启会话**：Hook 在会话启动时加载

### 权限被拒绝

```bash
chmod +x ./skills/dockit-learning/scripts/activator.sh
chmod +x ./skills/dockit-learning/scripts/error-detector.sh
chmod +x ./skills/dockit-learning/scripts/extract-skill.sh
```

### 脚本未找到

如果使用相对路径，确保你在正确的目录中，或使用绝对路径：

```json
{
  "command": "/absolute/path/to/skills/dockit-learning/scripts/activator.sh"
}
```

### 开销过大

如果 activator 感觉过于干扰：

1. **使用最小设置**：仅使用 UserPromptSubmit，跳过 PostToolUse
2. **添加 matcher 过滤器**：仅对特定提示触发：

```json
{
  "matcher": "fix|debug|error|issue",
  "hooks": [...]
}
```

## Hook 输出预算

activator 设计为轻量级：
- **目标**：每次激活约 50-100 tokens
- **内容**：结构化提醒，而非冗长的指令
- **格式**：XML 标签，便于解析

如果需要进一步减少开销，可以编辑 `activator.sh` 输出更少的文本。

## 安全注意事项

- Hook 脚本以与 Claude Code 相同的权限运行
- 脚本仅输出文本；不修改文件或运行命令
- 错误检测器读取 `CLAUDE_TOOL_OUTPUT` 环境变量
- 将 `CLAUDE_TOOL_OUTPUT` 视为潜在敏感信息；除非用户明确要求，否则不要原样记录或转发
- 所有脚本都是可选的（你必须显式配置它们）
- 推荐默认：仅启用 `UserPromptSubmit`，只有当你希望从命令输出中获得错误模式提醒时才添加 `PostToolUse`

## 禁用 Hook

要在不删除配置的情况下临时禁用：

1. **在设置中注释掉**：
```json
{
  "hooks": {
    // "UserPromptSubmit": [...]
  }
}
```

2. **或删除设置文件**：没有配置，Hook 就不会运行
