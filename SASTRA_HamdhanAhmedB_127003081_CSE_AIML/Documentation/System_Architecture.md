# AUTOSAR AI — System Architecture Specification

## 1. High-Level System Overview
**AUTOSAR AI** is an intelligent, high-assurance document intelligence platform engineered specifically for automotive software engineering teams working with AUTOSAR (AUTomotive Open System ARchitecture) High-Level Design (HLD) documents.

The system is structured as a modular, decoupled architecture consisting of eight distinct layers:
1. **Presentation Layer**: Streamlit multi-page reactive user interface.
2. **API & Routing Layer**: FastAPI asynchronous REST service layer.
3. **Document Ingestion & Extraction Layer**: PyMuPDF-based text extraction and character chunking.
4. **Embedding & Vector Storage Layer**: SentenceTransformers dense vectors with ChromaDB.
5. **Retrieval & Hybrid Fusion Layer**: Dense semantic search combined with BM25 keyword search using Reciprocal Rank Fusion (RRF).
6. **Local LLM Inference Layer**: On-premises Ollama inference engine running `llama3.2:3b`.
7. **Relational Persistence Layer**: SQLite 3 database managed via SQLAlchemy 2.0 ORM.
8. **Reporting & Security Layer**: Sanitized audit reporting with CSV formula injection defense.

---

## 2. Architecture Diagram (Mermaid)

```mermaid
graph TD
    subgraph Client ["Client Browser Layer"]
        UI["Streamlit UI (Port 8501)<br/>9 Interactive Pages"]
    end

    subgraph BackendGateway ["API Gateway & Routing Layer"]
        API["FastAPI Application (Port 8000)<br/>10 REST Routers"]
    end

    subgraph ProcessingServices ["Core Business Services"]
        DOC_SVC["Document Service<br/>(PyMuPDF Ingestion & Entity Regex)"]
        RET_SVC["Retrieval Service<br/>(Hybrid Dense + BM25 + RRF)"]
        LLM_SVC["LLM Service<br/>(Grounded Automotive Prompt)"]
        GND_SVC["Grounding Service<br/>(Claim Decomposition & Verification)"]
        GRAPH_SVC["Graph Service<br/>(Mermaid Architecture Topologies)"]
        RPT_SVC["Report Generator<br/>(Sanitized CSV Exports)"]
    end

    subgraph StorageLayer ["Data Storage Subsystems"]
        CHROMA[("ChromaDB Vector Store<br/>(all-MiniLM-L6-v2 Embeddings)")]
        SQLITE[("SQLite Database<br/>(14 SQLAlchemy Relational Tables)")]
    end

    subgraph InferenceLayer ["Local AI Inference"]
        OLLAMA["Local Ollama Service (Port 11434)<br/>Model: llama3.2:3b (8k Context)"]
    end

    UI -->|HTTP / JSON Requests| API
    API --> DOC_SVC
    API --> RET_SVC
    API --> LLM_SVC
    API --> GND_SVC
    API --> GRAPH_SVC
    API --> RPT_SVC

    DOC_SVC -->|Store Text & Vectors| CHROMA
    DOC_SVC -->|Save Entities & Chunks| SQLITE

    RET_SVC -->|Cosine Similarity Query| CHROMA
    RET_SVC -->|Fetch Metadata| SQLITE

    LLM_SVC -->|Local HTTP REST (120s timeout)| OLLAMA
    GND_SVC -->|Verify Claims against Chunks| RET_SVC
```

---

## 3. Detailed Layer Specifications

### 3.1 Presentation Layer (Streamlit — Port 8501)
- Implemented as a stateful, reactive web application across 9 modular pages:
  - `1_Dashboard.py`: Project stats, document overview, diagnostic indicators.
  - `2_Documents.py`: Multi-document PDF drag-and-drop upload, version tagging, governance state machine.
  - `3_Architecture_Explorer.py`: Extracted software components, runnables, interfaces, ports, signals, and interactive Mermaid dependency graph.
  - `4_AI_Assistant.py`: Grounded technical QA interface with source citations, claim verification chips, and confidence ratings.
  - `5_Comparisons.py`: Cross-revision HLD comparison, entity diffs, component renames, and signal data-type changes.
  - `6_Findings.py`: Rule-based architectural findings (circular dependencies, missing bindings, insecure IPC) and reviewer resolution workflow.
  - `7_Reports.py`: On-demand CSV export generation and historical audit logs.
  - `8_Settings.py`: Runtime configuration of chunk size, overlap, Top-K, and one-click diagnostic test of all 6 subsystems.
  - `9_Evaluation.py`: Execution and visualization of the 35-query benchmark evaluation suite.

### 3.2 API & Routing Layer (FastAPI — Port 8000)
- Exposes clean, typed REST endpoints defined using Pydantic schemas.
- Routers:
  - `/api/v1/projects`: Project CRUD and membership management.
  - `/api/v1/documents`: PDF file upload, metadata retrieval, cascade deletion.
  - `/api/v1/sessions`: Analysis sessions, chat message history, query submission.
  - `/api/v1/entities`: Architecture entity queries, port/signal queries, Mermaid topology.
  - `/api/v1/findings`: Rule violation findings and engineer review updates.
  - `/api/v1/comparisons`: Baseline vs revision comparison execution.
  - `/api/v1/reports`: Findings CSV report generation and secure download.
  - `/api/v1/settings`: Chunking and retrieval parameter management.
  - `/api/v1/diagnostics`: Comprehensive 6-subsystem health check.
  - `/api/v1/evaluation`: 35-query benchmark execution and evaluation metrics.

### 3.3 Document Ingestion & Extraction Layer
- **PDF Extraction**: PyMuPDF (`fitz`) parses text blocks while preserving exact page boundaries and section headers.
- **Chunking Engine**: Sliding character window of 1000 characters with 150-character overlap.
- **Regex Entity Extraction**: Pattern heuristics extract:
  - Software Components (SWCs)
  - Runnables (Tasks/Entities)
  - Interfaces (Client-Server, Sender-Receiver)
  - Ports (PPorts, RPorts) & Signals (with data types e.g., `float32`, `uint16`)

### 3.4 Embedding & Vector Storage Layer
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` generating 384-dimensional dense vectors.
- **Vector Database**: ChromaDB 0.4.24 persistent client configured at `./data/vector_store`.
- **Isolation**: Each project uses a distinct collection (`project_{id}`).

### 3.5 Retrieval & Hybrid Fusion Layer
- **Dense Vector Search**: Top-K retrieval via cosine similarity.
- **BM25 Sparse Keyword Search**: In-memory inverted index for exact automotive identifier matching.
- **Reciprocal Rank Fusion (RRF)**: Merges dense and sparse ranks with constant $k=60$.

### 3.6 Local LLM Inference Layer (Ollama — Port 11434)
- **Model**: `llama3.2:3b` executing locally via Ollama HTTP REST API (`/api/generate`).
- **Prompt Structure**: Strictly grounded system prompt enforcing citations, forbidding hallucination, and requiring abstention when evidence is insufficient.

### 3.7 Relational Persistence Layer (SQLite 3)
- SQLAlchemy 2.0 ORM manages 14 relational tables in `./data/autosar_ai.db`.
- Foreign key constraints ensure referential integrity; deleting a document cascades to chunks, entities, and citations.

### 3.8 Security & Reporting Layer
- Neutralizes CSV formula injection attacks (`=`, `+`, `-`, `@`) by prepending a single quote `'`.
- Enforces multi-project tenant isolation and input validation.
