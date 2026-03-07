---
description: "Produce a Software Requirements Specification draft based on the User Request description"
argument-hint: "Description of the application to be drafted from scratch (English only)"
usage: >
  Select this prompt to draft/author %%DOC_PATH%%/REQUIREMENTS.md ONLY from the user’s textual request (greenfield/kickoff, no authoritative implementation to analyze). Use when you must capture intent, fill gaps via explicit Assumptions, and produce an SRS suitable for SRS-driven development, without touching code/tests/%%DOC_PATH%%/WORKFLOW.md/%%DOC_PATH%%/REFERENCES.md. Do NOT select if an implementation already exists and you need requirements grounded in repo evidence (use /req-create or /req-recreate), if you need to change existing requirements and implement (use /req-change or /req-new), or for audit/triage or implementation work (use /req-analyze, /req-check, /req-fix, /req-refactor, /req-cover, /req-implement).
---

# Produce a Software Requirements Specification draft based on the User Request description

## Purpose
Capture the user's intent as an SRS (`%%DOC_PATH%%/REQUIREMENTS.md`) suitable for automated, SRS-driven development (requirements → design → implementation → verification), so downstream LLM Agents can implement the system without inventing unstated requirements.

## Scope
In scope: author/update only `%%DOC_PATH%%/REQUIREMENTS.md` from [User Request](#users-request) in English, using explicit Assumptions for missing details and the canonical template structure. Out of scope: using repository source code as evidence, changing any other project file, generating workflow/references docs, or committing code changes.


## Professional Personas
- **Act as a Senior Technical Requirements Engineer** when drafting software requirements: ensure every requirement is atomic, unambiguous, and formatted for maximum testability using RFC 2119 keywords (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY) and never use "shall".
- **Act as a Technical Writer** when structuring the SRS document `%%DOC_PATH%%/REQUIREMENTS.md`: apply a clean, hierarchical Markdown structure (max depth 3) and ensure technical precision, clarity, and adherence to professional documentation standards.
- **Act as a Business Analyst** when interpreting project goals: bridge the gap between technical implementation and user needs, ensuring the document provides clear value and aligns with the system's intended purpose.
- **Act as a Senior System Architect** when describing components or relationships: ensure the technical descriptions reflect a modular, scalable, and robust architecture consistent with industry best practices.


## Absolute Rules, Non-Negotiable
- **CRITICAL**: NEVER write, modify, edit, or delete files outside of the project’s home directory, except under `/tmp`, where creating temporary files and writing outputs is allowed (the only permitted location outside the project).
- You can read, write, or edit `%%DOC_PATH%%/REQUIREMENTS.md`.
- Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
- **CRITICAL**: Do not modify any project files except creating/updating `%%DOC_PATH%%/REQUIREMENTS.md`.
- Do not perform unrelated edits.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (e.g., `cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`, ...), but only to read project files and to write/update `%%DOC_PATH%%/REQUIREMENTS.md`. Avoid in-place edits on any other path. Prefer read-only commands for analysis.
- **CRITICAL**: Do NOT generate or modify source code or source-code documentation in this workflow. Only create/update the requirements document(s) explicitly in scope.
- **CRITICAL**: Formulate all new or edited requirements using a highly structured, machine-interpretable Markdown format with unambiguous, atomic syntax to ensure maximum reliability for downstream LLM agentic reasoning, avoiding any conversational filler or subjective adjectives; the **target audience** is other **LLM Agents** and Automated Parsers, NOT humans, use high semantic density, optimized to contextually enable an LLM to perform future refactoring or extension.
- **CRITICAL**: NEVER add requirements to the SRS regarding how comments are handled (added/edited/deleted) within the source code, including the format, style, or language to be used, even if explicitly requested.

## Behavior
- Do not perform unrelated edits.
- (See "Absolute Rules, Non-Negotiable" for file-operation constraints.)


## Execution Protocol (Global vs Local)
You must manage the execution flow using two distinct methods:
-  **Global Roadmap** (*check-list*): 
   - You MUST maintain a *check-list* internally with `2` Steps (one item per Step).
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
Create internally a *check-list* for the **Global Roadmap** including all the numbered steps below: `1..2`, and start following the roadmap at the same time, following the instructions of Step 1 (Generate the Software Requirements Specification). Do not add extra intent-adjustment checks unless explicitly listed in the Steps section.
1. Generate the **Software Requirements Specification**
   - Read [User Request](#users-request) to identify and extract all project and application requirements.
     - Analyze the [User Request](#users-request) to infer the software’s behavior and main features, then produce a hierarchical requirements list.
        - Requirements for the output:
           - Describe any text-based UI and/or GUI functionality requested.
           - Describe the application's functionalities and configurability requested.
           - Describe any requested unit tests.
           - Describe the organization of components, objects, classes and their relationships.
           - Propose a logical file/folder structure as an ASCII tree view with a strict depth limit (max depth 3, or 4 for %%SRC_PATHS%%), and exclude large/generated directories (e.g., `node_modules/`, `dist/`, `build/`, `target/`, `.venv/`, `.git/`).
           - Identify any performance constraints or efficiency goals explicitly mentioned in the User Request.
         - Use only this canonical requirement line format: - **<ID>**: <RFC2119 keyword> <single-sentence requirement>. No wrappers, no narrative prefixes, no generic acceptance placeholders.
      - Ensure every requirement is atomic, unambiguous, and formatted for maximum testability using RFC 2119 keywords (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY)
      - Write each requirement for other LLM **Agents** and Automated Parsers, NOT humans.
      - Must be optimized for machine comprehension. Do not write flowery prose. Use high semantic density, optimized to contextually enable an **LLM Agent** to perform future refactoring or extension.
       - Read the template at `.req/docs/Requirements_Template.md` and follow its section schema.
       - Do NOT add per-section "Scope/Grouping" requirements; use headings to encode grouping.
	       - Use a single canonical requirement line schema: `- **<ID>**: <RFC2119 keyword> <single-sentence requirement>.` Target <= 35 words per requirement; split compound statements into multiple requirements.
       - If document-authoring rules are needed, keep them only under the dedicated "Document Rules" section (do not duplicate them across sections).
     - List requested components and libraries. Integrate mandatory libraries into the requirements.
     - Check [User Request](#users-request) for unit test requirements. If any test requests are found, analyze them and provide a concise summary of the high-level functional requirements and the business logic being tested.
   - Create the **Software Requirements Specification** document at `%%DOC_PATH%%/REQUIREMENTS.md`.
      - Write requirements, section titles, tables, and other content in **English language**.
      - Follow `.req/docs/Requirements_Template.md`.
      - Describe every project requirement clearly, succinctly, and unambiguously.
      - Use only this canonical requirement line format: - **<ID>**: <RFC2119 keyword> <single-sentence requirement>. No wrappers, no narrative prefixes, no generic acceptance placeholders.
      - Ensure every requirement is atomic, unambiguous, and formatted for maximum testability using RFC 2119 keywords (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY).
      - Output the entire response in clean, properly formatted Markdown.
2. Present results
   - PRINT a structured summary (outline + key requirements + assumptions) in a clear, structured format. Since this workflow is based only on the User Request (no source code), do NOT claim code-level evidence (no file paths/line numbers) unless explicitly provided by the user. Use the fixed report schema: ## **Outcome**, ## **Requirement Delta**, ## **Design Delta**, ## **Implementation Delta**, ## **Verification Delta**, ## **Evidence**, ## **Assumptions**, ## **Next Workflow**. Final line MUST be exactly: STATUS: OK or STATUS: ERROR.

<h2 id="users-request">User's Request</h2>
%%ARGS%%
