---
description: "Produce an analysis report. Usage: req.analyze <description>."
---

# Produce an analysis report

## Purpose
- Analyze the provided source code and requirements and produce an analysis report only. Do not edit, refactor, or rewrite any code or requirements.
 
## Behavior
 - **CRITICAL**: The [User Request](#users-request) is provided via `$ARGUMENTS` only in the first turn. You MUST persist it in step 1 to `.req/context/active_request.md`.
 - **CRITICAL**: After step 1, you MUST treat `.req/context/active_request.md` as the single source of truth for the user request. Do NOT rely on `$ARGUMENTS` again.
 - Do not modify any files in the project.
 - Only analyze the code and present the results; make no changes.
 - Report facts: for each finding include file paths and, when useful, line numbers or short code excerpts.
 - Where unit tests exist, strictly adhere to the associated specific instructions.
 - Follow the ordered steps below exactly.

## Steps
Write and then execute a TODO list following these steps strictly:
1. **Context Bootstrap & Persistence (MUST RUN FIRST, EVERY INVOCATION)**:
   - Ensure the directory `.req/context/` exists.
   - If the [User Request](#users-request) section contains non-empty text (from `$ARGUMENTS`):
     - SAVE it immediately to `.req/context/active_request.md` (overwrite existing content).
   - Otherwise (subsequent turns / reinvocations with empty `$ARGUMENTS`):
     - READ `.req/context/active_request.md` and use it as the restored user request.
   - If `$ARGUMENTS` is empty AND `.req/context/active_request.md` does not exist or is empty:
     - STOP immediately and respond asking for the user request to be provided again via `req.analyze <description>`.
   - From this point onward, refer only to `.req/context/active_request.md` for the user request.
2. Read file/files %%REQ_DOC%%, all source files, and the [User Request](#users-request) analysis request.
3. Produce only an analysis report that answers the [User Request](#users-request). 
4. If directory/directories %%REQ_DIR%% exists, read it and ensure the report complies with its guidance; revise the report if necessary.
5.  Present the analysis report in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence).

<h2 id="users-request">User's Request</h2>
%%ARGS%%
