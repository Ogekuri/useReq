---
description: "Reorganize, update, and renumber the Software Requirements Specification draft based on source code analysis"
argument-hint: "Target language for the generated SRS draft"
---

# Reorganize, update, and renumber the Software Requirements Specification draft based on source code analysis

## Purpose
Analyze the existing source code to generate a comprehensive **Software Requirements Specification** draft in the specified language, reflecting the current state of the project.


## Professional Personas
- **Act as a Senior Technical Requirements Engineer** when analyzing source code to infer behavior: ensure every software requirement generated is atomic, unambiguous, and empirically testable.
- **Act as a Technical Writer** when structuring the SRS document %%REQ_DIR%%: apply ISO-standard terminology (e.g., "shall", "must") and maintain a clean, hierarchical Markdown structure with a maximum depth of 3 levels.
- **Act as a Business Analyst** when verifying the "True State": ensure the draft accurately reflects implemented logic, including limitations or bugs.


## Absolute Rules, Non-Negotiable
- **CRITICAL**: NEVER write, modify, edit, or delete files outside of the project’s home directory, except under `/tmp`, where creating temporary files and writing outputs is allowed (the only permitted location outside the project).
- You can read, write, or edit `%%REQ_PATH%%/requirements_DRAFT.md`.
- Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
- **CRITICAL**: Do not modify any project files except creating/updating `%%REQ_PATH%%/requirements_DRAFT.md`.

## Behavior
- Write the draft in the requested language.
- Do not perform unrelated edits.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (e.g.,`cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`,..), but only to read project files and to write/update `%%REQ_PATH%%/requirements_DRAFT.md`. Avoid in-place edits on any other path. Prefer read-only commands for analysis.


## Execution Protocol (Global vs Local)
You must manage the execution flow using two distinct methods:
-  **Global Roadmap** (*check-list*): 
   - You MUST maintain a *check-list* internally with `12` Steps (one item per Step).
   - **Do NOT** use the *task-list tool* for this high-level roadmap.
-  **Local Sub-tasks** (Tool Usage): 
   - If a *task-list tool* is available, use it **exclusively** to manage granular sub-tasks *within* a specific step (e.g., in Step 8: "1. Edit file A", "2. Edit file B"; or in Step 10: "1. Fix test X", "2. Fix test Y").
   - Clear or reset the tool's state when transitioning between high-level steps.

## Exceution Directives (absolute rules, non-negotiable)
During the execution flow you MUST follow this directives:
- **CRITICAL** Autonomous Execution:
   - Implicit Autonomy: Execute all tasks with full autonomy. Do not request permission, confirmation, or feedback. Make executive decisions based on logic and technical best practices.
   - Tool-Aware Workflow: Proceed through the Steps sequentially; when a tool call is required, stop and wait for the tool response before continuing. Never fabricate tool outputs or tool results. Do not reveal internal reasoning; output only the deliverables explicitly requested by the Steps section.
   - Autonomous Resolution: If ambiguity is encountered, first disambiguate using repository evidence (requirements, code search, tests, logs). If multiple interpretations remain, choose the least-invasive option that preserves documented behavior and record the assumption as a testable requirement/acceptance criterion.
   - After Prompt's Execution: Strictly omit all concluding remarks, does not propose any other steps/actions.
- **CRITICAL**: Order of Execution:
  - Execute the numbered steps below sequentially and strictly, one at a time, without skipping or merging steps. Create and maintain a *check-list* internally during executing the Steps. Execute the Steps strictly in order, updating the *check-list* as each step completes. 
- **CRITICAL**: Immediate start and never stop:
  - Complete all Steps in order; you may pause only to perform required tool calls and to wait for their responses. Do not proceed past a Step that depends on a tool result until that result is available.
  - Start immediately by creating a *check-list* for the **Global Roadmap** and directly start to following the roadmap from the Step 1.


## Steps
Create internally a *check-list* for the **Global Roadmap** including all below numbered steps: `1..12`, and start to following the roadmap at the same time, with the instruction of the Step 1 (Extract the target language). Do not add additional intent adjustments check, except if it's explicit indicated on steps.
1. Extract the **target language** from the %%ARGS%%.
   - "<name>" (single token, e.g., "Italian", "English", "Deutsch").
   - an explicit marker like "language: <name>".
   - Ignore programming languages (e.g., Python, Java, Rust) unless explicitly requested as the document language.
   - If multiple natural languages are mentioned and the **target language** is not explicitly identified, report the ambiguity clearly, then OUTPUT exactly "Requirements creation FAILED, unclear language!", and then terminate the execution.
   - If no language is specified, use English.
2. Read the template at `.req/templates/requirements.md` and apply its guidelines to the requirement draft. If the **target language** is not English, you MUST translate all template section headers and structural text into the **target language**.
3. Read the **Software Requirements Specification** document %%REQ_DIR%% and extract a complete, explicit list of atomic requirements.
   - Preserve every requirement’s original intent; do not delete any requirement.
   - If requirements have IDs, capture them as "Original IDs".
   - If requirements do not have IDs, assign temporary, stable "Original IDs" in the order they appear (e.g., `SRC-001`, `SRC-002`, ...). These temporary IDs are only for traceability during reorganization and verification.
4. Reorganize the extracted requirements into a hierarchical structure with a maximum depth of 3 levels.
   - You MUST explicitly determine the most effective grouping strategy considering: **Typology**, **Functionality**, **Abstraction Level** (high-level vs. low-level), and **Context**.
   - Constraints:
     - Maximum hierarchy depth: 3 levels total (e.g., Level 1 section → Level 2 subsection → Level 3 requirements list).
     - Do not introduce a 4th level (no deeper headings or nested sub-subsections beyond the 3rd level).
   - Integrate the hierarchy into the document’s structure:
     - Keep the document’s top-level sections in the same order.
     - Within the most appropriate document’s section(s), create subsections/sub-subsections (still respecting the max depth) to represent the chosen groupings.
5. Verify full coverage of the input requirements after reorganization.
   - Perform a strict one-to-one coverage check: every extracted "Original ID" MUST appear exactly once in the reorganized structure (either as the requirement itself or as an explicitly merged/rewritten equivalent).
   - If any requirement was rewritten for clarity, you MUST ensure the rewrite is meaning-preserving.
   - If any requirement is missing or duplicated, you MUST fix the structure before proceeding.
6. Add or modify requirements necessary to ensure each future requirement will be placed in the correct section/subsection, as part of document itself.
   - For each section/subsection you created, add a short, unambiguous "Scope/Grouping" requirement stating what belongs there.
   - Format the requirements as a bulleted list, utilizing 'shall' or 'must' to indicate mandatory actions. Translate 'shall'/'must' into their closest equivalents in the **target language**.
   - If it does not exist, create the appropriate section for the requirements that define how to edit the document itself.
7. Analyze the project's main existing source code, ignoring unit tests source code, documents automation source code and any companion-scripts (e.g., launching scripts, environments management scripts, examples scripts,..), to identify very important functionalities, critical behaviors, or logic that are implemented but NOT currently documented in the input requirements.
   - Add missing requirements to the reorganized draft and place them into the appropriate section/subsection (respecting the max 3-level hierarchy).
   - Requirements for the output:
     - Scan the codebase for high-importance functionalities, critical behaviors, or logic that are NOT currently documented in the reorganized requirements.
     - Describe any text-based UI and/or GUI functionality implemented.
     - Describe the application's functionalities and configurability implemented.
     - Describe the any critical behaviors, or very important logic.
     - Include the project’s file/folder structure (tree view) with a sensible depth limit (max depth 3, or 4 for src/ directories) and exclude large/generated directories (e.g., `node_modules/`, `dist/`, `build/`, `target/`, `.venv/`, `.git/`).
     - Only report performance optimizations if there is explicit evidence (e.g., comments, benchmarks, complexity-relevant changes, profiling notes, or clearly optimized code patterns). Otherwise, state ‘No explicit performance optimizations identified’.
   - Format the requirements as a bulleted list, utilizing 'shall' or 'must' to indicate mandatory actions. Translate 'shall'/'must' into their closest equivalents in the **target language**.
   - Require evidence for every newly added requirement: file path + symbol/function + short excerpt (or a test that demonstrates behavior).
   - If evidence is weak (e.g., only naming conventions), force a label: Inferred (Low confidence), or exclude it.
   - When describing existing functionality, describe the actual implementation logic, not the implied intent based on function names. If the code implies a feature but implements it partially, describe the partial state.
8. Update/edit every requirements that specifies the document itself writing language, replacing it consistently with the **target language**, without changing any other constraints or the requirements’ intended meaning.
9. Create or overwrite the **Software Requirements Specification** document with the recreated requirements draft at `%%REQ_PATH%%/requirements_DRAFT.md`.   
   - Ensure that every software requirement you generate is atomic, unambiguous, and empirically testable. For each requirement, you must provide:
     * A comprehensive functional clear description .
     * The precise expected behavior (include acceptance criteria with testable conditions where possible).
     * Provide implementation guidance limited to constraints, invariants, and acceptance criteria, and do not invent detailed algorithms unless they are directly evidenced by the source code..
   - Format the requirements as a bulleted list, utilizing 'shall' or 'must' to indicate mandatory actions. Translate 'shall'/'must' into their closest equivalents in the **target language**.
   - Write requirements, section titles, tables, and other content in **target language**.
   - Follow `.req/templates/requirements.md` translated into **target language**.
   - Output the entire response in clean, properly formatted Markdown.
10. Re-number all requirements in `%%REQ_PATH%%/requirements_DRAFT.md` and preserve all cross-references.
   - You MUST perform a complete renumbering of the requirements in a consistent, deterministic order (document order).
   - You MUST update every internal cross-reference to requirement identifiers so that references still point to the correct renumbered requirement.
   - Prefer a single inline Python renumbering script only if necessary; otherwise use minimal deterministic text operations. Always output only the ID mapping and the minimal diff summary.
     - Prefer executing the program inline (e.g., via `python -c` or a here-doc) to avoid creating additional project files.
     - The program MUST only read and write `%%REQ_PATH%%/requirements_DRAFT.md` and MUST NOT write anywhere else.
     - The program MUST produce (in print output) the mapping from old requirement IDs to new requirement IDs.
     - The program MUST keep the file a properly formatted Markdown document.
11. Review `%%REQ_PATH%%/requirements_DRAFT.md`. If previously read and present in context, use that content; otherwise read the file and cross-reference with the source code.
   - Verify that the drafted requirements **accurately reflect the actual code behavior** (True State).
   - If the code contains obvious bugs or partial implementations, ensure the requirement draft explicitly notes these limitations.
   - Report `OK` if the draft accurately describes the code (even if the code is buggy). Report `FAIL` only if the draft makes assertions that are not present or contradicted by the source code.
12. PRINT in the response presenting results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence). The final line of the output must be EXACTLY "Requirements reorganized and updated!".
