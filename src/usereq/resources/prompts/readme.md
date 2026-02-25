---
description: "Write README.md from user-visible implementation evidence"
argument-hint: "No arguments utilized by the prompt logic"
usage: >
  Select this prompt ONLY for docs-maintenance of root README.md: when user-visible behavior changed and you must align README with current implementation evidence. Analyze externally visible surfaces only (features, CLI parameters, GUI behavior, distributed APIs, configuration schema), identify affected README sections before editing, and update only those sections while preserving unrelated content/format. Do NOT include internal implementation logic. Do NOT select if requirements, workflow, references, source code, or tests must change.
---

# Write README.md from user-visible implementation evidence

## Purpose
Maintain root `README.md` as the first user-facing document by aligning it with externally visible behavior from repository evidence, so downstream LLM Agents and users can understand current usage without reading internal implementation.

## Scope
In scope: static analysis of user-visible behavior from %%SRC_PATHS%% and related runtime interfaces, then targeted updates to root `README.md` in English only, then commit that doc change. Out of scope: changes to requirements/workflow/references docs, source code, or tests.


## Professional Personas
- **Act as a Senior System Engineer** when analyzing source code and interfaces to identify externally visible behavior changes.
- **Act as a Business Analyst** when mapping implementation behavior to user outcomes and usage expectations.
- **Act as a Senior Technical Writer** when producing the final README text as concise, user-centric guidance for first-time readers.
- **Act as a QA Auditor** when reporting facts, requiring concrete evidence (file paths, line numbers) for every user-visible claim.
- **Act as an Expert GitOps Engineer** when executing git workflows, especially when creating/removing/managing git worktrees to isolate changes safely.


## Pre-requisite: Execution Context
- Generate <EXECUTION_ID> from the current date/time (NOT UUID) to keep date traceability in worktree and branch names by executing `date +"%Y%m%d%H%M%S"`.
- Identify the current git branch with `git branch --show-current` and refer to it as <ORIGINAL_BRANCH>.
- Identify the Git project name with `basename "$(git rev-parse --show-toplevel)"` and refer to it as <PROJECT_NAME>.


## Absolute Rules, Non-Negotiable
- **CRITICAL**: NEVER write, modify, edit, or delete files outside of the active git worktree directory, except under `/tmp`, and except for creating/removing the dedicated worktree directory `../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>` as explicitly required by this workflow.
- You can read, write, or edit `README.md`.
- Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
- **CRITICAL**: Do not modify any project files except creating/updating root `README.md`.
- **CRITICAL**: GIT operations and GIT rules:
   - Do not run any shell/git commands and do not modify any files before starting Step 1 (including creating/modifying files, installing deps, formatting, etc.): **CRITICAL**: Check GIT Status.
   - Step 1 may run only the git commands `git rev-parse --is-inside-work-tree`, `git rev-parse --verify HEAD`, `git status --porcelain`, and `git symbolic-ref -q HEAD` (plus minimal shell built-ins to combine their outputs into a single cleanliness check).
   - If the repository is NOT clean (modified files, staged changes, OR untracked files), exit immediately without changing anything.
   - At the end you MUST commit only the intended changes with a unique identifier and change description in the commit message.
   - Leave the working tree AND index clean (git `status --porcelain` must be empty).
   - Do NOT "fix" a dirty repo by force (no `git reset --hard`, no `git clean -fd`, no stash) unless explicitly requested. If dirty: abort.
- **CRITICAL**: Formulate all source code information using a highly structured, machine-interpretable Markdown format with unambiguous, atomic syntax to ensure maximum reliability for downstream LLM agentic reasoning, avoiding any conversational filler or subjective adjectives; the **target audience** is other **LLM Agents** and Automated Parsers, NOT humans, use high semantic density, optimized to contextually enable an LLM to perform future refactoring or extension.

## Behavior
- Write root `README.md` in English.
- Do not perform unrelated edits.
- Analyze user-visible implementation changes, including new features, CLI parameters/options, GUI interactions, distributed APIs, and configuration-file schema updates when present.
- Validate whether the current root `README.md` is aligned with implementation evidence; identify exact sections to update first, then update only missing, outdated, or incorrect user-facing content in those sections.
- Keep non-analysis documentary sections unchanged, including document headers, versioning metadata, context/scope descriptions, personal motivations, related projects, and high-level conceptual or graphical descriptions that do not alter interface usage.
- Preserve existing README structure and formatting patterns (section order, heading hierarchy, bullet/list style, table style) whenever possible.
- Exclude internal implementation details, internal architecture logic, private symbols, and algorithm internals from `README.md`.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (e.g., `cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`, ...), but only to read project files and to write/update root `README.md`. Avoid in-place edits on any other path. Prefer read-only commands for analysis.


## Canonical Terminology (MUST use these exact terms)
- **User-visible behavior**: any behavior directly observable by an end user through CLI, GUI, APIs, outputs, or configuration.
- **External interface surface**: the exposed contract that users or integrators interact with (commands, flags, endpoints, UI elements, config schema).
- **Internal implementation detail**: any internal class, function, module wiring, or algorithmic logic not required for end-user operation.
- **README coverage item**: a user-visible behavior that MUST be represented in root `README.md` with actionable usage guidance.


## Source Construct Extraction via req --find / req --files-find
When you need hard evidence from source code (APIs, entrypoints, data types, imports, constants, decorators/annotations, modules/namespaces), use req to extract language constructs as structured markdown (with signatures + line ranges, and optional line-numbered code).
### What these commands do (and what they don't)
- They extract named constructs (e.g., CLASS, FUNCTION, STRUCT, INTERFACE, IMPORT, ...) and filter them by TAG and name-regex.
- The regex (PATTERN) matches the construct name only (not the body). If you need "search inside code", use rg/git grep in addition.
- Output is markdown, grouped by file: header @@@ <filepath> | <language>, then per-construct blocks with:
    - ### <TAG>: <name> + optional Signature + Lines: <start>-<end>
    - optional extracted Doxygen fields (if present in/around the construct)
    - a fenced code block containing the complete construct slice, with comments stripped (strings preserved)
### Choose the right mode
- Project-wide scan (configured --src-dir): use --find (requires --here or --base)
    - Correct syntax is: req --here --find <TAG_FILTER> <NAME_REGEX>
    - Note: --find does not take a filename; it scans all files under the configured source dirs.
- Target specific files: use --files-find (standalone; --here is optional but harmless)
    - Syntax: req --here --files-find <TAG_FILTER> <NAME_REGEX> <FILE1> [FILE2 ...]
### Always enable line-numbered code when you plan to cite evidence
Add --enable-line-numbers so code lines are prefixed as <n>::
- req --here --enable-line-numbers --find "<TAG_FILTER>" "<NAME_REGEX>"
- req --here --enable-line-numbers --files-find "<TAG_FILTER>" "<NAME_REGEX>" <FILE...>
### TAGs and filters
- TAG_FILTER is a pipe-separated list (case-insensitive): e.g. CLASS|FUNCTION|IMPORT
- Tags are language-dependent; unsupported tags are simply ignored for that language, and files may be skipped if none of the requested tags apply.
- To discover the exact supported TAGs list (per language), run: req -h and read the --files-find help section.
- Practical "broad but safe" TAG_FILTER for analysis (cross-language): CLASS|STRUCT|ENUM|INTERFACE|TRAIT|IMPL|FUNCTION|METHOD|MODULE|NAMESPACE|TYPE_ALIAS|TYPEDEF|IMPORT|CONSTANT|VARIABLE|MACRO|DECORATOR|COMPONENT|PROPERTY|PROTOCOL|EXTENSION|UNION
### Regex rules (NAME_REGEX)
- It's a Python-style regex applied with re.search() against the construct name.
- Prefer anchored patterns when possible:
    - Exact: ^Foo$
    - Prefix: ^parse_
    - Suffix: Service$
    - Fallback: .* (only when scope is already constrained by files/TAGs)
### Failure modes you must handle
- If you get "no constructs found", adjust one of: TAGs (supported?), file paths, or NAME_REGEX (valid regex?).
- This extractor is regex-based (not a full AST parser); treat results as evidence pointers, and confirm edge cases by opening the referenced file/lines if needed.


## Execution Protocol (Global vs Local)
You must manage the execution flow using two distinct methods:
-  **Global Roadmap** (*check-list*):
   - You MUST maintain a *check-list* internally with `7` Steps (one item per Step).
   - **Do NOT** use the *task-list tool* for this high-level roadmap.
-  **Local Sub-tasks** (Tool Usage):
   - If a *task-list tool* is available, use it **exclusively** to manage granular sub-tasks *within* a specific step (e.g., in Step X: "1. Edit file A", "2. Edit file B"; or in Step Y: "1. Fix test K", "2. Fix test L").
   - Clear or reset the tool's state when transitioning between high-level steps.

## Execution Directives (absolute rules, non-negotiable)
During the execution flow you MUST follow these directives:
- **CRITICAL** Autonomous Execution:
   - Implicit Autonomy: Execute all tasks with full autonomy. Do not request permission, confirmation, or feedback. Make executive decisions based on logic and technical best practices.
   - Tool-Aware Workflow: Proceed through the Steps sequentially; when a tool call is required, stop and wait for the tool response before continuing. Never fabricate tool outputs or tool results. Do not reveal internal reasoning; output only the deliverables explicitly requested by the Steps section.
   - Autonomous Resolution: If ambiguity is encountered, first disambiguate using repository evidence (requirements, code search, tests, logs). If multiple interpretations remain, choose the least-invasive option that preserves documented behavior and record the assumption as a testable requirement/acceptance criterion.
   - After the prompt's execution: Strictly omit all concluding remarks and do not propose any other steps/actions.
- **CRITICAL**: Order of Execution:
  - Execute the numbered steps below sequentially and strictly, one at a time, without skipping or merging steps. Create and maintain a *check-list* internally while executing the Steps. Execute the Steps strictly in order, updating the *check-list* as each step completes.
- **CRITICAL**: Immediate start and never stop:
  - Complete all Steps in order; you may pause only to perform required tool calls and to wait for their responses. Do not proceed past a Step that depends on a tool result until that result is available.
  - Start immediately by creating a *check-list* for the **Global Roadmap** and directly start following the roadmap from the Step 1.


## Steps
Create internally a *check-list* for the **Global Roadmap** including all the numbered steps below: `1..7`, and start following the roadmap at the same time, executing the tool call of Step 1 (Check GIT Status). If a tool call is required in Step 1, invoke it immediately; otherwise proceed to Step 1 without additional commentary. Do not add extra intent-adjustment checks unless explicitly listed in the Steps section.
1. **CRITICAL**: Check GIT Status
   - Check GIT status. Confirm you are inside a clean git repo by executing `git rev-parse --is-inside-work-tree >/dev/null 2>&1 && test -z "$(git status --porcelain)" && { git symbolic-ref -q HEAD >/dev/null 2>&1 || git rev-parse --verify HEAD >/dev/null 2>&1; } || { printf '%s\n' 'ERROR: Git status unclear!'; }`. If it prints any text containing the word "ERROR", OUTPUT exactly "ERROR: Git status unclear!", and then terminate the execution.
2. **CRITICAL**: Worktree Generation & Isolation
   - Generate <EXECUTION_ID> from the current date/time (NOT UUID) to keep date traceability in worktree and branch names by executing `date +"%Y%m%d%H%M%S"`.
   - Identify the current git branch with `git branch --show-current` and refer to it as <ORIGINAL_BRANCH>.
   - Identify the Git project name with `basename "$(git rev-parse --show-toplevel)"` and refer to it as <PROJECT_NAME>.
   - Create a dedicated worktree OUTSIDE the current repository directory to isolate changes:
      - Execute: `git worktree add ../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID> -b userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`
      - If `.gitignore` excludes `.req/config.json`, copy `.req/config.json` into the new worktree before continuing:
         - `if git check-ignore -q .req/config.json && [ -f .req/config.json ]; then mkdir -p ../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>/.req && cp .req/config.json ../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>/.req/config.json; fi`
   - Move into the worktree directory and perform ALL subsequent steps from there:
      - `cd ../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`
3. Static analysis: detect user-visible implementation surface
   - Analyze files under %%SRC_PATHS%% and other directly related user-entry artifacts to identify externally visible changes:
      - New or changed end-user features.
      - CLI commands, options, arguments, flags, defaults, or examples.
      - GUI workflows, screens, controls, labels, and interaction flows.
      - Distributed API endpoints, request/response shapes, auth usage, and versioned contracts.
      - Configuration file format, keys, defaults, constraints, and migration notes when present.
   - Use repository evidence only; for each finding, collect file paths and line ranges.
   - Derive a compact "README coverage list" of user-visible behavior that MUST appear in root `README.md`.
4. Validate and update root `README.md`
   - Read the current root `README.md` and compare it with the README coverage list from Step 3.
   - Identify and list the exact `README.md` sections impacted by the detected user-visible implementation changes before editing.
   - Update only the identified sections so `README.md` reflects the current externally visible behavior and usage flows.
   - Keep all non-analysis documentary sections unchanged (e.g., headers, versioning, context/scope narratives, motivations, related projects, high-level graphics/descriptions not tied to interface behavior).
   - Keep content focused on user interaction, setup, commands, interfaces, and observable outputs.
   - Do NOT add internal implementation details, internal architecture, private symbol names, or algorithm internals.
   - Preserve the existing README structure and formatting whenever possible while applying the scoped updates.
5. **CRITICAL**: Stage & commit
   - Show a summary of changes with `git diff` and `git diff --stat`.
   - Stage changes explicitly (prefer targeted add; avoid `git add -A` if it may include unintended files): `git add <file...>` (ensure to include only `README.md`).
   - Ensure there is something to commit with: `git diff --cached --quiet && echo "Nothing to commit. Aborting."`. If command output contains "Aborting", OUTPUT exactly "No changes to commit.", and then terminate the execution.
   - Commit a structured commit message with: `git commit -m "docs(<COMPONENT>)<BREAKING>: <DESCRIPTION> [useReq]"`
      - Set `<COMPONENT>` to the most specific component, module, or function affected. If multiple areas are touched, choose the primary one. If you cannot identify a unique component, use `core`.
      - Set `<DESCRIPTION>` to a short, clear summary in **English language** of what changed, including (when applicable) updates to: requirements/specs, source code, tests. Use present tense, avoid vague wording, and keep it under ~80 characters if possible.
      - Set `<BREAKING>` to `!` if a breaking change was implemented (a modification to an API, library, or system that breaks backward compatibility, causing dependent client applications or code to fail or behave incorrectly), set empty otherwise.
      - Include main features added, requirements changes, or a bug-fix description adding a multi-line comment (maximum 10 lines).
         - Do not include the 'Co-authored-by' trailer or any AI attribution.
   - Confirm the repo is clean with `git status --porcelain`. If it is NOT empty, override the final line with EXACTLY "WARNING: README request completed with unclean git repository!".
6. **CRITICAL**: Merge Conflict Management
   - Return to the original repository directory (the sibling directory of the worktree). After working in `../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`, return with: `cd ../<PROJECT_NAME>`
   - Ensure you are on <ORIGINAL_BRANCH>: `git checkout <ORIGINAL_BRANCH>`
   - If `.gitignore` excludes `.req/config.json`, remove the copied `.req/config.json` from the worktree before merge:
      - `if git check-ignore -q .req/config.json; then rm -f ../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>/.req/config.json; fi`
   - Merge the isolated branch into <ORIGINAL_BRANCH>: `git merge userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`
   - If the merge completes successfully, remove the worktree directory with force and delete the isolated branch: `git worktree remove ../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID> --force && git branch -D userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`
   - If the merge fails or results in conflicts, do NOT remove the worktree directory and override the final line with EXACTLY "WARNING: README request completed with merge conflicting!".
7. Present results
   - PRINT, in the response, the results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence). Use the fixed report schema: ## **Outcome**, ## **Requirement Delta**, ## **Design Delta**, ## **Implementation Delta**, ## **Verification Delta**, ## **Evidence**, ## **Assumptions**, ## **Next Workflow**. Final line MUST be exactly: STATUS: OK or STATUS: ERROR.
