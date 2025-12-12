useReq (Req)

Strumento per inizializzare risorse di progetto a partire da template e prompt.

Scopo
`useReq` (alias `Req`) prepara una struttura di supporto del progetto a partire dai file presenti nel repository di `useReq`. Genera prompt, agent e comandi per integrazione con strumenti di AI, copia script e template personalizzati, e integra impostazioni di editor.

Cosa fa (in breve)
- Copia i prompt Markdown da `prompts/` in tre destinazioni dentro il progetto: `.codex/prompts`, `.github/agents` e `.github/prompts`.
- Converte i Markdown in file TOML per la cartella `.gemini/commands` usando `md2toml.sh`.
- Copia script personalizzati (`usereq_scripts`) e template (`usereq_templates`) in `.usereq` del progetto.
- Integra il `vscode/settings.json` del repository con quello del progetto facendo un merge ricorsivo e atomico.
- Sostituisce token nei file copiati: `%%REQ_DOC%%`, `%%TECH_DIR%%`, `%%ARGS%%` (con regole diverse per `.md` e `.toml`).

Requisiti
- `bash` (script scritto in POSIX/Bash)
- `readlink` (per normalizzare i percorsi)
- `python3` (usato per la conversione md->toml e per il merge sicuro di settings.json)
- Lo script `scripts/md2toml.sh` presente e eseguibile nel repository di `useReq`.

Uso
Esempio di esecuzione dalla directory `useReq`:

```bash
bash scripts/Req.sh --base /percorso/al/progetto --doc docs/requirements.md --dir tech --verbose
```

Opzioni principali:
- `--base <percorso>` : directory radice del progetto da aggiornare (obbligatorio o usare `--here`).
- `--here` : usa la directory corrente come `PROJECT_BASE`.
- `--doc <file.md>` : percorso (relativo rispetto a `PROJECT_BASE`) del file dei requisiti `.md` (obbligatorio).
- `--dir <dir>` : percorso relativo della directory tecnica del progetto (obbligatorio).
- `--verbose` : stampa informazioni aggiuntive.
- `--debug` : stampa informazioni di debug.

Note sul comportamento delle sostituzioni
- Nei file `.md` copiati (`.codex` e `.github/agents`) il token `%%ARGS%%` viene sostituito con la stringa letterale `$ARGUMENTS`.
- Nei file `.gemini/*.toml` il token `%%ARGS%%` viene sostituito con `{{args}}`.
- I token `%%REQ_DOC%%` e `%%TECH_DIR%%` vengono sostituiti con percorsi relativi calcolati rispetto alla root del progetto (il comportamento applica un prefisso `../../` nei prompt copiati per puntare dalla cartella dei prompt alla root del progetto).

Protezioni e avvertenze
- Lo script verifica che `TECH_DIR` esista all'interno del progetto e fallisce se manca (non crea la cartella automaticamente).
- L'integrazione di `settings.json` è atomica: il file di destinazione viene sovrascritto con un merge ricorsivo ma scritto su file temporaneo e poi spostato per evitare corruzione.
- `md2toml.sh` non sostituisce più `$ARGUMENTS`: la gestione dei token è affidata a `useReq`.

Esempio rapido
Supponendo un progetto con struttura minima:

```bash
mkdir -p /tmp/myproj/docs /tmp/myproj/tech
cp -r prompts /path/to/useReq/prompts
bash /path/to/useReq/scripts/Req.sh --base /tmp/myproj --doc docs/requirements.md --dir tech --verbose
```

Al termine troverai sotto `/tmp/myproj` le cartelle `.codex`, `.github`, `.gemini` e `.usereq` popolate.

Domande frequenti
- Q: Lo script modifica file esistenti nel progetto?
  - A: Non sovrascrive i file dei prompt o dei template se non esplicitamente richiesto, ma copia e può sovrascrivere i file di template in `.usereq` e gli agent generati. Usare `--verbose` per vedere le azioni.

File sorgente: `scripts/Req.sh`