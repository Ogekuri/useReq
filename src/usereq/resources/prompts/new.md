---
description: "Implement a new requirement and make the corresponding source code changes"
argument-hint: "req.new <description>"
---

# Implement a new requirement and make the corresponding source code changes

## Purpose
- Produce a clear change proposal and apply the approved changes to the requirements and source code.

## Behavior
 - Even in read-only mode, you can always read, write, or edit files in `.req/context/`. Files in `.req/context/` are assumed to be untracked/ignored.
 - You can read, write, or edit %%REQ_DOC%%.
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
 - Propose changes based only on the requirements, user's request and project's source code.
 - Use technical documents to implement features and changes.
 - Any new text added to an existing document MUST match that document’s current language.
 - Prioritize backward compatibility. Do not introduce breaking changes; preserve existing interfaces, data formats, and features.
 - If maintaining compatibility would require migrations/auto-upgrades/conversion logic, report the conflict instead of implementing, DELETE `.req/context/active_request.md`, `.req/context/state.md`, `.req/context/pending_proposal.md`, `.req/context/approved_proposal.md` (if present) and STOP.
 - If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
 - Use filesystem/shell tools to read/write/delete files as needed (e.g: `cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`,..). Prefer read-only commands for analysis.
 - Follow the ordered steps below exactly. Step 1 (Context Bootstrap & Persistence) MUST ALWAYS execute first and is never skipped. JUMP only affects steps AFTER Step 1. When JUMP is instructed, do not execute any numbered step prior to the target step except Step 1. STOP instruction means: after completing any explicitly required cleanup actions in the current step (e.g., deleting .req/context files), do not run any further commands, do not modify any additional files, and end the response immediately.

## Steps
Create a TODO list (use the todo tool if available; otherwise include it in the response) with below steps, then execute them strictly:
1. %%BOOTSTRAP%%
2. **NOTE**: Here start ANALYZE-REQUIREMENTS
3. Read %%REQ_DOC%% and `.req/context/active_request.md`. When editing requirements, follow the existing style, structure, and language of %%REQ_DOC%%.
4. Produce a comprehensive change proposal describing the edits to requirements needed to implement the feature(s) described by the `.req/context/active_request.md`. This proposal must account for the original request and all subsequent adjustments logged in that file.  
   - Never introduce new requirements solely to explicitly forbid functions/features/behaviors. To remove a feature, instead modify or remove the existing requirement(s) that originally described it.
   - In this step, do not edit, create, delete, or rename any source code files in the project (including refactors or formatting-only changes).
5. If directory/directories %%REQ_DIR%% exists, read only the relevant guidance files needed for this request (do not read large/irrelevant files) and ensure the proposed code changes conform to those documents; adjust the proposal if needed.
6. Do not change the intent of existing requirements unless the new feature logically requires it. You may make minimal edits for consistency (references, numbering, glossary) as long as you explicitly list them.
   - If you must adjust an existing requirement's intent, list the exact requirement(s) and explain why.
7. **Present the proposed requirements changes**.
8. SAVE the detailed change proposal (only requirements) into a temporary file `.req/context/pending_proposal.md` (save the full detailed content needed for implementation, do not summarize).
9. SAVE a file `.req/context/state.md` containing exactly these two lines:
    - `PREVIOUS-PHASE=ANALYZE-REQUIREMENTS`
    - `NEXT-PHASE=CHANGE-REQUIREMENTS`
10. %%STOPANDASKAPPROVE%%
11. **NOTE**: Here start CHANGE-REQUIREMENTS
12. Apply the approved proposal changes from `.req/context/approved_proposal.md` to %%REQ_DOC%%, following its formatting, language, and guidelines from the template at `.req/templates/requirements.md`. Do NOT introduce any additional edits beyond what the approved proposal describes.
13. SAVE a file `.req/context/state.md` containing exactly these two lines:
   - `PREVIOUS-PHASE=CHANGE-CODE`
   - `NEXT-PHASE=CHANGE-CODE`
14. **NOTE**: Here start CHANGE-CODE
15. Re-read %%REQ_DOC%% and verify that the project's source code satisfies the requirements listed there.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - **NOTE**: Since requirements have been updated but code has not, anticipate `FAIL` for the modified/new requirements, but verify the actual status. Report `FAIL` if the code does not fully satisfy the requirement. This confirms the gap to be filled.
   - For every `FAIL`, provide evidence: file path(s), line numbers (when relevant), and a short explanation.
16. Produce a clear change proposal describing edits to the source code that will cover all `FAIL` requirements and the `.req/context/active_request.md`.
17. If directory/directories %%REQ_DIR%% exists, read only the relevant guidance files needed for this request (do not read large/irrelevant files) and ensure the proposed code changes conform to those documents; adjust the proposal if needed.
18. Where unit tests exist, plan the necessary refactoring and expansion to cover new requirements and include these details in the change proposal.
19. **Present the proposed source code changes**.
20. SAVE the detailed change proposal (only code logic) into a temporary file `.req/context/pending_proposal.md` (save the full detailed content needed for implementation, do not summarize).
21. SAVE a file `.req/context/state.md` containing exactly these two lines:
    - `PREVIOUS-PHASE=CHANGE-CODE`
    - `NEXT-PHASE=IMPLEMENT-CODE`
22. %%STOPANDASKAPPROVE%%
23. **NOTE**: Here start IMPLEMENT-CODE
24. Implement the changes described in `.req/context/approved_proposal.md` in the source code (creating new files/directories if necessary). You may make minimal mechanical adjustments needed to fit the actual codebase (file paths, symbol names), but you MUST NOT add new features or scope beyond the approved proposal.
25. SAVE a file `.req/context/state.md` containing exactly these two lines:
   - `PREVIOUS-PHASE=TESTS`
   - `NEXT-PHASE=TESTS`
26. **NOTE**: Here start TESTS
27. Re-read %%REQ_DOC%% and cross-reference with the source code.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - For every `FAIL`, provide evidence: file path(s), line numbers (when relevant), and a short explanation.
28. If directory/directories %%REQ_DIR%% exists, read only the relevant guidance files needed for this request (do not read large/irrelevant files) and verify the application's code follows those documents and report discrepancies with file paths and concise explanations.
   - Report any discrepancies with file paths and concise explanations.
29. Run the updated test suite. 
   - Verify that the implemented changes satisfy the approved requirements and pass tests.
   - If a test fails, analyze if the failure is due to a bug in the source code or an incorrect test assumption.
   - Fix the source code to pass valid tests. Limitations: Do not introduce new features or change the architecture logic during this fix phase; if a fix requires substantial refactoring or requirements changes, report the failure and STOP. You may freely modify the new tests you added in the previous steps. For pre-existing tests, update or refactor them ONLY if they conflict with the new or modified requirements. Preserve the intent of tests covering unchanged logic. If you must modify a pre-existing test, you must include a specific section in your final report explaining why the test assumption was wrong or outdated, citing line numbers.
30. Present results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence).
31. %%WORKFLOW%%
32. **CRITICAL**: DELETE the following files if they exist (do not error if missing)
   - `.req/context/active_request.md`
   - `.req/context/state.md`
   - `.req/context/pending_proposal.md`
   - `.req/context/approved_proposal.md`
33. After the full report, OUTPUT exactly "New implementation completed!" as the FINAL line. The FINAL line MUST be plain text (no markdown/code block) and MUST have no trailing spaces. Terminate response immediately after task completion suppressing all conversational closings (does not propose any other steps/actions, ensure strictly no other text, conversational filler, or formatting follows FINAL line).

<h2 id="users-request">User's Request</h2>
%%ARGS%%

