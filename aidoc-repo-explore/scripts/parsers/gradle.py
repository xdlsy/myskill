#!/usr/bin/env python3
# =============================================================================
# parsers/gradle.py — Gradle 解析器（静态 + 动态）
# =============================================================================
# 支持 Groovy DSL (build.gradle) 和 Kotlin DSL (build.gradle.kts)
# 静态：解析 project 依赖 + 外部依赖字符串
# 动态：./gradlew dependencies → 精确版本 + 冲突检测
# 降级：gradlew/gradle 不存在或执行失败时保留静态结果
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


class GradleParser(BaseParser):
    """Gradle 构建系统解析器."""

    BUILD_SYSTEM = "gradle"

    # 依赖配置 → scope 映射
    CONFIG_SCOPE_MAP = {
        "implementation": DependencyScope.COMPILE,
        "api": DependencyScope.COMPILE,
        "compileOnly": DependencyScope.PROVIDED,
        "compileOnlyApi": DependencyScope.PROVIDED,
        "runtimeOnly": DependencyScope.RUNTIME,
        "testImplementation": DependencyScope.TEST,
        "testCompileOnly": DependencyScope.TEST,
        "testRuntimeOnly": DependencyScope.TEST,
        "androidTestImplementation": DependencyScope.TEST,
        "debugImplementation": DependencyScope.COMPILE,
        "releaseImplementation": DependencyScope.COMPILE,
        "kapt": DependencyScope.COMPILE,
        "annotationProcessor": DependencyScope.COMPILE,
        "developmentOnly": DependencyScope.DEV,
    }

    @staticmethod
    def detect(build_file_path: str) -> bool:
        basename = os.path.basename(build_file_path)
        return basename in {
            "build.gradle", "build.gradle.kts",
            "settings.gradle", "settings.gradle.kts",
        }

    # -------------------------------------------------------------------
    # 静态解析
    # -------------------------------------------------------------------

    def parse_static(self, build_file_path: str) -> ModuleDependencies:
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

        # 是否为 Kotlin DSL
        is_kts = build_file_path.endswith(".kts")

        # 提取子项目列表（从 settings.gradle）
        if not hasattr(self, "_subprojects"):
            self._subprojects = self._scan_subprojects()

        # 提取项目名
        name = self._extract_project_name(content, module_path)

        # 提取依赖
        internal_deps, external_deps = self._extract_deps(
            content, is_kts, module_path
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

        # 找到 gradlew 或 gradle
        gradle_cmd = self._find_gradle_command()

        # 对于子项目，构造正确的 task 路径
        # 格式: ./gradlew :subproject:dependencies
        project_path = result.path.replace("/", ":")
        if project_path == ".":
            task_path = "dependencies"
        else:
            task_path = f":{project_path}:dependencies"

        success, stdout, stderr = self._run_cmd(
            [
                gradle_cmd, task_path,
                "--configuration", "runtimeClasspath",
                "--console=plain",
                "-q",  # quiet — 只输出 task 结果
            ],
            timeout=120,
            cwd=self.repo_root,
        )

        if not success:
            result.degraded = True
            reason = f"gradle dependencies failed: {stderr.strip()[:200]}"
            result.degraded_reason = reason
            for dep in result.external_deps:
                dep.degraded = True
                dep.degraded_reason = reason
            return result

        self._apply_gradle_output(result, stdout)
        result.analysis_source = AnalysisSource.DYNAMIC
        return result

    # -------------------------------------------------------------------
    # 扫描
    # -------------------------------------------------------------------

    def scan_all_modules(self) -> list[str]:
        """扫描全仓 build.gradle(.kts) 文件."""
        gradle_files = []
        for root_path, dirs, files in os.walk(self.repo_root):
            dirs[:] = [
                d for d in dirs
                if d not in {
                    ".git", "build", ".gradle", "node_modules",
                } and not d.startswith(".")
            ]
            for fname in files:
                if fname in {"build.gradle", "build.gradle.kts"}:
                    gradle_files.append(os.path.join(root_path, fname))
        return gradle_files

    # -------------------------------------------------------------------
    # 内部方法
    # -------------------------------------------------------------------

    def _read_file(self, path: str) -> Optional[str]:
        try:
            with open(path, "r", errors="ignore") as f:
                return f.read()
        except Exception:
            return None

    def _scan_subprojects(self) -> set[str]:
        """从 settings.gradle(.kts) 提取子项目列表."""
        subprojects = set()
        for settings_name in ("settings.gradle", "settings.gradle.kts"):
            settings_path = os.path.join(self.repo_root, settings_name)
            content = self._read_file(settings_path)
            if content is None:
                continue

            # 匹配 include(":a", ":b") 或 include ':a', ':b'
            for match in re.finditer(
                r'include\s*[\(\s]\s*([^\)]+)\s*[\)\s]',
                content, re.MULTILINE
            ):
                args = match.group(1)
                # 提取每个 ":project" 字符串
                for proj_match in re.finditer(
                    r'["\'](:[^"\']+)["\']', args
                ):
                    subprojects.add(proj_match.group(1))

        return subprojects

    def _extract_project_name(
        self, content: str, module_path: str
    ) -> str:
        """从 settings.gradle 或目录路径推断项目名."""
        # 尝试从 settings.gradle 的 include 匹配
        path_colon = ":" + module_path.replace("/", ":")
        if path_colon in self._subprojects:
            return path_colon

        # 从 rootProject.name 提取
        m = re.search(r"rootProject\.name\s*=\s*['\"]([^'\"]+)['\"]", content)
        if m:
            return m.group(1)

        return module_path

    def _extract_deps(
        self, content: str, is_kts: bool, module_path: str
    ) -> tuple[list[InternalDependency], list[ExternalDependency]]:
        """从 build.gradle(.kts) 提取所有依赖."""
        internal_deps = []
        external_deps = []
        seen_internal = set()

        if is_kts:
            patterns = self._kts_patterns()
        else:
            patterns = self._groovy_patterns()

        for pattern in patterns:
            for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
                config = match.group(1)
                dep_str = match.group(2).strip()
                scope = self.CONFIG_SCOPE_MAP.get(
                    config, DependencyScope.COMPILE
                )

                # 检测 project 依赖
                if dep_str.startswith("project(") or dep_str.startswith("project "):
                    proj = self._parse_project_dep(dep_str)
                    if proj and proj not in seen_internal:
                        internal_deps.append(InternalDependency(
                            target=self._proj_to_path(proj),
                            scope=scope,
                            artifact=proj,
                        ))
                        seen_internal.add(proj)
                    continue

                # 检测外部依赖
                name, version = self._parse_external_dep(dep_str)
                if name:
                    external_deps.append(ExternalDependency(
                        name=name, version=version, scope=scope,
                    ))

        return internal_deps, external_deps

    def _groovy_patterns(self) -> list[str]:
        """Groovy DSL 依赖声明正则模式."""
        return [
            # implementation 'group:artifact:version'
            r"""(\w+)\s+['\"]([^'\"]+)['\"]""",
            # implementation group: 'g', name: 'a', version: 'v'
            r"""(\w+)\s+group:\s*['\"]([^'\"]+)['\"]""",
            # implementation project(':lib')
            r"""(\w+)\s+project\s*\(([^)]*)\)""",
            # implementation project ':lib'
            r"""(\w+)\s+project\s+['\"]([^'\"]+)['\"]""",
        ]

    def _kts_patterns(self) -> list[str]:
        """Kotlin DSL 依赖声明正则模式."""
        return [
            # implementation("group:artifact:version")
            r"""(\w+)\s*\(\s*\"([^\"]+)\"\s*\)""",
            # implementation(project(":lib"))
            r"""(\w+)\s*\(\s*project\s*\(([^)]+)\)\s*\)""",
            # implementation(group = "g", name = "a", version = "v")
            r"""(\w+)\s*\(\s*group\s*=\s*\"([^\"]+)\"\s*,\s*name""",
        ]

    def _parse_project_dep(self, dep_str: str) -> Optional[str]:
        """从 project 依赖中提取项目路径."""
        # project(':lib') 或 project(':lib', configuration: 'default')
        m = re.search(r"""['\"](:[^'\"]+)['\"]""", dep_str)
        if m:
            return m.group(1)
        # project(path: ':lib')
        m = re.search(r"""path\s*[=:]\s*['\"](:[^'\"]+)['\"]""", dep_str)
        if m:
            return m.group(1)
        return None

    def _parse_external_dep(self, dep_str: str) -> tuple[Optional[str], Optional[str]]:
        """解析外部依赖字符串 → (name, version).

        格式: 'group:artifact:version' 或 "group:artifact:version"
        """
        # 去除引号
        dep_str = dep_str.strip("'\"")

        # 格式: group:artifact:version
        parts = dep_str.split(":")
        if len(parts) >= 2:
            name = f"{parts[0]}:{parts[1]}"
            version = parts[2] if len(parts) >= 3 else None
            return name, version

        # 格式: 只有 artifact (version catalog 引用)
        # 像 libs.guava 或 libs.versions.guava
        if "." in dep_str and not dep_str.startswith(":"):
            return dep_str, None

        return None, None

    def _proj_to_path(self, proj: str) -> str:
        """将 Gradle 项目路径 (:lib:common) 转换为目录路径 (lib/common)."""
        path = proj.lstrip(":")
        return path.replace(":", "/")

    def _find_gradle_command(self) -> str:
        """找到可用的 gradle 命令."""
        # 优先使用 gradlew
        gradlew = os.path.join(self.repo_root, "gradlew")
        if os.path.isfile(gradlew) and os.access(gradlew, os.X_OK):
            return gradlew
        return "gradle"

    def _apply_gradle_output(
        self, result: ModuleDependencies, output: str
    ) -> None:
        """解析 gradle dependencies 文本输出并增强结果.

        格式示例:
        runtimeClasspath - Runtime classpath of source set 'main'.
        +--- org.springframework.boot:spring-boot-starter:3.2.0
        |    +--- org.springframework.boot:spring-boot:3.2.0
        |    \--- org.springframework:spring-core:6.1.0
        \--- com.google.guava:guava:33.0.0-jre
             \--- com.google.guava:failureaccess:1.0.2
        """
        # 按依赖名查找每个外部依赖
        dep_by_name = {}
        for dep in result.external_deps:
            dep_by_name[dep.name] = dep

        # 解析输出中的每行
        # 匹配: 缩进 + 符号 + group:artifact:version
        dep_pattern = re.compile(
            r'^([\s+|\\-]*)[+|\\]---\s+([^:\s]+):([^:\s]+):(\S+)'
        )

        for match in dep_pattern.finditer(output, re.MULTILINE):
            indent = match.group(1)
            group = match.group(2)
            artifact = match.group(3)
            version = match.group(4)
            gav = f"{group}:{artifact}"

            # 计算深度（用于区分直接依赖和传递依赖）
            depth = indent.count("|") + indent.count("+") + indent.count("\\")
            depth = max(0, depth)

            if gav in dep_by_name:
                dep_by_name[gav].version = version
            elif depth == 0:
                # 直接依赖（可能在静态解析时被遗漏）
                result.external_deps.append(ExternalDependency(
                    name=gav, version=version,
                ))

        # 收集传递依赖
        # 简化实现：将同组的依赖收集到相关外部依赖下
