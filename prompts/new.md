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
 - Do not make unrelated edits.
 - Follow the ordered steps below exactly.

## Steps (follow exactly)
1. Read [%%REQ_DOC%%](%%REQ_DOC%%), all source files, and the [User Request](#users-request).
2. Produce a clear change proposal describing the edits to requirements and to source code needed to implement the feature(s) described by the [User Request](#users-request).
3. Ensure the proposed requirement changes do NOT modify existing requirements but only add new ones. Present the requirements that will be added in [%%REQ_DOC%%](%%REQ_DOC%%).
4. If [%%REQ_DIR%%](%%REQ_DIR%%) exists, read it and ensure the proposed code changes conform to that document; adjust the proposal if needed.
5. Implement the approved changes in the requirements file [%%REQ_DOC%%](%%REQ_DOC%%), following its formatting, language, and the template at [/.req/templates/requirements.md](/.req/templates/requirements.md).
6. Implement the corresponding changes in the source code.
7. Re-read [%%REQ_DOC%%](%%REQ_DOC%%) and verify the project's source code satisfies the listed requirements.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - For every `FAIL`, provide evidence: file path(s), line numbers (when relevant), and a short explanation.
8. If [%%REQ_DIR%%](%%REQ_DIR%%) exists, verify the application's code follows that document and report discrepancies with file paths and concise explanations.
   - Report any discrepancies with file paths and concise explanations.
9. Present results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence).

<h2 id="users-request">User's Request</h2>

```text
%%ARGS%%
```
