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
 - Run unit tests.
 - Follow the ordered steps below exactly.

## Steps
Create and execute a TODO list following these steps strictly:
1. Read the file [docs/requirements.md](docs/requirements.md) and verify that the project's source code satisfies the requirements listed there.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - For every `FAIL`, provide evidence: file path(s), line numbers (when relevant), and a short explanation.
2. If the technical document [tech/](tech/) exists, read it and verify that the application's code follows that documentation.
   - Report any discrepancies with file paths and concise explanations.
3. Present results in a clear, structured way so an analytical system can process them without inferring intent.
