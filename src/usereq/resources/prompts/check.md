---
description: "Run the requirements check"
argument-hint: "req.check"
---

# Run the requirements check

## Purpose
- Perform the requirements check and report whether all items are correctly covered without making any changes.
 
## Behavior
 - Even in read-only mode, you can always read, write, or edit files in `.req/context/`. Files in `.req/context/` are assumed to be untracked/ignored.
 - You MAY read %%REQ_DOC%%, but you MUST NOT modify it in this workflow.
 - Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
 - **CRITICAL**: Do not modify any git tracked files (i.e., returned by `git ls-files`). You may run commands that create untracked artifacts ONLY if: (a) they are confined to standard disposable locations (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`), (b) they do not change any tracked file contents, and (c) you do NOT rely on those artifacts as permanent outputs. If unsure, run tools in a temporary directory (e.g., `tmp/`, `temp/`, `/tmp`) or use tool flags that disable caches.
 - Allowed git commands in this workflow (read-only only): `git status`, `git diff`, `git ls-files`, `git grep`. Do NOT run any other git commands.
 - Only analyze the code and present the results; make no changes.
 - Report facts: for each finding include file paths and, when useful, line numbers or short code excerpts.
 - If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
 - Use filesystem/shell tools to read/write/delete files as needed (e.g: `cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`,..). Prefer read-only commands for analysis.
 - Follow the ordered steps below exactly.

## Steps
Create a TODO list (use the todo tool if available; otherwise include it in the response) with below steps, then execute them strictly:
1. Run the test suite to verify the current state. Do not modify the source code or tests. Simply report the test results (`OK`/`FAIL`) as evidence for the analysis report.
2. Read %%REQ_DOC%% and verify that the project's source code satisfies the requirements listed there.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - **NOTE**: Mark `OK` only with direct evidence (file path + line numbers). If uncertain or evidence is missing, mark `FAIL` and state what evidence you could not find.
   - For every `FAIL`, provide evidence: file path(s), line numbers (when relevant), and a short explanation.
3. If directory/directories %%REQ_DIR%% exists, read only the relevant guidance files needed for this request (do not read large/irrelevant files) and verify that the application's code follows those documents.
   - Report any discrepancies with file paths and concise explanations.
4. Present results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence).
5. After the full report, OUTPUT exactly "Check completed!" as the FINAL line. The FINAL line MUST be plain text (no markdown/code block) and MUST have no trailing spaces. Terminate response immediately after task completion suppressing all conversational closings (does not propose any other steps/actions, ensure strictly no other text, conversational filler, or formatting follows FINAL line).
