---
description: "Perform an optimizazion without changing the requirements. Usage: req.optimize <description>."
---

# Perform an optimizazion without changing the requirements

## Purpose
- Produce a clear optimization proposal and apply the approved changes to the source code.

## Behavior
 - Do not modify files that contain requirements.
 - Always strictly respect requirements.
 - Use technical documents to implement features and changes.
 - Preserve the original language of documents, comments, and printed output.
 - Prioritize backward compatibility. Do not introduce breaking changes; preserve existing interfaces, data formats, and features. Do not implement migrations, auto-upgrades or any conversion logic.
 - Do not make unrelated edits.
 - Where unit tests exist, strictly adhere to the associated specific instructions.
 - Follow the ordered steps below exactly.

## Steps
Create and execute a TODO list following these steps strictly:
1. If %%ARGS%% does not contain a clear request, stop execution and return an error.
2. Read [%%REQ_DOC%%](%%REQ_DOC%%), all source files, and the [User Request](#users-request).
3. Produce a clear change proposal describing edits to the source code that implement the optimization described by the [User Request](#users-request).
4. Ensure the proposed source code changes do NOT modify existing requirements.
5. Read [%%REQ_DOC%%](%%REQ_DOC%%) and confirm that no changes are needed in [%%REQ_DOC%%](%%REQ_DOC%%).
6. If [%%REQ_DIR%%](%%REQ_DIR%%) exists, read it and ensure the proposed code changes conform to that document; adjust the proposal if needed.
7. Analyze the proposed source code changes and original requirements. Where unit tests exist, refactor and expand them for full coverage. If no unit tests are present, do not create a new testing suite.
8. Wait for approval.
9. Implement the corresponding changes in the source code.
10. Re-read [%%REQ_DOC%%](%%REQ_DOC%%) and verify the project's source code satisfies the listed requirements.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - For every `FAIL`, provide evidence: file path(s), line numbers (when relevant), and a short explanation.
11. If [%%REQ_DIR%%](%%REQ_DIR%%) exists, verify the application's code follows that document and report discrepancies with file paths and concise explanations.
   - Report any discrepancies with file paths and concise explanations.
12. Run all available unit tests and provide a summary of the results, highlighting any failures, but do not modify the existing test suite in any way. At this point, the unit tests must remain exactly as they are.
    - If a valid Python virtual environment exists at `.venv/`, run all Python test scripts using its Python interpreter; otherwise use the system Python. Before running tests, set `PYTHONPATH` to the directory that contains the modules to import.
13. Present results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence).

<h2 id="users-request">User's Request</h2>
%%ARGS%%

