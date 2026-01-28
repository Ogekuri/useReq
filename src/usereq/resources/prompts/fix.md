---
description: "Fix a defect without changing the requirements"
argument-hint: "Description of the defect/bug to fix"
---

# Fix a defect without changing the requirements

## Purpose
Diagnose a reported defect, make a fix that adheres to existing requirements, and implement the necessary source code changes to resolve the issue.

## Behavior (absolute rules, non-negotiable)
- **CRITICAL**: NEVER write, modify, edit, or delete files outside of the project’s home directory, except under `/tmp`, where creating temporary files and writing outputs is allowed (the only permitted location outside the project).
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
- You are an expert debugger specializing in root cause analysis.
- Do not modify files that contain requirements.
- Always strictly respect requirements.
- Use technical documents to implement features and changes.
- Any new text added to an existing document MUST match that document’s current language.
- Prioritize backward compatibility. Do not introduce breaking changes; preserve existing interfaces, data formats, and features.
- If maintaining compatibility would require migrations/auto-upgrades conversion logic, report the conflict instead of implementing, and then terminate the execution.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`,`PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (eg: `cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`,..). Prefer read-only commands for analysis.
- **CRITICAL**: Directives for autonomous execution:
   - Implicit Autonomy: Execute all tasks with full autonomy. Do not request permission, confirmation, or feedback. Make executive decisions based on logic and technical best practices.
   - Uninterrupted Workflow: Proceed through the entire sequence of tasks without pausing. Perform internal "Chain-of-Thought" reasoning, but output only the final results (last PRINT step).
   - Autonomous Resolution: If an ambiguity or constraint is encountered, resolve it using the most efficient and logical path. Do not halt for user input.
   - After Prompt's Execution: Strictly omit all concluding remarks, does not propose any other steps/actions.
- **CRITICAL**: Execute the steps below sequentially and strictly, one at a time, without skipping or merging steps. If a TODO LIST tool is available, you MUST use it to create the to-do list exactly as written and then follow it step by step.

## Steps
Generate a task list based strictly on the steps below:
1. **CRITICAL**: Check GIT Status
   - Check GIT status. Confirm you are inside a clean git repo executing `git rev-parse --is-inside-work-tree >/dev/null 2>&1 && test -z "$(git status --porcelain)" && git symbolic-ref -q HEAD >/dev/null 2>&1 || { printf '%s\n' 'GIT status check FAILED!'; exit 1; }`. If it fails, OUTPUT exactly "GIT status check FAILED!", and then terminate the execution.
2. Read %%REQ_DOC%% and the [User Request](#users-request).
   - Identify and read configuration files needed to detect language and test frameworks (e.g., package.json, pyproject.toml, cargo.toml).
   - Identify and read only the relevant source code files necessary to fulfill the request. Do not load the entire codebase unless absolutely necessary.
3. GENERATE a detailed **Comprehensive Technical Implementation Report** documenting the exact modifications to the source code that fix the bug/defect described by the [User Request](#users-request). The **Comprehensive Technical Implementation Report** MUST only code logic, full detailed content needed for implementation, do not summarize.
   - If directory/directories %%REQ_DIR%% exists, list files in %%REQ_DIR%% using `ls` or `tree`. Based on filenames, determine which are relevant and READ them. Ensure the proposed code changes conform to those documents; adjust the **Comprehensive Technical Implementation Report** if needed. Do not apply guidelines from files you have not explicitly read via a tool action.
4. Where unit tests exist, plan the necessary refactoring and expansion to cover bug/defect described and include these details in the **Comprehensive Technical Implementation Report**.
5. A change is allowed ONLY if it corrects behavior that is: (a) explicitly required by %%REQ_DOC%% (cite requirement ID/section) OR (b) a defect with concrete evidence (crash, security flaw, data corruption, failing test, or incorrect output that contradicts a specific documented behavior). If the request implies new requirements or changing documented behavior, recommend `req.new` or `req.change`, then OUTPUT exactly "Defect fix FAILED!", and then terminate the execution.
6. IMPLEMENT the **Comprehensive Technical Implementation Report** in the source code (creating new files/directories if necessary). You may make minimal mechanical adjustments needed to fit the actual codebase (file paths, symbol names), but you MUST NOT add new features or scope beyond the **Comprehensive Technical Implementation Report**.
7. Re-read %%REQ_DOC%% and cross-reference with the source code to check all requirements.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - It is forbidden to mark a requirement as `OK` without at least one verifiable reference (file path + line range or excerpt). If strict evidence (exact file and logic match) is missing, you MUST report `FAIL`. Do not assume implicit behavior.
   - For every `FAIL`, provide evidence: file path(s), line numbers (when relevant), and a short explanation.
8.  Run the updated test suite. 
   - Verify that the implemented changes satisfy the requirements and pass tests.
   - If a test fails, analyze if the failure is due to a bug in the source code or an incorrect test assumption. Assume the test is correct unless the requirement explicitly contradicts the test expectation. Changes to existing tests require a higher burden of proof and specific explanation.
   - Fix the source code to pass valid tests. After fixing, re-run the relevant tests to confirm they pass. Attempt to fix up to 2 times then, if they fail again, report the failure, then OUTPUT exactly "Defect fix FAILED!", revert changes executing `git checkout .` and `git clean -fd`, and then terminate the execution.
   - Limitations: Do not introduce new features or change the architecture logic during this fix phase; if a fix requires substantial refactoring or requirements changes, report the failure, then OUTPUT exactly "Defect fix FAILED!", revert changes executing `git checkout .` and `git clean -fd`, and then terminate the execution.
   - You may freely modify the new tests you added in the previous steps. Strictly avoid modifying pre-existing tests unless they are objectively incorrect. If you must modify a pre-existing test, you must include a specific section in your final report explaining why the test assumption was wrong, citing line numbers.
9.  %%WORKFLOW%%
10. **CRITICAL**: Stage & commit
   - Show a summary of changes with `git diff` and `git diff --stat`.
   - Stage changes explicitly (prefer targeted add; avoid `git add -A` if it may include unintended files): `git add <file...>` (ensure to include all modified source code & test and WORKFLOW.md only if it was modified/created).
   - Ensure there is something to commit with: `git diff --cached --quiet && echo "Nothing to commit. Aborting."`. If command output contains "Aborting", OUTPUT exactly "No changes to commit.", and then terminate the execution.
   - Commit a structured commit message with: `git commit -m "fix(useReq): <DESCRIPTION> [<DATE>]"`
      - Generate `<DATE>` executing `date +"%Y-%m-%d %H:%M:%S"`.
      - Generate `<DESCRIPTION>` as clear and concise description of the defect fix and changes made on source code, using English language.
11. Confirm the repo is clean with `git status --porcelain`, If NOT empty OUTPUT exactly "Defect fix FAILED!", and then terminate the execution.
12. PRINT in the response presenting the **Comprehensive Technical Implementation Report** in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence). The final line of the output must be EXACTLY "Defect fixed!".

<h2 id="users-request">User's Request</h2>
%%ARGS%%
