---
description: "Run the requirements check"
argument-hint: "No arguments utilized by the prompt logic"
---

# Run the requirements check

## Purpose
Verify that the project's source code satisfies the documented requirements and pass the test suite, reporting the status of each requirement without modifying any files.


## Professional Personas
- **Act as a Senior System Engineer** when analyzing source code and directory structures to understand the system's architecture and logic.
- **Act as a Business Analyst** when cross-referencing code findings with `%%DOC_PATH%%/REQUIREMENTS.md` to ensure functional alignment.
- **Act as a Technical Writer** when producing the final analysis report or workflow descriptions, ensuring clarity, technical precision, and structured formatting.
- **Act as a QA Auditor** when reporting facts, requiring concrete evidence (file paths, line numbers) for every finding.


## Absolute Rules, Non-Negotiable
- **CRITICAL**: NEVER write, modify, edit, or delete files outside of the project’s home directory, except under `/tmp`, where creating temporary files and writing outputs is allowed (the only permitted location outside the project).
- You MUST read `%%DOC_PATH%%/REQUIREMENTS.md`, but you MUST NOT modify it in this workflow.
- Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`,`.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
- **CRITICAL**: Do not modify any git tracked files (i.e., returned by `git ls-files`). You may run commands that create untracked artifacts ONLY if: (a) they are confined to standard disposable locations (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`,`node_modules/.cache`, `/tmp`), (b) they do not change any tracked file contents, and (c) you do NOT rely on those artifacts as permanent outputs. If unsure, run tools in a temporary directory (e.g., `tmp/`, `temp/`, `/tmp`) or use tool flags that disable caches.
- Allowed git commands in this workflow (read-only only): `git status`, `git diff`, `git ls-files`, `git grep`, `git rev-parse`. Do NOT run any other git commands.

## Behavior
- Only analyze the code and test execution and present the results; make no changes.
- Do NOT create or modify tests in this workflow.
- Report facts: for each finding include file paths and, when useful, line numbers or short code excerpts.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`,`PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read files as needed (read-only only; e.g., `cat`, `sed -n`, `head`, `tail`, `rg`, `less`).


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
   - After Prompt's Execution: Strictly omit all concluding remarks and do not propose any other steps/actions.
- **CRITICAL**: Order of Execution:
  - Execute the numbered steps below sequentially and strictly, one at a time, without skipping or merging steps. Create and maintain a *check-list* internally during executing the Steps. Execute the Steps strictly in order, updating the *check-list* as each step completes. 
- **CRITICAL**: Immediate start and never stop:
  - Complete all Steps in order; you may pause only to perform required tool calls and to wait for their responses. Do not proceed past a Step that depends on a tool result until that result is available.
  - Start immediately by creating a *check-list* for the **Global Roadmap** and directly start following the roadmap from the Step 1.


## Steps
Create internally a *check-list* for the **Global Roadmap** including all below numbered steps: `1..3`, and start following the roadmap at the same time, with the instruction of the Step 1 (Run the test suite). Do not stop generating until the tool is invoked. Do not add additional intent adjustments check, except if it's explicit indicated on steps.
1. **CRITICAL**: Check `%%DOC_PATH%%/REQUIREMENTS.md`, `%%DOC_PATH%%/WORKFLOW.md` and `%%DOC_PATH%%/REFERENCES.md` files presence
   - If the `%%DOC_PATH%%/REQUIREMENTS.md` file does NOT exist, OUTPUT exactly "ERROR: File %%DOC_PATH%%/REQUIREMENTS.md not exist, generate it with /req.write prompt!", and then terminate the execution.
   - If the `%%DOC_PATH%%/WORKFLOW.md` file does NOT exist, OUTPUT exactly "ERROR: File %%DOC_PATH%%/WORKFLOW.md not exist, generate it with /req.workflow prompt!", and then terminate the execution.
   - If the `%%DOC_PATH%%/REFERENCES.md` file does NOT exist, OUTPUT exactly "ERROR: File %%DOC_PATH%%/WORKFLOW.md not exist, generate it with /req.references prompt!", and then terminate the execution.
2. Run test suite, check requirements coverage and generate **Comprehensive Technical Implementation Report**
   - Run the test suite to verify the current state. Do not modify the source code or tests. Record the test results (`OK`/`FAIL`) to be used as evidence for the final analysis report. If tests fail, continue to Step 2.
   - Read `%%DOC_PATH%%/REQUIREMENTS.md` and cross-reference with the source code from %%SRC_PATHS%%, %%TEST_PATH%% to check ALL requirements, but use progressive disclosure: provide full evidence only for `FAIL` items and a compact pointer-only index for `OK` items. For each requirement, use tools (e.g., `git grep`, `find`, `ls`) to locate the relevant source code files used as evidence, read only the identified files to verify compliance and do not assume compliance without locating the specific code implementation.
      - For each requirement, report `OK` if satisfied or `FAIL` if not.
      - Do not mark a requirement as `OK` without code evidence; for `OK` items provide only a compact pointer (file path + symbol + line range). For each requirement, provide a concise evidence pointer (file path + symbol + line range) excerpts only for `FAIL` requirements or when requirement is architectural, structural, or negative (e.g., "shall not..."). For such high-level requirements, cite the specific file paths or directory structures that prove compliance. Line ranges MUST be obtained from tooling output (e.g., `nl -ba` / `sed -n`) and MUST NOT be estimated. If evidence is missing, you MUST report `FAIL`. Do not assume implicit behavior.
      - For every `FAIL`, provide evidence with a short explanation. Provide file path(s) and line numbers where possible.
   - **CRITICAL**: If all requirements report `OK`, OUTPUT exactly "All requirements are already covered. No changes needed.", and then terminate the execution.
   - If there are uncovered requirements, using uncovered requirements from `%%DOC_PATH%%/REQUIREMENTS.md` and [User Request](#users-request) as a semantic guides, extract all information from `%%DOC_PATH%%/WORKFLOW.md` that is directly or even tangentially related, prioritizing high recall to capture every relevant nuance and borderline connection, to identify the most likely related files and functions based on explicit evidence, and treat any uncertain links as candidates without claiming completeness, then analyze the involved source code from %%SRC_PATHS%% and GENERATE a detailed **Comprehensive Technical Implementation Report** documenting the exact modifications to the source code that will cover all `FAIL` requirements. The **Comprehensive Technical Implementation Report** MUST be implementation-only and patch-oriented: for each file, list exact edits (functions/classes touched), include only changed snippets, and map each change to the requirement ID(s) it satisfies (no narrative summary)
      - Read %%GUIDELINES_FILES%% files and apply those **guidelines**; ensure the proposed code changes conform to those **guidelines**, and adjust the **Comprehensive Technical Implementation Report** if needed. Do not apply unrelated **guidelines**.
   - From %%TEST_PATH%%, locate and read only the unit tests that are relevant to the affected requirement IDs and touched modules (via targeted search), and plan the necessary refactoring/additions
 to cover uncovered requirements and include these details in the **Comprehensive Technical Implementation Report**.
      - Read %%GUIDELINES_FILES%% files and apply those **guidelines**; ensure the proposed code changes conform to those **guidelines**, and adjust the **Comprehensive Technical Implementation Report** if needed. Do not apply unrelated **guidelines**.
3. Present results and **Comprehensive Technical Implementation Report**
   - PRINT in the response presenting the results of requirements check and **Comprehensive Technical Implementation Report** in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence). The final line of the output must be EXACTLY "Check completed!".
