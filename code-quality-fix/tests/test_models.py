from cqf.models import Issue, normalize_severity, categorize, SEVERITY_ORDER


def test_normalize_severity_gosec_passes_through():
    assert normalize_severity("HIGH", "gosec") == "HIGH"
    assert normalize_severity("medium", "gosec") == "MEDIUM"


def test_normalize_severity_spotbugs_priority():
    assert normalize_severity("1", "spotbugs") == "HIGH"
    assert normalize_severity("2", "spotbugs") == "MEDIUM"
    assert normalize_severity("3", "spotbugs") == "LOW"


def test_normalize_severity_pmd_priority():
    assert normalize_severity("1", "pmd") == "HIGH"
    assert normalize_severity("3", "pmd") == "MEDIUM"
    assert normalize_severity("5", "pmd") == "LOW"


def test_normalize_severity_unknown_falls_to_low():
    assert normalize_severity("weird", "gosec") == "LOW"


def test_categorize_security_tools():
    assert categorize("gosec", "G201") == "security"
    assert categorize("bandit", "B608") == "security"
    assert categorize("semgrep", "java.lang.security.audit") == "security"


def test_categorize_quality_and_style():
    assert categorize("pmd", "ExcessiveMethodLength") == "quality"
    assert categorize("checkstyle", "FileLength") == "style"
    assert categorize("ruff", "E501") == "style"


def test_categorize_golangci_by_linter():
    assert categorize("golangci-lint", "gosec") == "security"
    assert categorize("golangci-lint", "funlen") == "quality"
    assert categorize("golangci-lint", "gofmt") == "style"


def test_issue_to_dict_roundtrip():
    issue = Issue(
        id="GO-001", file="a.go", line=1, end_line=1, language="go",
        tool="gosec", rule_id="G201", severity="HIGH", category="security",
        message="sql injection", code_snippet="x", fixable=True,
    )
    d = issue.to_dict()
    assert d["id"] == "GO-001"
    assert d["severity"] == "HIGH"


def test_severity_order_ranks_high_above_low():
    assert SEVERITY_ORDER["HIGH"] > SEVERITY_ORDER["MEDIUM"] > SEVERITY_ORDER["LOW"]
