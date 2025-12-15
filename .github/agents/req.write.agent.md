---
description: "Write a requirement draft from the standard template. Usage: req.write <language>."
---

# Write a requirement's draft based on standard template

## Purpose
- Produce a requirement draft from the standard template using the project's source code.

## Behavior
- Create only the requirements draft and do not modify other project files.
- Ignore/exclude all files in .*/** from the project file analysis.
- Write the draft in the requested language.
- Do not perform unrelated edits.
- Follow the steps below in order.

## Steps
Create and execute a TODO list following these steps strictly:
1. Read the template at [.req/templates/requirements.md](.req/templates/requirements.md) and apply its guidelines to the requirement draft in $ARGUMENTS.
   - Translate template text into $ARGUMENTS when necessary.
2. Read the project's source code to determine software behavior and main features.
   - Ignore/exclude all files in .*/** from the project's source code analysis.
3. List used components and libraries.
4. Create a Markdown file with the requirements draft at [docs/requirements.md_DRAFT.md](docs/requirements.md_DRAFT.md).
   - Write requirements, section titles, tables, and other content in $ARGUMENTS.
   - Follow [.req/templates/requirements.md](.req/templates/requirements.md) translated into $ARGUMENTS.
   - Describe every project requirement clearly, succinctly, and unambiguously.
   - Format the requirements as a bulleted list, utilizing 'shall' or 'must' to indicate mandatory actions. Translate these terms into their closest $ARGUMENTS equivalents.
5. Re-read [docs/requirements.md](docs/requirements.md) and verify the project's source code satisfies the listed requirements.
   - For each requirement, report `OK` if satisfied or `FAIL` if not.
   - For every `FAIL`, provide evidence: file path(s), line numbers (when relevant), and a short explanation.
6. Present results in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence).
