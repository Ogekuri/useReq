## Execution Units Index
- `PROC:main` — CLI process entrypoint for command parsing and dispatch.

## Execution Units
### `PROC:main`
- **Type**: OS process
- **Entrypoint**: `main(argv: Optional[list[str]] = None) -> int`: parse CLI args, route command execution, return exit status [`src/usereq/cli.py`]
- **Threads**: no explicit threads detected.
- **Call Trace**
  - `main(...)`: command router and execution coordinator [`src/usereq/cli.py`]
    - `parse_args(...)`: parse argv into `Namespace` [`src/usereq/cli.py`]
    - `_is_standalone_command(...)`: detect standalone command path [`src/usereq/cli.py`]
      - `run_files_static_check_cmd(...)`: execute static checks on explicit file list [`src/usereq/cli.py`]
        - `load_static_check_from_config(...)`: load per-language static-check arrays from `.req/config.json` [`src/usereq/cli.py`]
        - `dispatch_static_check_for_file(...)`: run one configured static-check entry for one file [`src/usereq/static_check.py`]
          - `StaticCheckBase.run(...)`: iterate resolved files and aggregate result code [`src/usereq/static_check.py`]
            - `StaticCheckBase._check_file(...)` / subclass override: emit header/result or FAIL evidence per file [`src/usereq/static_check.py`]
              - `StaticCheckBase._emit_line(...)`: emit markdown lines with per-line newline termination and append one blank separator line after each file block [`src/usereq/static_check.py`]
    - `_is_project_scan_command(...)`: detect project-scan command path [`src/usereq/cli.py`]
      - `run_project_static_check_cmd(...)`: execute static checks on collected project source files [`src/usereq/cli.py`]
        - `_resolve_project_src_dirs(...)`: resolve project base and effective source dirs [`src/usereq/cli.py`]
        - `_collect_source_files(...)`: collect files from source dirs with extension/exclusion filters [`src/usereq/cli.py`]
        - `load_static_check_from_config(...)`: load per-language static-check arrays from `.req/config.json` [`src/usereq/cli.py`]
        - `dispatch_static_check_for_file(...)`: run one configured static-check entry for one file [`src/usereq/static_check.py`]
          - `StaticCheckBase.run(...)`: iterate resolved files and aggregate result code [`src/usereq/static_check.py`]
            - `StaticCheckBase._check_file(...)` / subclass override: emit header/result or FAIL evidence per file [`src/usereq/static_check.py`]
              - `StaticCheckBase._emit_line(...)`: emit markdown lines with per-line newline termination and append one blank separator line after each file block [`src/usereq/static_check.py`]
    - `run(...)`: install/update flow including `--enable-static-check` parsing and config persistence [`src/usereq/cli.py`]
      - `load_persisted_update_flags(...)`: on `--update`, load persisted boolean install/update flags from `.req/config.json` [`src/usereq/cli.py`]
      - `parse_enable_static_check(...)`: parse one SPEC into one static-check entry object [`src/usereq/static_check.py`]
      - `build_persisted_update_flags(...)`: collect current boolean flag state for persistence in `.req/config.json` [`src/usereq/cli.py`]
      - `save_config(...)`: persist paths, static-check arrays, and persisted boolean flags to `.req/config.json` [`src/usereq/cli.py`]

## Communication Edges
- None across execution units.
- Internal data handoff only within `PROC:main` stack frames (argv, parsed config objects, per-file static-check entry objects).
