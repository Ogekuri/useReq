---
description: "Run the requirements check. Usage: req.check."
---

# Run the requirements check

## Purpose
- Perform the requirements check and report whether all items are correctly covered without making any changes.
 
## Behavior
 - Do not modify any files in the project.
 - Only analyze the code and present the results; make no changes.
 - Report facts: for each finding include file paths and, when useful, line numbers or short code excerpts.
 - Where unit tests exist, strictly adhere to the associated specific instructions.
 - Follow the ordered steps below exactly.

## Steps
Create and execute a TODO list following these steps strictly:
1. Read file/files %%REQ_DOC%% and verify that the project's source code satisfies the requirements listed there.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - For every `FAIL`, provide evidence: file path(s), line numbers (when relevant), and a short explanation.
2. If directory/directories %%REQ_DIR%% exists, read it and verify that the application's code follows that documentations.
   - Report any discrepancies with file paths and concise explanations.
3. Run all available unit tests and provide a summary of the results, highlighting any failures, but do not modify the existing test suite in any way. The unit tests must remain exactly as they are.
   - If a valid Python virtual environment exists at `.venv/`, run all Python test scripts using its Python interpreter; otherwise use the system Python. Before running tests, set `PYTHONPATH` to the directory that contains the modules to import.
4. Present results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence).
