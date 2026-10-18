# AUTOSAR AI — Troubleshooting Guide

## 1. Service Port Conflicts

### Issue: FastAPI backend fails to start (`Port 8000 already in use`)
- **Cause**: A previous uvicorn instance or background service is occupying port 8000.
- **Diagnosis**:
  ```powershell
  Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess
  ```
- **Resolution**:
  ```powershell
  Stop-Process -Id <OwningProcessId> -Force
  ```
  Or change the port in `backend/main.py` or startup command:
  ```powershell
  uvicorn backend.main:app --port 8001
  ```

### Issue: Streamlit frontend fails to start (`Port 8501 is already in use`)
- **Resolution**:
  ```powershell
  streamlit run frontend/app.py --server.port 8502
  ```

---

## 2. Ollama & Local LLM Issues

### Issue: `Cannot connect to local Ollama at http://localhost:11434`
- **Cause**: Ollama background service is not running.
- **Resolution**:
  1. Open a new PowerShell window and run:
     ```powershell
     ollama serve
     ```
  2. Verify reachability:
     ```powershell
     curl http://localhost:11434/api/tags
     ```

### Issue: `Ollama model 'llama3.2:3b' not found`
- **Resolution**: Pull the required model:
  ```powershell
  ollama pull llama3.2:3b
  ```

### Issue: Ollama generation times out after 120 seconds
- **Cause**: High CPU/RAM load or model is loading into memory for the first time.
- **Resolution**:
  - Warm up the model by sending a short test prompt:
    ```powershell
    ollama run llama3.2:3b "test"
    ```
  - Close memory-intensive background applications.

---

## 3. Database & Vector Store Issues

### Issue: ChromaDB file lock on Windows (`PermissionError` on `chroma.sqlite3`)
- **Cause**: Another Python process has an exclusive lock on the SQLite file.
- **Resolution**: Ensure previous Python test or server processes are terminated:
  ```powershell
  Get-Process python | Stop-Process -Force
  ```

### Issue: SQLite schema migration or missing table errors
- **Resolution**: Run the automatic migration or delete the local development database file to trigger clean initialization:
  ```powershell
  Remove-Item data/autosar_ai.db
  # Re-launch backend to create all 14 tables automatically
  ```

---

## 4. Document Ingestion Issues

### Issue: Upload rejected with `400 Bad Request`
- **Cause**: Uploaded file is not a valid PDF or has an invalid MIME type.
- **Resolution**: Verify file is a valid `.pdf` document.

### Issue: Extracted document contains 0 chunks or empty text
- **Cause**: The PDF is a scanned bitmap without an embedded text layer.
- **Resolution**: Use text-searchable PDFs or run OCR prior to ingestion.
