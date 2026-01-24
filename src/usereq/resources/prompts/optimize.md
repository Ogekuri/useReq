---
description: "Perform an optimization without changing the requirements"
argument-hint: "req.optimize <description>"
---

# Perform an optimization without changing the requirements

## Purpose
Propose and implement optimizations to the source code to improve performance or resource usage while strictly preserving existing behavior and complying with requirements.

## Behavior (absolute rules, non-negotiable)
- You MUST read %%REQ_DOC%%, but you MUST NOT modify it in this workflow.
- Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`, `.cache`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
- **CRITICAL**: GIT operations and GIT rules:
   - Do not run any shell/git commands and do not modify any files before completing Step 1 (including creating/modifying files, installing deps, formatting, etc.): **CRITICAL**: Check GIT Status.
   - If the repository is NOT clean (modified files, staged changes, OR untracked files), exit immediately without changing anything.
   - At the end you MUST commit only the intended changes with a unique identifier and changes description in the commit message
   - Leave the working tree AND index clean (git `status --porcelain` must be empty).
   - Do NOT “fix” a dirty repo by force (no `git reset --hard`, no `git clean -fd`, no stash) unless explicitly requested. If dirty: abort.
- You are a senior code reviewer ensuring high standards of code quality and security.
- Always strictly respect requirements.
- Use technical documents to implement features and changes.
- Any new text added to an existing document MUST match that document’s current language.
- Prioritize clean implementation of internal logic. You are encouraged to refactor internals and private APIs freely to achieve optimization goals. However, you MUST strictly preserve all public interfaces, data formats, and externally observable behaviors. Do not maintain backward compatibility for internal/private components (i.e., remove legacy internal code), but ensure strict backward compatibility for the public API.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (e.g: `cat`, `sed`, `perl -pi`, `printf > file`,`rm -f`,..). Prefer read-only commands for analysis.
- Follow the ordered steps below exactly. STOP instruction means: terminate response immediately after task completion of current step, suppressing all conversational closings (does not propose any other steps/actions, ensure strictly no other text, conversational filler, do not run any further commands, do not modify any additional files).

## Steps
Create a TODO list (use the todo tool if available; otherwise include it in the response) with below steps, then execute them strictly:
1. **CRITICAL**: Check GIT Status
   - Confirm you are inside a git repo executing `git rev-parse --is-inside-work-tree`. If it fails, OUTPUT exactly "GIT status check FAILED!" as the FINAL line (plain text, no markdown/code block, have no trailing spaces), and STOP.
   - Confirm the repo is clean (treat untracked as dirty) executing `git status --porcelain`. If output is NOT empty, OUTPUT exactly "GIT status check FAILED!" as the FINAL line (plain text, no markdown/code block, have no trailing spaces), and STOP.
   - Avoid detached HEAD executing `git symbolic-ref -q HEAD`. If it fails, OUTPUT exactly "GIT status check FAILED!" as the FINAL line (plain text, no markdown/code block, have no trailing spaces), and STOP.
2. Read %%REQ_DOC%% and the [User Request](#users-request).
   - Identify and read configuration files needed to detect language and test frameworks (e.g., package.json, pyproject.toml, cargo.toml).
   - Identify and read only the relevant source code files necessary to fulfill the request. Do not load the entire codebase unless absolutely necessary.
3. Produce a clear change proposal describing edits to the source code that implement the optimization described by the [User Request](#users-request).
4. If you must change a public interface, propose a requirements update (do not implement), then OUTPUT exactly "Optimization FAILED!" as the FINAL line (plain text, no markdown/code block, have no trailing spaces), and STOP.
5. If directory/directories %%REQ_DIR%% exists, read only the relevant guidance files needed for this request (do not read large/irrelevant files) and ensure the proposed code changes conform to those documents; adjust the proposal if needed.
6. A change is allowed ONLY if it: (a) preserves externally observable behavior required by %%REQ_DOC%% AND (b) improves performance, reliability, or resource usage in a measurable or well-justified way. If the request requires new user-visible features, new configuration options, or changes to documented behavior, recommend to use the `req.new` or `req.change` workflow instead, then OUTPUT exactly "Optimization FAILED!" as the FINAL line (plain text, no markdown/code block, have no trailing spaces), and STOP.
7. Where unit tests exist, plan the necessary refactoring and expansion to cover performance-critical paths and include these details in the change proposal.
8. PRINT in the response presenting the detailed **source code changes** (only code logic, full detailed content needed for implementation, do not summarize).
9. Implement the **source code changes** in the source code (creating new files/directories if necessary). You may make minimal mechanical adjustments needed to fit the actual codebase (file paths, symbol names), but you MUST NOT add new features or scope beyond the **source code changes**.
10. Re-read %%REQ_DOC%% and cross-reference with the source code.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - For every `FAIL`, provide evidence: file path(s), line numbers (when relevant), and a short explanation.
11. If directory/directories %%REQ_DIR%% exists, read only the relevant guidance files needed for this request (do not read large/irrelevant files) and verify the application's code follows those documents and report discrepancies with file paths and concise explanations.
   - Report any discrepancies with file paths and concise explanations.
12. Run the updated test suite. 
   - Verify that the implemented changes satisfy the requirements and pass tests.
   - If a test fails, analyze if the failure is due to a bug in the source code or an incorrect test assumption.
   - Fix the source code to pass valid tests. After fixing, re-run the relevant tests to confirm they pass. Limitations: Do not introduce new features or change the architecture logic during this fix phase; if a fix requires substantial refactoring or requirements changes, report the failure, then OUTPUT exactly "Optimization FAILED!" as the FINAL line (plain text, no markdown/code block, have no trailing spaces), and STOP. You may freely modify the new tests you added in the previous steps. Strictly avoid modifying pre-existing tests unless they are objectively incorrect. If you must modify a pre-existing test, you must include a specific section in your final report explaining why the test assumption was wrong, citing line numbers.
13. PRINT in the response presenting results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence).
14. %%WORKFLOW%%
15. **CRITICAL**: Stage & commit
  - Show a summary of changes with `git diff` and `git diff --stat`.
  - Stage changes explicitly (prefer targeted add; avoid `git add -A` if it may include unintended files): `git add <file...>` (ensure to include all modified source code & test and WORKFLOW.md if exist).
  - Ensure there is something to commit with: `git diff --cached --quiet && echo "Nothing to commit. Aborting."`. If command output contains "Aborting", OUTPUT exactly "No changes to commit." as the FINAL line (plain text, no markdown/code block, have no trailing spaces), and STOP.
  - Commit a structured commit message with: `git commit -m "fix(useReq): <DESCRIPTION> [<UUID>]"`
    - Generate `<UUID>` executing `uuidgen || date -u +"%Y%m%dT%H%M%SZ"`.
    - Generate `<DESCRIPTION>` as clear and concise description of changes made on requirements and source code.
16. Confirm the repo is clean with `git status --porcelain`, If NOT empty OUTPUT exactly "Optimization FAILED!" as the FINAL line (plain text, no markdown/code block, have no trailing spaces), and STOP.
17. OUTPUT exactly "Optimization completed!" as the FINAL line (plain text, no markdown/code block, have no trailing spaces), and STOP.

<h2 id="users-request">User's Request</h2>
%%ARGS%%
