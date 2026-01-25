---
description: "Update the requirements and implement the corresponding changes"
argument-hint: "req.change <description>"
---

# Update the requirements and implement the corresponding changes

## Purpose
Update the requirements document based on the user request and make the necessary source code changes to satisfy the updated requirements.

## Behavior (absolute rules, non-negotiable)
 - You can read, write, or edit %%REQ_DOC%%.
 - Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
 - **CRITICAL**: GIT operations and GIT rules:
   - Do not run any shell/git commands and do not modify any files before completing Step 1 (including creating/modifying files, installing deps, formatting, etc.): **CRITICAL**: Check GIT Status.
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
 - Follow the ordered steps below exactly. STOP instruction means: terminate response immediately after task completion of current step, suppressing all conversational closings (does not propose any other steps/actions, ensure strictly no other text, conversational filler, do not run any further commands, do not modify any additional files).

## Steps
Create a TODO list (use the todo tool if available; otherwise include it in the response) with below steps, then execute them strictly:
1. **CRITICAL**: Check GIT Status
   - Confirm you are inside a git repo executing `git rev-parse --is-inside-work-tree`. If it fails, OUTPUT exactly "GIT status check FAILED!" as the FINAL line (plain text, no markdown/code block, have no trailing spaces), and STOP.
   - Confirm the repo is clean (treat untracked as dirty) executing `git status --porcelain`. If output is NOT empty, OUTPUT exactly "GIT status check FAILED!" as the FINAL line (plain text, no markdown/code block, have no trailing spaces), and STOP.
   - Avoid detached HEAD executing `git symbolic-ref -q HEAD`. If it fails, OUTPUT exactly "GIT status check FAILED!" as the FINAL line (plain text, no markdown/code block, have no trailing spaces), and STOP.
2. Read %%REQ_DOC%% and [User Request](#users-request), then apply the outlined guidelines when documenting changes to the requirements (follow the existing style, structure, and language).
3. Produce a comprehensive change proposal describing the edits to requirements needed to implement the changes described by the [User Request](#users-request). This proposal must account for the original request and all subsequent adjustments logged in that file. 
   - Never introduce new requirements solely to explicitly forbid functions/features/behaviors. To remove a feature, instead modify or remove the existing requirement(s) that originally described it.
   - In this step, do not edit, create, delete, or rename any source code files in the project (including refactors or formatting-only changes).
4. If a migration/compatibility need is discovered but not specified in requirements, propose a requirements update describing it, then OUTPUT exactly "Change request FAILED!" as the FINAL line (plain text, no markdown/code block, have no trailing spaces), and STOP.
5. If directory/directories %%REQ_DIR%% exists, read only the relevant guidance files needed for this request (do not read large/irrelevant files) and ensure the proposed code changes conform to those documents; adjust the proposal if needed.
6. PRINT in the response presenting the detailed **requirements changes** (only requirements, full detailed content needed for implementation, do not summarize).
7. Apply the **requirements changes** to %%REQ_DOC%%, following its formatting, language, and guidelines from the template at `.req/templates/requirements.md`. Do NOT introduce any additional edits beyond what the **requirements changes** describes.
8. Re-read %%REQ_DOC%% and verify that the project's source code satisfies the requirements listed there.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - **NOTE**: Since requirements have been updated but code has not, anticipate `FAIL` for the modified/new requirements, but verify the actual status. Report `FAIL` if the code does not fully satisfy the requirement. This confirms the gap to be filled.
   - For every `FAIL`, provide evidence: file path(s), line numbers (when relevant), and a short explanation.
9. Produce a clear change proposal describing edits to the source code that will cover all `FAIL` requirements and the [User Request](#users-request).
10. If a migration/compatibility need is discovered but not specified in requirements, propose a requirements update describing it, then OUTPUT exactly "Change request FAILED!" as the FINAL line (plain text, no markdown/code block, have no trailing spaces), and STOP.
11. If directory/directories %%REQ_DIR%% exists, read only the relevant guidance files needed for this request (do not read large/irrelevant files) and ensure the proposed code changes conform to those documents; adjust the proposal if needed.
12. Where unit tests exist, plan the necessary refactoring and expansion to cover new requirements and include these details in the change proposal.
13. PRINT in the response presenting the detailed **source code and test changes** (only code logic, full detailed content needed for implementation, do not summarize).
14. Implement the **source code changes** in the source code (creating new files/directories if necessary). You may make minimal mechanical adjustments needed to fit the actual codebase (file paths, symbol names), but you MUST NOT add new features or scope beyond the **source code changes**.  
15. Re-read %%REQ_DOC%% and cross-reference with the source code.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - For every `FAIL`, provide evidence: file path(s), line numbers (when relevant), and a short explanation.
16. If directory/directories %%REQ_DIR%% exists, read only the relevant guidance files needed for this request (do not read large/irrelevant files) and verify the application's code follows those documents and report discrepancies with file paths and concise explanations.
   - Report any discrepancies with file paths and concise explanations.
17. Run the updated test suite. 
   - Verify that the implemented changes satisfy the requirements and pass tests.
   - If a test fails, analyze if the failure is due to a bug in the source code or an incorrect test assumption.
   - Fix the source code to pass valid tests. After fixing, re-run the relevant tests to confirm they pass. Limitations: Do not introduce new features or change the architecture logic during this fix phase. If a fix requires substantial refactoring or requirements changes, report the failure, then OUTPUT exactly "Change request FAILED!", and STOP. You may freely modify the new tests you added in the previous steps. For pre-existing tests, update or refactor them ONLY if they conflict with the new or modified requirements. Preserve the intent of tests covering unchanged logic. If you must modify a pre-existing test, you must include a specific section in your final report explaining why the test assumption was wrong or outdated, citing line numbers.
18. PRINT in the response presenting results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence).
19. %%WORKFLOW%%
20. **CRITICAL**: Stage & commit
  - Show a summary of changes with `git diff` and `git diff --stat`.
  - Stage changes explicitly (prefer targeted add; avoid `git add -A` if it may include unintended files): `git add <file...>` (ensure to include all modified source code & test, %%REQ_DOC%% and WORKFLOW.md if exist).
  - Ensure there is something to commit with: `git diff --cached --quiet && echo "Nothing to commit. Aborting."`. If command output contains "Aborting", OUTPUT exactly "No changes to commit." as the FINAL line (plain text, no markdown/code block, have no trailing spaces), and STOP.
  - Commit a structured commit message with: `git commit -m "change(useReq): <DESCRIPTION> [<UUID>]"`
    - Generate `<UUID>` executing `date +"%Y-%m-%d %H:%M:%S"`.
    - Generate `<DESCRIPTION>` as clear and concise description of changes made on requirements and source code.
21. Confirm the repo is clean with `git status --porcelain`, If NOT empty OUTPUT exactly "Change request FAILED!" as the FINAL line (plain text, no markdown/code block, have no trailing spaces), and STOP.
22. OUTPUT exactly "Change request completed!" as the FINAL line (plain text, no markdown/code block, have no trailing spaces), and STOP.

<h2 id="users-request">User's Request</h2>
%%ARGS%%
