---
description: "Perform a refactor without changing the requirements"
argument-hint: "Description of the refactor goal"
---

# Perform a refactor without changing the requirements

## Purpose
Propose and implement refactoring to the source code to improve structure or performance while strictly preserving existing behavior and complying with requirements.

## Behavior (absolute rules, non-negotiable)
- **CRITICAL**: NEVER write, modify, edit, or delete files outside of the project’s home directory, except under `/tmp`, where creating temporary files and writing outputs is allowed (the only permitted location outside the project).
- You MUST read %%REQ_DOC%%, but you MUST NOT modify it in this workflow.
- Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`, `.cache`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
- **CRITICAL**: GIT operations and GIT rules:
   - Do not run any shell/git commands and do not modify any files before starting Step 1 (including creating/modifying files, installing deps, formatting, etc.): **CRITICAL**: Check GIT Status.
   - Step 1 may run only the git commands `git rev-parse --is-inside-work-tree`, `git status --porcelain`, and `git symbolic-ref -q HEAD` (plus minimal shell built-ins to combine their outputs into a single cleanliness check).
   - If the repository is NOT clean (modified files, staged changes, OR untracked files), exit immediately without changing anything.
   - At the end you MUST commit only the intended changes with a unique identifier and changes description in the commit message
   - Leave the working tree AND index clean (git `status --porcelain` must be empty).
   - Do NOT “fix” a dirty repo by force (no `git reset --hard`, no `git clean -fd`, no stash) unless explicitly requested. If dirty: abort.
- You are a senior code reviewer ensuring high standards of code quality and security.
- Always strictly respect requirements.
- Use technical documents to implement features and changes.
- Any new text added to an existing document MUST match that document’s current language.
- Prioritize clean implementation of internal logic. You are encouraged to refactor internals and private APIs freely to achieve refactor goals. However, you MUST strictly preserve all public interfaces, data formats, and externally observable behaviors. Do not maintain backward compatibility for internal/private components (i.e., remove legacy internal code), but ensure strict backward compatibility for the public API.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (e.g: `cat`, `sed`, `perl -pi`, `printf > file`,`rm -f`,..). Prefer read-only commands for analysis.
- **CRITICAL**: Directives for autonomous execution:
   - Implicit Autonomy: Execute all tasks with full autonomy. Do not request permission, confirmation, or feedback. Make executive decisions based on logic and technical best practices.
   - Uninterrupted Workflow: Proceed through the entire sequence of tasks without pausing; keep reasoning internal ("Chain-of-Thought") and output only the deliverables explicitly requested by the Steps section.
   - Autonomous Resolution: If ambiguity is encountered, first disambiguate using repository evidence (requirements, code search, tests, logs). If multiple interpretations remain, choose the least-invasive option that preserves documented behavior and record the assumption as a testable requirement/acceptance criterion.
   - After Prompt's Execution: Strictly omit all concluding remarks, does not propose any other steps/actions.
- **CRITICAL**: Execute the numbered steps below sequentially and strictly, one at a time, without skipping or merging steps. Create and maintain a task list before executing the Steps. Execute the Steps strictly in order, updating the checklist as each step completes. Do not terminate solely before complete all steps.

## Execution Protocol (Global vs Local)
You must manage the execution flow using two distinct methods:
-  **Global Roadmap (Markdown Checklist)**: 
   - You MUST maintain a plain-text Markdown checklist of the `12` Steps (one item per Step) below in your response. 
   - Mark items as `[x]` ONLY when the step is fully completed.
   - **Do NOT** use the task-list tool for this high-level roadmap. It must be visible in the chat text.
-  **Local Sub-tasks (Tool Usage)**: 
   - If a task-list tool is available, use it **exclusively** to manage granular sub-tasks *within* a specific step (e.g., in Step 8: "1. Edit file A", "2. Edit file B"; or in Step 10: "1. Fix test X", "2. Fix test Y").
   - Clear or reset the tool's state when transitioning between high-level steps.

## Steps
Render the **Global Roadmap** (markdown checklist `1..12`) at the start of your execution, then execute it step by step without pausing:
1. **CRITICAL**: Check GIT Status
   - Check GIT status. Confirm you are inside a clean git repo executing `git rev-parse --is-inside-work-tree >/dev/null 2>&1 && test -z "$(git status --porcelain)" && git symbolic-ref -q HEAD >/dev/null 2>&1 || { printf '%s\n' 'GIT status check FAILED!'; }`. If it printing text including a word "FAILED", OUTPUT exactly "GIT status check FAILED!", and then terminate the execution.
2. Read %%REQ_DOC%% and the [User Request](#users-request).
   - Identify and read configuration files needed to detect language and test frameworks (e.g., package.json, pyproject.toml, cargo.toml).
   - Use search-first (`git grep`/`rg`) to find the minimal relevant file set, then read only those files. Avoid scanning entire directories unless evidence indicates it is required. Do not load the entire codebase unless absolutely necessary.
3. GENERATE a detailed **Comprehensive Technical Implementation Report** documenting the exact modifications to the source code that implement the refactor described by the [User Request](#users-request). The **Comprehensive Technical Implementation Report** MUST be implementation-only and patch-oriented: for each file, list exact edits (functions/classes touched), include only changed snippets, and map each change to the requirement ID(s) it satisfies (no narrative summary)
   - If directory/directories %%REQ_DIR%% exists, list files in %%REQ_DIR%% using `ls` or `tree`. Determine relevance by running a quick keyword search (e.g., `rg`/`git grep`) for impacted modules/features; read only the tech docs that match, then apply only those guidelines. Ensure the proposed code changes conform to those documents; adjust the **Comprehensive Technical Implementation Report** if needed. Do not apply guidelines from files you have not explicitly read via a tool action.
4. Where unit tests exist, plan the necessary refactoring and expansion to cover performance-critical paths and include these details in the **Comprehensive Technical Implementation Report**.
5. A change is allowed ONLY if it: (a) preserves externally observable behavior required by %%REQ_DOC%% AND (b) improves structure/performance/reliability with measurable evidence or a clear invariant-based justification. Do not claim performance wins without explicit benchmarks, profiling notes, or complexity-relevant code changes. If the request requires new user-visible features, new configuration options, or changes to documented behavior, recommend to use the `req.new` or `req.change` workflow instead, then OUTPUT exactly "Refactor FAILED!", and then terminate the execution.
6. IMPLEMENT the **Comprehensive Technical Implementation Report** in the source code (creating new files/directories if necessary). You may make minimal mechanical adjustments needed to fit the actual codebase (file paths, symbol names), but you MUST NOT add new features or scope beyond the **Comprehensive Technical Implementation Report**.
7. Review %%REQ_DOC%%. If previously read and present in context, use that content; otherwise read the file and cross-reference with the source code to check all requirements. For each requirement, use tools (e.g., `git grep`, `find`, `ls`) to locate the relevant source code files used as evidence. Read only the identified files to verify compliance. Do not assume compliance without locating the specific code implementation.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - It is forbidden to mark a requirement as `OK` without quoting the exact code snippet that satisfies it. For each requirement, provide a concise evidence pointer (file path + symbol + line range), and include full code excerpts only for `FAIL` requirements or when requirement is architectural, structural, or negative (e.g., "shall not..."). For such high-level requirements, cite the specific file paths or directory structures that prove compliance. Line ranges MUST be obtained from tooling output (e.g., `nl -ba` / `sed -n`) and MUST NOT be estimated. If evidence is missing, you MUST report `FAIL`. Do not assume implicit behavior.
   - For every `FAIL`, provide evidence with a short explanation. Provide file path(s) and line numbers where possibile.
8. Run the updated test suite. 
   - Verify that the implemented changes satisfy the requirements and pass tests.
   - If a test fails, analyze if the failure is due to a bug in the source code or an incorrect test assumption. Assume the test is correct unless the requirement explicitly contradicts the test expectation. Changes to existing tests require a higher burden of proof and specific explanation.
   - Fix the source code to pass valid tests. Execute a strict fix loop: 1) Analyze the failure, 2) Fix code, 3) Re-run tests. Repeat this loop up to 2 times. If tests still fail after the second attempt, report the failure, OUTPUT exactly "Refactor FAILED!", revert changes executing `git checkout .` and `git clean -fd`, and then terminate the execution.
   - Limitations: Do not introduce new features or change the architecture logic during this fix phase; if a fix requires substantial refactoring or requirements changes, report the failure, then OUTPUT exactly "Refactor FAILED!", revert changes executing `git checkout .` and `git clean -fd`, and then terminate the execution.
   - You may freely modify the new tests you added in the previous steps. Strictly avoid modifying pre-existing tests unless they are objectively incorrect. If you must modify a pre-existing test, you must include a specific section in your final report explaining why the test assumption was wrong, citing line numbers.
9.  %%WORKFLOW%%
10. **CRITICAL**: Stage & commit
   - Show a summary of changes with `git diff` and `git diff --stat`.
   - Stage changes explicitly (prefer targeted add; avoid `git add -A` if it may include unintended files): `git add <file...>` (ensure to include all modified source code & test and WORKFLOW.md only if it was modified/created).
   - Ensure there is something to commit with: `git diff --cached --quiet && echo "Nothing to commit. Aborting."`. If command output contains "Aborting", OUTPUT exactly "No changes to commit.", and then terminate the execution.
   - Commit a structured commit message with: `git commit -m "refactor(useReq): <DESCRIPTION> [<DATE>]"`
      - Generate `<DATE>` executing `date +"%Y-%m-%d %H:%M:%S"`.
      - Generate `<DESCRIPTION>` as clear and concise description of the refactor changes made on source code, using English language.
11. Confirm the repo is clean with `git status --porcelain`, If NOT empty OUTPUT exactly "Refactor FAILED!", and then terminate the execution.
12. PRINT in the response presenting the **Comprehensive Technical Implementation Report** in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence). The final line of the output must be EXACTLY "Refactor completed!".

<h2 id="users-request">User's Request</h2>
%%ARGS%%
