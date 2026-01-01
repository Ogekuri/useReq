---
description: "Produce an analysis report. Usage: req.analyze <description>."
---

# Produce an analysis report

## Purpose
- Analyze the provided source code and requirements and produce an analysis report only. Do not edit, refactor, or rewrite any code or requirements.
 
## Behavior
 - Do not modify any files in the project.
 - Only analyze the code and present the results; make no changes.
 - Report facts: for each finding include file paths and, when useful, line numbers or short code excerpts.
 - Where unit tests exist, strictly adhere to the associated specific instructions.
 - Follow the ordered steps below exactly.

## Steps
Create and execute a TODO list following these steps strictly:
1. Read file/files %%REQ_DOC%%, all source files, and the [User Request](#users-request) analysis request.
2. Produce only an analysis report that answers the [User Request](#users-request). 
3. If directory/directories %%REQ_DIR%% exists, read it and ensure the report complies with its guidance; revise the report if necessary.
4.  Present the analysis report in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence).
