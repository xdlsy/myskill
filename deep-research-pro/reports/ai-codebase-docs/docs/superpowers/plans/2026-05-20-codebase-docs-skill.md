# codebase-docs Skill 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建 `codebase-docs` Claude Code Skill，为百万级存量代码仓自动生成根 AGENTS.md 和子模块 AGENTS.md

**Architecture:** Skill 编排 4 个 Phase（采集→根入口→子模块入口→Code Map），collect.sh 做结构化数据采集输出 codebase-profile.json，Claude 读 profile + 目标仓库关键文件合成文档

**Tech Stack:** Shell (collect.sh), Claude Code Skill (SKILL.md as orchestrator), tokei (LOC 统计), 语言特化工具按需（cmake/gomod/mvn/pydeps）

**MVP 范围:** Phase 0, 1, 2 + collect.sh。Phase 3 (ARCHITECTURE.md) 延后，claude-sync 为独立 skill

---

### Task 1: 项目脚手架

**Files:**
- Create: `skills/codebase-docs/SKILL.md`（骨架）
- Create: `skills/codebase-docs/scripts/collect.sh`（骨架）
- Create: `skills/codebase-docs/templates/root-agents.tmpl.md`
- Create: `skills/codebase-docs/templates/module-agents.tmpl.md`

- [ ] **Step 1: 创建目录结构**

```bash
mkdir -p skills/codebase-docs/scripts
mkdir -p skills/codebase-docs/templates
```

- [ ] **Step 2: 写 SKILL.md 骨架（frontmatter + 概述）**

```markdown
---
name: codebase-docs
description: Use when generating AI-friendly entry documentation (AGENTS.md) for existing codebases, especially large or multi-module repositories. Triggered by "generate entry files", "create AGENTS.md", or "document this codebase for AI agents".
---

# codebase-docs

## Overview

Generate structured AGENTS.md files for existing codebases by first collecting structured data via a shell script, then synthesizing documentation through interactive Claude-driven phases.

## When to Use

- Adding AI agent entry documentation to an existing project
- Onboarding a new repository for AI-assisted development
- Generating per-module AGENTS.md files in a monorepo
- Bootstrapping documentation for a codebase with 100K+ lines

## Prerequisites

- `tokei` installed (`brew install tokei` / `cargo install tokei`)
- `jq` installed (`brew install jq`)
- Run from the target repository root
```

- [ ] **Step 3: 写 collect.sh 骨架**

```bash
#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-.}"
OUTPUT="${2:-codebase-profile.json}"

echo "=== codebase-docs: collect ===" >&2
echo "Repo: $(cd "$REPO_ROOT" && pwd)" >&2

# detect_language
# scan_directory
# extract_build
# extract_style
# extract_ci
# extract_git
# extract_tests
# extract_deps
# write_profile

echo "TODO: full implementation" >&2
```

- [ ] **Step 4: 写两个模板文件的占位内容**

`templates/root-agents.tmpl.md`:
```markdown
# {{PROJECT_NAME}}

## Project Overview [~ inferred]
{{OVERVIEW}}

## Repository Structure [✓ auto]
```
{{STRUCTURE_TREE}}
```
{{MODULE_DESCRIPTIONS}}

## Build & Test Commands [✓ auto]
```bash
# Build
{{BUILD_COMMANDS}}

# Test
{{TEST_COMMANDS}}

# Lint
{{LINT_COMMANDS}}
```

## Coding Style [✓ auto]
{{STYLE_RULES}}

## Testing Guidelines [✓ auto]
- Framework: {{TEST_FRAMEWORK}}
- Test locations: {{TEST_DIRS}}
- File patterns: {{FILE_PATTERNS}}

## Commit & PR Guidelines [✓ auto]
- Format: {{COMMIT_FORMAT}}
{{COMMIT_EXAMPLES}}
- CI pipeline: {{CI_STAGES}}

## Do Not / Gotchas [? review]
<!-- HUMAN_REVIEW: 请填写本项目特有的禁止事项和常见陷阱 -->
{{AUTO_DETECTED_INVARIANTS}}
```

`templates/module-agents.tmpl.md`:
```markdown
# {{MODULE_NAME}}

## Responsibility [~ inferred]
{{RESPONSIBILITY}}

## Conventions [~ inferred]
{{CONVENTIONS}}
<!-- HUMAN_REVIEW: 请补充本模块特有的编码约定和禁止事项 -->

## Dependencies [? review]
- Depends on: {{DEPS_LIST}}
- Depended on by: {{REVERSE_DEPS_LIST}}
```

- [ ] **Step 5: Commit**

```bash
git add skills/codebase-docs/ templates/
git commit -m "feat: scaffold codebase-docs skill with templates"
```

---

### Task 2: collect.sh — 语言探测 + 目录拓扑

**Files:**
- Modify: `skills/codebase-docs/scripts/collect.sh`

- [ ] **Step 1: 实现 detect_language()**

```bash
detect_language() {
    local repo="$1"
    local langs=()

    [[ -f "$repo/go.mod" ]] && langs+=("go")
    [[ -f "$repo/pom.xml" || -f "$repo/build.gradle" || -f "$repo/build.gradle.kts" ]] && langs+=("java")
    [[ -f "$repo/CMakeLists.txt" ]] && langs+=("cpp")
    [[ -f "$repo/pyproject.toml" || -f "$repo/setup.py" || -f "$repo/setup.cfg" ]] && langs+=("python")

    # Fallback: extension heuristics
    if [[ ${#langs[@]} -eq 0 ]]; then
        local ext_counts
        ext_counts=$(find "$repo" -maxdepth 3 -type f \( -name "*.go" -o -name "*.java" -o -name "*.cpp" -o -name "*.cc" -o -name "*.py" \) 2>/dev/null | sed 's/.*\.//' | sort | uniq -c | sort -rn)
        local top_ext=$(echo "$ext_counts" | head -1 | awk '{print $2}')
        case "$top_ext" in
            go) langs+=("go") ;;
            java) langs+=("java") ;;
            cpp|cc|cxx) langs+=("cpp") ;;
            py) langs+=("python") ;;
        esac
    fi

    local primary="${langs[0]:-unknown}"
    echo "{\"primary_language\":\"$primary\",\"languages\":$(printf '%s\n' "${langs[@]}" | jq -R -s -c 'split("\n") | map(select(length>0))')}"
}
```

- [ ] **Step 2: 实现 scan_directory() 和 scan_leaf_modules()**

```bash
scan_root_modules() {
    local repo="$1"
    local modules="["
    local first=true

    for dir in $(find "$repo" -maxdepth 1 -type d \
        ! -name '.' ! -name '.git' ! -name 'node_modules' \
        ! -name 'vendor' ! -name 'target' ! -name 'build' \
        ! -name 'dist' ! -name '.claude' ! -name '__pycache__' | sort); do

        local name=$(basename "$dir")
        local file_count=$(find "$dir" -type f ! -path '*/.git/*' ! -path '*/node_modules/*' 2>/dev/null | wc -l | tr -d ' ')
        [[ $file_count -eq 0 ]] && continue

        local mtype="unknown"
        case "$name" in
            cmd|main|app|apps) mtype="app-entry" ;;
            internal|pkg|lib|libs|core|shared|common|packages) mtype="private-lib" ;;
            test|tests|e2e|integration) mtype="test" ;;
            docs|doc) mtype="docs" ;;
            deploy|infra|infrastructure|terraform|k8s|ci|.github) mtype="infrastructure" ;;
            api|service|services|server|handler|controller) mtype="service" ;;
            model|domain|entity|entities|repository|store|db) mtype="domain" ;;
        esac

        [[ "$first" == "false" ]] && modules+=","
        modules+="{\"path\":\"$name/\",\"type\":\"$mtype\",\"loc\":0,\"files\":$file_count}"
        first=false
    done
    modules+="]"
    echo "$modules"
}

scan_leaf_modules() {
    local repo="$1"
    local modules="["
    local first=true

    for dir in $(find "$repo" -mindepth 2 -maxdepth 3 -type d \
        ! -path '*/.git/*' ! -path '*/node_modules/*' ! -path '*/vendor/*' \
        ! -path '*/target/*' ! -path '*/build/*' ! -path '*/dist/*' \
        ! -path '*/test/*' ! -path '*/tests/*' ! -path '*/__pycache__/*' \
        ! -path '*/.venv/*' ! -path '*/venv/*' | sort); do

        local rel="${dir#$repo/}"
        local has_build=false
        [[ -f "$dir/go.mod" || -f "$dir/pom.xml" || -f "$dir/build.gradle" || \
           -f "$dir/CMakeLists.txt" || -f "$dir/pyproject.toml" || \
           -f "$dir/Makefile" || -f "$dir/package.json" ]] && has_build=true

        local src_count=$(find "$dir" -maxdepth 1 -type f \
            \( -name "*.go" -o -name "*.java" -o -name "*.py" -o -name "*.cpp" -o -name "*.c" \) 2>/dev/null | wc -l | tr -d ' ')

        if [[ "$has_build" == "true" || $src_count -ge 3 ]]; then
            local file_count=$(find "$dir" -type f ! -path '*/.git/*' 2>/dev/null | wc -l | tr -d ' ')
            local lang=$(detect_dir_language "$dir")
            local mtype=$(infer_dir_type "$rel")

            [[ "$first" == "false" ]] && modules+=","
            modules+="{\"path\":\"$rel/\",\"language\":\"$lang\",\"type\":\"$mtype\",\"loc\":0,\"files\":$file_count,\"inferred_responsibility\":null}"
            first=false
        fi
    done
    modules+="]"
    echo "$modules"
}

detect_dir_language() {
    local dir="$1"
    [[ -f "$dir/go.mod" ]] && { echo "go"; return; }
    [[ -f "$dir/pom.xml" || -f "$dir/build.gradle" ]] && { echo "java"; return; }
    [[ -f "$dir/CMakeLists.txt" ]] && { echo "cpp"; return; }
    [[ -f "$dir/pyproject.toml" || -f "$dir/setup.py" ]] && { echo "python"; return; }
    local ext=$(find "$dir" -maxdepth 2 -type f \( -name "*.go" -o -name "*.java" -o -name "*.py" -o -name "*.cpp" \) 2>/dev/null | head -1)
    case "$ext" in
        *.go) echo "go" ;;
        *.java) echo "java" ;;
        *.py) echo "python" ;;
        *.cpp|*.c|*.cc) echo "cpp" ;;
        *) echo "unknown" ;;
    esac
}

infer_dir_type() {
    local path="$1"
    case "$(basename "$path")" in
        cmd|main|app) echo "app-entry" ;;
        internal|core|domain|model|entity) echo "domain" ;;
        api|service|handler|controller|server|grpc|http|rest) echo "service" ;;
        adapter|connector|client|gateway|proxy) echo "adapter" ;;
        infra|config|deploy|monitoring|logging|common|shared|util|utils) echo "infrastructure" ;;
        *) echo "unknown" ;;
    esac
}
```

- [ ] **Step 3: Commit**

```bash
git add skills/codebase-docs/scripts/collect.sh
git commit -m "feat(collect): add language detection and directory scanning"
```

---

### Task 3: collect.sh — 构建系统提取

**Files:**
- Modify: `skills/codebase-docs/scripts/collect.sh`

- [ ] **Step 1: 实现 extract_build() 及四种语言子函数**

```bash
extract_build() {
    local repo="$1"
    local lang="$2"
    local cmds="["

    case "$lang" in
        go)
            cmds+="{\"scope\":\"root\",\"cmd\":\"go build ./...\",\"cwd\":\".\"}"
            cmds+=",{\"scope\":\"root\",\"cmd\":\"go vet ./...\",\"cwd\":\".\"}"
            # Extract Makefile targets if present
            if [[ -f "$repo/Makefile" ]]; then
                local targets=$(grep -oE '^[a-zA-Z_-]+:' "$repo/Makefile" | tr -d ':' | grep -E '^(build|test|lint|fmt|run|dev|setup)$' | tr '\n' ',' | sed 's/,$//')
                if [[ -n "$targets" ]]; then
                    cmds+=",{\"scope\":\"root\",\"cmd\":\"make [$targets]\",\"cwd\":\".\"}"
                fi
            fi
            ;;
        java)
            if [[ -f "$repo/pom.xml" ]]; then
                cmds+="{\"scope\":\"root\",\"cmd\":\"mvn clean compile\",\"cwd\":\".\"}"
                cmds+=",{\"scope\":\"root\",\"cmd\":\"mvn test\",\"cwd\":\".\"}"
                grep -q '<modules>' "$repo/pom.xml" 2>/dev/null && \
                    cmds+=",{\"scope\":\"module\",\"cmd\":\"mvn clean install -pl <module> -am\",\"cwd\":\".\"}"
            elif [[ -f "$repo/build.gradle" || -f "$repo/build.gradle.kts" ]]; then
                cmds+="{\"scope\":\"root\",\"cmd\":\"./gradlew build\",\"cwd\":\".\"}"
                cmds+=",{\"scope\":\"root\",\"cmd\":\"./gradlew test\",\"cwd\":\".\"}"
            fi
            ;;
        cpp)
            if [[ -f "$repo/CMakeLists.txt" ]]; then
                cmds+="{\"scope\":\"root\",\"cmd\":\"cmake -B build && cmake --build build\",\"cwd\":\".\"}"
                cmds+="{\"scope\":\"root\",\"cmd\":\"cmake --build build --target test\",\"cwd\":\".\"}"
            elif [[ -f "$repo/Makefile" ]]; then
                cmds+="{\"scope\":\"root\",\"cmd\":\"make\",\"cwd\":\".\"}"
                cmds+="{\"scope\":\"root\",\"cmd\":\"make test\",\"cwd\":\".\"}"
            fi
            ;;
        python)
            if [[ -f "$repo/pyproject.toml" ]]; then
                if grep -q '\[tool.poetry\]' "$repo/pyproject.toml" 2>/dev/null; then
                    cmds+="{\"scope\":\"root\",\"cmd\":\"poetry install\",\"cwd\":\".\"}"
                    cmds+="{\"scope\":\"root\",\"cmd\":\"poetry run pytest\",\"cwd\":\".\"}"
                else
                    cmds+="{\"scope\":\"root\",\"cmd\":\"pip install -e '.[dev]'\",\"cwd\":\".\"}"
                    cmds+="{\"scope\":\"root\",\"cmd\":\"pytest\",\"cwd\":\".\"}"
                fi
            elif [[ -f "$repo/setup.py" || -f "$repo/setup.cfg" ]]; then
                cmds+="{\"scope\":\"root\",\"cmd\":\"pip install -e '.[dev]'\",\"cwd\":\".\"}"
                cmds+="{\"scope\":\"root\",\"cmd\":\"pytest\",\"cwd\":\".\"}"
            fi
            ;;
    esac

    cmds+="]"
    echo "\"build_commands\": $cmds"
}
```

- [ ] **Step 2: Commit**

```bash
git add skills/codebase-docs/scripts/collect.sh
git commit -m "feat(collect): add build command extraction for go/java/cpp/python"
```

---

### Task 4: collect.sh — 代码风格 + CI + Git + 测试

**Files:**
- Modify: `skills/codebase-docs/scripts/collect.sh`

- [ ] **Step 1: 实现 extract_style()**

```bash
extract_style() {
    local repo="$1"
    shift
    local langs=("$@")
    local rules="{}"

    for lang in "${langs[@]}"; do
        case "$lang" in
            go)
                if [[ -f "$repo/.golangci.yml" ]]; then
                    rules=$(echo "$rules" | jq '.go = {"formatter":"go fmt","linter":"golangci-lint"}')
                else
                    rules=$(echo "$rules" | jq '.go = {"formatter":"go fmt"}')
                fi ;;
            java)
                [[ -f "$repo/checkstyle.xml" ]] && rules=$(echo "$rules" | jq '.java = {"linter":"checkstyle"}') ;;
            cpp)
                if [[ -f "$repo/.clang-format" ]]; then
                    local base=$(grep "BasedOnStyle" "$repo/.clang-format" | awk '{print $2}')
                    rules=$(echo "$rules" | jq --arg style "$base" '.cpp = {"formatter":"clang-format","base_style":$style}')
                fi
                [[ -f "$repo/.clang-tidy" ]] && rules=$(echo "$rules" | jq '.cpp.linter = "clang-tidy"') ;;
            python)
                if grep -q '\[tool.ruff\]' "$repo/pyproject.toml" 2>/dev/null; then
                    rules=$(echo "$rules" | jq '.python = {"linter":"ruff"}')
                elif grep -q '\[tool.black\]' "$repo/pyproject.toml" 2>/dev/null; then
                    rules=$(echo "$rules" | jq '.python = {"formatter":"black"}')
                fi ;;
        esac
    done

    echo "\"style_rules\": $rules"
}
```

- [ ] **Step 2: 实现 extract_ci()**

```bash
extract_ci() {
    local repo="$1"
    local pipeline="["

    if [[ -d "$repo/.github/workflows" ]]; then
        for yml in "$repo/.github/workflows"/*.yml "$repo/.github/workflows"/*.yaml; do
            [[ ! -f "$yml" ]] && continue
            local name=$(grep -m1 '^name:' "$yml" | sed 's/.*name:\s*//;s/"//g')
            local steps=$(grep -E '^\s+run:' "$yml" | sed 's/.*run:\s*//' | tr '\n' '|')
            pipeline+="{\"stage\":\"$name\",\"steps\":\"$steps\"},"
        done
    fi

    [[ -f "$repo/.gitlab-ci.yml" ]] && pipeline+="{\"source\":\"gitlab-ci\"},"

    pipeline="${pipeline%,}]"
    echo "\"ci_pipeline\": $pipeline"
}
```

- [ ] **Step 3: 实现 extract_git()**

```bash
extract_git() {
    local repo="$1"
    local convention="unknown"
    local samples="[]"

    if git -C "$repo" log --oneline -20 2>/dev/null | grep -qE '^(feat|fix|chore|docs|refactor|test|ci)(\(.+\))?:'; then
        convention="conventional-commits"
        samples=$(git -C "$repo" log --oneline -5 --format="%s" 2>/dev/null | grep -E '^(feat|fix|chore|docs|refactor)' | jq -R -s -c 'split("\n") | map(select(length>0))')
    fi

    echo "\"commit_convention\":{\"style\":\"$convention\",\"sample\":$samples}"

    # CODEOWNERS
    local owners_file=""
    [[ -f "$repo/.github/CODEOWNERS" ]] && owners_file="$repo/.github/CODEOWNERS"
    [[ -f "$repo/CODEOWNERS" ]] && owners_file="$repo/CODEOWNERS"
    if [[ -n "$owners_file" ]]; then
        local owners=$(grep -v '^#' "$owners_file" | grep -v '^$' | awk '{print $1, $NF}' | jq -R -s -c 'split("\n") | map(select(length>0) | split(" ") | {path: .[0], owner: .[1]})')
        echo ",\"code_owners\": $owners"
    fi
}
```

- [ ] **Step 4: 实现 extract_tests()**

```bash
extract_tests() {
    local repo="$1"
    local lang="$2"
    local framework="unknown"
    local cmds="[]"
    local dirs="[]"

    # Test directories
    dirs=$(find "$repo" -maxdepth 2 -type d \( -name "test" -o -name "tests" -o -name "__tests__" -o -name "spec" \) ! -path '*node_modules*' 2>/dev/null | sed "s|$repo/||" | jq -R -s -c 'split("\n") | map(select(length>0))')

    # File patterns
    local patterns="[]"
    case "$lang" in
        go)
            framework="go test"
            cmds="[{\"scope\":\"root\",\"cmd\":\"go test -race -coverprofile=coverage.out ./...\",\"cwd\":\".\"}]"
            patterns='["*_test.go"]' ;;
        java)
            framework="JUnit"
            cmds="[{\"scope\":\"root\",\"cmd\":\"mvn test\",\"cwd\":\".\"}]"
            patterns='["*Test.java","*Tests.java"]' ;;
        cpp)
            grep -qE '(GTest|gtest)' "$repo/CMakeLists.txt" 2>/dev/null && framework="GoogleTest"
            cmds="[{\"scope\":\"root\",\"cmd\":\"cmake --build build --target test\",\"cwd\":\".\"}]"
            patterns='["*_test.cpp","*_test.cc"]' ;;
        python)
            framework="pytest"
            cmds="[{\"scope\":\"root\",\"cmd\":\"pytest --cov -n auto\",\"cwd\":\".\"}]"
            patterns='["test_*.py","*_test.py"]' ;;
    esac

    echo "\"test\":{\"framework\":\"$framework\",\"commands\":$cmds,\"test_dirs\":$dirs,\"file_patterns\":$patterns}"
}
```

- [ ] **Step 5: Commit**

```bash
git add skills/codebase-docs/scripts/collect.sh
git commit -m "feat(collect): add style, CI, git, and test extraction"
```

---

### Task 5: collect.sh — 依赖关系 + profile 组装

**Files:**
- Modify: `skills/codebase-docs/scripts/collect.sh`

- [ ] **Step 1: 实现 extract_deps() 及四种语言子函数**

```bash
extract_deps() {
    local repo="$1"
    local lang="$2"
    local graph="{}"

    case "$lang" in
        go) graph=$(extract_go_deps "$repo") ;;
        java) graph=$(extract_java_deps "$repo") ;;
        python) graph=$(extract_python_deps "$repo") ;;
        cpp) graph=$(extract_cpp_deps "$repo") ;;
    esac

    echo "\"build_dependencies\": $graph"
}

extract_go_deps() {
    local repo="$1"
    local graph="{}"
    if ! command -v go &>/dev/null || [[ ! -f "$repo/go.mod" ]]; then echo "$graph"; return; fi

    local mod=$(grep "^module " "$repo/go.mod" | awk '{print $2}')
    [[ -z "$mod" ]] && { echo "$graph"; return; }

    for dir in $(find "$repo" -maxdepth 3 -type d ! -path '*/.git/*' ! -path '*/vendor/*' | sort); do
        local rel="${dir#$repo/}"
        local imports=$(grep -rh "\"$mod/" "$dir" --include="*.go" 2>/dev/null | \
            grep -o "\"$mod/[^\"]*\"" | sed "s|\"$mod/||;s|\"||" | sort -u | grep -v "^$rel" | tr '\n' ',' | sed 's/,$//')
        [[ -n "$imports" ]] && graph=$(echo "$graph" | jq --arg p "$rel/" --argjson d "$(echo "$imports" | jq -R -s -c 'split(",") | map(select(length>0))')" '. + {($p): $d}')
    done
    echo "$graph"
}

extract_java_deps() {
    local repo="$1"
    local graph="{}"
    [[ ! -f "$repo/pom.xml" ]] && { echo "$graph"; return; }

    local groupId=$(grep -A2 '<groupId>' "$repo/pom.xml" | head -3 | grep -oP '<groupId>\K[^<]+' | head -1)
    [[ -z "$groupId" ]] && { echo "$graph"; return; }

    for pom in $(find "$repo" -name "pom.xml" ! -path '*/target/*' 2>/dev/null); do
        local rel=$(dirname "${pom#$repo/}")
        [[ "$rel" == "." ]] && continue
        local deps=$(grep "<groupId>$groupId</groupId>" "$pom" -A1 | grep "<artifactId>" | grep -oP '<artifactId>\K[^<]+' | tr '\n' ',' | sed 's/,$//')
        [[ -n "$deps" ]] && graph=$(echo "$graph" | jq --arg p "$rel/" --argjson d "$(echo "$deps" | jq -R -s -c 'split(",") | map(select(length>0))')" '. + {($p): $d}')
    done
    echo "$graph"
}

extract_python_deps() {
    local repo="$1"
    local graph="{}"
    local pkg=""
    [[ -f "$repo/pyproject.toml" ]] && pkg=$(grep -A5 '\[project\]' "$repo/pyproject.toml" | grep 'name' | grep -oP '"\K[^"]+' | head -1)
    [[ -z "$pkg" ]] && { echo "$graph"; return; }

    for dir in $(find "$repo" -maxdepth 3 -type d ! -path '*/__pycache__/*' ! -path '*/.venv/*' ! -path '*/venv/*' | sort); do
        local rel="${dir#$repo/}"
        local imports=$(grep -rh "from $pkg\." "$dir" --include="*.py" 2>/dev/null | \
            grep -oP "from $pkg\.\K[^\s.]+" | sort -u | tr '\n' ',' | sed 's/,$//')
        [[ -n "$imports" ]] && graph=$(echo "$graph" | jq --arg p "$rel/" --argjson d "$(echo "$imports" | jq -R -s -c 'split(",") | map(select(length>0))')" '. + {($p): $d}')
    done
    echo "$graph"
}

extract_cpp_deps() {
    local repo="$1"
    local graph="{}"

    # Try cmake --graphviz first
    if [[ -d "$repo/build" ]] && command -v cmake &>/dev/null; then
        cmake --graphviz="$repo/build/_deps.dot" "$repo" 2>/dev/null || true
        if [[ -f "$repo/build/_deps.dot" ]]; then
            local edges=$(grep '->' "$repo/build/_deps.dot" | sed 's/.*"\(.*\)" -> "\(.*\)".*/"\1":"\2"/' | tr '\n' ',' | sed 's/,$//')
            [[ -n "$edges" ]] && graph="{$edges}"
        fi
    fi

    # Fallback: grep #include for internal headers
    if [[ "$graph" == "{}" ]]; then
        for dir in $(find "$repo" -maxdepth 3 -type d ! -path '*/build/*' | sort); do
            local rel="${dir#$repo/}"
            local incs=$(grep -rh '#include "' "$dir" --include="*.cpp" --include="*.h" --include="*.hpp" 2>/dev/null | \
                grep -oP '#include "\K[^"]+' | grep -v '^\.\./' | sort -u | tr '\n' ',' | sed 's/,$//')
            [[ -n "$incs" ]] && graph=$(echo "$graph" | jq --arg p "$rel/" --argjson d "$(echo "$incs" | jq -R -s -c 'split(",") | map(select(length>0))')" '. + {($p): $d}')
        done
    fi
    echo "$graph"
}
```

- [ ] **Step 2: 实现 write_profile() 和 main()**

```bash
write_profile() {
    local repo="$1"
    local output="$2"

    local lang_json=$(detect_language "$repo")
    local primary=$(echo "$lang_json" | jq -r '.primary_language')
    local langs_arr=$(echo "$lang_json" | jq -r '.languages[]')

    local total_loc=0
    command -v tokei &>/dev/null && total_loc=$(cd "$repo" && tokei --output json 2>/dev/null | jq '[.[].code] | add // 0' || echo 0)

    local root_mods=$(scan_root_modules "$repo")
    local leaf_mods=$(scan_leaf_modules "$repo")
    local leaf_count=$(echo "$leaf_mods" | jq 'length')
    local build=$(extract_build "$repo" "$primary")
    local style=$(extract_style "$repo" $langs_arr)
    local test=$(extract_tests "$repo" "$primary")
    local ci=$(extract_ci "$repo")
    local git_data=$(extract_git "$repo")
    local deps=$(extract_deps "$repo" "$primary")

    cat > "$output" <<ENDOFJSON
{
  "meta": {
    "repo_root": "$(cd "$repo" && pwd)",
    "primary_language": "$primary",
    "languages": $(echo "$lang_json" | jq '.languages'),
    "total_loc": $total_loc,
    "module_count": $leaf_count,
    "collected_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  },
  "directory_tree": {
    "root_modules": $root_mods,
    "leaf_modules": $leaf_mods
  },
  $build,
  $style,
  $test,
  $ci,
  $git_data,
  $deps
}
ENDOFJSON

    echo "Profile written to $output ($(wc -c < "$output") bytes)" >&2
}

main() {
    local repo="${1:-.}"
    local output="${2:-codebase-profile.json}"

    if ! command -v jq &>/dev/null; then
        echo "ERROR: jq is required. Install with: brew install jq" >&2
        exit 1
    fi
    command -v tokei &>/dev/null || echo "WARNING: tokei not installed. Install with: brew install tokei" >&2

    write_profile "$repo" "$output"
}

main "$@"
```

- [ ] **Step 3: 添加可执行权限并 Commit**

```bash
chmod +x skills/codebase-docs/scripts/collect.sh
git add skills/codebase-docs/scripts/collect.sh
git commit -m "feat(collect): add dependency extraction and profile assembly"
```

---

### Task 6: SKILL.md — Phase 0 与 Phase 1

**Files:**
- Modify: `skills/codebase-docs/SKILL.md`

- [ ] **Step 1: 替换 SKILL.md 为完整内容（含 Phase 0 + Phase 1）**

```markdown
---
name: codebase-docs
description: Use when generating AI-friendly entry documentation (AGENTS.md) for existing codebases, especially large or multi-module repositories. Triggered by "generate entry files", "create AGENTS.md", or "document this codebase for AI agents". Also use when bootstrapping AI onboarding docs for a brownfield project.
---

# codebase-docs

## Overview

Generate structured AGENTS.md files for existing codebases. Two-step pipeline: (1) run `scripts/collect.sh` to produce `codebase-profile.json`, (2) Claude reads profile + key source files to synthesize documentation through interactive phases.

**This skill generates tool-agnostic content only.** CLAUDE.md and `.claude/rules/` are handled by the separate `claude-sync` skill. Run claude-sync as the final step after all AGENTS.md files are in place.

## When to Use

- Adding AI agent entry documentation to an existing project
- Onboarding a new repository for AI-assisted development
- Generating per-module AGENTS.md files in a monorepo
- Bootstrapping documentation for a codebase with 100K+ lines

## Prerequisites

- `tokei` installed (LOC stats): `brew install tokei`
- `jq` installed (JSON processing): `brew install jq`
- Run from the target repository root

## Workflow

### Phase 0: Collect & Confirm

1. Run the collection script in the target repository:
   ```bash
   bash <path-to-skill>/scripts/collect.sh . codebase-profile.json
   ```

2. Read the generated `codebase-profile.json` and present a diagnostic summary:

```
Detected: <primary_language> repo, ~<total_loc> lines
├── Root modules: <N> (<type1>: X, <type2>: Y, ...)
├── Leaf modules: <M>
├── Build: <primary build command>
├── Test: <framework> — <test command>
├── Lint: <tools>
└── CI: <N> pipeline stages
```

3. Ask user to confirm or correct:
   - "Does this look right? Any modules to skip or re-categorize?"
   - "Is the primary build command correct?"

4. If the user corrects anything, update profile.json with the corrections before proceeding.

### Phase 1: Root AGENTS.md

Generate root `AGENTS.md` (80-150 lines). Use the templates in `templates/` as structural reference.

**Data-to-section mapping:**

| Section | Source | When |
|---------|--------|------|
| **Project Overview** | README.md (read if exists) + directory tree inference | Always |
| **Build & Test Commands** | build_commands + test.commands | Always |
| **Coding Style** | style_rules | Only if lint config detected |
| **Testing Guidelines** | test.framework + test_dirs + file_patterns | Always |
| **Commit & PR Guidelines** | commit_convention + ci_pipeline | Only if convention detected |
| **Do Not / Gotchas** | — | Always (with `<!-- HUMAN_REVIEW -->` placeholder) |
| **Repository Structure** | directory_tree + build_dependencies | Always |

**For Do Not / Gotchas:** Auto-detect obvious invariants from module types:
- "`internal/` modules must not be imported by external packages" (Go)
- "`domain/` packages must not depend on `adapter/` packages" (Java)
- "`core/` must not import `apps/` modules" (monorepo)

Mark everything else with `<!-- HUMAN_REVIEW: ... -->`.

**Confidence annotations per section:**
- `[✓ auto]` — purely from profile data (e.g., build commands)
- `[~ inferred]` — AI interpretation (e.g., module descriptions)
- `[? review]` — placeholder, requires human input (e.g., Gotchas)

**After generation:** Present the full AGENTS.md for review. Accept inline corrections.

> CLAUDE.md is NOT generated here — it belongs to the `claude-sync` skill which runs after all AGENTS.md files are finalized.
```

- [ ] **Step 2: Commit**

```bash
git add skills/codebase-docs/SKILL.md
git commit -m "feat(skill): add Phase 0 and Phase 1 to SKILL.md"
```

---

### Task 7: SKILL.md — Phase 2（子模块入口）+ 完成指引

**Files:**
- Modify: `skills/codebase-docs/SKILL.md`

- [ ] **Step 1: 追加 Phase 2 到 SKILL.md**

```markdown
### Phase 2: Sub-Module AGENTS.md

Process each leaf module from `directory_tree.leaf_modules` one at a time.

**For each module:**

1. Read 2-3 representative files:
   - The largest source file (core logic)
   - The main export/interface file (public API)
   - Any file with doc comments (intent)

2. Infer module responsibility from:
   - Package/namespace names (e.g., `com.example.order` → "Order domain")
   - File-level comments and docstrings
   - Exported/public symbols (functions, classes, interfaces)
   - Cross-reference `code_owners` for team context

3. Present to user and confirm:

```
📦 internal/order/ (Java, 8,500 lines, 42 files)
   Inferred: Order domain model and state machine
   → [Y] Confirm / [n] Skip / [e] Edit description
```

4. After confirmation, generate `{module_path}/AGENTS.md` (30-50 lines):

```markdown
# {{MODULE_NAME}}

## Responsibility [~ inferred]
{{USER_CONFIRMED_RESPONSIBILITY}}

## Conventions [~ inferred]
{{AUTO_EXTRACTED_PATTERNS}}
<!-- HUMAN_REVIEW: add module-specific conventions and gotchas -->

## Dependencies [✓ auto]
- Depends on: {{DEPS}}
- Depended on by: {{REVERSE_DEPS}}
```

**Conventions auto-extraction rules:**
- Detect error handling patterns (exceptions vs. Result types vs. error codes)
- Detect naming conventions (camelCase vs. snake_case, prefix/suffix patterns)
- Detect architectural layering (controller → service → repository)
- If uncertain, leave `<!-- HUMAN_REVIEW -->`

**Batch optimization for repeated patterns:**
- When >3 modules share the same internal structure (e.g., controller/service/repository), offer: "These modules look structurally identical. Generate all automatically?"
- Always display each result — user can interrupt and correct any one

**Constraints:**
- 30-50 lines per module AGENTS.md
- Only write module-specific additions — do NOT repeat root AGENTS.md content (per AGENTS.md "closest wins" nesting semantics)
- Mark confidence per section

**After all modules processed:** present summary:

```
| # | Module | Responsibility | Status |
|---|--------|---------------|--------|
| 1 | internal/order/ | Order domain model | ✓ confirmed |
| 2 | internal/payment/ | Payment processing | ~ inferred |
| ... |
```

Ask: "Review the summary. Any modules to revisit before finishing?"
```

- [ ] **Step 2: 追加完成指引**

```markdown
## After Completion

1. Review all generated AGENTS.md files
2. Fill in all `<!-- HUMAN_REVIEW -->` placeholders
3. Run the `claude-sync` skill to generate:
   - `CLAUDE.md` (one-line `@AGENTS.md` bridge)
   - `.claude/rules/` files (global rules + module `@-import` indexes)
4. Commit all generated files

## File Constraints

| File | Max Lines | Confidence Annotation |
|------|-----------|----------------------|
| Root AGENTS.md | 80-150 | Per-section: `[✓ auto]` / `[~ inferred]` / `[? review]` |
| Module AGENTS.md | 30-50 | Per-section |
| ARCHITECTURE.md | ≤300 (Phase 3, deferred) | — |

## Idempotency

If a file already exists at the target path:
- Do NOT overwrite silently
- Show a diff between the existing file and the generated content
- Let the user choose: keep existing, merge, or replace
```

- [ ] **Step 3: Commit**

```bash
git add skills/codebase-docs/SKILL.md
git commit -m "feat(skill): add Phase 2 and completion guide to SKILL.md"
```

---

### Task 8: 集成验证

**Files:**
- None (verification only)

- [ ] **Step 1: 在当前项目上运行 collect.sh**

```bash
cd /Users/lsy/clawd/research/ai-codebase-docs
bash skills/codebase-docs/scripts/collect.sh . /tmp/test-profile.json
```

- [ ] **Step 2: 验证 profile.json 结构**

```bash
cat /tmp/test-profile.json | jq '.meta'
# Expected: primary_language + languages + total_loc + module_count + collected_at

cat /tmp/test-profile.json | jq '.directory_tree.root_modules[:3]'
# Expected: array with path, type, loc, files

cat /tmp/test-profile.json | jq '.build_commands[:3]'
# Expected: array with scope, cmd, cwd

cat /tmp/test-profile.json | jq '.test'
# Expected: framework + commands + test_dirs + file_patterns
```

- [ ] **Step 3: 验证 profile.json 为合法 JSON**

```bash
cat /tmp/test-profile.json | jq '.' > /dev/null && echo "VALID JSON" || echo "INVALID JSON"
# Expected: VALID JSON
```

- [ ] **Step 4: 修复问题并 Commit**

```bash
# Fix any issues found in Steps 2-3
git add skills/codebase-docs/
git commit -m "fix: integration test corrections"
```
