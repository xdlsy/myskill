#!/usr/bin/env python3
# =============================================================================
# collect-dependencies.py — 模块依赖关系采集（核心引擎）
# =============================================================================
# 两遍扫描：
#   Pass 1（静态）: 纯文件解析 → 内部依赖 + 外部依赖名称
#   Pass 2（动态）: 运行构建工具 → 版本号 + 传递依赖
# 降级：按模块降级，动态增强失败时保留静态结果
#
# 用法：
#   python3 collect-dependencies.py --format json --dir <repo_root>
#   python3 collect-dependencies.py --format text --dir <repo_root> --no-dynamic
# =============================================================================

import argparse
import json
import os
import sys

from parsers import (
    PARSER_REGISTRY,
    DependencyGraphBuilder,
    AnalysisSource,
    detect_parser,
)


def discover_modules(repo_root: str) -> list[str]:
    """扫描仓库发现所有构建文件."""
    all_build_files = []
    for parser_cls in PARSER_REGISTRY:
        parser = parser_cls(repo_root)
        # 每个 parser 有 scan_all_modules 方法
        for bf in parser.scan_all_modules():
            all_build_files.append(bf)
    # 去重（同一文件可能被多个 parser 检测到）
    return sorted(set(all_build_files))


def run_pass1(
    repo_root: str, build_files: list[str]
) -> dict[str, "ModuleDependencies"]:
    """Pass 1: 静态解析所有模块."""
    from parsers import ModuleDependencies

    results: dict[str, ModuleDependencies] = {}

    for bf in build_files:
        parser_cls = detect_parser(bf)
        if parser_cls is None:
            continue

        parser = parser_cls(repo_root)
        try:
            result = parser.parse_static(bf)
            key = result.path or os.path.dirname(
                os.path.relpath(bf, repo_root)
            )
            if key not in results:
                results[key] = result
        except Exception as exc:
            # 解析失败不阻塞整体流程
            bf_rel = os.path.relpath(bf, repo_root)
            print(
                f"[warn] 静态解析失败: {bf_rel} ({exc})",
                file=sys.stderr,
            )

    return results


def run_pass2(
    repo_root: str,
    static_results: dict[str, "ModuleDependencies"],
    enable_dynamic: bool = True,
) -> dict[str, "ModuleDependencies"]:
    """Pass 2: 动态增强（best-effort）."""
    if not enable_dynamic:
        return static_results

    from parsers import ModuleDependencies

    enhanced: dict[str, ModuleDependencies] = {}

    for path, result in static_results.items():
        build_file_abs = os.path.join(repo_root, result.build_file)
        parser_cls = detect_parser(build_file_abs)
        if parser_cls is None:
            enhanced[path] = result
            continue

        parser = parser_cls(repo_root)
        try:
            enhanced_result = parser.enhance_dynamic(result)
            enhanced[path] = enhanced_result
        except Exception as exc:
            result.degraded = True
            result.degraded_reason = str(exc)
            enhanced[path] = result

    return enhanced


def build_output(
    repo_root: str,
    modules: dict[str, "ModuleDependencies"],
) -> dict:
    """构建最终 JSON 输出."""
    builder = DependencyGraphBuilder(repo_root)
    for result in modules.values():
        builder.add_module(result)

    graph = builder.build_graph()
    topo_order = builder.compute_topological_order()
    entry_points = builder.find_entry_points()
    circular = builder.detect_circular_dependencies()

    # 分析摘要
    dynamic_count = sum(
        1 for m in modules.values()
        if m.analysis_source == AnalysisSource.DYNAMIC
    )
    degraded_count = sum(1 for m in modules.values() if m.degraded)
    internal_edges = len(graph.edges)
    external_count = sum(
        len(m.external_deps) for m in modules.values()
    )

    degraded_reasons = {}
    for m in modules.values():
        if m.degraded and m.degraded_reason:
            degraded_reasons[m.path] = m.degraded_reason

    # 外部依赖索引
    ext_index = {}
    for m in modules.values():
        for dep in m.external_deps:
            if dep.name not in ext_index:
                ext_index[dep.name] = {"versions": {}, "conflicts": None}
            version_key = dep.version or "unknown"
            ext_index[dep.name]["versions"].setdefault(version_key, [])
            ext_index[dep.name]["versions"][version_key].append(m.path)

    # 检测版本冲突
    for dep_name, info in ext_index.items():
        versions = list(info["versions"].keys())
        if len(versions) > 1:
            info["conflicts"] = versions

    # 模块列表
    module_list = []
    for path, m in sorted(modules.items()):
        module_list.append({
            "path": m.path,
            "name": m.name,
            "build_system": m.build_system,
            "build_file": m.build_file,
            "type": "unknown",
            "analysis_source": m.analysis_source.value,
            "degraded": m.degraded,
            "degraded_reason": m.degraded_reason,
            "internal_dependencies": [
                {
                    "target": d.target,
                    "scope": d.scope.value,
                    "artifact": d.artifact,
                }
                for d in m.internal_deps
            ],
            "external_dependencies": [
                {
                    "name": d.name,
                    "version": d.version,
                    "scope": d.scope.value,
                    "transitive": d.transitive,
                    "degraded": d.degraded,
                    "degraded_reason": d.degraded_reason,
                }
                for d in m.external_deps
            ],
        })

    return {
        "tool": "collect-dependencies",
        "repository_root": repo_root,
        "analysis_summary": {
            "total_modules": len(modules),
            "internal_edges": internal_edges,
            "external_deps_count": external_count,
            "dynamic_modules": dynamic_count,
            "degraded_modules": degraded_count,
            "degraded_reasons": degraded_reasons,
            "circular_dependencies": circular,
            "entry_points": entry_points,
            "topological_order": topo_order,
        },
        "modules": module_list,
        "dependency_graph": {
            "nodes": graph.nodes,
            "edges": graph.edges,
        },
        "external_deps_index": ext_index,
    }


def output_json(data: dict) -> None:
    """JSON 输出."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def output_text(data: dict) -> None:
    """人类可读文本输出."""
    summary = data["analysis_summary"]
    print("🔗 模块依赖关系")
    print(f"   仓库: {data['repository_root']}")
    print(f"   模块数: {summary['total_modules']}")
    print(f"   内部依赖边: {summary['internal_edges']}")
    print(f"   外部依赖数: {summary['external_deps_count']}")
    print(f"   动态分析: {summary['dynamic_modules']} 个模块")
    if summary["degraded_modules"] > 0:
        print(f"   ⚠️  降级: {summary['degraded_modules']} 个模块")
        for path, reason in summary.get("degraded_reasons", {}).items():
            print(f"      - {path}: {reason}")
    print()

    if summary.get("circular_dependencies"):
        print("   ⚠️  发现循环依赖:")
        for cycle in summary["circular_dependencies"]:
            print(f"      {' → '.join(cycle)}")
        print()

    print(f"   拓扑排序: {' → '.join(summary.get('topological_order', []))}")
    print(f"   入口点: {', '.join(summary.get('entry_points', []))}")
    print()

    # 内部依赖图
    if data["dependency_graph"]["edges"]:
        print("📊 内部依赖图:")
        for edge in data["dependency_graph"]["edges"]:
            print(f"   {edge['from']} ──→ {edge['to']}  ({edge['scope']})")
        print()

    # 外部依赖摘要
    ext_index = data.get("external_deps_index", {})
    if ext_index:
        print("📦 外部依赖 (Top 10):")
        # 按引用模块数排序
        sorted_ext = sorted(
            ext_index.items(),
            key=lambda x: sum(len(v) for v in x[1]["versions"].values()),
            reverse=True,
        )
        for name, info in sorted_ext[:10]:
            consumers = sum(len(v) for v in info["versions"].values())
            conflict = " ⚠️ 版本冲突!" if info.get("conflicts") else ""
            print(f"   {name} — {consumers} 个模块引用{conflict}")
        if len(sorted_ext) > 10:
            print(f"   ... 共 {len(sorted_ext)} 个外部依赖")
        print()

    # 模块详情
    for mod in data["modules"]:
        source_icon = "🔧" if mod["analysis_source"] == "dynamic" else "📄"
        degraded_mark = " ⚠️ 降级" if mod.get("degraded") else ""
        print(f"   {source_icon} {mod['path']} ({mod.get('build_system', '?')}){degraded_mark}")
        if mod.get("internal_dependencies"):
            for d in mod["internal_dependencies"]:
                print(f"      ↳ {d['target']} [{d['scope']}]")
        if mod.get("external_dependencies"):
            ext_count = len(mod["external_dependencies"])
            degraded_ext = sum(
                1 for d in mod["external_dependencies"] if d.get("degraded")
            )
            dmsg = f" ({degraded_ext} 降级)" if degraded_ext else ""
            print(f"      + {ext_count} 个外部依赖{dmsg}")


def main():
    parser = argparse.ArgumentParser(
        description="模块依赖关系采集（两遍扫描）"
    )
    parser.add_argument(
        "--format", choices=["json", "text"], default="json",
        help="输出格式（默认 json）"
    )
    parser.add_argument(
        "--dir", default=".",
        help="目标仓库根目录（默认当前目录）"
    )
    parser.add_argument(
        "--no-dynamic", action="store_true",
        help="禁用动态增强（仅静态解析）"
    )
    args = parser.parse_args()

    repo_root = os.path.abspath(args.dir)
    if not os.path.isdir(repo_root):
        print(f"错误: 目录不存在: {repo_root}", file=sys.stderr)
        sys.exit(1)

    # Pass 1：发现模块 + 静态解析
    build_files = discover_modules(repo_root)
    empty_result = {
        "tool": "collect-dependencies",
        "repository_root": repo_root,
        "analysis_summary": {
            "total_modules": 0,
            "internal_edges": 0,
            "external_deps_count": 0,
            "dynamic_modules": 0,
            "degraded_modules": 0,
            "degraded_reasons": {},
            "circular_dependencies": None,
            "entry_points": [],
            "topological_order": [],
        },
        "modules": [],
        "dependency_graph": {"nodes": [], "edges": []},
        "external_deps_index": {},
    }

    if not build_files:
        if args.format == "text":
            print("未检测到任何支持的构建文件。")
        else:
            output_json(empty_result)
        return

    static_results = run_pass1(repo_root, build_files)

    # Pass 2：动态增强
    enhanced_results = run_pass2(
        repo_root, static_results,
        enable_dynamic=not args.no_dynamic,
    )

    # 构建输出
    output_data = build_output(repo_root, enhanced_results)

    if args.format == "text":
        output_text(output_data)
    else:
        output_json(output_data)


if __name__ == "__main__":
    main()
