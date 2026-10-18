# AUTOSAR AI — Installation, Setup and Execution Guide

## 1. System Requirements & Prerequisites
- **Operating System**: Windows 10 / Windows 11 (64-bit)
- **Python**: Python 3.11.x (tested on Python 3.11.9)
- **Ollama**: Local Ollama runtime installed (`ollama --version`)
- **Model**: `llama3.2:3b` pulled locally
- **Hardware Recommended**: 8 GB RAM minimum (16 GB recommended), 10 GB free disk space

---

## 2. Step-by-Step Installation

### Step 1: Verify Ollama Service and Model
1. Open PowerShell and verify Ollama is installed:
   ```powershell
   ollama list
   ```
2. If `llama3.2:3b` is not listed, pull it:
   ```powershell
   ollama pull llama3.2:3b
   ```
3. Start the Ollama background daemon:
   ```powershell
   ollama serve
   ```

### Step 2: Set Up Python Virtual Environment
1. Navigate to the submission `Code` directory:
   ```powershell
   cd SASTRA_HamdhanAhmedB_127003081_CSx_AIML\Code
   ```
2. Create a clean virtual environment:
   ```powershell
   python -m venv venv
   ```
3. Activate the virtual environment:
   ```powershell
   .env\Scripts\Activate.ps1
   ```
4. Install all dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Default settings in `.env`:
```ini
APP_NAME=AUTOSAR AI
ENVIRONMENT=development
DATABASE_URL=sqlite:///./data/autosar_ai.db
VECTOR_STORE_DIR=./data/vector_store
UPLOAD_DIR=./data/uploads
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
EMBEDDING_MODEL=all-MiniLM-L6-v2
DEFAULT_CHUNK_SIZE=1000
DEFAULT_CHUNK_OVERLAP=150
DEFAULT_TOP_K=5
```

---

## 3. Running the Application

### Method 1: Dual-Terminal Execution (Recommended)

**Terminal 1 — FastAPI Backend:**
```powershell
.env\Scripts\Activate.ps1
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Health Check: `http://localhost:8000/health`
- Swagger Documentation: `http://localhost:8000/docs`

**Terminal 2 — Streamlit Frontend:**
```powershell
.env\Scripts\Activate.ps1
python -m streamlit run frontend/app.py --server.port 8501
```
- Open your browser to: `http://localhost:8501`

### Method 2: Unified Launcher
```powershell
python run.py
```

---

## 4. Running Automated Tests
Execute the full test suite to verify all 28 automated tests:
```powershell
python -m pytest tests/ -v
```
Expected output:
```text
======================= 28 passed in ~27s =======================
```
