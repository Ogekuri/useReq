---
title: "Requisiti di useReq"
description: "Specifica dei requisiti software"
date: "2025-12-15"
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
tags: ["markdown", "requisiti", "esempio"]
---

# Requisiti di useReq
**Versione**: 0.1.0
**Autore**: Astral  
**Data**: 2025-12-15

## Indice
- [Requisiti di useReq](#requisiti-di-usereq)
  - [Indice](#indice)
  - [Cronologia delle revisioni](#cronologia-delle-revisioni)
  - [1. Introduzione](#1-introduzione)
    - [1.1 Regole del documento](#11-regole-del-documento)
    - [1.2 Scopo del progetto](#12-scopo-del-progetto)
    - [1.3 Componenti e librerie utilizzati](#13-componenti-e-librerie-utilizzati)
  - [2. Requisiti di progetto](#2-requisiti-di-progetto)
    - [2.1 Funzioni di progetto](#21-funzioni-di-progetto)
    - [2.2 Vincoli di progetto](#22-vincoli-di-progetto)
  - [3. Requisiti](#3-requisiti)
    - [3.1 Progettazione e implementazione](#31-progettazione-e-implementazione)
    - [3.2 Funzioni](#32-funzioni)

## Cronologia delle revisioni
| Data | Versione | Motivazione e descrizione della modifica |
|------|----------|-------------------------------------------|
| 2025-12-15 | 0.1.0 | Creazione iniziale del documento. |

## 1. Introduzione
useReq è un'utilità da linea di comando che inizializza un progetto con i prompt, gli agenti e i template distribuiti nel repository useReq. Lo strumento automatizza la creazione dei file di requisiti, delle cartelle tecniche e delle risorse per agenti Codex, GitHub e Gemini in modo coerente rispetto al percorso del progetto specificato dall'utente.

### 1.1 Regole del documento
Questo documento deve sempre seguire queste regole:
- Ogni identificativo (**PRJ-001**, **PRJ-002**, **CTN-001**, **CTN-002**, **DES-001**, **DES-002**, **REQ-001**, **REQ-002**, …) deve essere univoco.
- Ogni identificativo deve iniziare con il prefisso del proprio gruppo di requisiti (PRJ-, CTN-, DES-, REQ-).
- Ogni requisito deve essere identificabile, verificabile e testabile.
- Ad ogni modifica del documento si deve aggiornare il numero di versione e la cronologia delle revisioni.

### 1.2 Scopo del progetto
Lo scopo del progetto è fornire un comando `req`/`use-req` che, partendo da un progetto esistente, imposti automaticamente il documento di requisiti, la struttura tecnica e le risorse dei prompt, garantendo percorsi coerenti e percorsi relativi sicuri per l'agente.

### 1.3 Componenti e librerie utilizzati
- Python 3.11+: runtime richiesto dal pacchetto (`pyproject.toml`).
- Librerie standard (`argparse`, `pathlib`, `json`, `shutil`, `os`, `re`, `sys`): gestiscono parsing CLI, I/O e manipolazione dei percorsi (`src/usereq/cli.py`).
- `uvx` (strumento di esecuzione di Astral): fornisce il flusso di lavoro consigliato per distribuire il comando `req` (`README.md`).

## 2. Requisiti di progetto
### 2.1 Funzioni di progetto
- **PRJ-001**: Il comando deve accettare esattamente una delle opzioni `--base` o `--here` assieme ai percorsi `--doc` e `--dir` per individuare la radice del progetto e i file da trattare.
- **PRJ-002**: Il comando deve creare il documento di requisiti da template quando il percorso `--doc` non esiste e deve assicurare la directory tecnica `.req` ricreando i template locali.
- **PRJ-003**: Il comando deve generare le risorse dei prompt (`.codex`, `.github`, `.gemini`) copiando i file disponibili e sostituendo `%%REQ_DOC%%`, `%%REQ_DIR%%` e `%%ARGS%%` con i percorsi relativi calcolati.

### 2.2 Vincoli di progetto
- **CTN-001**: L'opzione `--doc` deve indicare un file Markdown che termina con l'estensione `.md`.
- **CTN-002**: I valori `--doc` e `--dir` devono essere normalizzati in percorsi relativi alla radice del progetto e deve essere generato un errore se rimangono percorsi assoluti.
- **CTN-003**: Il percorso `--dir` deve esistere come directory reale sotto la radice del progetto prima di eseguire qualsiasi copia di risorse.
- **CTN-004**: L'eventuale eliminazione della cartella `.req` esistente deve avvenire solo se la cartella si trova sotto `PROJECT_BASE`, prevenendo cancellazioni fuori dal perimetro.

## 3. Requisiti
### 3.1 Progettazione e implementazione
- **DES-001**: La normalizzazione dei percorsi deve produrre token `../../...` consistenti per i sostituti `%%REQ_DOC%%` e `%%REQ_DIR%%`, preservando l'eventuale barra finale della directory tecnica.
- **DES-002**: L'origine dei template `requirements.md` deve derivare dalla cartella `resources/templates` inclusa nel pacchetto e deve fallire se il file non esiste.
- **DES-003**: Ogni prompt Markdown deve poter essere convertito in TOML con un blocco `description` estratto dal front matter e il corpo racchiuso in una stringa multilinea.
- **DES-004**: Il merge delle impostazioni VS Code deve leggere JSON con o senza commenti, fondere ricorsivamente gli oggetti ed eseguire il salvataggio con indentazione leggibile, aggiungendo `chat.promptFilesRecommendations` dai prompt rilevati.

### 3.2 Funzioni
- **REQ-001**: Per ogni prompt disponibile, il comando deve copiare il file nella cartella `.codex/prompts` applicando i token sostitutivi calcolati.
- **REQ-002**: Per ogni prompt disponibile, il comando deve copiare il file nella cartella `.github/agents` con le stesse sostituzioni per consentire la registrazione dell'agente.
- **REQ-003**: Per ogni prompt disponibile, il comando deve creare un file `.github/prompts/req.<nome>.prompt.md` che referenzi l'agente `req.<nome>`.
- **REQ-004**: Per ogni prompt disponibile, il comando deve generare un file `.gemini/commands/req.<nome>.toml` trasformando il Markdown, sovrascrivendo in modo controllato e sostituendo i token con i percorsi relativi a `{{args}}`.
- **REQ-005**: Se è disponibile un template VS Code, il comando deve creare o aggiornare `.vscode/settings.json`, fondendo le impostazioni esistenti con quelle del template e aggiungendo i suggerimenti `chat.promptFilesRecommendations` per ogni prompt `req.*`.
- **REQ-006**: Dopo avere assicurato i template `.req`, il comando deve concludere stampando un messaggio di completamento con il percorso della radice di progetto trattata.
