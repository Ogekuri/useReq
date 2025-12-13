# useReq (Req)

Esegui il tool con `uvx --from git+https://github.com/Ogekuri/useReq.git req` per ricreare `.codex`, `.github`, `.gemini` e `.req` a partire dai prompt e dai template di questo repository:

```bash
uvx --from git+https://github.com/Ogekuri/useReq.git req \
  --base myproject/ \
  --doc myproject/docs/requirements.md \
  --dir myproject/tech_docs/ \
  --verbose --debug
```

Assicurati che `--doc` termini con `.md` e che `--dir` esista già sotto il progetto. Se usi `--here`, ometti `--base` e punta `--doc`/`--dir` a percorsi relativi alla directory corrente.

## Prompts disponibili (Gemini / Codex / Copilot CLI)

Ogni prompt definito in `prompts/` viene esposto come comando `req.<nome>` nelle CLI integrate da Google Gemini, OpenAI Codex e GitHub Copilot. Qui sotto i comandi principali e la descrizione tratta dal front-matter:

| Prompt | Descrizione |
| --- | --- |
| `req.change` | Update the requirements and implement the corresponding changes. |
| `req.check` | Run the requirements check. |
| `req.cover` | Implement changes needed to cover the new requirements. |
| `req.fix` | Fix a defect without changing the requirements. |
| `req.new` | Implement a new requirement and make the corresponding source code changes. |
| `req.write` | Write a requirement draft from the standard template. |

Ogni comando segue il procedimento descritto nel file Markdown corrispondente (passaggi numerati, controlli su `%%REQ_DOC%%` e `%%REQ_DIR%%`, reportistica). Le CLI mostrano lo stesso testo dei prompt (.codex, .github, .gemini) già elaborato da `useReq`.
