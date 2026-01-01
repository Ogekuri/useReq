---
title: "Requisiti di useReq"
description: "Specifica dei requisiti software"
date: "2025-12-31"
author: "Astral"
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
**Versione**: 0.1.9
**Autore**: Astral  
**Data**: 2026-01-01

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
| 2025-12-31 | 0.1.0 | Creazione della bozza dei requisiti. |
| 2026-01-01 | 0.1.1 | Aggiunto script req.sh per eseguire la versione in-development con venv. |
| 2026-01-01 | 0.1.2 | Aggiunta stampa della versione per invocazioni senza argomenti e con opzioni dedicate. |
| 2026-01-01 | 0.1.3 | Aggiunta stampa help con versione per invocazioni senza argomenti e stampa versione-only per opzioni dedicate. |
| 2026-01-01 | 0.1.4 | Aggiunta versione e comando nella stringa di usage dell'help. |
| 2026-01-01 | 0.1.5 | Aggiornata la generazione dei comandi Gemini in sottocartella dedicata. |
| 2026-01-01 | 0.1.6 | Aggiunto supporto per la generazione delle risorse Kiro CLI. |
| 2026-01-01 | 0.1.7 | Modificato il comando --doc per accettare directory e generare elenchi di file. |
| 2026-01-01 | 0.1.8 | Ripristinata la relativizzazione dei percorsi e organizzazione test sotto temp/. |
| 2026-01-01 | 0.1.9 | Modificato il comando --dir per processare sottocartelle e generare elenchi di directory. |

## 1. Introduzione
Questo documento definisce i requisiti software per useReq, una utility CLI che inizializza un progetto con template, prompt e risorse per agenti, assicurando percorsi relativi coerenti rispetto alla radice del progetto.

### 1.1 Regole del documento
Questo documento deve sempre seguire queste regole:
- Questo documento deve essere scritto in italiano.
- I requisiti devono essere formattati come elenco puntato, utilizzando il verbo "deve" per indicare azioni obbligatorie.
- Ogni identificativo (**PRJ-001**, **PRJ-002**, **CTN-001**, **CTN-002**, **DES-001**, **DES-002**, **REQ-001**, **REQ-002**, …) deve essere univoco.
- Ogni identificativo deve iniziare con il prefisso del proprio gruppo di requisiti (PRJ-, CTN-, DES-, REQ-).
- Ogni requisito deve essere identificabile, verificabile e testabile.
- Ad ogni modifica del documento si deve aggiornare il numero di versione e la cronologia delle revisioni.

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
├── dist
│   ├── usereq-0.1.0-py3-none-any.whl
│   └── usereq-0.1.0.tar.gz
├── docs
│   └── requirements.md
├── other-stuff
│   └── templates
│       ├── srs-template-bare.md
│       └── srs-template.md
├── pyproject.toml
├── scripts
│   └── version.sh
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
- **CTN-001**: L'opzione `--doc` deve indicare una directory che deve esistere.
- **CTN-002**: I valori di `--doc` e `--dir` devono essere normalizzati in percorsi relativi alla radice del progetto; in caso contrario il comando deve terminare con errore.
- **CTN-003**: Il percorso `--dir` deve esistere come directory reale sotto la radice del progetto prima della copia delle risorse.
- **CTN-004**: La rimozione di directory `.req` o `.req/templates` preesistenti deve essere consentita solo se tali percorsi si trovano sotto la radice del progetto.
- **CTN-005**: Il comando deve fallire se il progetto specificato non esiste sul filesystem.

## 3. Requisiti
### 3.1 Progettazione e implementazione
- **DES-001**: Il calcolo dei token `%%REQ_DOC%%` e `%%REQ_DIR%%` deve produrre percorsi relativi normalizzati e preservare l'eventuale barra finale di `--dir`.
- **DES-002**: L'origine del template `requirements.md` deve essere la cartella `resources/templates` inclusa nel pacchetto e il comando deve fallire se il template non e disponibile.
- **DES-003**: La conversione dei prompt Markdown in TOML deve estrarre il campo `description` dal front matter e salvare il corpo del prompt in una stringa multilinea.
- **DES-004**: Il merge delle impostazioni VS Code deve supportare file JSONC rimuovendo i commenti e deve fondere ricorsivamente gli oggetti con priorita ai valori del template.
- **DES-005**: Le raccomandazioni `chat.promptFilesRecommendations` devono essere generate a partire dai prompt Markdown disponibili.
- **DES-006**: L'entry point del pacchetto deve esporre `usereq.cli:main` tramite `use-req`, `req` e `usereq`.
- **DES-007**: Gli errori previsti devono essere gestiti tramite un'eccezione dedicata con codice di uscita non nullo.

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
- **REQ-016**: La stringa di usage dell'help deve includere il comando `req` e la versione `__version__` nel formato `usage: req -c [-h] (--base BASE | --here) --doc DOC --dir DIR [--verbose] [--debug] (x.y.z)`.
- **REQ-017**: Il comando deve creare le cartelle `.kiro/agents` e `.kiro/prompts` sotto la radice del progetto.
- **REQ-018**: Per ogni prompt Markdown disponibile, il comando deve copiare il file in `.kiro/prompts` con gli stessi contenuti generati per `.github/agents`.
- **REQ-019**: Per ogni prompt Markdown disponibile, il comando deve generare un file JSON in `.kiro/agents` con nome `req.<nome>.json` utilizzando un template presente in `src/usereq/resources/kiro`.
- **REQ-020**: Nei file JSON Kiro, i campi `name`, `description` e `prompt` devono essere valorizzati rispettivamente con `req-<nome>`, la `description` del front matter del prompt e il primo punto della sezione `## Purpose` del prompt.
- **REQ-021**: Il comando deve verificare che il parametro `--doc` indichi una directory esistente, altrimenti deve terminare con errore.
- **REQ-022**: Il comando deve esaminare tutti i file contenuti nella directory `--doc` in ordine alfabetico e sostituire la stringa `%%REQ_DOC%%` con un elenco dei file in formato markdown nella forma `[file1](file1), [file2](file2), [file3](file3)` separati da `", "` (virgola spazio).
- **REQ-023**: L'elenco dei file per la sostituzione di `%%REQ_DOC%%` deve utilizzare percorsi relativi calcolati dallo script, al netto del percorso assoluto e relativi alla home del progetto.
- **REQ-024**: I test devono essere eseguiti sotto la cartella temp/ e le cartelle temporanee devono essere cancellate al termine dell'esecuzione.
- **REQ-025**: Lo script deve relativizzare i percorsi che contengono il percorso della home del progetto (es. temp/project_sample/docs/ diventa docs/).
- **REQ-026**: Il comando deve esaminare tutti i sottofolder contenuti nella directory `--dir` in ordine alfabetico e sostituire la stringa `%%REQ_DIR%%` con un elenco delle directory in formato markdown nella forma `[dir1](dir1), [dir2](dir2), [dir3](dir3)` separati da `", "` (virgola spazio).
- **REQ-027**: Se la directory indicata da `--dir` è vuota, deve utilizzare la directory stessa per la sostituzione di `%%REQ_DIR%%`.
- **REQ-028**: L'elenco delle directory per la sostituzione di `%%REQ_DIR%%` deve utilizzare percorsi relativi calcolati dallo script.
