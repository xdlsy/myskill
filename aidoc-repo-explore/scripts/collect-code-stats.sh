#!/usr/bin/env bash
# =============================================================================
# collect-code-stats.sh — 代码规模与语言分布采集脚本（shell wrapper）
# =============================================================================
# 自动降级尝试 tokei → cloc → python3 (find+wc)
# 用法：./collect-code-stats.sh [--format json|text] [--dir <target>] [--exclude <pattern>...]
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYSCRIPT="$SCRIPT_DIR/collect-code-stats.py"
OUTPUT_FORMAT="json"
TARGET_DIR="."
declare -a EXTRA_EXCLUDES=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --format)
            OUTPUT_FORMAT="$2"; shift 2 ;;
        --dir)
            TARGET_DIR="$2"; shift 2 ;;
        --exclude)
            EXTRA_EXCLUDES+=("$2"); shift 2 ;;
        --help|-h)
            echo "用法: $0 [--format json|text] [--dir <target>] [--exclude <pattern>...]"
            echo ""
            echo "选项:"
            echo "  --format json|text   输出格式（默认 json）"
            echo "  --dir <target>       目标目录（默认当前目录）"
            echo "  --exclude <pattern>  排除的目录/文件模式（可重复）"
            echo "  --help, -h           显示帮助"
            echo ""
            echo "统计工具优先级: tokei → cloc → python3(find+wc)"
            exit 0
            ;;
        *)
            echo "未知参数: $1" >&2; exit 1 ;;
    esac
done

cd "$TARGET_DIR" || { echo "无法进入目录: $TARGET_DIR" >&2; exit 1; }

# ---- 默认排除目录 ----
DEFAULT_EXCLUDES=(
    ".git" "node_modules" "target" "build" "out" "dist"
    "__pycache__" ".venv" "venv" ".tox" ".mypy_cache"
    ".pytest_cache" ".next" ".nuxt" "coverage" ".nyc_output"
    "vendor" "bower_components" ".cache" ".turbo"
    ".sass-cache" "CMakeFiles" "compile_commands.json"
)

join_excludes() {
    local sep="$1"; shift
    local result=""
    for item in "$@"; do
        if [[ -z "$result" ]]; then result="$item"
        else result="$result$sep$item"; fi
    done
    echo "$result"
}

ALL_EXCLUDES=("${DEFAULT_EXCLUDES[@]}" "${EXTRA_EXCLUDES[@]+"${EXTRA_EXCLUDES[@]}"}")

# =============================================================================
# 方法 1: tokei
# =============================================================================
try_tokei() {
    command -v tokei &>/dev/null || return 1

    local exclude_args=()
    for pat in "${ALL_EXCLUDES[@]}"; do
        exclude_args+=("--exclude" "$pat")
    done

    local tmpfile
    tmpfile=$(mktemp /tmp/tokei-output.XXXXXX)
    if tokei --output json "${exclude_args[@]}" . > "$tmpfile" 2>/dev/null; then
        python3 "$PYSCRIPT" --format "$OUTPUT_FORMAT" --tool tokei --input "$tmpfile"
        rm -f "$tmpfile"
        return 0
    fi
    rm -f "$tmpfile"
    return 1
}

# =============================================================================
# 方法 2: cloc
# =============================================================================
try_cloc() {
    command -v cloc &>/dev/null || return 1

    local exclude_str
    exclude_str=$(join_excludes "," "${ALL_EXCLUDES[@]}")

    local tmpfile
    tmpfile=$(mktemp /tmp/cloc-output.XXXXXX)
    if cloc --json --exclude-dir="$exclude_str" . > "$tmpfile" 2>/dev/null; then
        python3 "$PYSCRIPT" --format "$OUTPUT_FORMAT" --tool cloc --input "$tmpfile"
        rm -f "$tmpfile"
        return 0
    fi
    rm -f "$tmpfile"
    return 1
}

# =============================================================================
# 方法 3: python3 (find + wc)
# =============================================================================
fallback_python() {
    local find_prune=""
    # 构建 find 排除表达式
    for pat in "${ALL_EXCLUDES[@]}"; do
        find_prune="$find_prune -not -path \"*/$pat/*\" -not -path \"*/$pat\""
    done

    local files_list
    files_list=$(mktemp /tmp/collect-files.XXXXXX)
    trap "rm -f '$files_list'" EXIT

    # shellcheck disable=SC2086
    eval "find . $find_prune -type f" 2>/dev/null | while IFS= read -r filepath; do
        if [[ -r "$filepath" ]] && [[ -s "$filepath" ]]; then
            if perl -e 'exit(-B $ARGV[0] ? 1 : 0)' "$filepath" 2>/dev/null; then
                echo "$filepath"
            fi
        fi
    done > "$files_list"

    # 统计每个文件的行数，输出 "ext<TAB>lines"
    local data_file
    data_file=$(mktemp /tmp/collect-data.XXXXXX)
    while IFS= read -r filepath; do
        local ext
        ext="${filepath##*.}"
        if [[ "$ext" = "$filepath" ]] || [[ -z "$ext" ]] || [[ ${#ext} -gt 15 ]]; then
            ext="(no extension)"
        fi
        ext=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
        local lc
        lc=$(wc -l < "$filepath" 2>/dev/null || echo 0)
        printf "%s\t%d\n" "$ext" "$lc"
    done < "$files_list" > "$data_file"

    python3 "$PYSCRIPT" --format "$OUTPUT_FORMAT" --tool "shell (find+wc)" --raw "$data_file"
    rm -f "$data_file"
}

# =============================================================================
# 主流程
# =============================================================================

if try_tokei; then
    exit 0
elif try_cloc; then
    exit 0
else
    fallback_python
fi
