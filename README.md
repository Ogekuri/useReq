# useReq aka req (0.0.3)

Run `uvx --from git+https://github.com/Ogekuri/useReq.git req` to recreate `.codex`, `.github`, `.gemini`, and `.req` from the prompts and templates shipped with this repository.

## Usage with uvx

- Launch the command from your home directory (or wherever you prefer) and specify `--base <project-folder>` or `--here` to use the current directory as the project base.
- `--doc` must be a path relative to the project base and must end with `.md`. If the file does not exist it is automatically created from the `requirements.md` template.
- `--dir` must be an existing directory under the project base that serves as the technical folder.
- Add `--verbose` and `--debug` to get detailed and diagnostic output.

Valid example (no need to use `--` before the flags):

```bash
uvx --from git+https://github.com/Ogekuri/useReq.git req \
  --base myproject/ \
  --doc myproject/docs/requirements.md \
  --dir myproject/tech_docs/ \
  --verbose --debug
```

## Available prompts (Gemini / Codex / Copilot CLI)

The prompts defined in `src/usereq/resources/prompts/` are exposed as `req.<name>` commands inside Google Gemini CLI, OpenAI Codex CLI, and GitHub Copilot CLI. The descriptions in the following table come from the `description` field in each prompt’s front matter:

| Prompt | Description |
| --- | --- |
| `req.analyze` | Produce an analysis report. Usage: req.analyze <description>. |
| `req.change` | Update the requirements and implement the corresponding changes. Usage: req.change <description>. |
| `req.check` | Run the requirements check. Usage: req.check. |
| `req.cover` | Implement changes needed to cover the new requirements. Usage: req.cover. |
| `req.fix` | Fix a defect without changing the requirements. Usage: req.fix <description>. |
| `req.new` | Implement a new requirement and make the corresponding source code changes. Usage: req.new <description>. |
| `req.optimize` | Perform an optimizazion without changing the requirements. Usage: req.optimize <description>. |
| `req.write` | Write a requirement draft from the standard template. Usage: req.write <language>. |
