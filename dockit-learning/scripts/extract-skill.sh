#!/bin/bash
# 技能提取辅助工具
# 从学习条目创建新技能
# 用法：./extract-skill.sh <skill-name> [--dry-run]

set -e

# 配置
SKILLS_DIR="./skills"

# 输出颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # 无颜色

usage() {
    cat << EOF
用法：$(basename "$0") <技能名称> [选项]

从学习条目创建新技能。

参数：
  技能名称     技能名称（小写，连字符分隔）

选项：
  --dry-run      显示将要创建的内容，不实际创建文件
  --output-dir   当前路径下的相对输出目录（默认：./skills）
  -h, --help     显示此帮助信息

示例：
  $(basename "$0") docker-m1-fixes
  $(basename "$0") api-timeout-patterns --dry-run
  $(basename "$0") pnpm-setup --output-dir ./skills/custom

技能将创建在：\$SKILLS_DIR/<技能名称>/
EOF
}

log_info() {
    echo -e "${GREEN}[信息]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[警告]${NC} $1"
}

log_error() {
    echo -e "${RED}[错误]${NC} $1" >&2
}

# 解析参数
SKILL_NAME=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --output-dir)
            if [ -z "${2:-}" ] || [[ "${2:-}" == -* ]]; then
                log_error "--output-dir 需要相对路径参数"
                usage
                exit 1
            fi
            SKILLS_DIR="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -*)
            log_error "未知选项：$1"
            usage
            exit 1
            ;;
        *)
            if [ -z "$SKILL_NAME" ]; then
                SKILL_NAME="$1"
            else
                log_error "意外参数：$1"
                usage
                exit 1
            fi
            shift
            ;;
    esac
done

# 验证技能名称
if [ -z "$SKILL_NAME" ]; then
    log_error "技能名称是必需的"
    usage
    exit 1
fi

# 验证技能名称格式（小写、连字符、无空格）
if ! [[ "$SKILL_NAME" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
    log_error "无效的技能名称格式。仅使用小写字母、数字和连字符。"
    log_error "示例：'docker-fixes'、'api-patterns'、'pnpm-setup'"
    exit 1
fi

# 验证输出路径，防止写入当前工作区之外。
if [[ "$SKILLS_DIR" = /* ]]; then
    log_error "输出目录必须是当前目录下的相对路径。"
    exit 1
fi

if [[ "$SKILLS_DIR" =~ (^|/)\.\.(/|$) ]]; then
    log_error "输出目录不能包含 '..' 路径段。"
    exit 1
fi

SKILLS_DIR="${SKILLS_DIR#./}"
SKILLS_DIR="./$SKILLS_DIR"

SKILL_PATH="$SKILLS_DIR/$SKILL_NAME"

# 检查技能是否已存在
if [ -d "$SKILL_PATH" ] && [ "$DRY_RUN" = false ]; then
    log_error "技能已存在：$SKILL_PATH"
    log_error "请使用不同的名称或先删除现有技能。"
    exit 1
fi

# 干运行输出
if [ "$DRY_RUN" = true ]; then
    log_info "干运行 - 将创建："
    echo "  $SKILL_PATH/"
    echo "  $SKILL_PATH/SKILL.md"
    echo ""
    echo "模板内容将是："
    echo "---"
    cat << TEMPLATE
name: $SKILL_NAME
description: "[待办：添加此技能功能和适用场景的简洁描述]"
---

# $(echo "$SKILL_NAME" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2))}1')

[待办：简要介绍技能用途]

## 快速参考

| 场景 | 操作 |
|-----------|--------|
| [触发条件] | [操作内容] |

## 使用说明

[待办：详细使用说明]

## 示例

[待办：添加具体示例]

## 来源学习

此技能从学习条目提取。
- 学习 ID：[待办：添加原始学习 ID]
- 原始文件：docs/learnings/LEARNINGS.md
TEMPLATE
    echo "---"
    exit 0
fi

# 创建技能目录结构
log_info "正在创建技能：$SKILL_NAME"

mkdir -p "$SKILL_PATH"

# 从模板创建 SKILL.md
cat > "$SKILL_PATH/SKILL.md" << TEMPLATE
---
name: $SKILL_NAME
description: "[待办：添加此技能功能和适用场景的简洁描述]"
---

# $(echo "$SKILL_NAME" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2))}1')

[待办：简要介绍技能用途]

## 快速参考

| 场景 | 操作 |
|-----------|--------|
| [触发条件] | [操作内容] |

## 使用说明

[待办：详细使用说明]

## 示例

[待办：添加具体示例]

## 来源学习

此技能从学习条目提取。
- 学习 ID：[待办：添加原始学习 ID]
- 原始文件：docs/learnings/LEARNINGS.md
TEMPLATE

log_info "已创建：$SKILL_PATH/SKILL.md"

# 建议后续步骤
echo ""
log_info "技能骨架创建成功！"
echo ""
echo "后续步骤："
echo "  1. 编辑 $SKILL_PATH/SKILL.md"
echo "  2. 将待办部分替换为学习内容"
echo "  3. 如有详细文档，添加 references/ 文件夹"
echo "  4. 如有可执行代码，添加 scripts/ 文件夹"
echo "  5. 更新原始学习条目："
echo "     **Status**：promoted_to_skill"
echo "     **Skill-Path**：skills/$SKILL_NAME"
