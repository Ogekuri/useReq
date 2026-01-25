---
description: "Produce a requirement draft based on the User Request description"
argument-hint: "Description of the requirements to be drafted (from scratch)"
---

# Produce a requirement draft based on the User Request description

## Purpose
Draft a new requirements document (`requirements_DRAFT.md`) based entirely on the user's description and specifications, without referencing existing source code.

## Behavior (absolute rules, non-negotiable)
- **CRITICAL**: NEVER write, modify, edit, delete file outside of project's home directory.
- You can read, write, or edit `%%REQ_PATH%%/requirements_DRAFT.md`.
- Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
- **CRITICAL**: Do not modify any project files except creating/updating `%%REQ_PATH%%/requirements_DRAFT.md`.
- Do not perform unrelated edits.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (e.g: `cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`,..), but only to read project files and to write/update `%%REQ_PATH%%/requirements_DRAFT.md`. Avoid in-place edits on any other path. Prefer read-only commands for analysis.
- Directives for autonomous execution:
   - Implicit Autonomy: Execute all tasks with full autonomy. Do not request permission, confirmation, or feedback. Make executive decisions based on logic and technical best practices.
   - Uninterrupted Workflow: Proceed through the entire sequence of tasks without pausing. Perform internal "Chain-of-Thought" reasoning, but output only the final results (PRINT Step).
   - Autonomous Resolution: If an ambiguity or constraint is encountered, resolve it using the most efficient and logical path. Do not halt for user input unless a fatal execution error occurs (expressly indicated in the steps).
   - Zero-Latency Output: Strictly omit all conversational fillers, introductions, and concluding remarks. Start immediately with the task output.
- Follow the ordered steps below exactly. STOP instruction means: terminate response immediately after task completion (e.g., PRINT, OUTPUT,..) of current step, suppressing all conversational closings (does not propose any other steps/actions, ensure strictly no other text, conversational filler, do not run any further commands, do not modify any additional files).

## Steps
Generate a task list based strictly on the steps below. Utilize the TODO LIST tool if supported; if not, list them in your response. Execute each step sequentially and strictly:
1. Read [User Request](#users-request) to identify and extract all project and application requirements.
2. Extract the target language from the [User Request](#users-request).
   - Prefer an explicit marker like "language: <name>".
   - Ignore programming languages (e.g., Python, Java, Rust) unless explicitly requested as the document language.
   - If multiple natural languages are mentioned and the target language is not explicitly identified, report the ambiguity clearly, then OUTPUT exactly "Requirements creation FAILED!"  as the FINAL line, and STOP.
   - If no language is specified, use English.
3. Read the template at `.req/templates/requirements.md` and apply its guidelines to the requirement draft. If the target language is not English, you MUST translate all template section headers and structural text into the target language.
4. Analyze the [User Request](#users-request) to infer the software’s behavior and main features, then produce a hierarchical requirements list.
   - Requirements for the output:
      - Describe any text-based UI and/or GUI functionality requested.
      - Describe the application's functionalities and configurability requested.
      - Describe any requested unit tests.
      - Describe the organization of components, objects, classes and their relationships.
      - Propose a logical file/folder structure for the project as a ascii tree view based on the requirements.
      - Identify any performance constraints or efficiency goals explicitly mentioned in the User Request.
5. List requested components and libraries.
6. Check [User Request](#users-request) for unit test requirements. If any test requests are found, analyze them and provide a concise summary of the high-level functional requirements and the business logic being tested.
7. Create a Markdown file with the requirements draft at `%%REQ_PATH%%/requirements_DRAFT.md`.
   - Write requirements, section titles, tables, and other content in target language.
   - Follow `.req/templates/requirements.md` translated into requested language.
   - Describe every project requirement clearly, succinctly, and unambiguously.
   - Format the requirements as a bulleted list, using 'shall' or 'must' to indicate mandatory actions. Translate these terms using their closest equivalents in the target language.
8. PRINT in the response presenting the requirements draft in a clear, structured format. Since this workflow is based only on the User Request (no source code), do NOT claim code-level evidence (no file paths/line numbers) unless explicitly provided by the user.
9. OUTPUT exactly "Requirements written!" as the FINAL line, and STOP.

<h2 id="users-request">User's Request</h2>
%%ARGS%%
