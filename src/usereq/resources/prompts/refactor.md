---
description: "Perform a refactor without changing the requirements"
argument-hint: "Description of the refactor goal"
---

# Perform a refactor without changing the requirements

## Purpose
Propose and implement refactoring to the source code to improve structure or performance while strictly preserving existing behavior and complying with requirements.


## Professional Personas
- **Act as a Senior Software Developer** when refactoring: prioritize clean internal logic and performance while strictly preserving public interfaces and backward compatibility.
- **Act as a Business Analyst** when reading `%%DOC_PATH%%/REQUIREMENTS.md` to ensure that fixes or refactors never violate or change existing documented behaviors.
- **Act as a QA Automation Engineer** when validating the fix/refactor: ensure that the test suite passes and that no regressions are introduced.
- **Act as an Expert Debugger (SSD)** only if tests fail or a defect emerges during refactor.


## Absolute Rules, Non-Negotiable
- **CRITICAL**: NEVER write, modify, edit, or delete files outside of the project’s home directory, except under `/tmp`, where creating temporary files and writing outputs is allowed (the only permitted location outside the project).
- You MUST read `%%DOC_PATH%%/REQUIREMENTS.md`, but you MUST NOT modify it in this workflow.
- Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`, `.cache`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
- **CRITICAL**: GIT operations and GIT rules:
   - Do not run any shell/git commands and do not modify any files before starting Step 1 (including creating/modifying files, installing deps, formatting, etc.): **CRITICAL**: Check GIT Status.
   - Step 1 may run only the git commands `git rev-parse --is-inside-work-tree`, `git status --porcelain`, and `git symbolic-ref -q HEAD` (plus minimal shell built-ins to combine their outputs into a single cleanliness check).
   - If the repository is NOT clean (modified files, staged changes, OR untracked files), exit immediately without changing anything.
   - At the end you MUST commit only the intended changes with a unique identifier and changes description in the commit message
   - Leave the working tree AND index clean (git `status --porcelain` must be empty).
   - Do NOT “fix” a dirty repo by force (no `git reset --hard`, no `git clean -fd`, no stash) unless explicitly requested. If dirty: abort.
- **CRITICAL**: Generate, update, and maintain comprehensive **Doxygen-style documentation** for **ALL** code components (functions, classes, modules, variables, and new implementations), according the **guidelines**. The **target audience** for the documentation are other **LLM Agents** and Automated Parsers, NOT humans, ensure maximum reliability for downstream LLM agentic reasoning, avoiding any conversational filler or subjective adjectives, use high semantic density, optimized to contextually enable an LLM to perform future refactoring or extension.
- **CRITICAL**: Formulate all source code information using a highly structured, machine-interpretable format Markdown with unambiguous, atomic syntax to ensure maximum reliability for downstream LLM agentic reasoning, avoiding any conversational filler or subjective adjectives; the **target audience** are other **LLM Agents** and Automated Parsers, NOT humans, use high semantic density, optimized to contextually enable an LLM to perform future refactoring or extension.

## Behavior
- Always strictly respect requirements.
- Use technical documents to implement features and changes.
- Any new text added to an existing document MUST match that document’s current language.
- Prioritize clean implementation of internal logic. You are encouraged to refactor internals and private APIs freely to achieve refactor goals. However, you MUST strictly preserve all public interfaces, data formats, and externally observable behaviors. Do not maintain backward compatibility for internal/private components (i.e., remove legacy internal code), but ensure strict backward compatibility for the public API.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`, `PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (e.g.,`cat`, `sed`, `perl -pi`, `printf > file`,`rm -f`,..). Prefer read-only commands for analysis.


## Execution Protocol (Global vs Local)
You must manage the execution flow using two distinct methods:
-  **Global Roadmap** (*check-list*): 
   - You MUST maintain a *check-list* internally with `8` Steps (one item per Step).
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
   - After Prompt's Execution: Strictly omit all concluding remarks and do not propose any other steps/actions.
- **CRITICAL**: Order of Execution:
  - Execute the numbered steps below sequentially and strictly, one at a time, without skipping or merging steps. Create and maintain a *check-list* internally during executing the Steps. Execute the Steps strictly in order, updating the *check-list* as each step completes. 
- **CRITICAL**: Immediate start and never stop:
  - Complete all Steps in order; you may pause only to perform required tool calls and to wait for their responses. Do not proceed past a Step that depends on a tool result until that result is available.
  - Start immediately by creating a *check-list* for the **Global Roadmap** and directly start following the roadmap from the Step 1.


## Steps
Create internally a *check-list* for the **Global Roadmap** including all below numbered steps: `1..8`, and start following the roadmap at the same time, executing the tool call of Step 1 (Check GIT Status). Do not stop generating until the tool is invoked. Do not add additional intent adjustments check, except if it's explicit indicated on steps.
1. **CRITICAL**: Check GIT Status
   - Check GIT status. Confirm you are inside a clean git repo executing `git rev-parse --is-inside-work-tree >/dev/null 2>&1 && test -z "$(git status --porcelain)" && git symbolic-ref -q HEAD >/dev/null 2>&1 || { printf '%s\n' 'ERROR: Git status unclear!'; }`. If it prints any text containing the word "ERROR", OUTPUT exactly "ERROR: Git status unclear!", and then terminate the execution.
2. **CRITICAL**: Check `%%DOC_PATH%%/REQUIREMENTS.md`, `%%DOC_PATH%%/WORKFLOW.md` and `%%DOC_PATH%%/REFERENCES.md` files presence
   - If the `%%DOC_PATH%%/REQUIREMENTS.md` file does NOT exist, OUTPUT exactly "ERROR: File %%DOC_PATH%%/REQUIREMENTS.md not exist, generate it with /req.write prompt!", and then terminate the execution.
   - If the `%%DOC_PATH%%/WORKFLOW.md` file does NOT exist, OUTPUT exactly "ERROR: File %%DOC_PATH%%/WORKFLOW.md not exist, generate it with /req.workflow prompt!", and then terminate the execution.
   - If the `%%DOC_PATH%%/REFERENCES.md` file does NOT exist, OUTPUT exactly "ERROR: File %%DOC_PATH%%/REFERENCES.md not exist, generate it with /req.references prompt!", and then terminate the execution.
3. Generate and implement the **Comprehensive Technical Implementation Report** to implemet the refactory
   - Using [User Request](#users-request) as a unified semantic framework, extract all directly and tangentially related information from `%%DOC_PATH%%/REQUIREMENTS.md`, `%%DOC_PATH%%/WORKFLOW.md` and `%%DOC_PATH%%/REFERENCES.md`, prioritizing high recall to capture every borderline connection across both sources, to identify the most likely related files and functions based on explicit evidence, and treat any uncertain links as candidates without claiming completeness, then analyze the involved source code from %%SRC_PATHS%% and GENERATE a detailed **Comprehensive Technical Implementation Report** documenting the exact modifications to the source code that implement the refactor described by the [User Request](#users-request). The **Comprehensive Technical Implementation Report** MUST be implementation-only and patch-oriented: for each file, list exact edits (functions/classes touched), include only changed snippets, and map each change to the requirement ID(s) it satisfies (no narrative summary)
      - **CRITICAL**: ALL code components MUST be properly documented by inserting Doxygen comments according to these indications: `.req/docs/Document_Source_Code_in_Doxygen_Style.md`.
      - Read %%GUIDELINES_FILES%% files and apply those **guidelines**; ensure the proposed code changes conform to those **guidelines**, and adjust the **Comprehensive Technical Implementation Report** if needed. Do not apply unrelated **guidelines**.
   - From %%TEST_PATH%%, locate and read only the unit tests that are relevant to the affected requirement IDs and touched modules (via targeted search), and plan the necessary refactoring/additions
 to cover performance-critical paths and include these details in the **Comprehensive Technical Implementation Report**.
      - **CRITICAL**: All tests MUST implement these instructions: `.req/docs/HDT_Test_Authoring_Guide.md`.
      - Read %%GUIDELINES_FILES%% files and apply those **guidelines**; ensure the proposed code changes conform to those **guidelines**, and adjust the **Comprehensive Technical Implementation Report** if needed. Do not apply unrelated **guidelines**.
   - A change is allowed ONLY if it: (a) preserves externally observable behavior required by `%%DOC_PATH%%/REQUIREMENTS.md` AND (b) improves structure/performance/reliability with measurable evidence or a clear invariant-based justification. Do not claim performance wins without explicit benchmarks, profiling notes, or complexity-relevant code changes. If the request requires new user-visible features, new configuration options, or changes to documented behavior, recommend to use the `req.new` or `req.change` workflow instead, then OUTPUT exactly "ERROR: Refactor failed due incompatible requirement!", and then terminate the execution.
   - IMPLEMENT the **Comprehensive Technical Implementation Report** in the source code (creating new files/directories if necessary). You may make minimal mechanical adjustments needed to fit the actual codebase (file paths, symbol names), but you MUST NOT add new features or scope beyond the **Comprehensive Technical Implementation Report**.
4. Test the implementation result and implement needed bug-fix
   - Read ALL requirements from `%%DOC_PATH%%/REQUIREMENTS.md` and analyze one-by-one and cross-reference with the source code to check requirements. For each requirement, use tools (e.g., `git grep`, `find`, `ls`) to locate the relevant source code files used as evidence, read only the identified files to verify compliance and do not assume compliance without locating the specific code implementation.
      - For each requirement, report `OK` if satisfied or `FAIL` if not.
      - Do not mark a requirement as `OK` without code evidence; for `OK` items provide only a compact pointer (file path + symbol + line range). For each requirement, provide a concise evidence pointer (file path + symbol + line range) excerpts only for `FAIL` requirements or when requirement is architectural, structural, or negative (e.g., "shall not..."). For such high-level requirements, cite the specific file paths or directory structures that prove compliance. Line ranges MUST be obtained from tooling output (e.g., `nl -ba` / `sed -n`) and MUST NOT be estimated. If evidence is missing, you MUST report `FAIL`. Do not assume implicit behavior.
      - For every `FAIL`, provide evidence with a short explanation. Provide file path(s) and line numbers where possible.
   - Run ALL tests of test suite. 
      - Verify that the implemented changes satisfy the requirements and pass tests.
      - If a test fails, analyze if the failure is due to a bug in the source code or an incorrect test assumption. Assume the test is correct unless the requirement explicitly contradicts the test expectation. Changes to existing tests require a higher burden of proof and specific explanation.
      - Fix the source code to pass valid tests autonomously without asking for user intervention. Execute a strict fix loop: 1) Read and analyze the specific failure output/logs using filesystem tools, 2) Analyze the root cause internally based on evidence, 3) Fix code, 4) Re-run tests. Repeat this loop up to 2 times. If tests still fail after the second attempt, report the failure, OUTPUT exactly "ERROR: Refactor  failed due unable to complete tests!", revert tracked-file changes using `git restore .` (or `git checkout .` on older Git), DO NOT run `git clean -fd`, and then terminate the execution.
      - Limitations: Do not introduce new features or change the architecture logic during this fix phase; if a fix requires substantial refactoring or requirements changes, report the failure, then OUTPUT exactly "ERROR: Refactor failed due incompatible requirement with tests!", revert tracked-file changes using `git restore .` (or `git checkout .` on older Git), DO NOT run `git clean -fd`, and then terminate the execution.
      - You may freely modify the new tests you added in the previous steps. Strictly avoid modifying pre-existing tests unless they are objectively incorrect. If you must modify a pre-existing test, you must include a specific section in your final report explaining why the test assumption was wrong, citing line numbers.
5. Update `%%DOC_PATH%%/WORKFLOW.md` document
   -  Analyze the recently implemented code changes and identify new features and behavioral updates to infer the software’s behavior and main features to reconstruct the software's execution logic: 
      -  Identify the primary functions and architectural components utilized based on static code analysis of the main entry points. Focus on explicit calls and visible dependencies..
      -  Identify all file-system operations (reading or writing files).
      -  Identify all external API call.
      -  Identify all external database access.
      -  Identify any common code logic.
      -  Ignore unit tests source code, documents automation source code and any companion-scripts (e.g., launching scripts, environments management scripts, examples scripts,..).
      Produce a hierarchical structure of bullet lists that reflect the implemented functionality. Detail the complete execution workflow, naming each function and sub-function called, recursively, only to the extent it is directly evidenced by the source code and repository artifacts. For every function, include a single-line description. Avoid unverified assumptions; focus strictly on the provided code; don't summarize.
      Review and update the file `%%DOC_PATH%%/WORKFLOW.md` following a strict Technical Call Tree structure. For each main feature, you must drill down from the entry point to the lower-level internal functions, and document structure and traceability, until you reach stable abstraction boundaries (public APIs, core domain functions, or I/O boundaries); do not expand further unless required for traceability:
      -  Use a hierarchical structure of bullet lists with at least 3 levels of depth, maximum 6 levels fo depth, and for EACH feature you MUST include:
         -  Level 1: High-level Feature or Process description (keep it concise).
         -  Level 2: Component, Class, or Module involved, list classes/services/modules used in the trace.
         -  Level 3+: Call Trace, specific Function/Method name (including sub functions) Called.
            -  Node Description, every *function node* entry must be described with below informations:
               -  `function_name()`: mandatory, the function name exactly as defined in the source code.
               -  `short single-line`: mandatory, a short single-line technical description of its specific action.
               -  `filename`: mandatory, filename where the function is defined.
               -  `description`: a high-density technical summary detailing critical algorithmic logic and side effects. Write description for other LLM **Agents** and Automated Parsers, NOT humans. Must be optimized for machine comprehension. Do not write flowery prose. Use high semantic density, optimized to contextually enable an **LLM Agent** to perform future refactoring or extension.
               -  `child nodes as child bullet-list`: optional, nested sub-function calls, in the same order as are called inside `function_name()`.
            -  Hierarchical Structure, child *function node* MUST be added to parent *function node* as child bullet-list. Do NOT add system, library or module functions (e.g., `os.walk()`, `re.sub()`, `<foobar>.open()`). Example:
               -  `parent_func1()`: `short single-line for parent_func1` [`filename where is declared parent_func1`]
                  -  `description of parent_func1`
                  -  `child_func2()`: `short single-line for child_func2` [`filename where is declared child_func2`]
                     -  `description of child_func2`
                  -  `child_func3()`: `short single-line for child_func3` [`filename where is declared child_func3`]
                     -  `description of child_func3`
                     -  `child_child_func4()`: `short single-line for child_child_func4` [`filename where is declared child_child_func4`]
                        -  `description of child_child_func4`
                        -  ...
      -  Ensure the workflow reflects the actual sequence of calls found in the code. Do not skip intermediate logic layers. Highlight existing common code logic.
      -  Prefer concise traces over prose, but expand the call-tree to the minimum needed for traceability.
6. Update `%%DOC_PATH%%/REFERENCES.md` refecences file
   -  Make refecences file with `req --references --here "%%DOC_PATH%%/REFERENCES.md"`
7. **CRITICAL**: Stage & commit
   - Show a summary of changes with `git diff` and `git diff --stat`.
   - Stage changes explicitly (prefer targeted add; avoid `git add -A` if it may include unintended files): `git add <file...>` (ensure to include all modified source code & test and WORKFLOW.md only if it was modified/created).
   - Ensure there is something to commit with: `git diff --cached --quiet && echo "Nothing to commit. Aborting."`. If command output contains "Aborting", OUTPUT exactly "No changes to commit.", and then terminate the execution.
   - Commit a structured commit message with: `git commit -m "refactor(<COMPONENT>): <DESCRIPTION> [<DATE>]"`
      - Set `<COMPONENT>` to the most specific component, module, or function affected. If multiple areas are touched, choose the primary one. If you cannot identify a unique component, use `core`.
      - Set `<DESCRIPTION>` to a short, clear summary in English language of what changed, including (when applicable) updates to: requirements/specs, source code, tests. Use present tense, avoid vague wording, and keep it under ~80 characters if possible.
      - Set `<DATE>` to the current local timestamp formatted exactly as: YYYY-MM-DD HH:MM:SS and obtained by executing: `date +"%Y-%m-%d %H:%M:%S"`.
   - Confirm the repo is clean with `git status --porcelain`, If NOT empty override the final line with EXACTLY "WARNING: Refactor request completed with unclean git repository!".
8. Present results
   - PRINT in the response presenting the **Comprehensive Technical Implementation Report** in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence). The final line of the output must be EXACTLY "Refactor completed!".

<h2 id="users-request">User's Request</h2>
%%ARGS%%
