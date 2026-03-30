# Changelog

## [0.50.0](https://github.com/Ogekuri/useReq/compare/v0.49.0..v0.50.0) - 2026-03-30
### 🚜  Changes
- always persist version-check idle state [useReq] *(cli)*
  - Update SRS-350 and add SRS-351 for failure persistence.
  - Rewrite idle-state JSON on every release-check failure.
  - Use 86400 seconds for API call failures and 3600 seconds for other failures.
  - Recompute idle-until from current time on failure writes.
  - Refresh WORKFLOW and REFERENCES docs and extend tests.
- raise version-check idle delays [useReq] *(cli)*
  - Update SRS-349 and SRS-350 idle-delay values.
  - Set successful version-check idle-delay to 3600 seconds.
  - Set rate-limit error idle-delay to 86400 seconds.
  - Refresh WORKFLOW and REFERENCES docs.
  - Update release-check tests for new timing constants.
- enforce 1h version-check backoff on rate limits [useReq] *(cli)*
  - Update SRS-345 and add SRS-348..350.
  - Persist 300s idle-delay after successful release-checks.
  - Persist 3600s idle-delay for HTTP 429 and HTTP 403 API rate-limit failures.
  - Refresh WORKFLOW and REFERENCES docs.
  - Update release-check tests.

## [0.49.0](https://github.com/Ogekuri/useReq/compare/v0.48.0..v0.49.0) - 2026-03-30
### 🐛  Bug Fixes
- Fix fix prompt.

## [0.48.0](https://github.com/Ogekuri/useReq/compare/v0.47.0..v0.48.0) - 2026-03-29
### 🐛  Bug Fixes
- Update images.

## [0.47.0](https://github.com/Ogekuri/useReq/compare/v0.46.0..v0.47.0) - 2026-03-29
### ⛰️  Features
- Update images.

## [0.46.0](https://github.com/Ogekuri/useReq/compare/v0.45.0..v0.46.0) - 2026-03-27
### 🚜  Changes
- force online release-check for version flags [useReq] *(cli)*
  - update SRS-345 for forced online check on --ver/--version
  - implement startup force override to bypass idle-state gating
  - add regression test for active-idle bypass on --version
  - update WORKFLOW and regenerate REFERENCES

## [0.45.0](https://github.com/Ogekuri/useReq/compare/v0.44.0..v0.45.0) - 2026-03-18
### ⛰️  Features
- Update promts files.

### 🐛  Bug Fixes
- resolve relative path config before chdir [useReq] *(git-wt-create)*
  - Add reproducer for relative git/base path config in --git-wt-create.
  - Resolve configured git-path/base-path against project base before worktree destination derivation.
  - Keep successful final cwd at <parent-path>/<WT_NAME> while restoring sibling destination behavior.
  - Update WORKFLOW runtime note and regenerate REFERENCES.

### 🚜  Changes
- replace git-parent-path with get-base-path [useReq] *(cli)*
  - Update SRS-333/SRS-334/SRS-347 and SRS-330 for path command scope.
  - Remove --git-parent-path and add --get-base-path in parser, routing, and docs.
  - Make --git-path read configured git-path and --get-base-path read base-path.
  - Adjust CLI tests for config-driven behavior and missing-config errors.
  - Regenerate WORKFLOW and REFERENCES documentation.
- replace git-wt-exit with git path commands [useReq] *(cli)*
  - Update SRS-333/SRS-334 and add SRS-347 for --git-path and --git-parent-path.
  - Remove --git-wt-exit parser/dispatch implementation from CLI.
  - Add command handlers and tests for git-root and git-parent-path resolution.
  - Refresh README, WORKFLOW, and REFERENCES documentation.
- BREAKING CHANGE: remove cwd mutation on create [useReq] *(git-wt-create)*
  - Update SRS-331 to require no cwd change for --git-wt-create.
  - Adjust SRS-335 wording to remove dependency on final directory change.
  - Remove chdir side effect from run_git_wt_create while preserving existing checks.
  - Update git-wt-create tests to assert unchanged cwd on success and failure.
  - Keep rollback verification by forcing post-create copy failure in tests.
  - Update WORKFLOW and regenerate REFERENCES for traceability.
- set success cwd to worktree root [useReq] *(git-wt-create)*
  - Update SRS-331 to require final cwd at <parent-path>/<WT_NAME>.
  - Adjust run_git_wt_create to chdir to worktree root on success.
  - Add nested base-path unit test to verify new cwd behavior.
  - Update WORKFLOW runtime model for git-wt-create success path.

### 📚  Documentation
- clarify git-path and get-base-path behavior [useReq] *(readme)*
  - Update CLI command descriptions for --git-path and --get-base-path.
  - Document config-driven output and missing-config error message.

## [0.44.0](https://github.com/Ogekuri/useReq/compare/v0.43.0..v0.44.0) - 2026-03-18
### ⛰️  Features
- Update prompts.

## [0.43.0](https://github.com/Ogekuri/useReq/compare/v0.42.0..v0.43.0) - 2026-03-18
### 🚜  Changes
- move release-check idle cache path [useReq] *(cli)*
  - Update SRS-344 and add SRS-345/SRS-346 for cache path and uninstall cleanup.
  - Persist idle-state at ~/.cache/usereq/check_version_idle-time.json.
  - Create cache directories automatically before idle-state writes.
  - On Linux --uninstall, remove idle-state file and empty cache directory.
  - Add unit tests for new path, directory creation, and uninstall cleanup.
  - Update WORKFLOW.md and regenerate REFERENCES.md.

## [0.42.0](https://github.com/Ogekuri/useReq/compare/v0.41.0..v0.42.0) - 2026-03-17
### ⛰️  Features
- Update .g.conf file.

### 🚜  Changes
- gate upgrade/uninstall to Linux [useReq] *(cli)*
  - Update SRS-034 and add SRS-343/SRS-344 for Linux-only execution.
  - Implement non-Linux guidance path for --upgrade and --uninstall.
  - Preserve Linux uv execution behavior and error propagation.
  - Add CLI unit tests for Linux and non-Linux command paths.
  - Refresh WORKFLOW.md and regenerate REFERENCES.md traceability docs.

## [0.41.0](https://github.com/Ogekuri/useReq/compare/v0.40.0..v0.41.0) - 2026-03-17
### ⛰️  Features
- Update prompts files.
- Update prompts.

### 🚜  Changes
- remove legacy and over-specific SRS rules [useReq] *(requirements)*
  - Removed requirement IDs classified as legacy/over-specific vs current implementation state.\n- Kept only requirements with direct repository evidence linkage.\n- Preserved SRS structure while reducing normative surface to implemented behavior.

### 📚  Documentation
- recreate SRS structure from repository evidence [useReq] *(requirements)*
  - Reorganized and normalized requirement statements.\n- Preserved all existing SRS IDs without renumbering.\n- Aligned requirement-line syntax to RFC2119 keyword-first form.\n- Updated SRS metadata date/version for this rewrite.

## [0.40.0](https://github.com/Ogekuri/useReq/compare/v0.39.0..v0.40.0) - 2026-03-17
### 🐛  Bug Fixes
- ensure build module for release build [useReq] *(release-workflow)*
  - Fix CI release workflow failure: python -m build missing module.
  - Use uv run --frozen --with build in release workflow.
  - Add regression test for build step command in workflow file.
  - Update WORKFLOW runtime model for release build trace.

## [0.39.0](https://github.com/Ogekuri/useReq/compare/v0.38.0..v0.39.0) - 2026-03-17
### ⛰️  Features
- Update prompts files.

### 🐛  Bug Fixes
- skip tests fixtures during project scan [useReq] *(static-check)*
  - Ignore tests/fixtures and <tests-dir>/fixtures in --static-check selection.
  - Add failing reproducer test and verify wrapper static-check succeeds.
  - Update WORKFLOW and regenerate REFERENCES for runtime/index alignment.
- preserve caller cwd with uv project execution [useReq] *(req.sh)*
  - Fix wrapper context leak for here-mode commands launched outside useReq.
  - Use uv run --project <repo-root> without changing current working directory.
  - Add reproducer test for external-cwd --git-check behavior.
  - Update WORKFLOW and regenerate REFERENCES docs.
- execute main on module run [useReq] *(cli)*
  - add __main__ guard in usereq.cli for python -m usereq.cli
  - add regression test for --ver stdout in module execution
  - update workflow/references runtime documentation
- defer cli import to avoid runpy warning [useReq] *(usereq-init)*
  - add reproducer test for python -m usereq.cli RuntimeWarning
  - lazy-load usereq.cli in package __init__ preserving public API
  - update WORKFLOW/REFERENCES documentation
- remove unsupported uv forms section [useReq] *(pyproject)*
  - remove deprecated [tool.uv.forms.use-req-init] from pyproject.toml
  - add regression test blocking unsupported uv forms settings
- resolve all static-check failures [useReq] *(static-check)*
  - Add _detect_venv_python() to detect project .venv Python for pyright
  - --pythonpath, fixing reportMissingImports false positives when req is
  - installed globally via uv tools
  - Fix all Ruff errors: F401 unused imports, F841 unused variables,
  - E741 ambiguous variable name, E731 lambda assignment, f-string
  - backslash expressions incompatible with Python 3.11
  - Fix Pylance errors: reportOptionalMemberAccess, reportArgumentType
  - Fix C/C++ fixtures: cppcheck-suppress directives, clang-format
  - Update fixture expected counts and line numbers in test helpers

### 🚜  Changes
- remove pyright extra-path forwarding [useReq] *(static-check)*
  - Update SRS-247/SRS-253/SRS-256/SRS-261/SRS-341 for no --extra-path behavior.
  - Remove src_dirs forwarding from static-check dispatch and CLI command paths.
  - Drop StaticCheckPylance extra-path command building logic.
  - Adapt static-check unit tests to assert absence of --extra-path.
  - Refresh WORKFLOW and REFERENCES docs for updated runtime model.
- BREAKING CHANGE: migrate dependency policy to uv.lock [useReq] *(dependencies)*
  - update SRS-055 and SRS-264 for uv.lock canonical lockfile policy
  - remove root requirements.txt and unignore uv.lock in .gitignore
  - switch release workflow build step to uv run --frozen python -m build
  - update dependency manifest tests and regenerate docs/REFERENCES.md
- BREAKING CHANGE: switch req.sh launcher to uv runtime [useReq] *(scripts)*
  - Update SRS-056 from .venv bootstrap to uv run CLI dispatch.
  - Add SRS-342 requiring README Requirements section for uv prerequisite.
  - Refactor scripts/req.sh to use uv run python -m usereq.cli with argv passthrough.
  - Update dependency-manifest tests for uv-based wrapper behavior and README requirement.
  - Update WORKFLOW model and regenerate REFERENCES.md.

### 📚  Documentation
- document requirements export command [useReq] *(readme)*
  - add Requirements note for generating requirements.txt via uv export
  - keep existing README structure and usage guidance unchanged

## [0.38.0](https://github.com/Ogekuri/useReq/compare/v0.37.0..v0.38.0) - 2026-03-16
### 🐛  Bug Fixes
- remove pytest from requirements.txt [useReq] *(dependencies)*
  - Removed 'pytest' from requirements.txt; it is a test/dev dependency,
  - not a runtime/build package (violates SRS-055).
  - Restores alignment between pyproject.toml and requirements.txt (SRS-264).
  - Both test_requirements_contains_only_runtime_build_packages and
  - test_pyproject_dependencies_are_aligned_with_requirements now pass.
  - Fallback no-test flow: defect is manifest-only, no source code change;
  - existing tests already cover this requirement.
- Fix requirements.txt file.

### 🚜  Changes
- BREAKING CHANGE: use package-installed ruff/pyright via sys.executable [useReq] *(static-check)*
  - SRS-242: StaticCheckPylance now invokes pyright via [sys.executable, "-m", "pyright"]
  - SRS-243: StaticCheckRuff now invokes ruff via [sys.executable, "-m", "ruff", "check"]
  - SRS-264: Updated to require ruff and pyright in pyproject.toml project.dependencies
  - SRS-338: pyproject.toml [project].dependencies includes ruff and pyright
  - SRS-339: Pylance/Ruff checkers use sys.executable -m invocation (no external PATH)
  - SRS-340: New test validates ruff/pyright in pyproject.toml dependencies
  - Updated test_static_check.py to verify new command invocation format
  - Updated test_dependency_manifests.py with pyright/ruff dependency test
  - Regenerated REFERENCES.md
- BREAKING CHANGE: add pytest, pyright, ruff to requirements.txt [useReq] *(dependencies)*
  - SRS-055: requirements.txt now covers all project deps
  - SRS-264: pyproject.toml deps now required to be subset of requirements.txt
  - Added pytest, pyright, ruff to requirements.txt
  - Renamed RUNTIME_BUILD_PACKAGES to ALL_PROJECT_PACKAGES in tests
  - Alignment test checks subset relationship instead of exact match
- BREAKING CHANGE: suppress stdout output for passing checks in --files-static-check and --static-check [useReq] *(static-check)*
  - SRS-241/242/243/244: add fail_only mode to all checker classes;
  - when active, passing files produce no output (no header, no Result: OK,
  - no trailing blank line)
  - SRS-253: --files-static-check now dispatches with fail_only=True
  - SRS-256: --static-check now dispatches with fail_only=True
  - SRS-261: dispatch_static_check_for_file gains fail_only kwarg (default False)
  - SRS-247: add fail_only mode unit tests for all checker classes
  - --test-static-check retains verbose output (fail_only defaults to False)
  - Updated WORKFLOW.md and REFERENCES.md to reflect changes

## [0.37.0](https://github.com/Ogekuri/useReq/compare/v0.36.0..v0.37.0) - 2026-03-16
### 🚜  Changes
- BREAKING CHANGE: remove ruff.sh and pyright.sh accessory scripts [useReq] *(scripts)*
  - Remove SRS-266 (scripts/ruff.sh requirement)
  - Remove SRS-267 (scripts/pyright.sh requirement)
  - Delete scripts/ruff.sh and scripts/pyright.sh
  - Remove PROC:ruff-sh and PROC:pyright-sh from WORKFLOW.md
  - Regenerate REFERENCES.md without deleted scripts
  - No source code or test changes needed (no references existed)
- BREAKING CHANGE: include tests-dir in --static-check file selection [useReq] *(static-check)*
  - SRS-256: --static-check now selects files from both src-dir and tests-dir
  - SRS-336: tests-dir loaded from config.json; missing/invalid skipped silently
  - SRS-337: unit tests verify both src-dir and tests-dir file inclusion
  - run_project_static_check_cmd loads full config to extract tests-dir
  - Two new tests in TestStaticCheckProjectScan class
  - WORKFLOW.md updated with new call-trace for load_full_config
  - REFERENCES.md regenerated

## [0.36.0](https://github.com/Ogekuri/useReq/compare/v0.35.0..v0.36.0) - 2026-03-16
### 🚜  Changes
- enforce Command params-before-file order [useReq] *(static-check)*
  - Update SRS-244/SRS-253/SRS-256 for Command invocation order.
  - Implement Command execution as <cmd> [params...] <filename>.
  - Add regression tests for --files-static-check and --static-check command ordering.
  - Refresh WORKFLOW and REFERENCES documents.

### 📚  Documentation
- Update README.md document.

## [0.35.0](https://github.com/Ogekuri/useReq/compare/v0.34.0..v0.35.0) - 2026-03-16
### 🐛  Bug Fixes
- preserve existing static-check entries [useReq] *(cli)*
  - Ensure --enable-static-check appends only non-duplicate entries and keeps existing ones.\nAdd regression test for non-update config with pre-existing JavaScript Command checker.\nUpdate runtime/reference docs.

### 🚜  Changes
- enforce identity-based update merge [useReq] *(static-check)*
  - Update SRS-301 to define duplicate detection by exact tuple (language,module,cmd,params).
  - Implement canonical static-check identity helper in cli merge flow.
  - Preserve existing static-check entries and append only non-duplicate identities.
  - Add tests covering tuple-based dedupe and metadata-insensitive duplicate detection.
  - Refresh WORKFLOW.md and regenerate REFERENCES.md.

### 📚  Documentation
- document git/docs utility commands [useReq] *(readme)*
  - Document CLI usage for --docs-check, --git-check, --git-wt-create, --git-wt-exit, and --git-wt-delete.\nKeep the existing README structure and limit edits to command coverage.
- align static-check merge behavior [useReq] *(readme)*
  - Document --enable-static-check merge semantics for existing config.\nClarify that existing entries are preserved, duplicates ignored, and new entries appended.

## [0.34.0](https://github.com/Ogekuri/useReq/compare/v0.33.0..v0.34.0) - 2026-03-16
### 🐛  Bug Fixes
- Minor fixex in promtps.
- Major fixes on prompts.

### 🚜  Changes
- decouple resource coverage from unused skills dir [useReq] *(packaging)*
  - Update SRS-272 to require only operational resource patterns.
  - Adjust dependency manifest test to validate fixed required subdirectories.
  - Keep provider skills generation logic unchanged; resources/skills remains absent.
- BREAKING CHANGE: remove provider skills artifact support [useReq] *(cli)*
  - Update SRS to drop skills artifact handling requirements.
  - Remove skills artifact parsing and generation logic from src/usereq/cli.py.
  - Adjust tests to align with prompts/agents-only provider artifacts.
  - Regenerate docs/REFERENCES.md and update docs/WORKFLOW.md runtime notes.
- harden git-wt safety [useReq] *(cli)*
  - Update SRS for exact-target and rollback guarantees in worktree commands.\nHarden --git-wt-create with rollback helper on post-create failures.\nHarden --git-wt-delete with exact path/ref matching and forced dirty-target removal.\nAdd regression tests for rollback, dirty delete, and partial-name safety.\nUpdate WORKFLOW and regenerate REFERENCES.

### ◀️  Revert
- Roll back branch to 26f54c01 (26f54c01a215e861b350ce3d6244cafb3d1f0b80).

## [0.33.0](https://github.com/Ogekuri/useReq/compare/v0.32.0..v0.33.0) - 2026-03-16
### ⛰️  Features
- Update prompt files.

### 🚜  Changes
- copy .venv in git-wt-create [useReq] *(cli)*
  - Update requirements for .venv copy in --git-wt-create (SRS-335).\nImplement .venv copy from base-path/git-path before final cwd switch.\nPreserve .venv relative placement from git-path and skip when destination exists.\nExtend unit tests for .venv copy behavior in worktree roundtrip.\nUpdate WORKFLOW and regenerate REFERENCES.
- update git worktree path transitions [useReq] *(cli)*
  - Update SRS for git-check output and worktree path behavior.\nImplement --git-wt-exit command and parser wiring.\nMake --git-wt-create cd into new worktree only on full success.\nMake --git-wt-delete cd to base-path before deletion and use git-only deletion.\nAdjust CLI tests for new behaviors and add --git-wt-exit coverage.\nRegenerate workflow and references docs.

## [0.32.0](https://github.com/Ogekuri/useReq/compare/v0.31.0..v0.32.0) - 2026-03-16
### 🐛  Bug Fixes
- Rimosso .req path.
- Rimosso .req path.

### 🚜  Changes
- add git integration, worktree management, and config path persistence [useReq] *(cli)*
  - SRS-302/303: persist and update absolute base-path in .req/config.json
  - SRS-305/306/307: validate git repo on install, persist and update git-path
  - SRS-308/309: derive parent-path and base-dir dynamically at runtime
  - SRS-310: load_full_config loads all config.json params for command use
  - SRS-311/312: new --git-check command verifying clean git status
  - SRS-313-317: new --docs-check command verifying docs file existence
  - SRS-318/319: new --git-wt-name command printing standardized worktree name
  - SRS-320-325: new --git-wt-create command with .req and provider dir copy
  - SRS-326-328: new --git-wt-delete command for worktree/branch removal
  - Updated requirements, workflow, references, and 13 new tests (1912 total pass)

## [0.31.0](https://github.com/Ogekuri/useReq/compare/v0.30.0..v0.31.0) - 2026-03-08
### 🚜  Changes
- deduplicate identical --enable-static-check entries on update [useReq] *(static-check)*
  - SRS-251 updated: identical entries (same module, cmd, params) within one invocation are silently discarded
  - SRS-301 added: --update/--here merge preserves all pre-existing static-check tools; new entries identical to existing ones are discarded; new entries with same module but different params are appended
  - cli.py run(): dedup logic applied both when collecting new specs and when merging with existing config
  - test_static_check.py: 5 new tests covering dedup within invocation, different params, update preservation, and identical-entry discard

## [0.30.0](https://github.com/Ogekuri/useReq/compare/v0.29.0..v0.30.0) - 2026-03-07
### ⛰️  Features
- Remove bell from prompts.

### 🚜  Changes
- enforce 300s update-check throttle [useReq] *(cli)*
  - Update SRS for usereq startup release-check, idle-state path, and 429 Retry-After behavior.
  - Implement fixed 300-second idle-delay gating and HTTP 429 idle-state backoff handling.
  - Keep --upgrade/--uninstall uv commands bound to usereq and repository constants.
  - Extend update-check tests for idle-delay semantics and rate-limit handling.
  - Regenerate WORKFLOW.md and REFERENCES.md for runtime and symbol traceability.
- hardcode release checks and upgrade source [useReq] *(cli)*
  - Update requirements SRS-043/SRS-050/SRS-271 and add SRS-299.
  - Hardcode release API endpoint and uv upgrade source for Ogekuri/useReq.
  - Set successful-check idle window default to 86400 seconds.
  - Add lower-bound startup release-check cadence default to 300 seconds.
  - Align update-check tests with hardcoded URL/source and timing semantics.
  - Refresh WORKFLOW and REFERENCES docs from updated implementation.

## [0.29.0](https://github.com/Ogekuri/useReq/compare/v0.28.0..v0.29.0) - 2026-03-07
### 🚜  Changes
- reduce release-check idle window to 300s [useReq] *(cli)*
  - Update SRS-271 default idle_window_seconds from 86400 to 300.
  - Set RELEASE_CHECK_IDLE_WINDOW_SECONDS to 300 in startup release-check logic.
  - Add test to assert five-minute default idle window.
  - Update WORKFLOW runtime note for release-check cadence.
  - Regenerate REFERENCES to reflect symbol/value updates.

## [0.28.0](https://github.com/Ogekuri/useReq/compare/v0.27.0..v0.28.0) - 2026-03-07
### ⛰️  Features
- Add bell to prompts.

### 🐛  Bug Fixes
- Fix prompts.
- update README and scripts to use new --provider parameter *(core)*
  - Updated README.md, scripts/test-install.sh, and tests/test_static_check.py
  - to replace deprecated global provider/artifact flags with the new
  - --provider PROVIDER:ARTIFACTS[:OPTIONS] syntax.
  - Satisfies SRS-034, SRS-275, SRS-086.

### 🚜  Changes
- adjust Modules Installed empty-options format [useReq] *(cli)*
  - Update SRS-291/SRS-295 and SRS-294/SRS-297 to allow bare artifact lines when no options are active.
  - Implement module-entry rendering in src/usereq/cli.py to output artifact without :options when absent.
  - Update related unit-test expectations in tests/test_cli.py.
  - Refresh docs/WORKFLOW.md and regenerate docs/REFERENCES.md.
- print artifact-option module lines [useReq] *(cli)*
  - Update requirements for Modules Installed artifact:options format.
  - Render one non-wrapped line per active artifact in Modules Installed.
  - Preserve parsed provider option order and emit '-' when options are absent.
  - Extend tests for multiline module rows and no-wrap width behavior.
  - Update WORKFLOW call-trace nodes and regenerate REFERENCES.
- render provider summary table with wrapped prompts [useReq] *(cli)*
  - Update SRS with Unicode table and provider-option summary requirements.
  - Implement Unicode box-drawing installation table with bright-red borders.
  - Rename header to Provider and wrap Prompts Installed at max 50 chars.
  - Render Modules Installed from active per-provider --provider option flags.
  - Add/adjust CLI unit tests for header, wrapping, and module option rendering.
  - Regenerate WORKFLOW/REFERENCES for updated runtime and symbols.

### ✨  Refactor
- remove 13 legacy global flags; --provider SPEC is sole configuration mechanism *(cli)*
  - Remove backward compatibility for --enable-models, --enable-tools,
  - --enable-claude, --enable-codex, --enable-gemini, --enable-github,
  - --enable-kiro, --enable-opencode, --install-prompts, --install-agents,
  - --install-skills, --prompts-use-agents, and --legacy global CLI flags.
  - The --provider PROVIDER:ARTIFACTS[:OPTIONS] repeatable argument is now
  - the sole mechanism for provider/artifact/option configuration.
  - --preserve-models is kept as a standalone global flag.
  - config.json persistence reduced from 14 boolean keys to preserve-models
  - boolean + providers array of SPEC strings.
  - resolve_provider_configs() no longer accepts args parameter.
  - build_persisted_update_flags() and load_persisted_update_flags() now
  - handle only preserve-models. Legacy mode is derived per-provider from
  - the :legacy option in --provider specs.
  - All 108 tests pass. REQUIREMENTS.md bumped to v1.05 with 4 SRS entries
  - removed (SRS-277, SRS-281, SRS-282, SRS-283) and SRS-288 added.

## [0.27.0](https://github.com/Ogekuri/useReq/compare/v0.26.0..v0.27.0) - 2026-03-07
### 🐛  Bug Fixes
- Fix scripts/test-install.sh script.

## [0.26.0](https://github.com/Ogekuri/useReq/compare/v0.25.0..v0.26.0) - 2026-03-07
### 🐛  Bug Fixes
- include resources/common/*.json in package-data and remove stale kiro reference [useReq] *(packaging)*

## [0.24.0](https://github.com/Ogekuri/useReq/compare/v0.23.0..v0.24.0) - 2026-03-06
### 🐛  Bug Fixes
- retry upgrade remote inspection from repo root [useReq] *(cli)*
  - retry git remote inspection in REPO_ROOT when cwd is outside repository
  - preserve upgrade source resolution contract and uv install command
  - add deterministic reproducer unit test for non-repo cwd failure
  - update WORKFLOW and regenerate REFERENCES docs

## [0.23.0](https://github.com/Ogekuri/useReq/compare/v0.22.0..v0.23.0) - 2026-03-06
### 🚜  Changes
- support .mjs extension [useReq] *(parser)*
  - Update SRS-131 to include JavaScript .mjs extension support.
  - Extend parser-facing extension maps and project source scanning filters for .mjs.
  - Align static-check extension mapping with JavaScript .js and .mjs aliases.
  - Add regression tests for .mjs detection and source file collection paths.

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
- \[0.22.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.22.0
- \[0.23.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.23.0
- \[0.24.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.24.0
- \[0.25.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.25.0
- \[0.26.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.26.0
- \[0.27.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.27.0
- \[0.28.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.28.0
- \[0.29.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.29.0
- \[0.30.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.30.0
- \[0.31.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.31.0
- \[0.32.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.32.0
- \[0.33.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.33.0
- \[0.34.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.34.0
- \[0.35.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.35.0
- \[0.36.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.36.0
- \[0.37.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.37.0
- \[0.38.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.38.0
- \[0.39.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.39.0
- \[0.40.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.40.0
- \[0.41.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.41.0
- \[0.42.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.42.0
- \[0.43.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.43.0
- \[0.44.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.44.0
- \[0.45.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.45.0
- \[0.46.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.46.0
- \[0.47.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.47.0
- \[0.48.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.48.0
- \[0.49.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.49.0
- \[0.50.0\]: https://github.com/Ogekuri/useReq/releases/tag/v0.50.0

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
[0.22.0]: https://github.com/Ogekuri/useReq/compare/v0.21.0..v0.22.0
[0.23.0]: https://github.com/Ogekuri/useReq/compare/v0.22.0..v0.23.0
[0.24.0]: https://github.com/Ogekuri/useReq/compare/v0.23.0..v0.24.0
[0.25.0]: https://github.com/Ogekuri/useReq/compare/v0.24.0..v0.25.0
[0.26.0]: https://github.com/Ogekuri/useReq/compare/v0.25.0..v0.26.0
[0.27.0]: https://github.com/Ogekuri/useReq/compare/v0.26.0..v0.27.0
[0.28.0]: https://github.com/Ogekuri/useReq/compare/v0.27.0..v0.28.0
[0.29.0]: https://github.com/Ogekuri/useReq/compare/v0.28.0..v0.29.0
[0.30.0]: https://github.com/Ogekuri/useReq/compare/v0.29.0..v0.30.0
[0.31.0]: https://github.com/Ogekuri/useReq/compare/v0.30.0..v0.31.0
[0.32.0]: https://github.com/Ogekuri/useReq/compare/v0.31.0..v0.32.0
[0.33.0]: https://github.com/Ogekuri/useReq/compare/v0.32.0..v0.33.0
[0.34.0]: https://github.com/Ogekuri/useReq/compare/v0.33.0..v0.34.0
[0.35.0]: https://github.com/Ogekuri/useReq/compare/v0.34.0..v0.35.0
[0.36.0]: https://github.com/Ogekuri/useReq/compare/v0.35.0..v0.36.0
[0.37.0]: https://github.com/Ogekuri/useReq/compare/v0.36.0..v0.37.0
[0.38.0]: https://github.com/Ogekuri/useReq/compare/v0.37.0..v0.38.0
[0.39.0]: https://github.com/Ogekuri/useReq/compare/v0.38.0..v0.39.0
[0.40.0]: https://github.com/Ogekuri/useReq/compare/v0.39.0..v0.40.0
[0.41.0]: https://github.com/Ogekuri/useReq/compare/v0.40.0..v0.41.0
[0.42.0]: https://github.com/Ogekuri/useReq/compare/v0.41.0..v0.42.0
[0.43.0]: https://github.com/Ogekuri/useReq/compare/v0.42.0..v0.43.0
[0.44.0]: https://github.com/Ogekuri/useReq/compare/v0.43.0..v0.44.0
[0.45.0]: https://github.com/Ogekuri/useReq/compare/v0.44.0..v0.45.0
[0.46.0]: https://github.com/Ogekuri/useReq/compare/v0.45.0..v0.46.0
[0.47.0]: https://github.com/Ogekuri/useReq/compare/v0.46.0..v0.47.0
[0.48.0]: https://github.com/Ogekuri/useReq/compare/v0.47.0..v0.48.0
[0.49.0]: https://github.com/Ogekuri/useReq/compare/v0.48.0..v0.49.0
[0.50.0]: https://github.com/Ogekuri/useReq/compare/v0.49.0..v0.50.0
