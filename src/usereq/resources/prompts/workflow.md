---
description: "Write a WORKFLOW.md using the project's source code"
argument-hint: "No arguments utilized by the prompt logic"
usage: >
  Select this prompt ONLY for docs-maintenance of %%DOC_PATH%%/WORKFLOW.md: when it is missing/outdated and you need to regenerate the runtime/workflow model (processes/threads, internal call-traces, communication edges) from evidence in %%SRC_PATHS%% and commit that doc change. Do NOT select if you will change requirements, source code, or tests; choose /req-change, /req-new, /req-fix, /req-refactor, /req-cover, /req-implement, /req-create, or /req-recreate as appropriate. Do NOT select for read-only analysis/audits (use /req-analyze or /req-check).
---

# Write a WORKFLOW.md using the project's source code

## Purpose
Maintain an LLM-oriented runtime/workflow model (`%%DOC_PATH%%/WORKFLOW.md`) derived from repository evidence so downstream LLM Agents can reason about execution units, communication edges, and internal call-traces during SRS-driven design/implementation.

## Scope
In scope: static analysis of source under %%SRC_PATHS%% to generate/overwrite only `%%DOC_PATH%%/WORKFLOW.md` in English only, following the mandated schema, then commit that doc change. Out of scope: changes to requirements, references, source code, or tests.


## Professional Personas
- **Act as a Senior System Engineer** when analyzing source code; your primary goal is to trace the execution flow (call stack) across files and modules, identifying exactly how data and control move from one function to another.
- **Act as a Business Analyst** when cross-referencing code findings with `%%DOC_PATH%%/REQUIREMENTS.md` to ensure functional alignment.
- **Act as a Technical Writer** when producing the final analysis report or workflow descriptions, ensuring clarity, technical precision, and structured formatting.
- **Act as a QA Auditor** when reporting facts, requiring concrete evidence (file paths, line numbers) for every finding.
- **Act as an Expert GitOps Engineer** when executing git workflows, especially when creating/removing/managing git worktrees to isolate changes safely.


## Pre-requisite: Execution Context
- Generate <EXECUTION_ID> from the current date/time (NOT UUID) to keep date traceability in worktree and branch names by executing `date +"%Y%m%d%H%M%S"`.
- Identify the current git branch with `git branch --show-current` and refer to it as <ORIGINAL_BRANCH>.
- Identify the Git project name with `basename "$(git rev-parse --show-toplevel)"` and refer to it as <PROJECT_NAME>.


## Absolute Rules, Non-Negotiable
- **CRITICAL**: NEVER write, modify, edit, or delete files outside of the active git worktree directory, except under `/tmp`, and except for creating/removing the dedicated worktree directory `../useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>` as explicitly required by this workflow.
- You can read, write, or edit `%%DOC_PATH%%/WORKFLOW.md`.
- Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
- **CRITICAL**: Do not modify any project files except creating/updating `%%DOC_PATH%%/WORKFLOW.md`.
- **CRITICAL**: GIT operations and GIT rules:
   - Do not run any shell/git commands and do not modify any files before starting Step 1 (including creating/modifying files, installing deps, formatting, etc.): **CRITICAL**: Check GIT Status.
   - Step 1 may run only the git commands `git rev-parse --is-inside-work-tree`, `git rev-parse --verify HEAD`, `git status --porcelain`, and `git symbolic-ref -q HEAD` (plus minimal shell built-ins to combine their outputs into a single cleanliness check).
   - If the repository is NOT clean (modified files, staged changes, OR untracked files), exit immediately without changing anything.
   - At the end you MUST commit only the intended changes with a unique identifier and change description in the commit message.
   - Leave the working tree AND index clean (git `status --porcelain` must be empty).
   - Do NOT “fix” a dirty repo by force (no `git reset --hard`, no `git clean -fd`, no stash) unless explicitly requested. If dirty: abort.
- **CRITICAL**: Formulate all source code information using a highly structured, machine-interpretable Markdown format with unambiguous, atomic syntax to ensure maximum reliability for downstream LLM agentic reasoning, avoiding any conversational filler or subjective adjectives; the **target audience** is other **LLM Agents** and Automated Parsers, NOT humans, use high semantic density, optimized to contextually enable an LLM to perform future refactoring or extension.

## Behavior
- Write the `%%DOC_PATH%%/WORKFLOW.md` document in English.
- Do not perform unrelated edits.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (e.g., `cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`, ...), but only to read project files and to write/update `%%DOC_PATH%%/WORKFLOW.md`. Avoid in-place edits on any other path. Prefer read-only commands for analysis.


## Canonical Terminology (MUST use these exact terms)
- **Process**: an OS process execution unit (MUST include the main process).
- **Thread**: an OS thread execution unit within a process.
- **Execution Unit**: a Process or a Thread.
- **Internal function**: a function/method defined in repository source under %%SRC_PATHS%% (only these can appear as call-trace nodes).
- **External boundary**: any call/interaction whose target implementation is not defined under %%SRC_PATHS%% (libraries/frameworks/OS/network/DB/etc.). External boundaries MUST NOT appear as call-trace nodes.
- **Communication Edge**: an explicit runtime interaction between two execution units (direction + mechanism + endpoint/channel + payload/data-shape reference).


## WORKFLOW.md Output Contract (MUST preserve this schema)
- The generated %%DOC_PATH%%/WORKFLOW.md MUST be parser-stable and token-efficient: fixed section order, atomic bullets, deterministic key names, and zero narrative filler.
- The document MUST be structured as:
  - `## Execution Units Index`
  - `## Execution Units` (one subsection per execution unit ID)
  - `## Communication Edges`
- The model MUST cover:
  - ALL processes and threads used at runtime (static analysis), including the main process.
  - For EACH execution unit: a complete internal call-trace tree from entrypoint(s) down to internal leaf functions (internal functions only).
  - ALL explicit communication/interconnection paths between execution units.

## Source Construct Extraction via req --find / req --files-find
When you need hard evidence from source code (APIs, entrypoints, data types, imports, constants, decorators/annotations, modules/namespaces), use req to extract language constructs as structured markdown (with signatures + line ranges, and optional line-numbered code).
### What these commands do (and what they don’t)
- They extract named constructs (e.g., CLASS, FUNCTION, STRUCT, INTERFACE, IMPORT, …) and filter them by TAG and name-regex.
- The regex (PATTERN) matches the construct name only (not the body). If you need “search inside code”, use rg/git grep in addition.
- Output is markdown, grouped by file: header @@@ <filepath> | <language>, then per-construct blocks with:
    - ### <TAG>: <name> + optional Signature + Lines: <start>-<end>
    - optional extracted Doxygen fields (if present in/around the construct)
    - a fenced code block containing the complete construct slice, with comments stripped (strings preserved)
### Choose the right mode
- Project-wide scan (configured --src-dir): use --find (`--here` is implicit; `--base` is forbidden)
    - Correct syntax is: req --find <TAG_FILTER> <NAME_REGEX>
    - Note: --find does not take a filename; it scans all files under the configured source dirs.
- Target specific files: use --files-find (standalone; --here is optional but harmless)
    - Syntax: req --here --files-find <TAG_FILTER> <NAME_REGEX> <FILE1> [FILE2 ...]
### Always enable line-numbered code when you plan to cite evidence
Add --enable-line-numbers so code lines are prefixed as "<n>:":
- req --enable-line-numbers --find "<TAG_FILTER>" "<NAME_REGEX>"
- req --here --enable-line-numbers --files-find "<TAG_FILTER>" "<NAME_REGEX>" <FILE...>
### TAGs and filters
- TAG_FILTER is a pipe-separated list (case-insensitive): e.g. CLASS|FUNCTION|IMPORT
- Tags are language-dependent; unsupported tags are simply ignored for that language, and files may be skipped if none of the requested tags apply.
- To discover the exact supported TAGs list (per language), run: req -h and read the --files-find help section.
- Practical “broad but safe” TAG_FILTER for analysis (cross-language): CLASS|STRUCT|ENUM|INTERFACE|TRAIT|IMPL|FUNCTION|METHOD|MODULE|NAMESPACE|TYPE_ALIAS|TYPEDEF|IMPORT|CONSTANT|VARIABLE|MACRO|DECORATOR|COMPONENT|PROPERTY|PROTOCOL|EXTENSION|UNION
### Regex rules (NAME_REGEX)
- It’s a Python-style regex applied with re.search() against the construct name.
- Prefer anchored patterns when possible:
    - Exact: ^Foo$
    - Prefix: ^parse_
    - Suffix: Service$
    - Fallback: .* (only when scope is already constrained by files/TAGs)
### Failure modes you must handle
- If you get “no constructs found”, adjust one of: TAGs (supported?), file paths, or NAME_REGEX (valid regex?).
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
      - Execute: `git worktree add ../useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID> -b useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`
      - If `.gitignore` excludes `.req/config.json`, copy `.req/config.json` into the new worktree before continuing:
         - `if git check-ignore -q .req/config.json && [ -f .req/config.json ]; then mkdir -p ../useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>/.req && cp .req/config.json ../useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>/.req/config.json; fi`
   - Move into the worktree directory and perform ALL subsequent steps from there:
      - `cd ../useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`
3. Static analysis: build the runtime model from %%SRC_PATHS%%
   - Analyze only files under %%SRC_PATHS%%; treat all files outside %%SRC_PATHS%% as out of scope and never document them.
   - Identify ALL execution units used at runtime:
      - OS processes (MUST include the main process).
      - OS threads (per process), including their entry functions/methods.
      - If no explicit thread creation is present, record "no explicit threads detected" for that process.
   - For EACH execution unit, derive entrypoint(s) and build a complete internal call-trace tree:
      - Include ONLY internal functions as call-trace nodes (defined under %%SRC_PATHS%%).
      - Do NOT include external boundaries (system/library/framework calls) as nodes; annotate them only as external boundaries where relevant.
      - No maximum depth: expand until an internal leaf function or an external boundary is reached.
   - Identify ALL explicit communication edges between execution units and record for each edge:
      - Direction (source -> destination), mechanism (IPC/thread communication), endpoint/channel (queue/topic/path/socket/etc.), and payload/data-shape references.
4. Generate and overwrite `%%DOC_PATH%%/WORKFLOW.md` document
   - Read any existing `%%DOC_PATH%%/WORKFLOW.md` to preserve stable IDs and minimize unnecessary churn, then update it to strictly conform to the Output Contract above.
   - Generate %%DOC_PATH%%/WORKFLOW.md in English only using deterministic, machine-interpretable Markdown with the required schema and stable field order.
      - `## Execution Units Index` (stable IDs)
         - Use stable IDs: `PROC:main`, `PROC:<name>` for processes; `THR:<proc_id>#<name>` for threads.
         - For each execution unit: ID, type (process/thread), parent process (for threads), role, entrypoint symbol(s), and defining file(s).
      - `## Execution Units`
         - One subsection per execution unit ID including:
           - Entrypoint(s)
           - Lifecycle/trigger (how it starts, stops, and loops/blocks)
           - Internal Call-Trace Tree (internal functions only; no maximum depth)
           - External Boundaries (file I/O, network, DB, external APIs, OS interaction)
      - `## Communication Edges`
         - List ALL `Communication Edge` items with direction + mechanism + endpoint/channel + payload/data-shape reference + evidence pointers.
   - Call-trace node format (MUST be consistent):
      - `symbol_name(...)`: `<single-line role>` [`<defining filepath>`]
         - `<optional: brief invariants/external boundaries>`
         - `<child internal calls as nested bullet list, in call order>`
5. **CRITICAL**: Stage & commit
   - Show a summary of changes with `git diff` and `git diff --stat`.
   - Stage changes explicitly (prefer targeted add; avoid `git add -A` if it may include unintended files): `git add <file...>` (ensure to include only `%%DOC_PATH%%/WORKFLOW.md`).
   - Ensure there is something to commit with: `git diff --cached --quiet && echo "Nothing to commit. Aborting."`. If command output contains "Aborting", OUTPUT exactly "No changes to commit.", and then terminate the execution.
   - Commit a structured commit message with: `git commit -m "docs(<COMPONENT>)<BREAKING>: <DESCRIPTION> [useReq]"`
      - Set `<COMPONENT>` to the most specific component, module, or function affected. If multiple areas are touched, choose the primary one. If you cannot identify a unique component, use `core`.
      - Set `<DESCRIPTION>` to a short, clear summary in **English language** of what changed, including (when applicable) updates to: requirements/specs, source code, tests. Use present tense, avoid vague wording, and keep it under ~80 characters if possible.
      - Set `<BREAKING>` to `!` if a breaking change was implemented (a modification to an API, library, or system that breaks backward compatibility, causing dependent client applications or code to fail or behave incorrectly), set empty otherwise.
      - Include main features added, requirements changes, or a bug-fix description adding a multi-line comment (maximum 10 lines).
         - Do not include the 'Co-authored-by' trailer or any AI attribution.
   - Confirm the repo is clean with `git status --porcelain`. If it is NOT empty, override the final line with EXACTLY "WARNING: Workflow request completed with unclean git repository!".
6. **CRITICAL**: Merge Conflict Management
   - Return to the original repository directory (the sibling directory of the worktree). After working in `../useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`, return with: `cd ../<PROJECT_NAME>`
   - Ensure you are on <ORIGINAL_BRANCH>: `git checkout <ORIGINAL_BRANCH>`
   - If `.gitignore` excludes `.req/config.json`, remove the copied `.req/config.json` from the worktree before merge:
      - `if git check-ignore -q .req/config.json; then rm -f ../useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>/.req/config.json; fi`
   - Merge the isolated branch into <ORIGINAL_BRANCH>: `git merge useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`
   - If the merge completes successfully, remove the worktree directory with force and delete the isolated branch: `git worktree remove ../useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID> --force && git branch -D useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`
   - Immediately before proceeding to the next step, verify effective deletion of the worktree directory and isolated branch: `test ! -d ../useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID> && ! git show-ref --verify --quiet refs/heads/useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID> || { printf '%s\n' 'ERROR: Worktree cleanup verification failed!'; }`
   - If the verification command prints any text containing the word "ERROR", OUTPUT exactly "ERROR: Worktree cleanup verification failed!", and then terminate the execution.
   - If the merge fails or results in conflicts, do NOT remove the worktree directory and override the final line with EXACTLY "WARNING: Workflow request completed with merge conflicting!".
7. Present results
   - PRINT, in the response, the results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence). Use the fixed report schema: ## **Outcome**, ## **Requirement Delta**, ## **Design Delta**, ## **Implementation Delta**, ## **Verification Delta**, ## **Evidence**, ## **Assumptions**, ## **Next Workflow**. Final line MUST be exactly: STATUS: OK or STATUS: ERROR.
