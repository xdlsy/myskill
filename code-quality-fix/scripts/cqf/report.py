"""把 Issue 聚合成报告：排序、分配 ID、汇总、过滤、写文件。"""

import json

from cqf.models import SEVERITY_ORDER

LANG_PREFIX = {"go": "GO", "java": "JAVA", "python": "PY", "unknown": "X"}


def assign_ids(issues):
    """按严重度（降序）后按文件/行排序，再按语言分配 LANG-NNN id。"""
    issues.sort(key=lambda i: (-SEVERITY_ORDER.get(i.severity, 0), i.file, i.line))
    counters = {}
    for issue in issues:
        prefix = LANG_PREFIX.get(issue.language, "X")
        counters[prefix] = counters.get(prefix, 0) + 1
        issue.id = f"{prefix}-{counters[prefix]:03d}"


def filter_issues(issues, category=None, min_severity=None, language=None):
    result = []
    for i in issues:
        if category and i.category != category:
            continue
        if language and i.language != language:
            continue
        if min_severity and SEVERITY_ORDER.get(i.severity, 0) < SEVERITY_ORDER[min_severity]:
            continue
        result.append(i)
    return result


def _count(values):
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    return counts


def build_report(issues, project_path, scan_time="1970-01-01T00:00:00Z"):
    return {
        "scan_time": scan_time,
        "project_path": project_path,
        "summary": {
            "total": len(issues),
            "by_severity": _count(i.severity for i in issues),
            "by_category": _count(i.category for i in issues),
            "by_language": _count(i.language for i in issues),
        },
        "issues": [i.to_dict() for i in issues],
    }


def write_report(report, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
