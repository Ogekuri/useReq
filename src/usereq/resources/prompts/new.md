---
description: "Implement a new requirement and make the corresponding source code changes. Usage: req.new <description>."
---

# Implement a new requirement and make the corresponding source code changes

## Purpose
- Produce a clear change proposal and apply the approved changes to the requirements and source code.

## Behavior
 - **CRITICAL**: The User Request is provided via %%ARGS%% only in the first turn. You MUST save it to `.req/context/active_request.md` immediately in step 1. For all subsequent steps, refer to `.req/context/active_request.md`.
 - Propose changes based only on the requirements, user's request and project's source code.
 - Use technical documents to implement features and changes.
 - Preserve the original language of documents, comments, and printed output.
 - Prioritize clean implementation over legacy support. Breaking changes are allowed. Do not add backward compatibility of any kind (no shims, adapters, fallbacks, legacy paths, deprecated formats, or transitional behavior) and do not implement migrations or auto-upgrades.
 - Do not make unrelated edits.
 - Where unit tests exist, strictly adhere to the associated specific instructions.
 - Follow the ordered steps below exactly.

## Steps
Write and then execute a TODO list following these steps strictly:
1. **Context Persistence**:
   - Check if the [User Request](#users-request) section contains text (from $ARGUMENTS).
   - If it does, SAVE this content immediately to a new file: `.req/context/current_objective.md`.
   - If the section is empty (subsequent turns), READ the content from `.req/context/current_objective.md` to restore the user intent.
2. Read file/files %%REQ_DOC%%, all source files, and the [User Request](#users-request).
3. Produce a clear change proposal describing the edits to requirements and to source code needed to implement the feature(s) described by the [User Request](#users-request).
4. Ensure the proposed requirement changes do NOT modify existing requirements but only add new ones. Present the requirements that will be added in %%REQ_DOC%%.
5. If directory/directories %%REQ_DIR%% exists, read it and ensure the proposed code changes conform to that documents; adjust the proposal if needed.
6. Analyze the proposed source code changes and new requirements. Where unit tests exist, refactor and expand them for full coverage. If no unit tests are present, do not create a new testing suite.
7. Wait for approval.
8. Implement the approved changes in the requirements file %%REQ_DOC%%, following its formatting, language, and the template at [/.req/templates/requirements.md](/.req/templates/requirements.md).
9. Implement the corresponding changes in the source code.
10. Re-read file/files %%REQ_DOC%% and verify the project's source code satisfies the listed requirements.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - For every `FAIL`, provide evidence: file path(s), line numbers (when relevant), and a short explanation.
11. If directory/directories %%REQ_DIR%% exists, verify the application's code follows that documents and report discrepancies with file paths and concise explanations.
   - Report any discrepancies with file paths and concise explanations.
12. Run all available unit tests and provide a summary of the results, highlighting any failures, but do not modify the existing test suite in any way. At this point, the unit tests must remain exactly as they are.
    - If a valid Python virtual environment exists at `.venv/`, run all Python test scripts using its Python interpreter; otherwise use the system Python. Before running tests, set `PYTHONPATH` to the directory that contains the modules to import.
13. Present results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence).

<h2 id="users-request">User's Request</h2>
%%ARGS%%

