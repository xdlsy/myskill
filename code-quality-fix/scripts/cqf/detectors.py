"""通过扫描构建文件来检测项目包含哪些语言。"""

import os

# 每种语言由其任一 marker 文件的存在来判定。
LANGUAGE_MARKERS = {
    "go": ["go.mod", "go.work"],
    "java": ["pom.xml", "build.gradle", "build.gradle.kts"],
    "python": ["pyproject.toml", "setup.py", "requirements.txt"],
}


def detect_languages(project_root):
    """返回在 project_root 下发现的语言列表。

    递归搜索，支持多模块的 monorepo。
    顺序稳定：go, java, python（LANGUAGE_MARKERS 的插入顺序）。
    """
    found = []
    for root, _dirs, files in os.walk(project_root):
        # 跳过常见的噪声目录。
        if any(part in {".git", "node_modules", "vendor", ".tmp", "target"}
               for part in root.split(os.sep)):
            continue
        for lang, markers in LANGUAGE_MARKERS.items():
            if lang not in found and any(m in files for m in markers):
                found.append(lang)
    return found


import shutil
import subprocess

# 工具按所扫描语言分组。"all" = 跨语言。
TOOLS_BY_LANGUAGE = {
    "go": ["golangci-lint", "gosec"],
    "java": ["spotbugs", "pmd", "checkstyle"],
    "python": ["ruff", "bandit"],
    "all": ["semgrep"],
}

# 如何查询工具版本（取输出第一行）。Maven 插件没有独立二进制，
# 所以视为"通过 mvn 始终可用"。
VERSION_ARGS = {
    "golangci-lint": ["golangci-lint", "--version"],
    "gosec": ["gosec", "-version"],
    "semgrep": ["semgrep", "--version"],
    "ruff": ["ruff", "--version"],
    "bandit": ["bandit", "--version"],
}

# 作为 Maven 插件运行的工具（无 PATH 二进制）。仅当 mvn 存在时算已安装。
MAVEN_PLUGINS = {"spotbugs", "pmd", "checkstyle"}


def _tool_status(name):
    if name in MAVEN_PLUGINS:
        mvn = shutil.which("mvn")
        return {"installed": bool(mvn), "version": "", "via_mvn": True}
    args = VERSION_ARGS.get(name)
    binary = args[0] if args else name
    if not shutil.which(binary):
        return {"installed": False, "version": ""}
    version = ""
    try:
        out = subprocess.run(args, capture_output=True, text=True, timeout=10)
        version = (out.stdout or out.stderr).strip().splitlines()[0] if (out.stdout or out.stderr) else ""
    except Exception:
        version = ""
    return {"installed": True, "version": version}


def detect_tools():
    """返回 {工具名: {installed, version, [via_mvn]}}，覆盖每个扫描器。"""
    all_tools = sorted({t for group in TOOLS_BY_LANGUAGE.values() for t in group})
    return {name: _tool_status(name) for name in all_tools}


TEST_COMMANDS = {
    "go":     {"detect": "go.mod",         "command": "go test ./...",        "timeout": 120},
    "java":   {"detect": "pom.xml",        "command": "mvn test -q",          "timeout": 300},
    "python": {"detect": "pyproject.toml", "command": "pytest --tb=short -q", "timeout": 120},
}


def detect_test_commands(project_root):
    """返回本项目适用的测试命令列表。"""
    cmds = []
    seen = set()
    for root, _dirs, files in os.walk(project_root):
        if any(part in {".git", "node_modules", "vendor", ".tmp", "target"}
               for part in root.split(os.sep)):
            continue
        for lang, spec in TEST_COMMANDS.items():
            if lang in seen:
                continue
            if spec["detect"] in files:
                seen.add(lang)
                cmds.append({"language": lang, **spec, "cwd": root})
    return cmds
