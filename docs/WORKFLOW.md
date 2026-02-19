# WORKFLOW

## Execution Units Index
- `PROC:main`: Process; `req` CLI runtime.
  - Entrypoints: `__main__()` [`src/usereq/__main__.py`], `main(argv=None)` [`src/usereq/cli.py`]
  - Primary role: Project initialization + artifact generation; file-scope utilities; project-scope utilities.
- `THR:PROC:main#main`: Thread; Python main thread (single-threaded control flow).
  - Parent: `PROC:main`
  - Entrypoints: `__main__()` [`src/usereq/__main__.py`], `main(argv=None)` [`src/usereq/cli.py`]
- `PROC:gha:release-uvx`: Process; GitHub Actions runner job `build-release` (tag push `v*`).
  - Entrypoints: `workflow_release_uvx.build_release()` [`.github/workflows/release-uvx.yml`]
- `THR:PROC:gha:release-uvx#main`: Thread; GitHub Actions runner main thread.
  - Parent: `PROC:gha:release-uvx`
  - Entrypoints: `workflow_release_uvx.build_release()` [`.github/workflows/release-uvx.yml`]

## Execution Units

### PROC:main
- Entrypoints
  - `__main__()`: module execution boundary [`src/usereq/__main__.py`]
  - `main(argv=None)`: CLI entrypoint; returns process exit code [`src/usereq/cli.py`]
- Lifecycle/Trigger
  - Trigger: OS invokes console script `req` OR `python -m usereq`.
  - Termination: `sys.exit(exit_code)` [`src/usereq/__main__.py`].
- Internal Call-Trace Tree
  - `__main__()`: delegate to CLI main [`src/usereq/__main__.py`]
    - `main(argv=None)`: argv-based dispatcher [`src/usereq/cli.py`]
      - `build_parser()`: construct argparse schema [`src/usereq/cli.py`]
      - `maybe_print_version(argv)`: version flag early-exit [`src/usereq/cli.py`]
      - `parse_args(argv=None)`: parse argv into `Namespace` [`src/usereq/cli.py`]
      - `_is_standalone_command(args)`: select file-scope commands [`src/usereq/cli.py`]
        - External boundary: CLI parsing determines which branch executes.
        - `run_files_tokens(paths)`: token report for explicit file list [`src/usereq/cli.py`]
          - External boundary: filesystem reads of `paths`.
          - `run_files_tokens(...)`: delegates token counting to `count_tokens_in_text(...)` [`src/usereq/token_counter.py`]
        - `run_files_references(paths)`: references report for explicit file list [`src/usereq/cli.py`]
          - `generate_markdown(..., output_base=Path.cwd())`: render structured markdown with symbol index and cwd-relative file paths [`src/usereq/generate_markdown.py`]
            - `_format_output_path(...)`: convert absolute source path to project-home-relative markdown path [`src/usereq/generate_markdown.py`]
            - `SourceAnalyzer.analyze(...)`: extract source constructs [`src/usereq/source_analyzer.py`]
            - `SourceAnalyzer.enrich(...)`: add names/signatures/Doxygen fields [`src/usereq/source_analyzer.py`]
              - `parse_doxygen_comment(...)`: parse Doxygen tag payloads [`src/usereq/doxygen_parser.py`]
            - `format_markdown(...)`: emit compact markdown payload [`src/usereq/source_analyzer.py`]
        - `run_files_compress(paths)`: compression for explicit file list [`src/usereq/cli.py`]
          - `compress_files(..., output_base=Path.cwd())`: compact multi-file markdown emission with cwd-relative headers [`src/usereq/compress_files.py`]
            - `_format_output_path(...)`: convert absolute source path to project-home-relative header path [`src/usereq/compress_files.py`]
            - External boundary: filesystem reads of `paths`.
        - `run_files_find(args)`: construct extraction for explicit file list [`src/usereq/cli.py`]
          - `find_constructs_in_files(...)`: extract tagged constructs [`src/usereq/find_constructs.py`]
            - `SourceAnalyzer.analyze(...)`: extract source constructs [`src/usereq/source_analyzer.py`]
            - `SourceAnalyzer.enrich(...)`: add names/signatures/Doxygen fields [`src/usereq/source_analyzer.py`]
      - `_is_project_scan_command(args)`: select project-scope commands [`src/usereq/cli.py`]
        - External boundary: `.req/config.json` presence when `--here` is used.
        - `run_references(args)`: repo-wide references report [`src/usereq/cli.py`]
          - `generate_markdown(..., output_base=project_base)`: render structured markdown with file tree + symbol index and project-relative file paths [`src/usereq/generate_markdown.py`]
            - `_format_output_path(...)`: convert absolute source path to project-home-relative markdown path [`src/usereq/generate_markdown.py`]
        - `run_compress_cmd(args)`: repo-wide compression [`src/usereq/cli.py`]
          - `compress_files(..., output_base=project_base)`: compact multi-file markdown emission with project-relative headers [`src/usereq/compress_files.py`]
            - `_format_output_path(...)`: convert absolute source path to project-home-relative header path [`src/usereq/compress_files.py`]
        - `run_tokens(args)`: docs token report [`src/usereq/cli.py`]
          - `run_files_tokens(paths)`: token report for discovered docs files [`src/usereq/cli.py`]
        - `run_find(args)`: repo-wide construct extraction [`src/usereq/cli.py`]
          - `find_constructs_in_files(...)`: extract tagged constructs [`src/usereq/find_constructs.py`]
      - `run(args)`: project initialization + provider artifact generation [`src/usereq/cli.py`]
        - External boundary: filesystem writes under `project_base`.
        - `ensure_doc_directory(...)`: validate docs directory constraints [`src/usereq/cli.py`]
        - `ensure_test_directory(...)`: validate tests directory constraints [`src/usereq/cli.py`]
        - `ensure_src_directory(...)`: validate source directory constraints [`src/usereq/cli.py`]
        - `maybe_notify_newer_version(...)`: optional network version check [`src/usereq/cli.py`]
        - `save_config(...)`: persist `.req/config.json` [`src/usereq/cli.py`]
        - `list_docs_templates()`: discover packaged doc templates [`src/usereq/cli.py`]
        - `find_requirements_template(...)`: select requirements template [`src/usereq/cli.py`]
        - `generate_guidelines_file_list(...)`: compute `%%GUIDELINES_FILES%%` payload [`src/usereq/cli.py`]
        - Provider artifact generation loop (per source prompt file) [`src/usereq/cli.py`]
          - Artifact activation controls: prompts require `--enable-prompts`; agents require `--enable-agents`; skills are generated by default and suppressed only when `--disable-skills` is present [`src/usereq/cli.py`]
          - Source invariant: prompt/agent/skill artifacts consume `src/usereq/resources/prompts/*.md` only [`src/usereq/cli.py`]
          - `extract_frontmatter(content)`: split YAML front matter vs body [`src/usereq/cli.py`]
          - `extract_description(frontmatter)`: prompt description for provider prompt/agent artifacts [`src/usereq/cli.py`]
          - `extract_argument_hint(frontmatter)`: optional prompt argument hint [`src/usereq/cli.py`]
          - `apply_replacements(text, replacements)`: token substitution in prompt payloads [`src/usereq/cli.py`]
          - `extract_skill_description(frontmatter)`: derive skill `description` from prompt YAML `usage` [`src/usereq/cli.py`]
            - External boundary: `yaml.safe_load(...)`.
          - `yaml_double_quote_escape(value)`: YAML double-quote escaping [`src/usereq/cli.py`]
          - `write_text_file(dst, text)`: filesystem write wrapper [`src/usereq/cli.py`]
          - External boundary: skill artifacts written under `{provider}/skills/req-<prompt_name>/SKILL.md` (or `.opencode/skill/req-<prompt_name>/SKILL.md`).
        - External boundary: provider-specific `models.json` parsing and optional model/tools emission.
        - `generate_guidelines_file_items(guidelines_dir, project_base)`: compute printed substitutions path list [`src/usereq/cli.py`]
        - `_format_install_table(installed_map, prompts_map)`: format installation summary ASCII table [`src/usereq/cli.py`]
          - Invariant: `prompts_map[cli]` includes prompt identifiers installed as prompts/commands, agents, or skills.
- External Boundaries
  - Filesystem: directory creation; file read/write/copy; path resolution.
  - Network: optional `maybe_notify_newer_version(...)`.
  - YAML: `yaml.safe_load(...)` parsing prompt front matter.
  - JSON: configuration/model loading via `json` module.
  - GitHub Actions: not invoked by this process; separate execution unit.

### THR:PROC:main#main
- Entrypoints
  - `__main__()`: module execution boundary [`src/usereq/__main__.py`]
  - `main(argv=None)`: CLI entrypoint [`src/usereq/cli.py`]
- Lifecycle/Trigger
  - Trigger: created by OS process start; executes Python interpreter main thread.
  - Termination: thread exit on `sys.exit(...)` / main return.
- Internal Call-Trace Tree
  - `main(argv=None)`: single-threaded call graph identical to `PROC:main` [`src/usereq/cli.py`]
- External Boundaries
  - None beyond `PROC:main` boundaries (thread is the execution locus for those boundaries).

### PROC:gha:release-uvx
- Entrypoints
  - `workflow_release_uvx.build_release()`: GitHub Actions job dispatcher [`.github/workflows/release-uvx.yml`]
- Lifecycle/Trigger
  - Trigger: GitHub event `push` with tag matching `v*` [`.github/workflows/release-uvx.yml`].
  - Termination: job completion (success/failure) on runner.
- Internal Call-Trace Tree
  - `workflow_release_uvx.build_release()`: orchestrate release pipeline [`.github/workflows/release-uvx.yml`]
    - `step.checkout()`: obtain repository content [`.github/workflows/release-uvx.yml`]
      - External boundary: `actions/checkout@v4`.
    - `step.setup_python()`: install Python runtime [`.github/workflows/release-uvx.yml`]
      - External boundary: `actions/setup-python@v5`.
    - `step.setup_uv()`: install `uv` toolchain [`.github/workflows/release-uvx.yml`]
      - External boundary: `astral-sh/setup-uv@v3`.
    - `step.install_build_dependencies()`: install build deps via `uv pip` [`.github/workflows/release-uvx.yml`]
      - External boundary: package index + network + system site-packages.
    - `step.build_distributions()`: build sdist/wheel via `python -m build` [`.github/workflows/release-uvx.yml`]
      - External boundary: Python build backend + filesystem writes under `dist/`.
    - `step.attest_build_provenance()`: provenance attestation [`.github/workflows/release-uvx.yml`]
      - External boundary: `actions/attest-build-provenance@v1`.
    - `step.create_release_and_upload_assets()`: publish release assets [`.github/workflows/release-uvx.yml`]
      - External boundary: `softprops/action-gh-release@v2` + GitHub API.
- External Boundaries
  - GitHub-hosted runner environment + GitHub API.
  - Third-party GitHub Actions.
  - Package index/network.

### THR:PROC:gha:release-uvx#main
- Entrypoints
  - `workflow_release_uvx.build_release()`: job dispatcher [`.github/workflows/release-uvx.yml`]
- Lifecycle/Trigger
  - Trigger: runner starts job execution.
  - Termination: runner completes steps.
- Internal Call-Trace Tree
  - `workflow_release_uvx.build_release()`: single-threaded step execution [`.github/workflows/release-uvx.yml`]
- External Boundaries
  - None beyond `PROC:gha:release-uvx` boundaries (thread is the execution locus for those boundaries).

## Communication Edges
- None observed between internal execution units under `src/` and `.github/workflows/`.
  - Evidence: `src/usereq/` contains no thread spawning, IPC, sockets, or multiprocessing primitives; `.github/workflows/release-uvx.yml` defines a single job without matrix/fan-out.
