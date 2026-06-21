#!/usr/bin/env python3
# =============================================================================
# parsers/maven.py — Maven (pom.xml) 解析器（静态 + 动态）
# =============================================================================
# 静态：解析 pom.xml 的 <dependencies>、<parent>、<modules>
# 动态：mvn dependency:tree -DoutputType=json → 精确版本 + 传递依赖 + 冲突
# 降级：mvn 不存在或执行失败时保留静态解析结果
# =============================================================================

from __future__ import annotations

import json as json_mod
import os
import xml.etree.ElementTree as ET
from typing import Optional

from .base import (
    BaseParser,
    DependencyScope,
    ExternalDependency,
    InternalDependency,
    ModuleDependencies,
    AnalysisSource,
)


class MavenParser(BaseParser):
    """Maven (pom.xml) 解析器."""

    BUILD_SYSTEM = "maven"

    # Maven scope 映射
    SCOPE_MAP = {
        "compile": DependencyScope.COMPILE,
        "runtime": DependencyScope.RUNTIME,
        "test": DependencyScope.TEST,
        "provided": DependencyScope.PROVIDED,
    }

    @staticmethod
    def detect(build_file_path: str) -> bool:
        return os.path.basename(build_file_path) == "pom.xml"

    # -------------------------------------------------------------------
    # 静态解析
    # -------------------------------------------------------------------

    def parse_static(self, build_file_path: str) -> ModuleDependencies:
        build_file_abs = (
            build_file_path
            if os.path.isabs(build_file_path)
            else os.path.join(self.repo_root, build_file_path)
        )

        root = self._parse_xml(build_file_abs)
        if root is None:
            return self._make_result(build_file_abs)

        module_path = os.path.dirname(
            os.path.relpath(build_file_abs, self.repo_root)
        )

        # 提取模块标识
        ns = self._get_ns(root)
        group_id = self._text(root, "groupId", ns)
        artifact_id = self._text(root, "artifactId", ns) or module_path
        name = f"{group_id}:{artifact_id}" if group_id else artifact_id

        # 建立全仓模块坐标索引（用于内部匹配）
        if not hasattr(self, "_module_index"):
            self._module_index = self._build_module_index()

        # 提取依赖
        internal_deps, external_deps = self._extract_deps(
            root, ns, module_path
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
        build_file_abs = os.path.join(self.repo_root, result.build_file)
        module_dir = os.path.dirname(build_file_abs)

        success, stdout, stderr = self._run_cmd(
            [
                "mvn", "dependency:tree",
                "-DoutputType=json",
                "-f", build_file_abs,
                "--batch-mode",
            ],
            timeout=120,
            cwd=module_dir,
        )

        if not success:
            result.degraded = True
            reason = f"mvn dependency:tree failed: {stderr.strip()[:200]}"
            result.degraded_reason = reason
            for dep in result.external_deps:
                dep.degraded = True
                dep.degraded_reason = reason
            return result

        # mvn 输出中 JSON 可能嵌在日志文本中
        # 查找第一个 { 开始的内容
        json_start = stdout.find("{")
        if json_start >= 0:
            json_text = stdout[json_start:]
            try:
                tree_data = json_mod.loads(json_text)
                self._apply_tree_results(result, tree_data)
            except json_mod.JSONDecodeError:
                result.degraded = True
                result.degraded_reason = "mvn dependency:tree JSON parse error"
                return result

        result.analysis_source = AnalysisSource.DYNAMIC
        return result

    # -------------------------------------------------------------------
    # 扫描
    # -------------------------------------------------------------------

    def scan_all_modules(self) -> list[str]:
        pom_files = []
        for root_path, dirs, files in os.walk(self.repo_root):
            dirs[:] = [
                d for d in dirs
                if d not in {
                    ".git", "target", "node_modules", ".mvn",
                } and not d.startswith(".")
            ]
            for fname in files:
                if fname == "pom.xml":
                    pom_files.append(os.path.join(root_path, fname))
        return pom_files

    # -------------------------------------------------------------------
    # 内部方法
    # -------------------------------------------------------------------

    def _parse_xml(self, path: str) -> Optional[ET.Element]:
        try:
            tree = ET.parse(path)
            return tree.getroot()
        except Exception:
            return None

    def _get_ns(self, root: ET.Element) -> str:
        """提取 XML 命名空间前缀."""
        tag = root.tag
        if "}" in tag:
            return tag.split("}")[0] + "}"
        return ""

    def _text(
        self, parent: ET.Element, child_name: str, ns: str
    ) -> Optional[str]:
        """提取子元素文本."""
        child = parent.find(f"{ns}{child_name}")
        if child is not None:
            return child.text
        # 尝试不带命名空间
        child = parent.find(child_name)
        return child.text if child is not None else None

    def _findall(
        self, parent: ET.Element, child_name: str, ns: str
    ) -> list[ET.Element]:
        """查找所有匹配的子元素."""
        result = parent.findall(f"{ns}{child_name}")
        if not result:
            result = parent.findall(child_name)
        return result

    def _build_module_index(self) -> dict[str, str]:
        """构建 (groupId:artifactId) → 模块路径 的索引."""
        index = {}
        parent_groups = {}  # artifactId → groupId (from parent)

        for pom_file in self.scan_all_modules():
            root = self._parse_xml(pom_file)
            if root is None:
                continue
            ns = self._get_ns(root)
            artifact_id = self._text(root, "artifactId", ns)
            group_id = self._text(root, "groupId", ns)

            # 如果没有显式 groupId，尝试从 parent 推断
            if not group_id:
                parent = root.find(f"{ns}parent")
                if parent is None:
                    parent = root.find("parent")
                if parent is not None:
                    p_group = (
                        parent.find(f"{ns}groupId")
                        or parent.find("groupId")
                    )
                    if p_group is not None and p_group.text:
                        group_id = p_group.text

            if artifact_id and group_id:
                dir_path = os.path.dirname(
                    os.path.relpath(pom_file, self.repo_root)
                )
                gav = f"{group_id}:{artifact_id}"
                index[gav] = dir_path

        return index

    def _extract_deps(
        self, root: ET.Element, ns: str, module_path: str
    ) -> tuple[list[InternalDependency], list[ExternalDependency]]:
        """提取依赖并分类为内部/外部."""
        internal_deps = []
        external_deps = []

        # 解析 dependencies
        deps_elem = root.find(f"{ns}dependencies")
        if deps_elem is None:
            deps_elem = root.find("dependencies")

        if deps_elem is not None:
            for dep in self._findall(deps_elem, "dependency", ns):
                g = self._text(dep, "groupId", ns) or ""
                a = self._text(dep, "artifactId", ns) or ""
                v = self._text(dep, "version", ns)
                scope_str = self._text(dep, "scope", ns) or "compile"
                # optional 依赖
                optional = self._text(dep, "optional", ns)

                if not a:
                    continue

                scope = self.SCOPE_MAP.get(
                    scope_str.lower(), DependencyScope.COMPILE
                )

                # 可选依赖一般不计入核心依赖
                if optional and optional.lower() == "true":
                    scope = DependencyScope.PROVIDED

                gav = f"{g}:{a}"
                dep_name = f"{g}:{a}"

                # 判断是否为内部依赖
                if gav in self._module_index:
                    target_path = self._module_index[gav]
                    if target_path != module_path:
                        internal_deps.append(InternalDependency(
                            target=target_path,
                            scope=scope,
                            artifact=gav,
                        ))
                else:
                    external_deps.append(ExternalDependency(
                        name=dep_name,
                        version=v,  # pom.xml 中可能有 version
                        scope=scope,
                    ))

        return internal_deps, external_deps

    def _apply_tree_results(
        self,
        result: ModuleDependencies,
        tree_data: dict,
    ) -> None:
        """递归解析 mvn dependency:tree JSON 输出.

        格式:
        {
          "children": [
            {
              "groupId": "...",
              "artifactId": "...",
              "version": "...",
              "scope": "...",
              "omitted": true/false,
              "children": [...]
            }
          ]
        }
        """

        def walk(node: dict) -> list[tuple[str, str, str, list[str]]]:
            """返回: [(name, version, scope, transitive_names), ...]."""
            results = []
            for child in node.get("children", []):
                g = child.get("groupId", "")
                a = child.get("artifactId", "")
                v = child.get("version", "")
                scope = child.get("scope", "compile")
                gav = f"{g}:{a}"
                # 递归获取传递依赖
                sub_results = walk(child)
                transitive = [r[0] for r in sub_results]
                results.append((gav, v, scope, transitive))
                results.extend(sub_results)
            return results

        dep_entries = walk(tree_data)

        # 用动态结果增强外部依赖
        dep_by_name = {d.name: d for d in result.external_deps}
        for name, version, scope, transitive in dep_entries:
            if name in dep_by_name:
                dep = dep_by_name[name]
                dep.version = version
                dep.transitive = transitive
                dep.scope = self.SCOPE_MAP.get(scope, DependencyScope.COMPILE)
