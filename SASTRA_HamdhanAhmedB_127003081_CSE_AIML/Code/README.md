# AUTOSAR AI — Codebase & Execution Guide

This directory contains the production-grade source code, backend services, Streamlit frontend application, automated test suites, Docker orchestration, and utility scripts for the **AUTOSAR AI — High-Level Design Document Intelligence Platform**.

---

## 1. Supported Runtime Requirements

- **Operating System:** Windows 10/11, Linux (Ubuntu 22.04+), or macOS
- **Python Version:** Python 3.11+ (Python 3.11.9 verified)
- **Local LLM Engine:** Ollama daemon with `llama3.2:3b` model (listening on `http://127.0.0.1:11434`)
- **Embedding Model:** Local SentenceTransformers (`all-MiniLM-L6-v2`, 384-dimensional dense vectors)
- **Vector Database:** Embedded ChromaDB (`chromadb>=0.4.24`)
- **Relational Database:** Embedded SQLite 3 via SQLAlchemy 2.0 ORM with Alembic schema migrations
- **Web Frontend:** Streamlit 1.32+ running on port 8501
- **Backend API:** FastAPI 0.110+ running on port 8000 via Uvicorn

---

## 2. Directory Structure

```text
Code/
├── backend/                  # Asynchronous FastAPI backend service layer
│   ├── api/v1/               # Typed REST API endpoints (10 routers)
│   │   ├── projects.py       # Project CRUD and active workspace management
│   │   ├── documents.py      # PDF upload, PyMuPDF parsing, and chunking
│   │   ├── sessions.py       # Chat sessions and conversational memory
│   │   ├── entities.py       # SWC, Runnable, Port, Signal entity queries
│   │   ├── findings.py       # Architectural violation findings & reviews
│   │   ├── comparisons.py    # Cross-revision HLD comparison & rename diff
│   │   ├── reports.py        # CSV/Markdown audit report generation & sanitization
│   │   ├── settings.py       # System parameters, overlap bounds, model settings
│   │   ├── diagnostics.py    # Multi-subsystem health check probe
│   │   └── evaluation.py     # Benchmark dataset execution and scoring
│   ├── core/
│   │   └── config.py         # Pydantic Settings with .env loading
│   ├── database/             # SQLAlchemy connection & Alembic migration scripts
│   ├── models/
│   │   └── domain.py         # 14 SQLAlchemy ORM entities
│   ├── schemas/
│   │   └── domain.py         # Pydantic v2 validation schemas
│   ├── services/             # Core business logic and intelligence engines
│   │   ├── document_service.py     # PDF parsing, entity regex heuristics
│   │   ├── retrieval_service.py    # Hybrid BM25 + dense Chroma retrieval
│   │   ├── vector_store_service.py # ChromaDB vector indexing and persistence
│   │   ├── llm_service.py          # Local Ollama client & prompt formatting
│   │   ├── grounding_service.py    # Claim segmentation & evidence scoring
│   │   ├── graph_service.py        # Mermaid component dependency graph builder
│   │   ├── report_generator.py     # Sanitized CSV and audit report export
│   │   └── evaluation_service.py   # Benchmark execution and metrics recording
│   └── main.py               # FastAPI application entrypoint and middleware
├── frontend/                 # Interactive 9-page Streamlit web user interface
│   ├── app.py                # Main Streamlit entrance and navigation router
│   ├── pages/                # Multi-page modular interface
│   │   ├── 1_Dashboard.py            # Overview metrics, system status, active docs
│   │   ├── 2_Documents.py            # PDF upload, indexing, and governance status
│   │   ├── 3_Architecture_Explorer.py# Extracted entities and interactive Mermaid graphs
│   │   ├── 4_AI_Assistant.py         # Grounded chat, citation cards, grounding chips
│   │   ├── 5_Comparisons.py          # Cross-version diff, renames, signal type delta
│   │   ├── 6_Findings.py             # Circular dependency & interface rule reviews
│   │   ├── 7_Reports.py              # Downloadable compliance and audit reports
│   │   ├── 8_Settings.py             # System diagnostics probe & configuration
│   │   └── 9_Evaluation.py           # 35-query benchmark evaluation dashboard
│   └── utils/
│       └── ui.py             # Design system, glassmorphism cards, metric badges
├── tests/                    # Automated testing suite (28 passing unit tests)
│   ├── conftest.py           # Pytest fixtures and mock database engine
│   └── unit/                 # 12 unit test modules
├── scripts/                  # Utility, data generation, and packaging scripts
│   ├── create_submission_zip.py       # Deterministic university ZIP packager
│   ├── generate_documentation_markdowns.py # Doc generator
│   └── ...
├── data/                     # Local SQLite database, Chroma storage, and uploads
├── docker/                   # Container configuration files
├── Dockerfile                # Production container specification
├── docker-compose.yml        # Multi-container orchestration (FastAPI + Streamlit + Ollama)
├── requirements.txt          # Pinned Python package dependencies
├── .env.example              # Sanitized environment configuration template
└── run.py                    # Unified single-command launcher with auto-port detection
```

---

## 3. Quick Start (Local Windows / Linux)

### Step 1: Create Virtual Environment
```powershell
# Open terminal in this Code directory
python -m venv venv
.\venv\Scripts\Activate.ps1    # On Linux/macOS: source venv/bin/activate
```

### Step 2: Install Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment
```powershell
Copy-Item .env.example .env     # On Linux: cp .env.example .env
```

### Step 4: Verify Ollama Service
Ensure Ollama is running locally with the required model:
```powershell
ollama serve                    # Start daemon if not running
ollama pull llama3.2:3b         # Pull 3.2B local model (~2.0 GB)
```

### Step 5: Launch Application
Run the automated unified launcher:
```powershell
python run.py
```
This automatically starts:
- **FastAPI Backend:** `http://127.0.0.1:8000` (API Docs: `http://127.0.0.1:8000/docs`)
- **Streamlit Frontend:** `http://localhost:8501`

---

## 4. Running the Automated Test Suite

To run all 28 automated tests across all 12 test modules:
```powershell
pytest tests/ -v
```
Expected output:
```text
======================== 28 passed in 27.35s ========================
```

To run individual subsystem tests:
```powershell
# Test live Ollama connectivity and grounded prompt behavior
pytest tests/unit/test_ollama_llm.py -v

# Test document ingestion, chunking, and ChromaDB vector indexing
pytest tests/unit/test_document_pipeline.py -v

# Test claim segmentation, grounding scores, and citation checks
pytest tests/unit/test_grounding_and_traceability.py -v

# Test architectural comparisons, rename detection, and signal type diff
pytest tests/unit/test_comparisons_and_renames.py -v
```

---

## 5. Docker Deployment

To launch the complete platform using Docker Compose:
```bash
docker compose up --build
```
This deploys:
1. `autosar-ai-backend`: FastAPI on port `8000`.
2. `autosar-ai-frontend`: Streamlit on port `8501`.
3. Persistent volume mapping for SQLite (`data/autosar_ai.db`) and ChromaDB vector store.
