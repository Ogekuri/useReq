---
title: "Requisiti di useReq"
description: "Specifica dei requisiti software"
date: "2026-01-11"
version: 0.30
author: "Ogekuri"
scope:
  paths:
    - "**/*.py"
    - "**/*.ipynb"
    - "**/*.c"
    - "**/*.h"
    - "**/*.cpp"
  excludes:
    - ".*/**"
visibility: "bozza"
tags: ["markdown", "requisiti", "useReq"]
---

# Requisiti di useReq
**Versione**: 0.30
**Autore**: Ogekuri  
**Data**: 2026-01-11

## Indice
<!-- TOC -->
- [Requisiti di useReq](#requisiti-di-usereq)
  - [Indice](#indice)
  - [Cronologia delle revisioni](#cronologia-delle-revisioni)
  - [1. Introduzione](#1-introduzione)
    - [1.1 Regole del documento](#11-regole-del-documento)
    - [1.2 Scopo del progetto](#12-scopo-del-progetto)
    - [1.3 Componenti e librerie utilizzati](#13-componenti-e-librerie-utilizzati)
    - [1.4 Struttura del progetto](#14-struttura-del-progetto)
    - [1.5 Componenti principali e relazioni](#15-componenti-principali-e-relazioni)
    - [1.6 Ottimizzazioni e prestazioni](#16-ottimizzazioni-e-prestazioni)
    - [1.7 Suite di test](#17-suite-di-test)
  - [2. Requisiti di progetto](#2-requisiti-di-progetto)
    - [2.1 Funzioni di progetto](#21-funzioni-di-progetto)
    - [2.2 Vincoli di progetto](#22-vincoli-di-progetto)
  - [3. Requisiti](#3-requisiti)
    - [3.1 Progettazione e implementazione](#31-progettazione-e-implementazione)
    - [3.2 Funzioni](#32-funzioni)
<!-- TOC -->

## Cronologia delle revisioni
| Data | Versione | Motivazione e descrizione della modifica |
|------|----------|-------------------------------------------|
| 2025-12-31 | 0.0 | Creazione della bozza dei requisiti. |
| 2026-01-01 | 0.1 | Aggiunto script req.sh per eseguire la versione in-development con venv. |
| 2026-01-01 | 0.2 | Aggiunta stampa della versione per invocazioni senza argomenti e con opzioni dedicate. |
| 2026-01-01 | 0.3 | Aggiunta stampa help con versione per invocazioni senza argomenti e stampa versione-only per opzioni dedicate. |
| 2026-01-01 | 0.4 | Aggiunta versione e comando nella stringa di usage dell'help. |
| 2026-01-01 | 0.5 | Aggiornata la generazione dei comandi Gemini in sottocartella dedicata. |
| 2026-01-01 | 0.6 | Aggiunto supporto per la generazione delle risorse Kiro CLI. |
| 2026-01-01 | 0.7 | Modificato il comando --doc per accettare directory e generare elenchi di file. |
| 2026-01-01 | 0.8 | Ripristinata la relativizzazione dei percorsi e organizzazione test sotto temp/. |
| 2026-01-01 | 0.9 | Modificato il comando --dir per processare sottocartelle e generare elenchi di directory. |
| 2026-01-01 | 0.10 | Aggiornata la generazione dei prompt Kiro con il corpo completo del Markdown. |
| 2026-01-01 | 0.11 | Aggiunto supporto per l'opzione --upgrade e aggiornato usage. |
| 2026-01-01 | 0.12 | Aggiunto supporto per l'opzione --uninstall e aggiornato usage. |
| 2026-01-01 | 0.13 | Aggiunta configurazione persistente per --doc e --dir. |
| 2026-01-02 | 0.14 | Aggiunto supporto per l'opzione --update. |
| 2026-01-02 | 0.15 | Aggiunto supporto per l'opzione --remove e ripristino impostazioni. |
| 2026-01-02 | 0.16 | Aggiunto requisito per le stampe in lingua inglese. |
| 2026-01-02 | 0.17 | Aggiunti requisiti per i commenti in lingua italiana nei sorgenti. |
| 2026-01-02 | 0.18 | Aggiunto requisito per l'ordine delle risorse Kiro. |
| 2026-01-09 | 0.19 | Aggiunto supporto per la generazione delle risorse OpenCode. |
| 2026-01-10 | 0.20 | Aggiunto supporto per la generazione delle risorse Claude Code CLI. |
| 2026-01-11 | 0.21 | Modificato supporto OpenCode: rimossa generazione opencode.json, aggiunta generazione agenti individuali in .opencode/agent/ con mode "all". |
| 2026-01-11 | 0.22 | Modificato generazione agenti OpenCode in .opencode/agent/ da JSON a Markdown con front matter. |
| 2026-01-11 | 0.23 | Rimossa generazione della cartella .opencode/prompts. |
| 2026-01-11 | 0.24 | Aggiunto requisito REQ-053: generazione front matter `name` per gli agenti in `.github/agents`. |
| 2026-01-11 | 0.25 | Rimosso obbligo `model: inherit` per gli agenti in `.github/agents` (REQ-053 aggiornato). |
| 2026-01-11 | 0.27 | Aggiunto output dettagliato negli unit test per mostrare lista test, esecuzione corrente, controllo e esito.
| 2026-01-11 | 0.28 | Evitata la generazione di .req/settings.json.absent; --remove non modifica .vscode/settings.json; merge idempotente delle impostazioni VS Code.
| 2026-01-11 | 0.29 | Chiarito comportamento di --remove: la cartella .req deve essere rimossa completamente; rimosso obbligo di ripristino delle impostazioni VS Code durante --remove.
| 2026-01-11 | 0.30 | Aggiunti requisiti e workflow GitHub Actions per build su tag v* e generazione attestazioni per release.

## 1. Introduzione
Questo documento definisce i requisiti software per useReq, una utility CLI che inizializza un progetto con template, prompt e risorse per agenti, assicurando percorsi relativi coerenti rispetto alla radice del progetto.

### 1.1 Regole del documento
Questo documento deve sempre seguire queste regole:
- Questo documento deve essere scritto in italiano.
- I requisiti devono essere formattati come elenco puntato, utilizzando il verbo "deve" per indicare azioni obbligatorie.
- Ogni identificativo (**PRJ-001**, **PRJ-002**, **CTN-001**, **CTN-002**, **DES-001**, **DES-002**, **REQ-001**, **REQ-002**, …) deve essere univoco.
- Ogni identificativo deve iniziare con il prefisso del proprio gruppo di requisiti (PRJ-, CTN-, DES-, REQ-).
- Ogni requisito deve essere identificabile, verificabile e testabile.
- Ad ogni modifica del documento si deve aggiornare il numero di versione e la cronologia delle revisioni, aggiungendo una voce in fondo alla lista.

### 1.2 Scopo del progetto
Lo scopo del progetto e fornire un comando `use-req`/`req` che, dato un progetto, inizializzi file di requisiti, cartelle tecniche e risorse di prompt per strumenti di sviluppo, garantendo percorsi relativi sicuri e un setup ripetibile.

### 1.3 Componenti e librerie utilizzati
- Python 3.11+ come runtime del pacchetto.
- Librerie standard (`argparse`, `json`, `pathlib`, `shutil`, `os`, `re`, `sys`) per parsing CLI, gestione file e percorsi.
- `setuptools` e `wheel` per packaging e distribuzione.

### 1.4 Struttura del progetto
```
.
├── CHANGELOG.md
├── LICENSE
├── README.md
├── TODO.md
├── docs
│   └── requirements.md
├── other-stuff
│   └── templates
│       ├── srs-template-bare.md
│       └── srs-template.md
├── pyproject.toml
└── src
    └── usereq
        ├── __init__.py
        ├── __main__.py
        ├── cli.py
        ├── kiro
        │   └── agent.json
        └── resources
            ├── prompts
            │   ├── analyze.md
            │   ├── change.md
            │   ├── check.md
            │   ├── cover.md
            │   ├── fix.md
            │   ├── new.md
            │   ├── optimize.md
            │   └── write.md
            ├── templates
            │   └── requirements.md
            └── vscode
                └── settings.json
```

### 1.5 Componenti principali e relazioni
- `usereq.cli` contiene la logica principale del comando, il parsing degli argomenti e il flusso di inizializzazione.
- `usereq.__main__` espone l'esecuzione come modulo Python e delega a `usereq.cli.main`.
- `usereq.__init__` fornisce metadati di versione e un re-export dell'entry point `main`.
- `resources/prompts`, `resources/templates` e `resources/vscode` contengono i file sorgenti che il comando copia o integra nel progetto di destinazione.

### 1.6 Ottimizzazioni e prestazioni
Non sono presenti ottimizzazioni prestazionali esplicite; il codice si limita a elaborazioni lineari dei file e dei percorsi necessari all'inizializzazione.

### 1.7 Suite di test
Non sono stati trovati test unitari nel repository.

## 2. Requisiti di progetto
### 2.1 Funzioni di progetto
- **PRJ-001**: Il comando deve inizializzare un progetto creando o aggiornando documenti di requisiti, template tecnici e risorse di prompt in base alla radice indicata dall'utente.
- **PRJ-002**: Il comando deve accettare esattamente una tra le opzioni `--base` o `--here` e i parametri `--doc` e `--dir` per determinare la radice del progetto e i percorsi da gestire.
- **PRJ-003**: Il comando deve generare risorse di prompt per Codex, GitHub e Gemini sostituendo i token di percorso con valori relativi calcolati.
- **PRJ-004**: Il comando deve aggiornare i template locali in `.req/templates` e integrare le impostazioni VS Code quando disponibili.
- **PRJ-005**: L'interfaccia utente deve essere una CLI testuale con messaggi di errore e log di progresso opzionali.

### 2.2 Vincoli di progetto
- **CTN-001**: I valori di `--doc` e `--dir` possono essere percosi assoluti o relativi. I percorsi devono essere normalizzati in percorsi relativi alla radice del progetto passata con `--base` verificando se questa è presente nei pecorsi passati con `--doc` e `--dir`.
- **CTN-002**: Il percorso passato `--doc` e poi normalizzato rispetto a `--base`, deve esistere come directory reale sotto la radice del progetto prima della copia delle risorse.
- **CTN-003**: Il percorso passato `--dir` e poi normalizzato rispetto a `--base`, deve esistere come directory reale sotto la radice del progetto prima della copia delle risorse.
- **CTN-004**: La rimozione di directory `.req` o `.req/templates` preesistenti deve essere consentita solo se tali percorsi si trovano sotto la radice del progetto.
- **CTN-005**: Il comando deve fallire se il progetto specificato non esiste sul filesystem.

## 3. Requisiti
### 3.1 Progettazione e implementazione
- **DES-001**: Il calcolo dei token `%%REQ_DOC%%` e `%%REQ_DIR%%` devono essere sostituiti con la lista dei documenti e delle directory in formato markdown. I documenti e le directory sono ricercati all'interno dei folder specificati con `--doc` e `--dir`.
- **DES-002**: L'origine del template `requirements.md` deve essere la cartella `resources/templates` inclusa nel pacchetto e il comando deve fallire se il template non e disponibile.
- **DES-003**: La conversione dei prompt Markdown in TOML deve estrarre il campo `description` dal front matter e salvare il corpo del prompt in una stringa multilinea.
- **DES-004**: Il merge delle impostazioni VS Code deve supportare file JSONC rimuovendo i commenti e deve fondere ricorsivamente gli oggetti con priorita ai valori del template.
- **DES-005**: Le raccomandazioni `chat.promptFilesRecommendations` devono essere generate a partire dai prompt Markdown disponibili.
- **DES-006**: L'entry point del pacchetto deve esporre `usereq.cli:main` tramite `use-req`, `req` e `usereq`.
- **DES-007**: Gli errori previsti devono essere gestiti tramite un'eccezione dedicata con codice di uscita non nullo.
- **DES-008**: Tutti i commenti nei codici sorgenti devono essere scritti esclusivamente in lingua italiana. Fanno eccezione i commenti di intestazioni dei file sorgenti. Ad esempio, i commenti che indicano versioni e/o autori come "# VERSION:" o "# AUTHORS:" che mantengono la formattazione standard in lingua inglese.
- **DES-009**: Ogni parte importante del codice (classi, funzioni complesse, logica di business, algoritmi critici) deve essere adeguatamente commentata.
- **DES-010**: Ogni nuova funzionalita aggiunta deve includere commenti esplicativi e, in caso di modifica di codice esistente, i commenti preesistenti devono essere aggiornati per riflettere il nuovo comportamento.

### 3.2 Funzioni
- **REQ-001**: Se la directory indicata da `--doc` è vuota, il comando deve generare un file `requirements.md` dal template.
- **REQ-002**: Il comando deve creare le cartelle `.codex/prompts`, `.github/agents`, `.github/prompts`, `.gemini/commands` e `.gemini/commands/req` sotto la radice del progetto.
- **REQ-003**: Per ogni prompt Markdown disponibile, il comando deve copiare il file in `.codex/prompts` e `.github/agents` sostituendo `%%REQ_DOC%%`, `%%REQ_DIR%%` e `%%ARGS%%` con i valori calcolati.
- **REQ-004**: Per ogni prompt Markdown disponibile, il comando deve creare un file `.github/prompts/req.<nome>.prompt.md` che referenzi l'agente `req.<nome>`.
- **REQ-005**: Per ogni prompt Markdown disponibile, il comando deve generare un file TOML in `.gemini/commands/req` con nome `<nome>.toml` (senza prefisso `req.`), convertendo il Markdown e sostituendo `%%REQ_DOC%%`, `%%REQ_DIR%%` e `%%ARGS%%` con valori appropriati per Gemini.
- **REQ-006**: Il comando deve copiare i template in `.req/templates`, sostituendo eventuali template preesistenti.
- **REQ-007**: Se il template VS Code e disponibile, il comando deve creare o aggiornare `.vscode/settings.json` fondendo le impostazioni con quelle esistenti e aggiungendo le raccomandazioni per i prompt.
- **REQ-008**: Il comando deve creare la configurazione `.github/prompts` con front matter che referenzi l'agente in uso.
- **REQ-009**: Il progetto deve includere uno script `req.sh` nella radice del repository per avviare la versione in-development del comando.
- **REQ-010**: Lo script `req.sh` deve essere eseguibile da qualsiasi percorso, risolvere la propria directory, verificare la presenza di `.venv` in tale directory e, se assente, creare il venv e installare i pacchetti da `requirements.txt` prima dell'esecuzione.
- **REQ-011**: Se `.venv` esiste, lo script `req.sh` deve eseguire il comando usando il Python del venv senza reinstallare i pacchetti, inoltrando gli argomenti ricevuti.
- **REQ-012**: Quando il comando `req` viene invocato senza parametri, l'output deve includere il numero di versione definito in `src/usereq/__init__.py` (`__version__`).
- **REQ-013**: Quando il comando `req` viene invocato con l'opzione `--ver` o `--version`, l'output deve includere il numero di versione definito in `src/usereq/__init__.py` (`__version__`).
- **REQ-014**: Quando il comando `req` viene invocato senza parametri, l'output deve includere l'help e il numero di versione definito in `src/usereq/__init__.py` (`__version__`).
- **REQ-015**: Quando il comando `req` viene invocato con l'opzione `--ver` o `--version`, l'output deve contenere solo il numero di versione definito in `src/usereq/__init__.py` (`__version__`).
- **REQ-016**: La stringa di usage dell'help deve includere il comando `req` e la versione `__version__` nel formato `req -c [-h] [--upgrade] [--uninstall] [--remove] [--update] (--base BASE | --here) --doc DOC --dir DIR [--verbose] [--debug] (x.y.z)`.
- **REQ-017**: Il comando deve creare le cartelle `.kiro/agents` e `.kiro/prompts` sotto la radice del progetto.
- **REQ-018**: Per ogni prompt Markdown disponibile, il comando deve copiare il file in `.kiro/prompts` con gli stessi contenuti generati per `.github/agents`.
- **REQ-019**: Per ogni prompt Markdown disponibile, il comando deve generare un file JSON in `.kiro/agents` con nome `req.<nome>.json` utilizzando un template presente in `src/usereq/resources/kiro`.
- **REQ-020**: Nei file JSON Kiro, i campi `name`, `description` e `prompt` devono essere valorizzati rispettivamente con `req-<nome>`, la `description` del front matter del prompt e il corpo del prompt Markdown senza la sezione iniziale tra delimitatori `---`, con i doppi apici `"` escapati.
- **REQ-021**: Il comando deve verificare che il parametro `--doc` indichi una directory esistente, altrimenti deve terminare con errore.
- **REQ-022**: Il comando deve esaminare tutti i file contenuti nella directory `--doc` in ordine alfabetico e sostituire la stringa `%%REQ_DOC%%` con un elenco dei file in formato markdown nella forma `[file1](file1), [file2](file2), [file3](file3)` separati da `", "` (virgola spazio).
- **REQ-023**: L'elenco dei file per la sostituzione di `%%REQ_DOC%%` deve utilizzare percorsi relativi calcolati dallo script, al netto del percorso assoluto e relativi alla home del progetto.
- **REQ-024**: Gli unit test, se implementati, devono essere eseguiti utilizzando la cartella temp/ e le cartelle temporanee devono essere cancellate al termine dell'esecuzione.
- **REQ-025**: Lo script deve relativizzare i percorsi che contengono il percorso della home del progetto (es. temp/project_sample/docs/ diventa docs/).
- **REQ-026**: Il comando deve esaminare tutti i sottofolder contenuti nella directory `--dir` in ordine alfabetico e sostituire la stringa `%%REQ_DIR%%` con un elenco delle directory in formato markdown nella forma `[dir1](dir1), [dir2](dir2), [dir3](dir3)` separati da `", "` (virgola spazio).
- **REQ-027**: Se la directory indicata da `--dir` è vuota, deve utilizzare la directory stessa per la sostituzione di `%%REQ_DIR%%`.
- **REQ-028**: L'elenco delle directory per la sostituzione di `%%REQ_DIR%%` deve utilizzare percorsi relativi calcolati dallo script.
- **REQ-029**: L'opzione `--upgrade` deve eseguire il comando `uv tool install usereq --force --from git+https://github.com/Ogekuri/useReq.git` e terminare con errore se il comando fallisce.
- **REQ-030**: La stringa di usage dell'help deve includere il parametro `--upgrade` come opzione disponibile.
- **REQ-031**: L'opzione `--uninstall` deve eseguire il comando `uv tool uninstall usereq` e terminare con errore se il comando fallisce.
- **REQ-032**: La stringa di usage dell'help deve includere il parametro `--uninstall` come opzione disponibile.
- **REQ-033**: Il comando deve salvare i valori di `--doc` e `--dir` in `.req/config.json` dopo la validazione e la normalizzazione in percorsi relativi alla root di progetto, e prima di selezionare i file presenti in `--doc` e le directory presenti in `--dir`.
- **REQ-034**: Il file `.req/config.json` deve includere i campi `doc` e `dir` con i percorsi relativi e preservare l'eventuale slash finale di `--dir` per permettere il bypass dei parametri `--doc` e `--dir`.
- **REQ-035**: Il comando deve supportare l'opzione `--update` per rieseguire l'inizializzazione utilizzando i parametri salvati in `.req/config.json`.
- **REQ-036**: Quando `--update` e presente, il comando deve verificare la presenza del file `.req/config.json` nella root di progetto e terminare con errore se il file non esiste.
- **REQ-037**: Quando `--update` e presente, il comando deve caricare i campi `doc` e `dir` da `.req/config.json` ed eseguire il flusso come se fossero stati passati `--doc` e `--dir` manualmente, senza riscrivere `.req/config.json`.
- **REQ-038**: Il comando deve supportare l'opzione `--remove` per rimuovere le risorse create dall'installazione nella root di progetto indicata da `--base` o `--here`.
- **REQ-039**: Quando `--remove` e presente, il comando deve richiedere obbligatoriamente `--base` o `--here` e deve rifiutare l'uso di `--doc`, `--dir` o `--update`.
- **REQ-040**: Quando `--remove` e presente, il comando deve verificare l'esistenza del file `.req/config.json` nella root di progetto e terminare con errore se assente.
- **REQ-041**: Prima di modificare `.vscode/settings.json`, il comando deve salvare lo stato originale in un file di backup sotto `.req/` per consentire il ripristino con `--remove`.
- **REQ-042**: Quando `--remove` è presente, il comando non deve ripristinare `.vscode/settings.json` dallo stato originale usando backup conservati in `.req/` (la directory `.req/` sarà rimossa quando l'opzione --remove è usata).
- **REQ-043**: Quando `--remove` è presente, il comando deve rimuovere le risorse create: `.codex/prompts/req.*`, `.github/agents/req.*`, `.github/prompts/req.*`, `.gemini/commands/req/`, `.kiro/agents/req.*`, `.kiro/prompts/req.*`, `.req/templates/`, `.req/config.json` e la cartella `.req/` completa (tutti i file e le sottocartelle devono essere eliminati).
- **REQ-055**: Il file `.req/settings.json.absent` non deve mai essere generato dal comando.
- **REQ-056**: Quando `--remove` è presente, il comando non deve in alcun caso modificare o rimuovere il file `.vscode/settings.json` presente nella root del progetto, anche se in precedenza era stato creato da useReq.
- **REQ-057**: Durante l'installazione o l'aggiornamento delle impostazioni VS Code (`.vscode/settings.json`), il comando deve calcolare il risultato del merge e verificare se il contenuto risultante differisce dal contenuto attualmente presente; se non vi sono differenze semantiche, il comando non deve riscrivere il file né creare backup. Se sono previste modifiche, il comando deve creare un backup solo se il file target già esiste, quindi applicare le modifiche.
- **REQ-044**: Dopo la rimozione, il comando deve eliminare le sottocartelle vuote sotto `.gemini`, `.codex`, `.kiro` e `.github` iterando dal basso verso l'alto.
- **REQ-045**: Tutte le stampe di usage, help, di informazione, verbose o di debug dello script devono essere in lingua inglese.
- **REQ-046**: Nei file JSON Kiro, il campo `resources` deve includere come prima voce il file prompt corrispondente in `.kiro/prompts/req.<nome>.md`, seguito dai link ai requirements.
- **REQ-047**: Per ogni prompt Markdown disponibile, il comando deve generare un file Markdown in `.opencode/agent` con nome `req.<nome>.md` con front matter contenente `description` dalla descrizione del front matter del prompt e `mode` impostato a "all", seguito dal corpo del prompt con le sostituzioni `%%REQ_DOC%%`, `%%REQ_DIR%%` e `%%ARGS%%`.
- **REQ-048**: Il comando deve creare la cartella `.opencode/agent` sotto la radice del progetto.
- **REQ-049**: Il comando deve creare la cartella `.claude/agents` sotto la radice del progetto.
- **REQ-050**: Per ogni prompt Markdown disponibile, il comando deve generare un file `.claude/agents/req.<nome>.md` applicando le stesse sostituzioni di token usate per `.kiro/prompts`.
- **REQ-051**: Nei file `.claude/agents/req.<nome>.md`, il front matter iniziale deve includere i campi `name` e `model`, dove `name` deve essere `req-<nome>` e `model` deve essere `inherit`, e deve preservare `description` valorizzandola dal prompt sorgente.
- **REQ-052**: Quando `--remove` e presente, il comando deve rimuovere i file `.claude/agents/req.*` generati e rimuovere eventuali directory vuote sotto `.claude`, e i file `.opencode/agent/req.*` generati.
- **REQ-058**: Il comando deve creare la cartella `.opencode/command` sotto la radice del progetto.
- **REQ-059**: Per ogni prompt Markdown disponibile, il comando deve copiare il file in `.opencode/command` con nome `req.<nome>.md` utilizzando le stesse sostituzioni (`%%REQ_DOC%%`, `%%REQ_DIR%%`, `%%REQ_PATH%%`, `%%ARGS%%`) applicate per `.kiro/prompts`. Quando `--remove` è presente, i file generati in `.opencode/command` devono essere rimossi e le directory vuote sotto `.opencode` eliminate.
 - **REQ-053**: Per ogni prompt Markdown disponibile, il comando deve generare un file `.github/agents/req.<nome>.agent.md` con front matter che includa `name` impostato a `req-<nome>`, preservando `description` dal prompt sorgente.
- **REQ-054**: Il progetto deve includere una suite di unit test (`tests/test_cli.py`) che verifichi il corretto funzionamento dello script CLI eseguendo le seguenti operazioni: (1) creare una directory di test vuota in `temp/project-test`, rimuovendola se già presente; (2) creare le sottocartelle `docs` e `tech`; (3) eseguire lo script con parametri `--base temp/project-test`, `--doc temp/project-test/docs` e `--dir temp/project-test/tech`; (4) verificare che la struttura dei file e directory generata e i relativi contenuti siano conformi ai requisiti documentati. Inoltre, la suite di test deve fornire output dettagliato durante l'esecuzione, mostrando la lista di tutti i test disponibili, quale test è in esecuzione in quel momento, cosa controllerà (basato sulla descrizione del metodo), e l'esito del test (PASS o FAIL).

 - **REQ-060**: Il comando deve creare la cartella `.claude/commands` e la sua sottocartella `.claude/commands/req` sotto la radice del progetto.
 - **REQ-061**: Per ogni prompt Markdown disponibile, il comando deve copiare il file in `.claude/commands/req` con nome `<nome>.md` (senza il prefisso `req.`), applicando le stesse sostituzioni (`%%REQ_DOC%%`, `%%REQ_DIR%%`, `%%REQ_PATH%%`, `%%ARGS%%`) usate per `.codex/prompts`.
 - **REQ-062**: Quando `--remove` è presente, il comando deve rimuovere i file generati in `.claude/commands/req` e rimuovere eventuali directory vuote sotto `.claude`.
- **REQ-063**: Il repository deve includere un workflow GitHub Actions sotto `.github/workflows/` che si attiva su push di tag che matchano `v*`.
- **REQ-064**: Il workflow deve eseguire la build delle distribuzioni Python del pacchetto (sdist e wheel) producendo gli output sotto `dist/`.
- **REQ-065**: Il workflow deve creare (o aggiornare) una GitHub Release per il tag e caricare come asset tutti i file prodotti in `dist/`.
- **REQ-066**: Il workflow deve generare le artifact attestations (build provenance) per i file in `dist/` usando OIDC, in modo che le attestations risultino visibili nell’interfaccia web di GitHub per la release/asset.
- **REQ-044**: Dopo la rimozione, il comando deve eliminare le sottocartelle vuote sotto `.gemini`, `.codex`, `.kiro` e `.github` iterando dal basso verso l'alto.
- **REQ-045**: Tutte le stampe di usage, help, di informazione, verbose o di debug dello script devono essere in lingua inglese.
- **REQ-046**: Nei file JSON Kiro, il campo `resources` deve includere come prima voce il file prompt corrispondente in `.kiro/prompts/req.<nome>.md`, seguito dai link ai requirements.
- **REQ-047**: Per ogni prompt Markdown disponibile, il comando deve generare un file Markdown in `.opencode/agent` con nome `req.<nome>.md` con front matter contenente `description` dalla descrizione del front matter del prompt e `mode` impostato a "all", seguito dal corpo del prompt con le sostituzioni `%%REQ_DOC%%`, `%%REQ_DIR%%` e `%%ARGS%%`.
- **REQ-048**: Il comando deve creare la cartella `.opencode/agent` sotto la radice del progetto.
- **REQ-049**: Il comando deve creare la cartella `.claude/agents` sotto la radice del progetto.
- **REQ-050**: Per ogni prompt Markdown disponibile, il comando deve generare un file `.claude/agents/req.<nome>.md` applicando le stesse sostituzioni di token usate per `.kiro/prompts`.
- **REQ-051**: Nei file `.claude/agents/req.<nome>.md`, il front matter iniziale deve includere i campi `name` e `model`, dove `name` deve essere `req-<nome>` e `model` deve essere `inherit`, e deve preservare `description` valorizzandola dal prompt sorgente.
- **REQ-052**: Quando `--remove` e presente, il comando deve rimuovere i file `.claude/agents/req.*` generati e rimuovere eventuali directory vuote sotto `.claude`, e i file `.opencode/agent/req.*` generati.
- **REQ-058**: Il comando deve creare la cartella `.opencode/command` sotto la radice del progetto.
- **REQ-059**: Per ogni prompt Markdown disponibile, il comando deve copiare il file in `.opencode/command` con nome `req.<nome>.md` utilizzando le stesse sostituzioni (`%%REQ_DOC%%`, `%%REQ_DIR%%`, `%%REQ_PATH%%`, `%%ARGS%%`) applicate per `.kiro/prompts`. Quando `--remove` è presente, i file generati in `.opencode/command` devono essere rimossi e le directory vuote sotto `.opencode` eliminate.
 - **REQ-053**: Per ogni prompt Markdown disponibile, il comando deve generare un file `.github/agents/req.<nome>.agent.md` con front matter che includa `name` impostato a `req-<nome>`, preservando `description` dal prompt sorgente.
- **REQ-054**: Il progetto deve includere una suite di unit test (`tests/test_cli.py`) che verifichi il corretto funzionamento dello script CLI eseguendo le seguenti operazioni: (1) creare una directory di test vuota in `temp/project-test`, rimuovendola se già presente; (2) creare le sottocartelle `docs` e `tech`; (3) eseguire lo script con parametri `--base temp/project-test`, `--doc temp/project-test/docs` e `--dir temp/project-test/tech`; (4) verificare che la struttura dei file e directory generata e i relativi contenuti siano conformi ai requisiti documentati. Inoltre, la suite di test deve fornire output dettagliato durante l'esecuzione, mostrando la lista di tutti i test disponibili, quale test è in esecuzione in quel momento, cosa controllerà (basato sulla descrizione del metodo), e l'esito del test (PASS o FAIL).

