---
description: "Produce an analysis report"
argument-hint: "Description of the analysis/investigation to perform"
---

# Produce an analysis report

## Purpose
Analyze the source code and requirements to answer the user request, producing a detailed analysis report without modifying any code or requirements.
 
## Behavior (absolute rules, non-negotiable)
- **CRITICAL**: NEVER write, modify, edit, or delete files outside of the project’s home directory, except under `/tmp`, where creating temporary files and writing outputs is allowed (the only permitted location outside the project).
- You MUST read %%REQ_DOC%%, but you MUST NOT modify it in this workflow.
- Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
- **CRITICAL**: Do not modify any git tracked files (i.e., returned by `git ls-files`). You may run commands that create untracked artifacts ONLY if: (a) they are confined to standard disposable locations (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`), (b) they do not change any tracked file contents, and (c) you do NOT rely on those artifacts as permanent outputs. If unsure, run tools in a temporary directory (e.g., `tmp/`, `temp/`, `/tmp`) or use tool flags that disable caches.
- You are an expert debugger specializing in root cause analysis.
- Only analyze the code and present the results; make no changes.
- Do NOT create or modify tests in this workflow.
- Report facts: for each finding include file paths and, when useful, line numbers or short code excerpts.
- Allowed git commands in this workflow (read-only only): `git status`, `git diff`, `git ls-files`, `git grep`, `git rev-parse`. Do NOT run any other git commands.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read files as needed (read-only only; e.g., `cat`, `sed -n`, `head`, `tail`, `rg`, `less`). Do NOT use in-place editing flags (e.g., `-i`, `perl -pi`) in this workflow.
- **CRITICAL**: Directives for autonomous execution:
   - Implicit Autonomy: Execute all tasks with full autonomy. Do not request permission, confirmation, or feedback. Make executive decisions based on logic and technical best practices.
   - Uninterrupted Workflow: Proceed through the entire sequence of tasks without pausing; keep reasoning internal ("Chain-of-Thought") and output only the deliverables explicitly requested by the Steps section.
   - Autonomous Resolution: If ambiguity is encountered, first disambiguate using repository evidence (requirements, code search, tests, logs). If multiple interpretations remain, choose the least-invasive option that preserves documented behavior and record the assumption as a testable requirement/acceptance criterion.
   - After Prompt's Execution: Strictly omit all concluding remarks, does not propose any other steps/actions.
- **CRITICAL**: Execute the steps below sequentially and strictly, one at a time, without skipping or merging steps. Check if a TODO LIST tool is available, you MUST use todo tool to create the to-do list exactly as written and then follow it step by step without pausing. If TODO LIST tool is NOT available OUTPUT exactly "TODO LIST tool check FAILED!", and then terminate the execution.

## Steps
Internally generate a task list based strictly on the steps below, then execute it step by step without pausing:
1. Read %%REQ_DOC%% and the [User Request](#users-request) analysis request.
   - Identify and read configuration files needed to detect language and test frameworks (e.g., package.json, pyproject.toml, cargo.toml).
   - Use search-first (`git grep`/`rg`) to find the minimal relevant file set, then read only those files. Avoid scanning entire directories unless evidence indicates it is required. Do not load the entire codebase unless absolutely necessary.
2. Analyze the source code to answer the [User Request](#users-request), ensuring compliance with %%REQ_DIR%% documents if present.
   - If directory/directories %%REQ_DIR%% exists, list files in %%REQ_DIR%% using `ls` or `tree`. Determine relevance by running a quick keyword search (e.g., `rg`/`git grep`) for impacted modules/features; read only the tech docs that match, then apply only those guidelines. Ensure the report complies with its guidance. Do not apply guidelines from files you have not explicitly read via a tool action.
3. PRINT in the response presenting the final analysis report in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence). The final line of the output must be EXACTLY "Analysis completed!".

<h2 id="users-request">User's Request</h2>
%%ARGS%%
