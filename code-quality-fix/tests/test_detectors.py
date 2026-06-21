import os
import tempfile

from cqf.detectors import detect_languages


def _write_tree(files):
    """创建一个临时目录，包含给定的 {相对路径: 内容} 文件。"""
    root = tempfile.mkdtemp()
    for rel, content in files.items():
        full = os.path.join(root, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(content)
    return root


def test_detect_go():
    root = _write_tree({"svc/go.mod": "module x\n"})
    assert detect_languages(root) == ["go"]


def test_detect_java_and_python():
    root = _write_tree({
        "app/pom.xml": "<project></project>",
        "proxy/pyproject.toml": "[project]\nname='p'\n",
    })
    assert set(detect_languages(root)) == {"java", "python"}


def test_detect_all_three():
    root = _write_tree({
        "go.mod": "", "pom.xml": "", "setup.py": "",
    })
    assert set(detect_languages(root)) == {"go", "java", "python"}


def test_detect_none():
    root = _write_tree({"readme.txt": "hi"})
    assert detect_languages(root) == []


from cqf.detectors import detect_tools, TOOLS_BY_LANGUAGE


def test_tools_by_language_groups():
    assert "golangci-lint" in TOOLS_BY_LANGUAGE["go"]
    assert "spotbugs" in TOOLS_BY_LANGUAGE["java"]
    assert "ruff" in TOOLS_BY_LANGUAGE["python"]
    assert "semgrep" in TOOLS_BY_LANGUAGE["all"]


def test_detect_tools_returns_status_per_tool():
    result = detect_tools()
    assert isinstance(result, dict)
    # 本测试环境里 python3 一定存在，所以至少有一条。
    assert "golangci-lint" in result
    assert "installed" in result["golangci-lint"]
    assert "version" in result["golangci-lint"]


from cqf.detectors import detect_test_commands


def test_detect_test_commands():
    root = _write_tree({"svc/go.mod": "", "app/pom.xml": ""})
    cmds = detect_test_commands(root)
    langs = {c["language"] for c in cmds}
    assert langs == {"go", "java"}
    assert any(c["command"] == "go test ./..." for c in cmds)
