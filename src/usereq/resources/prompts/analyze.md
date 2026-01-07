---
description: "Produce an analysis report. Usage: req.analyze <description>."
---

# Produce an analysis report

## Purpose
- Analyze the provided source code and requirements and produce an analysis report only. Do not edit, refactor, or rewrite any code or requirements.
 
## Behavior
 - **CRITICAL**: The [User Request](#users-request) is provided via %%ARGS%% only in the first turn. You MUST save it to `.req/context/active_request.md` immediately in step 1. For all subsequent steps, refer to `.req/context/active_request.md`.
 - Do not modify any files in the project.
 - Only analyze the code and present the results; make no changes.
 - Report facts: for each finding include file paths and, when useful, line numbers or short code excerpts.
 - Where unit tests exist, strictly adhere to the associated specific instructions.
 - Follow the ordered steps below exactly.

## Steps
Write and then execute a TODO list following these steps strictly:
1. **Context Persistence**:
   - Check if the [User Request](#users-request) section contains text (from $ARGUMENTS).
   - If it does, SAVE this content immediately to a new file: `.req/context/current_objective.md`.
   - If the section is empty (subsequent turns), READ the content from `.req/context/current_objective.md` to restore the user intent.
2. Read file/files %%REQ_DOC%%, all source files, and the [User Request](#users-request) analysis request.
3. Produce only an analysis report that answers the [User Request](#users-request). 
4. If directory/directories %%REQ_DIR%% exists, read it and ensure the report complies with its guidance; revise the report if necessary.
5.  Present the analysis report in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence).

<h2 id="users-request">User's Request</h2>
%%ARGS%%
