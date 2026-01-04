---
description: "Implement changes needed to cover the new requirements. Usage: req.cover."
---

# Implement changes needed to cover the new requirements

## Purpose
- Perform the requirements check and report whether all items are correctly covered, then propose a source code change to cover all uncovered requirements.
 
## Behavior
 - Do not modify files that contain requirements.
 - Always strictly respect requirements.
 - Use technical documents to implement features and changes.
 - Preserve the original language of documents, comments, and printed output.
 - Prioritize clean implementation over legacy support. Breaking changes are allowed. Do not add backward compatibility of any kind (no shims, adapters, fallbacks, legacy paths, deprecated formats, or transitional behavior) and do not implement migrations or auto-upgrades.
 - Do not make unrelated edits.
 - Where unit tests exist, strictly adhere to the associated specific instructions.
 - Follow the ordered steps below exactly.

## Steps
Write and then execute a TODO list following these steps strictly:
1. Read file/files %%REQ_DOC%% and verify that the project's source code satisfies the requirements listed there.
   - For each requirement, report `OK` if satisfied or `UNCOVERED` if not.
   - For every `UNCOVERED`, provide evidence: file path(s), line numbers (when relevant), and a short explanation.
2. Produce a clear change proposal describing edits to the source code that will cover all `UNCOVERED` requirements.
3. Re-read %%REQ_DOC%% and confirm that no changes are needed in %%REQ_DOC%%.
4. If directory/directories %%REQ_DIR%% exists, read it and ensure the proposed code changes conform to that documents; adjust the proposal if needed.
5. Analyze the proposed source code changes and new requirements. Where unit tests exist, refactor and expand them for full coverage. If no unit tests are present, do not create a new testing suite.
6. Wait for approval.
7. Implement the corresponding changes in the source code.
8. Re-read file/files %%REQ_DOC%% and verify the project's source code satisfies the listed requirements.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - For every `FAIL`, provide evidence: file path(s), line numbers (when relevant), and a short explanation.
9. If directory/directories %%REQ_DIR%% exists, verify the application's code follows that documents and report discrepancies with file paths and concise explanations.
   - Report any discrepancies with file paths and concise explanations.
10. Run all available unit tests and provide a summary of the results, highlighting any failures, but do not modify the existing test suite in any way. At this point, the unit tests must remain exactly as they are.
    - If a valid Python virtual environment exists at `.venv/`, run all Python test scripts using its Python interpreter; otherwise use the system Python. Before running tests, set `PYTHONPATH` to the directory that contains the modules to import.
11. Present results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence).
