#!/usr/bin/env bash
# =============================================================================
# collect-dependencies.sh — 模块依赖关系采集（shell wrapper）
# =============================================================================
# 两遍扫描：
#   Pass 1（静态）: 纯文件解析 → 内部依赖 + 外部依赖名称
#   Pass 2（动态）: 运行构建工具 → 版本号 + 传递依赖
# 降级：按模块降级，动态增强失败时保留静态结果
#
# 用法：
#   ./collect-dependencies.sh --format json --dir <repo_root>
#   ./collect-dependencies.sh --format text --dir <repo_root> --no-dynamic
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYSCRIPT="$SCRIPT_DIR/collect-dependencies.py"
OUTPUT_FORMAT="json"
TARGET_DIR="."
NO_DYNAMIC=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --format)
            OUTPUT_FORMAT="$2"; shift 2 ;;
        --dir)
            TARGET_DIR="$2"; shift 2 ;;
        --no-dynamic)
            NO_DYNAMIC="--no-dynamic"; shift ;;
        --help|-h)
            echo "用法: $0 [--format json|text] [--dir <target>] [--no-dynamic]"
            echo ""
            echo "选项:"
            echo "  --format json|text   输出格式（默认 json）"
            echo "  --dir <target>       目标仓库根目录（默认当前目录）"
            echo "  --no-dynamic         仅静态解析，不运行构建工具"
            echo "  --help, -h           显示帮助"
            echo ""
            echo "支持构建系统: CMake, Maven, Gradle, Go Modules, Python (pyproject.toml)"
            exit 0
            ;;
        *)
            echo "未知参数: $1" >&2; exit 1 ;;
    esac
done

if [[ ! -f "$PYSCRIPT" ]]; then
    echo "错误: 找不到 $PYSCRIPT" >&2
    exit 1
fi

python3 "$PYSCRIPT" --format "$OUTPUT_FORMAT" --dir "$TARGET_DIR" ${NO_DYNAMIC:-}
