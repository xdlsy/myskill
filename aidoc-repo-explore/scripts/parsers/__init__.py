#!/usr/bin/env python3
# =============================================================================
# parsers/__init__.py — 构建系统解析器注册表
# =============================================================================

from .base import (
    BaseParser,
    DependencyGraphBuilder,
    DependencyScope,
    AnalysisSource,
    InternalDependency,
    ExternalDependency,
    ModuleDependencies,
    DependencyGraph,
)
from .cmake import CMakeParser
from .gomod import GomodParser
from .maven import MavenParser
from .gradle import GradleParser
from .pyproject import PyprojectParser

# 构建文件 → Parser 类的注册表（按优先级排列）
PARSER_REGISTRY: list[type[BaseParser]] = [
    CMakeParser,
    MavenParser,
    GradleParser,
    GomodParser,
    PyprojectParser,
]


def detect_parser(build_file_path: str) -> type[BaseParser] | None:
    """检测 build_file_path 对应的 Parser 类."""
    for parser_cls in PARSER_REGISTRY:
        if parser_cls.detect(build_file_path):
            return parser_cls
    return None


__all__ = [
    "BaseParser",
    "DependencyGraphBuilder",
    "DependencyScope",
    "AnalysisSource",
    "InternalDependency",
    "ExternalDependency",
    "ModuleDependencies",
    "DependencyGraph",
    "CMakeParser",
    "GomodParser",
    "MavenParser",
    "GradleParser",
    "PyprojectParser",
    "PARSER_REGISTRY",
    "detect_parser",
]
