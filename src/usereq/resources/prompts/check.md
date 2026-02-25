---
description: "Run the requirements check"
argument-hint: "Optional: context to focus the audit (can be empty)"
usage: >
  Select this prompt if you need a complete, repository-read-only compliance audit that outputs an OK/FAIL verdict for EVERY requirement ID in %%DOC_PATH%%/REQUIREMENTS.md, backed by concrete code/test evidence (and typically by running the test suite). Use after requirements/code changes to measure coverage and to produce a gap list + implementation-only technical report when FAILs exist. Do NOT select if you will modify any files (requirements/code/tests/docs) or implement fixes; downstream implementation should be done via /req-cover (small set of uncovered IDs), /req-implement (large/greenfield gaps), /req-fix, /req-refactor, /req-new, or /req-change depending on intent.
---

# Run the requirements check

## Purpose
Provide an evidence-backed compliance audit by running tests and mapping every requirement in the SRS (`%%DOC_PATH%%/REQUIREMENTS.md`) to concrete implementation evidence, so downstream LLM Agents can decide whether coverage work is required and where to apply it.

## Scope
In scope: read `%%DOC_PATH%%/REQUIREMENTS.md` (and related docs), run the test suite as evidence, mark ALL requirements as OK/FAIL with proof, and (only when FAILs exist) produce an implementation-only, patch-oriented technical report. Out of scope: any file modification (requirements/code/tests/docs) or applying fixes.


## Professional Personas
- **Act as a Senior System Engineer** when analyzing source code and directory structures to understand the system's architecture and logic.
- **Act as a Business Analyst** when cross-referencing code findings with `%%DOC_PATH%%/REQUIREMENTS.md` to ensure functional alignment.
- **Act as a Technical Writer** when producing the final analysis report or workflow descriptions, ensuring clarity, technical precision, and structured formatting.
- **Act as a QA Auditor** when reporting facts, requiring concrete evidence (file paths, line numbers) for every finding.
- **Act as an Expert GitOps Engineer** when executing git workflows, especially when creating/removing/managing git worktrees to isolate changes safely.


## Pre-requisite: Execution Context
- Generate <EXECUTION_ID> from the current date/time (NOT UUID) to keep date traceability in worktree and branch names by executing `date +"%Y%m%d%H%M%S"`.
- Identify the current git branch with `git branch --show-current` and refer to it as <ORIGINAL_BRANCH>.
- Identify the Git project name with `basename "$(git rev-parse --show-toplevel)"` and refer to it as <PROJECT_NAME>.


## Absolute Rules, Non-Negotiable
- **CRITICAL**: NEVER write, modify, edit, or delete files outside of the project’s home directory, except under `/tmp`, where creating temporary files and writing outputs is allowed (the only permitted location outside the project).
- You MUST read `%%DOC_PATH%%/REQUIREMENTS.md`, but you MUST NOT modify it in this workflow.
- Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
- **CRITICAL**: Do not modify any git tracked files (i.e., returned by `git ls-files`). You may run commands that create untracked artifacts ONLY if: (a) they are confined to standard disposable locations (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`), (b) they do not change any tracked file contents, and (c) you do NOT rely on those artifacts as permanent outputs. If unsure, run tools in a temporary directory (e.g., `tmp/`, `temp/`, `/tmp`) or use tool flags that disable caches.
- Allowed git commands in this workflow (read-only only): `git status`, `git diff`, `git ls-files`, `git grep`, `git rev-parse`, `git branch --show-current`. Do NOT run any other git commands.

## Behavior
- Only analyze the code and test execution and present the results; make no changes.
- Do NOT create or modify tests in this workflow.
- Report facts: for each finding include file paths and, when useful, line numbers or short code excerpts.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read files as needed (read-only only; e.g., `cat`, `sed -n`, `head`, `tail`, `rg`, `less`).


## WORKFLOW.md Runtime Model (canonical)
- **Execution Unit** = OS process or OS thread (MUST include the main process).
- **Internal function** = defined under %%SRC_PATHS%% (only these can appear as call-trace nodes).
- **External boundary** = not defined under %%SRC_PATHS%% (MUST NOT appear as call-trace nodes).
- `%%DOC_PATH%%/WORKFLOW.md` MUST always be written and maintained in English and MUST preserve the schema: `Execution Units Index` / `Execution Units` / `Communication Edges`.

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
   - You MUST maintain a *check-list* internally with `3` Steps (one item per Step).
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
Create internally a *check-list* for the **Global Roadmap** including all the numbered steps below: `1..3`, and start following the roadmap at the same time, following the instructions of Step 1 (Check file presence). If a tool call is required in Step 1, invoke it immediately; otherwise proceed to Step 1 without additional commentary. Do not add extra intent-adjustment checks unless explicitly listed in the Steps section.
1. **CRITICAL**: Check `%%DOC_PATH%%/REQUIREMENTS.md`, `%%DOC_PATH%%/WORKFLOW.md` and `%%DOC_PATH%%/REFERENCES.md` file presence
   - If the `%%DOC_PATH%%/REQUIREMENTS.md` file does NOT exist, OUTPUT exactly "ERROR: File %%DOC_PATH%%/REQUIREMENTS.md does not exist, generate it with the /req-write prompt!", and then terminate the execution.
   - If the `%%DOC_PATH%%/WORKFLOW.md` file does NOT exist, OUTPUT exactly "ERROR: File %%DOC_PATH%%/WORKFLOW.md does not exist, generate it with the /req-workflow prompt!", and then terminate the execution.
   - If the `%%DOC_PATH%%/REFERENCES.md` file does NOT exist, OUTPUT exactly "ERROR: File %%DOC_PATH%%/REFERENCES.md does not exist, generate it with the /req-references prompt!", and then terminate the execution.
2. Run test suite, check requirements coverage and generate **Implementation Delta**
   - Run the test suite to verify the current state. Do not modify the source code or tests. Record the test results (`OK`/`FAIL`) to be used as evidence for the final analysis report. If tests fail, continue anyway and record the failures as evidence.
   - Read `%%DOC_PATH%%/REQUIREMENTS.md` and cross-reference with the source code from %%SRC_PATHS%%, %%TEST_PATH%% to check ALL requirements, but use progressive disclosure: provide full evidence only for `FAIL` items and a compact pointer-only index for `OK` items. For each requirement, use tools (e.g., `git grep`, `find`, `ls`) to locate the relevant source code files used as evidence, read only the identified files to verify compliance and do not assume compliance without locating the specific code implementation.
      - For each requirement, report `OK` if satisfied or `FAIL` if not.
      - Do not mark a requirement as `OK` without code evidence; for `OK` items provide only a compact pointer (file path + symbol + line range). For each requirement, provide a concise evidence pointer (file path + symbol + line range) excerpts only for `FAIL` requirements or when requirement is architectural, structural, or negative (e.g., "MUST NOT ..."). For such high-level requirements, cite the specific file paths or directory structures that prove compliance. Line ranges MUST be obtained from tooling output (e.g., `nl -ba` / `sed -n`) and MUST NOT be estimated. If evidence is missing, you MUST report `FAIL`. Do not assume implicit behavior.
      - For every `FAIL`, provide evidence with a short explanation. Provide file path(s) and line numbers where possible.
   - **CRITICAL**: If all requirements report `OK`, OUTPUT exactly "All requirements are already covered. No changes needed.", and then terminate the execution.
   - If there are uncovered requirements, using uncovered requirements from `%%DOC_PATH%%/REQUIREMENTS.md` and [User Request](#users-request) as a semantic guide, extract all information from `%%DOC_PATH%%/WORKFLOW.md` that is directly or even tangentially related, prioritizing high recall to capture every relevant nuance and borderline connection, to identify the most likely related files and functions based on explicit evidence, and treat any uncertain links as candidates without claiming completeness, then analyze the involved source code from %%SRC_PATHS%% and GENERATE a detailed **Implementation Delta** documenting the exact modifications to the source code that will cover all `FAIL` requirements. The **Implementation Delta** MUST be implementation-only and patch-oriented: for each file, list exact edits (functions/classes touched), include only changed snippets, and map each change to the requirement ID(s) it satisfies (no narrative summary)
      - **ENFORCEMENT**: The definition of "valid code" strictly includes its documentation. You are mandatorily required to apply the Doxygen-LLM Standard defined in `.req/docs/Document_Source_Code_in_Doxygen_Style.md` to every single code component. Any code block generated without this specific documentation format is considered a compilation error and must be rejected/regenerated.
      - Read %%GUIDELINES_FILES%% files and apply those **guidelines**; ensure the proposed code changes conform to those **guidelines**, and adjust the **Implementation Delta** if needed. Do not apply unrelated **guidelines**.
   - From %%TEST_PATH%%, locate and read only the unit tests that are relevant to the affected requirement IDs and touched modules (via targeted search), and plan the necessary refactoring/additions to cover uncovered requirements and include these details in the **Implementation Delta**.
      - **CRITICAL**: If you propose new tests, they MUST implement these instructions: `.req/docs/HDT_Test_Authoring_Guide.md`.
      - Read %%GUIDELINES_FILES%% files and apply those **guidelines**; ensure the proposed code changes conform to those **guidelines**, and adjust the **Implementation Delta** if needed. Do not apply unrelated **guidelines**.
3. Present results and **Implementation Delta**
   - PRINT, in the response, the results of the requirements check and the **Implementation Delta** in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence). Use the fixed report schema: ## **Outcome**, ## **Requirement Delta**, ## **Design Delta**, ## **Implementation Delta**, ## **Verification Delta**, ## **Evidence**, ## **Assumptions**, ## **Next Workflow**. Final line MUST be exactly: STATUS: OK or STATUS: ERROR.

<h2 id="users-request">User's Request</h2>
%%ARGS%%
