---
description: "Reorganize, update, and renumber the Software Requirements Specification draft based on source code analysis"
argument-hint: "No arguments utilized by the prompt logic (English only)"
usage: >
  Select this prompt when %%DOC_PATH%%/REQUIREMENTS.md already exists but must be rebuilt into a clean structure and deterministically RENUMBERED, including an explicit old-ID → new-ID mapping, grounded in evidence from code under %%SRC_PATHS%%. Output is only the rewritten SRS (English), preserving meaning while improving organization and traceability; source code, tests, %%DOC_PATH%%/WORKFLOW.md, and %%DOC_PATH%%/REFERENCES.md must not change. Do NOT select for incremental requirement edits or behavior changes (use /req.change or /req.new), for drafting SRS from user request only (use /req.write), or for implementation/fixing/refactoring work (use /req.fix, /req.refactor, /req.cover, /req.implement).
---

# Reorganize, update, and renumber the Software Requirements Specification draft based on source code analysis

## Purpose
Rebuild, reorganize, and deterministically renumber the SRS (`%%DOC_PATH%%/REQUIREMENTS.md`) from repository evidence so downstream LLM Agents can rely on a clean structure and stable traceability when driving subsequent design/implementation work.

## Scope
In scope: static analysis of source under %%SRC_PATHS%% (and targeted tests only as evidence when needed) to rewrite `%%DOC_PATH%%/REQUIREMENTS.md` in English, including required ID mapping and complete renumbering per the prompt’s rules. Out of scope: any changes to source code, tests, `%%DOC_PATH%%/WORKFLOW.md`, or `%%DOC_PATH%%/REFERENCES.md`.


## Professional Personas
- **Act as a Senior Technical Requirements Engineer** when analyzing source code to infer behavior: ensure every software requirement generated is atomic, unambiguous, and empirically testable.
- **Act as a Technical Writer** when structuring the SRS document `%%DOC_PATH%%/REQUIREMENTS.md`: use RFC 2119 keywords exclusively (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY) and never use "shall"; maintain a clean, hierarchical Markdown structure with a maximum depth of 3 levels.
- **Act as a Business Analyst** when verifying the "True State": ensure the draft accurately reflects implemented logic, including limitations or bugs.


## Absolute Rules, Non-Negotiable
- **CRITICAL**: NEVER write, modify, edit, or delete files outside of the project’s home directory, except under `/tmp`, where creating temporary files and writing outputs is allowed (the only permitted location outside the project).
- You can read, write, or edit `%%DOC_PATH%%/REQUIREMENTS.md`.
- Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
- **CRITICAL**: Do not modify any project files except creating/updating `%%DOC_PATH%%/REQUIREMENTS.md`.
- **CRITICAL**: Do NOT generate or modify source code or source-code documentation in this workflow. Only create/update the requirements document(s) explicitly in scope.
- **CRITICAL**: Formulate all new or edited requirements using a highly structured, machine-interpretable format Markdown with unambiguous, atomic syntax to ensure maximum reliability for downstream LLM agentic reasoning, avoiding any conversational filler or subjective adjectives; the **target audience** is other **LLM Agents** and Automated Parsers, NOT humans, use high semantic density, optimized to contextually enable an LLM to perform future refactoring or extension.
- **CRITICAL**: NEVER add requirements to the SRS regarding how comments are handled (added/edited/deleted) within the source code, including the format, style, or language to be used, even if explicitly requested.

## Behavior
- Write the document in English.
- Do not perform unrelated edits.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (e.g.,`cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`,..), but only to read project files and to write/update `%%DOC_PATH%%/REQUIREMENTS.md`. Avoid in-place edits on any other path. Prefer read-only commands for analysis.


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
   - You MUST maintain a *check-list* internally with `3` Steps (one item per Step).
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
Create internally a *check-list* for the **Global Roadmap** including all the numbered steps below: `1..3`, and start following the roadmap at the same time, following the instructions of Step 1 (Generate the Software Requirements Specification). Do not add extra intent-adjustment checks unless explicitly listed in the Steps section.
1. Generate the **Software Requirements Specification**
   - Read the template at `.req/docs/Requirements_Template.md` and apply its guidelines to the requirement draft.
   - Read the **Software Requirements Specification** document `%%DOC_PATH%%/REQUIREMENTS.md` and extract a complete, explicit list of atomic requirements.
      - Preserve every requirement’s original intent; do not delete any requirement.
      - If requirements have IDs, capture them as "Original IDs".
      - If requirements do not have IDs, assign temporary, stable "Original IDs" in the order they appear (e.g., `SRC-001`, `SRC-002`, ...). These temporary IDs are only for traceability during reorganization and verification.
   - Reorganize the extracted requirements into a hierarchical structure with a maximum depth of 3 levels.
      - You MUST explicitly determine the most effective grouping strategy considering: **Typology**, **Functionality**, **Abstraction Level** (high-level vs. low-level), and **Context**.
      - Constraints:
        - Maximum hierarchy depth: 3 levels total (e.g., Level 1 section → Level 2 subsection → Level 3 requirements list).
        - Do not introduce a 4th level (no deeper headings or nested sub-subsections beyond the 3rd level).
      - Integrate the hierarchy into the document’s structure:
        - Keep the document’s top-level sections in the same order.
        - Within the most appropriate document’s section(s), create subsections/sub-subsections (still respecting the max depth) to represent the chosen groupings.
   - Verify full coverage of the input requirements after reorganization.
      - Perform a strict one-to-one coverage check: every extracted "Original ID" MUST appear exactly once in the reorganized structure (either as the requirement itself or as an explicitly merged/rewritten equivalent). Keep "Original ID" markers only for verification, then remove all of them only after verification is fully complete and immediately before saving; the saved `%%DOC_PATH%%/REQUIREMENTS.md` MUST NOT contain any "Original ID" markers.
      - If any requirement was rewritten for clarity, you MUST ensure the rewrite is meaning-preserving.
      - If any requirement is missing or duplicated, you MUST fix the structure before proceeding.
   - Follow the template’s section schema; use headings to encode grouping.
   - Do NOT add per-section "Scope/Grouping" requirements.
   - Ensure every requirement remains atomic and testable after reorganization; split compound statements rather than adding meta-requirements.
   - Keep document-authoring rules only in the dedicated section (no duplication).
   - Analyze the project's main existing source code, ignoring unit test source code, documentation automation source code, and any companion scripts (e.g., launching scripts, environment management scripts, example scripts, ...), to identify very important functionalities, critical behaviors, or logic that are implemented but NOT currently documented in the input requirements.
      - Add missing requirements to the reorganized draft and place them into the appropriate section/subsection (respecting the max 3-level hierarchy).
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
   - Create or overwrite the **Software Requirements Specification** document at `%%DOC_PATH%%/REQUIREMENTS.md`.   
      - Ensure that every software requirement you generate is atomic, unambiguous, and empirically testable. For each requirement, you must provide:
        * A comprehensive, clear functional description.
        * The precise expected behavior (include acceptance criteria with testable conditions where possible).
        * Provide implementation guidance limited to constraints, invariants, and acceptance criteria, and do not invent detailed algorithms unless they are directly evidenced by the source code.
      - Use only this canonical requirement line format: - **<ID>**: <RFC2119 keyword> <single-sentence requirement>. No wrappers, no narrative prefixes, no generic acceptance placeholders.
      - Ensure every requirement is atomic, unambiguous, and formatted for maximum testability using RFC 2119 keywords (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY)
      - Write each requirement for other LLM **Agents** and Automated Parsers, NOT humans.
      - Must be optimized for machine comprehension. Do not write flowery prose. Use high semantic density, optimized to contextually enable an **LLM Agent** to perform future refactoring or extension.
      - Write requirements, section titles, tables, and other content in **English language**.
      - Follow `.req/docs/Requirements_Template.md`.
      - Output the entire response in clean, properly formatted Markdown.
   - Re-number all requirements in `%%DOC_PATH%%/REQUIREMENTS.md` and preserve all cross-references.
      - You MUST perform a complete renumbering of the requirements in a consistent, deterministic order (document order).
      - You MUST update every internal cross-reference to requirement identifiers so that references still point to the correct renumbered requirement.
      - Prefer a single inline Python renumbering script only if necessary; otherwise use minimal deterministic text operations. Always output only the ID mapping and the minimal diff summary.
        - Prefer executing the program inline (e.g., via `python -c` or a here-doc) to avoid creating additional project files.
        - The program MUST only read and write `%%DOC_PATH%%/REQUIREMENTS.md` and MUST NOT write anywhere else.
        - The program MUST produce (in print output) the mapping from old requirement IDs to new requirement IDs.
        - The program MUST keep the file a properly formatted Markdown document.
2. Validate the **Software Requirements Specification**
   - Review `%%DOC_PATH%%/REQUIREMENTS.md`. If previously read and present in context, use that content; otherwise read the file and cross-reference with the source code.
      - Verify that the drafted requirements **accurately reflect the actual code behavior** (True State).
      - If the code contains obvious bugs or partial implementations, ensure the requirement draft explicitly notes these limitations.
      - Report `OK` if the draft accurately describes the code (even if the code is buggy). Report `FAIL` only if the draft makes assertions that are not present or contradicted by the source code.
3. Present results
   - PRINT, in the response, the results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence). Use the fixed report schema: ## **Outcome**, ## **Requirement Delta**, ## **Design Delta**, ## **Implementation Delta**, ## **Verification Delta**, ## **Evidence**, ## **Assumptions**, ## **Next Workflow**. Final line MUST be exactly: STATUS: OK or STATUS: ERROR.
