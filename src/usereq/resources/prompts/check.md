---
description: "Run the requirements check"
argument-hint: "No arguments utilized by the prompt logic"
---

# Run the requirements check

## Purpose
Verify that the project's source code satisfies the documented requirements and pass the test suite, reporting the status of each requirement without modifying any files.
 
## Behavior (absolute rules, non-negotiable)
- **CRITICAL**: NEVER write, modify, edit, or delete files outside of the project’s home directory, except under `/tmp`, where creating temporary files and writing outputs is allowed (the only permitted location outside the project).
- You MUST read %%REQ_DOC%%, but you MUST NOT modify it in this workflow.
- Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`,`.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
- **CRITICAL**: Do not modify any git tracked files (i.e., returned by `git ls-files`). You may run commands that create untracked artifacts ONLY if: (a) they are confined to standard disposable locations (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`,`node_modules/.cache`, `/tmp`), (b) they do not change any tracked file contents, and (c) you do NOT rely on those artifacts as permanent outputs. If unsure, run tools in a temporary directory (eg., `tmp/`, `temp/`, `/tmp`) or use tool flags that disable caches.
- Allowed git commands in this workflow (read-only only): `git status`, `git diff`, `git ls-files`, `git grep`, `git rev-parse`. Do NOT run any other git commands.
- Only analyze the code and test execution and present the results; make no changes.
- Do NOT create or modify tests in this workflow.
- Report facts: for each finding include file paths and, when useful, line numbers or short code excerpts.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`,`PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read files as needed (read-only only; e.g., `cat`, `sed -n`, `head`, `tail`, `rg`, `less`).
- **CRITICAL**: Directives for autonomous execution:
   - Implicit Autonomy: Execute all tasks with full autonomy. Do not request permission, confirmation, or feedback. Make executive decisions based on logic and technical best practices.
   - Uninterrupted Workflow: Proceed through the entire sequence of tasks without pausing; keep reasoning internal ("Chain-of-Thought") and output only the deliverables explicitly requested by the Steps section.
   - Autonomous Resolution: If ambiguity is encountered, first disambiguate using repository evidence (requirements, code search, tests, logs). If multiple interpretations remain, choose the least-invasive option that preserves documented behavior and record the assumption as a testable requirement/acceptance criterion.
   - After Prompt's Execution: Strictly omit all concluding remarks, does not propose any other steps/actions.
- **CRITICAL**: Execute the steps below sequentially and strictly, one at a time, without skipping or merging steps. Check if a TODO LIST tool is available, you MUST use todo tool to create the to-do list exactly as written and then follow it step by step without pausing. If TODO LIST tool is NOT available OUTPUT exactly "TODO LIST tool check FAILED!", and then terminate the execution.

## Steps
Internally generate a task list based strictly on the steps below, then execute it step by step without pausing:
1. Run the test suite to verify the current state. Do not modify the source code or tests. Record the test results (`OK`/`FAIL`) to be used as evidence for the final analysis report. If tests fail, continue to Step 2.
2. Read %%REQ_DOC%%. If previously read and present in context, use that content; otherwise read the file and cross-reference with the source code to check all requirements. For each requirement, use tools (e.g., `git grep`, `find`, `ls`) to locate the relevant source code files used as evidence. Read only the identified files to verify compliance. Do not assume compliance without locating the specific code implementation.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - It is forbidden to mark a requirement as `OK` without quoting the exact code snippet that satisfies it. For each requirement, provide a concise evidence pointer (file path + symbol + line range), and include full code excerpts only for `FAIL` requirements or when requirement is architectural, structural, or negative (e.g., "shall not..."). For such high-level requirements, cite the specific file paths or directory structures that prove compliance. Line ranges MUST be obtained from tooling output (e.g., `nl -ba` / `sed -n`) and MUST NOT be estimated. If evidence is missing, you MUST report `FAIL`. Do not assume implicit behavior.
   - For every `FAIL`, provide evidence with a short explanation. Provide file path(s) and line numbers where possibile.
3. If directory/directories %%REQ_DIR%% exists, list files in %%REQ_DIR%% using `ls` or `tree`. Determine relevance by running a quick keyword search (e.g., `rg`/`git grep`) for impacted modules/features; read only the tech docs that match, then apply only those guidelines.
   - Verify that the application's source code follows those documents.
   - Do not check guidelines from files you have not explicitly read via a tool action.
   - Report any discrepancies with file paths and concise explanations.
4. PRINT in the response presenting results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence). The final line of the output must be EXACTLY "Check completed!".
