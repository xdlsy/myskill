"""把每个扫描器的输出解析为统一的 Issue 列表。"""

import os

from cqf.models import Issue, normalize_severity, categorize


def _relativize(path, project_root):
    """转为相对 project_root 的规范化相对路径。

    绝对路径做 relpath；最后统一 normpath，消去前导 ``./``（bandit/ruff 对
    ``.`` 扫描时会给路径加 ``./``，semgrep 则不加——不归一化会让同一文件在
    报告里以两种写法出现，导致备份文件计数虚高、去重失效）。
    """
    if not path:
        return path
    if os.path.isabs(path):
        try:
            path = os.path.relpath(path, project_root)
        except ValueError:
            return path
    return os.path.normpath(path)


def parse_golangci(data, project_root):
    issues = []
    for entry in data.get("Issues", []):
        pos = entry.get("Pos", {})
        rule_id = entry.get("FromLinter", "")
        line = pos.get("Line", 0)
        issues.append(Issue(
            id="",
            file=_relativize(pos.get("Filename", ""), project_root),
            line=line,
            end_line=line,
            language="go",
            tool="golangci-lint",
            rule_id=rule_id,
            severity=normalize_severity("WARNING", "golangci-lint"),
            category=categorize("golangci-lint", rule_id),
            message=entry.get("Text", ""),
            code_snippet="",
        ))
    return issues


def parse_gosec(data, project_root):
    issues = []
    for entry in data.get("Issues", []):
        line = entry.get("line", 0)
        issues.append(Issue(
            id="",
            file=_relativize(entry.get("file", ""), project_root),
            line=line,
            end_line=line,
            language="go",
            tool="gosec",
            rule_id=entry.get("rule_id", ""),
            severity=normalize_severity(entry.get("severity", "LOW"), "gosec"),
            category="security",
            message=entry.get("details", ""),
            code_snippet=entry.get("code", ""),
        ))
    return issues


def parse_ruff(data, project_root):
    """ruff --output-format=json 返回一个 JSON 数组。"""
    issues = []
    for entry in data:
        loc = entry.get("location", {})
        rule_id = entry.get("code", "")
        line = loc.get("row", 0)
        issues.append(Issue(
            id="",
            file=_relativize(entry.get("filename", ""), project_root),
            line=line,
            end_line=line,
            language="python",
            tool="ruff",
            rule_id=rule_id,
            severity=normalize_severity("WARNING", "ruff"),
            category=categorize("ruff", rule_id),
            message=entry.get("message", ""),
            code_snippet="",
        ))
    return issues


def parse_bandit(data, project_root):
    issues = []
    for entry in data.get("results", []):
        line = entry.get("line_number", 0)
        issues.append(Issue(
            id="",
            file=_relativize(entry.get("filename", ""), project_root),
            line=line,
            end_line=line,
            language="python",
            tool="bandit",
            rule_id=entry.get("test_id", ""),
            severity=normalize_severity(entry.get("issue_severity", "LOW"), "bandit"),
            category="security",
            message=entry.get("issue_text", ""),
            code_snippet="",
        ))
    return issues


import xml.etree.ElementTree as ET


def parse_spotbugs(xml_text, project_root):
    root = ET.fromstring(xml_text)
    issues = []
    for bug in root.findall("BugInstance"):
        source = bug.find("SourceLine")
        if source is None:
            continue
        line = int(source.get("start", "0") or 0)
        rule_id = bug.get("type", "")
        priority = bug.get("priority", "3")
        issues.append(Issue(
            id="",
            file=_relativize(source.get("sourcepath", ""), project_root),
            line=line,
            end_line=int(source.get("end", str(line)) or line),
            language="java",
            tool="spotbugs",
            rule_id=rule_id,
            severity=normalize_severity(priority, "spotbugs"),
            category=categorize("spotbugs", rule_id),
            message=bug.findtext("LongMessage") or bug.findtext("ShortMessage") or "",
            code_snippet="",
        ))
    return issues


def parse_pmd(xml_text, project_root):
    root = ET.fromstring(xml_text)
    issues = []
    for f in root.findall("file"):
        path = _relativize(f.get("name", ""), project_root)
        for v in f.findall("violation"):
            begin = int(v.get("beginline", "0") or 0)
            end = int(v.get("endline", str(begin)) or begin)
            rule_id = v.get("rule", "")
            priority = v.get("priority", "5")
            issues.append(Issue(
                id="",
                file=path,
                line=begin,
                end_line=end,
                language="java",
                tool="pmd",
                rule_id=rule_id,
                severity=normalize_severity(priority, "pmd"),
                category=categorize("pmd", rule_id),
                message=(v.text or "").strip(),
                code_snippet="",
            ))
    return issues


def parse_checkstyle(xml_text, project_root):
    root = ET.fromstring(xml_text)
    issues = []
    for f in root.findall("file"):
        path = _relativize(f.get("name", ""), project_root)
        for err in f.findall("error"):
            line = int(err.get("line", "0") or 0)
            sev = err.get("severity", "warning")
            # source 形如 "...Check"；取一个短规则 id。
            source = err.get("source", "")
            rule_id = source.rsplit(".", 1)[-1] if source else "checkstyle"
            issues.append(Issue(
                id="",
                file=path,
                line=line,
                end_line=line,
                language="java",
                tool="checkstyle",
                rule_id=rule_id,
                severity=normalize_severity(sev, "checkstyle"),
                category=categorize("checkstyle", rule_id),
                message=err.get("message", ""),
                code_snippet="",
            ))
    return issues


def _infer_language_from_path(path):
    ext = os.path.splitext(path)[1].lower()
    return {".go": "go", ".java": "java", ".py": "python"}.get(ext, "unknown")


def parse_semgrep(data, project_root, language_hint=None):
    """language_hint 覆盖按路径推断（monorepo 场景有用）。"""
    issues = []
    for entry in data.get("results", []):
        start = entry.get("start", {})
        end = entry.get("end", {})
        extra = entry.get("extra", {})
        path = entry.get("path", "")
        line = start.get("line", 0)
        rule_id = entry.get("check_id", "")
        issues.append(Issue(
            id="",
            file=_relativize(path, project_root),
            line=line,
            end_line=end.get("line", line),
            language=language_hint or _infer_language_from_path(path),
            tool="semgrep",
            rule_id=rule_id,
            severity=normalize_severity(extra.get("severity", "INFO"), "semgrep"),
            category=categorize("semgrep", rule_id),
            message=extra.get("message", ""),
            code_snippet=extra.get("lines", ""),
        ))
    return issues
