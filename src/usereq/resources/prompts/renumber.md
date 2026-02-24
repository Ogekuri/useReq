---
description: "Deterministically renumber requirement IDs in the Software Requirements Specification without changing requirement text or order"
argument-hint: "No arguments utilized by the prompt logic (English only)"
usage: >
  Select this prompt when %%DOC_PATH%%/REQUIREMENTS.md already exists and you must enforce a clean, progressive, deterministic requirement ID sequence in document order, WITHOUT changing any requirement text, headings, or ordering. Only IDs and internal requirement-ID cross-references may change; all requirement content after the ID MUST remain byte-identical. Output is only the updated SRS; source code, tests, %%DOC_PATH%%/WORKFLOW.md, and %%DOC_PATH%%/REFERENCES.md must not change.
---

# Deterministically renumber requirement IDs in the Software Requirements Specification

## Purpose
Deterministically renumber requirement IDs in `%%DOC_PATH%%/REQUIREMENTS.md` to produce a clean, progressive numbering scheme while preserving the exact requirement text and document order so downstream LLM Agents can rely on stable, sequential identifiers.

## Scope
In scope: renumbering requirement identifiers in `%%DOC_PATH%%/REQUIREMENTS.md` in document order and updating internal cross-references to those identifiers, without modifying any requirement text, headings, or ordering. Out of scope: any changes to source code, tests, `%%DOC_PATH%%/WORKFLOW.md`, or `%%DOC_PATH%%/REFERENCES.md`.


## Professional Personas
- **Act as a Senior Technical Requirements Engineer** when analyzing source code to infer behavior: ensure every software requirement generated is atomic, unambiguous, and empirically testable.
- **Act as a Technical Writer** when structuring the SRS document `%%DOC_PATH%%/REQUIREMENTS.md`: use RFC 2119 keywords exclusively (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY) and never use "shall"; maintain a clean, hierarchical Markdown structure with a maximum depth of 3 levels.
- **Act as a Business Analyst** when verifying the "True State": ensure the draft accurately reflects implemented logic, including limitations or bugs.
- **Act as an Expert GitOps Engineer** when executing git workflows, especially when creating/removing/managing git worktrees to isolate changes safely.


## Pre-requisite: Execution Context
- Generate a pseudo-random UUID v4 (or an equivalent unique alphanumeric tag) to identify the current operation, and refer to it as <EXECUTION_ID>. If available, use `uuidgen`.
- Identify the current git branch with `git branch --show-current` and refer to it as <ORIGINAL_BRANCH>.
- Identify the Git project name with `basename "$(git rev-parse --show-toplevel)"` and refer to it as <PROJECT_NAME>.


## Absolute Rules, Non-Negotiable
- **CRITICAL**: NEVER write, modify, edit, or delete files outside of the active git worktree directory, except under `/tmp`, and except for creating/removing the dedicated worktree directory `../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>` as explicitly required by this workflow.
- You can read, write, or edit `%%DOC_PATH%%/REQUIREMENTS.md`.
- Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
- **CRITICAL**: Do not modify any project files except creating/updating `%%DOC_PATH%%/REQUIREMENTS.md`.
- **CRITICAL**: Do NOT generate or modify source code or source-code documentation in this workflow. Only create/update the requirements document(s) explicitly in scope.
- **CRITICAL**: Do NOT add, delete, split, merge, or edit requirement content; only change requirement IDs and requirement-ID cross-references.
- **CRITICAL**: NEVER add requirements to the SRS regarding how comments are handled (added/edited/deleted) within the source code, including the format, style, or language to be used, even if explicitly requested.

## Behavior
- Write the document in English.
- Do not perform unrelated edits.
- Do NOT change any requirement content or document structure; only change requirement IDs and requirement-ID cross-references.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (e.g., `cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`, ...), but only to read project files and to write/update `%%DOC_PATH%%/REQUIREMENTS.md`. Avoid in-place edits on any other path. Prefer read-only commands for analysis.


## Execution Protocol (Global vs Local)
You must manage the execution flow using two distinct methods:
-  **Global Roadmap** (*check-list*): 
   - You MUST maintain a *check-list* internally with `8` Steps (one item per Step).
   - **Do NOT** use the *task-list tool* for this high-level roadmap.
-  **Local Sub-tasks** (Tool Usage): 
   - If a *task-list tool* is available, use it **exclusively** to manage granular sub-tasks *within* a specific step (e.g., in Step X: "1. Edit file A", "2. Edit file B"; or in Step Y: "1. Fix test K", "2. Fix test L").
   - Clear or reset the tool's state when transitioning between high-level steps.

## Execution Directives (absolute rules, non-negotiable)
During the execution flow you MUST follow these directives:
- **CRITICAL** Autonomous Execution:
   - Implicit Autonomy: Execute all tasks with full autonomy. Do not request permission, confirmation, or feedback. Make executive decisions based on logic and technical best practices.
   - Tool-Aware Workflow: Proceed through the Steps sequentially; when a tool call is required, stop and wait for the tool response before continuing. Never fabricate tool outputs or tool results. Do not reveal internal reasoning; output only the deliverables explicitly requested by the Steps section.
   - Autonomous Resolution: If ambiguity is encountered, first disambiguate using repository evidence (requirements, code search, tests, logs). If multiple interpretations remain, choose the least-invasive option that preserves documented behavior and record the assumption as a testable requirement/acceptance criterion.
   - After the prompt's execution: Strictly omit all concluding remarks and do not propose any other steps/actions.
- **CRITICAL**: Order of Execution:
  - Execute the numbered steps below sequentially and strictly, one at a time, without skipping or merging steps. Create and maintain a *check-list* internally while executing the Steps. Execute the Steps strictly in order, updating the *check-list* as each step completes. 
- **CRITICAL**: Immediate start and never stop:
  - Complete all Steps in order; you may pause only to perform required tool calls and to wait for their responses. Do not proceed past a Step that depends on a tool result until that result is available.
  - Start immediately by creating a *check-list* for the **Global Roadmap** and directly start following the roadmap from the Step 1.


## Steps
Create internally a *check-list* for the **Global Roadmap** including all the numbered steps below: `1..8`, and start following the roadmap at the same time, following the instructions of Step 1. Do not add extra intent-adjustment checks unless explicitly listed in the Steps section.
1. **CRITICAL**: Check GIT Status
   - Check GIT status. Confirm you are inside a clean git repo by executing `git rev-parse --is-inside-work-tree >/dev/null 2>&1 && test -z "$(git status --porcelain)" && { git symbolic-ref -q HEAD >/dev/null 2>&1 || git rev-parse --verify HEAD >/dev/null 2>&1; } || { printf '%s\n' 'ERROR: Git status unclear!'; }`. If it prints any text containing the word "ERROR", OUTPUT exactly "ERROR: Git status unclear!", and then terminate the execution.
2. **CRITICAL**: Check `%%DOC_PATH%%/REQUIREMENTS.md`, `%%DOC_PATH%%/WORKFLOW.md` and `%%DOC_PATH%%/REFERENCES.md` file presence
   - If the `%%DOC_PATH%%/REQUIREMENTS.md` file does NOT exist, OUTPUT exactly "ERROR: File %%DOC_PATH%%/REQUIREMENTS.md does not exist, generate it with the /req-write prompt!", and then terminate the execution.
   - If the `%%DOC_PATH%%/WORKFLOW.md` file does NOT exist, OUTPUT exactly "ERROR: File %%DOC_PATH%%/WORKFLOW.md does not exist, generate it with the /req-workflow prompt!", and then terminate the execution.
   - If the `%%DOC_PATH%%/REFERENCES.md` file does NOT exist, OUTPUT exactly "ERROR: File %%DOC_PATH%%/REFERENCES.md does not exist, generate it with the /req-references prompt!", and then terminate the execution.
3. **CRITICAL**: Worktree Generation & Isolation
   - Generate a pseudo-random UUID v4 (or an equivalent unique alphanumeric tag) to identify the current operation, and refer to it as <EXECUTION_ID>. If available, use `uuidgen`.
   - Identify the current git branch with `git branch --show-current` and refer to it as <ORIGINAL_BRANCH>.
   - Identify the Git project name with `basename "$(git rev-parse --show-toplevel)"` and refer to it as <PROJECT_NAME>.
   - Create a dedicated worktree OUTSIDE the current repository directory to isolate changes:
      - Execute: `git worktree add ../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID> -b userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`
      - If `.gitignore` excludes `.req/config.json`, copy `.req/config.json` into the new worktree before continuing:
         - `if git check-ignore -q .req/config.json && [ -f .req/config.json ]; then mkdir -p ../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>/.req && cp .req/config.json ../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>/.req/config.json; fi`
   - Move into the worktree directory and perform ALL subsequent steps from there:
      - `cd ../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`
4. **CRITICAL**: Renumber requirement IDs in the **Software Requirements Specification**
   - Read the **Software Requirements Specification** document `%%DOC_PATH%%/REQUIREMENTS.md`.
   - Determine the existing requirement ID scheme, if any (prefix + numeric width). If multiple schemes exist, select the most common one as the canonical output scheme; if no clear scheme exists, use `REQ-001`, `REQ-002`, ... as the output scheme.
   - Renumber requirements in strict document order (top-to-bottom, as they appear in the file) to a progressive sequence starting at 1.
      - You MUST NOT modify any requirement text after `:`, any headings, any ordering, or any non-ID content.
      - You MUST NOT add, delete, split, merge, or reorganize requirements.
      - You MUST ensure the final set of requirement IDs is unique and strictly progressive (no gaps) in the chosen scheme.
   - Update every internal cross-reference to requirement identifiers so that references still point to the correct renumbered requirement.
      - Cross-references MUST be updated wherever requirement IDs are referenced in `%%DOC_PATH%%/REQUIREMENTS.md`.
      - If an internal reference points to a non-existent requirement (before or after renumbering), treat this as an error and report it.
   - Produce and include in the final report an explicit old-ID → new-ID mapping in document order.
   - Save changes by overwriting `%%DOC_PATH%%/REQUIREMENTS.md` with only the ID and cross-reference updates applied.
5. Validate the **Software Requirements Specification**
   - Review `%%DOC_PATH%%/REQUIREMENTS.md` and validate the renumbering invariants:
      - Only requirement IDs and requirement-ID cross-references changed; all other text is identical.
      - Requirement IDs are unique and strictly progressive in document order.
      - All internal cross-references point to an existing renumbered requirement ID.
      - Report `OK` if the invariants hold. Report `FAIL` if any invariant is violated.
6. **CRITICAL**: Stage & commit
   - Show a summary of changes with `git diff` and `git diff --stat`.
   - Stage changes explicitly (prefer targeted add; avoid `git add -A` if it may include unintended files): `git add <file...>` (ensure to include only `%%DOC_PATH%%/REQUIREMENTS.md`).
   - Ensure there is something to commit with: `git diff --cached --quiet && echo "Nothing to commit. Aborting."`. If command output contains "Aborting", OUTPUT exactly "No changes to commit.", and then terminate the execution.
   - Commit a structured commit message with: `git commit -m "docs(<COMPONENT>)<BREAKING>: <DESCRIPTION> [useReq]"`
      - Set `<COMPONENT>` to the most specific component, module, or function affected. If multiple areas are touched, choose the primary one. If you cannot identify a unique component, use `core`.
      - Set `<DESCRIPTION>` to a short, clear summary in **English language** of what changed, including (when applicable) updates to: requirements/specs, source code, tests. Use present tense, avoid vague wording, and keep it under ~80 characters if possible.
      - Set `<BREAKING>` to `!` if a breaking change was implemented (a modification to an API, library, or system that breaks backward compatibility, causing dependent client applications or code to fail or behave incorrectly), set empty otherwise.
      - Include main features added, requirements changes, or a bug-fix description adding a multi-line comment (maximum 10 lines).
         - Do not include the 'Co-authored-by' trailer or any AI attribution.
   - Confirm the repo is clean with `git status --porcelain`. If it is NOT empty, override the final line with EXACTLY "WARNING: Renumber request completed with unclean git repository!".
7. **CRITICAL**: Merge Conflict Management
   - Return to the original repository directory (the sibling directory of the worktree). After working in `../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`, return with: `cd ../<PROJECT_NAME>`
   - Ensure you are on <ORIGINAL_BRANCH>: `git checkout <ORIGINAL_BRANCH>`
   - If `.gitignore` excludes `.req/config.json`, remove `.req/config.json` before merge:
      - `if git check-ignore -q .req/config.json; then rm -f .req/config.json; fi`
   - Merge the isolated branch into <ORIGINAL_BRANCH>: `git merge userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`
   - If the merge completes successfully, remove the worktree directory with force: `git worktree remove ../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID> --force`
   - If the merge fails or results in conflicts, do NOT remove the worktree directory and override the final line with EXACTLY "WARNING: Renumber request completed with merge conflicting!".
8. Present results
   - PRINT, in the response, the results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence). Use the fixed report schema: ## **Outcome**, ## **Requirement Delta**, ## **Design Delta**, ## **Implementation Delta**, ## **Verification Delta**, ## **Evidence**, ## **Assumptions**, ## **Next Workflow**. Final line MUST be exactly: STATUS: OK or STATUS: ERROR.
