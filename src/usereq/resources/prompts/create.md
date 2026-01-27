---
description: "Write a Software Requirements Specification draft using the project's source code"
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
2. Read the template at `.req/templates/requirements.md` and apply its guidelines to the requirement draft. If the **target language** is not English, you MUST translate all template section headers and structural text into the **target language**.
3. Analyze the project's source code to infer the software’s behavior and main features, then produce a hierarchical requirements list.
   - Requirements for the output:
      - Describe any text-based UI and/or GUI functionality implemented.
      - Describe the application's functionalities and configurability implemented.
      - Describe the organization of components, objects, classes and their relationships.
      - Include the project’s file/folder structure (tree view) with a sensible depth limit (e.g., max depth 4) and exclude large/generated directories (e.g., `node_modules/`, `dist/`, `build/`, `target/`, `.venv/`, `.git/`).
      - Only report performance optimizations if there is explicit evidence (e.g., comments, benchmarks, complexity-relevant changes, profiling notes, or clearly optimized code patterns). Otherwise, state ‘No explicit performance optimizations identified’.
4. List used components and libraries.
5. Locate and read the unit tests (do not execute them unless explicitly required). Summarize what they test and how. Analyze them and provide a concise summary of the high-level functional requirements and business logic being tested.
6. Create the **Software Requirements Specification** document with the requirements draft at `%%REQ_PATH%%/requirements_DRAFT.md`.
   - Write requirements, section titles, tables, and other content in **target language**.
   - Follow `.req/templates/requirements.md` translated into **target language**.
   - Describe every project requirement clearly, succinctly, and unambiguously.
   - Format the requirements as a bulleted list, utilizing 'shall' or 'must' to indicate mandatory actions. Translate 'shall'/'must' into their closest equivalents in the **target language**.
   - Output the entire response in clean, properly formatted Markdown.
7. Re-read `%%REQ_PATH%%/requirements_DRAFT.md` and cross-reference with the source code.
   - Verify that the drafted requirements **accurately reflect the actual code behavior** (True State).
   - If the code contains obvious bugs or partial implementations, ensure the requirement draft explicitly notes these limitations.
   - Report `OK` if the draft accurately describes the code (even if the code is buggy). Report `FAIL` only if the draft makes assertions that are not present or contradicted by the source code.
8. PRINT in the response presenting results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence).
9. OUTPUT exactly "Requirements written!".
