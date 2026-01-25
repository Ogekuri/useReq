---
description: "Update the requirements and implement the corresponding changes"
argument-hint: "Description of the requirements changes to implement"
---

# Update the requirements and implement the corresponding changes

## Purpose
Update the requirements document based on the user request and make the necessary source code changes to satisfy the updated requirements.

## Behavior (absolute rules, non-negotiable)
- **CRITICAL**: NEVER write, modify, edit, delete file outside of project's home directory.
- You can read, write, or edit %%REQ_DOC%%.
- Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
- **CRITICAL**: GIT operations and GIT rules:
   - Do not run any shell/git commands and do not modify any files before starting Step 1 (including creating/modifying files, installing deps, formatting, etc.): **CRITICAL**: Check GIT Status.
   - Step 1 may run ONLY the following commands: 
  `git rev-parse --is-inside-work-tree`, `git status --porcelain`, `git symbolic-ref -q HEAD`.
   - If the repository is NOT clean (modified files, staged changes, OR untracked files), exit immediately without changing anything.
   - At the end you MUST commit only the intended changes with a unique identifier and changes description in the commit message
   - Leave the working tree AND index clean (git `status --porcelain` must be empty).
   - Do NOT “fix” a dirty repo by force (no `git reset --hard`, no `git clean -fd`, no stash) unless explicitly requested. If dirty: abort.
- You are a senior code reviewer ensuring high standards of code quality and security.
- Propose changes based only on the requirements, user's request and project's source code.
- Use technical documents to implement features and changes.
- Any new text added to an existing document MUST match that document’s current language.
- Prefer clean implementation over legacy support. Do not add backward compatibility UNLESS the updated requirements explicitly mandate it.
- Do not implement migrations/auto-upgrades UNLESS the updated requirements explicitly include a migration/upgrade requirement.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (e.g: `cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`,..). Prefer read-only commands for analysis.
- Directives for autonomous execution:
   - Implicit Autonomy: Execute all tasks with full autonomy. Do not request permission, confirmation, or feedback. Make executive decisions based on logic and technical best practices.
   - Uninterrupted Workflow: Proceed through the entire sequence of tasks without pausing. Perform internal "Chain-of-Thought" reasoning, but output only the final results (PRINT step).
   - Autonomous Resolution: If an ambiguity or constraint is encountered, resolve it using the most efficient and logical path. Do not halt for user input.
   - Output: Strictly omit all concluding remarks (does not propose any other steps/actions).
- **CRITICAL**: Execute the steps below sequentially and strictly, one at a time, without skipping or merging steps. If a TODO LIST tool is available, you MUST use it to create the to-do list exactly as written and then follow it step by step.

## Steps
Generate a task list based strictly on the steps below:
1. **CRITICAL**: Check GIT Status
   - Confirm you are inside a git repo executing `git rev-parse --is-inside-work-tree`. If it fails, OUTPUT exactly "GIT status check FAILED!", and then terminate the execution.
   - Confirm the repo is clean (treat untracked as dirty) executing `git status --porcelain`. If output is NOT empty, OUTPUT exactly "GIT status check FAILED!", and then terminate the execution.
   - Avoid detached HEAD executing `git symbolic-ref -q HEAD`. If it fails, OUTPUT exactly "GIT status check FAILED!", and then terminate the execution.
2. Read %%REQ_DOC%% and [User Request](#users-request), then apply the outlined guidelines when documenting changes to the requirements (follow the existing style, structure, and language).
3. Generate a detailed **Software Requirements Specification Update** documenting the exact modifications to requirements needed to implement the changes described by the [User Request](#users-request). This **Software Requirements Specification Update** must account for the original User Request and all subsequent changes and adjustments for %%REQ_DOC%%. 
   - Never introduce new requirements solely to explicitly forbid functions/features/behaviors. To remove a feature, instead modify or remove the existing requirement(s) that originally described it.
   - In this step, do not edit, create, delete, or rename any source code files in the project (including refactors or formatting-only changes).
4. If directory/directories %%REQ_DIR%% exists, read only the relevant guidance files needed for this request (do not read large/irrelevant files) and ensure the proposed code changes conform to those documents; adjust the **Software Requirements Specification Update** if needed.
5. PRINT in the response presenting the detailed **Software Requirements Specification Update** (only requirements, full detailed content needed for implementation, do not summarize).
6. Apply the **Software Requirements Specification Update** to %%REQ_DOC%%, following its formatting, language, and guidelines from the template at `.req/templates/requirements.md`. Do NOT introduce any additional edits beyond what the **Software Requirements Specification Update** describes.
7. Re-read %%REQ_DOC%% and verify that the project's source code satisfies the requirements listed there.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - **NOTE**: Since requirements have been updated but code has not, anticipate `FAIL` for the modified/new requirements, but verify the actual status. Report `FAIL` if the code does not fully satisfy the requirement. This confirms the gap to be filled.
   - For every `FAIL`, provide evidence: file path(s), line numbers (when relevant), and a short explanation.
8. Generate a detailed **Comprehensive Technical Implementation Report** documenting the exact modifications to the source code that will cover all `FAIL` requirements and the [User Request](#users-request).
9.  If a migration/compatibility need is discovered but not specified in requirements, propose a requirements update describing it, then OUTPUT exactly "Change request FAILED!", revert changes executing `git checkout .` and `git clean -fd`, and then terminate the execution.
10. If directory/directories %%REQ_DIR%% exists, read only the relevant guidance files needed for this request (do not read large/irrelevant files) and ensure the proposed code changes conform to those documents; adjust the **Comprehensive Technical Implementation Report** if needed.
11. Where unit tests exist, plan the necessary refactoring and expansion to cover new requirements and include these details in the **Comprehensive Technical Implementation Report**.
12. PRINT in the response presenting the detailed **Comprehensive Technical Implementation Report** (only code logic, full detailed content needed for implementation, do not summarize).
13. Implement the **Comprehensive Technical Implementation Report** in the source code (creating new files/directories if necessary). You may make minimal mechanical adjustments needed to fit the actual codebase (file paths, symbol names), but you MUST NOT add new features or scope beyond the **Comprehensive Technical Implementation Report**.  
14. Re-read %%REQ_DOC%% and cross-reference with the source code.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - For every `FAIL`, provide evidence: file path(s), line numbers (when relevant), and a short explanation.
15. If directory/directories %%REQ_DIR%% exists, read only the relevant guidance files needed for this request (do not read large/irrelevant files) and verify the application's code follows those documents and report discrepancies with file paths and concise explanations.
   - Report any discrepancies with file paths and concise explanations.
16. Run the updated test suite. 
   - Verify that the implemented changes satisfy the requirements and pass tests.
   - If a test fails, analyze if the failure is due to a bug in the source code or an incorrect test assumption.
   - Fix the source code to pass valid tests. After fixing, re-run the relevant tests to confirm they pass. Attempt to fix up to 2 times then, if they fail again, report the failure, then OUTPUT exactly "Change request FAILED!", revert changes executing `git checkout .` and `git clean -fd`, and then terminate the execution.
   - Limitations: Do not introduce new features or change the architecture logic during this fix phase. If a fix requires substantial refactoring or requirements changes, report the failure, then OUTPUT exactly "Change request FAILED!", revert changes executing `git checkout .` and `git clean -fd`, and then terminate the execution.
   - You may freely modify the new tests you added in the previous steps. For pre-existing tests, update or refactor them ONLY if they conflict with the new or modified requirements. Preserve the intent of tests covering unchanged logic. If you must modify a pre-existing test, you must include a specific section in your final report explaining why the test assumption was wrong or outdated, citing line numbers.
17. PRINT in the response presenting results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence).
18. %%WORKFLOW%%
19. **CRITICAL**: Stage & commit
   - Show a summary of changes with `git diff` and `git diff --stat`.
   - Stage changes explicitly (prefer targeted add; avoid `git add -A` if it may include unintended files): `git add <file...>` (ensure to include all modified source code & test, %%REQ_DOC%% and WORKFLOW.md only if it was modified/created).
   - Ensure there is something to commit with: `git diff --cached --quiet && echo "Nothing to commit. Aborting."`. If command output contains "Aborting", OUTPUT exactly "No changes to commit.", and then terminate the execution.
   - Commit a structured commit message with: `git commit -m "change(useReq): <DESCRIPTION> [<DATE>]"`
      - Generate `<DATE>` executing `date +"%Y-%m-%d %H:%M:%S"`.
      - Generate `<DESCRIPTION>` as clear and concise description of changes made on requirements, source code and tests, using English language.
20. Confirm the repo is clean with `git status --porcelain`, If NOT empty OUTPUT exactly "Change request FAILED!", and then terminate the execution.
21. OUTPUT exactly "Change request completed!".

<h2 id="users-request">User's Request</h2>
%%ARGS%%
