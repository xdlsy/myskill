#!/usr/bin/env python3
# =============================================================================
# parsers/base.py — 构建系统解析器抽象基类
# =============================================================================
# 定义统一的模块依赖数据结构和解析器接口。
# 每个具体 parser 实现两个核心方法：
#   parse_static()  → 纯文件解析，零依赖，100% 可用
#   enhance_dynamic(base_result) → 运行构建工具，补充版本号 + 传递依赖
# =============================================================================

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# 数据类型定义
# ---------------------------------------------------------------------------

class DependencyScope(str, Enum):
    """依赖作用域."""
    COMPILE = "compile"
    RUNTIME = "runtime"
    TEST = "test"
    PROVIDED = "provided"
    DEV = "dev"
    UNKNOWN = "unknown"


class AnalysisSource(str, Enum):
    """分析来源."""
    DYNAMIC = "dynamic"    # 通过构建工具实际运行获取
    STATIC = "static"      # 纯文件解析


@dataclass
class InternalDependency:
    """内部依赖：同一仓库内模块 A → 模块 B."""
    target: str                           # 目标模块路径 (如 "libs/common")
    scope: DependencyScope = DependencyScope.COMPILE
    artifact: Optional[str] = None        # Maven/Gradle 坐标 (如 "com.example:common")


@dataclass
class ExternalDependency:
    """外部依赖：模块依赖的第三方库."""
    name: str                             # 依赖名称 (如 "com.google.guava:guava")
    version: Optional[str] = None         # 版本号 (动态增强后填充)
    scope: DependencyScope = DependencyScope.COMPILE
    transitive: list[str] = field(default_factory=list)  # 传递依赖列表
    degraded: bool = False                # 是否为静态降级结果
    degraded_reason: Optional[str] = None


@dataclass
class ModuleDependencies:
    """单个模块的完整依赖信息."""
    path: str                             # 模块路径 (如 "services/order")
    name: str                             # 模块名称 (从构建文件提取)
    build_system: str                     # 构建系统类型 (cmake/maven/gradle/gomod/pyproject)
    build_file: str                       # 构建文件路径
    analysis_source: AnalysisSource = AnalysisSource.STATIC
    internal_deps: list[InternalDependency] = field(default_factory=list)
    external_deps: list[ExternalDependency] = field(default_factory=list)
    degraded: bool = False                # 模块整体是否降级
    degraded_reason: Optional[str] = None


@dataclass
class DependencyGraph:
    """仓库级依赖图."""
    repository_root: str
    modules: dict[str, ModuleDependencies]  # path → ModuleDependencies
    edges: list[dict] = field(default_factory=list)       # [{from, to, scope}]
    nodes: list[str] = field(default_factory=list)        # 所有模块路径


# ---------------------------------------------------------------------------
# 抽象基类
# ---------------------------------------------------------------------------

class BaseParser(ABC):
    """构建系统解析器抽象基类.

    每个具体 parser 应：
    1. 设置 BUILD_SYSTEM 类属性（如 "cmake", "maven"）
    2. 实现 detect() → 判断是否为本 parser 负责的构建系统
    3. 实现 parse_static() → 纯文件解析
    4. 实现 enhance_dynamic() → 运行构建工具增强（可选，默认返回原结果）
    """

    BUILD_SYSTEM: str = "unknown"

    def __init__(self, repo_root: str):
        self.repo_root = os.path.abspath(repo_root)

    # -----------------------------------------------------------------------
    # 子类必须实现
    # -----------------------------------------------------------------------

    @staticmethod
    @abstractmethod
    def detect(build_file_path: str) -> bool:
        """检测 build_file_path 是否为本 parser 处理的构建文件类型.

        Args:
            build_file_path: 构建文件的完整路径.

        Returns:
            True 如果本 parser 能处理此构建文件.
        """
        ...

    @abstractmethod
    def parse_static(self, build_file_path: str) -> ModuleDependencies:
        """纯静态解析构建文件（不运行任何构建工具）.

        此方法必须能独立工作，不依赖任何外部工具。
        至少返回内部依赖列表 + 外部依赖名称（版本号可为 None）。

        Args:
            build_file_path: 构建文件的完整路径.

        Returns:
            模块依赖信息（分析来源标记为 STATIC）.
        """
        ...

    # -----------------------------------------------------------------------
    # 子类可选覆盖
    # -----------------------------------------------------------------------

    def enhance_dynamic(
        self, result: ModuleDependencies
    ) -> ModuleDependencies:
        """尝试运行构建工具增强依赖信息（填充版本号 + 传递依赖）.

        默认实现：不做任何增强，返回原结果。
        子类覆盖此方法以实现动态增强。

        Args:
            result: parse_static() 返回的静态分析结果.

        Returns:
            增强后的结果（成功时 analysis_source 改为 DYNAMIC，失败时标记 degraded）.
        """
        return result

    # -----------------------------------------------------------------------
    # 通用工具方法
    # -----------------------------------------------------------------------

    def _resolve_path(self, relative_path: str) -> str:
        """将相对路径解析为绝对路径."""
        return os.path.normpath(os.path.join(self.repo_root, relative_path))

    def _make_result(
        self,
        build_file_path: str,
        name: Optional[str] = None,
        internal_deps: Optional[list[InternalDependency]] = None,
        external_deps: Optional[list[ExternalDependency]] = None,
    ) -> ModuleDependencies:
        """创建 ModuleDependencies 的便捷方法."""
        build_file_rel = os.path.relpath(build_file_path, self.repo_root)
        module_path = os.path.dirname(build_file_rel)

        if name is None:
            name = module_path

        return ModuleDependencies(
            path=module_path,
            name=name,
            build_system=self.BUILD_SYSTEM,
            build_file=build_file_rel,
            analysis_source=AnalysisSource.STATIC,
            internal_deps=internal_deps or [],
            external_deps=external_deps or [],
        )

    def _run_cmd(
        self, cmd: list[str], timeout: int = 60, cwd: Optional[str] = None
    ) -> tuple[bool, str, str]:
        """运行外部命令，返回 (success, stdout, stderr).

        Args:
            cmd: 命令及其参数列表.
            timeout: 超时秒数.
            cwd: 工作目录（默认 repo_root）.

        Returns:
            (success, stdout, stderr) 三元组.
        """
        import subprocess

        work_dir = cwd or self.repo_root
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=work_dir,
            )
            return (result.returncode == 0, result.stdout, result.stderr)
        except FileNotFoundError:
            return (False, "", f"command not found: {cmd[0]}")
        except subprocess.TimeoutExpired:
            return (False, "", f"timeout ({timeout}s)")
        except Exception as exc:
            return (False, "", str(exc))


# ---------------------------------------------------------------------------
# 依赖图构建器（供核心引擎使用）
# ---------------------------------------------------------------------------

class DependencyGraphBuilder:
    """依赖图构建器，聚合各 parser 的结果生成完整依赖图."""

    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.modules: dict[str, ModuleDependencies] = {}

    def add_module(self, result: ModuleDependencies) -> None:
        """添加一个模块的依赖分析结果."""
        self.modules[result.path] = result

    def build_graph(self) -> DependencyGraph:
        """构建完整的依赖图."""
        nodes = list(self.modules.keys())
        edges = []
        for module_path, mod in self.modules.items():
            for dep in mod.internal_deps:
                target_path = self._resolve_target_path(module_path, dep.target)
                edges.append({
                    "from": module_path,
                    "to": target_path,
                    "scope": dep.scope.value,
                })

        graph = DependencyGraph(
            repository_root=self.repo_root,
            modules=self.modules,
            nodes=nodes,
            edges=edges,
        )
        return graph

    def _resolve_target_path(self, source_path: str, target_name: str) -> str:
        """将依赖目标名解析为模块路径.

        优先精确匹配，失败时保留原名.
        """
        # 精确匹配
        if target_name in self.modules:
            return target_name

        # 尝试作为子路径匹配
        for mod_path in self.modules:
            if mod_path.endswith(target_name) or mod_path == target_name:
                return mod_path

        return target_name

    def compute_topological_order(self) -> list[str]:
        """计算拓扑排序（Kahn 算法）.

        返回顺序：被依赖的模块在前，依赖方在后（即构建顺序）.
        """
        nodes = set(self.modules.keys())
        # 构建邻接表和入度
        # 边方向：depended_on → dependent（即 common → order 表示 order 依赖 common）
        adj = {n: [] for n in nodes}
        in_degree = {n: 0 for n in nodes}

        for module_path, mod in self.modules.items():
            for dep in mod.internal_deps:
                target = self._resolve_target_path(module_path, dep.target)
                if target in nodes:
                    # 被依赖方 → 依赖方 的入度 +1
                    adj[target].append(module_path)
                    in_degree[module_path] += 1

        # Kahn's algorithm
        queue = [n for n in nodes if in_degree.get(n, 0) == 0]
        order = []

        while queue:
            node = queue.pop(0)
            order.append(node)
            for neighbor in adj.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(nodes):
            # 存在循环依赖 —— 将剩余节点追加到末尾
            remaining = nodes - set(order)
            order.extend(remaining)

        return order

    def find_entry_points(self) -> list[str]:
        """找出不被任何内部模块依赖的模块（入口点）."""
        all_consumers = set()
        for mod in self.modules.values():
            for dep in mod.internal_deps:
                target = self._resolve_target_path(mod.path, dep.target)
                all_consumers.add(target)

        return sorted(
            path for path in self.modules if path not in all_consumers
        )

    def detect_circular_dependencies(self) -> Optional[list[list[str]]]:
        """检测循环依赖（DFS 颜色标记法）.

        Returns:
            循环依赖路径列表，无循环则返回 None.
        """
        nodes = set(self.modules.keys())
        adj = {n: [] for n in nodes}

        for module_path, mod in self.modules.items():
            for dep in mod.internal_deps:
                target = self._resolve_target_path(module_path, dep.target)
                if target in nodes:
                    adj[module_path].append(target)

        WHITE, GRAY, BLACK = 0, 1, 2
        color = {n: WHITE for n in nodes}
        cycles = []
        stack = []

        def dfs(node):
            color[node] = GRAY
            stack.append(node)
            for neighbor in adj.get(node, []):
                if color.get(neighbor) == GRAY:
                    # 找到循环
                    cycle_start = stack.index(neighbor)
                    cycles.append(stack[cycle_start:] + [neighbor])
                elif color.get(neighbor) == WHITE:
                    dfs(neighbor)
            stack.pop()
            color[node] = BLACK

        for node in nodes:
            if color.get(node) == WHITE:
                dfs(node)

        return cycles if cycles else None
