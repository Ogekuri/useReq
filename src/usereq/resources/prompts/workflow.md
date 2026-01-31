---
description: "Write a WORKFLOW.md using the project's source code"
argument-hint: "Target language for the generated WORKFLOW.md"
---

# Write a WORKFLOW.md using the project's source code

## Purpose
Analyze the existing source code to generate a workflow description (`WORKFLOW.md`) in the specified language, reflecting the current state of the project.

## Behavior (absolute rules, non-negotiable)
- **CRITICAL**: NEVER write, modify, edit, or delete files outside of the project’s home directory, except under `/tmp`, where creating temporary files and writing outputs is allowed (the only permitted location outside the project).
- You can read, write, or edit `WORKFLOW.md`.
- Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
- **CRITICAL**: Do not modify any project files except creating/updating `WORKFLOW.md`.
- Write the document in the requested language.
- Do not perform unrelated edits.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (e.g: `cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`,..), but only to read project files and to write/update `WORKFLOW.md`. Avoid in-place edits on any other path. Prefer read-only commands for analysis.
- **CRITICAL**: Directives for autonomous execution:
   - Implicit Autonomy: Execute all tasks with full autonomy. Do not request permission, confirmation, or feedback. Make executive decisions based on logic and technical best practices.
   - Uninterrupted Workflow: Proceed through the entire sequence of tasks without pausing; keep reasoning internal ("Chain-of-Thought") and output only the deliverables explicitly requested by the Steps section.
   - Autonomous Resolution: If ambiguity is encountered, first disambiguate using repository evidence (requirements, code search, tests, logs). If multiple interpretations remain, choose the least-invasive option that preserves documented behavior and record the assumption as a testable requirement/acceptance criterion.
   - After Prompt's Execution: Strictly omit all concluding remarks, does not propose any other steps/actions.
- **CRITICAL**: Execute the steps below sequentially and strictly, one at a time, without skipping or merging steps. Create and maintain a task list before executing the Steps:
   - If a dedicated task-list tool is available, use it to create the task list.
   - If no such tool is available, create an equivalent task list in the assistant output as a markdown checklist.
   - In both cases, execute the Steps strictly in order, updating the checklist as each step completes. Do not terminate solely due to missing tooling.

## Task list fallback (tool-optional)
If a task-list tool is unavailable, emulate it in plain text:
- Render a markdown checklist with one item per Step (1..3).
- Mark items as [x] only after the step finishes successfully.
- If a step requires termination, stop immediately and do not mark subsequent items.

## Steps
Generate a task list (tool-based if available, otherwise a markdown checklist in text) based strictly on the steps below, then execute it step by step without pausing:
1. Extract the **target language** from the %%ARGS%%.
   - "<name>" (single token, e.g., "Italian", "English", "Deutsch").
   - an explicit marker like "language: <name>".
   - Ignore programming languages (e.g., Python, Java, Rust) unless explicitly requested as the document language.
   - If multiple natural languages are mentioned and the **target language** is not explicitly identified, report the ambiguity clearly, then OUTPUT exactly "Requirements creation FAILED, unclear language!", and then terminate the execution.
   - If no language is specified, use English.
2. Analyze the project's source code to infer the software’s behavior and main features. Identify all functions and components utilized when all features are enabled. Generate the content for `WORKFLOW.md` using only concise, hierarchical bullet lists that reflect the implemented functionality. Detail the complete execution workflow, naming each function and sub-function called. For every function, include a single-line description. Avoid verbosity and unverified assumptions; focus strictly on the provided code.
3. PRINT in the response presenting results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence). The final line of the output must be EXACTLY "Requirements written!".
