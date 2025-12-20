---
description: "Implement a new requirement and make the corresponding source code changes. Usage: req.new <description>."
---

# Implement a new requirement and make the corresponding source code changes

## Purpose
- Produce a clear change proposal and apply the approved changes to the requirements and source code.

## Behavior
 - Propose changes based only on the requirements, user's request and project's source code.
 - Use technical documents to implement features and changes.
 - Preserve the original language of documents, comments, and printed output.
 - Prioritize clean implementation over legacy support. Breaking changes are allowed. Do not add backward compatibility of any kind (no shims, adapters, fallbacks, legacy paths, deprecated formats, or transitional behavior) and do not implement migrations or auto-upgrades.
 - Do not make unrelated edits.
 - Where unit tests exist, strictly adhere to the associated specific instructions.
 - Follow the ordered steps below exactly.

## Steps
Create and execute a TODO list following these steps strictly:
1. Read [%%REQ_DOC%%](%%REQ_DOC%%), all source files, and the [User Request](#users-request).
2. Produce a clear change proposal describing the edits to requirements and to source code needed to implement the feature(s) described by the [User Request](#users-request).
3. Ensure the proposed requirement changes do NOT modify existing requirements but only add new ones. Present the requirements that will be added in [%%REQ_DOC%%](%%REQ_DOC%%).
4. If [%%REQ_DIR%%](%%REQ_DIR%%) exists, read it and ensure the proposed code changes conform to that document; adjust the proposal if needed.
5. Analyze the proposed source code changes and new requirements. Where unit tests exist, refactor and expand them for full coverage. If no unit tests are present, do not create a new testing suite.
6. Wait for approval.
7. Implement the approved changes in the requirements file [%%REQ_DOC%%](%%REQ_DOC%%), following its formatting, language, and the template at [/.req/templates/requirements.md](/.req/templates/requirements.md).
8. Implement the corresponding changes in the source code.
9. Re-read [%%REQ_DOC%%](%%REQ_DOC%%) and verify the project's source code satisfies the listed requirements.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - For every `FAIL`, provide evidence: file path(s), line numbers (when relevant), and a short explanation.
10. If [%%REQ_DIR%%](%%REQ_DIR%%) exists, verify the application's code follows that document and report discrepancies with file paths and concise explanations.
   - Report any discrepancies with file paths and concise explanations.
11. Run all available unit tests and provide a summary of the results, highlighting any failures, but do not modify the existing test suite in any way. At this point, the unit tests must remain exactly as they are.
    - If a valid Python virtual environment exists at `.venv/`, run all Python test scripts using that environment’s Python interpreter. Otherwise, run them using the system Python.
12. Present results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence).

<h2 id="users-request">User's Request</h2>
%%ARGS%%

