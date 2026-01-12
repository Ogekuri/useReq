---
description: "Write a requirement draft from the standard template. Usage: req.write <language>."
---

# Write a requirement's draft based on standard template

## Purpose
- Produce a requirement draft from the standard template using the project's source code.

## Behavior
- **CRITICAL**: Create only the requirements draft and do not modify other project files.
- Ignore/exclude all files in .*/** from the project file analysis.
- Write the draft in the requested language.
- Do not perform unrelated edits.
- If a .venv directory is detected in the project root, explicitly use the Python interpreter located within that virtual environment for all code execution.
- Where unit tests exist, strictly adhere to the associated specific instructions.
- Follow the steps below in order.

## Steps
Write and then execute a TODO list following these steps strictly:
1. **Context Bootstrap & Persistence (MUST RUN FIRST, EVERY INVOCATION)**:
   - Ensure the directory `.req/context/` exists.
   - If the [User Request](#users-request) section contains non-empty text (from `$ARGUMENTS`):
     - SAVE it immediately to `.req/context/active_request.md` (overwrite existing content).
   - Otherwise (subsequent turns / reinvocations with empty `$ARGUMENTS`):
     - READ `.req/context/active_request.md` and use it as the restored user request.
   - If `$ARGUMENTS` is empty AND `.req/context/active_request.md` does not exist or is empty:
     - STOP immediately and respond asking for the user request to be provided again via `req.optimize <description>`.
   - From this point onward, refer only to `.req/context/active_request.md` for the user request.
2. Read [User Request](#users-request) to identify and extract all project and application requirements.
3. Read the template at [.req/templates/requirements.md](.req/templates/requirements.md) and apply its guidelines to the requirement draft.
   - Translate template text into the language specified on [User Request](#users-request), if specified.
4. Analyze the [User Request](#users-request) to infer the software’s behavior and main features, then produce a hierarchical requirements list.
   - Requirements for the output:
     - Describe any text-based UI and/or GUI functionality requested.
     - Describe the application's functionalities and configurability requested.
     - Describe any requested unit tests.
     - Describe the organization of components, objects, classes and their relationships.
     - Include the project’s file/folder structure (tree view).
     - Identify any performance improvements or code optimizations requested for the codebase.
   - Scope rules:
     - Exclude from analysis any files and directories matching the pattern .*/** (i.e., any path segment starting with a dot).
5. List requested components and libraries.
6. Check [User Request](#users-request) for unit test requirements. If any test requests are found, analyze them and provide a concise summary of the high-level functional requirements and the business logic being tested.
7. Create a Markdown file with the requirements draft at [%%REQ_PATH%%/requirements_DRAFT.md](%%REQ_PATH%%/requirements_DRAFT.md).
   - Write requirements, section titles, tables, and other content requested language.
   - Follow [.req/templates/requirements.md](.req/templates/requirements.md) translated into requested language.
   - Describe every project requirement clearly, succinctly, and unambiguously.
   - Format the requirements as a bulleted list, using 'shall' or 'must' to indicate mandatory actions. Translate these terms using their closest equivalents in the target language.
9. Present results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence).

<h2 id="users-request">User's Request</h2>
%%ARGS%%
