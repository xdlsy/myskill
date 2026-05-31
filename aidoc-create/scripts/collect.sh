#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-.}"
OUTPUT="${2:-codebase-profile.json}"

echo "=== aidoc-create: collect ===" >&2
echo "Repo: $(cd "$REPO_ROOT" && pwd)" >&2

# ── Language Detection ──────────────────────────────────────────────

detect_language() {
    local repo="$1"
    local langs=()

    [[ -f "$repo/go.mod" ]] && langs+=("go")
    [[ -f "$repo/pom.xml" || -f "$repo/build.gradle" || -f "$repo/build.gradle.kts" ]] && langs+=("java")
    [[ -f "$repo/CMakeLists.txt" ]] && langs+=("cpp")
    [[ -f "$repo/pyproject.toml" || -f "$repo/setup.py" || -f "$repo/setup.cfg" ]] && langs+=("python")

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
    if [[ ${#langs[@]} -eq 0 ]]; then
        echo "{\"primary_language\":\"unknown\",\"languages\":[]}"
    else
        echo "{\"primary_language\":\"$primary\",\"languages\":$(printf '%s\n' "${langs[@]}" | jq -R -s -c 'split("\n") | map(select(length>0))')}"
    fi
}

# ── Directory Scanning ──────────────────────────────────────────────

infer_root_type() {
    local name="$1"
    case "$name" in
        cmd|main|app|apps) echo "app-entry" ;;
        internal|pkg|lib|libs|core|shared|common|packages|src|source) echo "private-lib" ;;
        include|includes|headers) echo "public-headers" ;;
        test|tests|unittests|e2e|integration) echo "test" ;;
        docs|doc) echo "docs" ;;
        deploy|infra|infrastructure|terraform|k8s|ci|packaging|.github) echo "infrastructure" ;;
        api|service|services|server|handler|controller) echo "service" ;;
        model|domain|entity|entities|repository|store|db) echo "domain" ;;
        external|extern|thirdparty|third_party|vendor) echo "vendored" ;;
        perf|performance|bench|benchmark|benchmarks) echo "benchmarks" ;;
        tools|tool|scripts|script|util|utils) echo "tools" ;;
        *) echo "unknown" ;;
    esac
}

scan_root_modules() {
    local repo="$1"
    local modules="["
    local first=true

    for dir in $(find "$repo" -maxdepth 1 -type d \
        ! -name '.' ! -name '.git' ! -name 'node_modules' \
        ! -name 'vendor' ! -name 'target' ! -name 'build' \
        ! -name 'dist' ! -name '.claude' ! -name '__pycache__' \
        ! -name '.venv' ! -name 'venv' ! -name '.idea' \
        ! -name '.cursor' ! -name '.github' | sort); do

        local name=$(basename "$dir")
        local file_count=$(find "$dir" -type f ! -path '*/.git/*' ! -path '*/node_modules/*' ! -path '*/vendor/*' 2>/dev/null | wc -l | tr -d ' ')
        [[ $file_count -eq 0 ]] && continue

        local mtype=$(infer_root_type "$name")

        [[ "$first" == "false" ]] && modules+=","
        modules+="{\"path\":\"$name/\",\"type\":\"$mtype\",\"loc\":0,\"files\":$file_count}"
        first=false
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
    local name=$(basename "$path")
    case "$name" in
        cmd|main|app) echo "app-entry" ;;
        internal|core|domain|model|entity) echo "domain" ;;
        api|service|handler|controller|server|grpc|http|rest) echo "service" ;;
        adapter|connector|client|gateway|proxy) echo "adapter" ;;
        infra|config|deploy|monitoring|logging|common|shared|util|utils) echo "infrastructure" ;;
        *) echo "unknown" ;;
    esac
}

scan_leaf_modules() {
    local repo="$1"
    local modules="["
    local first=true

    for dir in $(find "$repo" -mindepth 2 -maxdepth 3 -type d \
        ! -path '*/.git/*' ! -path '*/node_modules/*' ! -path '*/vendor/*' \
        ! -path '*/target/*' ! -path '*/build/*' ! -path '*/builds/*' ! -path '*/dist/*' \
        ! -path '*/test/*' ! -path '*/tests/*' ! -path '*/unittests/*' ! -path '*/__pycache__/*' \
        ! -path '*/external/*' ! -path '*/extern/*' ! -path '*/vendor/*' ! -path '*/thirdparty/*' ! -path '*/third_party/*' \
        ! -path '*/.venv/*' ! -path '*/venv/*' | sort); do

        local rel="${dir#$repo/}"
        local has_build=false
        [[ -f "$dir/go.mod" || -f "$dir/pom.xml" || -f "$dir/build.gradle" || \
           -f "$dir/CMakeLists.txt" || -f "$dir/pyproject.toml" || \
           -f "$dir/Makefile" || -f "$dir/package.json" ]] && has_build=true

        local src_count=$(find "$dir" -maxdepth 1 -type f \
            \( -name "*.go" -o -name "*.java" -o -name "*.py" -o -name "*.cpp" -o -name "*.cc" -o -name "*.c" -o -name "*.h" -o -name "*.hpp" \) 2>/dev/null | wc -l | tr -d ' ')

        # Require at least 1 source file even if there's a build file
        if [[ $src_count -ge 3 ]] || { [[ "$has_build" == "true" && $src_count -ge 1 ]]; }; then
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

# ── Build System Extraction ─────────────────────────────────────────

extract_build() {
    local repo="$1"
    local lang="$2"
    local cmds="["

    case "$lang" in
        go)
            cmds+="{\"scope\":\"root\",\"cmd\":\"go build ./...\",\"cwd\":\".\"}"
            cmds+=",{\"scope\":\"root\",\"cmd\":\"go vet ./...\",\"cwd\":\".\"}"
            if [[ -f "$repo/Makefile" ]]; then
                local targets=$(grep -oE '^[a-zA-Z_-]+:' "$repo/Makefile" | tr -d ':' | grep -E '^(build|test|lint|fmt|run|dev|setup)$' | sort -u | tr '\n' ',' | sed 's/,$//')
                [[ -n "$targets" ]] && cmds+=",{\"scope\":\"root\",\"cmd\":\"make [$targets]\",\"cwd\":\".\"}"
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
                cmds+=",{\"scope\":\"root\",\"cmd\":\"cmake --build build --target test\",\"cwd\":\".\"}"
            fi
            if [[ -f "$repo/configure.ac" || -f "$repo/configure.in" ]]; then
                cmds+=",{\"scope\":\"root\",\"cmd\":\"./autogen.sh && ./configure && make\",\"cwd\":\".\"}"
                cmds+=",{\"scope\":\"root\",\"cmd\":\"make check\",\"cwd\":\".\"}"
            elif [[ -f "$repo/Makefile" ]]; then
                cmds+=",{\"scope\":\"root\",\"cmd\":\"make\",\"cwd\":\".\"}"
                cmds+=",{\"scope\":\"root\",\"cmd\":\"make test\",\"cwd\":\".\"}"
            fi
            ;;
        python)
            if [[ -f "$repo/pyproject.toml" ]]; then
                if grep -q '\[tool.poetry\]' "$repo/pyproject.toml" 2>/dev/null; then
                    cmds+="{\"scope\":\"root\",\"cmd\":\"poetry install\",\"cwd\":\".\"}"
                    cmds+=",{\"scope\":\"root\",\"cmd\":\"poetry run pytest\",\"cwd\":\".\"}"
                else
                    cmds+="{\"scope\":\"root\",\"cmd\":\"pip install -e '.[dev]'\",\"cwd\":\".\"}"
                    cmds+=",{\"scope\":\"root\",\"cmd\":\"pytest\",\"cwd\":\".\"}"
                fi
            elif [[ -f "$repo/setup.py" || -f "$repo/setup.cfg" ]]; then
                cmds+="{\"scope\":\"root\",\"cmd\":\"pip install -e '.[dev]'\",\"cwd\":\".\"}"
                cmds+=",{\"scope\":\"root\",\"cmd\":\"pytest\",\"cwd\":\".\"}"
            fi
            ;;
    esac

    cmds+="]"
    echo "\"build_commands\": $cmds"
}

# ── Style Rules Extraction ──────────────────────────────────────────

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
                [[ -f "$repo/checkstyle.xml" ]] && rules=$(echo "$rules" | jq '.java = {"linter":"checkstyle"}')
                grep -q "spotless" "$repo/build.gradle" 2>/dev/null && rules=$(echo "$rules" | jq '.java.formatter = "spotless"') ;;
            cpp)
                if [[ -f "$repo/.clang-format" ]]; then
                    local base=$(grep "BasedOnStyle" "$repo/.clang-format" 2>/dev/null | awk '{print $2}')
                    rules=$(echo "$rules" | jq --arg style "${base:-LLVM}" '.cpp = {"formatter":"clang-format","base_style":$style}')
                fi
                [[ -f "$repo/.clang-tidy" ]] && rules=$(echo "$rules" | jq '.cpp.linter = "clang-tidy"') ;;
            python)
                if [[ -f "$repo/pyproject.toml" ]]; then
                    if grep -q '\[tool.ruff\]' "$repo/pyproject.toml" 2>/dev/null; then
                        rules=$(echo "$rules" | jq '.python = {"linter":"ruff"}')
                    elif grep -q '\[tool.black\]' "$repo/pyproject.toml" 2>/dev/null; then
                        rules=$(echo "$rules" | jq '.python = {"formatter":"black"}')
                    fi
                fi
                [[ -f "$repo/.flake8" ]] && rules=$(echo "$rules" | jq '.python.linter = "flake8"') ;;
        esac
    done

    echo "\"style_rules\": $rules"
}

# ── CI Extraction ───────────────────────────────────────────────────

extract_ci() {
    local repo="$1"
    local pipeline="["

    if [[ -d "$repo/.github/workflows" ]]; then
        for yml in "$repo/.github/workflows"/*.yml "$repo/.github/workflows"/*.yaml; do
            [[ ! -f "$yml" ]] && continue
            local name=$(grep -m1 '^name:' "$yml" 2>/dev/null | sed 's/.*name:\s*//;s/"//g' | tr -d '\r')
            local steps=$(grep -E '^\s+run:' "$yml" 2>/dev/null | sed 's/.*run:\s*//;s/|//g' | tr '\n' '|' | sed 's/|$//')
            pipeline+=$(jq -n --arg stage "$name" --arg steps "$steps" '{stage: $stage, steps: $steps}'),
        done
    fi
    [[ -f "$repo/.gitlab-ci.yml" ]] && pipeline+=$(jq -n '{source: "gitlab-ci"}'),

    pipeline="${pipeline%,}]"
    echo "\"ci_pipeline\": $pipeline"
}

# ── Git Metadata Extraction ─────────────────────────────────────────

extract_git() {
    local repo="$1"
    local convention="unknown"
    local samples="[]"

    local recent_log=$(git -C "$repo" log --oneline -20 --format="%s" 2>/dev/null || true)
    if echo "$recent_log" | grep -qE '^(feat|fix|chore|docs|refactor|test|ci)(\(.+\))?:'; then
        convention="conventional-commits"
        local log5=$(git -C "$repo" log --oneline -5 --format="%s" 2>/dev/null || true)
        samples=$(echo "$log5" | grep -E '^(feat|fix|chore|docs|refactor)' | jq -R -s -c 'split("\n") | map(select(length>0))')
    elif echo "$recent_log" | grep -qiE '^(problem|solution):'; then
        convention="problem-solution"
        local log5=$(git -C "$repo" log --oneline -5 --format="%s" 2>/dev/null || true)
        samples=$(echo "$log5" | grep -iE '^(problem|solution):' | jq -R -s -c 'split("\n") | map(select(length>0))')
    fi

    echo "\"commit_convention\":{\"style\":\"$convention\",\"sample\":$samples}"

    local owners_file=""
    [[ -f "$repo/.github/CODEOWNERS" ]] && owners_file="$repo/.github/CODEOWNERS"
    [[ -f "$repo/CODEOWNERS" ]] && owners_file="$repo/CODEOWNERS"
    if [[ -n "$owners_file" ]]; then
        local owners=$(grep -v '^#' "$owners_file" | grep -v '^$' | awk '{print $1, $NF}' | jq -R -s -c 'split("\n") | map(select(length>0) | split(" ") | {path: .[0], owner: .[1]})')
        echo ",\"code_owners\": $owners"
    fi
}

# ── Test Framework Extraction ───────────────────────────────────────

extract_tests() {
    local repo="$1"
    local lang="$2"
    local framework="unknown"
    local cmds="[]"
    local dirs="[]"
    local patterns="[]"

    dirs=$(find "$repo" -maxdepth 2 -type d \( -name "test" -o -name "tests" -o -name "__tests__" -o -name "spec" \) ! -path '*node_modules*' 2>/dev/null | sed "s|$repo/||" | jq -R -s -c 'split("\n") | map(select(length>0))')

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
            if [[ -f "$repo/CMakeLists.txt" ]]; then
                if grep -qE '(GTest|gtest)' "$repo/CMakeLists.txt" 2>/dev/null; then
                    framework="GoogleTest"
                elif grep -qE '(Unity|unity)' "$repo/CMakeLists.txt" 2>/dev/null; then
                    framework="Unity"
                fi
            fi
            # Fallback: check for unity in external/ or test directories
            if [[ "$framework" == "unknown" ]]; then
                if [[ -d "$repo/external/unity" ]] || grep -qr 'unity' "$repo/tests" --include="*.cpp" -m1 2>/dev/null; then
                    framework="Unity"
                fi
            fi
            cmds="[{\"scope\":\"root\",\"cmd\":\"cmake --build build --target test\",\"cwd\":\".\"}]"
            # Detect actual test file naming patterns
            patterns="["
            if [[ -d "$repo/tests" ]]; then
                local pfxs=$(find "$repo/tests" -maxdepth 1 -type f \( -name "*.cpp" -o -name "*.cc" -o -name "*.c" \) 2>/dev/null | xargs -n1 basename 2>/dev/null | sed 's/\..*//' | sort -u)
                if echo "$pfxs" | grep -q '^test_'; then patterns+="\"test_*.cpp\",\"test_*.cc\","; fi
                if echo "$pfxs" | grep -q '_test$'; then patterns+="\"*_test.cpp\",\"*_test.cc\","; fi
                if echo "$pfxs" | grep -q '^unittest_'; then patterns+="\"unittest_*.cpp\",\"unittest_*.cc\","; fi
            fi
            if [[ -d "$repo/unittests" ]]; then
                local upfxs=$(find "$repo/unittests" -maxdepth 1 -type f \( -name "*.cpp" -o -name "*.cc" -o -name "*.c" \) 2>/dev/null | xargs -n1 basename 2>/dev/null | sed 's/\..*//' | sort -u)
                if echo "$upfxs" | grep -q '^unittest_'; then patterns+="\"unittest_*.cpp\",\"unittest_*.cc\","; fi
                if echo "$upfxs" | grep -q '^test_'; then patterns+="\"test_*.cpp\",\"test_*.cc\","; fi
            fi
            patterns="${patterns%,}]"
            if [[ "$patterns" == "]" ]]; then patterns='["*_test.cpp","*_test.cc"]'; fi ;;
        python)
            framework="pytest"
            cmds="[{\"scope\":\"root\",\"cmd\":\"pytest --cov -n auto\",\"cwd\":\".\"}]"
            patterns='["test_*.py","*_test.py"]' ;;
    esac

    echo "\"test\":{\"framework\":\"$framework\",\"commands\":$cmds,\"test_dirs\":$dirs,\"file_patterns\":$patterns}"
}

# ── Dependency Extraction ───────────────────────────────────────────

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
        [[ -n "$imports" ]] && graph=$(echo "$graph" | jq --arg p "$rel/" --argjson d "$(printf '%s' "$imports" | jq -R -s -c 'split(",") | map(select(length>0))')" '. + {($p): $d}')
    done
    echo "$graph"
}

extract_java_deps() {
    local repo="$1"
    local graph="{}"
    [[ ! -f "$repo/pom.xml" ]] && { echo "$graph"; return; }

    local groupId=$(grep -A2 '<groupId>' "$repo/pom.xml" | head -3 | sed -n 's/.*<groupId>\([^<]*\)<\/groupId>.*/\1/p' | head -1)
    [[ -z "$groupId" ]] && { echo "$graph"; return; }

    for pom in $(find "$repo" -name "pom.xml" ! -path '*/target/*' 2>/dev/null); do
        local rel=$(dirname "${pom#$repo/}")
        [[ "$rel" == "." ]] && continue
        local deps=$(grep "<groupId>$groupId</groupId>" "$pom" -A1 | grep "<artifactId>" | sed -n 's/.*<artifactId>\([^<]*\)<\/artifactId>.*/\1/p' | tr '\n' ',' | sed 's/,$//')
        [[ -n "$deps" ]] && graph=$(echo "$graph" | jq --arg p "$rel/" --argjson d "$(printf '%s' "$deps" | jq -R -s -c 'split(",") | map(select(length>0))')" '. + {($p): $d}')
    done
    echo "$graph"
}

extract_python_deps() {
    local repo="$1"
    local graph="{}"
    local pkg=""
    [[ -f "$repo/pyproject.toml" ]] && pkg=$(grep -A5 '\[project\]' "$repo/pyproject.toml" | grep 'name' | sed -n 's/.*"\([^"]*\)".*/\1/p' | head -1)
    [[ -z "$pkg" ]] && { echo "$graph"; return; }

    for dir in $(find "$repo" -maxdepth 3 -type d ! -path '*/__pycache__/*' ! -path '*/.venv/*' ! -path '*/venv/*' | sort); do
        local rel="${dir#$repo/}"
        local imports=$(grep -rh "from $pkg\." "$dir" --include="*.py" 2>/dev/null | \
            sed -n "s/.*from $pkg\.\([^[:space:].]*\).*/\1/p" | sort -u | tr '\n' ',' | sed 's/,$//')
        [[ -n "$imports" ]] && graph=$(echo "$graph" | jq --arg p "$rel/" --argjson d "$(printf '%s' "$imports" | jq -R -s -c 'split(",") | map(select(length>0))')" '. + {($p): $d}')
    done
    echo "$graph"
}

extract_cpp_deps() {
    local repo="$1"
    local graph="{}"

    if [[ -d "$repo/build" ]] && command -v cmake &>/dev/null; then
        cmake --graphviz="$repo/build/_deps.dot" "$repo" 2>/dev/null || true
        if [[ -f "$repo/build/_deps.dot" ]]; then
            local edges=$(grep '->' "$repo/build/_deps.dot" | sed 's/.*"\(.*\)" -> "\(.*\)".*/"\1":"\2"/' | tr '\n' ',' | sed 's/,$//')
            [[ -n "$edges" ]] && graph="{$edges}"
        fi
    fi

    if [[ "$graph" == "{}" ]]; then
        for dir in $(find "$repo" -maxdepth 3 -type d ! -path '*/build/*' | sort); do
            local rel="${dir#$repo/}"
            local incs=$(grep -rh '#include "' "$dir" --include="*.cpp" --include="*.h" --include="*.hpp" 2>/dev/null | \
                sed -n 's/.*#include "\([^"]*\)".*/\1/p' | grep -v '^\.\./' | sort -u | tr '\n' ',' | sed 's/,$//')
            [[ -n "$incs" ]] && graph=$(echo "$graph" | jq --arg p "$rel/" --argjson d "$(printf '%s' "$incs" | jq -R -s -c 'split(",") | map(select(length>0))')" '. + {($p): $d}')
        done
    fi
    echo "$graph"
}

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

# ── Profile Assembly ────────────────────────────────────────────────

write_profile() {
    local repo="$1"
    local output="$2"

    local lang_json=$(detect_language "$repo")
    local primary=$(echo "$lang_json" | jq -r '.primary_language')
    local langs_arr=$(echo "$lang_json" | jq -r '.languages[]')

    local total_loc=0
    if command -v tokei &>/dev/null; then
        total_loc=$(cd "$repo" && tokei --output json 2>/dev/null | jq '[.[].code] | add // 0' || echo 0)
    fi

    local root_mods=$(scan_root_modules "$repo")
    local leaf_mods=$(scan_leaf_modules "$repo")
    local leaf_count=$(echo "$leaf_mods" | jq 'length')
    local build=$(extract_build "$repo" "$primary")
    local style
    if [[ -n "$langs_arr" ]]; then
        style=$(extract_style "$repo" $langs_arr)
    else
        style="\"style_rules\": {}"
    fi
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
    command -v tokei &>/dev/null || echo "WARNING: tokei not installed (LOC stats will be 0). Install with: brew install tokei" >&2

    write_profile "$repo" "$output"
}

main "$@"
