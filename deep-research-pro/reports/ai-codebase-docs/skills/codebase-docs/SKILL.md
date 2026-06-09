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

### Phase 3: ARCHITECTURE.md (Code Map)

Generate `ARCHITECTURE.md` (≤300 lines) using the matklad three-section format. Use `templates/architecture.tmpl.md` as structural reference.

**Section 1 — Bird's-eye view (2-3 sentences):**
- Read README.md if it exists; extract the project's purpose
- Identify: what problem does this solve? who are the users?
- If README is absent, infer from directory names and module types

**Section 2 — Code map (2-5 sentences per significant module):**

For each root module and key leaf module:
```
### `path/to/module/`
<One sentence: what this module does.>
Entry point: `<key/file.go>`. Key exports: `<symbol1>`, `<symbol2>`.
<Architectural role: API boundary / internal / adapter / domain.>
<Optional: critical invariant specific to this module.>
```

**Critical constraint:** Name important files, modules, and types. Do NOT directly link them (links rot). Readers use grep or agent file search to locate.

**Section 3 — Cross-cutting concerns:**

Auto-detect from profile and source sampling:
- **Error handling**: exceptions vs. Result types vs. error codes (infer from representative files)
- **Observability**: logging patterns, metrics libraries (detect from imports)
- **Testing strategy**: contract/integration/unit split (from test file patterns)
- **Build & deploy**: CI pipeline summary (from profile ci_pipeline)

Mark uncertain claims with `[? review]` and add `<!-- HUMAN_REVIEW -->` for gaps:

```markdown
### Security [~ inferred]
{{AUTO_DETECTED_AUTHZ_PATTERNS}}
<!-- HUMAN_REVIEW: add security review process, threat model link -->

### Performance [? review]
<!-- HUMAN_REVIEW: add performance SLAs, profiling approach -->
```

**Post-generation:** Present the full ARCHITECTURE.md for review. Focus confirmation on:
- "Are the module descriptions accurate?"
- "Which cross-cutting concerns are missing?"
- "Any architectural invariants not captured?"

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
| ARCHITECTURE.md | ≤300 | Per-module: `[✓ auto]` / `[~ inferred]`; cross-cutting: `[? review]` |

## Idempotency

If a file already exists at the target path:
- Do NOT overwrite silently
- Show a diff between the existing file and the generated content
- Let the user choose: keep existing, merge, or replace
