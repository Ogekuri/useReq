# Changelog

## [0.0.70](https://github.com/Ogekuri/useReq/compare/v0.0.69..v0.0.70) - 2026-02-16
### ⛰️  Features
- *(core)* move HDT and Doxygen templaste into docs dir.
- *(cli)* add --tokens docs-dir token scan command [2026-02-16 07:46:03]

### 🐛  Bug Fixes
- *(guidelines)* bundle template files for overwrite copy [2026-02-16 16:07:16]
- *(source_analyzer)* align fixture count expectations [2026-02-16 14:33:59]
- *(tests.sh)* scope pytest to tests directory [2026-02-16 10:56:35]

### 🚜  Changes
- *(cli)* rename copy-guidelines to upgrade-guidelines [2026-02-16 16:27:24]
- *(cli)* restore copy-guidelines option and align tests [2026-02-16 16:21:41]
- *(guidelines)* support empty template source and remove defaults [2026-02-16 16:12:29]
- *(cli)* rename docs template and dynamic req docs copy [2026-02-16 15:59:47]
- *(test_find_constructs_comprehensive)* enforce five extractions per tag [2026-02-16 14:04:02]
- *(fixtures)* expand multi-language construct fixtures and coverage [2026-02-16 13:58:36]
- *(cli)* rename template paths to docs [2026-02-16 13:48:12]
- *(compress)* switch line prefixes to nn: across outputs [2026-02-16 13:41:08]
- *(cli)* invert line-number flag defaults [2026-02-16 13:35:55]
- *(compress_files)* add lines header and fenced compress output [2026-02-16 13:28:59]
- *(find_constructs)* extract complete constructs without truncation [$DATE]
- *(cli)* enforce --here config path precedence [2026-02-16 12:16:35]
- *(cli)* gate scan progress logs behind --verbose [2026-02-16 12:01:09]
- *(find_constructs)* add dynamic TAG listing in help and error messages [2026-02-16 11:54:46]
- *(tests)* add comprehensive unit tests for find_constructs covering all language-construct combinations [2026-02-16 11:47:21]
- *(cli)* add --files-find and --find commands for construct extraction [2026-02-16 11:38:48]
- *(cli)* add disable-line-numbers support for compression [2026-02-16 11:15:36]
- *(tests/source_analyzer)* add parity analyzer tests and requirements update [2026-02-16 10:48:11]

## [0.0.69](https://github.com/Ogekuri/useReq/compare/v0.0.68..v0.0.69) - 2026-02-15
### ⛰️  Features
- *(core)* add REFERENCES.md as source of true.
- *(core)* set **English language** for WORKFLOW.md.
- *(core)* add REFERENCES.md management and /req.references prompt.

### 🐛  Bug Fixes
- *(core)* minor fixes.
- *(core)* fix WORKFLOW.md.
- *(load_config)* add fallback for legacy config keys doc-dir/test-dir [2026-02-15 17:21:55]

### 🚜  Changes
- *(cli)* prepend files structure in --references [2026-02-15 19:45:56]
- *(core)* remove doc-comment reqs and normalize doxygen docs [2026-02-15 19:31:18]
- *(references)* regenerate references after doxygen updates [2026-02-15 19:20:19]

### 📚  Documentation
- *(core)* update README.md.
- *(workflow)* add generated call-tree workflow [2026-02-15 19:07:20]
- *(references)* regenerate code references document [2026-02-15 18:58:58]
- *(workflow)* regenerate call-tree workflow specification [2026-02-15 18:56:13]

## [0.0.68](https://github.com/Ogekuri/useReq/compare/v0.0.67..v0.0.68) - 2026-02-14
### ⛰️  Features
- *(core)* add Google_C++_Style_Guide.md template.
- *(core)* add common scripts.
- *(core)* add SKILLs to codex.
- *(core)* add Google Python Guide
- *(core)* add req/ dir.
- *(core)* tocken optimization.
- *(core)* add /req.implement prompt.
- *(core)* add %%SRC_PATH%% on promtps.
- *(cli)* add src-dir support and update specs/tests [2026-02-08 12:07:55]
- *(cli)* add --test-dir support and update specs/tests [2026-02-08 11:27:54]
- *(core)* add WORKFLOW.md.
- *(core)* add %%DOC_PATH%% on prompts.
- *(cli)* add doc-dir support [2026-02-08 10:18:36]
- *(core)* change WORKFLOW.md logic.
- *(core)* add --write-tech and --overwrite-tech CLI parameters for tech template copy [2026-02-07 17:15:42]

### 🐛  Bug Fixes
- *(cli)* narrow run path type handling [2026-02-14 19:13:18]
- *(cli)* normalize base-prefixed relative paths [2026-02-14 18:29:13]
- *(core)* codex model.json.
- *(core)* minor fixes.
- *(core)* fix tests in prompts.
- *(core)* fix WORKFLOW.md structure.
- *(core)* fix WORKFLOW.md structure.
- *(core)* major fix on prompts.
- *(core)* fix calls on WORKFLOW.md.
- *(core)* fix prompts step numbering.
- *(core)* minor fixes on prompts.
- *(core)* minor fix on create and recreate.
- *(core)* minor fix on prompts.
- *(core)* add %%TEST_PATH%% to prompts.
- *(core)* fix global roadmap.
- *(core)* fix commit language.
- *(core)* fix workflow prompt.
- *(core)* fix on workflow prompt.

### 🚜  Changes
- *(cli)* rename guidelines copy flags [2026-02-14 18:55:48]
- *(cli)* rename docs/tests dir flags and update specs/tests [2026-02-14 18:42:42]
- *(cli)* remove --req-dir and req token handling [2026-02-14 18:14:30]
- *(cli)* add codex skills generation [2026-02-13 16:06:16]
- *(cli)* format %%TEST_PATH%% with backticks [2026-02-08 11:43:18]
- *(cli)* enforce %%TEST_PATH%% trailing slash [2026-02-08 11:35:50]
- *(cli)* ignore dotfiles, update specs/tests [2026-02-08 10:34:42]
- *(cli)* update TECH_PATH replacement and specs/tests [2026-02-08 09:45:30]
- *(cli)* remove workflow flag logic and update specs/tests [2026-02-07 19:45:51]
- *(core)* refactor deep parameter and function renaming [$(date +"%Y-%m-%d %H:%M:%S")]

### ✨  Refactor
- *(core)* complete prompts refactory.
- *(core)* major changes on command line parameters.

### 📚  Documentation
- *(core)* update WORKFLOW.md with detailed call tree [2026-02-09 10:18:10]
- *(usereq/cli)* documented CLI execution workflow [2026-02-09 08:17:19]
- *(docs)* Update workflow analysis based on current source code [2026-02-08 19:00:42]

## [0.0.67](https://github.com/Ogekuri/useReq/compare/v0.0.66..v0.0.67) - 2026-02-04
### 🐛  Bug Fixes
- *(core)* fix Professional Personas specifications.

## [0.0.66](https://github.com/Ogekuri/useReq/compare/v0.0.65..v0.0.66) - 2026-02-04
### ⛰️  Features
- *(core)* add Professional Personas specifications.
- *(core)* add COMPONENT on commits.

## [0.0.65](https://github.com/Ogekuri/useReq/compare/v0.0.64..v0.0.65) - 2026-02-04
### ⛰️  Features
- *(core)* add models.json config.

## [0.0.64](https://github.com/Ogekuri/useReq/compare/v0.0.63..v0.0.64) - 2026-01-31
### 🐛  Bug Fixes
- *(core)* **Global Roadmap** on prompts

## [0.0.63](https://github.com/Ogekuri/useReq/compare/v0.0.62..v0.0.63) - 2026-01-31
### ⛰️  Features
- *(core)* use text list for global activities and todo list for tasks.

## [0.0.62](https://github.com/Ogekuri/useReq/compare/v0.0.61..v0.0.62) - 2026-01-31
### ⛰️  Features
- *(core)* add todo tool fallback if missing.

## [0.0.61](https://github.com/Ogekuri/useReq/compare/v0.0.60..v0.0.61) - 2026-01-30
### 🐛  Bug Fixes
- *(core)* change prompts.
- *(core)* promtps changed.
- *(core)* major fix on prompts

## [0.0.60](https://github.com/Ogekuri/useReq/compare/v0.0.59..v0.0.60) - 2026-01-27
### 🐛  Bug Fixes
- *(core)* minor fixes.
- *(useReq)* prevent unbound claude metadata [2026-01-27 10:32:37]
- *(core)* update **CRITICAL** about project's home writing.

### 🚜  Changes
- *(useReq)* add recreate prompt and align configs/tests

### 📚  Documentation
- *(core)* recreate tested on requirements.md.
- *(core)* update docs with recreate.

## [0.0.59](https://github.com/Ogekuri/useReq/compare/v0.0.58..v0.0.59) - 2026-01-26
### ⛰️  Features
- *(core)* change models for github copilot.

### 🐛  Bug Fixes
- *(core)* rename Optimize in Refactor
- *(core)* Typo on GPT-5.1-Codex-Mini (Preview) (copilot)
- *(useReq)* report workflow in summary table [2026-01-25 20:51:19]
- *(useReq)* align install summary header [2026-01-25 20:32:17]
- *(core)* change SRS Update and Technical Implementation Records
- *(useReq)* align install summary table [2026-01-25 20:01:42]
- *(core)* fix --enable-workflow help string.

### 🚜  Changes
- *(useReq)* record prompts in install summary table [2026-01-26 14:10:43]
- *(useReq)* Rename 'optimize' prompt to 'refactor' and update configurations and tests [2026-01-26 12:27:00]
- *(useReq)* print discovered REQ_DOC files and REQ_DIR folders after install; update REQ-078 and bump version to 0.43 [2026-01-25 20:43:09]
- *(useReq)* include installation modules table in final message; update requirements and tests [2026-01-25 19:36:10]
- *(useReq)* Make workflow prompt generation conditional on --enable-workflow; adjust recommendations and tests [2026-01-25 19:31:42]

### 📚  Documentation
- *(core)* update README.md.
- *(core)* update Mermaid flowchart.

## [0.0.58](https://github.com/Ogekuri/useReq/compare/v0.0.57..v0.0.58) - 2026-01-25
### ⛰️  Features
- *(core)* add worklow command.

### 🚜  Changes
- *(useReq)* add workflow prompt models to provider configs and update requirements [2026-01-25 19:04:06]

## [0.0.57](https://github.com/Ogekuri/useReq/compare/v0.0.56..v0.0.57) - 2026-01-25
### 🐛  Bug Fixes
- *(core)* change terminate execution.

### 🚜  Changes
- *(useReq)* Add final installation success message in CLI and update requirements/tests [2026-01-25 17:36:52]

## [0.0.56](https://github.com/Ogekuri/useReq/compare/v0.0.55..v0.0.56) - 2026-01-25
### ⛰️  Features
- *(core)* add refactor to optimize.

### 🐛  Bug Fixes
- *(core)* change todo list step.
- *(useReq)* align workflow default test with resource text [2026-01-25 15:48:30]
- *(core)* minor fix on workflow.
- *(core)* misc fixes.

### 🚜  Changes
- *(useReq)* extract workflow strings to resources/common and load them from files [2026-01-25 11:32:01]

### 📚  Documentation
- *(core)* add tech dir.

## [0.0.55](https://github.com/Ogekuri/useReq/compare/v0.0.54..v0.0.55) - 2026-01-24
### 🚜  Changes
- *(useReq)* remove obsolete bootstrap test and update requirements revision [fb8f2113-4a6a-4f23-a0d0-0c5db444338b]

## [0.0.54](https://github.com/Ogekuri/useReq/compare/v0.0.53..v0.0.54) - 2026-01-20
### ⛰️  Features
- *(core)* implement --yolo mode.

## [0.0.53](https://github.com/Ogekuri/useReq/compare/v0.0.52..v0.0.53) - 2026-01-19
### ⛰️  Features
- *(core)* add --prompts-use-agents.

## [0.0.52](https://github.com/Ogekuri/useReq/compare/v0.0.51..v0.0.52) - 2026-01-17
### ⛰️  Features
- *(core)* add WORKFLOW.md management.

## [0.0.51](https://github.com/Ogekuri/useReq/compare/v0.0.50..v0.0.51) - 2026-01-16
### 📚  Documentation
- *(core)* add WORKFLOW.md.

## [0.0.50](https://github.com/Ogekuri/useReq/compare/v0.0.49..v0.0.50) - 2026-01-15
### 📚  Documentation
- *(core)* update README.md.

## [0.0.49](https://github.com/Ogekuri/useReq/compare/v0.0.48..v0.0.49) - 2026-01-15
### 📚  Documentation
- *(core)* update README.md.

## [0.0.48](https://github.com/Ogekuri/useReq/compare/v0.0.47..v0.0.48) - 2026-01-15
### 🐛  Bug Fixes
- *(core)* major defects fixed.

## [0.0.47](https://github.com/Ogekuri/useReq/compare/v0.0.46..v0.0.47) - 2026-01-14
### ⛰️  Features
- *(core)* Ann --enable-model and --enable-tools for Claude and Kiro.

## [0.0.46](https://github.com/Ogekuri/useReq/compare/v0.0.45..v0.0.46) - 2026-01-14
### 🐛  Bug Fixes
- *(core)* change models.

## [0.0.45](https://github.com/Ogekuri/useReq/compare/v0.0.44..v0.0.45) - 2026-01-14
### 📚  Documentation
- *(core)* update README.md

## [0.0.44](https://github.com/Ogekuri/useReq/compare/v0.0.43..v0.0.44) - 2026-01-14
### ⛰️  Features
- *(core)* add --enable-model and --enable-tools for GitHub Copilot.

## [0.0.43](https://github.com/Ogekuri/useReq/compare/v0.0.42..v0.0.43) - 2026-01-13
### 🐛  Bug Fixes
- *(core)* change prioritize for change, optimize, new and cover.

## [0.0.42](https://github.com/Ogekuri/useReq/compare/v0.0.41..v0.0.42) - 2026-01-12
### ⛰️  Features
- *(core)* rename write into create, implement write.

## [0.0.41](https://github.com/Ogekuri/useReq/compare/v0.0.40..v0.0.41) - 2026-01-12
### 📚  Documentation
- *(core)* update README.md.

## [0.0.40](https://github.com/Ogekuri/useReq/compare/v0.0.39..v0.0.40) - 2026-01-11
### ⛰️  Features
- *(core)* implement new version check.

## [0.0.39](https://github.com/Ogekuri/useReq/compare/v0.0.38..v0.0.39) - 2026-01-11
### 🐛  Bug Fixes
- *(core)* major fix opencode.

## [0.0.38](https://github.com/Ogekuri/useReq/compare/v0.0.37..v0.0.38) - 2026-01-11
### 📚  Documentation
- *(core)* update README.md.

## [0.0.37](https://github.com/Ogekuri/useReq/compare/v0.0.36..v0.0.37) - 2026-01-11
### 📚  Documentation
- *(core)* update README.md.

## [0.0.36](https://github.com/Ogekuri/useReq/compare/v0.0.35..v0.0.36) - 2026-01-11
### 📚  Documentation
- *(core)* update README.md.

## [0.0.35](https://github.com/Ogekuri/useReq/compare/v0.0.34..v0.0.35) - 2026-01-11
### 🐛  Bug Fixes
- *(core)* flowchart.

## [0.0.34](https://github.com/Ogekuri/useReq/compare/v0.0.33..v0.0.34) - 2026-01-11
### 🐛  Bug Fixes
- *(core)* add images folder.

## [0.0.33](https://github.com/Ogekuri/useReq/compare/v0.0.32..v0.0.33) - 2026-01-10
### 📚  Documentation
- *(core)* update README.md.

## [0.0.32](https://github.com/Ogekuri/useReq/compare/v0.0.31..v0.0.32) - 2026-01-10
### 📚  Documentation
- *(core)* update README.md.

## [0.0.31](https://github.com/Ogekuri/useReq/compare/v0.0.30..v0.0.31) - 2026-01-10
### 📚  Documentation
- *(core)* update flowchart link.

## [0.0.30](https://github.com/Ogekuri/useReq/compare/v0.0.29..v0.0.30) - 2026-01-10
### 📚  Documentation
- *(core)* update flowchart link.

## [0.0.29](https://github.com/Ogekuri/useReq/compare/v0.0.28..v0.0.29) - 2026-01-10
### 📚  Documentation
- *(core)* update flowchart.

## [0.0.28](https://github.com/Ogekuri/useReq/compare/v0.0.27..v0.0.28) - 2026-01-10
### 📚  Documentation
- *(core)* update flowchart.

## [0.0.27](https://github.com/Ogekuri/useReq/compare/v0.0.26..v0.0.27) - 2026-01-10
### 📚  Documentation
- *(core)* update flowchart.

## [0.0.26](https://github.com/Ogekuri/useReq/compare/v0.0.25..v0.0.26) - 2026-01-10
### 📚  Documentation
- *(core)* update flowchart.

## [0.0.25](https://github.com/Ogekuri/useReq/compare/v0.0.24..v0.0.25) - 2026-01-10
### 📚  Documentation
- *(core)* update flowchart.

## [0.0.24](https://github.com/Ogekuri/useReq/compare/v0.0.23..v0.0.24) - 2026-01-10
### ⛰️  Features
- *(core)* add Claude Code CLI support.

## [0.0.23](https://github.com/Ogekuri/useReq/compare/v0.0.22..v0.0.23) - 2026-01-09
### 🐛  Bug Fixes
- *(core)* wait for approval.

## [0.0.22](https://github.com/Ogekuri/useReq/compare/v0.0.21..v0.0.22) - 2026-01-09
### 📚  Documentation
- *(core)* update README.md.

## [0.0.21](https://github.com/Ogekuri/useReq/compare/v0.0.20..v0.0.21) - 2026-01-09
### ⛰️  Features
- *(core)* add OpenCode CLI support.

## [0.0.20](https://github.com/Ogekuri/useReq/compare/v0.0.19..v0.0.20) - 2026-01-09
### 🐛  Bug Fixes
- *(core)* use python virtual environment.

## [0.0.19](https://github.com/Ogekuri/useReq/compare/v0.0.18..v0.0.19) - 2026-01-09
### 📚  Documentation
- *(core)* update Kiro CLI infos.

## [0.0.18](https://github.com/Ogekuri/useReq/compare/v0.0.17..v0.0.18) - 2026-01-09
### 🐛  Bug Fixes
- *(core)* change kiro cli json files.

## [0.0.17](https://github.com/Ogekuri/useReq/compare/v0.0.16..v0.0.17) - 2026-01-09
### 🐛  Bug Fixes
- *(core)* block git write operations.

## [0.0.14](https://github.com/Ogekuri/useReq/compare/v0.0.13..v0.0.14) - 2026-01-07
### 🐛  Bug Fixes
- *(core)* major fix on templates.

## [0.0.13](https://github.com/Ogekuri/useReq/compare/v0.0.12..v0.0.13) - 2026-01-05
### 🐛  Bug Fixes
- *(core)* minor fix on templates.

## [0.0.12](https://github.com/Ogekuri/useReq/compare/v0.0.11..v0.0.12) - 2026-01-04
### 🐛  Bug Fixes
- *(core)* minor change on templates.
- *(core)* minor change on templates.

## [0.0.11](https://github.com/Ogekuri/useReq/compare/v0.0.10..v0.0.11) - 2026-01-04
### 🐛  Bug Fixes
- *(core)* minor fixes on templates.

## [0.0.10](https://github.com/Ogekuri/useReq/compare/v0.0.9..v0.0.10) - 2026-01-03
### 🐛  Bug Fixes
- *(core)* update templates/requirements.md.

## [0.0.9](https://github.com/Ogekuri/useReq/compare/v0.0.8..v0.0.9) - 2026-01-02
### 🐛  Bug Fixes
- *(core)* fix --update command.

## [0.0.8](https://github.com/Ogekuri/useReq/compare/v0.0.7..v0.0.8) - 2026-01-02
### 🐛  Bug Fixes
- *(core)* version on venv.sh.
- *(core)* version on req.sh.

### 📚  Documentation
- *(core)* update README.md and TODO.md files.
- Improve English in README.md and TODO.md

## [0.0.7](https://github.com/Ogekuri/useReq/compare/v0.0.6..v0.0.7) - 2026-01-01
### 📚  Documentation
- *(core)* update README.md file.

## [0.0.6](https://github.com/Ogekuri/useReq/compare/v0.0.5..v0.0.6) - 2026-01-01
### ⛰️  Features
- *(core)* add support for multiple requirement files and multiple tech dirs.

## [0.0.5](https://github.com/Ogekuri/useReq/compare/v0.0.4..v0.0.5) - 2026-01-01
### ⛰️  Features
- *(core)* add preliminary Kiro CLI support.

## [0.0.4](https://github.com/Ogekuri/useReq/compare/v0.0.3..v0.0.4) - 2025-12-31
### 📚  Documentation
- *(core)* edit README.md

## [0.0.3](https://github.com/Ogekuri/useReq/compare/v0.0.2..v0.0.3) - 2025-12-31
### 🚜  Changes
- *(core)* fix all prompts.

## [0.0.2](https://github.com/Ogekuri/useReq/compare/v0.0.1..v0.0.2) - 2025-12-31
### 📚  Documentation
- *(core)* aggiornato TODO.md.

## [0.0.1](https://github.com/Ogekuri/useReq/releases/tag/v0.0.1) - 2025-12-31
### ⛰️  Features
- *(core)* Initial draft release.
- *(core)* Add analyze and optimize commands.


# History

- \[0.0.1\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.1
- \[0.0.2\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.2
- \[0.0.3\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.3
- \[0.0.4\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.4
- \[0.0.5\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.5
- \[0.0.6\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.6
- \[0.0.7\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.7
- \[0.0.8\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.8
- \[0.0.9\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.9
- \[0.0.10\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.10
- \[0.0.11\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.11
- \[0.0.12\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.12
- \[0.0.13\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.13
- \[0.0.14\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.14
- \[0.0.15\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.15
- \[0.0.16\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.16
- \[0.0.17\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.17
- \[0.0.18\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.18
- \[0.0.19\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.19
- \[0.0.20\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.20
- \[0.0.21\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.21
- \[0.0.22\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.22
- \[0.0.23\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.23
- \[0.0.24\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.24
- \[0.0.25\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.25
- \[0.0.26\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.26
- \[0.0.27\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.27
- \[0.0.28\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.28
- \[0.0.29\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.29
- \[0.0.30\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.30
- \[0.0.31\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.31
- \[0.0.32\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.32
- \[0.0.33\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.33
- \[0.0.34\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.34
- \[0.0.35\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.35
- \[0.0.36\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.36
- \[0.0.37\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.37
- \[0.0.38\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.38
- \[0.0.39\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.39
- \[0.0.40\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.40
- \[0.0.41\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.41
- \[0.0.42\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.42
- \[0.0.43\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.43
- \[0.0.44\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.44
- \[0.0.45\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.45
- \[0.0.46\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.46
- \[0.0.47\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.47
- \[0.0.48\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.48
- \[0.0.49\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.49
- \[0.0.50\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.50
- \[0.0.51\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.51
- \[0.0.52\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.52
- \[0.0.53\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.53
- \[0.0.54\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.54
- \[0.0.55\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.55
- \[0.0.56\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.56
- \[0.0.57\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.57
- \[0.0.58\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.58
- \[0.0.59\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.59
- \[0.0.60\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.60
- \[0.0.61\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.61
- \[0.0.62\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.62
- \[0.0.63\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.63
- \[0.0.64\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.64
- \[0.0.65\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.65
- \[0.0.66\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.66
- \[0.0.67\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.67
- \[0.0.68\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.68
- \[0.0.69\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.69
- \[0.0.70\]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.70

[0.0.1]: https://github.com/Ogekuri/useReq/releases/tag/v0.0.1
[0.0.2]: https://github.com/Ogekuri/useReq/compare/v0.0.1..v0.0.2
[0.0.3]: https://github.com/Ogekuri/useReq/compare/v0.0.2..v0.0.3
[0.0.4]: https://github.com/Ogekuri/useReq/compare/v0.0.3..v0.0.4
[0.0.5]: https://github.com/Ogekuri/useReq/compare/v0.0.4..v0.0.5
[0.0.6]: https://github.com/Ogekuri/useReq/compare/v0.0.5..v0.0.6
[0.0.7]: https://github.com/Ogekuri/useReq/compare/v0.0.6..v0.0.7
[0.0.8]: https://github.com/Ogekuri/useReq/compare/v0.0.7..v0.0.8
[0.0.9]: https://github.com/Ogekuri/useReq/compare/v0.0.8..v0.0.9
[0.0.10]: https://github.com/Ogekuri/useReq/compare/v0.0.9..v0.0.10
[0.0.11]: https://github.com/Ogekuri/useReq/compare/v0.0.10..v0.0.11
[0.0.12]: https://github.com/Ogekuri/useReq/compare/v0.0.11..v0.0.12
[0.0.13]: https://github.com/Ogekuri/useReq/compare/v0.0.12..v0.0.13
[0.0.14]: https://github.com/Ogekuri/useReq/compare/v0.0.13..v0.0.14
[0.0.15]: https://github.com/Ogekuri/useReq/compare/v0.0.14..v0.0.15
[0.0.16]: https://github.com/Ogekuri/useReq/compare/v0.0.15..v0.0.16
[0.0.17]: https://github.com/Ogekuri/useReq/compare/v0.0.16..v0.0.17
[0.0.18]: https://github.com/Ogekuri/useReq/compare/v0.0.17..v0.0.18
[0.0.19]: https://github.com/Ogekuri/useReq/compare/v0.0.18..v0.0.19
[0.0.20]: https://github.com/Ogekuri/useReq/compare/v0.0.19..v0.0.20
[0.0.21]: https://github.com/Ogekuri/useReq/compare/v0.0.20..v0.0.21
[0.0.22]: https://github.com/Ogekuri/useReq/compare/v0.0.21..v0.0.22
[0.0.23]: https://github.com/Ogekuri/useReq/compare/v0.0.22..v0.0.23
[0.0.24]: https://github.com/Ogekuri/useReq/compare/v0.0.23..v0.0.24
[0.0.25]: https://github.com/Ogekuri/useReq/compare/v0.0.24..v0.0.25
[0.0.26]: https://github.com/Ogekuri/useReq/compare/v0.0.25..v0.0.26
[0.0.27]: https://github.com/Ogekuri/useReq/compare/v0.0.26..v0.0.27
[0.0.28]: https://github.com/Ogekuri/useReq/compare/v0.0.27..v0.0.28
[0.0.29]: https://github.com/Ogekuri/useReq/compare/v0.0.28..v0.0.29
[0.0.30]: https://github.com/Ogekuri/useReq/compare/v0.0.29..v0.0.30
[0.0.31]: https://github.com/Ogekuri/useReq/compare/v0.0.30..v0.0.31
[0.0.32]: https://github.com/Ogekuri/useReq/compare/v0.0.31..v0.0.32
[0.0.33]: https://github.com/Ogekuri/useReq/compare/v0.0.32..v0.0.33
[0.0.34]: https://github.com/Ogekuri/useReq/compare/v0.0.33..v0.0.34
[0.0.35]: https://github.com/Ogekuri/useReq/compare/v0.0.34..v0.0.35
[0.0.36]: https://github.com/Ogekuri/useReq/compare/v0.0.35..v0.0.36
[0.0.37]: https://github.com/Ogekuri/useReq/compare/v0.0.36..v0.0.37
[0.0.38]: https://github.com/Ogekuri/useReq/compare/v0.0.37..v0.0.38
[0.0.39]: https://github.com/Ogekuri/useReq/compare/v0.0.38..v0.0.39
[0.0.40]: https://github.com/Ogekuri/useReq/compare/v0.0.39..v0.0.40
[0.0.41]: https://github.com/Ogekuri/useReq/compare/v0.0.40..v0.0.41
[0.0.42]: https://github.com/Ogekuri/useReq/compare/v0.0.41..v0.0.42
[0.0.43]: https://github.com/Ogekuri/useReq/compare/v0.0.42..v0.0.43
[0.0.44]: https://github.com/Ogekuri/useReq/compare/v0.0.43..v0.0.44
[0.0.45]: https://github.com/Ogekuri/useReq/compare/v0.0.44..v0.0.45
[0.0.46]: https://github.com/Ogekuri/useReq/compare/v0.0.45..v0.0.46
[0.0.47]: https://github.com/Ogekuri/useReq/compare/v0.0.46..v0.0.47
[0.0.48]: https://github.com/Ogekuri/useReq/compare/v0.0.47..v0.0.48
[0.0.49]: https://github.com/Ogekuri/useReq/compare/v0.0.48..v0.0.49
[0.0.50]: https://github.com/Ogekuri/useReq/compare/v0.0.49..v0.0.50
[0.0.51]: https://github.com/Ogekuri/useReq/compare/v0.0.50..v0.0.51
[0.0.52]: https://github.com/Ogekuri/useReq/compare/v0.0.51..v0.0.52
[0.0.53]: https://github.com/Ogekuri/useReq/compare/v0.0.52..v0.0.53
[0.0.54]: https://github.com/Ogekuri/useReq/compare/v0.0.53..v0.0.54
[0.0.55]: https://github.com/Ogekuri/useReq/compare/v0.0.54..v0.0.55
[0.0.56]: https://github.com/Ogekuri/useReq/compare/v0.0.55..v0.0.56
[0.0.57]: https://github.com/Ogekuri/useReq/compare/v0.0.56..v0.0.57
[0.0.58]: https://github.com/Ogekuri/useReq/compare/v0.0.57..v0.0.58
[0.0.59]: https://github.com/Ogekuri/useReq/compare/v0.0.58..v0.0.59
[0.0.60]: https://github.com/Ogekuri/useReq/compare/v0.0.59..v0.0.60
[0.0.61]: https://github.com/Ogekuri/useReq/compare/v0.0.60..v0.0.61
[0.0.62]: https://github.com/Ogekuri/useReq/compare/v0.0.61..v0.0.62
[0.0.63]: https://github.com/Ogekuri/useReq/compare/v0.0.62..v0.0.63
[0.0.64]: https://github.com/Ogekuri/useReq/compare/v0.0.63..v0.0.64
[0.0.65]: https://github.com/Ogekuri/useReq/compare/v0.0.64..v0.0.65
[0.0.66]: https://github.com/Ogekuri/useReq/compare/v0.0.65..v0.0.66
[0.0.67]: https://github.com/Ogekuri/useReq/compare/v0.0.66..v0.0.67
[0.0.68]: https://github.com/Ogekuri/useReq/compare/v0.0.67..v0.0.68
[0.0.69]: https://github.com/Ogekuri/useReq/compare/v0.0.68..v0.0.69
[0.0.70]: https://github.com/Ogekuri/useReq/compare/v0.0.69..v0.0.70
