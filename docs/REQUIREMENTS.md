---
title: "Requisiti useReq"
description: "Specifica dei Requisiti Software"
date: "2026-02-16"
version: 0.64
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
**Versione**: 0.64
**Autore**: Ogekuri
**Data**: 2026-02-16

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
    - [3.15 Analisi Sorgenti e Linguaggi Supportati](#315-analisi-sorgenti-e-linguaggi-supportati)
    - [3.16 Conteggio Token](#316-conteggio-token)
    - [3.17 Generazione Markdown di Riferimento](#317-generazione-markdown-di-riferimento)
    - [3.18 Compressione Sorgenti](#318-compressione-sorgenti)
    - [3.19 Comandi Standalone su File Arbitrari](#319-comandi-standalone-su-file-arbitrari)
    - [3.20 Comandi di Progetto su Directory Sorgenti](#320-comandi-di-progetto-su-directory-sorgenti)
<!-- TOC -->

## Cronologia delle Revisioni
| Data | Versione | Motivo e Descrizione del Cambiamento |
|------|---------|----------------------------------|
| 2025-12-31 | 0.0 | Creazione bozza requisiti. |
| 2026-01-26 | 0.45 | Aggiunta flag di abilitazione specifici per provider per la generazione prompt e tabella di riepilogo installazione ristretta ai provider target. |
| 2026-01-27 | 0.46 | Traduzione in Italiano, riorganizzazione e rinumerazione. |
| 2026-02-01 | 0.47 | Aggiunta del parametro --legacy per supportare configurazioni legacy. |
| 2026-02-07 | 0.48 | Aggiunti parametri --write-guidelines e --overwrite-guidelines per copia template tecnici. |
| 2026-02-07 | 0.49 | Rimossi flag e sostituzioni dedicate al workflow. |
| 2026-02-08 | 0.50 | Aggiunta sostituzione token %%GUIDELINES_PATH%% con il percorso di --guidelines-dir. |
| 2026-02-08 | 0.51 | Aggiunto parametro --docs-dir e sostituzione token %%DOC_PATH%%. |
| 2026-02-08 | 0.52 | Ignorati file che iniziano con punto nella lista di --req-dir e --guidelines-dir. |
| 2026-02-08 | 0.53 | Aggiunto parametro --tests-dir e sostituzione token %%TEST_PATH%%. |
| 2026-02-08 | 0.54 | Aggiornata sostituzione token %%TEST_PATH%% con slash finale. |
| 2026-02-08 | 0.55 | Aggiornata sostituzione token %%TEST_PATH%% con backticks e slash finale. |
| 2026-02-08 | 0.56 | Aggiunto parametro --src-dir multiplo e sostituzione token %%SRC_PATHS%%. |
| 2026-02-13 | 0.57 | Aggiunta generazione skill Codex in .codex/skills/req con SKILL.md per ogni prompt. |
| 2026-02-14 | 0.58 | Rimosso parametro --req-dir e rimossa sostituzione token %%REQ_DIR%%/%%REQ_PATH%%. |
| 2026-02-14 | 0.59 | Rinominati i parametri CLI `--doc-dir`/`--test-dir` in `--docs-dir`/`--tests-dir` e aggiornati i campi configurazione correlati. |
| 2026-02-14 | 0.60 | Rinominati i parametri CLI `--write-guidelines`/`--overwrite-guidelines` in `--add-guidelines`/`--copy-guidelines`. |
| 2026-02-15 | 0.61 | Aggiunti comandi `--files-tokens`, `--files-references`, `--files-compress`, `--references`, `--compress` e relativi moduli: analisi sorgenti multi-linguaggio, conteggio token, generazione markdown di riferimento, compressione sorgenti. |
| 2026-02-15 | 0.62 | Aggiornati i requisiti DES-008..DES-010 imponendo documentazione Doxygen completa, strutturata e in Inglese per tutti i componenti codice. |
| 2026-02-15 | 0.63 | Rimossi i requisiti DES-008..DES-010 relativi alle modalità di documentazione nei sorgenti. |
| 2026-02-16 | 0.64 | Aggiunto comando CLI `--tokens` per conteggio token dei file presenti in `--docs-dir` con contesto `--base`/`--here`. |

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
- `tiktoken` per il conteggio token compatibile con modelli OpenAI/Claude.

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
        ├── compress.py
        ├── compress_files.py
        ├── generate_markdown.py
        ├── source_analyzer.py
        ├── token_counter.py
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
├── guidelines
├── temp
└── tests
    ├── __init__.py
    └── test_cli.py
```

### 1.5 Componenti Principali e Relazioni
- `usereq.cli` contiene la logica principale del comando, parsing degli argomenti e flusso di inizializzazione.
- `usereq.__main__` espone l'esecuzione come modulo Python e delega a `usereq.cli.main`.
- `usereq.__init__` fornisce metadati di versione e riesporta l'entry point `main`.
- `usereq.source_analyzer` implementa l'analisi multi-linguaggio del codice sorgente, estraendo definizioni, commenti e struttura.
- `usereq.token_counter` implementa il conteggio token e caratteri tramite la libreria `tiktoken`.
- `usereq.generate_markdown` implementa la generazione di markdown strutturato di riferimento per il contesto LLM.
- `usereq.compress` implementa la compressione del codice sorgente rimuovendo commenti, righe vuote e spazi ridondanti.
- `usereq.compress_files` implementa la compressione e concatenazione di file sorgente multipli.
- `resources/prompts`, `resources/templates`, e `resources/vscode` contengono i file sorgente che il comando copia o integra nel progetto target.

### 1.6 Ottimizzazioni e Prestazioni
Non ci sono ottimizzazioni delle prestazioni esplicite identificate; il codice si limita all'elaborazione lineare di file e percorsi necessari per l'inizializzazione.

### 1.7 Suite di Test
Il progetto include una suite di test in `tests/`.
- `tests/test_cli.py` verifica le operazioni CLI in cartella temporanea.
- `tests/test_source_analyzer.py` verifica l'analisi multi-linguaggio su tutti i 20 linguaggi supportati.
- `tests/test_token_counter.py` verifica il conteggio token e caratteri.
- `tests/test_generate_markdown.py` verifica la generazione di markdown di riferimento.
- `tests/test_compress.py` verifica la compressione del codice sorgente.
- `tests/test_files_commands.py` verifica i comandi `--files-tokens`, `--files-references`, `--files-compress`, `--references`, `--compress`.

## 2. Requisiti di Progetto
### 2.1 Funzioni del Progetto
- Questa sezione definisce le funzioni principali che il progetto deve implementare.
- **PRJ-001**: Il comando deve inizializzare un progetto creando o aggiornando documenti di requisiti, template tecnici e risorse di prompt basati sulla root indicata dall'utente.
- **PRJ-002**: Il comando deve accettare esattamente una delle opzioni `--base` o `--here` e i parametri `--guidelines-dir`, `--docs-dir`, `--tests-dir`, e `--src-dir` per determinare la root del progetto e i percorsi da gestire.
- **PRJ-003**: Il comando deve generare risorse di prompt per Codex, GitHub e Gemini sostituendo i token di percorso con valori relativi calcolati.
- **PRJ-004**: Il comando deve aggiornare i template locali in `.req/templates` e integrare le impostazioni di VS Code quando disponibili.
- **PRJ-005**: L'interfaccia utente deve essere una CLI testuale con messaggi di errore e log di progresso opzionali.

### 2.2 Vincoli del Progetto
- Questa sezione definisce i vincoli e le limitazioni che il progetto deve rispettare.
- **CTN-001**: I valori di `--guidelines-dir`, `--docs-dir`, `--tests-dir`, e `--src-dir` possono essere percorsi assoluti o relativi. I percorsi devono essere normalizzati rispetto alla root del progetto passata con `--base` verificando se presente nei percorsi passati con `--guidelines-dir`, `--docs-dir`, `--tests-dir`, e `--src-dir`.
- **CTN-002**: La directory requisiti del progetto deve coincidere con il percorso `--docs-dir` normalizzato sotto la root del progetto e non deve essere configurabile con un parametro dedicato.
- **CTN-003**: Il percorso passato a `--guidelines-dir` e poi normalizzato rispetto a `--base`, deve esistere come directory reale sotto la root del progetto prima della copia delle risorse.
- **CTN-006**: Il percorso passato a `--docs-dir` e poi normalizzato rispetto a `--base`, deve esistere come directory reale sotto la root del progetto prima della copia delle risorse.
- **CTN-007**: Il percorso passato a `--tests-dir` e poi normalizzato rispetto a `--base`, deve esistere come directory reale sotto la root del progetto prima della copia delle risorse.
- **CTN-008**: Il percorso passato a `--src-dir` e poi normalizzato rispetto a `--base`, deve esistere come directory reale sotto la root del progetto prima della copia delle risorse.
- **CTN-004**: La rimozione di directory preesistenti `.req` o `.req/templates` deve essere permessa solo se tali percorsi sono sotto la root del progetto.
- **CTN-005**: Il comando deve fallire se il progetto specificato non esiste sul filesystem.

## 3. Requisiti
### 3.1 Progettazione e Implementazione
- Questa sezione delinea i requisiti relativi alle scelte di progettazione e ai dettagli implementativi.
- **DES-001**: Il calcolo del token `%%GUIDELINES_FILES%%` deve essere sostituito con la lista di directory trovate nella cartella specificata con `--guidelines-dir`. Quando espanso inline, la lista deve essere formattata usando notazione inline code (backticks) per ogni elemento nella forma `dir1/`, `dir2/` (con slash finale).
- **DES-002**: La sorgente del template `requirements.md` deve essere la cartella `resources/templates` inclusa nel pacchetto e il comando deve fallire se il template non è disponibile.
- **DES-003**: La conversione di prompt Markdown in TOML deve estrarre il campo `description` dal front matter e salvare il corpo del prompt in una stringa multilinea.
- **DES-004**: L'unione delle impostazioni VS Code deve supportare file JSONC rimuovendo i commenti e deve unire ricorsivamente gli oggetti con priorità ai valori del template.
- **DES-005**: Le raccomandazioni `chat.promptFilesRecommendations` devono essere generate partendo dai prompt Markdown disponibili.
- **DES-006**: L'entry point del pacchetto deve esporre `usereq.cli:main` via `use-req`, `req`, e `usereq`.
- **DES-007**: Gli errori attesi devono essere gestiti via eccezione dedicata con exit code non-zero.
- **DES-012**: La funzione `load_cli_configs` deve essere sostituita con `load_centralized_models` che carica i dati dal file `src/usereq/resources/common/models.json`. Quando `legacy_mode` è attivo, deve caricare `models-legacy.json` se esiste, altrimenti fare fallback su `models.json`. Il fallback deve avvenire a livello di file completo, non per singole voci. La struttura di ritorno deve rimanere compatibile: un dizionario `cli_name -> config` dove `config` contiene le chiavi `prompts`, `usage_modes`, e opzionalmente `agent_template`.
- **DES-013**: La funzione `generate_req_file_list` non deve essere utilizzata dal flusso di generazione prompt e il token `%%REQ_DIR%%` non deve essere più supportato.
- **DES-014**: La funzione `generate_dir_list` deve essere rinominata in `generate_guidelines_file_list`. Il comportamento deve essere allineato a `generate_req_file_list`: scansionare la directory specificata (quella passata con `--guidelines-dir`) e restituire la lista dei file presenti in quella directory (senza ricerca ricorsiva di sottocartelle), ignorando i file che iniziano con punto (`.`). Se la directory è vuota o non contiene file non nascosti, deve restituire il nome della directory stessa come fallback (preservando il comportamento originale solo per il caso di directory vuota).

### 3.2 Interfaccia CLI e Comportamento Generale
- Questa sezione definisce l'interfaccia a riga di comando e i comportamenti generali dell'applicazione.
- **REQ-001**: Quando il comando `req` è invocato senza parametri, l'output deve includere aiuto e numero versione definito in `src/usereq/__init__.py`.
- **REQ-002**: Quando il comando `req` è invocato con l'opzione `--ver` o `--version`, l'output deve contenere solo il numero versione.
- **REQ-003**: La stringa di utilizzo aiuto deve includere il comando `req`, la versione e tutte le opzioni disponibili inclusa `--legacy`, `--add-guidelines`, `--copy-guidelines`, `--files-tokens`, `--files-references`, `--files-compress`, `--references`, `--compress`, e `--tokens` nel formato `usage: req -c ...`.
- **REQ-004**: Tutti gli output di utilizzo, aiuto, informazione, verbose o debug dello script devono essere in Inglese.
- **REQ-005**: Il comando deve richiedere i parametri `--docs-dir`, `--tests-dir`, e `--src-dir` e verificare che indichino directory esistenti, altrimenti deve terminare con errore.
- **REQ-093**: Il parametro `--src-dir` deve poter essere fornito più volte; ogni directory passata deve essere normalizzata come gli altri percorsi e deve esistere, altrimenti il comando deve terminare con errore.
- **REQ-006**: Il comando deve accettare flag booleani `--enable-claude`, `--enable-codex`, `--enable-gemini`, `--enable-github`, `--enable-kiro`, `--enable-opencode`, `--legacy`, e `--preserve-models` (default false). Quando un flag `--enable-*` è omesso, la CLI deve saltare la creazione di risorse per quel provider. Quando `--legacy` è attivo, la CLI deve attivare la "legacy mode" per il caricamento delle configurazioni. Quando `--preserve-models` è attivo in combinazione con `--update`, la CLI deve preservare il file `.req/models.json` esistente e il flag `--legacy` non ha effetto.
- **REQ-007**: Durante installazioni normali (non upgrade/remove/help), il comando deve richiedere che almeno un flag `--enable-*` sia fornito. Il flag `--legacy` non conta come flag di abilitazione del provider. Se nessun flag `--enable-*` è fornito, deve stampare un messaggio di errore in Inglese e uscire.
- **REQ-008**: La tabella riassuntiva di installazione ASCII deve includere righe solo per i target CLI i cui prompt sono stati installati durante l'invocazione corrente.
- **REQ-085**: Il comando deve supportare i flag booleani `--add-guidelines` e `--copy-guidelines` (default false). Questi flag attivano la copia dei contenuti della directory `src/usereq/resources/guidelines/` nella directory specificata da `--guidelines-dir`. L'operazione di copia deve essere eseguita prima della chiamata a `generate_guidelines_file_list`.
- **REQ-086**: Quando `--add-guidelines` è attivo, il comando deve copiare tutti i file presenti in `src/usereq/resources/guidelines/` nella directory target specificata da `--guidelines-dir`, preservando i file esistenti (senza sovrascriverli) se hanno lo stesso nome.
- **REQ-087**: Quando `--copy-guidelines` è attivo, il comando deve copiare tutti i file presenti in `src/usereq/resources/guidelines/` nella directory target specificata da `--guidelines-dir`, sovrascrivendo i file esistenti se hanno lo stesso nome.
- **REQ-088**: I flag `--add-guidelines` e `--copy-guidelines` sono mutualmente esclusivi: se entrambi sono forniti contemporaneamente, il comando deve terminare con errore.
- **REQ-089**: La copia dei template tecnici deve avvenire solo quando almeno uno dei due flag (`--add-guidelines` o `--copy-guidelines`) è attivo. Se nessuno dei due flag è fornito, l'operazione di copia non deve essere eseguita.

### 3.3 Installazione e Aggiornamenti
- Questa sezione copre i requisiti per l'installazione, l'aggiornamento e la disinstallazione del tool e delle risorse.
- **REQ-009**: L'opzione `--upgrade` deve eseguire il comando `uv tool install usereq --force --from git+https://github.com/Ogekuri/useReq.git` e terminare con errore se fallisce.
- **REQ-010**: La stringa di aiuto deve includere `--upgrade` come opzione disponibile.
- **REQ-011**: L'opzione `--uninstall` deve eseguire `uv tool uninstall usereq` e terminare con errore se fallisce.
- **REQ-012**: La stringa di aiuto deve includere `--uninstall` come opzione disponibile.
- **REQ-013**: Dopo il completamento con successo di un'installazione o aggiornamento, la CLI deve stampare una singola riga in Inglese informando l'utente del successo includendo il percorso root risolto.
- **REQ-014**: Immediatamente dopo il messaggio di successo, la CLI deve stampare una lista delle directory scoperte per la sostituzione del token `%%GUIDELINES_FILES%%`, prefissate da `- `.
- **REQ-015**: Immediatamente dopo la lista file, la CLI deve stampare una tabella leggibile ASCII descrivendo quali prompt e moduli sono stati installati per ogni target CLI.

### 3.4 Controllo Versione
- Questa sezione specifica i requisiti per la verifica online di nuove versioni del software.
- **REQ-016**: Il comando, dopo validazione input e prima di modifiche filesystem, deve verificare disponibilità online di nuova versione tramite chiamata HTTP GET a GitHub API con timeout 1 secondo.
- **REQ-017**: Se la chiamata ha successo e la versione remota è maggiore di `__version__`, il comando deve stampare un messaggio in Inglese indicando versione corrente, disponibile e comando per aggiornare.

### 3.5 Inizializzazione e Configurazione del Progetto
- Questa sezione descrive come il progetto deve essere inizializzato e configurato.
- **REQ-018**: Se la directory indicata da `--docs-dir` è vuota, il comando deve generare un file `requirements.md` dal template.
- **REQ-019**: Il progetto deve includere uno script `req.sh` nella root repository per avviare la versione in sviluppo.
- **REQ-020**: Lo script `req.sh` deve essere eseguibile da qualsiasi percorso, risolvere la propria directory, verificare `.venv` e crearlo se assente.
- **REQ-021**: Se `.venv` esiste, `req.sh` deve eseguire il comando usando il Python del venv inoltrando gli argomenti.
- **REQ-022**: Il comando deve salvare i valori di `--guidelines-dir`, `--docs-dir`, `--tests-dir`, e l'elenco di `--src-dir` in `.req/config.json` come percorsi relativi.
- **REQ-023**: Il file `.req/config.json` deve includere campi `guidelines-dir`, `docs-dir`, `tests-dir`, e `src-dir` preservando slash finali; `src-dir` deve essere un array con una voce per ogni directory passata.
- **REQ-024**: Il comando deve supportare l'opzione `--update` per rieseguire l'inizializzazione usando parametri salvati.
- **REQ-025**: Quando `--update` è presente, il comando deve verificare presenza di `.req/config.json` e terminare con errore se assente.
- **REQ-026**: Con `--update`, il comando deve caricare `guidelines-dir`, `docs-dir`, `tests-dir`, e `src-dir` da config ed eseguire il flusso come se passati manualmente.
- **REQ-027**: Il comando deve copiare i template in `.req/templates`, rimpiazzando pre-esistenti.
- **REQ-084**: Il comando deve copiare il file di configurazione modelli in `.req/models.json`, rimpiazzando il file pre-esistente se presente, a meno che `--preserve-models` sia attivo. Quando `--preserve-models` NON è attivo: se `--legacy` NON è attivo, deve copiare `models.json` dalle risorse del pacchetto (`src/usereq/resources/common/models.json`); se `--legacy` è attivo E il file `models-legacy.json` è caricato con successo (cioè quando esiste), deve copiare `models-legacy.json` dalle risorse del pacchetto (`src/usereq/resources/common/models-legacy.json`); se `--legacy` è attivo ma `models-legacy.json` non esiste, deve copiare `models.json`. Questa copia deve avvenire dopo la creazione della directory `.req` e dopo il salvataggio di `config.json`.
- **REQ-028**: Se il template VS Code è disponibile, deve creare o aggiornare `.vscode/settings.json` unendo impostazioni.
- **REQ-029**: Prima di modificare `.vscode/settings.json`, deve salvare lo stato originale in backup sotto `.req/` (per ripristino con remove).
- **REQ-030**: L'aggiornamento di `.vscode/settings.json` deve avvenire solo se ci sono differenze semantiche; se non ce ne sono, non deve riscrivere né creare backup.
- **REQ-031**: Il file `.req/settings.json.absent` non deve mai essere generato.

### 3.6 Generazione Risorse - Comune
- Questa sezione contiene i requisiti comuni per la generazione delle risorse per i vari provider AI.
- **REQ-032**: Il comando non deve generare né sostituire i token `%%REQ_DIR%%` e `%%REQ_PATH%%` nei prompt.
- **REQ-033**: I template prompt devono essere trattati senza parsing o rendering di placeholder relativi ai requisiti (`%%REQ_*%%`).
- **REQ-034**: Lo script deve relativizzare percorsi che contengono il path home progetto.
- **REQ-035**: Il comando deve sostituire `%%GUIDELINES_FILES%%` con la lista di sottocartelle in `--guidelines-dir` formattate come inline code con slash finale.
- **REQ-036**: Se la directory `--guidelines-dir` è vuota, usare la directory stessa per `%%GUIDELINES_FILES%%`.
- **REQ-037**: La lista directory per `%%GUIDELINES_FILES%%` deve usare percorsi relativi.
- **REQ-090**: Il comando deve sostituire `%%GUIDELINES_PATH%%` con il percorso passato con `--guidelines-dir`, normalizzato rispetto alla root del progetto.
- **REQ-091**: Il comando deve sostituire `%%DOC_PATH%%` con il percorso passato con `--docs-dir`, normalizzato rispetto alla root del progetto.
- **REQ-092**: Il comando deve sostituire `%%TEST_PATH%%` con il percorso passato con `--tests-dir`, normalizzato rispetto alla root del progetto, formattato come inline code (backticks) e aggiungendo sempre una slash finale anche quando il valore passato non la include.
- **REQ-094**: Il comando deve sostituire `%%SRC_PATHS%%` con l'elenco delle directory passate con `--src-dir`, normalizzate rispetto alla root del progetto, formattate come inline code con slash finale, e separate da `, `.
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
- **REQ-095**: Durante la generazione dei prompt Codex, il comando deve creare la directory `.codex/skills/req` e, per ogni prompt Markdown, la sottodirectory `.codex/skills/req/<nome>` se non esiste.
- **REQ-096**: Per ogni sottodirectory skill Codex, il comando deve generare `SKILL.md` contenente il testo del prompt con lo stesso rendering di `.github/agents/req.<name>.agent.md`, usando la configurazione `codex` caricata da `models.json` o `models-legacy.json` secondo la modalità legacy.

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
- **REQ-068**: Con `--remove`, richiedere obbligatoriamente `--base` o `--here` e rifiutare `--guidelines-dir`, `--update`.
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

### 3.15 Analisi Sorgenti e Linguaggi Supportati
- Questa sezione definisce i requisiti per il modulo di analisi multi-linguaggio del codice sorgente.
- **SRC-001**: Il modulo `usereq.source_analyzer` deve supportare 20 linguaggi di programmazione: C (`.c`), C++ (`.cpp`), C# (`.cs`), Elixir (`.ex`), Go (`.go`), Haskell (`.hs`), Java (`.java`), JavaScript (`.js`), Kotlin (`.kt`), Lua (`.lua`), Perl (`.pl`), PHP (`.php`), Python (`.py`), Ruby (`.rb`), Rust (`.rs`), Scala (`.scala`), Shell (`.sh`), Swift (`.swift`), TypeScript (`.ts`), Zig (`.zig`).
- **SRC-002**: Per ciascun linguaggio, il modulo deve riconoscere e classificare i seguenti tipi di elementi: `FUNCTION`, `METHOD`, `CLASS`, `STRUCT`, `ENUM`, `TRAIT`, `INTERFACE`, `MODULE`, `IMPL`, `MACRO`, `CONSTANT`, `VARIABLE`, `TYPE_ALIAS`, `IMPORT`, `DECORATOR`, `COMMENT_SINGLE`, `COMMENT_MULTI`, `COMPONENT`, `PROTOCOL`, `EXTENSION`, `UNION`, `NAMESPACE`, `PROPERTY`, `SIGNAL`, `TYPEDEF`.
- **SRC-003**: Ogni elemento riconosciuto deve contenere: tipo elemento, riga iniziale, riga finale, estratto del codice sorgente (massimo 5 righe), nome opzionale, firma opzionale, visibilità opzionale, nome genitore opzionale, ereditarietà opzionale, profondità gerarchica.
- **SRC-004**: Il parametro linguaggio deve essere normalizzato: deve accettare maiuscole, minuscole, case misto, punto iniziale e spazi.
- **SRC-005**: Per ciascun linguaggio, il modulo deve riconoscere i commenti a riga singola con il delimitatore appropriato e i commenti multi-riga con i delimitatori di apertura e chiusura specifici del linguaggio.
- **SRC-006**: Il modulo deve supportare alias dei linguaggi (es. `js` per `javascript`, `ts` per `typescript`, `rs` per `rust`, `py` per `python`, `rb` per `ruby`, `hs` per `haskell`, `cs` per `csharp`, `kt` per `kotlin`, `ex` per `elixir`, `sh`/`bash`/`zsh` per `shell`, `cc`/`cxx` per `cpp`, `h` per `c`, `hpp` per `cpp`, `pl` per `perl`, `exs` per `elixir`). Gli alias devono produrre risultati identici al linguaggio canonico.
- **SRC-007**: Il modulo deve gestire la gerarchia degli elementi: gli elementi contenitore (class, struct, module, etc.) devono rimanere a profondità 0, gli elementi contenuti devono avere profondità 1 e il campo `parent_name` impostato.
- **SRC-008**: Il metodo `enrich()` deve arricchire gli elementi con firme pulite, gerarchia, visibilità, ereditarietà, commenti interni e punti di uscita.
- **SRC-009**: La funzione `format_output()` deve produrre un output strutturato con sezioni DEFINITIONS, COMMENTS e COMPLETE STRUCTURED LISTING.
- **SRC-010**: La funzione `format_markdown()` deve produrre un output Markdown compatto ottimizzato per il contesto LLM, con header, imports, definizioni gerarchiche, commenti, annotazioni del corpo e indice dei simboli.
- **SRC-011**: Il modulo deve gestire correttamente: file vuoti (restituire lista vuota), file con solo spazi (restituire lista vuota), linguaggi non supportati (lanciare `ValueError`), file non trovati (lanciare `FileNotFoundError`).
- **SRC-012**: La ricerca della fine dei blocchi deve utilizzare strategie specifiche per famiglia di linguaggio: indentazione per Python e Haskell, parentesi graffe per C/C++/Rust/JavaScript/TypeScript/Java/Go/C#/Swift/Kotlin/PHP/Scala/Zig, keyword `end` per Ruby/Elixir/Lua.
- **SRC-013**: I commenti all'interno di stringhe letterali non devono essere riconosciuti come commenti.
- **SRC-014**: I fixture di test per tutti i 20 linguaggi devono essere presenti nella directory `tests/fixtures/` con il formato `fixture_<linguaggio>.<estensione>`.

### 3.16 Conteggio Token
- Questa sezione definisce i requisiti per il modulo di conteggio token.
- **TOK-001**: Il modulo `usereq.token_counter` deve contare i token usando la codifica `tiktoken` con encoding `cl100k_base` come default.
- **TOK-002**: La classe `TokenCounter` deve esporre i metodi `count_tokens(content)` e `count_chars(content)`.
- **TOK-003**: La funzione `count_file_metrics(content, encoding_name)` deve restituire un dizionario con chiavi `tokens` e `chars`.
- **TOK-004**: La funzione `count_files_metrics(file_paths, encoding_name)` deve restituire una lista di dizionari con chiavi `file`, `tokens`, `chars` e opzionalmente `error` in caso di errore di lettura.
- **TOK-005**: La funzione `format_pack_summary(results)` deve formattare un riepilogo con dettagli per file e totali, usando il formato: nome file, conteggio token, conteggio caratteri, e una sezione Pack Summary con totali.
- **TOK-006**: In caso di errore di conteggio token (eccezione nell'encoding), il conteggio deve restituire 0 senza propagare l'eccezione.

### 3.17 Generazione Markdown di Riferimento
- Questa sezione definisce i requisiti per il modulo di generazione markdown di riferimento per il contesto LLM.
- **MKD-001**: Il modulo `usereq.generate_markdown` deve analizzare file sorgente utilizzando `usereq.source_analyzer` e produrre un output markdown concatenato.
- **MKD-002**: Il modulo deve determinare il linguaggio dal file extension utilizzando la mappa estensione-linguaggio supportata.
- **MKD-003**: I file non trovati devono essere ignorati con un messaggio SKIP su stderr.
- **MKD-004**: I file con estensione non supportata devono essere ignorati con un messaggio SKIP su stderr.
- **MKD-005**: Se nessun file valido viene processato, deve essere lanciata una eccezione `ValueError`.
- **MKD-006**: I risultati di analisi markdown devono essere concatenati con separatore `\n\n---\n\n`.
- **MKD-007**: Lo stato di elaborazione (OK/FAIL e conteggio) deve essere stampato su stderr.

### 3.18 Compressione Sorgenti
- Questa sezione definisce i requisiti per il modulo di compressione del codice sorgente.
- **CMP-001**: Il modulo `usereq.compress` deve comprimere il codice sorgente rimuovendo commenti (inline, a riga singola, multi-riga), righe vuote, spazi finali e spaziatura ridondante, preservando la semantica del linguaggio.
- **CMP-002**: Per i linguaggi con indentazione significativa (Python, Haskell, Elixir), l'indentazione deve essere preservata durante la compressione.
- **CMP-003**: Il formato di output deve supportare i prefissi con numero di riga nel formato `L<n>> <testo>`, abilitati di default e disabilitabili con l'opzione `include_line_numbers=False`.
- **CMP-004**: Le shebang lines (`#!`) alla prima riga del file devono essere preservate.
- **CMP-005**: I commenti all'interno di stringhe letterali non devono essere rimossi.
- **CMP-006**: Il modulo deve determinare automaticamente il linguaggio dall'estensione del file, con possibilità di override manuale.
- **CMP-007**: Il modulo `usereq.compress_files` deve comprimere e concatenare file sorgente multipli, producendo per ciascun file un header nel formato `@@@ <percorso> | <linguaggio>` seguito dal contenuto compresso.
- **CMP-008**: I file non trovati devono essere ignorati con un messaggio SKIP su stderr.
- **CMP-009**: I file con estensione non supportata devono essere ignorati con un messaggio SKIP su stderr.
- **CMP-010**: Se nessun file valido viene processato, deve essere lanciata una eccezione `ValueError`.
- **CMP-011**: Lo stato di elaborazione (OK/FAIL e conteggio) deve essere stampato su stderr.
- **CMP-012**: I blocchi di commenti multi-riga (incluse docstrings Python con `"""` e `'''`) devono essere rimossi nella compressione.

### 3.19 Comandi Standalone su File Arbitrari
- Questa sezione definisce i comandi CLI che operano su liste arbitrarie di file, indipendentemente dalla configurazione del progetto (`--base`, `--here`).
- **CMD-001**: Il comando `--files-tokens` deve accettare una lista di file come parametro e calcolare il conteggio token e caratteri per ciascun file, stampando un riepilogo con dettagli per file e totali su stdout.
- **CMD-002**: Il comando `--files-tokens` deve operare indipendentemente da `--base`, `--here` e dalla configurazione di useReq. I parametri `--base` e `--here` non devono essere richiesti.
- **CMD-003**: Il comando `--files-tokens` deve ignorare i file non trovati con un avviso su stderr e terminare con errore se nessun file valido è fornito.
- **CMD-004**: Il comando `--files-references` deve accettare una lista arbitraria di file e generare un markdown strutturato di riferimento per il contesto LLM, stampandolo su stdout.
- **CMD-005**: Il comando `--files-references` deve operare indipendentemente da `--base`, `--here` e dalla configurazione di useReq. I parametri `--base` e `--here` non devono essere richiesti.
- **CMD-006**: Il comando `--files-compress` deve accettare una lista arbitraria di file e generare un output compresso per il contesto LLM, stampandolo su stdout.
- **CMD-007**: Il comando `--files-compress` deve operare indipendentemente da `--base`, `--here` e dalla configurazione di useReq. I parametri `--base` e `--here` non devono essere richiesti.

### 3.20 Comandi di Progetto su Directory Sorgenti
- Questa sezione definisce i comandi CLI che operano sulle directory sorgenti configurate nel progetto.
- **CMD-008**: Il comando `--references` deve richiedere `--base` o `--here` per determinare il contesto di esecuzione. Se nessuno dei due è presente, il comando deve terminare con un messaggio di errore che indica i parametri obbligatori.
- **CMD-009**: Il comando `--references` deve eseguire la generazione markdown di riferimento utilizzando come input tutti i file con estensione supportata (come definiti in SRC-001) trovati nelle directory sorgenti configurate con `--src-dir` o con il campo `src-dir` del file `config.json`.
- **CMD-010**: Il comando `--compress` deve richiedere `--base` o `--here` per determinare il contesto di esecuzione. Se nessuno dei due è presente, il comando deve terminare con un messaggio di errore che indica i parametri obbligatori.
- **CMD-011**: Il comando `--compress` deve eseguire la compressione sorgenti utilizzando come input tutti i file con estensione supportata (come definiti in SRC-001) trovati nelle directory sorgenti configurate con `--src-dir` o con il campo `src-dir` del file `config.json`.
- **CMD-012**: Durante la scansione delle directory sorgenti per i comandi `--references` e `--compress`, le seguenti directory devono essere escluse (elenco hardcoded): `.git`, `.vscode`, `tmp`, `temp`, `.cache`, `.pytest_cache`, `node_modules`, `__pycache__`, `.venv`, `venv`, `dist`, `build`, `.tox`, `.mypy_cache`, `.ruff_cache`.
- **CMD-013**: La scansione delle directory sorgenti per i comandi `--references` e `--compress` deve essere ricorsiva, esaminando tutte le sottodirectory delle directory sorgenti configurate, escludendo le directory elencate in CMD-012.
- **CMD-014**: I comandi `--references` e `--compress`, quando utilizzati con `--update`, devono caricare le directory sorgenti dal campo `src-dir` del file `config.json`.
- **CMD-015**: Il comando `--references` deve anteporre al markdown generato una sezione `# Files Structure` contenente l'albero ASCII dei file effettivamente selezionati dalla scansione (`--src-dir` o `src-dir` da configurazione), applicando gli stessi filtri di estensione supportata (SRC-001) ed esclusione directory (CMD-012); l'albero deve essere racchiuso in code fence Markdown.
- **CMD-016**: Il comando `--tokens` deve richiedere `--base` o `--here` e `--docs-dir`, risolvere la directory documentazione rispetto alla root progetto, elencare i file regolari presenti direttamente in `--docs-dir`, eseguire il flusso di `--files-tokens` su tali file e stampare il riepilogo su stdout.
