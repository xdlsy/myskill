from cqf.installer import INSTALL_COMMANDS, build_install_commands


def test_install_commands_cover_all_tools():
    for tool in ["golangci-lint", "gosec", "ruff", "bandit", "semgrep"]:
        assert tool in INSTALL_COMMANDS


def test_build_install_commands_filters_missing():
    status = {
        "golangci-lint": {"installed": True},
        "ruff": {"installed": False},
        "bandit": {"installed": False},
    }
    cmds = build_install_commands(status)
    # golangci-lint 已安装 → 排除；ruff + bandit 包含。
    assert any("ruff" in c for c in cmds)
    assert any("bandit" in c for c in cmds)
    assert not any("golangci-lint" in c for c in cmds)
