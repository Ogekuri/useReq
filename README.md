# useReq (Req)

Esegui `uvx --from git+https://github.com/Ogekuri/useReq.git req` per ricreare `.codex`, `.github`, `.gemini` e `.req` a partire dai prompt e dai template inclusi in questo repository.

## Uso con uvx

- Avvia il comando dalla tua directory home (o da dove vuoi) e specifica `--base <cartella-progetto>` oppure `--here` per usare la directory corrente come base del progetto.
- `--doc` deve essere un percorso relativo alla base del progetto e terminare con `.md`; se il file non esiste viene creato automaticamente dal template `requirements.md`.
- `--dir` deve essere una directory esistente sotto la base del progetto usata come cartella tecnica.
- Puoi aggiungere `--verbose` e `--debug` per avere messaggi di dettaglio e diagnostica.

Esempio valido (non serve usare `--` prima dei flag):

```bash
uvx --from git+https://github.com/Ogekuri/useReq.git req \
  --base myproject/ \
  --doc myproject/docs/requirements.md \
  --dir myproject/tech_docs/ \
  --verbose --debug
```

## Prompt disponibili (Gemini / Codex / Copilot CLI)

I prompt definiti in `src/usereq/resources/prompts/` vengono esposti come comandi `req.<nome>` all'interno di Google Gemini CLI, OpenAI Codex CLI e GitHub Copilot CLI. Le descrizioni riportate nella tabella seguente provengono dal campo `description` del front matter di ciascun prompt:

| Prompt | Descrizione |
| --- | --- |
| `req.change` | Update the requirements and implement the corresponding changes. Usage: req.change <description>. |
| `req.check` | Run the requirements check. Usage: req.check. |
| `req.cover` | Implement changes needed to cover the new requirements. Usage: req.cover. |
| `req.fix` | Fix a defect without changing the requirements. Usage: req.fix <description>. |
| `req.new` | Implement a new requirement and make the corresponding source code changes. Usage: req.new <description>. |
| `req.write` | Write a requirement draft from the standard template. Usage: req.write <language>. |
