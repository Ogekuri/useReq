---
description: "Fix a defect without changing the requirements"
argument-hint: "Description of the defect/bug to fix"
usage: >
  Select this prompt when behavior is wrong relative to already-existing requirement IDs in %%DOC_PATH%%/REQUIREMENTS.md (a defect), and the intent is to restore compliance without changing the SRS. Prefer a test-oriented fix flow: analyze defect -> add one failing guideline-compliant reproducer test -> implement smallest safe fix -> verify test. Fallback to no-test flow only when that test is too costly or one-test isolation is not feasible. Then update %%DOC_PATH%%/WORKFLOW.md and %%DOC_PATH%%/REFERENCES.md, and commit. Do NOT select if the requested outcome changes requirements/behavior (use /req-change or /req-new), if the goal is structural/performance improvement with no behavioral change (use /req-refactor), or if the primary task is satisfying a set of uncovered requirement IDs (use /req-cover or /req-implement).
---

# Fix a defect without changing the requirements

## Purpose
Restore required behavior by diagnosing and fixing a defect while keeping the normative SRS (`%%DOC_PATH%%/REQUIREMENTS.md`) unchanged, so downstream LLM Agents can treat the fix as a semantics-correcting change rather than a requirements change.

## Scope
In scope: reproduce/triage the defect with concrete evidence and prefer a test-oriented fix flow (analyze defect -> create one guideline-compliant failing test -> implement smallest safe fix under %%SRC_PATHS%% -> verify test), with fallback to analyze -> implement fix -> verify only when building that test is too costly or one-test defect isolation is not feasible; then update `%%DOC_PATH%%/WORKFLOW.md` and `%%DOC_PATH%%/REFERENCES.md`, and commit. Out of scope: editing requirements, adding new features, or refactoring beyond what is necessary to implement the fix safely.


## Professional Personas
- **Act as an Expert Debugger** when diagnosing defects: you MUST identify the failure symptom with concrete evidence (failing test, stack trace) before proposing the fix.
- **Act as a Senior Software Developer** when implementing a defect fix: apply the smallest safe change that restores required behavior while preserving public interfaces.
- **Act as a Business Analyst** when reading `%%DOC_PATH%%/REQUIREMENTS.md` to ensure that fixes or refactors never violate or change existing documented behaviors.
- **Act as a QA Automation Engineer** when validating the fix/refactor: ensure that the test suite passes and that no regressions are introduced.
- **Act as an Expert GitOps Engineer** when executing git workflows, especially when creating/removing/managing git worktrees to isolate changes safely.


## Pre-requisite: Execution Context
- Generate <EXECUTION_ID> from the current date/time (NOT UUID) to keep date traceability in worktree and branch names by executing `date +"%Y%m%d%H%M%S"`.
- Identify the current git branch with `git branch --show-current` and refer to it as <ORIGINAL_BRANCH>.
- Identify the Git project name with `basename "$(git rev-parse --show-toplevel)"` and refer to it as <PROJECT_NAME>.


## Absolute Rules, Non-Negotiable
- **CRITICAL**: NEVER write, modify, edit, or delete files outside of the active git worktree directory, except under `/tmp`, and except for creating/removing the dedicated worktree directory `../useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>` as explicitly required by this workflow.
- You MUST read `%%DOC_PATH%%/REQUIREMENTS.md`, but you MUST NOT modify it in this workflow.
- Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
- **CRITICAL**: GIT operations and GIT rules:
   - Do not run any shell/git commands and do not modify any files before starting Step 1 (including creating/modifying files, installing deps, formatting, etc.): **CRITICAL**: Check GIT Status.
   - Step 1 may run only the git commands `git rev-parse --is-inside-work-tree`, `git rev-parse --verify HEAD`, `git status --porcelain`, and `git symbolic-ref -q HEAD` (plus minimal shell built-ins to combine their outputs into a single cleanliness check).
   - If the repository is NOT clean (modified files, staged changes, OR untracked files), exit immediately without changing anything.
   - At the end you MUST commit only the intended changes with a unique identifier and change description in the commit message.
   - Leave the working tree AND index clean (git `status --porcelain` must be empty).
   - Do NOT “fix” a dirty repo by force (no `git reset --hard`, no `git clean -fd`, no stash) unless explicitly requested. If dirty: abort.
- **CRITICAL**: Generate, update, and maintain comprehensive **Doxygen-style documentation** for **ALL** code components (functions, classes, modules, variables, and new implementations), according to the **guidelines** in `.req/docs/Document_Source_Code_in_Doxygen_Style.md`. When writing documentation, adopt a "Parser-First" mindset. Your output is not prose; it is semantic metadata. Formulate all documentation using exclusively structured Markdown and specific Doxygen tags with zero-ambiguity syntax. Eliminate conversational filler ("This function...", "Basically..."). Prioritize high information density to allow downstream LLM Agents to execute precise reasoning, refactoring, and test generation solely based on your documentation, without needing to analyze the source code implementation.
- **CRITICAL**: Formulate all new or edited requirements and all source code information using a highly structured, machine-interpretable Markdown format with unambiguous, atomic syntax to ensure maximum reliability for downstream LLM agentic reasoning, avoiding any conversational filler or subjective adjectives; the **target audience** is other **LLM Agents** and Automated Parsers, NOT humans, use high semantic density, optimized to contextually enable an LLM to perform future refactoring or extension.
- **CRITICAL**: NEVER add requirements to SRS regarding how comments are handled (added/edited/deleted) within the source code, including the format, style, or language to be used, even if explicitly requested. Ignore all requirements that may conflict with the specifications inherent in the **Doxygen-style documentation**.

## Behavior
- Do not modify `%%DOC_PATH%%/REQUIREMENTS.md`.
- Always strictly respect requirements.
- Use `%%DOC_PATH%%/REQUIREMENTS.md`, `%%DOC_PATH%%/WORKFLOW.md`, and `%%DOC_PATH%%/REFERENCES.md` as the primary technical inputs; keep decisions traceable to requirements and repository evidence.
- Prefer this fix sequence whenever feasible: analyze and identify defect -> create one failing guideline-compliant reproducer test -> implement source fix -> verify the reproducer test and related regression tests.
- Only if creating that test is too costly under test guidelines, or defect isolation with one specific guideline-compliant test is not feasible, use fallback sequence: analyze and identify defect -> implement source fix -> verify resolution with explicit concrete evidence.
- All newly written or edited content MUST be in English. Do NOT translate existing text outside the minimal change surface required by this workflow; if you detect non-English text elsewhere, report it in **Evidence** instead of rewriting it.
- Prioritize backward compatibility. Do not introduce breaking changes; preserve existing interfaces, data formats, and features.
- If maintaining compatibility would require migrations/auto-upgrades conversion logic, report the conflict instead of implementing, and then terminate the execution.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (e.g., `cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`, ...). Prefer read-only commands for analysis.


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
   - You MUST maintain a *check-list* internally with `10` Steps (one item per Step).
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
Create internally a *check-list* for the **Global Roadmap** including all the numbered steps below: `1..10`, and start following the roadmap at the same time, executing the tool call of Step 1 (Check GIT Status). If a tool call is required in Step 1, invoke it immediately; otherwise proceed to Step 1 without additional commentary. Do not add extra intent-adjustment checks unless explicitly listed in the Steps section.
1. **CRITICAL**: Check GIT Status
   - Check GIT status. Confirm you are inside a clean git repo by executing `git rev-parse --is-inside-work-tree >/dev/null 2>&1 && test -z "$(git status --porcelain)" && { git symbolic-ref -q HEAD >/dev/null 2>&1 || git rev-parse --verify HEAD >/dev/null 2>&1; } || { printf '%s\n' 'ERROR: Git status unclear!'; }`. If it prints any text containing the word "ERROR", OUTPUT exactly "ERROR: Git status unclear!", and then terminate the execution.
2. **CRITICAL**: Check `%%DOC_PATH%%/REQUIREMENTS.md`, `%%DOC_PATH%%/WORKFLOW.md` and `%%DOC_PATH%%/REFERENCES.md` file presence
   - If the `%%DOC_PATH%%/REQUIREMENTS.md` file does NOT exist, OUTPUT exactly "ERROR: File %%DOC_PATH%%/REQUIREMENTS.md does not exist, generate it with the /req-write prompt!", and then terminate the execution.
   - If the `%%DOC_PATH%%/WORKFLOW.md` file does NOT exist, OUTPUT exactly "ERROR: File %%DOC_PATH%%/WORKFLOW.md does not exist, generate it with the /req-workflow prompt!", and then terminate the execution.
   - If the `%%DOC_PATH%%/REFERENCES.md` file does NOT exist, OUTPUT exactly "ERROR: File %%DOC_PATH%%/REFERENCES.md does not exist, generate it with the /req-references prompt!", and then terminate the execution.
3. **CRITICAL**: Worktree Generation & Isolation
   - Generate <EXECUTION_ID> from the current date/time (NOT UUID) to keep date traceability in worktree and branch names by executing `date +"%Y%m%d%H%M%S"`.
   - Identify the current git branch with `git branch --show-current` and refer to it as <ORIGINAL_BRANCH>.
   - Identify the Git project name with `basename "$(git rev-parse --show-toplevel)"` and refer to it as <PROJECT_NAME>.
   - Create a dedicated worktree OUTSIDE the current repository directory to isolate changes:
      - Execute: `git worktree add ../useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID> -b useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`
      - If `.gitignore` excludes `.req/config.json`, copy `.req/config.json` into the new worktree before continuing:
         - `if git check-ignore -q .req/config.json && [ -f .req/config.json ]; then mkdir -p ../useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>/.req && cp .req/config.json ../useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>/.req/config.json; fi`
   - Move into the worktree directory and perform ALL subsequent steps from there:
      - `cd ../useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`
4. Read requirements, generate **Design Delta** and implement the **Implementation Delta** to fix the defect
   - Using [User Request](#users-request) as a unified semantic framework, extract all directly and tangentially related information from `%%DOC_PATH%%/REQUIREMENTS.md`, `%%DOC_PATH%%/WORKFLOW.md` and `%%DOC_PATH%%/REFERENCES.md`, prioritizing high recall to capture every borderline connection across both sources, to identify the most likely related files and functions based on explicit evidence, and treat any uncertain links as candidates without claiming completeness, then analyze the involved source code from %%SRC_PATHS%% and GENERATE a detailed **Implementation Delta** documenting the exact modifications to the source code that fix the bug/defect described by the [User Request](#users-request). The **Implementation Delta** MUST be implementation-only and patch-oriented: for each file, list exact edits (functions/classes touched), include only changed snippets, and map each change to the requirement ID(s) it satisfies (no narrative summary)
      - **ENFORCEMENT**: The definition of "valid code" strictly includes its documentation. You are mandatorily required to apply the Doxygen-LLM Standard defined in `.req/docs/Document_Source_Code_in_Doxygen_Style.md` to every single code component. Any code block generated without this specific documentation format is considered a compilation error and must be rejected/regenerated.
      - Read %%GUIDELINES_FILES%% files and apply those **guidelines**; ensure the proposed code changes conform to those **guidelines**, and adjust the **Implementation Delta** if needed. Do not apply unrelated **guidelines**.
   - From %%TEST_PATH%%, locate and read only the unit tests that are relevant to the affected requirement IDs and touched modules (via targeted search), then prefer adding one specific failing reproducer test for the defect (guideline-compliant), and include these details in the **Implementation Delta**.
      - **CRITICAL**: All tests MUST implement these instructions: `.req/docs/HDT_Test_Authoring_Guide.md`.
      - Read %%GUIDELINES_FILES%% files and apply those **guidelines**; ensure the proposed code changes conform to those **guidelines**, and adjust the **Implementation Delta** if needed. Do not apply unrelated **guidelines**.
   - A change is allowed ONLY if it corrects behavior that is: (a) explicitly required by `%%DOC_PATH%%/REQUIREMENTS.md` (cite requirement ID/section) OR (b) a defect with concrete evidence (crash, security flaw, data corruption, failing test, or incorrect output that contradicts a specific documented behavior). If the request implies new requirements or changing documented behavior, recommend `/req-new` or `/req-change`, then OUTPUT exactly "ERROR: Defect fix failed due to incompatible requirements!", and then terminate the execution.
   - Preferred execution order for Step 4: analyze/identify defect -> create one failing guideline-compliant reproducer test -> implement source fix. If that test is too costly to build or one-test isolation is not feasible, explicitly declare fallback mode and proceed with analyze/identify defect -> implement source fix.
   - IMPLEMENT the **Implementation Delta** in the source code (creating new files/directories if necessary). You may make minimal mechanical adjustments needed to fit the actual codebase (file paths, symbol names), but you MUST NOT add new features or scope beyond the **Implementation Delta**.
5. Generate **Verification Delta** by testing the implementation result and implementing needed bug fixes
   - Using [User Request](#users-request) as a semantic guide, extract all information from `%%DOC_PATH%%/REQUIREMENTS.md` that is directly or even tangentially related, prioritizing high recall to capture every relevant nuance and borderline connection, to determine related requirements, then analyze them one by one and cross-reference them with the source code. For each requirement, use tools (e.g., `git grep`, `find`, `ls`) to locate the relevant source code files used as evidence, read only the identified files to verify compliance, and do not assume compliance without locating the specific code implementation.
      - For each requirement, report `OK` if satisfied or `FAIL` if not.
      - Do not mark a requirement as `OK` without code evidence; for `OK` items provide only a compact pointer (file path + symbol + line range). For each requirement, provide a concise evidence pointer (file path + symbol + line range) excerpts only for `FAIL` requirements or when requirement is architectural, structural, or negative (e.g., "MUST NOT ..."). For such high-level requirements, cite the specific file paths or directory structures that prove compliance. Line ranges MUST be obtained from tooling output (e.g., `nl -ba` / `sed -n`) and MUST NOT be estimated. If evidence is missing, you MUST report `FAIL`. Do not assume implicit behavior.
      - For every `FAIL`, provide evidence with a short explanation. Provide file path(s) and line numbers where possible.
   - Perform a static analysis check by executing `req --here --static-check`.
      - Review the produced output and fix every reported issue in source code and tests.
      - Re-run `req --here --static-check` until it produces no issues. Do not proceed to regression tests until it is clean.
   - Perform a regression test by executing ALL tests in the test suite.
      - Verify that the implemented changes satisfy the requirements and pass tests.
      - If Step 4 used preferred test-oriented flow, the reproducer test MUST fail before the fix and MUST pass after the fix; include this before/after evidence.
      - If Step 4 used fallback no-test flow, you MUST provide explicit concrete verification evidence that the defect is resolved and explain why guideline-compliant one-test reproduction was not feasible or was too costly.
      - If a test fails, analyze if the failure is due to a bug in the source code or an incorrect test assumption. Assume the test is correct unless the requirement explicitly contradicts the test expectation. Changes to existing tests require a higher burden of proof and specific explanation.
      - Fix the source code to pass valid tests autonomously without asking for user intervention. Execute a strict fix loop: 1) Read and analyze the specific failure output/logs using filesystem tools, 2) Analyze the root cause internally based on evidence, 3) Fix code, 4) Re-run tests. Repeat this loop up to 2 times. If tests still fail after the second attempt, report the failure, OUTPUT exactly "ERROR: Defect fix failed due to inability to complete tests!", revert tracked-file changes using `git restore .` (or `git checkout .` on older Git), DO NOT run `git clean -fd`, and then terminate the execution.
      - Limitations: Do not introduce new features or change the architecture logic during this fix phase; if a fix requires substantial refactoring or requirements changes, report the failure, then OUTPUT exactly "ERROR: Defect fix failed due to requirements incompatible with tests!", revert tracked-file changes using `git restore .` (or `git checkout .` on older Git), DO NOT run `git clean -fd`, and then terminate the execution.
      - You may freely modify the new tests you added in the previous steps. Strictly avoid modifying pre-existing tests unless they are objectively incorrect. If you must modify a pre-existing test, you must include a specific section in your final report explaining why the test assumption was wrong, citing line numbers.
6. Update `%%DOC_PATH%%/WORKFLOW.md` via targeted edits using the canonical WORKFLOW.md contract (same terminology, same schema, same call-trace rules).
   - Update `%%DOC_PATH%%/WORKFLOW.md` as an LLM-first runtime model (English only) using a TARGETED EDIT policy.
      - Determine the change surface from repository evidence: run `git diff --name-only` and `git diff` to identify the modified files/symbols under %%SRC_PATHS%%.
      - Modify ONLY the WORKFLOW.md sections impacted by those changes (execution unit index entries, execution unit subsections, and communication edges); preserve stable IDs and do not rewrite unrelated content.
      - Ensure global consistency: if a changed internal symbol appears in any call-trace, update all affected call-trace nodes; if a unit/edge is added/removed, reflect it.
   - Analyze only files under %%SRC_PATHS%% (everything else is out of scope) and identify ALL runtime execution units:
      - OS processes (MUST include the main process).
      - OS threads (per process), including their entry functions/methods.
      - If no explicit thread creation is present, record "no explicit threads detected" for that process.
   - For EACH execution unit, generate a complete internal call-trace tree starting from its entrypoint(s):
      - Include ONLY internal functions/methods defined in repository source under %%SRC_PATHS%%.
      - Do NOT include external boundaries (system/library/framework calls) as nodes; annotate them only as external boundaries where relevant.
      - No maximum depth: expand until an internal leaf function or an external boundary is reached.
   - Identify and document ALL Communication Edges between Execution Units:
      - For each edge: direction (source -> destination), mechanism, endpoint/channel, payload/data-shape reference, and evidence pointers.
   - Preserve and maintain the canonical `WORKFLOW.md` schema:
      - `## Execution Units Index`
      - `## Execution Units`
      - `## Communication Edges`
   - Use stable execution unit IDs: `PROC:main`, `PROC:<name>` for processes; `THR:<proc_id>#<name>` for threads.
   - Call-trace node format (MUST be consistent):
      - `symbol_name(...)`: `<single-line role>` [`<defining filepath>`]
         - `<optional: brief invariants/external boundaries>`
         - `<child internal calls as nested bullet list, in call order>`
7. Update `%%DOC_PATH%%/REFERENCES.md` references file
   -  Create/update the references file with `req --here --references >"%%DOC_PATH%%/REFERENCES.md"`
8. **CRITICAL**: Stage & commit
   - Show a summary of changes with `git diff` and `git diff --stat`.
   - Stage changes explicitly (prefer targeted add; avoid `git add -A` if it may include unintended files): `git add <file...>` (ensure to include all modified source code & test and WORKFLOW.md only if it was modified/created).
   - Ensure there is something to commit with: `git diff --cached --quiet && echo "Nothing to commit. Aborting."`. If command output contains "Aborting", OUTPUT exactly "No changes to commit.", and then terminate the execution.
   - Commit a structured commit message with: `git commit -m "fix(<COMPONENT>)<BREAKING>: <DESCRIPTION> [useReq]"`
      - Set `<COMPONENT>` to the most specific component, module, or function affected. If multiple areas are touched, choose the primary one. If you cannot identify a unique component, use `core`.
      - Set `<DESCRIPTION>` to a short, clear summary in **English language** of what changed, including (when applicable) updates to: requirements/specs, source code, tests. Use present tense, avoid vague wording, and keep it under ~80 characters if possible.
      - Set `<BREAKING>` to `!` if a breaking change was implemented (a modification to an API, library, or system that breaks backward compatibility, causing dependent client applications or code to fail or behave incorrectly), set empty otherwise.
      - Include main features added, requirements changes, or a bug-fix description adding a multi-line comment (maximum 10 lines).
         - Do not include the 'Co-authored-by' trailer or any AI attribution.
   - Confirm the repo is clean with `git status --porcelain`. If it is NOT empty, override the final line with EXACTLY "WARNING: Defect fix completed with unclean git repository!".
9.  **CRITICAL**: Merge Conflict Management
   - Return to the original repository directory (the sibling directory of the worktree). After working in `../useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`, return with: `cd ../<PROJECT_NAME>`
   - Ensure you are on <ORIGINAL_BRANCH>: `git checkout <ORIGINAL_BRANCH>`
   - If `.gitignore` excludes `.req/config.json`, remove the copied `.req/config.json` from the worktree before merge:
      - `if git check-ignore -q .req/config.json; then rm -f ../useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>/.req/config.json; fi`
   - Merge the isolated branch into <ORIGINAL_BRANCH>: `git merge useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`
   - If the merge completes successfully, remove the worktree directory with force and delete the isolated branch: `git worktree remove ../useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID> --force && git branch -D useReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`
   - If the merge fails or results in conflicts, do NOT remove the worktree directory and override the final line with EXACTLY "WARNING: Defect fix completed with merge conflicting!".
10. Present results
   - PRINT, in the response, the results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence). Use the fixed report schema: ## **Outcome**, ## **Requirement Delta**, ## **Design Delta**, ## **Implementation Delta**, ## **Verification Delta**, ## **Evidence**, ## **Assumptions**, ## **Next Workflow**. Final line MUST be exactly: STATUS: OK or STATUS: ERROR.

<h2 id="users-request">User's Request</h2>
%%ARGS%%
