from cqf.parsers import parse_golangci, parse_gosec, parse_ruff, parse_bandit, \
    parse_spotbugs, parse_pmd, parse_checkstyle, parse_semgrep, _relativize
from conftest import load_fixture


def test_relativize_strips_dot_slash_prefix():
    """bandit/ruff 扫描 '.' 时给路径加 './'；必须归一化，否则同一文件会
    在报告里出现两种写法（导致备份计数虚高、去重失效）。"""
    assert _relativize("./browser-proxy/main.py", "/abs") == "browser-proxy/main.py"
    assert _relativize("browser-proxy/main.py", "/abs") == "browser-proxy/main.py"
    assert _relativize("/abs/src/x.go", "/abs") == "src/x.go"
    assert _relativize("", "/abs") == ""


def test_parse_golangci_quality_and_style():
    data = load_fixture("golangci.json")
    issues = parse_golangci(data, "/abs")
    assert len(issues) == 2
    funlen = next(i for i in issues if i.rule_id == "funlen")
    assert funlen.language == "go"
    assert funlen.tool == "golangci-lint"
    assert funlen.category == "quality"
    assert funlen.file == "src/service/cache.go"
    assert funlen.line == 42
    gofmt = next(i for i in issues if i.rule_id == "gofmt")
    assert gofmt.category == "style"


def test_parse_gosec_security_issue():
    data = load_fixture("gosec.json")
    issues = parse_gosec(data, "/abs")
    assert len(issues) == 1
    issue = issues[0]
    assert issue.tool == "gosec"
    assert issue.category == "security"
    assert issue.severity == "HIGH"
    assert issue.rule_id == "G201"
    assert issue.code_snippet.startswith("db.Exec")
    # fixture 中的绝对路径相对于项目根做相对化。
    assert issue.file == "src/service/cache.go"


def test_parse_ruff_style_and_quality():
    data = load_fixture("ruff.json")
    issues = parse_ruff(data, "/abs")
    assert len(issues) == 2
    e501 = next(i for i in issues if i.rule_id == "E501")
    assert e501.category == "style"
    assert e501.line == 30
    assert e501.file == "browser_proxy/main.py"
    sim = next(i for i in issues if i.rule_id == "SIM102")
    assert sim.category == "quality"


def test_parse_bandit_security():
    data = load_fixture("bandit.json")
    issues = parse_bandit(data, "/abs")
    assert len(issues) == 1
    issue = issues[0]
    assert issue.tool == "bandit"
    assert issue.category == "security"
    assert issue.severity == "HIGH"
    assert issue.rule_id == "B608"
    assert issue.line == 55


def test_parse_spotbugs_security_and_quality():
    data = load_fixture("spotbugs.xml")
    issues = parse_spotbugs(data, "/abs")
    assert len(issues) == 2
    sql = next(i for i in issues if i.rule_id == "SQL_INJECTION_JDBC")
    assert sql.category == "security"
    assert sql.severity == "HIGH"          # priority 1
    assert sql.file == "src/main/java/com/example/UserService.java"
    assert sql.line == 155
    np = next(i for i in issues if i.rule_id == "NP_NULL_ON_SOME_PATH")
    assert np.category == "quality"        # 数字前缀码 → quality
    assert np.severity == "MEDIUM"         # priority 2


def test_parse_pmd_quality():
    data = load_fixture("pmd.xml")
    issues = parse_pmd(data, "/abs")
    assert len(issues) == 1
    issue = issues[0]
    assert issue.tool == "pmd"
    assert issue.category == "quality"
    assert issue.severity == "MEDIUM"      # priority 3
    assert issue.line == 200
    assert issue.end_line == 280


def test_parse_checkstyle_style():
    data = load_fixture("checkstyle.xml")
    issues = parse_checkstyle(data, "/abs")
    assert len(issues) == 1
    issue = issues[0]
    assert issue.tool == "checkstyle"
    assert issue.category == "style"
    assert issue.severity == "HIGH"        # severity=error
    assert issue.line == 12


def test_parse_semgrep_security():
    data = load_fixture("semgrep.json")
    issues = parse_semgrep(data, "/abs", language_hint="java")
    assert len(issues) == 1
    issue = issues[0]
    assert issue.tool == "semgrep"
    assert issue.category == "security"
    assert issue.severity == "HIGH"        # ERROR -> HIGH
    assert issue.language == "java"
    assert issue.line == 60
    assert issue.rule_id == "java.lang.security.audit.sqli.jdbc-sqli"
    assert "stmt.execute" in issue.code_snippet
