# Workflow Analysis

## Project Initialization and Update
*   **Module**: `src/usereq/cli.py`
    *   `main()`: Entry point for the CLI tool. [src/usereq/cli.py, 2006-2035]
        *   description: Orchestrates argument parsing, version checking, and command execution.
        *   input: Command line arguments (list[str])
        *   output: Exit code (int)
        *   calls: `maybe_print_version()`, `run_upgrade()`, `run_uninstall()`, `maybe_notify_newer_version()`, `build_parser()`, `parse_args()`, `run_remove()`, `run()`
    *   `run()`: Core logic for initializing or updating the project. [src/usereq/cli.py, 1212-1600+]
        *   description: Validates inputs, manages configuration, ensures directories, and generates resources.
        *   input: Parsed arguments (Namespace)
        *   output: None
        *   calls: `load_config()`, `ensure_req_directory()`, `ensure_doc_directory()`, `ensure_test_directory()`, `ensure_src_directory()`, `make_relative_if_contains_project()`, `ensure_relative()`, `resolve_absolute()`, `copy_tech_templates()`, `maybe_notify_newer_version()`, `save_config()`, `compute_sub_path()`, `make_relative_token()`, `find_template_source()`, `generate_req_file_list()`, `generate_tech_file_list()`, `load_kiro_template()`, `load_centralized_models()`, `extract_frontmatter()`, `extract_description()`, `apply_replacements()`, `get_model_tools_for_prompt()`, `write_text_file()`, `generate_req_file_items()`, `generate_tech_file_items()`, `_format_install_table()`
        *   `load_config()`: Loads existing configuration from req.json. [src/usereq/cli.py, 486-523]
            *   description: Reads and parses the project configuration file.
            *   input: Project base path (Path)
            *   output: Configuration dictionary (dict)
        *   `save_config()`: Saves configuration to req.json. [src/usereq/cli.py, 463-483]
            *   description: Writes the current configuration to disk.
            *   input: Project base path, directory paths (req, tech, doc, test, src)
            *   output: None
        *   `maybe_notify_newer_version()`: Checks for updates. [src/usereq/cli.py, 298-339]
            *   description: Queries GitHub API for the latest release and warns if outdated.
            *   input: Timeout (float)
            *   output: None
            *   calls: `load_package_version()`, `normalize_release_tag()`, `is_newer_version()`
        *   `copy_tech_templates()`: Copies technical templates. [src/usereq/cli.py, 623-659]
            *   description: Copies template files from resources to the tech directory.
            *   input: Destination path (Path), overwrite flag (bool)
            *   output: Number of files copied (int)
            *   calls: `copy_with_replacements()`
        *   `load_centralized_models()`: Loads model configurations. [src/usereq/cli.py, 945-993]
            *   description: Loads model definitions from JSON resources, handling legacy and preserve modes.
            *   input: Resource root (Path), legacy mode (bool), preserve path (Optional[Path])
            *   output: Configuration dictionary (dict)
            *   calls: `strip_json_comments()`, `deep_merge_dict()`

## Documentation Generation
*   **Module**: `src/usereq/pdoc_utils.py`
    *   `generate_pdoc_docs()`: Generates API documentation. [src/usereq/pdoc_utils.py, 31-84]
        *   description: Runs pdoc to generate HTML documentation for specified modules.
        *   input: Output directory (Path), modules (Sequence[str] | str), all_submodules (bool)
        *   output: None
        *   calls: `_normalize_modules()`, `_run_pdoc()`
    *   `_run_pdoc()`: Executes pdoc subprocess. [src/usereq/pdoc_utils.py, 19-28]
        *   description: Helper to run the pdoc command via subprocess.
        *   input: Command (list[str]), environment (dict), working directory (Path)
        *   output: Completed process object (subprocess.CompletedProcess)
