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
1. If %%ARGS%% does not contain a language identifier (e.g., "language: <name>" or "<name>"), stop execution and return an error.
2. Read the template at [.req/templates/requirements.md](.req/templates/requirements.md) and apply its guidelines to the requirement draft in %%ARGS%%.
   - Translate template text into %%ARGS%% when necessary.
3. Analyze the project's source code to infer the software’s behavior and main features, then produce a hierarchical requirements list.
   - Requirements for the output:
     - Describe any text-based UI and/or GUI functionality implemented.
     - Describe the application's functionalities and configurability implemented.
     - Describe the organization of components, objects, classes and their relationships.
     - Include the project’s file/folder structure (tree view).
     - Identify any in-place performance improvements or code optimizations present in the codebase.
   - Scope rules:
     - Exclude from analysis any files and directories matching the pattern .*/** (i.e., any path segment starting with a dot).
4. List used components and libraries.
5. Check the unit test suite. If tests are found, analyze them and provide a concise summary of the high-level functional requirements and business logic being tested.
6. Create a Markdown file with the requirements draft at [%%REQ_PATH%%/requirements_DRAFT.md](%%REQ_PATH%%/requirements_DRAFT.md).
   - Write requirements, section titles, tables, and other content in %%ARGS%%.
   - Follow [.req/templates/requirements.md](.req/templates/requirements.md) translated into %%ARGS%%.
   - Describe every project requirement clearly, succinctly, and unambiguously.
   - Format the requirements as a bulleted list, utilizing 'shall' or 'must' to indicate mandatory actions. Translate these terms into their closest %%ARGS%% equivalents.
7. Re-read file/files %%REQ_DOC%% and verify the project's source code satisfies the listed requirements.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - For every `FAIL`, provide evidence: file path(s), line numbers (when relevant), and a short explanation.
8. Present results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence).
