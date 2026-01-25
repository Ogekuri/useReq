---
description: "Produce an analysis report"
argument-hint: "Description of the analysis/investigation to perform"
---

# Produce an analysis report

## Purpose
Analyze the source code and requirements to answer the user request, producing a detailed analysis report without modifying any code or requirements.
 
## Behavior (absolute rules, non-negotiable)
- **CRITICAL**: NEVER write, modify, edit, delete file outside of project's home directory.
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
- Directives for autonomous execution:
   - Implicit Autonomy: Execute all tasks with full autonomy. Do not request permission, confirmation, or feedback. Make executive decisions based on logic and technical best practices.
   - Uninterrupted Workflow: Proceed through the entire sequence of tasks without pausing. Perform internal "Chain-of-Thought" reasoning, but output only the final results (PRINT Step).
   - Autonomous Resolution: If an ambiguity or constraint is encountered, resolve it using the most efficient and logical path. Do not halt for user input unless a fatal execution error occurs (expressly indicated in the steps).
   - Zero-Latency Output: Strictly omit all conversational fillers, introductions, and concluding remarks. Start immediately with the task output.
- Follow the ordered steps below exactly. STOP instruction means: terminate response immediately after task completion (e.g., PRINT, OUTPUT,..) of current step, suppressing all conversational closings (does not propose any other steps/actions, ensure strictly no other text, conversational filler, do not run any further commands, do not modify any additional files).

## Steps
Generate a task list based strictly on the steps below. Utilize the TODO LIST tool if supported; if not, list them in your response. Execute each step sequentially and strictly:
1. Read %%REQ_DOC%% and the [User Request](#users-request) analysis request.
   - Identify and read configuration files needed to detect language and test frameworks (e.g., package.json, pyproject.toml, cargo.toml).
   - Identify and read only the relevant source code files necessary to fulfill the request. Do not load the entire codebase unless absolutely necessary.
2. If directory/directories %%REQ_DIR%% exists, read only the relevant guidance files needed for this request (do not read large/irrelevant files) and ensure the report complies with its guidance.
3. Analyze the code to answer the [User Request](#users-request), ensuring compliance with %%REQ_DIR%% documents if present.
4. PRINT in the response presenting the final analysis report in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence).
5. OUTPUT exactly "Analysis completed!" as the FINAL line, and STOP.

<h2 id="users-request">User's Request</h2>
%%ARGS%%
