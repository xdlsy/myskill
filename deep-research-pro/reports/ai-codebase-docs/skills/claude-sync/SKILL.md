---
name: claude-sync
description: Use when building Claude Code loading bridges (CLAUDE.md + .claude/rules/) for projects that already have AGENTS.md entry files. Triggered by "sync claude config", "generate claude rules", or as the final step after codebase-docs. Also use when AGENTS.md files were manually written and need Claude Code wiring.
---

# claude-sync

## Overview

Generate Claude Code loading infrastructure — `CLAUDE.md` and `.claude/rules/` — for a project that already has AGENTS.md entry files. This skill does NOT generate content; it builds bridges to existing content via `@-import` and path-scoped rules.

**Prerequisite:** Run after `codebase-docs` (or after manually creating AGENTS.md files).

## When to Use

- AGENTS.md files exist and need Claude Code wiring
- After running codebase-docs (final step)
- Rebuilding `.claude/rules/` after AGENTS.md structure changes
- Adding Claude Code support to a repo that already has AGENTS.md

## Prerequisites

- AGENTS.md at repo root (and optionally in sub-modules)
- `codebase-profile.json` from collect.sh (provides language/module inventory)
- `jq` installed

## Workflow

### Step 1: Inventory Existing State

1. Read `codebase-profile.json` for: primary language, languages array, leaf_modules
2. Scan for existing Claude Code files:
   - `CLAUDE.md` (root)
   - `.claude/CLAUDE.md` (monorepo variant)
   - `.claude/rules/*.md` (existing rules)
   - `.claude/settings.json` (existing settings)

3. Scan for existing AGENTS.md files:
   - `./AGENTS.md` (root)
   - `{leaf_module.path}/AGENTS.md` (sub-modules)

4. Present inventory:

```
Claude Code state:
├── CLAUDE.md: [absent / present (N lines, [has @AGENTS.md] / [missing @AGENTS.md])]
├── .claude/CLAUDE.md: [absent / present]
├── .claude/rules/: [absent / N existing rules]
└── AGENTS.md files: [root + M module AGENTS.md]

Plan:
├── CLAUDE.md: [create / append @AGENTS.md / no change needed]
├── .claude/rules/global-style.md: [create]
├── .claude/rules/global-testing.md: [create]
├── .claude/rules/architecture.md: [create]
└── .claude/rules/<module>.md: [M files to create]
```

### Step 2: Generate CLAUDE.md Bridge

| Existing State | Action |
|---|---|
| No `CLAUDE.md` at root | Create one line: `@AGENTS.md` |
| `CLAUDE.md` exists, no `@AGENTS.md` ref | Append `@AGENTS.md` at end (with newline separator) |
| `CLAUDE.md` exists, already references `@AGENTS.md` | No change |
| `.claude/CLAUDE.md` exists (monorepo) | Read it, check if it references root AGENTS.md. If not, suggest merge. If it has independent content, leave as-is and note to user |

**Never overwrite an existing CLAUDE.md** — only append or skip.

### Step 3: Generate Global Rules

Three self-contained rule files. Content is expanded from profile data, not @-imported (these ARE the source of truth for their paths).

**global-style.md** — paths scoped to source file extensions:

```markdown
---
paths: {{LANGUAGE_GLOB_PATTERNS}}
---

# Code Style

{{EXPANDED_STYLE_RULES_FROM_PROFILE}}
```

`paths` derivation:
- Go: `["**/*.go"]`
- Python: `["**/*.py"]`
- Java: `["**/*.java"]`
- C++: `["**/*.cpp", "**/*.cc", "**/*.cxx", "**/*.h", "**/*.hpp"]`
- If multiple languages, combine all patterns into one array

Content: format `style_rules` from profile into readable form — formatter name, linter name, config file path, key rules.

**global-testing.md** — paths scoped to test files:

```markdown
---
paths: {{TEST_GLOB_PATTERNS}}
---

# Testing Guidelines

- Framework: {{TEST_FRAMEWORK}}
- Run: `{{TEST_COMMAND}}`
- Test files: {{FILE_PATTERNS}}
- Test directories: {{TEST_DIRS}}
```

`paths` derivation:
- Go: `["**/*_test.go"]`
- Python: `["**/test_*.py", "**/*_test.py", "tests/**"]`
- Java: `["**/*Test.java", "**/*Tests.java"]`
- C++: `["**/*_test.cpp", "**/*_test.cc"]`

**architecture.md** — global invariants, always loaded (`paths: [ ]`):

```markdown
---
paths: []
---

# Architecture Invariants

{{AUTO_DETECTED_INVARIANTS_FROM_ROOT_AGENTS_MD}}
<!-- HUMAN_REVIEW: add codebase-specific architecture rules -->
```

Content: extract from root AGENTS.md "Do Not / Gotchas" section, or infer from module types (e.g., "internal/ must not be imported externally").

### Step 4: Generate Module Index Rules

For each sub-module that has an `AGENTS.md`, create a one-line rule file:

```markdown
---
paths: ["{{MODULE_PATH}}**"]
---

@{{MODULE_PATH}}AGENTS.md
```

The `paths:` field ensures Claude only loads this rule when reading files in that module. The `@-import` loads the module's full AGENTS.md content.

**Constraints:**
- Module rules ≤15 lines (mostly frontmatter)
- No duplication of AGENTS.md content — only the @-import
- Skip modules that have no AGENTS.md
- If a `.claude/rules/<module>.md` already exists, show a diff before overwriting

### Step 5: Summary & Verify

Present final state:

```
Generated/Updated:
├── CLAUDE.md: [created / appended / unchanged]
├── .claude/rules/
│   ├── global-style.md       (paths: ["**/*.go", "**/*.py"])
│   ├── global-testing.md     (paths: ["**/*_test.go", "**/test_*.py", "tests/**"])
│   ├── architecture.md       (paths: [] — always loaded)
│   ├── order.md              (paths: ["internal/order/**"] → @internal/order/AGENTS.md)
│   └── payment.md            (paths: ["internal/payment/**"] → @internal/payment/AGENTS.md)
```

## Idempotency

- **CLAUDE.md**: never overwrite; only create or append
- **.claude/rules/global-*.md**: show diff if exists, let user choose (keep / merge / replace)
- **.claude/rules/<module>.md**: show diff if exists
- **No-op detection**: if everything is already wired correctly, report "Already synchronized" and exit

## File Constraints

| File | Max Lines | Content |
|------|-----------|---------|
| CLAUDE.md (generated) | 1 | `@AGENTS.md` only |
| global-style.md | 30-50 | Self-contained, from profile |
| global-testing.md | 20-30 | Self-contained, from profile |
| architecture.md | 20-40 | Self-contained invariants |
| module rule .md | ≤15 | Frontmatter + one-line @-import |

## Design Notes

- **AGENTS.md is source of truth.** Rules don't duplicate — they @-import.
- **Global rules are self-contained** because they apply across modules (no single AGENTS.md to import from).
- **No per-module CLAUDE.md files** — module rules via `.claude/rules/` with `paths:` achieve the same effect.
- **paths: []** means "always loaded" — use for architecture invariants only.
