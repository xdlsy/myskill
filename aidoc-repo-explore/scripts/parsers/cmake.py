#!/usr/bin/env python3
# =============================================================================
# parsers/cmake.py — CMake 构建系统解析器（仅静态）
# =============================================================================
# CMake 没有标准化的依赖树命令，因此仅做静态解析。
# 策略：
#   1. 全仓扫描 CMakeLists.txt → 建立 target名 → 目录路径 映射
#   2. 解析每个 CMakeLists.txt → 提取 target_link_libraries、add_subdirectory
#   3. 用映射将依赖的 target 名解析为模块路径
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
)


class CMakeParser(BaseParser):
    """CMake 构建系统解析器（仅静态）."""

    BUILD_SYSTEM = "cmake"

    # CMake 中 target_link_libraries 的可见性关键字
    VISIBILITY_KEYWORDS = {"PUBLIC", "PRIVATE", "INTERFACE"}

    # 知名的外部库前缀（不在本仓库内的 target 名）
    EXTERNAL_PREFIXES = {
        "Boost::", "OpenSSL::", "CURL::", "ZLIB::", "PNG::", "JPEG::",
        "Qt", "Qt5::", "Qt6::", "wxWidgets::", "GTest::", "gmock", "gtest",
        "Catch2::", "fmt::", "spdlog::", "nlohmann_json::", "yaml-cpp::",
        "absl::", "protobuf::", "gRPC::", "utf8_range", "Threads::",
        "Python", "Python3::", "MPI::", "OpenMP::", "Vulkan::",
        "SDL2::", "SFML", "glfw", "GLEW::", "GLUT::", "OpenGL::",
        "CUDA::", "OpenCL::", "TBB::", "Eigen3::", "doxygen",
        "PkgConfig::", "Doxygen", "LAPACK", "BLAS",
        "cpr::", "curl", "libcurl", "c-ares::",
        "unofficial-", "pkg-config",
    }

    @staticmethod
    def detect(build_file_path: str) -> bool:
        """检测是否为 CMakeLists.txt."""
        return os.path.basename(build_file_path) == "CMakeLists.txt"

    # -------------------------------------------------------------------
    # 主入口
    # -------------------------------------------------------------------

    def parse_static(self, build_file_path: str) -> ModuleDependencies:
        """解析单个 CMakeLists.txt 的依赖关系.

        注意：此方法需要访问 self.repo_root 进行全局 target 扫描。
        建议先调用 build_target_map() 再对每个 CMakeLists.txt 调用此方法。
        """
        # 确保 target map 已构建
        if not hasattr(self, "_target_map"):
            self._target_map = self._build_target_map()

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
        project_name = self._extract_project_name(content)

        internal_deps = self._extract_internal_deps(content, module_path)
        external_deps = self._extract_external_deps(content)

        return ModuleDependencies(
            path=module_path,
            name=project_name or module_path,
            build_system=self.BUILD_SYSTEM,
            build_file=os.path.relpath(build_file_abs, self.repo_root),
            internal_deps=internal_deps,
            external_deps=external_deps,
        )

    # -------------------------------------------------------------------
    # 全局扫描
    # -------------------------------------------------------------------

    def build_target_map(self) -> dict[str, str]:
        """扫描全仓 CMakeLists.txt，建立 target名 → 目录路径 映射."""
        self._target_map = self._build_target_map()
        return self._target_map

    def scan_all_modules(self) -> list[str]:
        """扫描全仓所有 CMakeLists.txt，返回构建文件路径列表."""
        cmake_files = []
        for root, dirs, files in os.walk(self.repo_root):
            # 跳过常见的非源码目录
            dirs[:] = [
                d for d in dirs
                if d not in {
                    ".git", "build", "cmake-build-*", "out", "dist",
                    "__pycache__", ".venv", "venv",
                } and not d.startswith(".")
            ]
            for fname in files:
                if fname == "CMakeLists.txt":
                    cmake_files.append(os.path.join(root, fname))
        return cmake_files

    # -------------------------------------------------------------------
    # 内部方法
    # -------------------------------------------------------------------

    def _read_file(self, path: str) -> Optional[str]:
        """读取文件内容."""
        try:
            with open(path, "r", errors="ignore") as f:
                return f.read()
        except Exception:
            return None

    def _build_target_map(self) -> dict[str, str]:
        """构建 target 名 → 模块路径 映射."""
        target_map: dict[str, str] = {}

        for cmake_file in self.scan_all_modules():
            content = self._read_file(cmake_file)
            if content is None:
                continue

            dir_path = os.path.dirname(
                os.path.relpath(cmake_file, self.repo_root)
            )

            # 提取 add_library 和 add_executable 定义的 target
            for pattern in [
                r"add_library\s*\(\s*(\S+)",
                r"add_executable\s*\(\s*(\S+)",
            ]:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    target_name = match.group(1)
                    # 处理 ${PROJECT_NAME} 等变量引用
                    if "${" in target_name:
                        continue
                    if target_name not in target_map:
                        target_map[target_name] = dir_path

        return target_map

    def _extract_project_name(self, content: str) -> Optional[str]:
        """从 project() 命令提取项目名."""
        match = re.search(
            r"project\s*\(\s*(\S+)", content, re.IGNORECASE
        )
        return match.group(1) if match else None

    def _extract_internal_deps(
        self, content: str, module_path: str
    ) -> list[InternalDependency]:
        """从 target_link_libraries 提取内部依赖."""
        deps: list[InternalDependency] = []
        seen = set()

        # 提取所有 target_link_libraries 调用
        # 模式：target_link_libraries(<target> [visibility] <dep1> <dep2> ...)
        tll_pattern = r"target_link_libraries\s*\(([^)]+)\)"
        for match in re.finditer(tll_pattern, content, re.IGNORECASE):
            args = self._tokenize_cmake_args(match.group(1))

            if len(args) < 2:
                continue

            # 第一个参数是 target 名，后面是依赖
            current_scope = DependencyScope.COMPILE  # 默认 PUBLIC

            for arg in args[1:]:
                # 跳过 visibility 关键字
                if arg.upper() in self.VISIBILITY_KEYWORDS:
                    continue
                # 跳过 generator expressions
                if arg.startswith("$<"):
                    continue
                # 跳过条件表达式和变量引用
                if "${" in arg:
                    continue

                dep_name = arg.strip()
                if not dep_name:
                    continue

                # 判断是否为内部依赖
                if dep_name in self._target_map:
                    target_path = self._target_map[dep_name]
                    if target_path != module_path and dep_name not in seen:
                        deps.append(InternalDependency(
                            target=target_path,
                            scope=current_scope,
                            artifact=dep_name,
                        ))
                        seen.add(dep_name)

        return deps

    def _extract_external_deps(
        self, content: str
    ) -> list[ExternalDependency]:
        """提取外部依赖（find_package + target_link_libraries 中的外部 target）."""
        deps: list[ExternalDependency] = []
        seen = set()

        # 1. find_package 调用
        for match in re.finditer(
            r"find_package\s*\(\s*(\S+)", content, re.IGNORECASE
        ):
            name = match.group(1)
            if name not in seen:
                deps.append(ExternalDependency(name=name))
                seen.add(name)

        # 2. FetchContent 声明
        for match in re.finditer(
            r"FetchContent_Declare\s*\(\s*(\S+)", content, re.IGNORECASE
        ):
            name = match.group(1)
            if name not in seen:
                version = None
                # 尝试提取 GIT_TAG 作为版本
                v_match = re.search(
                    r"GIT_TAG\s+(\S+)", content, re.IGNORECASE
                )
                if v_match:
                    version = v_match.group(1)
                deps.append(ExternalDependency(
                    name=f"FetchContent::{name}", version=version
                ))
                seen.add(name)

        # 3. target_link_libraries 中的外部 target
        tll_pattern = r"target_link_libraries\s*\(([^)]+)\)"
        for match in re.finditer(tll_pattern, content, re.IGNORECASE):
            args = self._tokenize_cmake_args(match.group(1))
            for arg in args[1:]:
                if arg.upper() in self.VISIBILITY_KEYWORDS:
                    continue
                if arg.startswith("$<"):
                    continue
                if "${" in arg:
                    continue

                dep_name = arg.strip()
                if not dep_name:
                    continue

                # 排除内部 target
                if dep_name in self._target_map:
                    continue

                # 检查是否为外部依赖
                if self._is_external_lib(dep_name) and dep_name not in seen:
                    deps.append(ExternalDependency(name=dep_name))
                    seen.add(dep_name)

        return deps

    def _is_external_lib(self, name: str) -> bool:
        """判断 target 名是否为外部库."""
        # 带 :: 的一般是 CMake 导入 target（如 Boost::filesystem）
        if "::" in name:
            return True

        # 常见外部库名前缀
        for prefix in self.EXTERNAL_PREFIXES:
            if name.startswith(prefix) or name == prefix:
                return True

        # 全小写且不含路径分隔符的（可能是系统库）
        if name.islower() and "/" not in name and "." not in name:
            # 某些常见的 short name
            if name in {"m", "pthread", "dl", "rt", "c", "z", "ssl",
                         "crypto", "curl", "lzma", "bz2", "lz4"}:
                return True

        return False

    def _tokenize_cmake_args(self, args_str: str) -> list[str]:
        """简单 tokenize CMake 参数列表（处理引号）."""
        tokens = []
        current = ""
        in_quote = False
        quote_char = None

        for char in args_str:
            if in_quote:
                if char == quote_char:
                    in_quote = False
                    if current.strip():
                        tokens.append(current.strip())
                    current = ""
                else:
                    current += char
            elif char in ('"', "'"):
                in_quote = True
                quote_char = char
            elif char in (" ", "\t", "\n"):
                if current.strip():
                    tokens.append(current.strip())
                    current = ""
            else:
                current += char

        if current.strip():
            tokens.append(current.strip())

        return tokens
