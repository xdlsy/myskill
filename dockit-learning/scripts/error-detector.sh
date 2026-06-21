#!/bin/bash
# 学习改进错误检测器 Hook
# 在 PostToolUse 时触发（Bash），检测命令失败
# 读取 CLAUDE_TOOL_OUTPUT 环境变量

set -e

# 检查工具输出是否表明错误
# CLAUDE_TOOL_OUTPUT 包含工具执行的结果
OUTPUT="${CLAUDE_TOOL_OUTPUT:-}"

# 表明错误的模式（大小写不敏感匹配）
ERROR_PATTERNS=(
    "error:"
    "Error:"
    "ERROR:"
    "failed"
    "FAILED"
    "command not found"
    "No such file"
    "Permission denied"
    "fatal:"
    "Exception"
    "Traceback"
    "npm ERR!"
    "ModuleNotFoundError"
    "SyntaxError"
    "TypeError"
    "exit code"
    "non-zero"
)

# 检查输出是否包含任何错误模式
contains_error=false
for pattern in "${ERROR_PATTERNS[@]}"; do
    if [[ "$OUTPUT" == *"$pattern"* ]]; then
        contains_error=true
        break
    fi
done

# 仅当检测到错误时输出提醒
if [ "$contains_error" = true ]; then
    cat << 'EOF'
<error-detected>
检测到命令错误。如果满足以下条件，考虑将其记录到 docs/learnings/ERRORS.md：
- 错误是意外或非显而易见的
- 需要通过调查来解决
- 在类似的上下文中可能会再次出现
- 解决方案可能有助于将来的会话

使用学习改进技能格式：[ERR-YYYYMMDD-XXX]
</error-detected>
EOF
fi
