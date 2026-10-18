# Project Synopsis (`Synopsis/`)

This directory contains the formal academic project synopsis documents and the executive abstract for **AUTOSAR AI**.

---

## 1. Deliverables Inventory

| File | Format | Description & Scope |
| :--- | :---: | :--- |
| [`Project_Synopsis.pdf`](Project_Synopsis.pdf) | PDF | Official academic project synopsis covering motivation, domain context, mathematical problem formulation, system architecture, methodology, expected outcomes, and academic references. |
| [`Project_Synopsis.docx`](Project_Synopsis.docx) | DOCX | Editable Microsoft Word version of the project synopsis formatted according to university capstone guidelines. |
| [`Abstract.txt`](Abstract.txt) | Plain Text | Clean, standardized plain-text abstract suitable for online portal submission forms, paper metadata, and cataloging. |

---

## 2. Executive Abstract

Modern automotive architectures under the AUTOSAR (AUTomotive Open System ARchitecture) standard have grown exceptionally complex, encompassing hundreds of Software Components (SWCs), Runnables, Ports, and carried Signals. In automotive software engineering, manual cross-referencing and verification of High-Level Design (HLD) specifications across vehicle revision cycles is labor-intensive and prone to missing subtle interface incompatibilities or circular dependencies. Furthermore, strict automotive cybersecurity regulations (such as ISO/SAE 21434) prohibit transmitting proprietary vehicle designs to public cloud AI platforms, while the risk of Large Language Model (LLM) hallucinations is intolerable in safety-critical systems governed by ISO 26262.

To solve this challenge, this capstone project introduces **AUTOSAR AI** — an on-premises, factual verification, and traceability platform for automotive software specifications. The platform implements an end-to-end ingestion pipeline using PyMuPDF with physical page provenance; heuristic regex extraction of architectural entities; a two-stage hybrid retrieval engine fusing dense ChromaDB embeddings with sparse BM25 keyword matching via Reciprocal Rank Fusion ($k=60$); and local offline inference via Ollama (`llama3.2:3b`). An independent Grounding Service segments generated responses into discrete claims, evaluates cosine similarity against retrieved citation excerpts, and outputs a quantitative Grounding Score. The system is delivered through an interactive 9-page Streamlit web interface and a modular FastAPI backend, backed by 14 relational SQLite tables and validated through a 28-test automated suite with 100% pass rate.
