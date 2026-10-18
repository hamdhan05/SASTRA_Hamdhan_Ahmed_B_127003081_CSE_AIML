# Presentation Deliverables (`Presentation/`)

This directory contains the formal capstone project presentation slide deck in both PowerPoint (`.pptx`) and portable document (`.pdf`) formats for the **AUTOSAR AI** platform.

---

## 1. Deliverables Inventory

| File | Format | Slides | Purpose & Scope |
| :--- | :---: | :---: | :--- |
| [`AUTOSAR_AI_Hamdhan_Ahmed_B_Presentation.pptx`](AUTOSAR_AI_Hamdhan_Ahmed_B_Presentation.pptx) | PPTX | 8 Slides | Editable, high-resolution presentation deck with custom automotive typography, glassmorphism card styling, and architectural diagrams. |
| [`AUTOSAR_AI_Hamdhan_Ahmed_B_Presentation.pdf`](AUTOSAR_AI_Hamdhan_Ahmed_B_Presentation.pdf) | PDF | 8 Slides | High-definition, standardized PDF export for presentation viewers, evaluation panels, and competition submissions. |

---

## 2. Slide Structure & Narrative Synopsis

| Slide # | Slide Title | Key Narrative & Engineering Highlights |
| :---: | :--- | :--- |
| **Slide 1** | **Title Slide: Project Introduction** | Introduction of candidate (Hamdhan Ahmed B, 127003081, SASTRA University) and project title: *AUTOSAR AI — High-Level Design Document Intelligence Platform*. |
| **Slide 2** | **Problem Statement & Objectives** | The automotive software complexity challenge: manual HLD review bottlenecks, cybersecurity constraints prohibiting public cloud LLMs (ISO/SAE 21434), and the danger of hallucinations in safety-critical systems (ISO 26262). |
| **Slide 3** | **Decoupled System Architecture** | Comprehensive overview of the 8 decoupled architectural layers: Streamlit frontend (port 8501), FastAPI backend (port 8000), PyMuPDF parser, SentenceTransformers, ChromaDB vector store, SQLite DB, and local Ollama inference. |
| **Slide 4** | **Document Ingestion & Hybrid Retrieval** | Ingestion pipeline walkthrough: physical page provenance tracking, 1000/150 character chunking, regex entity heuristics, Dense Chroma search + Sparse BM25 keyword matching fused via Reciprocal Rank Fusion ($k=60$). |
| **Slide 5** | **Grounded Local RAG & Verification** | Factual grounding workflow: strict evidence-based system prompt, local Ollama `llama3.2:3b` generation, automated claim decomposition, and quantitative Grounding Score (0.0 to 1.0) with confidence rating. |
| **Slide 6** | **Implemented Modules & User Interface** | Walkthrough of the 9 functional Streamlit pages: Dashboard, Documents, Architecture Explorer, AI Assistant, Comparisons, Findings, Reports, Settings/Diagnostics, and Evaluation. |
| **Slide 7** | **Verification, Testing & Empirical Results** | Rigorous automated testing evidence: 28/28 unit tests passing in 27.35 seconds, 35-query benchmark evaluation (94.2% hit rate, 0.864 MRR, 100% abstention on out-of-scope adversarial questions). |
| **Slide 8** | **Limitations, Future Roadmap & Conclusion** | Transparent appraisal of current system boundaries and future evolution: bidirectional ARXML AST generation, OCR table extraction for legacy blueprints, and real-time CAN bus timing simulation. |

---

## 3. Defense & Presentation Guidance

For oral defense or competition jury presentations:
- **Recommended Presentation Duration:** 8 to 10 minutes (approx. 1 to 1.25 minutes per slide).
- **Spoken Script:** A verbatim spoken script matching every slide is provided in [`Video/Presentation_Script.md`](../Video/Presentation_Script.md).
- **Live Demonstration Walkthrough:** A step-by-step interactive demo script is provided in [`Video/Demo_Scenes.md`](../Video/Demo_Scenes.md).
