---
description: "Produce a requirement draft based on the User Request description"
argument-hint: "req.write <description>"
---

# Produce a requirement draft based on the User Request description

## Purpose
- Produce a requirement draft from the standard template based on the User Request.

## Behavior
- Even in read-only mode, you can always read, write, or edit files in `.req/context/`. Files in `.req/context/` are assumed to be untracked/ignored. 
- You can read, write, or edit `%%REQ_PATH%%/requirements_DRAFT.md`.
- Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
- **CRITICAL**: Do not modify any project files except creating/updating `%%REQ_PATH%%/requirements_DRAFT.md` and files in `.req/context/`.
- Do not perform unrelated edits.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (e.g: `cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`,..), but only to read project files and to write/update `%%REQ_PATH%%/requirements_DRAFT.md` and files under `.req/context/`. Avoid in-place edits on any other path. Prefer read-only commands for analysis.
- Follow the steps below in order.

## Steps
Create a TODO list (use the todo tool if available; otherwise include it in the response) with below steps, then execute them strictly:
1. Read [User Request](#users-request) to identify and extract all project and application requirements.
2. Extract the target language from the [User Request](#users-request).
   - Prefer an explicit marker like "language: <name>".
   - Ignore programming languages (e.g., Python, Java, Rust) unless explicitly requested as the document language.
   - If multiple languages are mentioned or it is ambiguous, ask the user to specify exactly one target language, DELETE `.req/context/active_request.md`, `.req/context/state.md`, `.req/context/pending_proposal.md`, `.req/context/approved_proposal.md` (if present) and STOP.
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
8. Present the requirements draft in a clear, structured format. Since this workflow is based only on the User Request (no source code), do NOT claim code-level evidence (no file paths/line numbers) unless explicitly provided by the user.
9. After the full report, OUTPUT exactly "Requirements written!" as the FINAL line. The FINAL line MUST be plain text (no markdown/code block) and MUST have no trailing spaces. Terminate response immediately after task completion suppressing all conversational closings (does not propose any other steps/actions, ensure strictly no other text, conversational filler, or formatting follows FINAL line).

<h2 id="users-request">User's Request</h2>
%%ARGS%%
