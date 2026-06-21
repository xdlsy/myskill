#!/usr/bin/env python3
"""code-quality-fix 扫描器 CLI。

运行语言对应的扫描器，把输出解析为统一报告格式，写出 report.json。
不做任何修复 —— 修复由 Claude 按 SKILL.md 完成。

用法：
  scan.py --check-tools                              # 打印工具状态 JSON
  scan.py --install-tools                            # 安装缺失扫描器
  scan.py --detect-tests --project <root>            # 打印测试命令 JSON
  scan.py --backup <report.json> --backup-root <dir> --backup-id <ts>
  scan.py --restore --backup-root <dir> --backup-id <ts> [--project <root>]
  scan.py --project <root> --output <report.json> [--lang L] [--category C] [--severity S]
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone


def _utc_now_iso():
    """当前 UTC 时间，ISO 8601 带 Z 后缀（报告 scan_time 用）。"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cqf.detectors import detect_languages, detect_tools, detect_test_commands
from cqf.installer import install_missing_tools
from cqf.parsers import (
    parse_golangci, parse_gosec, parse_ruff, parse_bandit,
    parse_spotbugs, parse_pmd, parse_checkstyle, parse_semgrep,
)
from cqf.report import assign_ids, filter_issues, build_report, write_report
from cqf.backup import backup_files, restore_backup

CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "configs")

# 永不扫描的目录：VCS、依赖、构建产物、本 skill 自己的暂存目录。
# bandit 不读 .gitignore，必须显式排除；ruff/semgrep 虽读 .gitignore，
# 这里也显式传一遍，确保即使用户漏做 SKILL.md 的 gitignore 步骤也不会
# 扫到噪声（且能避免反复备份导致的扫描膨胀）。
EXCLUDED_DIRS = (".git", "node_modules", "vendor", ".tmp", "target")


def _repeated_excludes(flag):
    """ruff --extend-exclude / semgrep --exclude：每个目录重复一次 flag。"""
    return [tok for d in EXCLUDED_DIRS for tok in (flag, d)]


def _bandit_exclude_arg():
    """bandit -x 用 glob，逗号分隔；*/<dir>/* 匹配任意层级的该目录。"""
    return ["-x", ",".join(f"*/{d}/*" for d in EXCLUDED_DIRS)]


def _config(name, project_root):
    """项目根有同名配置则用它，否则用内置默认。"""
    local = os.path.join(project_root, name)
    return local if os.path.isfile(local) else os.path.join(CONFIG_DIR, name)


def _run(cmd, cwd, timeout=300):
    """运行扫描器，返回 (stdout文本, 是否成功)。绝不抛异常。"""
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return proc.stdout, proc.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        sys.stderr.write(f"[warn] {cmd[0]} failed: {e}\n")
        return "", False


def run_go_scanners(project_root):
    issues = []
    root = project_root
    gocfg = _config(".golangci.yml", project_root)
    out, _ = _run(["golangci-lint", "run", "--config", gocfg,
                   "--out-format=json", "--issues-exit-code=0", "./..."], root)
    if out:
        try:
            issues += parse_golangci(json.loads(out), project_root)
        except json.JSONDecodeError:
            sys.stderr.write("[warn] golangci-lint produced non-JSON output\n")
    out, _ = _run(["gosec", "-fmt=json", "-quiet", "./..."], root)
    if out:
        try:
            issues += parse_gosec(json.loads(out), project_root)
        except json.JSONDecodeError:
            sys.stderr.write("[warn] gosec produced non-JSON output\n")
    return issues


def run_python_scanners(project_root):
    issues = []
    rcfg = _config("ruff.toml", project_root)
    out, _ = _run(["ruff", "check", "--config", rcfg,
                   *_repeated_excludes("--extend-exclude"),
                   "--output-format=json", "--exit-zero", "."], project_root)
    if out:
        try:
            issues += parse_ruff(json.loads(out), project_root)
        except json.JSONDecodeError:
            sys.stderr.write("[warn] ruff produced non-JSON output\n")
    out, _ = _run(["bandit", "-r", ".", "-f", "json", "-q",
                   *_bandit_exclude_arg()], project_root)
    if out:
        try:
            issues += parse_bandit(json.loads(out), project_root)
        except json.JSONDecodeError:
            sys.stderr.write("[warn] bandit produced non-JSON output\n")
    return issues


def run_java_scanners(project_root):
    """通过 Maven 插件运行 spotbugs/pmd/checkstyle，解析其 XML。"""
    issues = []
    cs_cfg = _config("checkstyle.xml", project_root)
    pmd_cfg = _config("pmd-rules.xml", project_root)
    # goal 拆成 argv 元素 —— subprocess 不经 shell，单字符串会被 Maven 当成单个 goal。
    targets = {
        "spotbugs": (["spotbugs:check"], "target/spotbugsXml.xml", parse_spotbugs),
        "pmd": (["pmd:check", f"-Druleset={pmd_cfg}", "-Dformat=xml"],
                "target/pmd.xml", parse_pmd),
        "checkstyle": (["checkstyle:check", f"-Dconfig.location={cs_cfg}"],
                       "target/checkstyle-result.xml", parse_checkstyle),
    }
    for _name, (goal_args, artifact, parser) in targets.items():
        _run(["mvn", *goal_args, "-q", "-DskipTests"], project_root, timeout=600)
        path = os.path.join(project_root, artifact)
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                issues += parser(f.read(), project_root)
    return issues


def run_semgrep(project_root, languages):
    issues = []
    out, _ = _run(["semgrep", "scan", "--config", "p/owasp-top-ten",
                   *_repeated_excludes("--exclude"),
                   "--json", "--quiet", project_root], project_root, timeout=600)
    if out:
        try:
            hint = languages[0] if len(languages) == 1 else None
            issues += parse_semgrep(json.loads(out), project_root, language_hint=hint)
        except json.JSONDecodeError:
            sys.stderr.write("[warn] semgrep produced non-JSON output\n")
    return issues


def scan_project(project_root, output, lang=None, category=None, severity=None):
    languages = [lang] if lang else detect_languages(project_root)
    if not languages:
        sys.stderr.write(f"[warn] no supported languages detected under {project_root}\n")

    issues = []
    if "go" in languages:
        issues += run_go_scanners(project_root)
    if "java" in languages:
        issues += run_java_scanners(project_root)
    if "python" in languages:
        issues += run_python_scanners(project_root)
    issues += run_semgrep(project_root, languages)

    issues = filter_issues(issues, category=category, min_severity=severity)
    assign_ids(issues)
    report = build_report(issues, project_root, scan_time=_utc_now_iso())
    write_report(report, output)
    print(f"[ok] scanned {len(issues)} issues -> {output}")
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description="code-quality-fix scanner")
    p.add_argument("--project", help="project root to scan")
    p.add_argument("--output", help="path to write report.json")
    p.add_argument("--lang", choices=["go", "java", "python"])
    p.add_argument("--category", choices=["security", "quality", "style"])
    p.add_argument("--severity", choices=["HIGH", "MEDIUM", "LOW"])
    p.add_argument("--check-tools", action="store_true")
    p.add_argument("--install-tools", action="store_true")
    p.add_argument("--detect-tests", action="store_true")
    p.add_argument("--backup", help="path to report.json; backs up referenced files")
    p.add_argument("--backup-root", help="directory to store snapshots under")
    p.add_argument("--backup-id", help="timestamp id for the snapshot")
    p.add_argument("--restore", action="store_true")
    args = p.parse_args(argv)

    if args.check_tools:
        print(json.dumps(detect_tools(), indent=2, ensure_ascii=False))
        return 0

    if args.install_tools:
        results = install_missing_tools(detect_tools())
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 0

    if args.detect_tests:
        if not args.project:
            sys.exit("--detect-tests requires --project")
        print(json.dumps(detect_test_commands(args.project), indent=2, ensure_ascii=False))
        return 0

    if args.backup:
        if not (args.backup_root and args.backup_id):
            sys.exit("--backup requires --backup-root and --backup-id")
        with open(args.backup) as f:
            report = json.load(f)
        files = sorted({os.path.join(args.project or ".", i["file"]) for i in report["issues"]})
        bid = backup_files(files, args.backup_root, args.backup_id, project_root=args.project)
        print(f"[ok] backed up {len(files)} files -> {args.backup_root}/{bid}")
        return 0

    if args.restore:
        if not (args.backup_root and args.backup_id):
            sys.exit("--restore requires --backup-root and --backup-id")
        restore_backup(args.backup_root, args.backup_id, project_root=args.project)
        print(f"[ok] restored from {args.backup_root}/{args.backup_id}")
        return 0

    if args.project and args.output:
        scan_project(args.project, args.output, lang=args.lang,
                     category=args.category, severity=args.severity)
        return 0

    p.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
