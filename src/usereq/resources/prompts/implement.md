---
description: "Implement source code from scratch from requirements"
argument-hint: "No arguments utilized by the prompt logic"
---

# Implement source code from scratch from requirements

## Purpose
Produce a working implementation from the normative SRS (`%%DOC_PATH%%/REQUIREMENTS.md`) by building missing functionality end-to-end (including “from scratch” where needed), so the codebase becomes fully compliant with the documented requirement IDs without changing those requirements.

## Scope
In scope: read `%%DOC_PATH%%/REQUIREMENTS.md`, implement/introduce source under %%SRC_PATHS%% (including new modules/files), add tests under %%TEST_PATH%%, verify via the test suite, update `%%DOC_PATH%%/WORKFLOW.md` and `%%DOC_PATH%%/REFERENCES.md`, and commit. Out of scope: editing requirements or introducing features not present in the SRS (use `/req.change` or `/req.new` to evolve requirements first).

## Usage
Use this prompt when the SRS is already authoritative and stable, but the codebase is missing large parts of the required implementation (greenfield or major gaps), and you must build functionality end-to-end without changing requirements. If only a small, known set of requirement IDs is uncovered in an otherwise working codebase, use `/req.cover` instead.

## WORKFLOW.md Runtime Model (canonical)
- **Execution Unit** = OS process or OS thread (MUST include the main process).
- **Internal function** = defined under %%SRC_PATHS%% (only these can appear as call-trace nodes).
- **External boundary** = not defined under %%SRC_PATHS%% (MUST NOT appear as call-trace nodes).
- `%%DOC_PATH%%/WORKFLOW.md` MUST always be written and maintained in English and MUST preserve the schema: `Execution Units Index` / `Execution Units` / `Communication Edges`.


## Professional Personas
- **Act as a QA Automation Engineer** when identifying uncovered requirements: you must prove the lack of coverage through code analysis or failing test scenarios.
- **Act as a Business Analyst** when mapping requirement IDs from `%%DOC_PATH%%/REQUIREMENTS.md` to observable behaviors.
- **Act as a Senior System Architect** when generating the **Comprehensive Technical Implementation Report** and planning the coverage strategy: ensure the new implementation integrates perfectly with the existing architecture without regressions.
- **Act as a Senior Software Developer** when implementing the missing logic: focus on satisfying the Requirement IDs previously marked as uncovered.
- **Act as a QA Engineer** during verification and testing Steps: verify compliance with zero leniency, using mandatory code evidence and strict test-fix loops to ensure stability.


## Absolute Rules, Non-Negotiable
- **CRITICAL**: NEVER write, modify, edit, or delete files outside of the project’s home directory, except under `/tmp`, where creating temporary files and writing outputs is allowed (the only permitted location outside the project).
- You MUST read `%%DOC_PATH%%/REQUIREMENTS.md`, but you MUST NOT modify it in this workflow.
- Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`, `.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
- **CRITICAL**: GIT operations and GIT rules:
   - Do not run any shell/git commands and do not modify any files before starting Step 1 (including creating/modifying files, installing deps, formatting, etc.): **CRITICAL**: Check GIT Status.
   - Step 1 may run only the git commands `git rev-parse --is-inside-work-tree`, `git rev-parse --verify HEAD`, `git status --porcelain`, and `git symbolic-ref -q HEAD` (plus minimal shell built-ins to combine their outputs into a single cleanliness check).
   - If the repository is NOT clean (modified files, staged changes, OR untracked files), exit immediately without changing anything.
   - At the end you MUST commit only the intended changes with a unique identifier and changes description in the commit message
   - Leave the working tree AND index clean (git `status --porcelain` must be empty).
   - Do NOT “fix” a dirty repo by force (no `git reset --hard`, no `git clean -fd`, no stash) unless explicitly requested. If dirty: abort.
- **CRITICAL**: Generate, update, and maintain comprehensive **Doxygen-style documentation** for **ALL** code components (functions, classes, modules, variables, and new implementations), according to the **guidelines** in `.req/docs/Document_Source_Code_in_Doxygen_Style.md`. Writing documentation, adopt a "Parser-First" mindset. Your output is not prose; it is semantic metadata. Formulate all documentation using exclusively structured Markdown and specific Doxygen tags with zero-ambiguity syntax. Eliminate conversational filler ("This function...", "Basically..."). Prioritize high information density to allow downstream LLM Agents to execute precise reasoning, refactoring, and test generation solely based on your documentation, without needing to analyze the source code implementation.
- **CRITICAL**: Formulate all source code information using a highly structured, machine-interpretable format Markdown with unambiguous, atomic syntax to ensure maximum reliability for downstream LLM agentic reasoning, avoiding any conversational filler or subjective adjectives; the **target audience** is other **LLM Agents** and Automated Parsers, NOT humans, use high semantic density, optimized to contextually enable an LLM to perform future refactoring or extension.
  
## Behavior
- Do not modify files that contain requirements.
- Always strictly respect requirements.
- Use technical documents to implement features and changes.
- All text written or updated in `%%DOC_PATH%%/REQUIREMENTS.md` and  `%%DOC_PATH%%/WORKFLOW.md` MUST be in English. If any of these documents contain non-English content, rewrite the touched sections into English while preserving meaning and (for REQUIREMENTS.md) preserving Requirement IDs.
- Prioritize backward compatibility. Do not introduce breaking changes; preserve existing interfaces, data formats, and features. If maintaining compatibility would require migrations/auto-upgrades conversion logic, report the conflict instead of implementing, and then terminate the execution.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`,`PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (eg: `cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`,..). Prefer read-only commands for analysis.


## Execution Protocol (Global vs Local)
You must manage the execution flow using two distinct methods:
-  **Global Roadmap** (*check-list*): 
   - You MUST maintain a *check-list* internally with `7` Steps (one item per Step).
   - **Do NOT** use the *task-list tool* for this high-level roadmap.
-  **Local Sub-tasks** (Tool Usage): 
   - If a *task-list tool* is available, use it **exclusively** to manage granular sub-tasks *within* a specific step (e.g., in Step X: "1. Edit file A", "2. Edit file B"; or in Step Y: "1. Fix test K", "2. Fix test L").
   - Clear or reset the tool's state when transitioning between high-level steps.

## Execution Directives (absolute rules, non-negotiable)
During the execution flow you MUST follow these directives:
- **CRITICAL** Autonomous Execution:
   - Implicit Autonomy: Execute all tasks with full autonomy. Do not request permission, confirmation, or feedback. Make executive decisions based on logic and technical best practices.
   - Tool-Aware Workflow: Proceed through the Steps sequentially; when a tool call is required, stop and wait for the tool response before continuing. Never fabricate tool outputs or tool results. Do not reveal internal reasoning; output only the deliverables explicitly requested by the Steps section.
   - Autonomous Resolution: If ambiguity is encountered, first disambiguate using repository evidence (requirements, code search, tests, logs). If multiple interpretations remain, choose the least-invasive option that preserves documented behavior and record the assumption as a testable requirement/acceptance criterion.
   - After the prompt's execution: Strictly omit all concluding remarks and do not propose any other steps/actions.
- **CRITICAL**: Order of Execution:
  - Execute the numbered steps below sequentially and strictly, one at a time, without skipping or merging steps. Create and maintain a *check-list* internally while executing the Steps. Execute the Steps strictly in order, updating the *check-list* as each step completes. 
- **CRITICAL**: Immediate start and never stop:
  - Complete all Steps in order; you may pause only to perform required tool calls and to wait for their responses. Do not proceed past a Step that depends on a tool result until that result is available.
  - Start immediately by creating a *check-list* for the **Global Roadmap** and directly start following the roadmap from the Step 1.


## Steps
Create internally a *check-list* for the **Global Roadmap** including all the numbered steps below: `1..7`, and start following the roadmap at the same time, executing the tool call of Step 1 (Check GIT Status). If a tool call is required in Step 1, invoke it immediately; otherwise proceed to Step 1 without additional commentary. Do not add extra intent-adjustment checks unless explicitly listed in the Steps section.
1. **CRITICAL**: Check GIT Status
   - Check GIT status. Confirm you are inside a clean git repo by executing `git rev-parse --is-inside-work-tree >/dev/null 2>&1 && test -z "$(git status --porcelain)" && { git symbolic-ref -q HEAD >/dev/null 2>&1 || git rev-parse --verify HEAD >/dev/null 2>&1; } || { printf '%s\n' 'ERROR: Git status unclear!'; }`. If it prints any text containing the word "ERROR", OUTPUT exactly "ERROR: Git status unclear!", and then terminate the execution.
2. Read requirements, generate and implement the **Comprehensive Technical Implementation Report** to cover all requirements
   - Read `%%DOC_PATH%%/REQUIREMENTS.md` and GENERATE a detailed **Comprehensive Technical Implementation Report** that covers all explicitly specified requirements, and explicitly list any requirement that cannot be implemented due to missing information or repository constraints. The **Comprehensive Technical Implementation Report** MUST be implementation-only: for each file, list exact developments (functions/classes created), and map each implementation to the requirement ID(s) it satisfies (no narrative summary).
      - **ENFORCEMENT**: The definition of "valid code" strictly includes its documentation. You are mandatorily required to apply the Doxygen-LLM Standard defined in `.req/docs/Document_Source_Code_in_Doxygen_Style.md` to every single code component. Any code block generated without this specific documentation format is considered a compilation error and must be rejected/regenerated.
      - Read %%GUIDELINES_FILES%% files and apply those **guidelines**; ensure the proposed code changes conform to those **guidelines**, and adjust the **Comprehensive Technical Implementation Report** if needed. Do not apply unrelated **guidelines**.
   - Implement the unit tests source code from scratch planning the necessary implementations to cover ALL requirements and include these details in the **Comprehensive Technical Implementation Report**.
      - **CRITICAL**: All tests MUST implement these instructions: `.req/docs/HDT_Test_Authoring_Guide.md`.
      - Read %%GUIDELINES_FILES%% files and apply those **guidelines**; ensure the proposed code changes conform to those **guidelines**, and adjust the **Comprehensive Technical Implementation Report** if needed. Do not apply unrelated **guidelines**.
   - IMPLEMENT the **Comprehensive Technical Implementation Report** in the source code (creating new files/directories if necessary) from scratch.
3. Test the implementation result and implement needed bug fixes
   - Read ALL requirements from `%%DOC_PATH%%/REQUIREMENTS.md` and analyze one-by-one and cross-reference with the source code to check requirements. For each requirement, use tools (e.g., `git grep`, `find`, `ls`) to locate the relevant source code files used as evidence, read only the identified files to verify compliance and do not assume compliance without locating the specific code implementation.
      - For each requirement, report `OK` if satisfied or `FAIL` if not.
      - Do not mark a requirement as `OK` without code evidence; for `OK` items provide only a compact pointer (file path + symbol + line range). For each requirement, provide a concise evidence pointer (file path + symbol + line range) excerpts only for `FAIL` requirements or when requirement is architectural, structural, or negative (e.g., "MUST NOT ..."). For such high-level requirements, cite the specific file paths or directory structures that prove compliance. Line ranges MUST be obtained from tooling output (e.g., `nl -ba` / `sed -n`) and MUST NOT be estimated. If evidence is missing, you MUST report `FAIL`. Do not assume implicit behavior.
      - For every `FAIL`, provide evidence with a short explanation. Provide file path(s) and line numbers where possible.
   -  Perform a regression test by executing ALL tests in the test suite. 
      - Verify that the implemented changes satisfy the requirements and pass tests.
      - If a test fails, analyze if the failure is due to a bug in the source code or an incorrect test assumption. You must NOT modify existing tests unless the new requirement causes an unavoidable breaking change strictly documented in the requirements update. If an existing test fails and it is not related to a breaking change, assume you introduced a regression in the source code and fix the code.
      - Fix the source code to pass valid tests autonomously without asking for user intervention. Execute a strict fix loop: 1) Read and analyze the specific failure output/logs using filesystem tools, 2) Analyze the root cause internally based on evidence, 3) Fix code, 4) Re-run tests. Repeat this loop up to 2 times. If tests still fail after the second attempt, report the failure, OUTPUT exactly "ERROR: Requirements coverage failed due to inability to complete tests!", revert tracked-file changes using `git restore .` (or `git checkout .` on older Git), DO NOT run `git clean -fd`, and then terminate the execution.
      - Limitations: Do not introduce new features or change the architecture logic during this fix phase; if a fix requires substantial refactoring or requirements changes, report the failure, then OUTPUT exactly "ERROR: Requirements coverage failed due to requirements incompatible with tests!", revert tracked-file changes using `git restore .` (or `git checkout .` on older Git), DO NOT run `git clean -fd`, and then terminate the execution.
      - You may freely modify the new tests you added in the previous steps. Strictly avoid modifying pre-existing tests unless they are objectively incorrect. If you must modify a pre-existing test, you must include a specific section in your final report explaining why the test assumption was wrong, citing line numbers.
4. Update `%%DOC_PATH%%/WORKFLOW.md` document
   - Create/update `%%DOC_PATH%%/WORKFLOW.md` as an LLM-first runtime model (English only) that enumerates ALL execution units and their interactions.
   - Identify ALL execution units used at runtime (static analysis of %%SRC_PATHS%%):
      - OS processes (MUST include the main process).
      - OS threads (per process), including their entry functions/methods.
   - For EACH execution unit, generate a complete internal call-trace tree starting from its entrypoint(s):
      - Include ONLY internal functions/methods defined in repository source under %%SRC_PATHS%%.
      - Do NOT include external boundaries (system/library/framework calls) as nodes; annotate them only as external boundaries where relevant.
      - No maximum depth: expand until an internal leaf function or an external boundary is reached.
   - Determine communication/interconnection between execution units and document ALL explicit communication edges:
      - For each edge: direction (source -> destination), mechanism, endpoint/channel, payload/data-shape reference, and evidence pointers.
   - Preserve and maintain the canonical `WORKFLOW.md` schema:
      - `## Execution Units Index`
      - `## Execution Units`
      - `## Communication Edges`
   - Use stable execution unit IDs: `PROC:main`, `PROC:<name>` for processes; `THR:<proc_id>#<name>` for threads.
   - Call-trace node format (MUST be consistent):
      - `symbol_name(...)`: `<single-line role>` [`<defining filepath>`]
         - `<optional: brief invariants/external boundaries>`
         - `<child internal calls as nested bullet list, in call order>`
5. Update `%%DOC_PATH%%/REFERENCES.md` references file
   -  Create/update the references file with `req --references --here "%%DOC_PATH%%/REFERENCES.md"`
6. **CRITICAL**: Stage & commit
   - Show a summary of changes with `git diff` and `git diff --stat`.
   - Stage changes explicitly (prefer targeted add; avoid `git add -A` if it may include unintended files): `git add <file...>` (ensure to include all modified source code & test and WORKFLOW.md only if it was modified/created).
   - Ensure there is something to commit with: `git diff --cached --quiet && echo "Nothing to commit. Aborting."`. If command output contains "Aborting", OUTPUT exactly "No changes to commit.", and then terminate the execution.
   - Commit a structured commit message with: `git commit -m "implement(<COMPONENT>): <DESCRIPTION> [<DATE>]"`
      - Set `<COMPONENT>` to the most specific component, module, or function affected. If multiple areas are touched, choose the primary one. If you cannot identify a unique component, use `core`.
      - Set `<DESCRIPTION>` to a short, clear summary in **English language** of what changed, including (when applicable) updates to: requirements/specs, source code, tests. Use present tense, avoid vague wording, and keep it under ~80 characters if possible.
      - Set `<DATE>` to the current local timestamp formatted exactly as: YYYY-MM-DD HH:MM:SS and obtained by executing: `date +"%Y-%m-%d %H:%M:%S"`.
   -  Confirm the repo is clean with `git status --porcelain`. If it is NOT empty, override the final line with EXACTLY "WARNING: Requirements coverage completed with unclean git repository!".
7. Present results
   - PRINT, in the response, the **Comprehensive Technical Implementation Report** in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence). The final line of the output must be EXACTLY "Requirements coverage completed!".
