"""安装缺失的扫描器二进制。python 工具用 pip，go 工具用 go install。"""

import subprocess

INSTALL_COMMANDS = {
    "golangci-lint": ["go", "install", "github.com/golangci/golangci-lint/cmd/golangci-lint@latest"],
    "gosec": ["go", "install", "github.com/securego/gosec/v2/cmd/gosec@latest"],
    "ruff": ["pip", "install", "ruff"],
    "bandit": ["pip", "install", "bandit"],
    "semgrep": ["pip", "install", "semgrep"],
}


def build_install_commands(tool_status):
    """返回报告为未安装的工具的安装命令列表。"""
    cmds = []
    for tool, status in tool_status.items():
        if not status.get("installed") and tool in INSTALL_COMMANDS:
            cmds.append(INSTALL_COMMANDS[tool])
    return cmds


def install_missing_tools(tool_status, runner=None):
    """执行每个缺失工具的安装命令。runner 注入便于测试。

    返回 {tool, success, output} 列表。
    """
    run = runner or (lambda cmd: subprocess.run(cmd, capture_output=True, text=True, timeout=300))
    results = []
    for tool, status in tool_status.items():
        if status.get("installed") or tool not in INSTALL_COMMANDS:
            continue
        proc = run(INSTALL_COMMANDS[tool])
        results.append({
            "tool": tool,
            "success": proc.returncode == 0,
            "output": (proc.stdout + proc.stderr).strip(),
        })
    return results
