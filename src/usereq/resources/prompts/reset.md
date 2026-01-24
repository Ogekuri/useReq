---
description: "Reset useReq/req bootstrap context"
argument-hint: "req.reset"
---

# Reset useReq/req bootstrap context

## Purpose
- Reset useReq/req bootstrap context.

## Behavior
 - Even in read-only mode, you can always read, write, or edit files in `.req/context/`. Files in `.req/context/` are assumed to be untracked/ignored.
 - Use filesystem/shell tools to read/write/delete files as needed (e.g: `cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`,..). Use the minimum set of commands needed to delete the listed files.
 - Follow the ordered steps below exactly.

## Steps
Create a TODO list (use the todo tool if available; otherwise include it in the response) with below steps, then execute them strictly:
1. **CRITICAL**: DELETE the following files if they exist (do not error if missing)
   - `.req/context/active_request.md`
   - `.req/context/state.md`
   - `.req/context/pending_proposal.md`
   - `.req/context/approved_proposal.md`
2. After completing the deletions, OUTPUT exactly "Reset done!" as the FINAL line. The FINAL line MUST be plain text (no markdown/code block) and MUST have no trailing spaces. Terminate response immediately after task completion suppressing all conversational closings (does not propose any other steps/actions, ensure strictly no other text, conversational filler, or formatting follows FINAL line).
