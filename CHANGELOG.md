# Changelog

## [0.21.0](https://github.com/Ogekuri/useReq/compare/v0.20.0..v0.21.0) - 2026-03-06
### 🚜  Changes
- derive upgrade source from remotes [useReq] *(cli)*
  - Update SRS for dynamic --upgrade source and program-name-based --uninstall.
  - Align idle-state JSON keys to explicit human-readable timestamp field names.
  - Implement remote owner/repository resolver shared by release check and upgrade path.
  - Keep startup idle-gated check before argv parsing with 2s timeout and 24h idle window.
  - Extend tests for upgrade command source URL, uninstall target, and idle JSON schema fields.
- add idle-gated release checks [useReq] *(cli)*
  - Update release-check requirements to run at most once per idle window.
  - Persist startup check state in /home/ogekuri/.github_api_idle-time.<program_name>.
  - Keep dynamic GitHub endpoint resolution from active git remotes.
  - Retain 2-second timeout and bright green/red output semantics.
  - Add tests for idle skip and successful idle-state persistence.
- align version-warning color semantics [useReq] *(requirements)*
  - Update SRS-029 from bright-red to bright-green to match new startup release-check behavior.
- derive release-check URL from git remotes [useReq] *(cli)*
  - Update SRS-050/SRS-051/SRS-052 and add SRS-269 for startup release-check behavior.
  - Resolve latest-release API URL from active git remotes instead of fixed owner/repo.
  - Set hardcoded default timeout to 2 seconds and keep pre-parse execution order.
  - Emit bright-green message for newer version with installed/latest values.
  - Emit bright-red diagnostic messages for release-check failures (including HTTP 403 details).
  - Adjust and extend tests for timeout, URL resolution, color output, and failure diagnostics.

## [0.19.0](https://github.com/Ogekuri/useReq/compare/v0.18.0..v0.19.0) - 2026-03-06
### 🚜  Changes
- move update check before argument parsing and color warning [useReq] *(cli)*
  - Update SRS-050/SRS-052 and align SRS-029 with startup check behavior.
  - Run release-check at program startup before parse/validation.
  - Emit newer-version warning in bright red on stderr with ANSI reset.
  - Refresh update-check tests for startup-order and red warning output.
  - Update WORKFLOW runtime call-trace and regenerate REFERENCES index.

## [0.17.0](https://github.com/Ogekuri/useReq/compare/v0.16.0..v0.17.0) - 2026-03-06
### ⛰️  Features
- add manual dispatch trigger [useReq] *(release-workflow)*
  - append SRS-268 for manual release workflow dispatch
  - enable workflow_dispatch in .github/workflows/release-uvx.yml
  - add test for release workflow trigger configuration
  - update WORKFLOW.md and regenerate REFERENCES.md

## [0.15.0](https://github.com/Ogekuri/useReq/compare/v0.14.0..v0.15.0) - 2026-03-05
### 🐛  Bug Fixes
- Fix .gitignore file.
- Remove .place-holder files.

## [0.13.0](https://github.com/Ogekuri/useReq/compare/v0.12.0..v0.13.0) - 2026-03-05
### 🐛  Bug Fixes
- ensure release-check for standalone/project commands [useReq] *(cli)*
  - add reproducer tests for standalone update-check and version-only bypass
  - invoke online release-check for standalone and project-scan flows
  - refresh WORKFLOW.md and REFERENCES.md

## [0.12.0](https://github.com/Ogekuri/useReq/compare/v0.11.0..v0.12.0) - 2026-03-05
### 🐛  Bug Fixes
- add English REQUIREMENS alias [useReq] *(docs)*
  - add docs/REQUIREMENS.md in English\n- point to docs/REQUIREMENTS.md as canonical SRS

### 🚜  Changes
- translate REQUIREMENTS.md to English [useReq] *(requirements)*
  - Translate previously Italian requirement statements to English.
  - Preserve requirement IDs and existing requirement structure.
  - Normalize RFC 2119 keyword casing in edited requirements.
- remove centralized model version metadata [useReq] *(models-config)*
  - update SRS-084 to remove settings.version requirement
  - remove settings.version from models.json and models-legacy.json
  - remove .g.conf version checks for centralized model files

### 📚  Documentation
- Update README.md document.
- align SRS IDs with true-state wrappers [useReq] *(requirements)*
  - reassign duplicate SRS-264 collision to SRS-265\n- align script-path requirements to scripts/ wrappers\n- document missing root doxygen.sh as current limitation\n- add wrapper requirements for scripts/ruff.sh and scripts/pyright.sh

## [0.11.0](https://github.com/Ogekuri/useReq/compare/v0.10.0..v0.11.0) - 2026-03-05
### ⛰️  Features
- Add package.json file.
- Update .req/models.json file.

### 🐛  Bug Fixes
- complete Doxygen tags for source declarations [useReq] *(src-docs)*
  - add missing @details/@param/@return tags across src/usereq modules
  - regenerate docs/REFERENCES.md with updated declaration metadata
  - stabilize references tests by matching log() block by signature
- Fix version numbers.

### 🚜  Changes
- remove mandatory .venv refresh on requirements changes [useReq] *(scripts)*
  - replace SRS-056 with execution-only req.sh requirement
  - remove hash-based .venv recreation logic from req/ruff/pyright scripts
  - align dependency manifest test with updated SRS-056 behavior
  - update WORKFLOW.md runtime descriptions and regenerate REFERENCES.md
- align dependency manifests and venv refresh [useReq] *(deps)*
  - update SRS-055/SRS-056 and add SRS-264 for dependency governance
  - align requirements.txt with pyproject runtime/build dependencies
  - refresh req.sh, ruff.sh, and pyright.sh on requirements hash changes
  - add tests for manifest alignment and runner sync behavior
  - update WORKFLOW.md and regenerate REFERENCES.md
- scope --tokens to canonical docs files [useReq] *(cli)*
  - Update SRS-184 to constrain --tokens file selection.
  - Run --tokens only on REQUIREMENTS.md/WORKFLOW.md/REFERENCES.md.
  - Adjust CLI help and run_tokens Doxygen contract.
  - Refresh CMD-016 token tests and regenerate docs references/workflow.

### 📚  Documentation
- Update src/usereq/resources/docs/Document_Source_Code_in_Doxygen_Style.md file.

## [0.10.0](https://github.com/Ogekuri/useReq/compare/v0.9.0..v0.10.0) - 2026-03-04
### ⛰️  Features
- Update .req/models.json file.

### 📚  Documentation
- Update README.md documenet.

## [0.9.0](https://github.com/Ogekuri/useReq/compare/v0.8.0..v0.9.0) - 2026-03-04
### ⛰️  Features
- Update prompts.

### 🐛  Bug Fixes
- Fix workflow line numbers bug.
- Include .req directory to support worktree.

### 🚜  Changes
- enforce doxygen coverage for nested helpers [useReq] *(source-analyzer)*
  - update SRS-024 to require Doxygen coverage for declarations under src/\n- add missing Doxygen docstrings for nested helper functions\n- regenerate docs/REFERENCES.md for updated symbol metadata\n- verify with req --here --static-check and full tests.sh suite

### 📚  Documentation
- document .req tracking for git worktree [useReq] *(readme)*
  - add an IMPORTANT note in Git usage section\n- require tracking .req/ so worktrees inherit config
- regenerate runtime workflow model [useReq] *(core)*
  - rewrite docs/WORKFLOW.md with parser-stable schema\n- refresh execution unit metadata and lifecycle fields\n- update internal call-trace tree from src evidence\n- record external boundaries and communication-edge evidence

## [0.8.0](https://github.com/Ogekuri/useReq/compare/v0.7.0..v0.8.0) - 2026-03-03
### ⛰️  Features
- Update readme prompt.

## [0.7.0](https://github.com/Ogekuri/useReq/compare/v0.6.0..v0.7.0) - 2026-03-03
### ⛰️  Features
- Update prompts.

### 📚  Documentation
- Update README.md doc.
- Update README.md doc.

## [0.6.0](https://github.com/Ogekuri/useReq/compare/v0.5.0..v0.6.0) - 2026-03-01
### ⛰️  Features
- Update prompts.
- Update prompts.

### 🚜  Changes
- switch markdown metadata prefixes to blockquote [useReq] *(find-compress)*
  - Update SRS-163, SRS-211, and SRS-220 for '> Signature' and '> Lines' metadata format.
  - Implement output changes in find_constructs and compress_files.
  - Adjust affected unit tests and project_examples fixtures.
  - Keep workflow runtime documentation aligned with metadata rendering behavior.
- preserve raw doxygen tags in output [useReq] *(doxygen_parser)*
  - Update SRS-219/SRS-220 and SRS-234..SRS-237 for raw @tag emission.
  - Refactor doxygen field markdown formatter to keep original @tag tokens.
  - Adjust parser/find/references tests to assert no human-readable label conversion.
  - Refresh WORKFLOW and regenerate REFERENCES documentation.

## [0.5.0](https://github.com/Ogekuri/useReq/compare/v0.4.0..v0.5.0) - 2026-02-28
### 📚  Documentation
- Update README.md document.

## [0.4.0](https://github.com/Ogekuri/useReq/compare/v0.3.0..v0.4.0) - 2026-02-28
### ⛰️  Features
- Update prompts with more checks.
- Update prompts.

### 🚜  Changes
- enforce here-only tokens mode [useReq] *(cli)*
  - update SRS-184 for implicit --here and --base rejection on --tokens\n- route --tokens through here-only project-scan gating\n- always load docs-dir from .req/config.json in run_tokens\n- adapt CMD-016 tests to new --tokens behavior\n- update WORKFLOW and regenerate REFERENCES
- use git ls-files for here-only scans [useReq] *(cli)*
  - update requirements for here-only project scans and git-based collection\n- enforce implicit --here and reject --base for references/compress/find/static-check\n- replace project-scan file discovery with git ls-files scoped by configured src-dir\n- adapt command tests to git-backed temp repos and base-rejection semantics\n- update WORKFLOW and regenerate REFERENCES

### 📚  Documentation
- align tokens command semantics [useReq] *(readme)*
  - update --tokens usage to reflect here-only project-scan behavior
  - document implicit --here and explicit --base rejection
  - clarify that explicit --docs-dir is ignored for --tokens
- align project-scan CLI usage [useReq] *(readme)*
  - update --references, --compress, --find, and --static-check usage notes\n- document here-only behavior with implicit --here\n- document --base rejection for project-scan commands\n- clarify project-scan scope as git-tracked files under configured src-dir

## [0.3.0](https://github.com/Ogekuri/useReq/compare/v0.2.0..v0.3.0) - 2026-02-25
### ⛰️  Features
- Update prompts.

### 🐛  Bug Fixes
- Fix .g.conf file.

### 📚  Documentation
- sync configured model names [useReq] *(opencode)*
  - Align OpenCode configured model entries with models.json (gemini-3.1-pro-preview).

## [0.2.0](https://github.com/Ogekuri/useReq/compare/v0.1.0..v0.2.0) - 2026-02-24
### ⛰️  Features
- update prompts. *(core)*
- update models. *(core)*
- add new prompts. *(core)*
- add guidelines. *(core)*
- update prompts and templates. *(core)*
- remove other examples. *(core)*
- update README.md. *(core)*

### 🐛  Bug Fixes
- Fix workflow file. *(core)*
- update .gitignore. *(core)*
- opencode models. *(core)*
- replace req. with req-. *(core)*
- test.sh. *(core)*
- stop cross-function Doxygen leakage [useReq] *(source_analyzer)*
  - treat completed enclosing constructs as blockers when associating preceding comments
  - keep nested/contained comment association behavior intact
  - add regression for parse_args in find_constructs output
  - align fixture expectation helper and regenerate docs/REFERENCES.md
- fix docs/REQUIREMENTS.md. *(core)*
- fix typo on breaking changes. *(core)*

### 🚜  Changes
- align readme prompt mapping with write [useReq] *(models)*
  - Update SRS-085 to require readme prompt model/mode parity with write when write.model exists.
  - Add readme entries to models.json and models-legacy.json for codex, copilot, opencode, claude, and kiro.
  - Add regression tests asserting readme/write parity across bundled model files.
  - Update WORKFLOW.md runtime note for centralized model loading semantics.
- normalize prompt and agent filenames to hyphen style [useReq] *(cli)*
  - Update SRS IDs SRS-090/091/093/099/100/105/106/108 for req-<name> artifact naming.
  - Generate Codex/GitHub/Kiro/Claude/OpenCode prompt and agent files with hyphenated names.
  - Align prompts-use-agents references to agent: req-<name> across providers.
  - Refresh CLI tests for the new artifact names and resource references.
  - Regenerate REFERENCES.md and adjust WORKFLOW.md targeted runtime note.
- stop creating requirements.md in docs-dir [useReq] *(cli)*
  - update SRS-053 to forbid requirements.md generation in --docs-dir
  - keep Requirements_Template validation and copy only to .req/docs
  - adjust REQ-001 tests for empty docs directories
  - refresh WORKFLOW and REFERENCES docs
- enforce packaged resource read-only rules [useReq] *(requirements)*
  - Remove SRS-088 editing-oriented requirement on resources/prompts
  - Add SRS-263 and SRS-264 read-only constraints for packaged resources
  - Add regression tests verifying CLI runs do not modify packaged prompts/docs

### 🎯  Cover Requirements
- enforce fixture doxygen coverage and temp dirs [useReq] *(tests)*
  - replace tmp_path usage with repository temp fixture under temp/tests
  - add deterministic Doxygen helper blocks across all fixtures for SRS-231
  - recalibrate analyzer expected counts for updated fixture corpus

### 📚  Documentation
- align README prompt descriptions [useReq] *(prompts)*
  - sync Prompts and Agents descriptions with packaged prompt metadata
  - keep README structure and non-interface sections unchanged
- fix typos and update model configurations [useReq] *(readme)*
  - Fixed typos: cutomizable, implement, requirements.
  - Updated Gemini 3 Pro to Gemini 3.1 Pro for Copilot and OpenCode.
  - Updated OpenCode models to Claude Opus 4.6 as per models.json evidence.
- update README.md. *(core)*
- align prompt and model tables with implementation [useReq] *(readme)*
  - add missing prompt coverage entries (readme, renumber)\n- add readme model rows across provider configured-model tables\n- correct OpenCode create/workflow model mapping

## [0.1.0](https://github.com/Ogekuri/useReq/releases/tag/v0.1.0) - 2026-02-22
### ⛰️  Features
- verbose commit. *(core)*
- add worktree branch on all promts. *(core)*
- add DataTypes example. *(core)*
- update tests/project_examples. *(core)*
- add @satisfies. *(core)*
- update github workflow. *(core)*
- update github workflow. *(core)*
- add static code check. *(core)*
- add static-check on req-init.sh. *(core)*
- add --enable-static-check, --files-static-check, --static-check commands [2026-02-20 09:55:00] *(static_check)*
  - SRS-248..SRS-262: configurable per-language static analysis (Dummy/Pylance/Ruff/Command)
  - static_check.py: STATIC_CHECK_LANG_CANONICAL, STATIC_CHECK_EXT_TO_LANG, parse_enable_static_check(), dispatch_static_check_for_file()
  - cli.py: --enable-static-check (repeatable, case-insensitive), --files-static-check, --static-check, save_config static-check persistence, load_static_check_from_config()
  - tests/test_static_check.py: 60+ new tests covering parse, dispatch, CLI commands, config persistence
  - docs/REQUIREMENTS.md, WORKFLOW.md, REFERENCES.md updated
  - Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
- max 35 words for requirement. *(core)*
- add --test-static-check with Dummy/Pylance/Ruff/Command classes [2026-02-20 00:00:00] *(static_check)*
  - Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
- add pyright.sh, ruff.sh scripts. *(core)*
- add ruff e pyright. *(core)*
- extend skill generation to resources/skills [2026-02-19 17:30:26] *(cli)*
- add fallback. *(core)*
- remove legacy form scripts. *(core)*
- update models. *(core)*
- add renumber command. *(core)*
- recreate use git to commit new requirements file. *(core)*
- optimize requirements for LLM Agents. *(core)*
- add usage on prompts. *(core)*
- add Usage on prompts. *(core)*
- update for new WORKFLOW.md. *(core)*
- add Source Construct Extraction. *(core)*
- add project_examples_doxygen_occurrence_parity_two_phase_flow test. *(core)*
- move HDT and Doxygen templaste into docs dir. *(core)*
- add --tokens docs-dir token scan command [2026-02-16 07:46:03] *(cli)*
- add REFERENCES.md as source of true. *(core)*
- set English language for WORKFLOW.md. *(core)*
- add REFERENCES.md management and /req.references prompt. *(core)*
- add Google_C++_Style_Guide.md template. *(core)*
- add common scripts. *(core)*
- add SKILLs to codex. *(core)*
- add Google Python Guide *(core)*
- add req/ dir. *(core)*
- tocken optimization. *(core)*
- add /req.implement prompt. *(core)*
- add %%SRC_PATH%% on promtps. *(core)*
- add src-dir support and update specs/tests [2026-02-08 12:07:55] *(cli)*
- add --test-dir support and update specs/tests [2026-02-08 11:27:54] *(cli)*
- add WORKFLOW.md. *(core)*
- add %%DOC_PATH%% on prompts. *(core)*
- add doc-dir support [2026-02-08 10:18:36] *(cli)*
- change WORKFLOW.md logic. *(core)*
- add --write-tech and --overwrite-tech CLI parameters for tech template copy [2026-02-07 17:15:42] *(core)*
- add Professional Personas specifications. *(core)*
- add COMPONENT on commits. *(core)*
- add models.json config. *(core)*
- use text list for global activities and todo list for tasks. *(core)*
- add todo tool fallback if missing. *(core)*
- change models for github copilot. *(core)*
- add worklow command. *(core)*
- add refactor to optimize. *(core)*
- implement --yolo mode. *(core)*
- add --prompts-use-agents. *(core)*
- add WORKFLOW.md management. *(core)*
- Ann --enable-model and --enable-tools for Claude and Kiro. *(core)*
- add --enable-model and --enable-tools for GitHub Copilot. *(core)*
- rename write into create, implement write. *(core)*
- implement new version check. *(core)*
- add Claude Code CLI support. *(core)*
- add OpenCode CLI support. *(core)*
- add support for multiple requirement files and multiple tech dirs. *(core)*
- add preliminary Kiro CLI support. *(core)*
- Initial draft release. *(core)*
- Add analyze and optimize commands. *(core)*

### 🐛  Bug Fixes
- fix prompt to check file's precence before fork the branch. *(core)*
- minor fixes. *(core)*
- restore full multi-line comment Doxygen extraction and add param[in,out] support [COMMIT_DATE_PLACEHOLDER] *(doxygen_parser)*
  - Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
- avoid duplicate default pytest run [2026-02-22 13:47:12] *(tests.sh)*
- preserve multi-line doxygen blocks for cmd_major tests [2026-02-22 12:23:52] *(source_analyzer)*
- restore full doxygen extraction with @satisfies [2026-02-22 12:09:25] *(doxygen_parser)*
- fix workflow. *(core)*
- persist install flags for update reload [2026-02-20 15:51:44] *(cli)*
- fix WORKFLOW.md update. *(core)*
- resolve static-check typing and lint defects [2026-02-20 14:08:07] *(core)*
- minor fixes. *(core)*
- minor fixes. *(core)*
- docs/REQUIREMENTS.md *(core)*
- fix scripts. *(core)*
- minor fix to recreate.md. *(core)*
- fix REFERENCES.md. *(core)*
- minor fixes. *(core)*
- minor fixes to workflow.md. *(core)*
- minor fixes. *(core)*
- include skills/agents in prompts summary [2026-02-19 09:52:36] *(cli)*
- test.sh script. *(core)*
- fix scripts. *(core)*
- fix recreate.md. *(core)*
- minor prompts fixes. *(core)*
- minor prompts fixes. *(core)*
- minor fix. *(core)*
- minor fixes. *(core)*
- minor fixes. *(core)*
- align DOX-018 baselines with command semantics [2026-02-17 14:01:58] *(test_files_commands)*
- scope collection to tests to avoid conftest mismatch [2026-02-17 12:28:53] *(pytest)*
- minor fix on prompts *(core)*
- bundle template files for overwrite copy [2026-02-16 16:07:16] *(guidelines)*
- align fixture count expectations [2026-02-16 14:33:59] *(source_analyzer)*
- scope pytest to tests directory [2026-02-16 10:56:35] *(tests.sh)*
- minor fixes. *(core)*
- fix WORKFLOW.md. *(core)*
- add fallback for legacy config keys doc-dir/test-dir [2026-02-15 17:21:55] *(load_config)*
- narrow run path type handling [2026-02-14 19:13:18] *(cli)*
- normalize base-prefixed relative paths [2026-02-14 18:29:13] *(cli)*
- codex model.json. *(core)*
- minor fixes. *(core)*
- fix tests in prompts. *(core)*
- fix WORKFLOW.md structure. *(core)*
- fix WORKFLOW.md structure. *(core)*
- major fix on prompts. *(core)*
- fix calls on WORKFLOW.md. *(core)*
- fix prompts step numbering. *(core)*
- minor fixes on prompts. *(core)*
- minor fix on create and recreate. *(core)*
- minor fix on prompts. *(core)*
- add %%TEST_PATH%% to prompts. *(core)*
- fix global roadmap. *(core)*
- fix commit language. *(core)*
- fix workflow prompt. *(core)*
- fix on workflow prompt. *(core)*
- fix Professional Personas specifications. *(core)*
- **Global Roadmap** on prompts *(core)*
- change prompts. *(core)*
- promtps changed. *(core)*
- major fix on prompts *(core)*
- minor fixes. *(core)*
- prevent unbound claude metadata [2026-01-27 10:32:37] *(useReq)*
- update **CRITICAL** about project's home writing. *(core)*
- rename Optimize in Refactor *(core)*
- Typo on GPT-5.1-Codex-Mini (Preview) (copilot) *(core)*
- report workflow in summary table [2026-01-25 20:51:19] *(useReq)*
- align install summary header [2026-01-25 20:32:17] *(useReq)*
- change SRS Update and Technical Implementation Records *(core)*
- align install summary table [2026-01-25 20:01:42] *(useReq)*
- fix --enable-workflow help string. *(core)*
- change terminate execution. *(core)*
- change todo list step. *(core)*
- align workflow default test with resource text [2026-01-25 15:48:30] *(useReq)*
- minor fix on workflow. *(core)*
- misc fixes. *(core)*
- major defects fixed. *(core)*
- change models. *(core)*
- change prioritize for change, optimize, new and cover. *(core)*
- major fix opencode. *(core)*
- flowchart. *(core)*
- add images folder. *(core)*
- wait for approval. *(core)*
- use python virtual environment. *(core)*
- change kiro cli json files. *(core)*
- block git write operations. *(core)*
- major fix on templates. *(core)*
- minor fix on templates. *(core)*
- minor change on templates. *(core)*
- minor change on templates. *(core)*
- minor fixes on templates. *(core)*
- update templates/requirements.md. *(core)*
- fix --update command. *(core)*
- version on venv.sh. *(core)*
- version on req.sh. *(core)*

### 🚜  Changes
- export full Doxygen fields in references/find and strengthen tests [2026-02-22 16:26:20] *(doxygen)*
- add regex project_examples files-references parity [2026-02-22 14:18:17] *(test_files_commands)*
- enforce fixture Doxygen file headers [2026-02-22 12:54:06] *(fixtures)*
- add @satisfies extraction support [2026-02-22 11:55:20] *(doxygen_parser)*
- validate Command executable for static-check [2026-02-20 16:27:09] *(cli)*
- fix --update persisted config precedence and validation [2026-02-20 16:11:33] *(cli)*
- add markdown blank separator lines [2026-02-20 13:44:45] *(static_check)*
- remove markdown trailing blank lines [2026-02-20 13:33:42] *(static_check)*
- support multi-module arrays in config [2026-02-20 13:17:36] *(static-check)*
- support quoted comma params in enable parser [2026-02-20 11:54:56] *(static-check)*
- update comma-separated spec parsing [2026-02-20 11:41:19] *(static-check)*
- use '#' as SPEC separator in --enable-static-check to avoid bash ';' conflict [2026-02-20 11:30:51] *(static_check)*
  - SRS-248, SRS-250, SRS-260: replace ';' separator with '#' in LANG=MODULE[#CMD[#PARAM...]] format
  - src/usereq/static_check.py: split on '#' in parse_enable_static_check; update docstring and error messages
  - src/usereq/cli.py: update --enable-static-check help text and example to '#' separator
  - tests/test_static_check.py: update all SPEC strings and descriptions to '#' separator
  - docs/REFERENCES.md: regenerated
- use ';' as SPEC separator in --enable-static-check to allow comma-containing params [2026-02-20 11:13:47] *(static_check)*
  - SRS-248/SRS-250/SRS-260: SPEC format changed from LANG=MODULE[,CMD[,PARAM...]] to LANG=MODULE[;CMD[;PARAM...]]
  - src/usereq/static_check.py: parse_enable_static_check splits on ';', error messages and docstring updated
  - tests/test_static_check.py: updated Command module tests to ';'; added test_command_module_param_with_comma
  - docs/REQUIREMENTS.md: SRS-248, SRS-250, SRS-260 updated to reflect semicolon separator
  - docs/REFERENCES.md: regenerated
- remove --recursive flag; use ** glob for recursive resolution [2026-02-20 09:47:53] *(static_check)*
  - SRS-240/245: remove --recursive custom flag from Dummy/Pylance/Ruff/Command
  - _resolve_files: remove recursive param; glob always uses recursive=True (** support)
  - StaticCheckBase/Command: remove recursive constructor param and _recursive attr
  - run_static_check: no --recursive extraction; all tokens passed as FILES
  - cli.py: remove [--recursive] from usage/help strings
  - tests: replace --recursive tests with ** glob test; update _resolve_files call sites
- remove resources/skills from skill generation [2026-02-19 17:40:54] *(cli)*
- use project-relative paths in references/compress output [2026-02-19 12:23:34] *(cli)*
- default-enable skills with --disable-skills [2026-02-19 09:23:09] *(cli)*
- generate skills as req-<prompt> dirs [2026-02-19 08:13:27] *(skills)*
- derive SKILL.md description from prompt usage [2026-02-18 16:50:50] *(skills)*
- add SKILL.md generation for all CLI providers with skill description from sections [2026-02-18 16:10:07] *(cli)*
- add --enable-prompts, --enable-agents, --enable-skills artifact-type flags [2026-02-18 15:51:06] *(cli)*
  - SRS: add SRS-231, update SRS-030/034/035/089/090-111 to define three new
  - artifact-type flags and enforce at least one is required (exit code 4)
  - cli.py: register --enable-prompts/--enable-agents/--enable-skills in
  - build_parser(); validate in run(); gate all artifact generation with
  - compound provider+artifact-type conditions
  - tests: add ARTIFACT_TYPE_FLAGS constant; update all inline cli.main()
  - calls; add TestArtifactTypeFlags class with 5 new test cases
  - docs: update WORKFLOW.md, regenerate REFERENCES.md
  - Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
- add root doxygen generator and docs updates [2026-02-17 15:22:33] *(doxygen)*
- remove remaining legacy doc references [2026-02-17 15:05:28] *(core)*
- remove legacy doc generator and align docs [2026-02-17 15:04:49] *(core)*
- strip comments in --find and --files-find output [2026-02-17 14:37:01] *(find_constructs)*
- enforce semantic doxygen fields in references [2026-02-17 14:20:31] *(source_analyzer)*
- enforce fixture Doxygen parity in find tests [2026-02-17 12:14:10] *(find-commands)*
- align doxygen reference count tests with fixtures [2026-02-17 12:00:27] *(test_files_commands)*
- aggregate doxygen fields and extend find tests [2026-02-17 11:51:06] *(find_constructs)*
- enforce ordered Doxygen output and update tests/spec [2026-02-17 11:40:52] *(references)*
- validate doxygen fixture extraction [2026-02-17 11:25:26] *(source_analyzer)*
- expand parser test matrix and specs [2026-02-17 11:13:49] *(doxygen-parser)*
- enhance fixtures with comprehensive Doxygen documentation [2026-02-17 10:57:00] *(tests)*
  - Updated test fixtures to meet DOX-008 and FND-014 requirements:
  - Added inline Doxygen documentation to Python fixture (8 tags)
  - Added file-level documentation to Go fixture
  - Updated test expectations for new comment element counts
  - All 1362 tests passing
  - Implements requirements:
  - DOX-008: Comprehensive Doxygen tags on fixture constructs
  - FND-014: Heterogeneous comment styles (inline, multi-line)
  - Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
- add Doxygen parser module with integration into source analyzer and output commands [2026-02-17 10:36:12] *(core)*
- update source_analyzer output format to Markdown tables and fix tests [2026-02-17 09:43:41] *(core)*
- rename copy-guidelines to upgrade-guidelines [2026-02-16 16:27:24] *(cli)*
- restore copy-guidelines option and align tests [2026-02-16 16:21:41] *(cli)*
- support empty template source and remove defaults [2026-02-16 16:12:29] *(guidelines)*
- rename docs template and dynamic req docs copy [2026-02-16 15:59:47] *(cli)*
- enforce five extractions per tag [2026-02-16 14:04:02] *(test_find_constructs_comprehensive)*
- expand multi-language construct fixtures and coverage [2026-02-16 13:58:36] *(fixtures)*
- rename template paths to docs [2026-02-16 13:48:12] *(cli)*
- switch line prefixes to nn: across outputs [2026-02-16 13:41:08] *(compress)*
- invert line-number flag defaults [2026-02-16 13:35:55] *(cli)*
- add lines header and fenced compress output [2026-02-16 13:28:59] *(compress_files)*
- extract complete constructs without truncation [$DATE] *(find_constructs)*
  - Updated --files-find and --find commands to extract COMPLETE constructs
  - from source files instead of truncated snippets. Changes include:
  - Requirements (docs/REQUIREMENTS.md):
  - FND-005: Updated to specify reading complete construct from source file
  - FND-006: Updated to specify no truncation or snippet limitations
  - REQ-100: Updated to verify complete extraction in tests
  - Source code (src/usereq/find_constructs.py):
  - format_construct(): Added source_lines parameter to read complete code
  - find_constructs_in_files(): Reads complete source file and passes to formatter
  - Tests (tests/):
  - test_find_constructs.py: Updated to pass source_lines to format_construct
  - test_find_constructs_comprehensive.py: Added tests for complete extraction
  - Documentation:
  - docs/WORKFLOW.md: Updated format_construct description
  - docs/REFERENCES.md: Regenerated with updated signatures
  - Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
- enforce --here config path precedence [2026-02-16 12:16:35] *(cli)*
- gate scan progress logs behind --verbose [2026-02-16 12:01:09] *(cli)*
- add dynamic TAG listing in help and error messages [2026-02-16 11:54:46] *(find_constructs)*
- add comprehensive unit tests for find_constructs covering all language-construct combinations [2026-02-16 11:47:21] *(tests)*
  - Added tests/test_find_constructs_comprehensive.py with 54 tests validating construct extraction
  - Updated docs/REQUIREMENTS.md to version 0.67 with new requirement REQ-100
  - Updated docs/WORKFLOW.md with comprehensive test feature documentation
  - Updated docs/REFERENCES.md with regenerated source references
  - Validates extraction of all construct types defined in FND-002 for all 20 supported languages
  - using fixture files in tests/fixtures/. Tests verify correct identification and extraction of
  - constructs matching tag filters and regex patterns across Python, C, C++, Rust, JavaScript,
  - TypeScript, Java, Go, Ruby, PHP, Swift, Kotlin, Scala, Lua, Shell, Perl, Haskell, Zig, Elixir, C#.
- add --files-find and --find commands for construct extraction [2026-02-16 11:38:48] *(cli)*
  - Add new find_constructs module for filtering source constructs by tag and regex pattern
  - Implement --files-find TAG PATTERN FILE... for standalone file lists
  - Implement --find TAG PATTERN for project source directories
  - Support 20 languages with comprehensive TAG mapping (CLASS, FUNCTION, STRUCT, etc.)
  - Support --disable-line-numbers flag for both commands
  - Add test coverage with 12 unit tests
  - Update REQUIREMENTS.md v0.66 with FND-001..011, CMD-018..028
  - Update WORKFLOW.md with new command workflows and function call traces
  - Update REFERENCES.md with find_constructs module documentation
  - Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
- add disable-line-numbers support for compression [2026-02-16 11:15:36] *(cli)*
- add parity analyzer tests and requirements update [2026-02-16 10:48:11] *(tests/source_analyzer)*
- prepend files structure in --references [2026-02-15 19:45:56] *(cli)*
- remove doc-comment reqs and normalize doxygen docs [2026-02-15 19:31:18] *(core)*
- regenerate references after doxygen updates [2026-02-15 19:20:19] *(references)*
- rename guidelines copy flags [2026-02-14 18:55:48] *(cli)*
- rename docs/tests dir flags and update specs/tests [2026-02-14 18:42:42] *(cli)*
- remove --req-dir and req token handling [2026-02-14 18:14:30] *(cli)*
- add codex skills generation [2026-02-13 16:06:16] *(cli)*
- format %%TEST_PATH%% with backticks [2026-02-08 11:43:18] *(cli)*
- enforce %%TEST_PATH%% trailing slash [2026-02-08 11:35:50] *(cli)*
- ignore dotfiles, update specs/tests [2026-02-08 10:34:42] *(cli)*
- update TECH_PATH replacement and specs/tests [2026-02-08 09:45:30] *(cli)*
- remove workflow flag logic and update specs/tests [2026-02-07 19:45:51] *(cli)*
- refactor deep parameter and function renaming [$(date +"%Y-%m-%d %H:%M:%S")] *(core)*
  - Renamed CLI parameters: --doc to --req-dir, --dir to --tech-dir. Updated config.json fields from doc/dir to req-dir/tech-dir. Renamed functions: generate_doc_file_list to generate_req_file_list, generate_dir_list to generate_tech_file_list (now scans files instead of subdirectories, with fallback to directory name if empty). Updated all requirements, tests, and workflow documentation to reflect these changes. No backward compatibility implemented as per requirements.
  - Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
- add recreate prompt and align configs/tests *(useReq)*
- record prompts in install summary table [2026-01-26 14:10:43] *(useReq)*
- Rename 'optimize' prompt to 'refactor' and update configurations and tests [2026-01-26 12:27:00] *(useReq)*
- print discovered REQ_DOC files and REQ_DIR folders after install; update REQ-078 and bump version to 0.43 [2026-01-25 20:43:09] *(useReq)*
- include installation modules table in final message; update requirements and tests [2026-01-25 19:36:10] *(useReq)*
- Make workflow prompt generation conditional on --enable-workflow; adjust recommendations and tests [2026-01-25 19:31:42] *(useReq)*
- add workflow prompt models to provider configs and update requirements [2026-01-25 19:04:06] *(useReq)*
- Add final installation success message in CLI and update requirements/tests [2026-01-25 17:36:52] *(useReq)*
- extract workflow strings to resources/common and load them from files [2026-01-25 11:32:01] *(useReq)*
- remove obsolete bootstrap test and update requirements revision [fb8f2113-4a6a-4f23-a0d0-0c5db444338b] *(useReq)*
- fix all prompts. *(core)*

### ✨  Refactor
- complete prompts refactory. *(core)*
- major changes on command line parameters. *(core)*

### 📚  Documentation
- review README.md. *(core)*
- Review README.md. *(core)*
- recreate SRS ID stability rules [2026-02-19 15:17:54] *(core)*
- recreate and renumber SRS [2026-02-19 14:36:33] *(requirements)*
- update README.md. *(core)*
- Update all documentation. *(core)*
- Update requirements. *(core)*
- update README.md. *(core)*
- add generated call-tree workflow [2026-02-15 19:07:20] *(workflow)*
- regenerate code references document [2026-02-15 18:58:58] *(references)*
- regenerate call-tree workflow specification [2026-02-15 18:56:13] *(workflow)*
- update WORKFLOW.md with detailed call tree [2026-02-09 10:18:10] *(core)*
- documented CLI execution workflow [2026-02-09 08:17:19] *(usereq/cli)*
- Update workflow analysis based on current source code [2026-02-08 19:00:42] *(docs)*
- recreate tested on requirements.md. *(core)*
- update docs with recreate. *(core)*
- update README.md. *(core)*
- update Mermaid flowchart. *(core)*
- add tech dir. *(core)*
- add WORKFLOW.md. *(core)*
- update README.md. *(core)*
- update README.md. *(core)*
- update README.md *(core)*
- update README.md. *(core)*
- update README.md. *(core)*
- update README.md. *(core)*
- update README.md. *(core)*
- update README.md. *(core)*
- update README.md. *(core)*
- update flowchart link. *(core)*
- update flowchart link. *(core)*
- update flowchart. *(core)*
- update flowchart. *(core)*
- update flowchart. *(core)*
- update flowchart. *(core)*
- update flowchart. *(core)*
- update README.md. *(core)*
- update Kiro CLI infos. *(core)*
- update README.md and TODO.md files. *(core)*
- Improve English in README.md and TODO.md
- update README.md file. *(core)*
- edit README.md *(core)*
- aggiornato TODO.md. *(core)*


# History

- \[0.1.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.1.0
- \[0.2.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.2.0
- \[0.3.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.3.0
- \[0.4.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.4.0
- \[0.5.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.5.0
- \[0.6.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.6.0
- \[0.7.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.7.0
- \[0.8.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.8.0
- \[0.9.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.9.0
- \[0.10.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.10.0
- \[0.11.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.11.0
- \[0.12.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.12.0
- \[0.13.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.13.0
- \[0.14.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.14.0
- \[0.15.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.15.0
- \[0.16.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.16.0
- \[0.17.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.17.0
- \[0.18.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.18.0
- \[0.19.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.19.0
- \[0.20.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.20.0
- \[0.21.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.21.0

[0.1.0]: https://github.com/Ogekuri/useReq/releases/tag/v0.1.0
[0.2.0]: https://github.com/Ogekuri/useReq/compare/v0.1.0..v0.2.0
[0.3.0]: https://github.com/Ogekuri/useReq/compare/v0.2.0..v0.3.0
[0.4.0]: https://github.com/Ogekuri/useReq/compare/v0.3.0..v0.4.0
[0.5.0]: https://github.com/Ogekuri/useReq/compare/v0.4.0..v0.5.0
[0.6.0]: https://github.com/Ogekuri/useReq/compare/v0.5.0..v0.6.0
[0.7.0]: https://github.com/Ogekuri/useReq/compare/v0.6.0..v0.7.0
[0.8.0]: https://github.com/Ogekuri/useReq/compare/v0.7.0..v0.8.0
[0.9.0]: https://github.com/Ogekuri/useReq/compare/v0.8.0..v0.9.0
[0.10.0]: https://github.com/Ogekuri/useReq/compare/v0.9.0..v0.10.0
[0.11.0]: https://github.com/Ogekuri/useReq/compare/v0.10.0..v0.11.0
[0.12.0]: https://github.com/Ogekuri/useReq/compare/v0.11.0..v0.12.0
[0.13.0]: https://github.com/Ogekuri/useReq/compare/v0.12.0..v0.13.0
[0.14.0]: https://github.com/Ogekuri/useReq/compare/v0.13.0..v0.14.0
[0.15.0]: https://github.com/Ogekuri/useReq/compare/v0.14.0..v0.15.0
[0.16.0]: https://github.com/Ogekuri/useReq/compare/v0.15.0..v0.16.0
[0.17.0]: https://github.com/Ogekuri/useReq/compare/v0.16.0..v0.17.0
[0.18.0]: https://github.com/Ogekuri/useReq/compare/v0.17.0..v0.18.0
[0.19.0]: https://github.com/Ogekuri/useReq/compare/v0.18.0..v0.19.0
[0.20.0]: https://github.com/Ogekuri/useReq/compare/v0.19.0..v0.20.0
[0.21.0]: https://github.com/Ogekuri/useReq/compare/v0.20.0..v0.21.0
