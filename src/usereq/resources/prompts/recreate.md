---
description: "Reorganize and update the Software Requirements Specification based on source code analysis (preserve requirement IDs)"
argument-hint: "No arguments utilized by the prompt logic (English only)"
usage: >
  Select this prompt when %%DOC_PATH%%/REQUIREMENTS.md already exists but must be rebuilt into a clean structure based on evidence from code under %%SRC_PATHS%%, while preserving all existing requirement IDs (no renumbering). Requirements may be reorganized, moved, grouped, and clarified, and new requirements may be added only with NEW non-colliding IDs appended beyond the existing ID space. Output is only the rewritten SRS (English); source code, tests, %%DOC_PATH%%/WORKFLOW.md, and %%DOC_PATH%%/REFERENCES.md must not change. Do NOT select for incremental requirement edits or behavior changes (use /req-change or /req-new), for drafting SRS from user request only (use /req-write), or for implementation/fixing/refactoring work (use /req-fix, /req-refactor, /req-cover, /req-implement).
---

# Reorganize and update the Software Requirements Specification draft based on source code analysis

## Purpose
Rebuild and reorganize the SRS (`%%DOC_PATH%%/REQUIREMENTS.md`) from repository evidence while preserving all existing requirement IDs so downstream LLM Agents can rely on a clean structure and stable traceability when driving subsequent design/implementation work.

## Scope
In scope: static analysis of source under %%SRC_PATHS%% (and targeted tests only as evidence when needed) to rewrite `%%DOC_PATH%%/REQUIREMENTS.md` in English, allowing reorganization and additions, but forbidding any renumbering/renaming of existing requirement IDs. Out of scope: any changes to source code, tests, `%%DOC_PATH%%/WORKFLOW.md`, or `%%DOC_PATH%%/REFERENCES.md`.


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
- **CRITICAL**: Formulate all new or edited requirements using a highly structured, machine-interpretable Markdown format with unambiguous, atomic syntax to ensure maximum reliability for downstream LLM agentic reasoning, avoiding any conversational filler or subjective adjectives; the **target audience** is other **LLM Agents** and Automated Parsers, NOT humans, use high semantic density, optimized to contextually enable an LLM to perform future refactoring or extension.
- **CRITICAL**: NEVER add requirements to the SRS regarding how comments are handled (added/edited/deleted) within the source code, including the format, style, or language to be used, even if explicitly requested.

## Behavior
- Write the document in English.
- Do not perform unrelated edits.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (e.g., `cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`, ...), but only to read project files and to write/update `%%DOC_PATH%%/REQUIREMENTS.md`. Avoid in-place edits on any other path. Prefer read-only commands for analysis.


## WORKFLOW.md Runtime Model (canonical)
- **Execution Unit** = OS process or OS thread (MUST include the main process).
- **Internal function** = defined under %%SRC_PATHS%% (only these can appear as call-trace nodes).
- **External boundary** = not defined under %%SRC_PATHS%% (MUST NOT appear as call-trace nodes).
- `%%DOC_PATH%%/WORKFLOW.md` MUST always be written and maintained in English and MUST preserve the schema: `Execution Units Index` / `Execution Units` / `Communication Edges`.

## Source Construct Extraction via req --find / req --files-find
When you need hard evidence from source code (APIs, entrypoints, data types, imports, constants, decorators/annotations, modules/namespaces), use req to extract language constructs as structured markdown (with signatures + line ranges, and optional line-numbered code).
### What these commands do (and what they don’t)
- They extract named constructs (e.g., CLASS, FUNCTION, STRUCT, INTERFACE, IMPORT, …) and filter them by TAG and name-regex.
- The regex (PATTERN) matches the construct name only (not the body). If you need “search inside code”, use rg/git grep in addition.
- Output is markdown, grouped by file: header @@@ <filepath> | <language>, then per-construct blocks with:
    - ### <TAG>: <name> + optional Signature + Lines: <start>-<end>
    - optional extracted Doxygen fields (if present in/around the construct)
    - a fenced code block containing the complete construct slice, with comments stripped (strings preserved)
### Choose the right mode
- Project-wide scan (configured --src-dir): use --find (requires --here or --base)
    - Correct syntax is: req --here --find <TAG_FILTER> <NAME_REGEX>
    - Note: --find does not take a filename; it scans all files under the configured source dirs.
- Target specific files: use --files-find (standalone; --here is optional but harmless)
    - Syntax: req --here --files-find <TAG_FILTER> <NAME_REGEX> <FILE1> [FILE2 ...]
### Always enable line-numbered code when you plan to cite evidence
Add --enable-line-numbers so code lines are prefixed as <n>::
- req --here --enable-line-numbers --find "<TAG_FILTER>" "<NAME_REGEX>"
- req --here --enable-line-numbers --files-find "<TAG_FILTER>" "<NAME_REGEX>" <FILE...>
### TAGs and filters
- TAG_FILTER is a pipe-separated list (case-insensitive): e.g. CLASS|FUNCTION|IMPORT
- Tags are language-dependent; unsupported tags are simply ignored for that language, and files may be skipped if none of the requested tags apply.
- To discover the exact supported TAGs list (per language), run: req -h and read the --files-find help section.
- Practical “broad but safe” TAG_FILTER for analysis (cross-language): CLASS|STRUCT|ENUM|INTERFACE|TRAIT|IMPL|FUNCTION|METHOD|MODULE|NAMESPACE|TYPE_ALIAS|TYPEDEF|IMPORT|CONSTANT|VARIABLE|MACRO|DECORATOR|COMPONENT|PROPERTY|PROTOCOL|EXTENSION|UNION
### Regex rules (NAME_REGEX)
- It’s a Python-style regex applied with re.search() against the construct name.
- Prefer anchored patterns when possible:
    - Exact: ^Foo$
    - Prefix: ^parse_
    - Suffix: Service$
    - Fallback: .* (only when scope is already constrained by files/TAGs)
### Failure modes you must handle
- If you get “no constructs found”, adjust one of: TAGs (supported?), file paths, or NAME_REGEX (valid regex?).
- This extractor is regex-based (not a full AST parser); treat results as evidence pointers, and confirm edge cases by opening the referenced file/lines if needed.


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
Create internally a *check-list* for the **Global Roadmap** including all the numbered steps below: `1..8`, and start following the roadmap at the same time, following the instructions of Step 1 (Check GIT Status). Do not add extra intent-adjustment checks unless explicitly listed in the Steps section.
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
4. Generate the **Software Requirements Specification**
   - Read the template at `.req/docs/Requirements_Template.md` and apply its guidelines to the requirement draft.
   - Read the **Software Requirements Specification** document `%%DOC_PATH%%/REQUIREMENTS.md` and extract a complete, explicit list of atomic requirements.
      - Preserve every requirement’s original intent; do not delete any requirement.
      - **ID preservation**: If a requirement already has an ID, you MUST keep that exact ID unchanged.
      - **No renumbering**: You MUST NOT renumber, rename, or otherwise change any pre-existing requirement ID, even if requirements are moved between sections or rewritten for clarity.
      - **ID assignment for missing IDs**: If any requirement does not have an ID, you MUST assign a NEW non-colliding ID that follows the document’s existing ID scheme (prefix + numeric width) and is appended beyond the existing ID space.
   - Reorganize the extracted requirements into a hierarchical structure with a maximum depth of 3 levels.
      - You MUST explicitly determine the most effective grouping strategy considering: **Typology**, **Functionality**, **Abstraction Level** (high-level vs. low-level), and **Context**.
      - Constraints:
        - Maximum hierarchy depth: 3 levels total (e.g., Level 1 section → Level 2 subsection → Level 3 requirements list).
        - Do not introduce a 4th level (no deeper headings or nested sub-subsections beyond the 3rd level).
      - Integrate the hierarchy into the document’s structure:
        - Keep the document’s top-level sections in the same order.
        - Within the most appropriate document’s section(s), create subsections/sub-subsections (still respecting the max depth) to represent the chosen groupings.
   - Verify full coverage of the input requirements after reorganization.
      - Perform a strict one-to-one coverage check: every requirement ID present in the input `%%DOC_PATH%%/REQUIREMENTS.md` MUST appear exactly once in the saved output document.
      - You MUST NOT merge multiple input requirement IDs into a single output requirement line; each input ID must remain its own requirement line.
      - If any requirement was rewritten for clarity, you MUST ensure the rewrite is meaning-preserving and the requirement ID remains unchanged.
      - Target <= 35 words per requirement; split any compound behavior into separate IDs. If any compound requirement is split into multiple atomic requirements, the original requirement ID MUST remain attached to exactly one of the split requirements, and all additional split requirements MUST receive NEW non-colliding IDs appended beyond the existing ID space.
      - If any requirement is missing or duplicated, you MUST fix the structure before proceeding.
   - Follow the template’s section schema; use headings to encode grouping.
   - Do NOT add per-section "Scope/Grouping" requirements.
   - Ensure every requirement remains atomic and testable after reorganization; split compound statements rather than adding meta-requirements.
   - Keep document-authoring rules only in the dedicated section (no duplication).
   - Read `%%DOC_PATH%%/WORKFLOW.md` and `%%DOC_PATH%%/REFERENCES.md`, then analyze the project's main existing source code in %%SRC_PATHS%% directories, ignoring unit test source code, documentation automation source code, and any companion scripts (e.g., launching scripts, environment management scripts, example scripts, ...), to identify very important functionalities, critical behaviors, or logic that are implemented but NOT currently documented in the input requirements.
      - Add missing requirements to the reorganized draft and place them into the appropriate section/subsection (respecting the max 3-level hierarchy).
      - All added requirements MUST receive NEW non-colliding IDs appended beyond the existing ID space; new IDs MUST NOT collide with any existing ID in the document.
      - Requirements for the output:
        - Scan the codebase for high-importance functionalities, critical behaviors, or logic that are NOT currently documented in the reorganized requirements.
        - Describe any text-based UI and/or GUI functionality implemented.
        - Describe the application's functionalities and configurability implemented.
        - Describe any critical behaviors or important logic.
        - Include the project’s file/folder structure (tree view) with a sensible depth limit (max depth 3, or 4 for %%SRC_PATHS%% directories) and exclude large/generated directories (e.g., `node_modules/`, `dist/`, `build/`, `target/`, `.venv/`, `.git/`).
        - Only report performance optimizations if there is explicit evidence (e.g., comments, benchmarks, complexity-relevant changes, profiling notes, or clearly optimized code patterns). Otherwise, state ‘No explicit performance optimizations identified’.
      - Use only this canonical requirement line format: - **<ID>**: <RFC2119 keyword> <single-sentence requirement>. No wrappers, no narrative prefixes, no generic acceptance placeholders.
      - Ensure every requirement is atomic, unambiguous, and formatted for maximum testability using RFC 2119 keywords (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY)
      - Write each requirement for other LLM **Agents** and Automated Parsers, NOT humans.
      - Must be optimized for machine comprehension. Do not write flowery prose. Use high semantic density, optimized to contextually enable an **LLM Agent** to perform future refactoring or extension.
      - Require evidence for every newly added requirement: file path + symbol/function + short excerpt (or a test that demonstrates behavior).
      - If evidence is weak or ambiguous (e.g., based solely on naming conventions or commented-out code), strictly exclude the requirement to avoid documenting non-existent features.
      - When describing existing functionality, describe the actual implementation logic, not the implied intent based on function names. If the code implies a feature but implements it partially, describe the partial state.
   - Update or edit every requirement that specifies the document’s writing language, replacing it consistently with the **English language**, without changing any other constraints or the requirement’s intended meaning.
   - Overwrite the **Software Requirements Specification** document at `%%DOC_PATH%%/REQUIREMENTS.md`.   
	      - Ensure every requirement remains atomic, single-sentence, and testable (target <= 35 words per requirement). If acceptance criteria/procedures are needed, express them as separate requirement IDs (prefer `TST-` test requirements), not as multi-sentence sub-bullets under a single requirement.
      - Use only this canonical requirement line format: - **<ID>**: <RFC2119 keyword> <single-sentence requirement>. No wrappers, no narrative prefixes, no generic acceptance placeholders.
      - Ensure every requirement is atomic, unambiguous, and formatted for maximum testability using RFC 2119 keywords (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY)
      - Write each requirement for other LLM **Agents** and Automated Parsers, NOT humans.
      - Must be optimized for machine comprehension. Do not write flowery prose. Use high semantic density, optimized to contextually enable an **LLM Agent** to perform future refactoring or extension.
      - Write requirements, section titles, tables, and other content in **English language**.
      - Follow `.req/docs/Requirements_Template.md`.
      - Output the entire response in clean, properly formatted Markdown.
   - Preserve requirement identifiers and cross-references.
      - You MUST ensure all requirement IDs in the saved document are unique (no collisions).
      - If the input document contains duplicate IDs, preserve the first occurrence and assign NEW non-colliding IDs to subsequent duplicates (treating them as appended IDs), and update any now-ambiguous internal references as needed.
      - You MUST preserve internal cross-references to requirement IDs; update references only when you created NEW IDs (due to splits/collisions) or when you introduce references to newly added requirements.
5. Validate the **Software Requirements Specification**
   - Review `%%DOC_PATH%%/REQUIREMENTS.md`. If previously read and present in context, use that content; otherwise read the file and cross-reference with the source code.
      - Verify that the drafted requirements **accurately reflect the actual code behavior** (True State).
      - If the code contains obvious bugs or partial implementations, ensure the requirement draft explicitly notes these limitations.
      - Report `OK` if the draft accurately describes the code (even if the code is buggy). Report `FAIL` only if the draft makes assertions that are not present or contradicted by the source code.
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
   - Confirm the repo is clean with `git status --porcelain`. If it is NOT empty, override the final line with EXACTLY "WARNING: Recreate request completed with unclean git repository!".
7. **CRITICAL**: Merge Conflict Management
   - Return to the original repository directory (the sibling directory of the worktree). After working in `../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`, return with: `cd ../<PROJECT_NAME>`
   - Ensure you are on <ORIGINAL_BRANCH>: `git checkout <ORIGINAL_BRANCH>`
   - If `.gitignore` excludes `.req/config.json`, remove `.req/config.json` before merge:
      - `if git check-ignore -q .req/config.json; then rm -f .req/config.json; fi`
   - Merge the isolated branch into <ORIGINAL_BRANCH>: `git merge userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID>`
   - If the merge completes successfully, remove the worktree directory with force: `git worktree remove ../userReq-<PROJECT_NAME>-<ORIGINAL_BRANCH>-<EXECUTION_ID> --force`
   - If the merge fails or results in conflicts, do NOT remove the worktree directory and override the final line with EXACTLY "WARNING: Recreate request completed with merge conflicting!".
8. Present results
   - PRINT, in the response, the results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence). Use the fixed report schema: ## **Outcome**, ## **Requirement Delta**, ## **Design Delta**, ## **Implementation Delta**, ## **Verification Delta**, ## **Evidence**, ## **Assumptions**, ## **Next Workflow**. Final line MUST be exactly: STATUS: OK or STATUS: ERROR.
