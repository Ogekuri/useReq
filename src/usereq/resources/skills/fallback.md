---
description: "Fallback router (no matching skill)"
argument-hint: "The user's request (free-form)"
usage: >
  Select this prompt only when none of the other SKILLs clearly apply. Use it to stop execution, tell the user the request is ambiguous/underspecified for SRS-driven workflows, and provide a compact menu of the available skills with guidance and example phrasings so the user can re-run their request using the correct workflow.
---

# Fallback router (no matching skill)

## Purpose
Route ambiguous or underspecified user requests to the correct SRS-driven workflow by presenting the available skills and how to invoke them.

## Scope
In scope: produce a short clarification message and a skill-selection menu. Out of scope: reading repository files, running commands, generating patches, modifying requirements, implementing code/tests, or updating docs.

## Absolute Rules, Non-Negotiable
- Do NOT run any tool calls or shell commands.
- Do NOT read or reference any repository files.
- Do NOT propose a plan or start any implementation work.
- After outputting the message in **Steps**, terminate the execution immediately.

## Steps
1. Output a single response that:
   - States that the request is unclear/ambiguous for the SRS-driven workflows.
   - Asks the user to choose exactly one of the workflows below and re-run the request using it.
   - Provides the following routing menu (keep it compact; include 1 example per workflow):
     - `analyze`: read-only investigation/triage with evidence pointers.
     - `check`: read-only compliance audit with OK/FAIL for every requirement ID.
     - `write`: draft `%%DOC_PATH%%/REQUIREMENTS.md` from the request text only (no code changes).
     - `create`: (re)build `%%DOC_PATH%%/REQUIREMENTS.md` from existing code evidence only (no code changes).
     - `recreate`: rewrite/clean SRS structure based on code evidence, preserving existing requirement IDs (no code changes).
     - `renumber`: renumber requirement IDs deterministically without changing requirement text/order (no code changes).
     - `new`: strictly additive, backwards-compatible feature (append new requirement IDs, then implement + verify).
     - `change`: modify existing requirement IDs/behavior (edit/replace/remove existing IDs, then implement + verify).
     - `fix`: defect fix to restore compliance without changing the SRS.
     - `refactor`: internal restructuring/performance improvements with no behavior change (SRS unchanged).
     - `cover`: implement minimal deltas to satisfy already-known uncovered requirement IDs (SRS unchanged).
     - `implement`: build missing functionality end-to-end from an authoritative SRS (SRS unchanged).
     - `workflow`: regenerate only `%%DOC_PATH%%/WORKFLOW.md` from source evidence.
     - `references`: regenerate only `%%DOC_PATH%%/REFERENCES.md` from source evidence.
   - Mentions that placeholders (%%ARGS%%, %%DOC_PATH%%, %%GUIDELINES_FILES%%, %%SRC_PATHS%%, %%TEST_PATH%%) are auto-substituted by the installer and must not be edited by the user.
2. Terminate immediately after the response. Do not do anything else.

<h2 id="users-request">User's Request</h2>
%%ARGS%%

