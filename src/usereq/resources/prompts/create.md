---
description: "Write a Software Requirements Specification using the project's source code"
argument-hint: "No arguments utilized by the prompt logic (English only)"
usage: >
  Select this prompt when an implementation already exists under %%SRC_PATHS%% but %%DOC_PATH%%/REQUIREMENTS.md is missing or incomplete, and you need to bootstrap/update the SRS to reflect the code’s true current behavior (with evidence) BEFORE any SRS-driven change work. Output is only an updated SRS; source code, tests, %%DOC_PATH%%/WORKFLOW.md, and %%DOC_PATH%%/REFERENCES.md must remain unchanged. Do NOT select if you must draft the SRS from a user description without relying on code (use /req-write), if you must reorganize/renumber an existing SRS with an explicit old→new ID mapping (use /req-recreate), or if you intend to implement/fix/refactor anything (use /req-change, /req-new, /req-fix, /req-refactor, /req-cover, /req-implement).
---

# Write a Software Requirements Specification using the project's source code

## Purpose
Bootstrap an SRS (`%%DOC_PATH%%/REQUIREMENTS.md`) from repository evidence so downstream LLM Agents can start SRS-driven work grounded in what the code actually does (requirements → design → implementation → verification), without guessing undocumented behavior.

## Scope
In scope: static analysis of source under %%SRC_PATHS%% (and targeted tests only as evidence when needed) to create/update `%%DOC_PATH%%/REQUIREMENTS.md` in English. Out of scope: any changes to source code, tests, `%%DOC_PATH%%/WORKFLOW.md`, or `%%DOC_PATH%%/REFERENCES.md`.


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
- **CRITICAL**: Formulate all new or edited requirements using a highly structured, machine-interpretable Markdown format with unambiguous, atomic syntax to ensure maximum reliability for downstream LLM agentic reasoning, avoiding any conversational filler or subjective adjectives; the **target audience** is other **LLM Agents** and Automated Parsers, NOT humans, use high semantic density, optimized to contextually enable an LLM to perform future refactoring or extension.
- **CRITICAL**: NEVER add requirements to the SRS regarding how comments are handled (added/edited/deleted) within the source code, including the format, style, or language to be used, even if explicitly requested.

## Behavior
- Write the document in English.
- Do not perform unrelated edits.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (e.g., `cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`, ...), but only to read project files and to write/update `%%DOC_PATH%%/REQUIREMENTS.md`. Avoid in-place edits on any other path. Prefer read-only commands for analysis.


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
   - Analyze the project's main existing source code, ignoring unit test source code, documentation automation source code, and any companion scripts (e.g., launching scripts, environment management scripts, example scripts, ...), to infer the software’s behavior and main features, then produce a hierarchical requirements structure with a maximum depth of 3 levels.
      - Requirements for the output:
         - Describe any text-based UI and/or GUI functionality implemented.
         - Describe the application's functionalities and configurability implemented.
         - Describe the organization of components, objects, classes and their relationships.
         - Include the project’s file/folder structure (tree view) with a sensible depth limit (max depth 3, or 4 for %%SRC_PATHS%% directories) and exclude large/generated directories (e.g., `node_modules/`, `dist/`, `build/`, `target/`, `.venv/`, `.git/`).
         - Only report performance optimizations if there is explicit evidence (e.g., comments, benchmarks, complexity-relevant changes, profiling notes, or clearly optimized code patterns). Otherwise, state ‘No explicit performance optimizations identified’.
	      - Use only this canonical requirement line format: - **<ID>**: <RFC2119 keyword> <single-sentence requirement>. Target <= 35 words per requirement; split compound behavior into separate requirement IDs. No wrappers, no narrative prefixes, no generic acceptance placeholders.
      - Ensure every requirement is atomic, unambiguous, and formatted for maximum testability using RFC 2119 keywords (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY)
      - Write each requirement for other LLM **Agents** and Automated Parsers, NOT humans.
      - Must be optimized for machine comprehension. Do not write flowery prose. Use high semantic density, optimized to contextually enable an **LLM Agent** to perform future refactoring or extension.
      - Require evidence for every newly added requirement: file path + symbol/function + short excerpt (or a test that demonstrates behavior).
      - If evidence is weak or ambiguous (e.g., based solely on naming conventions or commented-out code), strictly exclude the requirement to avoid documenting non-existent features.
      - When describing existing functionality, describe the actual implementation logic, not the implied intent based on function names. If the code implies a feature but implements it partially, describe the partial state.
   - Follow the template’s section schema; use headings to encode grouping.
   - Do NOT add per-section "Scope/Grouping" requirements.
   - Preserve Requirement IDs and keep requirements short and atomic; split compound requirements into multiple IDs.
   - Keep document-authoring rules only in the dedicated section (no duplication).
   - List used components and libraries ONLY if evidenced by manifest/lock/config files or direct imports; cite the file path(s) used as evidence and do not guess.
   - Locate and read only the unit tests relevant to the inferred features/requirements; summarize test coverage at a high level and deep-dive only into failing or high-risk areas. Analyze them and provide a concise summary of the high-level functional requirements and business logic being tested.
	   - Create the **Software Requirements Specification** document at `%%DOC_PATH%%/REQUIREMENTS.md`.
	      - Ensure every requirement remains atomic, single-sentence, and testable (target <= 35 words per requirement). If acceptance criteria/procedures are needed, express them as separate requirement IDs (prefer `TST-` test requirements), not as multi-sentence sub-bullets under a single requirement.
	      - Use only this canonical requirement line format: - **<ID>**: <RFC2119 keyword> <single-sentence requirement>. Target <= 35 words per requirement; split compound behavior into separate requirement IDs. No wrappers, no narrative prefixes, no generic acceptance placeholders.
      - Ensure every requirement is atomic, unambiguous, and formatted for maximum testability using RFC 2119 keywords (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY)
      - Write each requirement for other LLM **Agents** and Automated Parsers, NOT humans.
      - Must be optimized for machine comprehension. Do not write flowery prose. Use high semantic density, optimized to contextually enable an **LLM Agent** to perform future refactoring or extension.
      - Write requirements, section titles, tables, and other content in **English language**.
      - Follow `.req/docs/Requirements_Template.md`.
      - Output the entire response in clean, properly formatted Markdown.
2. Validate the **Software Requirements Specification**
   - Review `%%DOC_PATH%%/REQUIREMENTS.md`. If previously read and present in context, use that content; otherwise read the file and cross-reference with the source code.
      - Verify that the drafted requirements **accurately reflect the actual code behavior** (True State).
      - If the code contains obvious bugs or partial implementations, ensure the requirement draft explicitly notes these limitations.
      - Report `OK` if the draft accurately describes the code (even if the code is buggy). Report `FAIL` only if the draft makes assertions that are not present or contradicted by the source code.
3. Present results
   - PRINT, in the response, the results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence). Use the fixed report schema: ## **Outcome**, ## **Requirement Delta**, ## **Design Delta**, ## **Implementation Delta**, ## **Verification Delta**, ## **Evidence**, ## **Assumptions**, ## **Next Workflow**. Final line MUST be exactly: STATUS: OK or STATUS: ERROR.
