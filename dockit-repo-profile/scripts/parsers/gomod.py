#!/usr/bin/env python3
# =============================================================================
# parsers/gomod.py — Go Modules 构建系统解析器（静态 + 动态）
# =============================================================================
# 静态：解析 go.mod 的 require / replace 指令
# 动态：go mod graph → 传递依赖 + 精确版本
# 降级：go 命令不存在或 go mod graph 失败时，保留静态解析结果
# =============================================================================

from __future__ import annotations

import os
import re
from typing import Optional

from .base import (
    BaseParser,
    DependencyScope,
    ExternalDependency,
    InternalDependency,
    ModuleDependencies,
    AnalysisSource,
)


class GomodParser(BaseParser):
    """Go Modules 构建系统解析器."""

    BUILD_SYSTEM = "gomod"

    @staticmethod
    def detect(build_file_path: str) -> bool:
        """检测 go.mod 文件."""
        return os.path.basename(build_file_path) == "go.mod"

    # -------------------------------------------------------------------
    # 静态解析
    # -------------------------------------------------------------------

    def parse_static(self, build_file_path: str) -> ModuleDependencies:
        """静态解析 go.mod."""
        build_file_abs = (
            build_file_path
            if os.path.isabs(build_file_path)
            else os.path.join(self.repo_root, build_file_path)
        )

        content = self._read_file(build_file_abs)
        if content is None:
            return self._make_result(build_file_abs)

        module_path = os.path.dirname(
            os.path.relpath(build_file_abs, self.repo_root)
        )

        # 提取 module 名称
        module_name = self._extract_module_name(content)
        name = module_name or module_path

        # 提取 require
        requires = self._extract_requires(content)

        # 提取 replace（用于识别内部依赖）
        replaces = self._extract_replaces(content)

        # 分类：内部 vs 外部
        internal_deps, external_deps = self._categorize(
            requires, replaces, module_name
        )

        return ModuleDependencies(
            path=module_path,
            name=name,
            build_system=self.BUILD_SYSTEM,
            build_file=os.path.relpath(build_file_abs, self.repo_root),
            internal_deps=internal_deps,
            external_deps=external_deps,
        )

    # -------------------------------------------------------------------
    # 动态增强
    # -------------------------------------------------------------------

    def enhance_dynamic(
        self, result: ModuleDependencies
    ) -> ModuleDependencies:
        """运行 go mod graph 增强依赖信息."""
        build_file_abs = os.path.join(self.repo_root, result.build_file)
        module_dir = os.path.dirname(build_file_abs)

        success, stdout, stderr = self._run_cmd(
            ["go", "mod", "graph"], timeout=60, cwd=module_dir
        )

        if not success:
            result.degraded = True
            result.degraded_reason = f"go mod graph failed: {stderr.strip()}"
            for dep in result.external_deps:
                dep.degraded = True
                dep.degraded_reason = result.degraded_reason
            return result

        # 解析 go mod graph 输出
        graph_deps = self._parse_graph(stdout)

        # 用 graph 结果增强外部依赖
        self._apply_graph_results(result, graph_deps)

        result.analysis_source = AnalysisSource.DYNAMIC
        return result

    # -------------------------------------------------------------------
    # 扫描
    # -------------------------------------------------------------------

    def scan_all_modules(self) -> list[str]:
        """扫描全仓 go.mod 文件."""
        gomod_files = []
        for root, dirs, files in os.walk(self.repo_root):
            dirs[:] = [
                d for d in dirs
                if d not in {
                    ".git", "vendor", "node_modules",
                } and not d.startswith(".")
            ]
            for fname in files:
                if fname == "go.mod":
                    gomod_files.append(os.path.join(root, fname))
        return gomod_files

    # -------------------------------------------------------------------
    # 内部方法
    # -------------------------------------------------------------------

    def _read_file(self, path: str) -> Optional[str]:
        try:
            with open(path, "r", errors="ignore") as f:
                return f.read()
        except Exception:
            return None

    def _extract_module_name(self, content: str) -> Optional[str]:
        """提取 module 指令."""
        m = re.search(r"module\s+(\S+)", content)
        return m.group(1) if m else None

    @staticmethod
    def _parse_block(content: str, directive: str) -> list[str]:
        """解析 go.mod 中的块或单行指令.

        支持两种格式：
            单行: require module/path v1.2.3
            块:   require (
                      module/a v1.2.3
                      module/b v0.1.0
                  )
        """
        entries = []

        # 尝试块格式
        block_pattern = rf"{directive}\s*\(([^)]+)\)"
        for match in re.finditer(block_pattern, content, re.MULTILINE | re.DOTALL):
            for line in match.group(1).strip().split("\n"):
                line = line.strip()
                # 跳过注释
                if line.startswith("//") or line.startswith("#"):
                    continue
                if line:
                    entries.append(line)

        # 单行格式
        line_pattern = rf"^{directive}\s+(.+)$"
        for match in re.finditer(line_pattern, content, re.MULTILINE):
            entries.append(match.group(1).strip())

        return entries

    def _extract_requires(self, content: str) -> dict[str, str]:
        """提取 require 指令 → {module_path: version}."""
        requires = {}
        for entry in self._parse_block(content, "require"):
            parts = entry.split()
            if len(parts) >= 2:
                # 跳过 // indirect 标记
                module = parts[0]
                version = parts[1]
                requires[module] = version
        return requires

    def _extract_replaces(self, content: str) -> dict[str, str]:
        """提取 replace 指令 → {old: new}.

        关注指向本地路径的 replace，这些表示内部依赖.
        """
        replaces = {}
        for entry in self._parse_block(content, "replace"):
            parts = entry.split("=>")
            if len(parts) == 2:
                old = parts[0].strip().split()[0]
                new = parts[1].strip().split()[0] if parts[1].strip() else ""
                replaces[old] = new
        return replaces

    def _categorize(
        self,
        requires: dict[str, str],
        replaces: dict[str, str],
        module_name: Optional[str],
    ) -> tuple[list[InternalDependency], list[ExternalDependency]]:
        """将依赖分类为内部/外部.

        内部依赖判定:
        - replace 目标为本地路径 (./ 或 ../)
        - replace 目标或模块路径匹配本仓库内的 go.mod 模块
        """
        internal_deps = []
        external_deps = []

        # 收集本仓库内的模块路径（用于匹配）
        local_modules = set()
        for gomod_file in self.scan_all_modules():
            rel = os.path.dirname(os.path.relpath(gomod_file, self.repo_root))
            local_modules.add(rel)
            # 也从 go.mod 中提取模块名
            content = self._read_file(gomod_file)
            if content:
                name = self._extract_module_name(content)
                if name:
                    local_modules.add(name)

        for mod_path, version in requires.items():
            scope = DependencyScope.COMPILE

            # 检查是否有 replace 指向本地
            is_local = False
            target_path = None
            if mod_path in replaces:
                replacement = replaces[mod_path]
                if replacement.startswith("./") or replacement.startswith("../"):
                    is_local = True
                    # 计算相对路径
                    target_path = os.path.normpath(replacement)
                elif replacement in local_modules:
                    is_local = True
                    target_path = replacement

            # 检查模块路径是否匹配本地模块
            for local in local_modules:
                if local in mod_path or mod_path in local:
                    is_local = True
                    target_path = local
                    break

            if is_local:
                internal_deps.append(InternalDependency(
                    target=target_path or mod_path,
                    scope=scope,
                    artifact=mod_path,
                ))
            else:
                external_deps.append(ExternalDependency(
                    name=mod_path,
                    version=version,  # go.mod 中静态就有版本
                ))

        return internal_deps, external_deps

    def _parse_graph(self, output: str) -> dict[str, list[tuple[str, str]]]:
        """解析 go mod graph 输出.

        格式（每行）: <source>@<version> <target>@<version>

        Returns: {source_module: [(target_module, version), ...]}
        """
        graph: dict[str, list[tuple[str, str]]] = {}
        for line in output.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 2:
                continue

            source = parts[0]
            target_ver = parts[1]

            # 拆分 target@version
            if "@" in target_ver:
                idx = target_ver.rindex("@")
                target = target_ver[:idx]
                version = target_ver[idx + 1:]
            else:
                target = target_ver
                version = ""

            if source not in graph:
                graph[source] = []
            graph[source].append((target, version))

        return graph

    def _apply_graph_results(
        self,
        result: ModuleDependencies,
        graph: dict[str, list[tuple[str, str]]],
    ) -> None:
        """用 go mod graph 结果增强外部依赖信息."""
        module_name = result.name

        # 在 graph 中找到本模块的条目
        graph_key = None
        for key in graph:
            if key.startswith(module_name):
                graph_key = key
                break

        if graph_key is None:
            return

        graph_deps = graph.get(graph_key, [])

        # 为每个外部依赖补充版本号和传递依赖
        for ext_dep in result.external_deps:
            # 精确版本
            for dep_target, dep_version in graph_deps:
                if dep_target == ext_dep.name:
                    ext_dep.version = dep_version
                    break

            # 传递依赖
            transitive = []
            for dep_target, dep_version in graph_deps:
                if dep_target == ext_dep.name:
                    sub_deps = graph.get(f"{dep_target}@{dep_version}", [])
                    for t_name, t_ver in sub_deps:
                        transitive.append(f"{t_name}@{t_ver}")
            ext_dep.transitive = transitive
