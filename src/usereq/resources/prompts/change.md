---
description: "Update the requirements and implement the corresponding changes"
argument-hint: "Description of the requirements changes to implement"
---

# Update the requirements and implement the corresponding changes

## Purpose
Update the requirements document based on the user request and make the necessary source code changes to satisfy the updated requirements.

## Behavior (absolute rules, non-negotiable)
- **CRITICAL**: NEVER write, modify, edit, or delete files outside of the project’s home directory, except under `/tmp`, where creating temporary files and writing outputs is allowed (the only permitted location outside the project).
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
- Propose changes based only on the requirements, user request, and repository evidence. Every proposed code change MUST reference at least one requirement ID (or explicit new request text) it implements.
- Use technical documents to implement features and changes.
- Any new text added to an existing document MUST match that document’s current language.
- Prefer clean implementation over legacy support. Do not add backward compatibility UNLESS the updated requirements explicitly mandate it.
- Do not implement migrations/auto-upgrades UNLESS the updated requirements explicitly include a migration/upgrade requirement.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (e.g: `cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`,..). Prefer read-only commands for analysis.
- **CRITICAL**: Directives for autonomous execution:
   - Implicit Autonomy: Execute all tasks with full autonomy. Do not request permission, confirmation, or feedback. Make executive decisions based on logic and technical best practices.
   - Uninterrupted Workflow: Proceed through the entire sequence of tasks without pausing. Perform internal "Chain-of-Thought" reasoning, but output only the final results (last PRINT step).
   - Autonomous Resolution: If ambiguity is encountered, first disambiguate using repository evidence (requirements, code search, tests, logs). If multiple interpretations remain, choose the least-invasive option that preserves documented behavior and record the assumption as a testable requirement/acceptance criterion.
   - After Prompt's Execution: Strictly omit all concluding remarks, does not propose any other steps/actions.
- **CRITICAL**: Execute the steps below sequentially and strictly, one at a time, without skipping or merging steps. If a TODO LIST tool is available, you MUST use it to create the to-do list exactly as written and then follow it step by step.

## Steps
Generate a task list based strictly on the steps below:
1. **CRITICAL**: Check GIT Status
   - Check GIT status. Confirm you are inside a clean git repo executing `git rev-parse --is-inside-work-tree >/dev/null 2>&1 && test -z "$(git status --porcelain)" && git symbolic-ref -q HEAD >/dev/null 2>&1 || { printf '%s\n' 'GIT status check FAILED!'; exit 1; }`. If it fails, OUTPUT exactly "GIT status check FAILED!", and then terminate the execution.
2. Read %%REQ_DOC%% and [User Request](#users-request), then apply the outlined guidelines when documenting changes to the requirements (follow the existing style, structure, and language).
3. GENERATE a detailed **Software Requirements Specification Update** documenting the exact modifications to requirements needed to implement the changes described by the [User Request](#users-request). This **Software Requirements Specification Update** must account for the original User Request and all subsequent changes and adjustments for %%REQ_DOC%%, must contain only the exact requirement edits needed: provide patch-style ‘Before → After’ blocks for each modified section/requirement, quoting only the changed text (no full-document rewrites):
   - Never introduce new requirements solely to explicitly forbid functions/features/behaviors. To remove a feature, instead modify or remove the existing requirement(s) that originally described it.
   - In this step, do not edit, create, delete, or rename any source code files in the project (including refactors or formatting-only changes).
4. Apply the **Software Requirements Specification Update** to %%REQ_DOC%%, following its formatting, language, and guidelines. Do NOT introduce any additional edits beyond what the **Software Requirements Specification Update** describes.
5. GENERATE a detailed **Comprehensive Technical Implementation Report** documenting the exact modifications to the source code that will cover all new requirements in **Software Requirements Specification Update** and the [User Request](#users-request). The **Comprehensive Technical Implementation Report** MUST be implementation-only and patch-oriented: for each file, list exact edits (functions/classes touched), include only changed snippets, and map each change to the requirement ID(s) it satisfies (no narrative summary)
   - If directory/directories %%REQ_DIR%% exists, list files in %%REQ_DIR%% using `ls` or `tree`. Determine relevance by running a quick keyword search (e.g., `rg`/`git grep`) for impacted modules/features; read only the tech docs that match, then apply only those guidelines.Ensure the proposed code changes conform to those documents; adjust the **Comprehensive Technical Implementation Report** if needed. Do not apply guidelines from files you have not explicitly read via a tool action. 
6.  Where unit tests exist, plan the necessary refactoring and expansion to cover new requirements and include these details in the **Comprehensive Technical Implementation Report**.
7.  If a migration/compatibility need is discovered but not specified in requirements, propose a requirements update describing it, then OUTPUT exactly "Change request FAILED!", revert changes executing `git checkout .` and `git clean -fd`, and then terminate the execution.
8.  IMPLEMENT the **Comprehensive Technical Implementation Report** in the source code (creating new files/directories if necessary). You may make minimal mechanical adjustments needed to fit the actual codebase (file paths, symbol names), but you MUST NOT add new features or scope beyond the **Comprehensive Technical Implementation Report**.  
9.  Review %%REQ_DOC%%. If previously read and present in context, use that content; otherwise read the file and cross-reference with the source code to check all requirements.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - It is forbidden to mark a requirement as `OK` without quoting the exact code snippet that satisfies it, alongside the file path and line ranges. Line ranges MUST be obtained from tooling output (e.g., `nl -ba` / `sed -n`) and MUST NOT be estimated.. If strict evidence (exact file and logic match) is missing, you MUST report `FAIL`. Do not assume implicit behavior.
   - For every `FAIL`, provide evidence: file path(s), line numbers (when relevant), and a short explanation.
10. Run the updated test suite. 
   - Verify that the implemented changes satisfy the requirements and pass tests.
   - If a test fails, analyze if the failure is due to a bug in the source code or an incorrect test assumption. You are authorized to update or refactor existing tests ONLY if they cover logic that was explicitly modified by the updated requirements. When a test fails, verify: does the failure align with the new requirement?
     - IF YES (the test expects the old behavior): Update the test to match the new requirement.
     - IF NO (the test fails on unrelated logic): You likely broke something else. Fix the source code."
   - Fix the source code to pass valid tests. After fixing, re-run the relevant tests to confirm they pass. Attempt to fix up to 2 times then, if they fail again, report the failure, then OUTPUT exactly "Change request FAILED!", revert changes executing `git checkout .` and `git clean -fd`, and then terminate the execution.
   - Limitations: Do not introduce new features or change the architecture logic during this fix phase. If a fix requires substantial refactoring or requirements changes, report the failure, then OUTPUT exactly "Change request FAILED!", revert changes executing `git checkout .` and `git clean -fd`, and then terminate the execution.
   - You may freely modify the new tests you added in the previous steps. For pre-existing tests, update or refactor them ONLY if they conflict with the new or modified requirements. Preserve the intent of tests covering unchanged logic. If you must modify a pre-existing test, you must include a specific section in your final report explaining why the test assumption was wrong or outdated, citing line numbers.
11. %%WORKFLOW%%
12. **CRITICAL**: Stage & commit
   - Show a summary of changes with `git diff` and `git diff --stat`.
   - Stage changes explicitly (prefer targeted add; avoid `git add -A` if it may include unintended files): `git add <file...>` (ensure to include all modified source code & test, %%REQ_DOC%% and WORKFLOW.md only if it was modified/created).
   - Ensure there is something to commit with: `git diff --cached --quiet && echo "Nothing to commit. Aborting."`. If command output contains "Aborting", OUTPUT exactly "No changes to commit.", and then terminate the execution.
   - Commit a structured commit message with: `git commit -m "change(useReq): <DESCRIPTION> [<DATE>]"`
      - Generate `<DATE>` executing `date +"%Y-%m-%d %H:%M:%S"`.
      - Generate `<DESCRIPTION>` as clear and concise description of changes made on requirements, source code and tests, using English language.
13. Confirm the repo is clean with `git status --porcelain`, If NOT empty OUTPUT exactly "Change request FAILED!", and then terminate the execution.
14. PRINT in the response presenting the **Software Requirements Specification Update** and the **Comprehensive Technical Implementation Report** in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence). The final line of the output must be EXACTLY "Change request completed!".

<h2 id="users-request">User's Request</h2>
%%ARGS%%
