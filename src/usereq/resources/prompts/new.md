---
description: "Implement a new requirement and make the corresponding source code changes"
argument-hint: "Description of the new requirement/feature to implement"
---

# Implement a new requirement and make the corresponding source code changes

## Purpose
Introduce a new, backwards-compatible capability by first extending the normative SRS (`%%DOC_PATH%%/REQUIREMENTS.md`) with the new requirement(s), then implementing and verifying the corresponding code/test changes with strict traceability to requirement IDs so downstream LLM Agents can reason over the new feature deterministically.

## Scope
In scope: patch-style updates to `%%DOC_PATH%%/REQUIREMENTS.md` that add the new feature requirements, an implementation plan, code/test changes under %%SRC_PATHS%% and %%TEST_PATH%%, verification via the test suite, updates to `%%DOC_PATH%%/WORKFLOW.md` and `%%DOC_PATH%%/REFERENCES.md`, and a clean git commit. Out of scope: breaking changes, migrations/compatibility conversions, or any feature work not captured as explicit requirements (report conflicts and terminate per prompt rules).


## Professional Personas
- **Act as a Business Analyst** when generating **Software Requirements Specification Update** and during requirements analysis and update: your priority is requirement integrity, atomic description of changes, and ensuring no logical conflicts in `%%DOC_PATH%%/REQUIREMENTS.md`.
- **Act as a Senior System Architect** when generating the **Comprehensive Technical Implementation Report**: translate requirements into a robust, modular, and non-breaking technical implementation plan.
- **Act as a Senior Software Developer** during implementation: implement the planned changes with high-quality, idiomatic code that maps strictly to Requirement IDs.
- **Act as a QA Engineer** during verification and testing: verify compliance with zero leniency, using mandatory code evidence and strict test-fix loops to ensure stability.


## Absolute Rules, Non-Negotiable
- **CRITICAL**: NEVER write, modify, edit, or delete files outside of the project’s home directory, except under `/tmp`, where creating temporary files and writing outputs is allowed (the only permitted location outside the project).
- You can read, write, or edit `%%DOC_PATH%%/REQUIREMENTS.md`.
- Treat running the test suite as safe. Any files created solely as test artifacts should be considered acceptable because they are always confined to temporary or ignored directories and do not alter existing project files. All file operations executed by tests are restricted to temporary or cache directories (e.g., `tmp/`, `temp/`,`.cache/`, `.pytest_cache/`, `node_modules/.cache`, `/tmp`); when generating new test cases, strictly adhere to this rule and ensure all write operations use these specific directories.
- **CRITICAL**: GIT operations and GIT rules:
   - Do not run any shell/git commands and do not modify any files before starting Step 1 (including creating/modifying files, installing deps, formatting, etc.): **CRITICAL**: Check GIT Status.
   - Step 1 may run only the git commands `git rev-parse --is-inside-work-tree`, `git status --porcelain`, and `git symbolic-ref -q HEAD` (plus minimal shell built-ins to combine their outputs into a single cleanliness check).
   - If the repository is NOT clean (modified files, staged changes, OR untracked files), exit immediately without changing anything.
   - At the end you MUST commit only the intended changes with a unique identifier and changes description in the commit message
   - Leave the working tree AND index clean (git `status --porcelain` must be empty).
   - Do NOT “fix” a dirty repo by force (no `git reset --hard`, no `git clean -fd`, no stash) unless explicitly requested. If dirty: abort.
- **CRITICAL**: Generate, update, and maintain comprehensive **Doxygen-style documentation** for **ALL** code components (functions, classes, modules, variables, and new implementations), according to the **guidelines** in `.req/docs/Document_Source_Code_in_Doxygen_Style.md`. Writing documentation, adopt a "Parser-First" mindset. Your output is not prose; it is semantic metadata. Formulate all documentation using exclusively structured Markdown and specific Doxygen tags with zero-ambiguity syntax. Eliminate conversational filler ("This function...", "Basically..."). Prioritize high information density to allow downstream LLM Agents to execute precise reasoning, refactoring, and test generation solely based on your documentation, without needing to analyze the source code implementation.
- **CRITICAL**: Formulate all new or edited requirements and all source code information using a highly structured, machine-interpretable format Markdown with unambiguous, atomic syntax to ensure maximum reliability for downstream LLM agentic reasoning, avoiding any conversational filler or subjective adjectives; the **target audience** are other **LLM Agents** and Automated Parsers, NOT humans, use high semantic density, optimized to contextually enable an LLM to perform future refactoring or extension.
- **CRITICAL**: NEVER add requirements to SRS regarding how comments are handled (added/edited/deteled) within the source code, including the format, style, or language to be used, even if explicitly requested. Ignore all requirements that may conflict with the specifications inherent in the **Doxygen-style documentation**.

## Behavior
- Propose changes based only on the requirements, user request, and repository evidence. Every proposed code change MUST reference at least one requirement ID or explicit text in user request.
- Use technical documents to implement features and changes.
- Any new text added to an existing document MUST match that document’s current language.
- Prioritize backward compatibility. Do not introduce breaking changes; preserve existing interfaces, data formats, and features.
- If maintaining compatibility would require migrations/auto-upgrades conversion logic, report the conflict instead of implementing, and then terminate the execution.
- If `.venv/bin/python` exists in the project root, use it for Python executions (e.g., `PYTHONPATH=src .venv/bin/python -m pytest`,`PYTHONPATH=src .venv/bin/python -m <program name>`). Non-Python tooling should use the project's standard commands.
- Use filesystem/shell tools to read/write/delete files as needed (e.g., `cat`, `sed`, `perl -pi`, `printf > file`, `rm -f`, ...). Prefer read-only commands for analysis.


## Source Construct Extraction via req --find / req --files-find
When you need hard evidence from source code (APIs, entrypoints, data types, imports, constants, decorators/annotations, modules/namespaces), use req to extract language constructs as structured markdown (with signatures + line ranges, and optional line-numbered code).
### What these commands do (and what they don’t)
- They extract named constructs (e.g., CLASS, FUNCTION, STRUCT, INTERFACE, IMPORT, …) and filter them by TAG and name-regex.
- The regex (PATTERN) matches the construct name only (not the body). If you need “search inside code”, use rg/git grep in addition.
- Output is markdown, grouped by file: header @@@ <filepath> | <language>, then per-construct blocks with:
    - ### <TAG>: <name> + optional Signature + Lines: <start>-<end>
    - optional extracted Doxygen fields (if present in/around the construct)
    - a fenced code block containing the complete construct slice, with comments stripped (strings preserved)
### Choose the right mode
- Project-wide scan (configured --src-dir): use --find (requires --here or --base)
    - Correct syntax is: req --here --find <TAG_FILTER> <NAME_REGEX>
    - Note: --find does not take a filename; it scans all files under the configured source dirs.
- Target specific files: use --files-find (standalone; --here is optional but harmless)
    - Syntax: req --here --files-find <TAG_FILTER> <NAME_REGEX> <FILE1> [FILE2 ...]
### Always enable line-numbered code when you plan to cite evidence
Add --enable-line-numbers so code lines are prefixed as <n>::
- req --here --enable-line-numbers --find "<TAG_FILTER>" "<NAME_REGEX>"
- req --here --enable-line-numbers --files-find "<TAG_FILTER>" "<NAME_REGEX>" <FILE...>
### TAGs and filters
- TAG_FILTER is a pipe-separated list (case-insensitive): e.g. CLASS|FUNCTION|IMPORT
- Tags are language-dependent; unsupported tags are simply ignored for that language, and files may be skipped if none of the requested tags apply.
- To discover the exact supported TAGs list (per language), run: req -h and read the --files-find help section.
- Practical “broad but safe” TAG_FILTER for analysis (cross-language): CLASS|STRUCT|ENUM|INTERFACE|TRAIT|IMPL|FUNCTION|METHOD|MODULE|NAMESPACE|TYPE_ALIAS|TYPEDEF|IMPORT|CONSTANT|VARIABLE|MACRO|DECORATOR|COMPONENT|PROPERTY|PROTOCOL|EXTENSION|UNION
### Regex rules (NAME_REGEX)
- It’s a Python-style regex applied with re.search() against the construct name.
- Prefer anchored patterns when possible:
    - Exact: ^Foo$
    - Prefix: ^parse_
    - Suffix: Service$
    - Fallback: .* (only when scope is already constrained by files/TAGs)
### Failure modes you must handle
- If you get “no constructs found”, adjust one of: TAGs (supported?), file paths, or NAME_REGEX (valid regex?).
- This extractor is regex-based (not a full AST parser); treat results as evidence pointers, and confirm edge cases by opening the referenced file/lines if needed.


## Execution Protocol (Global vs Local)
You must manage the execution flow using two distinct methods:
-  **Global Roadmap** (*check-list*): 
   - You MUST maintain a *check-list* internally with `9` Steps (one item per Step).
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
Create internally a *check-list* for the **Global Roadmap** including all below numbered steps: `1..9`, and start following the roadmap at the same time, executing the tool call of Step 1 (Check GIT Status). If a tool call is required in Step 1, invoke it immediately; otherwise proceed to Step 1 without additional commentary.Do not add extra intent-adjustment checks unless explicitly listed in the Steps section.
1. **CRITICAL**: Check GIT Status
   - Check GIT status. Confirm you are inside a clean git repo executing `git rev-parse --is-inside-work-tree >/dev/null 2>&1 && test -z "$(git status --porcelain)" && git symbolic-ref -q HEAD >/dev/null 2>&1 || { printf '%s\n' 'ERROR: Git status unclear!'; }`. If it prints any text containing the word "ERROR", OUTPUT exactly "ERROR: Git status unclear!", and then terminate the execution.
2. **CRITICAL**: Check `%%DOC_PATH%%/REQUIREMENTS.md`, `%%DOC_PATH%%/WORKFLOW.md` and `%%DOC_PATH%%/REFERENCES.md` files presence
   - If the `%%DOC_PATH%%/REQUIREMENTS.md` file does NOT exist, OUTPUT exactly "ERROR: File %%DOC_PATH%%/REQUIREMENTS.md not exist, generate it with /req.write prompt!", and then terminate the execution.
   - If the `%%DOC_PATH%%/WORKFLOW.md` file does NOT exist, OUTPUT exactly "ERROR: File %%DOC_PATH%%/WORKFLOW.md not exist, generate it with /req.workflow prompt!", and then terminate the execution.
   - If the `%%DOC_PATH%%/REFERENCES.md` file does NOT exist, OUTPUT exactly "ERROR: File %%DOC_PATH%%/REFERENCES.md not exist, generate it with /req.references prompt!", and then terminate the execution.
3. Generate and apply the **Software Requirements Specification Update** to cover new requirements
   - Using [User Request](#users-request) as a semantic guide, extract all information from `%%DOC_PATH%%/REQUIREMENTS.md` that is directly or even tangentially related, prioritizing high recall to capture every relevant nuance and borderline connection, to determine the required requirement adjustments, then integrate new uncovered requirements from [User Request](#users-request), then GENERATE a detailed **Software Requirements Specification Update** documenting the exact modifications to requirements needed to implement the changes described by the [User Request](#users-request). This **Software Requirements Specification Update** must account for the original User Request and all subsequent changes and adjustments for `%%DOC_PATH%%/REQUIREMENTS.md`, must contain only the exact requirement edits needed: provide patch-style ‘Before → After’ blocks for each modified section/requirement, quoting only the changed text (no full-document rewrites):
      - Apply the outlined guidelines when documenting changes to the requirements (follow the existing style, structure, and language)
      - Never introduce new requirements solely to explicitly forbid functions/features/behaviors. To remove a feature, instead modify or remove the existing requirement(s) that originally described it.
      - Format the requirements as a bulleted list.
      - Ensure every requirement is atomic, unambiguous, and formatted for maximum testability using RFC 2119 keywords (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY)
      - Write each requirement for other LLM **Agents** and Automated Parsers, NOT humans.
      - Must be optimized for machine comprehension. Do not write flowery prose. Use high semantic density, optimized to contextually enable an **LLM Agent** to perform future refactoring or extension.
      - In this step, do not edit, create, delete, or rename any source code files in the project (including refactors or formatting-only changes).
   - Do not change the intent of existing requirements unless the new feature logically requires it. You may make minimal edits for consistency (references, numbering, glossary) as long as you explicitly list them.
      - If you must *adjust* an existing requirement's intent, list the exact requirement(s) and explain why.
   - APPLY the **Software Requirements Specification Update** to `%%DOC_PATH%%/REQUIREMENTS.md`, following its formatting, language, and guidelines from the template at `.req/docs/Requirements_Template.md`. Do NOT introduce any additional edits beyond what the **Software Requirements Specification Update** describes.
4. Generate and implement the **Comprehensive Technical Implementation Report** according to the **Software Requirements Specification Update**
   - Using [User Request](#users-request) as a unified semantic framework, extract all directly and tangentially related information from `%%DOC_PATH%%/REQUIREMENTS.md`, `%%DOC_PATH%%/WORKFLOW.md` and `%%DOC_PATH%%/REFERENCES.md`, prioritizing high recall to capture every borderline connection across both sources, to identify the most likely related files and functions based on explicit evidence, and treat any uncertain links as candidates without claiming completeness, then analyze the involved source code from %%SRC_PATHS%% and GENERATE a detailed **Comprehensive Technical Implementation Report** documenting the exact modifications to the source code that will cover all new requirements in **Software Requirements Specification Update** and the [User Request](#users-request). The **Comprehensive Technical Implementation Report** MUST be implementation-only and patch-oriented: for each file, list exact edits (functions/classes touched), include only changed snippets, and map each change to the requirement ID(s) it satisfies (no narrative summary)
      - **ENFORCEMENT**: The definition of "valid code" strictly includes its documentation. You are mandatorily required to apply the Doxygen-LLM Standard defined in `.req/docs/Document_Source_Code_in_Doxygen_Style.md` to every single code component. Any code block generated without this specific documentation format is considered a compilation error and must be rejected/regenerated.
      - Read %%GUIDELINES_FILES%% files and apply those **guidelines**; ensure the proposed code changes conform to those **guidelines**, and adjust the **Comprehensive Technical Implementation Report** if needed. Do not apply unrelated **guidelines**.
   -  From %%TEST_PATH%%, locate and read only the unit tests that are relevant to the affected requirement IDs and touched modules (via targeted search), and plan the necessary refactoring/additions
 to cover new requirements and include these details in the **Comprehensive Technical Implementation Report**.
       - **CRITICAL**: All tests MUST implement these instructions: `.req/docs/HDT_Test_Authoring_Guide.md`.
       - Read %%GUIDELINES_FILES%% files and apply those **guidelines**; ensure the proposed code changes conform to those **guidelines**, and adjust the **Comprehensive Technical Implementation Report** if needed. Do not apply unrelated **guidelines**.
   -  IMPLEMENT the **Comprehensive Technical Implementation Report** in the source code (creating new files/directories if necessary). You may make minimal mechanical adjustments needed to fit the actual codebase (file paths, symbol names), but you MUST NOT add new features or scope beyond the **Comprehensive Technical Implementation Report**.
5. Test the implementation result and implement needed bug-fix
   -  Using [User Request](#users-request) as a semantic guide, extract all information from `%%DOC_PATH%%/REQUIREMENTS.md` that is directly or even tangentially related, prioritizing high recall to capture every relevant nuance and borderline connection, to determine related requirements, then analyze one-by-one and cross-reference with the source code. For each requirement, use tools (e.g., `git grep`, `find`, `ls`) to locate the relevant source code files used as evidence, read only the identified files to verify compliance and do not assume compliance without locating the specific code implementation.
      - For each requirement, report `OK` if satisfied or `FAIL` if not.
      - Do not mark a requirement as `OK` without code evidence; for `OK` items provide only a compact pointer (file path + symbol + line range). For each requirement, provide a concise evidence pointer (file path + symbol + line range) excerpts only for `FAIL` requirements or when requirement is architectural, structural, or negative (e.g., "shall not..."). For such high-level requirements, cite the specific file paths or directory structures that prove compliance. Line ranges MUST be obtained from tooling output (e.g., `nl -ba` / `sed -n`) and MUST NOT be estimated. If evidence is missing, you MUST report `FAIL`. Do not assume implicit behavior.
      - For every `FAIL`, provide evidence with a short explanation. Provide file path(s) and line numbers where possible.
   - Perform a regression test executing ALL tests of test suite. 
      - Verify that the implemented changes satisfy the requirements and pass tests.
      - If a test fails, analyze if the failure is due to a bug in the source code or an incorrect test assumption. You must NOT modify existing tests unless the new requirement causes an unavoidable breaking change strictly documented in the requirements update. If an existing test fails and it is not related to a breaking change, assume you introduced a regression in the source code and fix the code.
      - Fix the source code to pass valid tests autonomously without asking for user intervention. Execute a strict fix loop: 1) Read and analyze the specific failure output/logs using filesystem tools, 2) Analyze the root cause internally based on evidence, 3) Fix code, 4) Re-run tests. Repeat this loop up to 2 times. If tests still fail after the second attempt, report the failure, OUTPUT exactly "ERROR: New implementation failed due unable to complete tests!", revert tracked-file changes using `git restore .` (or `git checkout .` on older Git), DO NOT run `git clean -fd`, and then terminate the execution.
      - Limitations: Do not introduce new features or change the architecture logic during this fix phase; if a fix requires substantial refactoring or requirements changes, report the failure, then OUTPUT exactly "ERROR: New implementation failed due incompatible requirement with tests!", revert tracked-file changes using `git restore .` (or `git checkout .` on older Git), DO NOT run `git clean -fd`, and then terminate the execution.
      - You may freely modify the new tests you added in the previous steps. For pre-existing tests, update or refactor them ONLY if they conflict with the new or modified requirements. Preserve the intent of tests covering unchanged logic. If you must modify a pre-existing test, you must include a specific section in your final report explaining why the test assumption was wrong or outdated, citing line numbers.
6. Update `%%DOC_PATH%%/WORKFLOW.md` document
   - Analyze the recently implemented code changes and identify new features and behavioral updates to infer the software’s behavior and main features to reconstruct the software's execution logic: 
      -  Identify the primary functions and architectural components utilized based on static code analysis of the main entry points. Focus on explicit calls and visible dependencies.
      -  Identify all file-system operations (reading or writing files).
      -  Identify all external API calls.
      -  Identify all external database access.
      -  Identify any common code logic.
      -  Ignore unit tests source code, documents automation source code and any companion-scripts (e.g., launching scripts, environments management scripts, examples scripts,..).
      Produce a hierarchical structure of bullet lists that reflect the implemented functionality. Detail the complete execution workflow, naming each function and sub-function called, recursively, only to the extent it is directly evidenced by the source code and repository artifacts. For every function, include a single-line description. Avoid unverified assumptions; focus strictly on the provided code; don't summarize.
      Review and update the file `%%DOC_PATH%%/WORKFLOW.md` following a strict Technical Call Tree structure. For each main feature, you must drill down from the entry point to the lower-level internal functions, and document structure and traceability, until you reach stable abstraction boundaries (public APIs, core domain functions, or I/O boundaries); do not expand further unless required for traceability:
      -  Use a hierarchical structure of bullet lists with at least 3 levels of depth, maximum 6 levels of depth, and for EACH feature you MUST include:
         -  Level 1: High-level Feature or Process description (keep it concise).
         -  Level 2: Component, Class, or Module involved, list classes/services/modules used in the trace.
         -  Level 3+: Call Trace, specific Function/Method name (including sub functions) Called.
            -  Node Description, every *function node* entry must include the following information:
               -  `function_name()`: mandatory, the function name exactly as defined in the source code.
               -  `filename`: mandatory, filename where the function is defined.
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
7. Update `%%DOC_PATH%%/REFERENCES.md` references file
   -  Create/update the references file with `req --references --here "%%DOC_PATH%%/REFERENCES.md"`
8. **CRITICAL**: Stage & commit
   - Show a summary of changes with `git diff` and `git diff --stat`.
   - Stage changes explicitly (prefer targeted add; avoid `git add -A` if it may include unintended files): `git add <file...>` (ensure to include all modified source code & test, `%%DOC_PATH%%/REQUIREMENTS.md` and WORKFLOW.md only if it was modified/created).
   - Ensure there is something to commit with: `git diff --cached --quiet && echo "Nothing to commit. Aborting."`. If command output contains "Aborting", OUTPUT exactly "No changes to commit.", and then terminate the execution.
   - Commit a structured commit message with: `git commit -m "new(<COMPONENT>): <DESCRIPTION> [<DATE>]"`
      - Set `<COMPONENT>` to the most specific component, module, or function affected. If multiple areas are touched, choose the primary one. If you cannot identify a unique component, use `core`.
      - Set `<DESCRIPTION>` to a short, clear summary in **English language** of what changed, including (when applicable) updates to: requirements/specs, source code, tests. Use present tense, avoid vague wording, and keep it under ~80 characters if possible.
      - Set `<DATE>` to the current local timestamp formatted exactly as: YYYY-MM-DD HH:MM:SS and obtained by executing: `date +"%Y-%m-%d %H:%M:%S"`.
   - Confirm the repo is clean with `git status --porcelain`, If NOT empty override the final line with EXACTLY "WARNING: New implementation completed with unclean git repository!".
9. Present results
   - PRINT in the response presenting the **Software Requirements Specification Update** and the **Comprehensive Technical Implementation Report** in a clear, structured format suitable for analytical processing (lists of findings, file paths, and concise evidence). The final line of the output must be EXACTLY "New implementation completed!".

<h2 id="users-request">User's Request</h2>
%%ARGS%%
