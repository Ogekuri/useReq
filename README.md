useReq (Req)

Strumento per inizializzare risorse di progetto a partire da template e prompt.

Scopo
`useReq` (alias `Req`) prepara una struttura di supporto del progetto a partire dai file presenti nel repository di `useReq`. Genera prompt, agent e comandi per integrazione con strumenti di AI, copia script e template personalizzati, e integra impostazioni di editor.

Cosa fa (in breve)
- Copia i prompt Markdown da `prompts/` in tre destinazioni dentro il progetto: `.codex/prompts`, `.github/agents` e `.github/prompts`.
- Converte i Markdown in file TOML per la cartella `.gemini/commands` usando `md2toml.sh`.
- Copia script personalizzati (`req_scripts`) e template (`templates`) in `.req` del progetto.
- Integra il `vscode/settings.json` del repository con quello del progetto facendo un merge ricorsivo e atomico.
- Sostituisce token nei file copiati: `%%REQ_DOC%%`, `%%TECH_DIR%%`, `%%ARGS%%` (con regole diverse per `.md` e `.toml`).
```markdown
useReq (Req)

Strumento per inizializzare risorse di progetto a partire da template e prompt.

Scopo
`useReq` (alias `Req`) prepara una struttura di supporto del progetto a partire dai file presenti nel repository di `useReq`. Genera prompt, agent e comandi per integrazione con strumenti di AI, ricrea template locali, e integra impostazioni di editor.

Cosa fa (in breve)
- Copia i prompt Markdown da `prompts/` in queste destinazioni nel progetto: `.codex/prompts`, `.github/agents` e `.github/prompts`.
- Converte i Markdown in file TOML per `.gemini/commands` usando `scripts/md2toml.sh`.
- Ricrea la directory `.req/templates` nel progetto a partire da `templates/` o `usetemplates/` del repository; il contenuto precedente viene cancellato.
- Non installa più automaticamente script personalizzati nel progetto: il supporto per `req_scripts` è stato rimosso.
- Integra il `vscode/settings.json` del repository con quello del progetto facendo un merge atomico.
- Sostituisce token nei file copiati: `%%REQ_DOC%%`, `%%REQ_DIR%%`, `%%ARGS%%` (con regole diverse per `.md` e `.toml`).

Requisiti
- `bash` (script scritto in POSIX/Bash)
- `readlink` (per normalizzare i percorsi)
- `python3` (usato per `md2toml` e per il merge sicuro di `settings.json`)
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

Dettagli operativi rilevanti
- Pulizia/ricreazione `.req`: All'avvio lo script rimuove qualsiasi contenuto esistente in `PROJECT_BASE/.req` e ricrea la struttura. Questo garantisce che i template copiati siano freschi ma comporta la perdita di eventuali file modificati manualmente in `.req`.
- Creazione di `REQ_DOC`: se il file specificato con `--doc` non esiste nel progetto, lo script lo crea copiando `templates/requirements.md` dal repository (cerca `templates/` o `usetemplates/`).
- Copia dei prompt: per ogni file in `prompts/` lo script genera/aggiorna:
  - `.codex/prompts/req.<name>.md` (sostituzioni token)
  - `.github/agents/req.<name>.agent.md` (sostituzioni token)
  - `.github/prompts/req.<name>.prompt.md` (file agente minimale)
  - `.gemini/commands/req.<name>.toml` (generato tramite `md2toml.sh`)
- Messaggi verbose: quando `--verbose` è attivo, lo script stampa per ciascun file se è stato `COPIATO` (creato) o `SOVRASCRITTO` (esisteva e aggiornato).
- Sostituzioni token: la funzione `copy_and_replace` applica queste regole:
  - `%%REQ_DOC%%` → percorso relativo calcolato (`SUB_REQ_DOC`).
  - `%%REQ_DIR%%` → percorso relativo calcolato (`SUB_TECH_DIR`).
  - `%%ARGS%%` → per `codex`/`github` viene sostituito con la stringa letterale `$ARGUMENTS`; per `gemini`/TOML viene sostituito con `{{args}}`.
- Templates: la directory `.req/templates` nel progetto è ricreata a partire dal contenuto di `templates/` o `usetemplates/` del repository; l'operazione cancella il contenuto precedente nella destinazione.
- `req_scripts`: lo script non copia più contenuti da `req_scripts` o `usereq_scripts` in `PROJECT_BASE/.req/scripts` (funzionalità rimossa).
- `md2toml.sh`: lo script deve essere presente ed eseguibile in `scripts/` e viene chiamato per generare i `.toml`; eventuali errori del convertitore causano il fallimento di `Req.sh`.
- `vscode` settings: se presente `vcode/settings.json` nel repository viene fatto un merge con il file del progetto (`.vscode/settings.json`) in modo sicuro.

Protezioni e avvertenze
- Verifica `--dir`: lo script verifica che la directory tecnica (`--dir`) esista sotto `PROJECT_BASE` e fallisce se non esiste.
- Operazione distruttiva su `.req`: la pulizia iniziale di `.req` è intenzionale; eseguire lo script solo se si è d'accordo a ricreare i template.
- Verbose: usare `--verbose` per vedere quali file sono stati creati o sovrascritti.

Esempio rapido

```bash
mkdir -p /tmp/myproj/docs /tmp/myproj/tech
bash /path/to/useReq/scripts/Req.sh --base /tmp/myproj --doc docs/requirements.md --dir tech --verbose
```

Al termine troverai sotto `/tmp/myproj` le cartelle `.codex`, `.github`, `.gemini` e `.req` popolate.

File sorgente: `scripts/Req.sh`
````