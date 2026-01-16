# Analysis Report: useReq Processing Phases

Below are listed the phases and functions performed by the `useReq` tool, analyzing the main flow (`main` -> `run`) and the specific processing for all implemented converters: **Gemini**, **Claude**, **GitHub Copilot**, **Kiro**, and **OpenCode**.

## 1. Common Initial Phases
These operations prepare the environment and normalize data before processing individual prompts.

*   **Argument Parsing** (`parse_args`): Read and validate command-line flags (`--doc`, `--dir`, `--base`, etc.).
*   **Config Loading/Saving** (`load_config`, `save_config`): Read `.req/config.json` in case of updates or persistence of new parameters.
*   **Path Validation** (`ensure_doc_directory`, `ensure_relative`): Verify that documentation and technical directories exist and are relative to the project root.
*   **Update Check** (`maybe_notify_newer_version`): Asynchronously check for new versions of the package on GitHub.
*   **Directory Preparation**: Create the hidden destination folder structure (`.req`, `.codex`, `.github`, `.gemini`, `.claude`, `.opencode`, `.kiro`).
*   **Requirements Management**: If the docs folder is empty, copy the default `requirements.md` template.
*   **Context Generation** (`generate_doc_file_list`, `generate_dir_list`): Create replacement strings for `%%REQ_DOC%%` (markdown files) and `%%REQ_DIR%%` (directory structure) tokens.
*   **CLI Config Loading** (`load_cli_configs`): Load optional configurations (models, tools) for various providers if requested by flags.

## 2. Converter Processing Phases
The tool iterates over all `.md` files found in the `prompts/` folder and, for each one, executes the generation of specific resources.

### A. Gemini Converter
Generates TOML configuration files for use with Gemini tools.

*   **Format Conversion** (`md_to_toml`):
    *   Reads the prompt in Markdown.
    *   Extracts frontmatter and description.
    *   Constructs a TOML file with `description` and `prompt` fields.
*   **Token Replacement** (`replace_tokens`): Injects the generated file and directory lists into the `%%REQ_DOC%%` and `%%REQ_DIR%%` placeholders.
*   **Config Injection** (Inline): If enabled, adds `model` and `tools` fields to the TOML by reading them from the specific Gemini config.

### B. Claude Converter
Generates agent and command definitions for the Claude/Anthropic ecosystem.

*   **Data Extraction** (`extract_frontmatter`): Retrieves metadata and prompt body.
*   **Agent Generation**:
    *   Builds the file in `.claude/agents/` with YAML frontmatter (`name`, `description`).
    *   Injects `model` and `tools` (inline list) if configured.
    *   Performs token replacement in the text body.
*   **Command Generation**:
    *   Creates the file in `.claude/commands/req/`.
    *   Sets frontmatter with reference to the agent (`agent: req-{PROMPT}`).
    *   Defines `allowed-tools` as a CSV string if tools are configured.

### C. GitHub Copilot Converter
Generates resources for GitHub Copilot Workspace and Chat.

*   **Agent Generation**:
    *   Creates the `.agent.md` file in `.github/agents/`.
    *   Defines `name` and `description` in the frontmatter.
    *   Injects `model` and `tools` retrieved from the `copilot` configuration.
    *   Replaces context tokens in the prompt body.
*   **Prompt Stub Generation**:
    *   Creates a `.prompt.md` file in `.github/prompts/` containing only the reference to the agent (`agent: req-{PROMPT}`), serving as an entry point.
*   **Legacy Codex Support** (`copy_with_replacements`): Maintains compatibility by also generating files in `.codex/prompts/` with direct token replacement.

### D. Kiro Converter
Generates resources for the Kiro editor, including prompts and agent definitions.

*   **Prompt Generation** (`copy_with_replacements`):
    *   Creates the markdown file in `.kiro/prompts/`.
    *   Performs standard token replacement.
*   **Resource Preparation** (`generate_kiro_resources`):
    *   Builds a list of `file://` URIs that include the prompt itself and all relevant documentation files.
*   **Agent Building** (`render_kiro_agent`):
    *   Loads the template and agent configuration (`load_kiro_template`).
    *   Populates the agent JSON with name, description, and the calculated resources.
    *   Injects `tools` and `model` if defined in the specific configuration or template.

### E. OpenCode Converter
Generates definitions for OpenCode-compatible agents and commands.

*   **Agent Generation**:
    *   Creates the file in `.opencode/agent/`.
    *   Builds frontmatter with `description`, `mode: all`, and optionally `model` and `tools`.
    *   Assembles the prompt body with replaced tokens.
*   **Command Generation**:
    *   Creates the file in `.opencode/command/`.
    *   Sets frontmatter correlating the command to the agent (`agent: req.{PROMPT}`).
    *   Replicates `model` and `tools` configurations if necessary for command execution.

## 3. Common Final Phases
Closing operations to configure the IDE environment and clean up resources.

*   **Template Distribution**: Copies standard templates (e.g., `srs-template.md`) to the `.req/templates` folder.
*   **VS Code Settings Management**:
    *   `find_vscode_settings_source`: Locates the settings template.
    *   `load_settings`: Loads current project settings and the new ones.
    *   `deep_merge_dict`: Merges configurations preserving existing user preferences.
    *   `build_prompt_recommendations`: Adds generated prompts to the list of recommended files for chat (`chat.promptFilesRecommendations`).
*   **Backup and Writing**:
    *   `save_vscode_backup`: Backs up `settings.json` if changes are detected.
    *   Writes the updated `settings.json` file.
