from cqf.models import Issue
from cqf.report import assign_ids, filter_issues, build_report, write_report
import json
import os
import tempfile


def _issue(file, lang, sev, cat, line=1):
    return Issue(id="", file=file, line=line, end_line=line, language=lang,
                 tool="t", rule_id="r", severity=sev, category=cat,
                 message="m", code_snippet="", fixable=True)


def test_assign_ids_language_prefixed_and_severity_sorted():
    issues = [
        _issue("a.go", "go", "LOW", "quality"),
        _issue("b.go", "go", "HIGH", "security"),
        _issue("c.py", "python", "MEDIUM", "quality"),
    ]
    assign_ids(issues)
    # go 内 HIGH 在前。
    high = next(i for i in issues if i.severity == "HIGH")
    assert high.id == "GO-001"
    low = next(i for i in issues if i.severity == "LOW")
    assert low.id == "GO-002"
    py = next(i for i in issues if i.language == "python")
    assert py.id == "PY-001"


def test_filter_issues_by_category_and_severity():
    issues = [
        _issue("a.go", "go", "HIGH", "security"),
        _issue("b.go", "go", "LOW", "quality"),
    ]
    only_sec = filter_issues(issues, category="security")
    assert len(only_sec) == 1 and only_sec[0].category == "security"
    only_high = filter_issues(issues, min_severity="HIGH")
    assert len(only_high) == 1 and only_high[0].severity == "HIGH"


def test_build_report_summary_aggregates():
    issues = [
        _issue("a.go", "go", "HIGH", "security"),
        _issue("b.go", "go", "LOW", "quality"),
        _issue("c.py", "python", "MEDIUM", "quality"),
    ]
    report = build_report(issues, "/proj")
    assert report["summary"]["total"] == 3
    assert report["summary"]["by_severity"]["HIGH"] == 1
    assert report["summary"]["by_category"]["quality"] == 2
    assert report["summary"]["by_language"]["go"] == 2
    assert report["project_path"] == "/proj"


def test_write_report_creates_json_file():
    issues = [_issue("a.go", "go", "HIGH", "security")]
    assign_ids(issues)
    report = build_report(issues, "/proj")
    out = os.path.join(tempfile.mkdtemp(), "report.json")
    write_report(report, out)
    with open(out) as f:
        loaded = json.load(f)
    assert loaded["summary"]["total"] == 1
    assert loaded["issues"][0]["id"] == "GO-001"
