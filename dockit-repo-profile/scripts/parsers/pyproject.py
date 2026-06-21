#!/usr/bin/env python3
# =============================================================================
# parsers/pyproject.py — Python (pyproject.toml) 解析器（静态 + 动态）
# =============================================================================
# 静态：解析 pyproject.toml 的 [project].dependencies / optional-dependencies
#       + [tool.uv.sources] / [tool.poetry.dependencies]
# 动态：pipdeptree --json → 安装后精确版本 + 传递依赖
# 降级：无虚拟环境或 pipdeptree 不可用时保留静态解析结果
# =============================================================================

from __future__ import annotations

import json as json_mod
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


class PyprojectParser(BaseParser):
    """Python pyproject.toml 解析器."""

    BUILD_SYSTEM = "pyproject"

    @staticmethod
    def detect(build_file_path: str) -> bool:
        return os.path.basename(build_file_path) == "pyproject.toml"

    # -------------------------------------------------------------------
    # 静态解析
    # -------------------------------------------------------------------

    def parse_static(self, build_file_path: str) -> ModuleDependencies:
        build_file_abs = (
            build_file_path
            if os.path.isabs(build_file_path)
            else os.path.join(self.repo_root, build_file_path)
        )

        data = self._read_toml(build_file_abs)
        if data is None:
            return self._make_result(build_file_abs)

        module_path = os.path.dirname(
            os.path.relpath(build_file_abs, self.repo_root)
        )

        # 提取项目名
        project = data.get("project", {})
        name = project.get("name", module_path)

        # 提取依赖
        internal_deps, external_deps = self._extract_deps(data, module_path)

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
        """运行 pipdeptree 获取精确版本 + 传递依赖."""
        success, stdout, stderr = self._run_cmd(
            ["pipdeptree", "--json"], timeout=60
        )
        if not success:
            # 尝试 python -m pipdeptree
            success, stdout, stderr = self._run_cmd(
                ["python", "-m", "pipdeptree", "--json"], timeout=60
            )

        if not success:
            result.degraded = True
            result.degraded_reason = (
                f"pipdeptree not available: {stderr.strip()}"
            )
            for dep in result.external_deps:
                dep.degraded = True
                dep.degraded_reason = result.degraded_reason
            return result

        # 解析 pipdeptree JSON
        try:
            tree = json_mod.loads(stdout)
        except json_mod.JSONDecodeError:
            result.degraded = True
            result.degraded_reason = "pipdeptree output parse error"
            return result

        self._apply_tree_results(result, tree)
        result.analysis_source = AnalysisSource.DYNAMIC
        return result

    # -------------------------------------------------------------------
    # 扫描
    # -------------------------------------------------------------------

    def scan_all_modules(self) -> list[str]:
        pyproject_files = []
        for root, dirs, files in os.walk(self.repo_root):
            dirs[:] = [
                d for d in dirs
                if d not in {
                    ".git", "__pycache__", ".venv", "venv", ".tox",
                    ".mypy_cache", ".pytest_cache", ".egg-info",
                    "node_modules", "dist", "build",
                } and not d.startswith(".")
            ]
            for fname in files:
                if fname == "pyproject.toml":
                    pyproject_files.append(os.path.join(root, fname))
        return pyproject_files

    # -------------------------------------------------------------------
    # 内部方法
    # -------------------------------------------------------------------

    def _read_toml(self, path: str) -> Optional[dict]:
        """读取 TOML 文件（兼容 Python 3.10-）."""
        try:
            with open(path, "r", errors="ignore") as f:
                content = f.read()
        except Exception:
            return None

        # 尝试使用标准库 tomllib (3.11+)
        try:
            import tomllib
            return tomllib.loads(content)
        except ImportError:
            pass

        # 尝试使用 tomli (第三方)
        try:
            import tomli
            return tomli.loads(content)
        except ImportError:
            pass

        # 回退：简单的 TOML 解析（只提取我们需要的 sections）
        return self._simple_toml_parse(content)

    def _simple_toml_parse(self, content: str) -> dict:
        """简化版 TOML 解析器，只提取 project/uv/poetry sections."""
        result = {}
        current_section: Optional[str] = None
        current_table: dict = {}

        for line in content.split("\n"):
            line = line.strip()

            # 跳过空行和注释
            if not line or line.startswith("#"):
                continue

            # Section header
            section_match = re.match(r"\[([^\]]+)\]", line)
            if section_match:
                if current_section and current_table:
                    self._set_nested(result, current_section, current_table)
                current_section = section_match.group(1)
                current_table = {}
                continue

            # Key-value pair
            if current_section:
                kv_match = re.match(r'(\S+)\s*=\s*(.+)', line)
                if kv_match:
                    key = kv_match.group(1)
                    raw_value = kv_match.group(2).strip()

                    # 字符串值
                    if raw_value.startswith('"') or raw_value.startswith("'"):
                        value = raw_value[1:-1] if len(raw_value) > 1 else ""
                        current_table[key] = value
                    # 数组值
                    elif raw_value.startswith("["):
                        current_table[key] = self._parse_toml_array(raw_value)
                    # 内联表
                    elif raw_value.startswith("{"):
                        current_table[key] = self._parse_toml_inline_table(raw_value)
                    else:
                        current_table[key] = raw_value

        # 保存最后一个 section
        if current_section and current_table:
            self._set_nested(result, current_section, current_table)

        return result

    def _set_nested(self, d: dict, key_path: str, value):
        """将点分隔的 key_path 设置到嵌套字典中."""
        keys = key_path.split(".")
        for key in keys[:-1]:
            if key not in d:
                d[key] = {}
            d = d[key]
        d[keys[-1]] = value

    def _parse_toml_array(self, raw: str) -> list:
        """解析 TOML 数组（格式: ["a", "b"]）."""
        items = []
        raw = raw.strip("[]")
        # 简单按逗号分割（不处理嵌套）
        for item in raw.split(","):
            item = item.strip().strip('"').strip("'")
            if item:
                items.append(item)
        return items

    def _parse_toml_inline_table(self, raw: str) -> dict:
        """解析 TOML 内联表（格式: {key = "value"}）."""
        result = {}
        raw = raw.strip("{}")
        # 简单按逗号分割
        for item in raw.split(","):
            item = item.strip()
            if "=" in item:
                k, v = item.split("=", 1)
                result[k.strip()] = v.strip().strip('"').strip("'")
        return result

    def _extract_deps(
        self, data: dict, module_path: str
    ) -> tuple[list[InternalDependency], list[ExternalDependency]]:
        """从 pyproject.toml 数据提取依赖."""
        internal_deps = []
        external_deps = []

        project = data.get("project", {})

        # [project].dependencies
        for dep_str in project.get("dependencies", []):
            self._process_dep(dep_str, DependencyScope.COMPILE,
                              module_path, internal_deps, external_deps)

        # [project].optional-dependencies
        for group, deps in project.get("optional-dependencies", {}).items():
            scope = self._group_to_scope(group)
            for dep_str in deps:
                self._process_dep(dep_str, scope,
                                  module_path, internal_deps, external_deps)

        # [tool.uv.sources] — 检查本地路径引用
        uv_sources = data.get("tool", {}).get("uv", {}).get("sources", {})
        for dep_name, source in uv_sources.items():
            if isinstance(source, dict):
                path = source.get("path", "")
                if path and (path.startswith("./") or path.startswith("../")):
                    # 这是一个内部依赖（已在 _process_dep 中处理）
                    pass

        # [tool.poetry.dependencies]
        poetry_deps = (
            data.get("tool", {}).get("poetry", {}).get("dependencies", {})
        )
        for dep_name, constraint in poetry_deps.items():
            if dep_name.lower() == "python":
                continue
            scope = DependencyScope.COMPILE
            if isinstance(constraint, dict):
                path = constraint.get("path", "")
                if path and (path.startswith("./") or path.startswith("../")):
                    internal_deps.append(InternalDependency(
                        target=os.path.normpath(
                            os.path.join(module_path, path)
                        ),
                        scope=scope,
                        artifact=dep_name,
                    ))
                    continue
                version = constraint.get("version", str(constraint))
            else:
                version = str(constraint)

            external_deps.append(ExternalDependency(
                name=dep_name, version=version, scope=scope,
            ))

        # [tool.poetry.group.*.dependencies]
        poetry_groups = (
            data.get("tool", {}).get("poetry", {}).get("group", {})
        )
        for group, group_data in poetry_groups.items():
            scope = self._group_to_scope(group)
            for dep_name, constraint in group_data.get("dependencies", {}).items():
                version = str(constraint) if not isinstance(constraint, dict) \
                    else constraint.get("version", str(constraint))
                external_deps.append(ExternalDependency(
                    name=dep_name, version=version, scope=scope,
                ))

        return internal_deps, external_deps

    def _process_dep(
        self,
        dep_str: str,
        scope: DependencyScope,
        module_path: str,
        internal_deps: list[InternalDependency],
        external_deps: list[ExternalDependency],
    ) -> None:
        """处理单个 PEP 508 依赖字符串."""
        # 提取包名（去除版本约束和 extras）
        name_match = re.match(r"([a-zA-Z0-9_.-]+)", dep_str)
        if not name_match:
            return
        dep_name = name_match.group(1)

        # 提取版本约束
        version = None
        ver_match = re.search(r"[><=!~^]+[^;,\s]+", dep_str)
        if ver_match:
            version = ver_match.group(0).strip()

        # 检测本地路径引用
        # 格式: "mylib @ file:///path/to/lib" 或 "mylib @ ../libs/mylib"
        if "file://" in dep_str or "@" in dep_str:
            local_match = re.search(
                r'@\s*(?:file://\S*/)?(\S+)', dep_str
            )
            if local_match:
                local_path = local_match.group(1)
                if local_path.startswith("."):
                    internal_deps.append(InternalDependency(
                        target=os.path.normpath(
                            os.path.join(module_path, local_path)
                        ),
                        scope=scope,
                        artifact=dep_name,
                    ))
                    return

        # 外部依赖
        external_deps.append(ExternalDependency(
            name=dep_name, version=version, scope=scope,
        ))

    def _group_to_scope(self, group: str) -> DependencyScope:
        """将 optional-dependencies 组名映射为 DependencyScope."""
        group_lower = group.lower()
        if group_lower in {"test", "tests", "testing"}:
            return DependencyScope.TEST
        if group_lower in {"dev", "develop", "development"}:
            return DependencyScope.DEV
        if group_lower in {"docs", "doc"}:
            return DependencyScope.DEV
        return DependencyScope.COMPILE

    def _apply_tree_results(
        self, result: ModuleDependencies, tree: list[dict]
    ) -> None:
        """用 pipdeptree 结果增强外部依赖."""
        # 构建 name → entry 映射
        tree_map = {}
        for entry in tree:
            pkg_name = entry.get("package", {}).get("package_name", "")
            if pkg_name:
                tree_map[pkg_name.lower()] = entry

        for ext_dep in result.external_deps:
            entry = tree_map.get(ext_dep.name.lower())
            if entry:
                pkg = entry.get("package", {})
                ext_dep.version = pkg.get("installed_version",
                                          ext_dep.version)
                ext_dep.transitive = [
                    d.get("package_name", "")
                    for d in entry.get("dependencies", [])
                ]
