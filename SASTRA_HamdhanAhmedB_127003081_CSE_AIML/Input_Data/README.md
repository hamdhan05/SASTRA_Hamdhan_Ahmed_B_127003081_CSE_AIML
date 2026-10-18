# Input Data — AUTOSAR High-Level Design (HLD) Specifications

This directory contains the primary automotive software architectural specifications and the standardized query benchmark sets utilized to evaluate the **AUTOSAR AI** platform.

---

## 1. Specification Inventory

| File / Folder | Release Version / Type | Scope | Content Summary |
| :--- | :---: | :--- | :--- |
| [`AUTOSAR_HLD_v1.0.pdf`](AUTOSAR_HLD_v1.0.pdf) | **v1.0** (Baseline) | Powertrain & Sensor Management | Baseline architectural specification defining initial Software Components (SWCs), ports, Sender-Receiver / Client-Server interfaces, and signals (e.g., `PowertrainManager`, `SensorManager`, `sig_MotorTorque`, `sig_VehicleSpeed`). |
| [`AUTOSAR_HLD_v2.0.pdf`](AUTOSAR_HLD_v2.0.pdf) | **v2.0** (Evolution) | ADAS, Perception, & Diagnostics | Major architectural evolution introducing new SWCs (`ADAS_Perception`, `DiagnosticManager`), modified interfaces, altered component dependencies, and signal data type alterations. |
| [`Sample_HLD_Documents/`](Sample_HLD_Documents/) | Additional Specifications | Extended Automotive Domains | Additional realistic specifications for cross-domain evaluation: [`AUTOSAR_Adaptive_Powertrain_HLD.pdf`](Sample_HLD_Documents/AUTOSAR_Adaptive_Powertrain_HLD.pdf) and [`1_Synthetic_Automotive_Architecture_RAG_Test.pdf`](Sample_HLD_Documents/1_Synthetic_Automotive_Architecture_RAG_Test.pdf). |
| [`Sample_Query_Set/`](Sample_Query_Set/) | Benchmark Queries | Evaluation Datasets | 35 standardized queries formatted in JSON ([`benchmark_dataset_35.json`](Sample_Query_Set/benchmark_dataset_35.json)) and CSV ([`sample_queries_35.csv`](Sample_Query_Set/sample_queries_35.csv)) containing 25 domain-specific queries and 10 adversarial queries. |

---

## 2. Ingestion & Processing Pipeline

When an HLD specification PDF is uploaded via the **Documents** page (`frontend/pages/2_Documents.py`) or the backend API (`/api/v1/documents/upload`):

1. **Text & Provenance Extraction (`backend/services/document_service.py`):**
   - PyMuPDF (`fitz`) parses each page at native C-speed, recording physical page numbers, paragraph geometry, and section headers.
2. **Deterministic Semantic Chunking:**
   - Text is segmented into chunks using a character window of 1000 characters with a 150-character overlap, guaranteeing that component boundary definitions and port tables are not split arbitrarily.
3. **Domain Entity Heuristics:**
   - Regular expression engines extract Software Components (SWCs), Runnables, PPorts/RPorts, Interfaces, and carried Signals with their AUTOSAR data types (`uint8`, `float32`, `boolean`).
4. **Dense & Sparse Indexing:**
   - Dense embeddings are generated via SentenceTransformers (`all-MiniLM-L6-v2`, 384 dimensions) and stored in ChromaDB with document ID and page metadata.
   - An in-memory BM25 index is tokenized for exact keyword lookup on architectural tokens.
5. **Relational Persistence:**
   - Extracted entities, relationships, and document metadata are stored in local SQLite (`autosar_ai.db`) across 14 relational tables.
