---
description: "Perform an optimization without changing the requirements"
argument-hint: "req.optimize <description>"
---

# Perform an optimization without changing the requirements

## Purpose
- Produce a clear optimization proposal and apply the approved changes to the source code.

## Behavior
 - Even in read-only mode, you can always read, write, or edit files in `.req/context/`. Files in `.req/context/` are assumed to be untracked/ignored.
 - You MAY read %%REQ_DOC%%, but you MUST NOT modify it in this workflow.
 - Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
 - **CRITICAL**: You may use `git` only in ways that do not modify the repository history (HEAD) or branches/tags and do not update the Git index (staging area). You are allowed to modify the working tree (the checked-out files) using either normal filesystem edits or `git` commands that only change files in the working directory.
   - Allowed `git` operations (read-only or working-tree-only):
     - Read-only inspection: `git status`, `git diff`, `git log`, `git show`, `git ls-files`, `git rev-parse`, `git grep`.
     - Apply changes to the working tree: `git apply` (including --check, --verbose), and `git apply --reject` if needed.
     - Only the git commands explicitly listed as Allowed are permitted. If a git command is not listed, DO NOT run it.
   - Forbidden git operations (write to history/HEAD/branches/tags or to the index):
     - History/refs changes: `git commit`, `git merge`, `git rebase`, `git cherry-pick`, `git revert`, `git reset`, `git checkout`, `git switch`, `git restore`, `git tag`, `git branch` (create/delete/move), `git push`, `git fetch`, `git pull`
     - Index changes: `git add`, `git rm`, `git mv`, `git stash`, `git apply --index`, `git commit -a`.
     - Destructive cleanup: `git clean`.
 - You are a senior code reviewer ensuring high standards of code quality and security.
 - Always strictly respect requirements.
 - Use technical documents to implement features and changes.
 - Any new text added to an existing document MUST match that document’s current language.
 - Prioritize clean implementation over legacy support. You may refactor internals freely. Do not add backward compatibility of any kind (no shims, adapters, fallbacks, legacy paths, deprecated formats, or transitional behavior) and do not implement migrations or auto-upgrades.
 - If you must change a public interface, propose a requirements update (do not implement), DELETE `.req/context/active_request.md`, `.req/context/state.md`, `.req/context/pending_proposal.md`, `.req/context/approved_proposal.md` (if present) and STOP.
 - If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
 - Use filesystem/shell tools to read/write/delete files as needed (e.g: `cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`,..). Prefer read-only commands for analysis.
 - Follow the ordered steps below exactly. Step 1 (Context Bootstrap & Persistence) MUST ALWAYS execute first and is never skipped. JUMP only affects steps AFTER Step 1. When JUMP is instructed, do not execute any numbered step prior to the target step except Step 1. STOP instruction means: after completing any explicitly required cleanup actions in the current step (e.g., deleting .req/context files), do not run any further commands, do not modify any additional files, and end the response immediately.

## Steps
Create a TODO list (use the todo tool if available; otherwise include it in the response) with below steps, then execute them strictly:
1. %%BOOTSTRAP%%
2. **NOTE**: Here start CHANGE-CODE
3. Read %%REQ_DOC%% and the `.req/context/active_request.md`.
   - Identify and read configuration files needed to detect language and test frameworks (e.g., package.json, pyproject.toml, cargo.toml).
   - Identify and read only the relevant source code files necessary to fulfill the request. Do not load the entire codebase unless absolutely necessary.
4. Produce a clear change proposal describing edits to the source code that implement the optimization described by the `.req/context/active_request.md`.
5. If directory/directories %%REQ_DIR%% exists, read only the relevant guidance files needed for this request (do not read large/irrelevant files) and ensure the proposed code changes conform to those documents; adjust the proposal if needed.
6. A change is allowed ONLY if it: (a) preserves externally observable behavior required by %%REQ_DOC%% AND (b) improves performance, reliability, or resource usage in a measurable or well-justified way. If the request requires new user-visible features, new configuration options, or changes to documented behavior, ask to use the `req.new` or `req.change` workflow instead, DELETE `.req/context/active_request.md`, `.req/context/state.md`, `.req/context/pending_proposal.md`, `.req/context/approved_proposal.md` (if present) and STOP.
7. Where unit tests exist, plan the necessary refactoring and expansion to cover performance-critical paths and include these details in the change proposal.
8. **Present the proposed source code changes**.
9. SAVE the detailed change proposal (only code logic) into a temporary file `.req/context/pending_proposal.md` (save the full detailed content needed for implementation, do not summarize).
10. SAVE a file `.req/context/state.md` containing exactly these two lines:
    - `PREVIOUS-PHASE=CHANGE-CODE`
    - `NEXT-PHASE=IMPLEMENT-CODE`
11. %%STOPANDASKAPPROVE%%
12. **NOTE**: Here start IMPLEMENT-CODE
13. Implement the changes described in `.req/context/approved_proposal.md` in the source code (creating new files/directories if necessary). You may make minimal mechanical adjustments needed to fit the actual codebase (file paths, symbol names), but you MUST NOT add new features or scope beyond the approved proposal.
14. SAVE a file `.req/context/state.md` containing exactly these two lines:
   - `PREVIOUS-PHASE=TESTS`
   - `NEXT-PHASE=TESTS`
15. **NOTE**: Here start TESTS
16. Re-read %%REQ_DOC%% and cross-reference with the source code.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - For every `FAIL`, provide evidence: file path(s), line numbers (when relevant), and a short explanation.
17. If directory/directories %%REQ_DIR%% exists, read only the relevant guidance files needed for this request (do not read large/irrelevant files) and verify the application's code follows those documents and report discrepancies with file paths and concise explanations.
   - Report any discrepancies with file paths and concise explanations.
18. Run the updated test suite. 
   - Verify that the implemented changes satisfy the approved requirements and pass tests.
   - If a test fails, analyze if the failure is due to a bug in the source code or an incorrect test assumption.
   - Fix the source code to pass valid tests. Limitations: Do not introduce new features or change the architecture logic during this fix phase; if a fix requires substantial refactoring or requirements changes, report the failure and STOP. You may freely modify the new tests you added in the previous steps. Strictly avoid modifying pre-existing tests unless they are objectively incorrect. If you must modify a pre-existing test, you must include a specific section in your final report explaining why the test assumption was wrong, citing line numbers.
19. Present results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence).
20. %%WORKFLOW%%
21. **CRITICAL**: DELETE the following files if they exist (do not error if missing)
   - `.req/context/active_request.md`
   - `.req/context/state.md`
   - `.req/context/pending_proposal.md`
   - `.req/context/approved_proposal.md`
22. After the full report, OUTPUT exactly "Optimization completed!" as the FINAL line. The FINAL line MUST be plain text (no markdown/code block) and MUST have no trailing spaces. Terminate response immediately after task completion suppressing all conversational closings (does not propose any other steps/actions, ensure strictly no other text, conversational filler, or formatting follows FINAL line).

<h2 id="users-request">User's Request</h2>
%%ARGS%%

