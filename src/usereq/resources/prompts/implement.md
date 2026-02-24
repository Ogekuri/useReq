---
description: "Implement source code from requirements (from scratch)"
argument-hint: "No arguments utilized by the prompt logic"
usage: >
  Select this prompt when %%DOC_PATH%%/REQUIREMENTS.md is already authoritative and stable, but the codebase under %%SRC_PATHS%% is missing large parts of the required functionality (greenfield or major gaps) and you must build an end-to-end implementation (including creating new modules/files and tests under %%TEST_PATH%%) WITHOUT changing requirements. Do NOT select if only a small/known set of requirement IDs is uncovered in an otherwise working codebase (use /req-cover), if you need to modify or add requirements (use /req-change or /req-new), or if the task is a narrow defect fix or refactor (use /req-fix or /req-refactor). Do NOT select for auditing/triage (use /req-check or /req-analyze).
---

# Implement source code from requirements from scratch

## Purpose
Produce a working implementation from the normative SRS (`%%DOC_PATH%%/REQUIREMENTS.md`) by building missing functionality end-to-end (including “from scratch” where needed), so the codebase becomes fully compliant with the documented requirement IDs without changing those requirements.

## Scope
In scope: read `%%DOC_PATH%%/REQUIREMENTS.md`, implement/introduce source under %%SRC_PATHS%% (including new modules/files), add tests under %%TEST_PATH%%, verify via the test suite, update `%%DOC_PATH%%/WORKFLOW.md` and `%%DOC_PATH%%/REFERENCES.md`, and commit. Out of scope: editing requirements or introducing features not present in the SRS (use `/req-change` or `/req-new` to evolve requirements first).


## Professional Personas
- **Act as a QA Automation Engineer** when identifying uncovered requirements: you must prove the lack of coverage through code analysis or failing test scenarios.
- **Act as a Business Analyst** when mapping requirement IDs from `%%DOC_PATH%%/REQUIREMENTS.md` to observable behaviors.
- **Act as a Senior System Architect** when generating the **Implementation Delta** and planning the coverage strategy: ensure the new implementation integrates perfectly with the existing architecture without regressions.
- **Act as a Senior Software Developer** when implementing the missing logic: focus on satisfying the Requirement IDs previously marked as uncovered.
- **Act as a QA Engineer** during verification and testing Steps: verify compliance with zero leniency, using mandatory code evidence and strict test-fix loops to ensure stability.
- **Act as an Expert GitOps Engineer** when executing git workflows, especially when creating/removing/managing git worktrees to isolate changes safely.


## Pre-requisite: Execution Context
- Generate a pseudo-random UUID v4 (or an equivalent unique alphanumeric tag) to identify the current operation, and refer to it as <EXECUTION_ID>. If available, use `uuidgen`.
- Identify the current git branch with `git branch --show-current` and refer to it as <ORIGINAL_BRANCH>.
- Identify the Git project name with `basename "$(git rev-parse --show-toplevel)"` and refer to it as <PROJECT_NAME>.


## Absolute Rules, Non-Negotiable
- **CRITICAL**: NEVER write, modify, edit, or delete files outside of the active git worktree directory, except under `/tmp`, and except for creating/removing the dedicated worktree directory `../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>` as explicitly required by this workflow.
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
- **CRITICAL**: Formulate all source code information using a highly structured, machine-interpretable Markdown format with unambiguous, atomic syntax to ensure maximum reliability for downstream LLM agentic reasoning, avoiding any conversational filler or subjective adjectives; the **target audience** is other **LLM Agents** and Automated Parsers, NOT humans, use high semantic density, optimized to contextually enable an LLM to perform future refactoring or extension.
  
## Behavior
- Do not modify `%%DOC_PATH%%/REQUIREMENTS.md`.
- Always strictly respect requirements.
- Use `%%DOC_PATH%%/REQUIREMENTS.md`, `%%DOC_PATH%%/WORKFLOW.md`, and `%%DOC_PATH%%/REFERENCES.md` as the primary technical inputs; keep decisions traceable to requirements and repository evidence.
- All newly written or edited content MUST be in English. Do NOT translate existing text outside the minimal change surface required by this workflow; if you detect non-English text elsewhere, report it in **Evidence** instead of rewriting it.
- Prioritize backward compatibility. Do not introduce breaking changes; preserve existing interfaces, data formats, and features. If maintaining compatibility would require migrations/auto-upgrades conversion logic, report the conflict instead of implementing, and then terminate the execution.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (e.g., `cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`, ...). Prefer read-only commands for analysis.


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
2. **CRITICAL**: Worktree Generation & Isolation
   - Generate a pseudo-random UUID v4 (or an equivalent unique alphanumeric tag) to identify the current operation, and refer to it as <EXECUTION_ID>. If available, use `uuidgen`.
   - Identify the current git branch with `git branch --show-current` and refer to it as <ORIGINAL_BRANCH>.
   - Identify the Git project name with `basename "$(git rev-parse --show-toplevel)"` and refer to it as <PROJECT_NAME>.
   - Create a dedicated worktree OUTSIDE the current repository directory to isolate changes:
      - Execute: `git worktree add ../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID> -b userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`
      - If `.gitignore` excludes `.req/config.json`, copy `.req/config.json` into the new worktree before continuing:
         - `if git check-ignore -q .req/config.json && [ -f .req/config.json ]; then mkdir -p ../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>/.req && cp .req/config.json ../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>/.req/config.json; fi`
   - Move into the worktree directory and perform ALL subsequent steps from there:
      - `cd ../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`
3. Read requirements, generate **Design Delta** and implement the **Implementation Delta** to cover all requirements
   - Read `%%DOC_PATH%%/REQUIREMENTS.md` and GENERATE a detailed **Implementation Delta** that covers all explicitly specified requirements, and explicitly list any requirement that cannot be implemented due to missing information or repository constraints. The **Implementation Delta** MUST be implementation-only: for each file, list exact developments (functions/classes created), and map each implementation to the requirement ID(s) it satisfies (no narrative summary).
      - **ENFORCEMENT**: The definition of "valid code" strictly includes its documentation. You are mandatorily required to apply the Doxygen-LLM Standard defined in `.req/docs/Document_Source_Code_in_Doxygen_Style.md` to every single code component. Any code block generated without this specific documentation format is considered a compilation error and must be rejected/regenerated.
      - Read %%GUIDELINES_FILES%% files and apply those **guidelines**; ensure the proposed code changes conform to those **guidelines**, and adjust the **Implementation Delta** if needed. Do not apply unrelated **guidelines**.
   - Implement the unit test source code from scratch, plan the necessary implementations to cover ALL requirements, and include these details in the **Implementation Delta**.
      - **CRITICAL**: All tests MUST implement these instructions: `.req/docs/HDT_Test_Authoring_Guide.md`.
      - Read %%GUIDELINES_FILES%% files and apply those **guidelines**; ensure the proposed code changes conform to those **guidelines**, and adjust the **Implementation Delta** if needed. Do not apply unrelated **guidelines**.
   - IMPLEMENT the **Implementation Delta** in the source code (creating new files/directories if necessary) from scratch.
4. Generate **Verification Delta** by testing the implementation result and implementing needed bug fixes
   - Read ALL requirements from `%%DOC_PATH%%/REQUIREMENTS.md`, analyze them one by one, and cross-reference them with the source code to check requirements. For each requirement, use tools (e.g., `git grep`, `find`, `ls`) to locate the relevant source code files used as evidence, read only the identified files to verify compliance, and do not assume compliance without locating the specific code implementation.
      - For each requirement, report `OK` if satisfied or `FAIL` if not.
      - Do not mark a requirement as `OK` without code evidence; for `OK` items provide only a compact pointer (file path + symbol + line range). For each requirement, provide a concise evidence pointer (file path + symbol + line range) excerpts only for `FAIL` requirements or when requirement is architectural, structural, or negative (e.g., "MUST NOT ..."). For such high-level requirements, cite the specific file paths or directory structures that prove compliance. Line ranges MUST be obtained from tooling output (e.g., `nl -ba` / `sed -n`) and MUST NOT be estimated. If evidence is missing, you MUST report `FAIL`. Do not assume implicit behavior.
      - For every `FAIL`, provide evidence with a short explanation. Provide file path(s) and line numbers where possible.
   - Perform a static analysis check by executing `req --here --static-check`.
      - Review the produced output and fix every reported issue in source code and tests.
      - Re-run `req --here --static-check` until it produces no issues. Do not proceed to regression tests until it is clean.
   - Perform a regression test by executing ALL tests in the test suite.
      - Verify that the implemented changes satisfy the requirements and pass tests.
      - If a test fails, determine whether the failure is due to a bug in the source code or an incorrect test assumption. Do NOT modify pre-existing tests unless they are objectively incorrect or inconsistent with `%%DOC_PATH%%/REQUIREMENTS.md`; otherwise treat failures as regressions and fix the source code.
      - Fix the source code to pass valid tests autonomously without asking for user intervention. Execute a strict fix loop: 1) Read and analyze the specific failure output/logs using filesystem tools, 2) Analyze the root cause internally based on evidence, 3) Fix code, 4) Re-run tests. Repeat this loop up to 2 times. If tests still fail after the second attempt, report the failure, OUTPUT exactly "ERROR: Implement request failed due to inability to complete tests!", revert tracked-file changes using `git restore .` (or `git checkout .` on older Git), DO NOT run `git clean -fd`, and then terminate the execution.
      - Limitations: Do not introduce new features or change the architecture logic during this fix phase; if a fix requires substantial refactoring or requirements changes, report the failure, then OUTPUT exactly "ERROR: Implement request failed due to requirements incompatible with tests!", revert tracked-file changes using `git restore .` (or `git checkout .` on older Git), DO NOT run `git clean -fd`, and then terminate the execution.
      - You may freely modify the new tests you added in the previous steps. Strictly avoid modifying pre-existing tests unless they are objectively incorrect. If you must modify a pre-existing test, you must include a specific section in your final report explaining why the test assumption was wrong, citing line numbers.
5. Static analysis: build the runtime model from %%SRC_PATHS%%
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
6. Generate and overwrite `%%DOC_PATH%%/WORKFLOW.md` document
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
7. Update `%%DOC_PATH%%/REFERENCES.md` references file
   -  Create/update the references file with `req --here --references >"%%DOC_PATH%%/REFERENCES.md"`
8. **CRITICAL**: Stage & commit
   - Show a summary of changes with `git diff` and `git diff --stat`.
   - Stage changes explicitly (prefer targeted add; avoid `git add -A` if it may include unintended files): `git add <file...>` (ensure to include all modified source code & test and WORKFLOW.md only if it was modified/created).
   - Ensure there is something to commit with: `git diff --cached --quiet && echo "Nothing to commit. Aborting."`. If command output contains "Aborting", OUTPUT exactly "No changes to commit.", and then terminate the execution.
   - Commit a structured commit message with: `git commit -m "implement(<COMPONENT>)<BREAKING>: <DESCRIPTION> [useReq]"`
      - Set `<COMPONENT>` to the most specific component, module, or function affected. If multiple areas are touched, choose the primary one. If you cannot identify a unique component, use `core`.
      - Set `<DESCRIPTION>` to a short, clear summary in **English language** of what changed, including (when applicable) updates to: requirements/specs, source code, tests. Use present tense, avoid vague wording, and keep it under ~80 characters if possible.
      - Set `<BREAKING>` to `!` if a breaking change was implemented (a modification to an API, library, or system that breaks backward compatibility, causing dependent client applications or code to fail or behave incorrectly), set empty otherwise.
      - Include main features added, requirements changes, or a bug-fix description adding a multi-line comment (maximum 10 lines).
         - Do not include the 'Co-authored-by' trailer or any AI attribution.
   - Confirm the repo is clean with `git status --porcelain`. If it is NOT empty, override the final line with EXACTLY "WARNING: Implement request completed with unclean git repository!".
9. **CRITICAL**: Merge Conflict Management
   - Return to the original repository directory (the sibling directory of the worktree). After working in `../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`, return with: `cd ../<PROJECT_NAME>`
   - Ensure you are on <ORIGINAL_BRANCH>: `git checkout <ORIGINAL_BRANCH>`
   - If `.gitignore` excludes `.req/config.json`, remove the copied `.req/config.json` from the worktree before merge:
      - `if git check-ignore -q .req/config.json; then rm -f ../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>/.req/config.json; fi`
   - Merge the isolated branch into <ORIGINAL_BRANCH>: `git merge userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`
   - If the merge completes successfully, remove the worktree directory with force and delete the isolated branch: `git worktree remove ../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID> --force && git branch -D userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`
   - If the merge fails or results in conflicts, do NOT remove the worktree directory and override the final line with EXACTLY "WARNING: Implement request completed with merge conflicting!".
10. Present results
   - PRINT, in the response, the results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence). Use the fixed report schema: ## **Outcome**, ## **Requirement Delta**, ## **Design Delta**, ## **Implementation Delta**, ## **Verification Delta**, ## **Evidence**, ## **Assumptions**, ## **Next Workflow**. Final line MUST be exactly: STATUS: OK or STATUS: ERROR.
