---
description: "Produce a Software Requirements Specification draft based on the User Request description"
argument-hint: "Description of the application to be drafted from scratch"
---

# Produce a Software Requirements Specification draft based on the User Request description

## Purpose
Draft a new **Software Requirements Specification** draft based entirely on the user's description and specifications, without referencing existing source code.


## Professional Personas
- **Act as a Senior Technical Requirements Engineer** when drafting software requirements: ensure every requirement is atomic, unambiguous, and formatted for maximum testability using standard "shall/must" terminology.
- **Act as a Technical Writer** when structuring the document: apply a clean, hierarchical Markdown structure (max depth 3) and ensure technical precision, clarity, and adherence to professional documentation standards.
- **Act as a Business Analyst** when interpreting project goals: bridge the gap between technical implementation and user needs, ensuring the document provides clear value and aligns with the system's intended purpose.
- **Act as a Senior System Architect** when describing components or relationships: ensure the technical descriptions reflect a modular, scalable, and robust architecture consistent with industry best practices.


## Behavior (absolute rules, non-negotiable)
- **CRITICAL**: NEVER write, modify, edit, or delete files outside of the project’s home directory, except under `/tmp`, where creating temporary files and writing outputs is allowed (the only permitted location outside the project).
- You can read, write, or edit `%%REQ_PATH%%/requirements_DRAFT.md`.
- Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
- **CRITICAL**: Do not modify any project files except creating/updating `%%REQ_PATH%%/requirements_DRAFT.md`.
- Do not perform unrelated edits.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (e.g.,`cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`,..), but only to read project files and to write/update `%%REQ_PATH%%/requirements_DRAFT.md`. Avoid in-place edits on any other path. Prefer read-only commands for analysis.


## Execution Protocol (Global vs Local)
You must manage the execution flow using two distinct methods:
-  **Global Roadmap (Markdown Checklist)**: 
   - You MUST maintain a plain-text Markdown checklist of the `9` Steps (one item per Step) below in your response. 
   - Mark items as `[x]` ONLY when the step is fully completed.
   - **Do NOT** use the task-list tool for this high-level roadmap. It must be visible in the chat text.
-  **Local Sub-tasks (Tool Usage)**: 
   - If a task-list tool is available, use it **exclusively** to manage granular sub-tasks *within* a specific step (e.g., in Step 8: "1. Edit file A", "2. Edit file B"; or in Step 10: "1. Fix test X", "2. Fix test Y").
   - Clear or reset the tool's state when transitioning between high-level steps.

## Exceution Directives (absolute rules, non-negotiable)
During the execution flow you MUST follow this directives:
- **CRITICAL** Autonomous Execution:
   - Implicit Autonomy: Execute all tasks with full autonomy. Do not request permission, confirmation, or feedback. Make executive decisions based on logic and technical best practices.
   - Uninterrupted Workflow: Proceed through the entire sequence of tasks without pausing; keep reasoning internal ("Chain-of-Thought") and output only the deliverables explicitly requested by the Steps section.
   - Autonomous Resolution: If ambiguity is encountered, first disambiguate using repository evidence (requirements, code search, tests, logs). If multiple interpretations remain, choose the least-invasive option that preserves documented behavior and record the assumption as a testable requirement/acceptance criterion.
   - After Prompt's Execution: Strictly omit all concluding remarks, does not propose any other steps/actions.
- **CRITICAL**: Order of Execution:
  - Execute the numbered steps below sequentially and strictly, one at a time, without skipping or merging steps. Create and maintain a *check-list* internally during executing the Steps. Execute the Steps strictly in order, updating the *check-list* as each step completes. 
- **CRITICAL**: Immediate start and never stop:
  - Complete all tasks of steps without pausing or any stop, except explicit indicated.
  - Start immediately by creating a *check-list* for the **Global Roadmap** and directly start to following the roadmap from the Step 1.


## Steps
Create internally a *check-list* for the **Global Roadmap** including all below numbered steps: `1..9`, and start to following the roadmap at the same time, with the instruction of the Step 1 (Read user request).
1. Read [User Request](#users-request) to identify and extract all project and application requirements.
2. Extract the **target language** from the [User Request](#users-request).
   - Prefer an explicit marker like "language: <name>".
   - Ignore programming languages (e.g., Python, Java, Rust) unless explicitly requested as the document language.
   - If multiple natural languages are mentioned, infer the **target language** based on context (e.g., phrases like "translate into...", "write in..."). Only if the target remains completely ambiguous, report it, then OUTPUT exactly "Requirements creation FAILED, unclear language!", and then terminate the execution.
   - If no language is specified, use English.
3. Read the template at `.req/templates/requirements.md` and apply its guidelines to the requirement draft. If the **target language** is not English, you MUST translate all template section headers and structural text into the **target language**.
4. Analyze the [User Request](#users-request) to infer the software’s behavior and main features, then produce a hierarchical requirements list.
   - Requirements for the output:
      - Describe any text-based UI and/or GUI functionality requested.
      - Describe the application's functionalities and configurability requested.
      - Describe any requested unit tests.
      - Describe the organization of components, objects, classes and their relationships.
      - Propose a logical file/folder structure for the project as a ascii tree view based on the requirements.
      - Identify any performance constraints or efficiency goals explicitly mentioned in the User Request.
    - Format the requirements as a bulleted list, utilizing 'shall' or 'must' to indicate mandatory actions. Translate 'shall'/'must' into their closest equivalents in the **target language**.
5. Add or modify requirements necessary to ensure each future requirement will be placed in the correct section/subsection, as part of document itself.
   - For each section/subsection you created, add a short, unambiguous "Scope/Grouping" requirement stating what belongs there.
   - Format the requirements as a bulleted list, utilizing 'shall' or 'must' to indicate mandatory actions. Translate 'shall'/'must' into their closest equivalents in the **target language**.
   - If it does not exist, create the appropriate section for the requirements that define how to edit the document itself.
6. List requested components and libraries.
7. Check [User Request](#users-request) for unit test requirements. If any test requests are found, analyze them and provide a concise summary of the high-level functional requirements and the business logic being tested.
8. Create the **Software Requirements Specification** document with the requirements draft at `%%REQ_PATH%%/requirements_DRAFT.md`.
   - Write requirements, section titles, tables, and other content in **target language**.
   - Follow `.req/templates/requirements.md` translated into requested language.
   - Describe every project requirement clearly, succinctly, and unambiguously.
   - Format the requirements as a bulleted list, using 'shall' or 'must' to indicate mandatory actions. Translate these terms using their closest equivalents in the **target language**.
   - Output the entire response in clean, properly formatted Markdown.
9. PRINT in the response presenting the requirements draft in a clear, structured format. Since this workflow is based only on the User Request (no source code), do NOT claim code-level evidence (no file paths/line numbers) unless explicitly provided by the user. The final line of the output must be EXACTLY "Requirements written!".

<h2 id="users-request">User's Request</h2>
%%ARGS%%
