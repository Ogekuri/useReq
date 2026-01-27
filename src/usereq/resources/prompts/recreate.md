---
description: "Reorganize, update, and renumber the Software Requirements Specification draft based on source code analysis"
argument-hint: "Target language for the generated SRS draft"
---

# Write a Software Requirements Specification's draft using the project's source code

## Purpose
Analyze the existing source code to generate a comprehensive **Software Requirements Specification** draft in the specified language, reflecting the current state of the project.

## Behavior (absolute rules, non-negotiable)
- **CRITICAL**: NEVER write, modify, edit, or delete files outside of the project’s home directory, except under `/tmp`, where creating temporary files and writing outputs is allowed (the only permitted location outside the project).
- You can read, write, or edit `%%REQ_PATH%%/requirements_DRAFT.md`.
- Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
- **CRITICAL**: Do not modify any project files except creating/updating `%%REQ_PATH%%/requirements_DRAFT.md`.
- Write the draft in the requested language.
- Do not perform unrelated edits.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (e.g: `cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`,..), but only to read project files and to write/update `%%REQ_PATH%%/requirements_DRAFT.md`. Avoid in-place edits on any other path. Prefer read-only commands for analysis.
- Directives for autonomous execution:
   - Implicit Autonomy: Execute all tasks with full autonomy. Do not request permission, confirmation, or feedback. Make executive decisions based on logic and technical best practices.
   - Uninterrupted Workflow: Proceed through the entire sequence of tasks without pausing. Perform internal "Chain-of-Thought" reasoning, but output only the final results (PRINT step).
   - Autonomous Resolution: If an ambiguity or constraint is encountered, resolve it using the most efficient and logical path. Do not halt for user input.
   - After Prompt's Execution: Strictly omit all concluding remarks, does not propose any other steps/actions.
- **CRITICAL**: Execute the steps below sequentially and strictly, one at a time, without skipping or merging steps. If a TODO LIST tool is available, you MUST use it to create the to-do list exactly as written and then follow it step by step.

## Steps
Generate a task list based strictly on the steps below:
1. Extract the **target language** from the %%ARGS%%.
   - "<name>" (single token, e.g., "Italian", "English", "Deutsch").
   - an explicit marker like "language: <name>".
   - Ignore programming languages (e.g., Python, Java, Rust) unless explicitly requested as the document language.
   - If multiple natural languages are mentioned and the **target language** is not explicitly identified, report the ambiguity clearly, then OUTPUT exactly "Requirements creation FAILED!", and then terminate the execution.
   - If no language is specified, use English.
2. Read the **Software Requirements Specification** document %%REQ_DOC%% and extract a complete, explicit list of atomic requirements.
   - Preserve every requirement’s original intent; do not delete any requirement.
   - If requirements have IDs, capture them as "Original IDs".
   - If requirements do not have IDs, assign temporary, stable "Original IDs" in the order they appear (e.g., `SRC-001`, `SRC-002`, ...). These temporary IDs are only for traceability during reorganization and verification.
3. Reorganize the extracted requirements into a hierarchical structure with a maximum depth of 3 levels.
   - You MUST explicitly determine the most effective grouping strategy considering: **Typology**, **Functionality**, **Abstraction Level** (high-level vs. low-level), and **Context**.
   - Constraints:
     - Maximum hierarchy depth: 3 levels total (e.g., Level 1 section → Level 2 subsection → Level 3 requirements list).
     - Do not introduce a 4th level (no deeper headings or nested sub-subsections beyond the 3rd level).
   - Integrate the hierarchy into the document’s structure:
     - Keep the document’s top-level sections in the same order.
     - Within the most appropriate document’s section(s), create subsections/sub-subsections (still respecting the max depth) to represent the chosen groupings.
4. Verify full coverage of the input requirements after reorganization.
   - Perform a strict one-to-one coverage check: every extracted "Original ID" MUST appear exactly once in the reorganized structure (either as the requirement itself or as an explicitly merged/rewritten equivalent).
   - If any requirement was rewritten for clarity, you MUST ensure the rewrite is meaning-preserving.
   - If any requirement is missing or duplicated, you MUST fix the structure before proceeding.
5. Add all requirements necessary to ensure each future requirement will be placed in the correct section/subsection, as part of document itself.
   - For each section/subsection you created, add a short, unambiguous "Scope/Grouping" requirement stating what belongs there.
   - Format the requirements as a bulleted list, utilizing 'shall' or 'must' to indicate mandatory actions. Translate 'shall'/'must' into their closest equivalents in the **target language**.
   - If it does not exist, create the appropriate section for the requirements that define how to edit the document itself.
6. Analyze the project's source code to identify very important functionalities, critical behaviors, or logic that are implemented but NOT currently documented in the input requirements.
   - Add missing requirements to the reorganized draft and place them into the appropriate section/subsection (respecting the max 3-level hierarchy).
   - Requirements for the output:
     - Scan the codebase for high-importance functionalities, critical behaviors, or logic that are NOT currently documented in the reorganized requirements.
     - Describe any text-based UI and/or GUI functionality implemented.
     - Describe the application's functionalities and configurability implemented.
     - Describe the any critical behaviors, or very important logic.
     - Include the project’s file/folder structure (tree view) with a sensible depth limit (e.g., max depth 4) and exclude large/generated directories (e.g., `node_modules/`, `dist/`, `build/`, `target/`, `.venv/`, `.git/`).
     - Only report performance optimizations if there is explicit evidence (e.g., comments, benchmarks, complexity-relevant changes, profiling notes, or clearly optimized code patterns). Otherwise, state ‘No explicit performance optimizations identified’.
     - Format the requirements as a bulleted list, utilizing 'shall' or 'must' to indicate mandatory actions. Translate 'shall'/'must' into their closest equivalents in the **target language**.
7. Update/edit every requirements that specifies the document itself writing language, replacing it consistently with the **target language**, without changing any other constraints or the requirements’ intended meaning.
8. Create or update the **Software Requirements Specification** document with the recreated requirements draft at `%%REQ_PATH%%/requirements_DRAFT.md`.
   - Write requirements, section titles, tables, and other content in **target language**.
   - Describe every project requirement clearly, succinctly, and unambiguously.
   - Format the requirements as a bulleted list, utilizing 'shall' or 'must' to indicate mandatory actions. Translate 'shall'/'must' into their closest equivalents in the **target language**.
   - Output the entire response in clean, properly formatted Markdown.
9. Re-number all requirements in `%%REQ_PATH%%/requirements_DRAFT.md` and preserve all cross-references.
   - You MUST perform a complete renumbering of the requirements in a consistent, deterministic order (document order).
   - You MUST update every internal cross-reference to requirement identifiers so that references still point to the correct renumbered requirement.
   - If renumbering and reference-updating cannot be performed safely with simple text operations, you MUST implement and execute a Python renumbering utility.
     - Prefer executing the program inline (e.g., via `python -c` or a here-doc) to avoid creating additional project files.
     - The program MUST only read and write `%%REQ_PATH%%/requirements_DRAFT.md` and MUST NOT write anywhere else.
     - The program MUST produce (in print output) the mapping from old requirement IDs to new requirement IDs.
10. Re-read `%%REQ_PATH%%/requirements_DRAFT.md` and cross-reference with the source code.
   - Verify that the drafted requirements **accurately reflect the actual code behavior** (True State).
   - If the code contains obvious bugs or partial implementations, ensure the requirement draft explicitly notes these limitations.
   - Report `OK` if the draft accurately describes the code (even if the code is buggy). Report `FAIL` only if the draft makes assertions that are not present or contradicted by the source code.
11. PRINT in the response presenting results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence).
12. OUTPUT exactly "Requirements reorganized and updated!".
