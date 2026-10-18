# AUTOSAR AI â€” Live Software Demonstration Guide & Scene Script

## 1. Demonstration Checklist Before You Begin
- [ ] Ensure local Ollama is running: `ollama serve` in a background terminal.
- [ ] Ensure FastAPI backend is running: `http://localhost:8000/docs` reachable.
- [ ] Ensure Streamlit UI is running: `http://localhost:8501` open in browser.
- [ ] Have sample PDF ready: `Input_Data/Sample_HLD_Documents/AUTOSAR_Adaptive_Powertrain_HLD.pdf`.

---

## 2. Scene-by-Scene Demonstration Walkthrough

### Scene 1: Dashboard & System Health Diagnostic (1 minute)
- **Action**: Open browser to `http://localhost:8501`. Navigate to **Settings** (`8_Settings.py`). Click **Run System Diagnostics**.
- **What to Say**:
  > *"To begin our live demonstration, I will open the Settings and Diagnostics page to verify that all six core subsystemsâ€”FastAPI, SQLite, ChromaDB, local Ollama running llama3.2:3b, the embedding model, and PyMuPDFâ€”are healthy and communicating properly."*
- **Expected Result**: All 6 checks display green **PASS** badges.
- **Fallback Plan**: If Ollama shows an error, verify `ollama serve` in the terminal and click retry.

### Scene 2: Document Ingestion & Architecture Extraction (2 minutes)
- **Action**: Navigate to **Documents** (`2_Documents.py`). Select `Default Project`. Drag and drop `AUTOSAR_Adaptive_Powertrain_HLD.pdf`.
- **What to Say**:
  > *"Now I will upload an AUTOSAR Adaptive Powertrain High-Level Design document. As you can see, PyMuPDF immediately parses the 12 pages, creates 38 chunks with 150-character overlap, extracts domain entities, generates 384-dimensional dense embeddings, and stores them in persistent local ChromaDB. The document badge transitions to green INDEXED."*
- **Action**: Click on **Architecture Explorer** (`3_Architecture_Explorer.py`).
- **What to Say**:
  > *"In the Architecture Explorer, we can see the extracted Software Components like PowertrainManager and BatteryManagement, their Runnables, Ports, and carried Signals with their data types. The platform also renders an interactive Mermaid dependency graph showing how these components interact."*

### Scene 3: Grounded AI Query with Citations & Verification (2 minutes)
- **Action**: Navigate to **AI Assistant** (`4_AI_Assistant.py`). Enter query:
  `Which software component manages engine operations and torque arbitration?`
  Click **Submit Query**.
- **What to Say**:
  > *"Now I will ask a technical architectural question. The backend executes our hybrid Dense-plus-BM25 retrieval pipeline, merges the results using Reciprocal Rank Fusion, and formats our grounded prompt for local Ollama. Notice the response: it explicitly identifies the PowertrainManager component and provides an exact citation card linking to Page 4 of the HLD. Furthermore, our Grounding Service has decomposed the answer into claims and verified that the statement is Grounded with a High Confidence Grounding Score of 0.95."*
- **Action**: Submit an adversarial / out-of-scope query:
  `What is the capital city of France?`
- **What to Say**:
  > *"When an out-of-scope or unanswerable query is submitted, observe that the system does not hallucinate; it strictly abstains, confirming that the available documents do not provide sufficient evidence."*

### Scene 4: Architectural Findings & Revision Comparison (1.5 minutes)
- **Action**: Navigate to **Findings** (`6_Findings.py`).
- **What to Say**:
  > *"The platform automatically applies architectural validation rules. Here we see an Insecure IPC finding and a Circular Dependency finding between BatteryManagement and PowertrainManager. As an architect, I can review this finding, mark it Confirmed, and enter review notes, which are permanently logged in our SQLite audit trail."*
- **Action**: Navigate to **Comparisons** (`5_Comparisons.py`).
- **What to Say**:
  > *"Finally, when updated HLD revisions arrive, the Comparison module diffs baseline against revised specifications, highlighting added and removed components and detecting component renames and signal type alterations."*
