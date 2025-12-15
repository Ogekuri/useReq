---
title: "{{project name}} Requirements"
description: Software requirements specification
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
**Version**: {{version}}
**Author**: {{author}}  
**Date**: {{date_modified}}
<!-- Example:
---
title: "Foo Bar Web Interface Requirements"
description: Software requirements specification
date: "2025-12-25"
author: "Pinco Pallino"
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

# Foo Bar Web Interface Requirements
**Version**: 0.1
**Author**: Pinco Pallino
**Date**: 2025-12-25
-->

## Table of Contents
<!-- TOC -->
- [{{project name}} Requirements](#project-name-requirements)
  - [Table of Contents](#table-of-contents)
  - [Revision History](#revision-history)
  - [1. Introduction](#1-introduction)
    - [1.1 Document Rules](#11-document-rules)
    - [1.2 Project Scope](#12-project-scope)
  - [2. Project Requirements](#2-project-requirements)
    - [2.1 Project Functions](#21-project-functions)
    - [2.2 Project Constraints](#22-project-constraints)
  - [3. Requirements](#3-requirements)
    - [3.1 Design and Implementation](#31-design-and-implementation)
    - [3.2 Functions](#32-functions)
<!-- if needed, add verification chapter
* [4. Verification](#4-verification)
-->
<!-- TOC -->

## Revision History
<!-- On every change to this document, update the version number and add a new row to the revision history -->
| Date | Version | Change reason and description |
|------|---------|-------------------------------|
|      |         |                               |
|      |         |                               |

## 1. Introduction
<!-- Overview of the SRS: purpose, scope, audience, and document organization. Avoid detailed requirements here. -->

### 1.1 Document Rules
This document shall always follow these rules:
- Each requirement ID (for example, **PRJ-001**, **PRJ-002**,..  **CTN-001**, **CTN-002**,.. **DES-001**, **DES-002**,.. **REQ-001**, **REQ-002**,..) must be unique; do not assign the same ID to different requirements.
- Each requirement ID start with string that identify the requirement's group:
  * All project function requirements start with **PRJ-**
  * All project constraint requirements start with **CTN-**
  * All design and implementation requirements start with **DES-**
  * All function requirements start with **REQ-**
- Every requirement shall be identifiable, verifiable, and testable.
- On every change to this document, update the version number and add a new row to the revision history.

### 1.2 Project Scope
<!-- The project (name/version), primary purpose, key capabilities, and boundaries. Keep brief and focus on the "what" and "why", not the "how". Avoid detailed requirements here. -->

## 2. Project Requirements
<!-- Background and context that shape the project's requirements. Avoid detailed requirements here. -->

### 2.1 Project Functions
<!-- Major functional areas or features of the project -->
- **PRJ-001**: Requirement description of project function 1
- **PRJ-002**: Requirement description of project function 2
<!-- add here other project function requirements -->

### 2.2 Project Constraints
<!-- Design and implementation constraints that affect the solution of the project -->
- **CTN-001**: Requirement description of project constraint 1
- **CTN-002**: Requirement description of project constraint 2
<!-- add here other project constraint requirements -->

## 3. Requirements
<!-- Identifiable, verifiable, and testable requirements. Avoid implementation details. -->

### 3.1 Design and Implementation
<!-- Constraints and mandates on design, deployment, and maintenance -->
- **DES-001**: Requirement description of design constraint 1
- **DES-002**: Requirement description of design constraint 1
<!-- add here other design constraint requirements -->
### 3.2 Functions
<!-- Externally observable behaviors organized by feature or use case -->
- **REQ-001**: Requirement description of function 1
- **REQ-002**: Requirement description of function 2
<!-- add here other function requirements -->

<!-- if needed, add verification chapter
## 4. Verification
| Requirement ID | Requirement brief descrition | Verification procedure |
|----------------|------------------------------|------------------------|
|                |                              |                        |
-->
