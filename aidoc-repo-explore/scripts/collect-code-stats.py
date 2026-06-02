#!/usr/bin/env python3
# =============================================================================
# collect-code-stats.py — 代码规模与语言分布采集（python3 核心处理引擎）
# =============================================================================
# 由 collect-code-stats.sh 调用，也可独立使用：
#   python3 collect-code-stats.py --format json --tool tokei --input <file>
#   python3 collect-code-stats.py --format text --tool cloc --input <file>
#   python3 collect-code-stats.py --format json --tool "shell (find+wc)" --raw <file>
#   python3 collect-code-stats.py --format json --tool find-wc --scan <dir>
# =============================================================================

import argparse
import json
import os
import sys
from collections import defaultdict

# ---------------------------------------------------------------------------
# 语言映射表：扩展名 → 语言名称
# ---------------------------------------------------------------------------
LANG_MAP = {
    # C/C++
    "c": "C", "h": "C Header",
    "cpp": "C++", "cc": "C++", "cxx": "C++", "c++": "C++",
    "hpp": "C++ Header", "hh": "C++ Header", "hxx": "C++ Header",
    # Java / JVM
    "java": "Java", "kt": "Kotlin", "kts": "Kotlin Script",
    "scala": "Scala", "groovy": "Groovy",
    # Python
    "py": "Python", "pyx": "Cython", "pxd": "Cython", "pyi": "Python Stub",
    # JavaScript / TypeScript
    "js": "JavaScript", "jsx": "JavaScript JSX",
    "mjs": "JavaScript", "cjs": "JavaScript",
    "ts": "TypeScript", "tsx": "TypeScript TSX",
    "cts": "TypeScript", "mts": "TypeScript",
    # Web
    "vue": "Vue", "svelte": "Svelte",
    "html": "HTML", "htm": "HTML",
    # Go
    "go": "Go",
    # Rust
    "rs": "Rust",
    # Swift / ObjC
    "swift": "Swift", "m": "Objective-C", "mm": "Objective-C++",
    # .NET
    "cs": "C#", "vb": "Visual Basic", "fs": "F#", "fsx": "F# Script",
    # Ruby
    "rb": "Ruby", "rake": "Ruby",
    # PHP
    "php": "PHP", "phtml": "PHP",
    # Shell
    "sh": "Shell", "bash": "Bash", "zsh": "Zsh", "fish": "Fish",
    # Perl
    "pl": "Perl", "pm": "Perl",
    # Lua
    "lua": "Lua",
    # R
    "r": "R", "rmd": "R Markdown",
    # Haskell
    "hs": "Haskell", "lhs": "Haskell",
    # Elixir / Erlang
    "ex": "Elixir", "exs": "Elixir Script",
    "erl": "Erlang", "hrl": "Erlang Header",
    # Clojure
    "clj": "Clojure", "cljs": "ClojureScript", "cljc": "Clojure",
    "edn": "Clojure EDN",
    # Dart
    "dart": "Dart",
    # Zig
    "zig": "Zig",
    # Nim
    "nim": "Nim",
    # Julia
    "jl": "Julia",
    # Fortran
    "f90": "Fortran", "f95": "Fortran", "f03": "Fortran",
    "f08": "Fortran", "f": "Fortran", "for": "Fortran",
    # 协议 / IDL
    "proto": "Protocol Buffers", "thrift": "Thrift", "avdl": "Avro IDL",
    # 构建
    "cmake": "CMake",
    # SQL
    "sql": "SQL",
    # Docker / Containerfile
    "dockerfile": "Dockerfile",
    # IaC
    "tf": "Terraform", "tfvars": "Terraform", "hcl": "HCL",
    # Nix
    "nix": "Nix",
    # Solidity
    "sol": "Solidity",
    # Vala
    "vala": "Vala",
    # 样式
    "css": "CSS", "scss": "SCSS", "sass": "Sass", "less": "Less",
}

# 非源码扩展名（文档 / 配置 / 数据 / 媒体）
NON_SOURCE_EXTS = {
    "md", "mdx", "rst", "txt", "adoc", "asciidoc",
    "json", "yaml", "yml", "toml", "ini", "cfg", "conf", "config",
    "xml", "plist", "properties", "env", "example",
    "csv", "tsv", "dat", "data",
    "svg", "png", "jpg", "jpeg", "gif", "ico", "webp", "bmp",
    "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
    "lock", "sum", "sha256", "md5",
    "patch", "diff",
    "graffle", "sketch",
}

# 源码文件后缀白名单 —— find+wc 兜底时只统计这些后缀的文件
SOURCE_EXTS = frozenset({
    # C/C++
    "c", "h", "cpp", "cc", "cxx", "c++", "hpp", "hh", "hxx",
    # Java / JVM
    "java", "kt", "kts", "scala", "groovy",
    # Python
    "py", "pyx", "pxd", "pyi",
    # JavaScript / TypeScript
    "js", "jsx", "mjs", "cjs", "ts", "tsx", "cts", "mts",
    # Web
    "vue", "svelte", "html", "htm",
    # Go
    "go",
    # Rust
    "rs",
    # Swift / ObjC
    "swift", "m", "mm",
    # .NET
    "cs", "vb", "fs", "fsx",
    # Ruby
    "rb", "rake",
    # PHP
    "php", "phtml",
    # Shell
    "sh", "bash", "zsh", "fish",
    # Perl
    "pl", "pm",
    # Lua
    "lua",
    # R
    "r", "rmd",
    # Haskell
    "hs", "lhs",
    # Elixir / Erlang
    "ex", "exs", "erl", "hrl",
    # Clojure
    "clj", "cljs", "cljc", "edn",
    # Dart
    "dart",
    # Zig
    "zig",
    # Nim
    "nim",
    # Julia
    "jl",
    # Fortran
    "f90", "f95", "f03", "f08", "f", "for",
    # 协议 / IDL
    "proto", "thrift", "avdl",
    # 构建
    "cmake",
    # SQL
    "sql",
    # Docker
    "dockerfile",
    # IaC
    "tf", "tfvars", "hcl",
    # Nix
    "nix",
    # Solidity
    "sol",
    # Vala
    "vala",
    # 样式
    "css", "scss", "sass", "less",
})


def ext_to_lang(ext: str) -> str:
    """将文件扩展名映射为语言名称."""
    return LANG_MAP.get(ext, f"Other ({ext})")


def is_source(ext: str) -> bool:
    """判断扩展名是否对应源代码文件."""
    return ext not in NON_SOURCE_EXTS


# ---------------------------------------------------------------------------
# 数据源解析
# ---------------------------------------------------------------------------

def parse_tokei(path: str) -> dict:
    """解析 tokei --output json 的输出."""
    with open(path) as f:
        data = json.load(f)

    languages = {}
    total_code = 0
    for lang, stats in data.items():
        if lang == "Total":
            continue
        code = stats.get("code", 0)
        comments = stats.get("comments", 0)
        blanks = stats.get("blanks", 0)
        reports = stats.get("reports", [])
        files = len(reports) if isinstance(reports, list) else reports
        if code == 0 and files == 0:
            continue
        languages[lang] = {
            "files": files,
            "code": code,
            "comments": comments,
            "blanks": blanks,
            "is_source": True,  # tokei 默认只统计源码文件
        }
        total_code += code
    return languages, total_code


def parse_cloc(path: str) -> dict:
    """解析 cloc --json 的输出."""
    with open(path) as f:
        data = json.load(f)

    languages = {}
    total_code = 0
    for lang, stats in data.items():
        if lang in ("header", "SUM"):
            continue
        code = stats.get("code", 0)
        comments = stats.get("comment", 0)
        blanks = stats.get("blank", 0)
        files = stats.get("nFiles", 0)
        if code == 0 and files == 0:
            continue
        languages[lang] = {
            "files": files,
            "code": code,
            "comments": comments,
            "blanks": blanks,
            "is_source": True,
        }
        total_code += code
    return languages, total_code


def parse_raw(path: str) -> dict:
    """解析 find+wc 原始数据文件（每行: ext<TAB>lines）.

    统计所有文件类型，源码/非源码分别标记。返回 (languages, source_code_total)。
    占比以 source_code_total 为基数计算，避免文档/配置文件扭曲语言分布。
    """
    ext_files = defaultdict(int)
    ext_lines = defaultdict(int)

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) != 2:
                continue
            ext, lc = parts[0], int(parts[1])
            ext_files[ext] += 1
            ext_lines[ext] += lc

    # 按语言名称合并，标记源码/非源码
    languages = {}
    source_code_total = 0
    for ext, files in sorted(ext_files.items()):
        lines = ext_lines.get(ext, 0)
        if lines == 0:
            continue
        lang = ext_to_lang(ext)
        src = is_source(ext)
        if lang in languages:
            languages[lang]["files"] += files
            languages[lang]["code"] += lines
        else:
            languages[lang] = {
                "files": files,
                "code": lines,
                "comments": 0,
                "blanks": 0,
                "is_source": src,
            }
        if src:
            source_code_total += lines
    return languages, source_code_total


def scan_directly(target_dir: str, excludes: list) -> dict:
    """直接在目标目录扫描文件并统计（不依赖 tokei/cloc）。

    统计所有文件类型，源码/非源码分别标记。返回 (languages, source_code_total)。
    占比以 source_code_total 为基数计算，避免文档/配置文件扭曲语言分布。
    """
    import subprocess

    # 构建 find 命令
    find_cmd = ["find", target_dir]
    for pat in excludes:
        find_cmd.extend(["-not", "-path", f"*/{pat}/*", "-not", "-path", f"*/{pat}"])
    find_cmd.extend(["-type", "f"])

    try:
        result = subprocess.run(find_cmd, capture_output=True, text=True)
        filepaths = [p.strip() for p in result.stdout.split("\n") if p.strip()]
    except Exception:
        filepaths = []

    ext_files = defaultdict(int)
    ext_lines = defaultdict(int)

    for fp in filepaths:
        ext = os.path.splitext(fp)[1].lstrip(".").lower()
        if not ext or len(ext) > 15:
            ext = "(no extension)"

        if not os.path.isfile(fp) or os.path.getsize(fp) == 0:
            continue
        # 检查是否为文本文件（跳过二进制）
        try:
            with open(fp, "rb") as fh:
                chunk = fh.read(512)
            if b"\x00" in chunk:
                continue
        except Exception:
            continue

        try:
            with open(fp, "r", errors="ignore") as fh:
                lc = sum(1 for _ in fh)
        except Exception:
            lc = 0

        ext_files[ext] += 1
        ext_lines[ext] += lc

    # 按语言名称合并，标记源码/非源码
    languages = {}
    source_code_total = 0
    for ext, files in sorted(ext_files.items()):
        lines = ext_lines.get(ext, 0)
        if lines == 0:
            continue
        lang = ext_to_lang(ext)
        src = is_source(ext)
        if lang in languages:
            languages[lang]["files"] += files
            languages[lang]["code"] += lines
        else:
            languages[lang] = {
                "files": files,
                "code": lines,
                "comments": 0,
                "blanks": 0,
                "is_source": src,
            }
        if src:
            source_code_total += lines
    return languages, source_code_total


# ---------------------------------------------------------------------------
# 结果构建与输出
# ---------------------------------------------------------------------------

def build_result(languages: dict, source_code_total: int, tool: str,
                 warning: str = None) -> dict:
    """构建最终结果字典.

    - 占比以全部行数（源码 + 非源码）为基数，反映完整的文件内容构成
    - 主语言从源码文件中选取，避免 Markdown 等文档文件成为主语言
    """
    # 全部行数 = 源码 + 非源码
    all_lines = sum(s["code"] for s in languages.values())
    if all_lines == 0:
        return {
            "tool": tool,
            "total_code": 0,
            "total_files": 0,
            "languages": {},
            "primary_language": None,
        }

    # 计算占比（以全部行数为基数）
    for stats in languages.values():
        stats["percentage"] = round(stats["code"] / all_lines * 100, 1)

    # 主语言从源码中选取；若没有源码文件则回退到全部语言
    source_langs = {l: s for l, s in languages.items()
                    if s.get("is_source", False)}
    primary_pool = source_langs if source_langs else languages
    primary = max(primary_pool, key=lambda l: primary_pool[l]["code"])
    total_files = sum(s["files"] for s in languages.values())

    result = {
        "tool": tool,
        "total_code": all_lines,
        "source_code_total": source_code_total,
        "total_files": total_files,
        "languages": languages,
        "primary_language": primary,
        "primary_language_code": languages[primary]["code"],
        "primary_language_files": languages[primary]["files"],
        "primary_language_percentage": languages[primary]["percentage"],
    }
    if warning:
        result["warning"] = warning
    return result


def output_json(result: dict):
    """JSON 输出."""
    print(json.dumps(result, indent=2, ensure_ascii=False))


def output_text(result: dict):
    """人类可读文本输出."""
    source_total = result.get("source_code_total", result["total_code"])
    all_lines = result["total_code"]

    print("📊 代码规模与语言分布")
    print(f"   采集工具: {result['tool']}")
    print(f"   全部行数: {all_lines:,}（源码 {source_total:,} + 非源码 {all_lines - source_total:,}）")
    print(f"   总文件数: {result['total_files']:,}")
    if result.get("warning"):
        print(f"   ⚠️  {result['warning']}")
    print()

    if not result["languages"]:
        print("   未检测到任何代码文件。")
        return

    # 按代码行数降序排列
    langs = sorted(result["languages"].items(),
                   key=lambda x: x[1]["code"], reverse=True)

    name_w = max(max(len(l) for l, _ in langs), 20)
    files_w = 8
    code_w = 12
    pct_w = 8
    src_w = 6

    header = (f'   {"Language":<{name_w}} {"Files":>{files_w}} '
              f'{"Code":>{code_w}} {"%":>{pct_w}} {"Source":>{src_w}}')
    print(header)
    print("   " + "-" * (name_w + files_w + code_w + pct_w + src_w + 4))

    src_sum = 0
    nonsrc_sum = 0

    for lang, stats in langs:
        is_src = stats.get("is_source", True)
        src_mark = "✓" if is_src else "·"
        comments = stats.get("comments", 0)
        comment_str = f" (+{comments:,} comments)" if comments > 0 else ""
        print(f'   {lang:<{name_w}} {stats["files"]:>{files_w},} '
              f'{stats["code"]:>{code_w},}{comment_str} '
              f'{stats["percentage"]:>{pct_w - 1}.1f}% {src_mark:>{src_w}}')

        if is_src:
            src_sum += stats["code"]
        else:
            nonsrc_sum += stats["code"]

    print()
    print(f'   ✦ 主语言: {result["primary_language"]} '
          f'({result["primary_language_percentage"]:.1f}%, '
          f'{result["primary_language_files"]} 文件, '
          f'{result["primary_language_code"]:,} 行)')
    print(f"   ✦ 源码行数: {src_sum:,}  |  非源码行数: {nonsrc_sum:,}")
    if result.get("warning"):
        print(f"   ⚠ {result['warning']}")


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="代码规模与语言分布采集脚本（由 collect-code-stats.sh 调用）"
    )
    parser.add_argument("--format", choices=["json", "text"], default="json",
                        help="输出格式")
    parser.add_argument("--tool", default="unknown",
                        help="使用的采集工具名称")
    parser.add_argument("--input", help="tokei/cloc JSON 输出文件路径")
    parser.add_argument("--raw", help="find+wc 原始数据文件路径")
    parser.add_argument("--scan", help="直接扫描的目标目录")
    parser.add_argument("--exclude", nargs="*", default=[],
                        help="排除的目录模式")
    args = parser.parse_args()

    tool = args.tool
    warning = None

    # ---- 根据数据源解析 ----
    if args.input:
        # tokei / cloc 的 JSON 输出（所有语言均为源码）
        if "tokei" in tool.lower():
            languages, source_total = parse_tokei(args.input)
        else:
            languages, source_total = parse_cloc(args.input)
    elif args.raw:
        # find+wc 原始数据
        languages, source_total = parse_raw(args.raw)
        warning = "注释行数未统计（需要安装 tokei 或 cloc）"
    elif args.scan:
        # 直接扫描
        languages, source_total = scan_directly(args.scan, args.exclude)
        tool = "python3 (find+wc)"
        warning = "注释行数未统计（需要安装 tokei 或 cloc）"
    else:
        print("错误: 必须指定 --input, --raw, 或 --scan", file=sys.stderr)
        sys.exit(1)

    result = build_result(languages, source_total, tool, warning)

    if args.format == "text":
        output_text(result)
    else:
        output_json(result)


if __name__ == "__main__":
    main()
