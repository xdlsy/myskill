---
name: aidoc-repo-explore
description: 用于探索和采集代码仓画像信息，生成诊断摘要供用户确认。适用于代码仓文档化、新人上手、架构评审等场景。结果写入 .aidoc/phase0/repo-profile.md 供下游 skill（如 aidoc-create）消费。由"帮我分析代码仓"、"采集代码仓信息"、"探索项目结构"等指令触发。
---

# 代码仓探索与画像采集

## 概览

LLM 自主探索代码仓，采集代码规模、语言分布、模块结构、构建系统、测试框架、CI/CD 等关键信息，汇总为诊断摘要供用户确认。结果记入内存，供下游 skill 消费。

**纯 LLM 驱动，不依赖外部脚本。** 用 `tokei`、`ls`、`git log`、文件读取等原生工具完成所有采集。

## 适用场景

- 为代码仓文档化提供基础数据
- 新人快速了解陌生代码仓的全貌
- 架构评审前的信息采集
- CI/CD 迁移前的现状摸排

## 前置条件

- 推荐安装 `tokei`（代码行数统计）：`brew install tokei`；若不可用则用 `cloc` 或 `find` + `wc -l` 代替
- 从目标仓库根目录运行

## 工作流程

### 步骤 1：代码规模与语言分布

运行 `tokei`（首选）获取按语言分类的文件数、代码行数、注释行数。

若 tokei 不可用，降级方案：
- `cloc .` 
- 或按主要扩展名分别统计：`find . -name "*.py" | xargs wc -l` 等

输出要点：
- 识别 **primary_language**（代码行数最多的那门语言）
- 列出所有检测到的语言及其代码行数、文件数、占比
- 注意区分真正的源代码和 Markdown/JSON/YAML 等配置/文档文件
- 对 C/C++ 项目，注意区分 C 和 C++ 各自的文件数/行数（`.c`/`.h` vs `.cpp`/`.cc`/`.cxx`/`.hpp`/`.hxx`），以及两者混合的比例

### 步骤 2：目录结构与模块划分

扫描仓库顶层目录，区分以下内容并归类：

| 目录类型 | 判定标准 | 示例 |
|---------|---------|------|
| **根模块** | 含独立构建文件（CMakeLists.txt、Makefile、pom.xml、go.mod、pyproject.toml、package.json、Cargo.toml 等）或独立 src 目录 | `services/order/`, `frontend/`, `libs/network/` |
| **配置/部署** | 仅含 CI 配置、Dockerfile、K8s yaml 等 | `deploy/`, `.github/` |
| **文档** | 仅含 .md, .rst 等 | `docs/`, `wiki/` |
| **脚本/工具** | 辅助脚本，非主体代码 | `scripts/`, `tools/` |

对每个根模块，深入 3-4 层识别子模块结构：
- 寻找是否有 `src/main/java/com/...`（Java）、`internal/`、`pkg/`（Go）等标准布局
- 对 C/C++ 项目，识别目录模式：
  - `src/` + `include/` + `tests/`：经典分离式布局
  - `lib/` + `src/`：库 + 可执行文件分离
  - 单层 `*.c`/`*.cpp` + `CMakeLists.txt`：小型项目
  - `third_party/` / `vendor/`：第三方依赖目录
- 识别包/命名空间的第一级分组

**判定模块类型：**
- `service` — 有 main/入口类的独立可运行服务
- `library` — 被其他模块依赖的公共库（无独立入口）
- `extension` — 浏览器扩展、IDE 插件等
- `adapter` — 适配器/桥接层（如多平台适配）
- `config` — 纯配置文件集合
- `test` — 独立的测试模块

**识别叶子模块：** 不再包含独立子模块的最细粒度功能单元。一个根模块下可有多个叶子模块。

### 步骤 3：构建系统检测

扫描以下构建文件并推断构建命令：

| 构建文件 | 语言/生态 | 推断命令 |
|---------|----------|---------|
| `CMakeLists.txt`（顶层） | C/C++ (CMake) | `cmake -B build && cmake --build build` |
| `CMakeLists.txt`（顶层 + Presets） | C/C++ (CMake + Presets) | `cmake --preset default && cmake --build --preset default` |
| `CMakeLists.txt`（子目录） | C/C++ (CMake 子项目) | 由顶层 CMakeLists.txt 通过 `add_subdirectory` 引入 |
| `CMakeLists.txt`（header-only） | C/C++ (header-only 库) | `cmake -B build && cmake --build build`（仅构建测试/示例）；库本身无需编译 |
| `Makefile` / `GNUmakefile` | C/C++/通用 | `make` / `make all`（检测默认目标决定） |
| `Makefile`（含 `build/` 或 `obj/` 目标） | C/C++ (Makefile) | `make` + 推荐 `make -j$(nproc)` 并行编译 |
| `configure.ac` / `configure.in` + `Makefile.am` | C/C++ (Autotools) | `autoreconf -fi && ./configure && make` |
| `meson.build` | C/C++ (Meson) | `meson setup build && meson compile -C build` |
| `BUILD` / `BUILD.bazel` | C/C++/多语言 (Bazel) | `bazel build //...` |
| `conanfile.txt` / `conanfile.py` | C/C++ (Conan 包管理器) | `conan install .`（配合 CMake：`conan install . --build=missing -s build_type=Release`） |
| `vcpkg.json` / `vcpkg-configuration.json` | C/C++ (vcpkg 包管理器) | `vcpkg install`（配合 CMake：`cmake -B build -DCMAKE_TOOLCHAIN_FILE=...`） |
| `xmake.lua` | C/C++ (Xmake) | `xmake` / `xmake build` |
| `pom.xml` | Java/Maven | `mvn clean package` |
| `build.gradle` | Java/Kotlin/Gradle (Groovy DSL) | `gradle build` |
| `build.gradle.kts` | Java/Kotlin/Gradle (Kotlin DSL) | `gradle build` |
| `settings.gradle` / `settings.gradle.kts` | Gradle 多项目 | 从根项目运行：`gradle build` |
| `gradle.properties` | Gradle 配置 | 配合 `build.gradle*` 使用 |
| `gradlew` / `gradlew.bat` | Gradle Wrapper | `./gradlew build`（推荐，无需系统安装 Gradle） |
| `package.json` | Node.js | `npm run build` / `yarn build` |
| `pyproject.toml` / `setup.py` | Python | `pip install -e .` |
| `go.mod` | Go | `go build ./...` |
| `Cargo.toml` | Rust | `cargo build` |

**CMake 专项检测**（若检测到 `CMakeLists.txt`）：
1. 读取顶层 `CMakeLists.txt` 的前 120 行，提取：
   - `project(...)` — 项目名称和使用的语言（LANGUAGES C CXX 等）
   - `cmake_minimum_required(VERSION ...)` — CMake 最低版本要求
   - `add_subdirectory(...)` — 子项目/子模块列表
   - `find_package(...)` — 主要外部依赖
   - `FetchContent_Declare(...)` / `FetchContent_MakeAvailable(...)` — 源码级依赖
   - `set(CMAKE_C_STANDARD ...)` / `set(CMAKE_CXX_STANDARD ...)` — C/C++ 标准版本
   - `option(...)` — 构建选项（如 BUILD_TESTS、BUILD_SHARED_LIBS 等）
   - `include(CTest)` / `enable_testing()` — 测试支持
   - `install(...)` — 安装目标
   - `export(...)` / `CPack` 相关 — 打包/导出配置
2. 扫描各子目录的 `CMakeLists.txt`，识别：
   - `add_executable(...)` — 可执行目标
   - `add_library(...)` — 库目标（区分 STATIC / SHARED / INTERFACE / OBJECT / MODULE）
   - `target_link_libraries(...)` — 目标间的依赖关系
   - `target_include_directories(...)` — 头文件搜索路径
   - `target_compile_definitions(...)` — 编译宏定义
   - `target_compile_options(...)` — 编译选项
3. 检查是否存在 `CMakePresets.json` 或 `CMakeUserPresets.json`：
   - 列出 configure / build / test preset 的名称
   - 检测预设的构建类型（Debug / Release / RelWithDebInfo / MinSizeRel）
4. 检查 `CMakeLists.txt` 中是否包含 `include(CMakePackageConfigHelpers)` 或 `write_basic_package_version_file`，判断是否为可分发库

**Makefile 专项检测**（若检测到 `Makefile` / `GNUmakefile` / `makefile`）：
1. 读取顶层 Makefile 的前 100 行，提取：
   - `.PHONY` 声明的伪目标（如 `all`, `clean`, `install`, `test`, `check`, `dist`）
   - `CC` / `CXX` — 编译器选择（gcc / clang / icc 等）
   - `CFLAGS` / `CXXFLAGS` — 编译选项（判断优化级别 `-O0`/`-O2`/`-Os`、警告级别 `-Wall`/`-Wextra`/`-Werror`）
   - `LDFLAGS` / `LDLIBS` — 链接选项和库依赖
   - `PREFIX` / `DESTDIR` — 安装路径前缀
   - 条件编译指令（`ifeq` / `ifdef` / `ifndef`）— 判断是否区分 Debug/Release
   - `include` 指令 — 是否引入子目录 Makefile 或 `.mk` / `.d` 文件
2. 检查是否存在 `config.mk` / `local.mk` / `Makefile.inc` 等辅助配置文件
3. 列出 Makefile 中声明的所有顶层目标（target），标注默认目标
4. 若 `make -n` 或类似可用，记录默认构建行为；否则从规则中推断
5. 检查 `PREFIX` 或 `DESTDIR` 变量判断是否支持 `make install`

**C/C++ 工具链专项检测**：
1. **编译器检测**：
   - 扫描 `CMakeLists.txt` 中的 `CMAKE_C_COMPILER` / `CMAKE_CXX_COMPILER` 配置
   - 扫描 Makefile 中的 `CC` / `CXX` 变量
   - 检查是否存在交叉编译工具链文件（`*.cmake` 中 `CMAKE_TOOLCHAIN_FILE` 引用，或 `--toolchain` 参数说明）
   - 检查是否存在 `arm-*`、`aarch64-*`、`riscv64-*` 等前缀的工具链引用
2. **C/C++ 标准检测**：
   - CMake：`CMAKE_C_STANDARD` / `CMAKE_CXX_STANDARD`（如 99、11、17、20、23）
   - Makefile：`CFLAGS` 中 `-std=c11` / `-std=gnu17`，`CXXFLAGS` 中 `-std=c++17` / `-std=c++20`
   - 编译数据库：若存在 `compile_commands.json`，从中提取实际使用的 `-std=` 参数
3. **头文件与源文件比例分析**：
   - 若 `.h`/`.hpp` 文件数 > 源文件数（`.c`/`.cpp`），标注可能的 header-only 或模板密集型项目
   - 若仅有头文件 + 构建文件但无可编译源文件 → 判定为 **header-only 库**，构建命令标注为 `（header-only，无需编译）`
4. **包管理器检测**：
   - `conanfile.txt` / `conanfile.py` → Conan
   - `vcpkg.json` / `vcpkg-configuration.json` → vcpkg
   - `*.pc` 文件 → pkg-config（检查是否有自定义 `.pc.in` 模板）
   - `.gitmodules` → Git 子模块依赖（常见于 C/C++ 项目的 `third_party/` 或 `external/`）

	**Gradle 专项检测**（若检测到 `build.gradle` / `build.gradle.kts`）：
	1. 检测 Gradle 项目类型：
	   - **Groovy DSL**：`build.gradle` + `settings.gradle`
	   - **Kotlin DSL**：`build.gradle.kts` + `settings.gradle.kts`
	   - **Gradle Wrapper**：`gradlew` / `gradlew.bat` + `gradle/wrapper/gradle-wrapper.properties`（提取 Gradle 版本）
	   - **多项目构建**：`settings.gradle(.kts)` 中包含 `include(...)` 或 `includeFlat(...)`
	2. 读取 `build.gradle(.kts)` 的前 80 行，提取：
	   - `plugins { }` — 插件列表（如 `java`、`kotlin`、`application`、`spring-boot`、`org.springframework.boot`）
	   - `group` / `version` — 项目坐标
	   - `sourceCompatibility` / `targetCompatibility` — Java 版本
	   - `repositories { }` — 仓库配置（mavenCentral、google、jitpack、私有仓库 URL）
	   - `dependencies { }` — 关键依赖（识别 Spring Boot、Ktor、Quarkus 等框架）
	   - `application { mainClass.set(...) }` — 主类（可运行应用）
	   - `test { useJUnitPlatform() }` — 测试引擎
	   - `tasks.withType<Test> { ... }` — 测试配置
	   - `kotlin { jvmToolchain(...) }` — Kotlin 版本
	3. 若为多项目构建，扫描 `settings.gradle(.kts)` 中的子项目列表：
	   - `include(":app", ":lib", ":shared")` → 列出所有子项目名称
	   - 检查各子项目的 `build.gradle(.kts)` 以确定类型（application / library）
	4. 检测 Gradle 插件生态：
	   | 插件 | 推断信息 |
	   |------|---------|
	   | `java` / `java-library` | 基础 Java 项目 |
	   | `kotlin("jvm")` / `kotlin("multiplatform")` | Kotlin 项目 / Kotlin 多平台 |
	   | `application` | 可运行应用（含 main 类） |
	   | `org.springframework.boot` / `war` | Spring Boot 应用 / 部署方式 |
	   | `com.android.application` / `com.android.library` | Android 项目 |
	   | `org.jetbrains.kotlin.android` | Kotlin Android 项目 |
	   | `org.graalvm.buildtools.native` | GraalVM Native Image |
	   | `com.diffplug.spotless` | 代码格式化 |
	5. 检测 Gradle 缓存与性能配置：
	   - `gradle.properties` 中是否包含 `org.gradle.caching=true` / `org.gradle.parallel=true`
	   - `org.gradle.jvmargs` — Gradle 进程 JVM 参数
	   - 是否有自定义的 `init.gradle` 或 `gradle/init.d/` 脚本
	6. 检测 Gradle 版本目录（Version Catalog）：
	   - 是否存在 `gradle/libs.versions.toml`（Gradle 7.0+ 推荐依赖管理方式）
	   - 提取 `[versions]`、`[libraries]`、`[bundles]`、`[plugins]` 中的关键条目

### 步骤 4：测试框架与命令

检测测试目录和配置文件：

- 测试目录：`src/test/java/`（Java）、`tests/`、`test/`、`__tests__/`、`spec/`（Ruby）、`*_test.go`（Go）、`*.spec.ts` 等
- 测试配置：`pytest.ini`/`pyproject.toml[tool.pytest]`、`jest.config.*`、`.phpunit.xml`、`karma.conf.js`、`CTestTestfile.cmake`、`Catch2Config.cmake` 等
- 对 C/C++ 项目，额外检测：
  - `CMakeLists.txt` 中是否包含 `enable_testing()` 和 `add_test(...)`（CMake/CTest）
  - 是否链接了 GoogleTest（`GTest::gtest` / `gtest` / `GTest::gmock`）、Catch2（`Catch2::Catch2`）、CppUTest、Unity、doctest、Boost.Test 等测试框架
  - `CMakeLists.txt` 中 `FetchContent` 或 `find_package` 拉取的测试框架（常见于 header-only 测试框架如 Catch2、doctest）
  - `*_test.cpp`、`*_test.cc`、`*_unittest.cpp`、`test_*.c`、`*_test.c`、`*Test.cpp`、`*.test.cpp` 等 C/C++ 测试文件命名模式
  - 是否存在 `tests/` 或 `test/` 目录下的独立 `CMakeLists.txt` 或 `Makefile`
  - Makefile 中是否包含 `test` 或 `check` 目标（用于非 CMake 项目的测试入口）
  - 是否使用了 `valgrind`、`AddressSanitizer`（`-fsanitize=address`）、`UndefinedBehaviorSanitizer`（`-fsanitize=undefined`）等运行时检测工具
- 从构建文件中提取测试依赖（如 pom.xml 中的 junit、CMakeLists.txt 中的 `find_package(GTest)`）

推断测试命令：
- Java/Maven：`mvn test`
- Java/Gradle（Wrapper）：`./gradlew test`
- Java/Gradle（系统安装）：`gradle test`
- Java/Gradle（多项目，特定子项目）：`./gradlew :<subproject>:test`
- Java/Gradle（并行测试）：`./gradlew test -Dorg.gradle.workers.max=<N>`
- Kotlin/Gradle：`./gradlew test`
- Kotlin/Gradle（Kotlin 多平台）：`./gradlew allTests`
- Python/pytest：`pytest --cov -n auto`
- Node.js：`npm test` / `jest`
- Go：`go test ./...`
- Python/pytest：`pytest --cov -n auto`
- Node.js：`npm test` / `jest`
- Go：`go test ./...`
- C/C++ (CMake + CTest)：`cd build && ctest --output-on-failure`
- C/C++ (CMake + CTest 并行)：`cd build && ctest -j$(nproc) --output-on-failure`
- C/C++ (CMake + CMakePresets)：`cd build && ctest --preset default`
- C/C++ (Makefile 含 test 目标)：`make test`
- C/C++ (Makefile 含 check 目标)：`make check`
- C/C++ (Autotools)：`make check`
- C/C++ (Meson)：`meson test -C build`
- C/C++ (Bazel)：`bazel test //...`
- C/C++ (Xmake)：`xmake test`
- C/C++ (header-only 库)：`cd build && ctest --output-on-failure`（仅测试，无编译步骤）
- C/C++ (GTest 独立可执行)：`./build/tests/<test_binary>` 或 `./build/test_*`

### 步骤 5：代码风格与检查工具

检测以下配置文件的存在性：

| 配置类型 | 文件示例 |
|---------|---------|
| Lint | `.eslintrc*`, `.pylintrc`, `checkstyle.xml`, `.golangci.yml`, `.rubocop.yml`, `.clang-tidy`, `CPPLINT.cfg` |
| Formatter | `.clang-format`, `.prettierrc*`, `.editorconfig`, `pyproject.toml` 中的 `[tool.black]` / `[tool.ruff]` |
| 静态分析（C/C++） | `cppcheck` 配置（`.cppcheck` / `cppcheck.xml`）、`clang-tidy` 配置 |
| 类型检查 | `mypy.ini`, `tsconfig.json` (strict), `pyrightconfig.json` |
| 拼写检查 | `.cspell.json`, `.codespellrc` |

### 步骤 6：CI/CD 流水线

检测 CI 配置文件：
- `.github/workflows/` — 列出所有 workflow 文件，提取 job 名称
- `.gitlab-ci.yml` — 列出 stage 和 job
- `Jenkinsfile` — 检测 pipeline 结构
- `azure-pipelines.yml` — 列出 stage
- `.circleci/config.yml` — 列出 job
- `bitbucket-pipelines.yml` — 列出 step

对于检测到的 CI 配置，读取内容并提取关键阶段（如 build、test、lint、deploy）。

### 步骤 7：提交规范

运行 `git log --oneline -20` 分析提交信息格式。

判定标准：
- **Conventional Commits** — 大部分提交以 `feat:` / `fix:` / `chore:` / `docs:` / `refactor:` 等开头
- **自定义规范** — 有规律性的前缀模式但不符合 Conventional Commits（如 `[JIRA-123]`）
- **无规范** — 提交信息格式不一，无固定模式

提取 3-5 条典型提交作为示例。

### 步骤 8：展示诊断摘要并确认

将以上所有采集结果汇总为以下格式展示：

```
🔍 代码仓画像

语言分布：
  Java      12,541 行  219 文件  57.5%
  Python     1,264 行   13 文件   5.8%
  ...

根模块（N 个）：
  path/to/module1/     service     276 文件  ~12,500 行  <一句话描述>
  path/to/module2/     service      18 文件  ~1,300 行  <一句话描述>

叶子模块（M 个）：
  path/to/leaf1/       adapter       6 文件  ~500 行  <一句话描述>
  path/to/leaf2/       test          4 文件  ~200 行  <一句话描述>

构建：
  module1 → cmake -B build && cmake --build build
  module2 → mvn clean package -f module2/pom.xml
  （module3 未检测到构建文件 — 可能是 header-only C 库）

测试：
  module1 → cd build && ctest --output-on-failure
  module2 → pytest --cov -n auto
  （module3 未检测到测试框架）

代码检查：<检测到的工具列表，或"未检测到">

CI/CD：
  <流水线摘要，或"未检测到 CI 配置">

提交规范：
  Conventional Commits（示例：feat: add xxx, fix: correct yyy）
```

然后向用户提问：
1. "各模块的类型判定和描述是否准确？是否有需要跳过或重新归类的模块？"
2. "主构建命令和测试命令是否正确？"
3. "是否有未检测到的 CI 流水线或代码检查工具？"

## 输出与持久化

用户确认（并完成修正）后：
1. **将最终确认的画像写入项目仓库**：创建 `.aidoc/phase0/` 目录，将画像数据写入 `.aidoc/phase0/repo-profile.md`
2. 文件格式为 Markdown，包含以下内容：
   - 语言分布（表格：语言、代码行数、文件数、占比）
   - 根模块列表（表格：路径、类型、文件数、代码行数、描述）
   - 叶子模块列表（表格：路径、类型、文件数、代码行数、描述）
   - 构建命令（每个模块的构建命令）
   - 测试命令（每个模块的测试命令）
   - 代码检查工具列表（或"未检测到"）
   - CI/CD 流水线摘要（或"未检测到 CI 配置"）
   - 提交规范判定及示例
3. 告知用户："画像已写入 `.aidoc/phase0/repo-profile.md`，下游 skill（如 aidoc-create）可直接读取使用。"
4. 在使用 `aidoc-create` 或类似下游 skill 时，先检查 `.aidoc/phase0/repo-profile.md` 是否存在，避免重复采集

## 注意事项

- 优先并行执行独立的探索步骤（如 tokei 可以和 ls 并发）
- 对不确定的判定（如模块类型），标注为 `[? 待确认]` 而非猜测后直接确认
- 如果仓库特别大（> 50 万行），先做顶层探索，在确认阶段让用户指定需要深入分析的范围
- 不要在仓库中生成任何中间文件（JSON、YAML 等），所有结果直接在对话中展示
