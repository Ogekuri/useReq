---
title: "Requisiti useReq"
description: "Specifica dei Requisiti Software"
date: "2026-02-08"
version: 0.50
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
visibility: "draft"
tags: ["markdown", "requisiti", "useReq"]
---

# Requisiti useReq
**Versione**: 0.50
**Autore**: Ogekuri
**Data**: 2026-02-08

## Indice
<!-- TOC -->
- [Requisiti useReq](#requisiti-usereq)
  - [Indice](#indice)
  - [Cronologia delle Revisioni](#cronologia-delle-revisioni)
  - [1. Introduzione](#1-introduzione)
    - [1.1 Regole del Documento](#11-regole-del-documento)
    - [1.2 Ambito del Progetto](#12-ambito-del-progetto)
    - [1.3 Componenti e Librerie Utilizzati](#13-componenti-e-librerie-utilizzati)
    - [1.4 Struttura del Progetto](#14-struttura-del-progetto)
    - [1.5 Componenti Principali e Relazioni](#15-componenti-principali-e-relazioni)
    - [1.6 Ottimizzazioni e Prestazioni](#16-ottimizzazioni-e-prestazioni)
    - [1.7 Suite di Test](#17-suite-di-test)
  - [2. Requisiti di Progetto](#2-requisiti-di-progetto)
    - [2.1 Funzioni del Progetto](#21-funzioni-del-progetto)
    - [2.2 Vincoli del Progetto](#22-vincoli-del-progetto)
  - [3. Requisiti](#3-requisiti)
    - [3.1 Progettazione e Implementazione](#31-progettazione-e-implementazione)
    - [3.2 Interfaccia CLI e Comportamento Generale](#32-interfaccia-cli-e-comportamento-generale)
    - [3.3 Installazione e Aggiornamenti](#33-installazione-e-aggiornamenti)
    - [3.4 Controllo Versione](#34-controllo-versione)
    - [3.5 Inizializzazione e Configurazione del Progetto](#35-inizializzazione-e-configurazione-del-progetto)
    - [3.6 Generazione Risorse - Comune](#36-generazione-risorse---comune)
    - [3.7 Generazione Risorse - GitHub e Codex](#37-generazione-risorse---github-e-codex)
    - [3.8 Generazione Risorse - Gemini](#38-generazione-risorse---gemini)
    - [3.9 Generazione Risorse - Kiro](#39-generazione-risorse---kiro)
    - [3.10 Generazione Risorse - OpenCode](#310-generazione-risorse---opencode)
    - [3.11 Generazione Risorse - Claude](#311-generazione-risorse---claude)
    - [3.12 Rimozione](#312-rimozione)
    - [3.13 Sviluppo e Test](#313-sviluppo-e-test)
    - [3.14 Workflow CI/CD](#314-workflow-cicd)
<!-- TOC -->

## Cronologia delle Revisioni
| Data | Versione | Motivo e Descrizione del Cambiamento |
|------|---------|----------------------------------|
| 2025-12-31 | 0.0 | Creazione bozza requisiti. |
| 2026-01-26 | 0.45 | Aggiunta flag di abilitazione specifici per provider per la generazione prompt e tabella di riepilogo installazione ristretta ai provider target. |
| 2026-01-27 | 0.46 | Traduzione in Italiano, riorganizzazione e rinumerazione. |
| 2026-02-01 | 0.47 | Aggiunta del parametro --legacy per supportare configurazioni legacy. |
| 2026-02-07 | 0.48 | Aggiunti parametri --write-tech e --overwrite-tech per copia template tecnici. |
| 2026-02-07 | 0.49 | Rimossi flag e sostituzioni dedicate al workflow. |
| 2026-02-08 | 0.50 | Aggiunta sostituzione token %%TECH_PATH%% con il percorso di --tech-dir. |

## 1. Introduzione
Questo documento definisce i requisiti software per useReq, una utility CLI che inizializza un progetto con template, prompt e risorse per agenti, garantendo percorsi relativi coerenti rispetto alla root del progetto.

### 1.1 Regole del Documento
Questo documento deve sempre seguire queste regole:
- Una breve descrizione dello scopo/raggruppamento delle regole del documento.
- Questo documento deve essere scritto in Italiano.
- I requisiti devono essere formattati come elenco puntato, utilizzando il verbo "deve" per indicare azioni obbligatorie.
- Ogni identificatore (**PRJ-001**, **PRJ-002**, **CTN-001**, **CTN-002**, **DES-001**, **DES-002**, **REQ-012**, **REQ-036**, …) deve essere univoco.
- Ogni identificatore deve iniziare con il prefisso del gruppo del requisito (PRJ-, CTN-, DES-, REQ-).
- Ogni requisito deve essere identificabile, verificabile e testabile.
- Ad ogni modifica del documento, il numero di versione e la cronologia delle revisioni devono essere aggiornati aggiungendo una voce in fondo alla lista.

### 1.2 Ambito del Progetto
L'ambito del progetto è fornire un comando `use-req`/`req` che, dato un progetto, inizializza file di requisiti, cartelle tecniche e risorse di prompt per strumenti di sviluppo, garantendo percorsi relativi sicuri e un setup ripetibile.

### 1.3 Componenti e Librerie Utilizzati
- Python 3.11+ come runtime del pacchetto.
- Librerie standard (`argparse`, `json`, `pathlib`, `shutil`, `os`, `re`, `sys`) per parsing CLI, gestione file e percorsi.
- `setuptools` e `wheel` per pacchettizzazione e distribuzione.

### 1.4 Struttura del Progetto
```
.
├── CHANGELOG.md
├── LICENSE
├── package.json
├── pdoc.sh
├── pyproject.toml
├── README.md
├── req.sh
├── requirements.txt
├── tests.sh
├── TODO.md
├── venv.sh
├── WORKFLOW.md
├── docs
│   ├── requirements.md
│   └── requirements_DRAFT.md
├── images
│   └── flowchart.md
├── other-stuff
│   └── templates
│       ├── srs-template-bare.md
│       └── srs-template.md
├── pdoc
│   ├── index.html
│   ├── search.js
│   ├── usereq.html
│   └── usereq
├── src
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
            │   ├── create.md
            │   ├── fix.md
            │   ├── new.md
            │   ├── refactor.md
            │   ├── recreate.md
            │   └── write.md
            ├── templates
            │   └── requirements.md
            └── vscode
                └── settings.json
├── tech
├── temp
└── tests
    ├── __init__.py
    └── test_cli.py
```

### 1.5 Componenti Principali e Relazioni
- `usereq.cli` contiene la logica principale del comando, parsing degli argomenti e flusso di inizializzazione.
- `usereq.__main__` espone l'esecuzione come modulo Python e delega a `usereq.cli.main`.
- `usereq.__init__` fornisce metadati di versione e riesporta l'entry point `main`.
- `resources/prompts`, `resources/templates`, e `resources/vscode` contengono i file sorgente che il comando copia o integra nel progetto target.

### 1.6 Ottimizzazioni e Prestazioni
Non ci sono ottimizzazioni delle prestazioni esplicite identificate; il codice si limita all'elaborazione lineare di file e percorsi necessari per l'inizializzazione.

### 1.7 Suite di Test
Il progetto include una suite di test in `tests/`.

## 2. Requisiti di Progetto
### 2.1 Funzioni del Progetto
- Questa sezione definisce le funzioni principali che il progetto deve implementare.
- **PRJ-001**: Il comando deve inizializzare un progetto creando o aggiornando documenti di requisiti, template tecnici e risorse di prompt basati sulla root indicata dall'utente.
- **PRJ-002**: Il comando deve accettare esattamente una delle opzioni `--base` o `--here` e parametri `--req-dir` e `--tech-dir` per determinare la root del progetto e i percorsi da gestire.
- **PRJ-003**: Il comando deve generare risorse di prompt per Codex, GitHub e Gemini sostituendo i token di percorso con valori relativi calcolati.
- **PRJ-004**: Il comando deve aggiornare i template locali in `.req/templates` e integrare le impostazioni di VS Code quando disponibili.
- **PRJ-005**: L'interfaccia utente deve essere una CLI testuale con messaggi di errore e log di progresso opzionali.

### 2.2 Vincoli del Progetto
- Questa sezione definisce i vincoli e le limitazioni che il progetto deve rispettare.
- **CTN-001**: I valori di `--req-dir` e `--tech-dir` possono essere percorsi assoluti o relativi. I percorsi devono essere normalizzati rispetto alla root del progetto passata con `--base` verificando se presente nei percorsi passati con `--req-dir` e `--tech-dir`.
- **CTN-002**: Il percorso passato a `--req-dir` e poi normalizzato rispetto a `--base`, deve esistere come directory reale sotto la root del progetto prima della copia delle risorse.
- **CTN-003**: Il percorso passato a `--tech-dir` e poi normalizzato rispetto a `--base`, deve esistere come directory reale sotto la root del progetto prima della copia delle risorse.
- **CTN-004**: La rimozione di directory preesistenti `.req` o `.req/templates` deve essere permessa solo se tali percorsi sono sotto la root del progetto.
- **CTN-005**: Il comando deve fallire se il progetto specificato non esiste sul filesystem.

## 3. Requisiti
### 3.1 Progettazione e Implementazione
- Questa sezione delinea i requisiti relativi alle scelte di progettazione e ai dettagli implementativi.
- **DES-001**: Il calcolo dei token `%%REQ_DIR%%` e `%%TECH_DIR%%` deve essere sostituito con la lista di documenti e directory trovati nelle cartelle specificate con `--req-dir` e `--tech-dir`. Quando espansi inline, queste liste devono essere formattate usando notazione inline code (backticks) per ogni elemento invece di link markdown. Per documenti usare la forma `file1`, `file2`, `file3`; per directory usare la forma `dir1/`, `dir2/` (con slash finale).
- **DES-002**: La sorgente del template `requirements.md` deve essere la cartella `resources/templates` inclusa nel pacchetto e il comando deve fallire se il template non è disponibile.
- **DES-003**: La conversione di prompt Markdown in TOML deve estrarre il campo `description` dal front matter e salvare il corpo del prompt in una stringa multilinea.
- **DES-004**: L'unione delle impostazioni VS Code deve supportare file JSONC rimuovendo i commenti e deve unire ricorsivamente gli oggetti con priorità ai valori del template.
- **DES-005**: Le raccomandazioni `chat.promptFilesRecommendations` devono essere generate partendo dai prompt Markdown disponibili.
- **DES-006**: L'entry point del pacchetto deve esporre `usereq.cli:main` via `use-req`, `req`, e `usereq`.
- **DES-007**: Gli errori attesi devono essere gestiti via eccezione dedicata con exit code non-zero.
- **DES-008**: Tutti i commenti nel codice sorgente devono essere scritti esclusivamente in Inglese. Eccezioni sono fatte per header di file sorgente.
- **DES-009**: Ogni parte importante del codice (classi, funzioni complesse, logica di business, algoritmi critici) dovrebbe essere commentata dove necessario.
- **DES-010**: Ogni nuova funzionalità aggiunta dovrebbe includere commenti esplicativi dove applicabile.
- **DES-012**: La funzione `load_cli_configs` deve essere sostituita con `load_centralized_models` che carica i dati dal file `src/usereq/resources/common/models.json`. Quando `legacy_mode` è attivo, deve caricare `models-legacy.json` se esiste, altrimenti fare fallback su `models.json`. Il fallback deve avvenire a livello di file completo, non per singole voci. La struttura di ritorno deve rimanere compatibile: un dizionario `cli_name -> config` dove `config` contiene le chiavi `prompts`, `usage_modes`, e opzionalmente `agent_template`.
- **DES-013**: La funzione `generate_doc_file_list` deve essere rinominata in `generate_req_file_list`. Il comportamento della funzione deve rimanere invariato: scansiona la directory specificata (quella passata con `--req-dir`) e restituisce la lista dei file Markdown (`.md`) presenti in quella directory, ignorando le sottocartelle.
- **DES-014**: La funzione `generate_dir_list` deve essere rinominata in `generate_tech_file_list`. Il comportamento deve essere allineato a `generate_req_file_list`: scansionare la directory specificata (quella passata con `--tech-dir`) e restituire la lista dei file presenti in quella directory (senza ricerca ricorsiva di sottocartelle). Se la directory è vuota o non contiene file, deve restituire il nome della directory stessa come fallback (preservando il comportamento originale solo per il caso di directory vuota).

### 3.2 Interfaccia CLI e Comportamento Generale
- Questa sezione definisce l'interfaccia a riga di comando e i comportamenti generali dell'applicazione.
- **REQ-001**: Quando il comando `req` è invocato senza parametri, l'output deve includere aiuto e numero versione definito in `src/usereq/__init__.py`.
- **REQ-002**: Quando il comando `req` è invocato con l'opzione `--ver` o `--version`, l'output deve contenere solo il numero versione.
- **REQ-003**: La stringa di utilizzo aiuto deve includere il comando `req`, la versione e tutte le opzioni disponibili inclusa `--legacy`, `--write-tech`, e `--overwrite-tech` nel formato `usage: req -c ...`.
- **REQ-004**: Tutti gli output di utilizzo, aiuto, informazione, verbose o debug dello script devono essere in Inglese.
- **REQ-005**: Il comando deve verificare che il parametro `--req-dir` indichi una directory esistente, altrimenti deve terminare con errore.
- **REQ-006**: Il comando deve accettare flag booleani `--enable-claude`, `--enable-codex`, `--enable-gemini`, `--enable-github`, `--enable-kiro`, `--enable-opencode`, `--legacy`, e `--preserve-models` (default false). Quando un flag `--enable-*` è omesso, la CLI deve saltare la creazione di risorse per quel provider. Quando `--legacy` è attivo, la CLI deve attivare la "legacy mode" per il caricamento delle configurazioni. Quando `--preserve-models` è attivo in combinazione con `--update`, la CLI deve preservare il file `.req/models.json` esistente e il flag `--legacy` non ha effetto.
- **REQ-007**: Durante installazioni normali (non upgrade/remove/help), il comando deve richiedere che almeno un flag `--enable-*` sia fornito. Il flag `--legacy` non conta come flag di abilitazione del provider. Se nessun flag `--enable-*` è fornito, deve stampare un messaggio di errore in Inglese e uscire.
- **REQ-008**: La tabella riassuntiva di installazione ASCII deve includere righe solo per i target CLI i cui prompt sono stati installati durante l'invocazione corrente.
- **REQ-085**: Il comando deve supportare i flag booleani `--write-tech` e `--overwrite-tech` (default false). Questi flag attivano la copia dei contenuti della directory `src/usereq/resources/tech/` nella directory specificata da `--tech-dir`. L'operazione di copia deve essere eseguita prima della chiamata a `generate_tech_file_list`.
- **REQ-086**: Quando `--write-tech` è attivo, il comando deve copiare tutti i file presenti in `src/usereq/resources/tech/` nella directory target specificata da `--tech-dir`, preservando i file esistenti (senza sovrascriverli) se hanno lo stesso nome.
- **REQ-087**: Quando `--overwrite-tech` è attivo, il comando deve copiare tutti i file presenti in `src/usereq/resources/tech/` nella directory target specificata da `--tech-dir`, sovrascrivendo i file esistenti se hanno lo stesso nome.
- **REQ-088**: I flag `--write-tech` e `--overwrite-tech` sono mutualmente esclusivi: se entrambi sono forniti contemporaneamente, il comando deve terminare con errore.
- **REQ-089**: La copia dei template tecnici deve avvenire solo quando almeno uno dei due flag (`--write-tech` o `--overwrite-tech`) è attivo. Se nessuno dei due flag è fornito, l'operazione di copia non deve essere eseguita.

### 3.3 Installazione e Aggiornamenti
- Questa sezione copre i requisiti per l'installazione, l'aggiornamento e la disinstallazione del tool e delle risorse.
- **REQ-009**: L'opzione `--upgrade` deve eseguire il comando `uv tool install usereq --force --from git+https://github.com/Ogekuri/useReq.git` e terminare con errore se fallisce.
- **REQ-010**: La stringa di aiuto deve includere `--upgrade` come opzione disponibile.
- **REQ-011**: L'opzione `--uninstall` deve eseguire `uv tool uninstall usereq` e terminare con errore se fallisce.
- **REQ-012**: La stringa di aiuto deve includere `--uninstall` come opzione disponibile.
- **REQ-013**: Dopo il completamento con successo di un'installazione o aggiornamento, la CLI deve stampare una singola riga in Inglese informando l'utente del successo includendo il percorso root risolto.
- **REQ-014**: Immediatamente dopo il messaggio di successo, la CLI deve stampare una lista dei file e directory scoperti per la sostituzione dei token `%%REQ_DIR%%` e `%%TECH_DIR%%`, prefissati da `- `.
- **REQ-015**: Immediatamente dopo la lista file, la CLI deve stampare una tabella leggibile ASCII descrivendo quali prompt e moduli sono stati installati per ogni target CLI.

### 3.4 Controllo Versione
- Questa sezione specifica i requisiti per la verifica online di nuove versioni del software.
- **REQ-016**: Il comando, dopo validazione input e prima di modifiche filesystem, deve verificare disponibilità online di nuova versione tramite chiamata HTTP GET a GitHub API con timeout 1 secondo.
- **REQ-017**: Se la chiamata ha successo e la versione remota è maggiore di `__version__`, il comando deve stampare un messaggio in Inglese indicando versione corrente, disponibile e comando per aggiornare.

### 3.5 Inizializzazione e Configurazione del Progetto
- Questa sezione descrive come il progetto deve essere inizializzato e configurato.
- **REQ-018**: Se la directory indicata da `--req-dir` è vuota, il comando deve generare un file `requirements.md` dal template.
- **REQ-019**: Il progetto deve includere uno script `req.sh` nella root repository per avviare la versione in sviluppo.
- **REQ-020**: Lo script `req.sh` deve essere eseguibile da qualsiasi percorso, risolvere la propria directory, verificare `.venv` e crearlo se assente.
- **REQ-021**: Se `.venv` esiste, `req.sh` deve eseguire il comando usando il Python del venv inoltrando gli argomenti.
- **REQ-022**: Il comando deve salvare i valori di `--req-dir` e `--tech-dir` in `.req/config.json` come percorsi relativi.
- **REQ-023**: Il file `.req/config.json` deve includere campi `req-dir` e `tech-dir` preservando slash finali.
- **REQ-024**: Il comando deve supportare l'opzione `--update` per rieseguire l'inizializzazione usando parametri salvati.
- **REQ-025**: Quando `--update` è presente, il comando deve verificare presenza di `.req/config.json` e terminare con errore se assente.
- **REQ-026**: Con `--update`, il comando deve caricare `req-dir` e `tech-dir` da config ed eseguire il flusso come se passati manualmente.
- **REQ-027**: Il comando deve copiare i template in `.req/templates`, rimpiazzando pre-esistenti.
- **REQ-084**: Il comando deve copiare il file di configurazione modelli in `.req/models.json`, rimpiazzando il file pre-esistente se presente, a meno che `--preserve-models` sia attivo. Quando `--preserve-models` NON è attivo: se `--legacy` NON è attivo, deve copiare `models.json` dalle risorse del pacchetto (`src/usereq/resources/common/models.json`); se `--legacy` è attivo E il file `models-legacy.json` è caricato con successo (cioè quando esiste), deve copiare `models-legacy.json` dalle risorse del pacchetto (`src/usereq/resources/common/models-legacy.json`); se `--legacy` è attivo ma `models-legacy.json` non esiste, deve copiare `models.json`. Questa copia deve avvenire dopo la creazione della directory `.req` e dopo il salvataggio di `config.json`.
- **REQ-028**: Se il template VS Code è disponibile, deve creare o aggiornare `.vscode/settings.json` unendo impostazioni.
- **REQ-029**: Prima di modificare `.vscode/settings.json`, deve salvare lo stato originale in backup sotto `.req/` (per ripristino con remove).
- **REQ-030**: L'aggiornamento di `.vscode/settings.json` deve avvenire solo se ci sono differenze semantiche; se non ce ne sono, non deve riscrivere né creare backup.
- **REQ-031**: Il file `.req/settings.json.absent` non deve mai essere generato.

### 3.6 Generazione Risorse - Comune
- Questa sezione contiene i requisiti comuni per la generazione delle risorse per i vari provider AI.
- **REQ-032**: Il comando deve sostituire `%%REQ_DIR%%` con la lista di file in `--req-dir` formattati come inline code, relativi alla root.
- **REQ-033**: La lista file per `%%REQ_DIR%%` deve usare percorsi relativi netti.
- **REQ-034**: Lo script deve relativizzare percorsi che contengono il path home progetto.
- **REQ-035**: Il comando deve sostituire `%%TECH_DIR%%` con la lista di sottocartelle in `--tech-dir` formattate come inline code con slash finale.
- **REQ-036**: Se la directory `--tech-dir` è vuota, usare la directory stessa per `%%TECH_DIR%%`.
- **REQ-037**: La lista directory per `%%TECH_DIR%%` deve usare percorsi relativi.
- **REQ-090**: Il comando deve sostituire `%%TECH_PATH%%` con il percorso passato con `--tech-dir`, normalizzato rispetto alla root del progetto.
- **REQ-038**: Il comando deve supportare opzioni `--enable-models` e `--enable-tools` per includere campi `model` e `tools` nei file generati.
- **REQ-039**: Con `--enable-models`, includere `model: <valore>` se presente in `config.json` della risorsa.
- **REQ-040**: Con `--enable-tools`, includere `tools` derivato da `usage_modes` se presente in `config.json`.
- **REQ-041**: L'inclusione di `model` e `tools` è condizionale alla validità del file di configurazione centralizzato (`models.json` o `models-legacy.json` a seconda della modalità legacy).
- **REQ-082**: La CLI deve caricare le configurazioni per la generazione dei prompt. Quando `--preserve-models` è attivo in combinazione con `--update` e il file `.req/models.json` esiste, deve caricare le configurazioni da `.req/models.json`; in questo caso il flag `--legacy` non ha effetto. Quando `--preserve-models` NON è attivo o il file `.req/models.json` non esiste: deve caricare dal file centralizzato `src/usereq/resources/common/models.json`, leggendo la voce corrispondente al CLI (`<cli>`) per ottenere `prompts` e `usage_modes`; se il flag `--legacy` è attivo, la CLI deve prima verificare la presenza del file `src/usereq/resources/common/models-legacy.json`; se esiste, deve caricarlo al posto di `models.json` (fallback a livello di file, non di singole voci); se `models-legacy.json` non esiste, deve usare `models.json`. I file `src/usereq/resources/<cli>/config.json` non devono più essere utilizzati e possono essere rimossi dal disco.
- **REQ-083**: La stringa di aiuto deve includere `--legacy` e `--preserve-models` come opzioni disponibili.
- **REQ-044**: La generazione risorse descritta nelle sezioni specifiche deve eseguire solo quando il flag `--enable-<provider>` corrispondente è attivo.
- **REQ-045**: Il prompt `recreate` deve essere aggiunto a `src/usereq/resources/prompts` e trattato come prompt standard. Deve essere generato per ogni provider abilitato.

### 3.7 Generazione Risorse - GitHub e Codex
- Requisiti specifici per la generazione di risorse per GitHub Copilot e Codex.
- **REQ-046**: Il comando deve creare cartelle `.codex/prompts`, `.github/agents`, `.github/prompts`.
- **REQ-047**: Per ogni prompt Markdown, copiare in `.codex/prompts` e `.github/agents` con sostituzioni.
- **REQ-048**: Per ogni prompt Markdown, creare file `.github/prompts/req.<name>.prompt.md`.
- **REQ-049**: Creare configurazione `.github/prompts` con front matter che referenzia l'agente solo se `--prompts-use-agents` è abilitato.
- **REQ-050**: Per ogni prompt, generare `.github/agents/req.<name>.agent.md` con front matter incluso `name`.

### 3.8 Generazione Risorse - Gemini
- Requisiti specifici per Gemin.
- **REQ-051**: Il comando deve creare cartelle `.gemini/commands` e `.gemini/commands/req`.
- **REQ-052**: Per ogni prompt Markdown, generare file TOML in `.gemini/commands/req` convertendo Markdown e sostituendo token.

### 3.9 Generazione Risorse - Kiro
- Requisiti specifici per Kiro.
- **REQ-053**: Il comando deve creare cartelle `.kiro/agents` e `.kiro/prompts`.
- **REQ-054**: Per ogni prompt Markdown, copiare in `.kiro/prompts` mantenendo front matter.
- **REQ-055**: Per ogni prompt, generare JSON in `.kiro/agents` usando template agent da `config.json`.
- **REQ-056**: In file Kiro JSON, popolare campi `name`, `description`, `prompt` (body escaped).
- **REQ-057**: In file Kiro JSON, popolare campo `resources` con il file prompt relativo e requisiti.
- **REQ-058**: Popolare `tools` e `allowedTools` in `.kiro/agents` basandosi su `config.json` e mode prompt.

### 3.10 Generazione Risorse - OpenCode
- Requisiti specifici per OpenCode.
- **REQ-059**: Creare cartella `.opencode/agent` e `.opencode/command`.
- **REQ-060**: Per ogni prompt, generare Markdown in `.opencode/agent` con front matter e mode "all".
- **REQ-061**: Per ogni prompt, generare file in `.opencode/command` con front matter (agent ref se abilitato, model/tools opzionali).

### 3.11 Generazione Risorse - Claude
- Requisiti specifici per Claude.
- **REQ-062**: Creare cartella `.claude/agents`.
- **REQ-063**: Generare file `.claude/agents/req.<name>.md` con sostituzioni.
- **REQ-064**: In `.claude/agents`, includere front matter con `name`, `description`. `model`/`tools` solo se abilitati e configurati.
- **REQ-065**: Creare cartella `.claude/commands/req`.
- **REQ-066**: Generare file in `.claude/commands/req` con front matter (agent ref se abilitato, model/tools/allowed-tools opzionali).

### 3.12 Rimozione
- Questa sezione specifica il comportamento per la rimozione delle risorse generate.
- **REQ-067**: Il comando deve supportare l'opzione `--remove` per rimuovere risorse create.
- **REQ-068**: Con `--remove`, richiedere obbligatoriamente `--base` o `--here` e rifiutare `--req-dir`, `--tech-dir`, `--update`.
- **REQ-069**: Con `--remove`, verificare esistenza `.req/config.json`.
- **REQ-070**: Con `--remove`, NON ripristinare `.vscode/settings.json` dai backup.
- **REQ-071**: Con `--remove`, rimuovere risorse create: `.codex`, `.github`, `.gemini`, `.kiro`, `.req`, etc.
- **REQ-072**: Dopo rimozione, eliminare sottocartelle vuote nei provider folder.
- **REQ-073**: Con `--remove`, rimuovere file generati in `.claude` e `.opencode` ed eliminare directory vuote.
- **REQ-074**: Con `--remove`, non modificare mai `.vscode/settings.json` esistente.

### 3.13 Sviluppo e Test
- Requisiti per lo sviluppo e l'esecuzione dei test.
- **REQ-075**: Unit test devono usare esclusivamente la cartella `temp/` (o `tests/temp/`).
- **REQ-076**: Il progetto deve includere suite `tests/test_cli.py` che verifica operazioni CLI in cartella temporanea.
- **REQ-077**: Unit test non devono creare/modificare file fuori da `temp/`.

### 3.14 Workflow CI/CD
- Requisiti per l'automazione CI/CD.
- **REQ-078**: Il repository deve includere workflow GitHub Actions che scatta su push di tag `v*`.
- **REQ-079**: Il workflow deve eseguire build pacchetto Python (sdist e wheel) in `dist/`.
- **REQ-080**: Il workflow deve creare GitHub Release per il tag e caricare asset da `dist/`.
- **REQ-081**: Il workflow deve generare attestazioni artefatto per file in `dist/`.
