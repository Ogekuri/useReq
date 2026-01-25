---
description: "Implement changes needed to cover the new requirements"
argument-hint: "No arguments utilized by the prompt logic"
---

# Implement changes needed to cover the new requirements

## Purpose
Identify uncovered requirements and implement source code changes to ensure all documented requirements are fully satisfied by the codebase.
 
## Behavior (absolute rules, non-negotiable)
- **CRITICAL**: NEVER write, modify, edit, delete file outside of project's home directory.
- You MUST read %%REQ_DOC%%, but you MUST NOT modify it in this workflow.
- Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`,`.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
- **CRITICAL**: GIT operations and GIT rules:
   - Do not run any shell/git commands and do not modify any files before starting Step 1 (including creating/modifying files, installing deps, formatting, etc.): **CRITICAL**: Check GIT Status.
   - Step 1 may run ONLY the following commands: 
  `git rev-parse --is-inside-work-tree`, `git status --porcelain`, `git symbolic-ref -q HEAD`.
   - If the repository is NOT clean (modified files, staged changes, OR untracked files), exit immediately without changing anything.
   - At the end you MUST commit only the intended changes with a unique identifier and changes description in the commit message
   - Leave the working tree AND index clean (git `status --porcelain` must be empty).
   - Do NOT “fix” a dirty repo by force (no `git reset --hard`, no `git clean -fd`, no stash) unless explicitly requested. If dirty: abort.
- You are a senior code reviewer ensuring high standards of code quality and security.
- Do not modify files that contain requirements.
- Always strictly respect requirements.
- Use technical documents to implement features and changes.
- Any new text added to an existing document MUST match that document’s current language.
- Prioritize backward compatibility. Do not introduce breaking changes; preserve existing interfaces, data formats, and features. If maintaining compatibility would require migrations/auto-upgrades conversion logic, report the conflict instead of implementing and STOP.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`,`PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (eg: `cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`,..). Prefer read-only commands for analysis.
- Directives for autonomous execution:
   - Implicit Autonomy: Execute all tasks with full autonomy. Do not request permission, confirmation, or feedback. Make executive decisions based on logic and technical best practices.
   - Uninterrupted Workflow: Proceed through the entire sequence of tasks without pausing. Perform internal "Chain-of-Thought" reasoning, but output only the final results (PRINT Step).
   - Autonomous Resolution: If an ambiguity or constraint is encountered, resolve it using the most efficient and logical path. Do not halt for user input unless a fatal execution error occurs (expressly indicated in the steps).
   - Zero-Latency Output: Strictly omit all conversational fillers, introductions, and concluding remarks. Start immediately with the task output.
- Follow the ordered steps below exactly. STOP instruction means: terminate response immediately after task completion (e.g., PRINT, OUTPUT,..) of current step, suppressing all conversational closings (does not propose any other steps/actions, ensure strictly no other text, conversational filler, do not run any further commands, do not modify any additional files).

## Steps
Generate a task list based strictly on the steps below. Utilize the TODO LIST tool if supported; if not, list them in your response. Execute each step sequentially and strictly:
1. **CRITICAL**: Check GIT Status
   - Confirm you are inside a git repo executing `git rev-parse --is-inside-work-tree`. If it fails, OUTPUT exactly "GIT status check FAILED!" as the FINAL line, and STOP.
   - Confirm the repo is clean (treat untracked as dirty) executing `git status --porcelain`. If output is NOT empty, OUTPUT exactly "GIT status check FAILED!" as the FINAL line, and STOP.
   - Avoid detached HEAD executing `git symbolic-ref -q HEAD`. If it fails, OUTPUT exactly "GIT status check FAILED!" as the FINAL line, and STOP.
2. Read %%REQ_DOC%% and verify that the project's source code satisfies the requirements listed there.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - For every `FAIL`, provide evidence: file path(s), line numbers (when relevant), and a short explanation.
3. **CRITICAL**: If all requirements report `OK`, OUTPUT exactly "All requirements are already covered. No changes needed." as the FINAL line, and STOP.
4. If there are uncovered requirements, produce a clear change proposal describing edits to the source code that will cover all `FAIL` requirements.
5. If directory/directories %%REQ_DIR%% exists, read only the relevant guidance files needed for this request (do not read large/irrelevant files) and ensure the proposed code changes conform to those documents; adjust the proposal if needed.
6. Where unit tests exist, plan the necessary refactoring and expansion to cover uncovered requirements and include these details in the change proposal.
7. PRINT in the response presenting the detailed **source code and test changes** (only code logic, full detailed content needed for implementation, do not summarize).
8. Implement the **source code changes** in the source code (creating new files/directories if necessary). You may make minimal mechanical adjustments needed to fit the actual codebase (file paths, symbol names), but you MUST NOT add new features or scope beyond the **source code changes**.
9. Re-read %%REQ_DOC%% and cross-reference with the source code.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - For every `FAIL`, provide evidence: file path(s), line numbers (when relevant), and a short explanation.
10. If directory/directories %%REQ_DIR%% exists, read only the relevant guidance files needed for this request (do not read large/irrelevant files) and verify that the application's code follows those documents. Report discrepancies with file paths and concise explanations.
   - Report any discrepancies with file paths and concise explanations.
11. Run the updated test suite. 
   - Verify that the implemented changes satisfy the requirements and pass tests.
   - If a test fails, analyze if the failure is due to a bug in the source code or an incorrect test assumption.
   - Fix the source code to pass valid tests. After fixing, re-run the relevant tests to confirm they pass. Attempt to fix up to 2 times then, if they fail again, report the failure, then OUTPUT exactly "Requirements coverage FAILED!" as the FINAL line, and STOP.
   - Limitations: Do not introduce new features or change the architecture logic during this fix phase; if a fix requires substantial refactoring or requirements changes, report the failure, then OUTPUT exactly "Requirements coverage FAILED!" as the FINAL line, and STOP.
   - You may freely modify the new tests you added in the previous steps. Strictly avoid modifying pre-existing tests unless they are objectively incorrect. If you must modify a pre-existing test, you must include a specific section in your final report explaining why the test assumption was wrong, citing line numbers.
12. PRINT in the response presenting results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence).
13. %%WORKFLOW%%
14. **CRITICAL**: Stage & commit
   - Show a summary of changes with `git diff` and `git diff --stat`.
   - Stage changes explicitly (prefer targeted add; avoid `git add -A` if it may include unintended files): `git add <file...>` (ensure to include all modified source code & test and WORKFLOW.md only if it was modified/created).
   - Ensure there is something to commit with: `git diff --cached --quiet && echo "Nothing to commit. Aborting."`. If command output contains"Aborting",  OUTPUT exactly "No changes to commit." as the FINAL line(plain text, no  markdown/code block, have no trailing spaces), and STOP.
   - Commit a structured commit message with: `git commit -m "cover(useReq):<DESCRIPTION> [<DATE>]"`
      - Generate `<DATE>` executing `date +"%Y-%m-%d %H:%M:%S"`.
      - Generate `<DESCRIPTION>` as a clear and concise description of changes made to source code and tests, using English language.
15. Confirm the repo is clean with `git status --porcelain`, If NOT empty OUTPUT exactly "Requirements coverage FAILED!" as the FINAL line, and STOP.
16. OUTPUT exactly "Requirements coverage completed!" as the FINAL line, and STOP.
