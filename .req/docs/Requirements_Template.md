---
title: "{{project name}} Requirements"
description: Software requirements specification
version: "{{version}}"
date: "{{date_modified}}"
author: "{{author}}"
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
tags: ["markdown", "requirements", "example"]
---

# {{project name}} Requirements
<!-- Metadata is in the YAML front matter; do not duplicate it in the body. -->

<!-- Optional: omit a Table of Contents to reduce token footprint for LLM agents. If a TOC is included, it MUST be auto-generated and kept minimal. -->

## 1. Introduction
<!-- Overview of the SRS: purpose, scope, audience, and document organization. Avoid detailed requirements here. -->

### 1.1 Document Rules
This document MUST follow these authoring rules (LLM-first, normative SRS):
- This document MUST be written and maintained in English.
- Use RFC 2119 keywords exclusively (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY). Do not use "shall".
- In requirements sections, every bullet MUST be a requirement and MUST start with a unique, stable Requirement ID (e.g., **REQ-001**).
- Requirement IDs MUST be stable: never renumber, reuse, or repurpose an ID. Only the dedicated reorganization workflow may renumber and it MUST emit an old→new ID mapping.
- Requirement ID prefixes MUST be consistent; if additional prefixes are needed beyond PRJ/CTN/DES/REQ/TST, they MUST be defined once in this section before first use.
- Each requirement MUST be atomic, single-sentence, and testable; target <= 35 words per requirement; split any compound behavior into separate IDs.
- Write for other LLM Agents and automated parsers (high semantic density; no filler).
- On every change to this document:
  - Update `date` and `version` in the YAML front matter only (avoid duplicating metadata in the body).
  - Do NOT maintain an in-document revision history; use git history / CHANGELOG.md for change tracking.

### 1.2 Project Scope
<!-- The project (name/version), primary purpose, key capabilities, and boundaries. Keep brief and focus on the "what" and "why", not the "how". Avoid detailed requirements here. -->

## 2. Project Requirements
<!-- Background and context that shape the project's requirements. Avoid detailed requirements here. -->

### 2.1 Project Functions
<!-- Major functional areas or features of the project -->
- **PRJ-001**: MUST <single-sentence project function (<= 35 words)>.
- **PRJ-002**: Requirement description of project function 2
<!-- add here other project function requirements -->

### 2.2 Project Constraints
<!-- Design and implementation constraints that affect the solution of the project -->
- **CTN-001**: MUST <single-sentence constraint (<= 35 words)>.
- **CTN-002**: Requirement description of project constraint 2
<!-- add here other project constraint requirements -->

## 3. Requirements
<!-- Identifiable, verifiable, and testable requirements. Avoid implementation details. -->

### 3.1 Design and Implementation
<!-- Constraints and mandates on design, deployment, and maintenance -->
- **DES-001**: Requirement description of design constraint 1
- **DES-002**: MUST <single-sentence design constraint (<= 35 words)>.
<!-- add here other design constraint requirements -->
### 3.2 Functions
<!-- Externally observable behaviors organized by feature or use case -->
- **REQ-001**: MUST <single observable behavior with explicit trigger and expected outcome>.
- **REQ-002**: Requirement description of function 2
<!-- add here other function requirements -->

## 4. Test Requirements
<!-- Define the test requirements linked to functional/non-functional requirements (or to a verification context) and specify a clear, reproducible test procedure with explicit pass/fail criteria.  -->

- **TST-001**: MUST verify <requirement-id> using <reproducible procedure> with explicit pass/fail criteria.

<!-- Do not add a revision history section here; use git history / CHANGELOG.md instead. -->
