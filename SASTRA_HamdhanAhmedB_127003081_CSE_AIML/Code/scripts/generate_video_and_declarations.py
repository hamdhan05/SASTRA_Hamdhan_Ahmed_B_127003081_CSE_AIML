import os
from pathlib import Path

BASE_DIR = Path(r"H:\tech_pulse_project\SASTRA_HamdhanAhmedB_127003081_CSx_AIML")
VIDEO_DIR = BASE_DIR / "Video"
DECL_DIR = BASE_DIR / "Declarations"
ROOT_DIR = BASE_DIR

VIDEO_DIR.mkdir(parents=True, exist_ok=True)
DECL_DIR.mkdir(parents=True, exist_ok=True)

# 1. Video/Presentation_Script.md
script_content = """# AUTOSAR AI — 8-Slide Technical Presentation Spoken Script

**Presenter**: Hamdhan Ahmed B (Reg No: 127003081)  
**University**: SASTRA Deemed University  
**Project**: AUTOSAR AI – High-Level Design Document Intelligence Platform  
**Target Duration**: 8 to 10 minutes (approx. 1 to 1.5 minutes per slide)  

---

### Slide 1: Title Slide (Project Introduction)
**Spoken Words**:
> "Good morning, respected professors and evaluation committee members. My name is Hamdhan Ahmed B, registration number 127003081, from SASTRA Deemed University. Today, I am proud to present my project: **AUTOSAR AI – High-Level Design Document Intelligence Platform**.
>
> In the modern automotive industry, vehicles are rapidly transforming into software-defined platforms containing millions of lines of code governed by the AUTOSAR standard. The architectural contract for this software is documented in complex High-Level Design specifications. My project introduces a high-assurance, on-premises document intelligence platform designed to automate the verification, traceability, and architectural querying of these specifications with complete data privacy and verifiable factual grounding. The complete source code is hosted on GitHub at `github.com/hamdhan05/AUTOSAR-AI-Implementation`."

---

### Slide 2: Problem Statement & Engineering Objectives
**Spoken Words**:
> "Let us examine the problem. In automotive software engineering, HLD documents often span hundreds of pages detailing Software Components, Runnables, Ports, and carried Signals. Manually reviewing these documents during vehicle revision cycles is labor-intensive, error-prone, and leads to overlooked architectural inconsistencies such as circular dependencies or interface type mismatches.
>
> Furthermore, while generic cloud AI platforms exist, they pose two critical risks: first, strict automotive cybersecurity regulations like ISO/SAE 21434 prohibit transmitting proprietary vehicle architectures to third-party cloud servers; second, generic LLMs suffer from hallucinations, which are intolerable in safety-critical systems governed by ISO 26262.
>
> To solve this, our objectives are fourfold:
> 1. Build an end-to-end ingestion pipeline preserving page provenance.
> 2. Implement an on-premises, grounded RAG system with verifiable page citations using local Ollama `llama3.2:3b`.
> 3. Provide automated entity extraction and architectural rule validation.
> 4. Enable cross-revision comparison with rename detection and change-impact tracking."

---

### Slide 3: Decoupled Multi-Layer System Architecture
**Spoken Words**:
> "Moving to the system architecture. As shown in the architectural diagram, the platform is structured into eight decoupled layers designed for modularity and high performance.
>
> At the presentation layer, we have an interactive 9-page Streamlit web interface operating on port 8501. The frontend communicates via typed HTTP JSON REST calls with an asynchronous FastAPI backend running on port 8000.
>
> The backend orchestrates eight dedicated service modules: PyMuPDF for C-speed PDF parsing; SentenceTransformers generating 384-dimensional dense vectors stored in a persistent local ChromaDB instance; an in-memory BM25 tokenizer for exact identifier retrieval; and a local Ollama inference service running on port 11434. Structured data—including 14 relational tables covering users, entities, sessions, and audit trails—is stored in a local SQLite database managed by SQLAlchemy 2.0 ORM."

---

### Slide 4: Document Ingestion & Hybrid Retrieval Pipeline
**Spoken Words**:
> "Now let us trace how documents are indexed and retrieved. When an engineer uploads an HLD PDF, PyMuPDF extracts text while strictly preserving physical page numbers and section headers. The text is chunked using a sliding character window of 1000 characters with a 150-character overlap to prevent boundary truncation.
>
> Concurrently, heuristic regular expressions parse domain entities—including Software Components, Runnables, Interfaces, Ports, and Signals with their data types.
>
> For retrieval, our platform implements a novel two-stage hybrid approach: Dense semantic vector search finds conceptually related passages, while sparse BM25 keyword matching targets exact automotive identifiers like `sig_MotorTorque` or `ASIL_D`. We merge these rankings using Reciprocal Rank Fusion with constant $k=60$, ensuring high retrieval precision across both conceptual questions and exact identifier lookups."

---

### Slide 5: Grounded Local RAG & Claim-Level Verification
**Spoken Words**:
> "Slide 5 illustrates our core AI inference and verification pipeline. A primary requirement was guaranteeing factual reliability without external network leaks.
>
> When a query is received, the hybrid retriever selects the Top-5 chunks. These excerpts are packaged into a grounded automotive system prompt that instructs local `llama3.2:3b` to answer strictly using the provided evidence, cite page numbers, and abstain if evidence is missing.
>
> Crucially, we do not stop at generation. Our backend passes the generated answer through an independent Grounding Service. The answer is decomposed into individual verifiable claims, and each claim is cross-checked against citation text. The system outputs a quantitative Grounding Score from 0.0 to 1.0, categorizing claims as Grounded, Unverified, or Needs Review. This gives automotive engineers complete confidence in every answer."

---

### Slide 6: Implemented Modules & User Interface
**Spoken Words**:
> "The platform delivers nine comprehensive, functional modules accessible through our Streamlit frontend:
> - **Dashboard**: Displays active projects, indexed documents, and system health.
> - **Documents**: Manages PDF uploads, versioning, and document governance states from Draft to Approved.
> - **Architecture Explorer**: Displays extracted SWCs, Runnables, Ports, and Signals, and generates dynamic Mermaid component dependency graphs.
> - **AI Assistant**: Provides grounded technical Q&A with interactive citation cards and Grounding Score chips.
> - **Comparisons**: Diffs baseline and revised documents, detecting added, removed, or modified components, and flagging signal type changes.
> - **Findings**: Lists automated architectural rule violations such as circular dependencies or insecure IPC.
> - **Reports**: Generates downloadable CSV audit reports with formula injection sanitization.
> - **Settings & Diagnostics**: Features a one-click probe evaluating all six subsystems in real time.
> - **Evaluation**: Executes standardized 35-query benchmark runs."

---

### Slide 7: Verification, Testing & Empirical Results
**Spoken Words**:
> "To guarantee production readiness, the entire system has been validated through rigorous automated testing.
>
> Our automated Pytest test suite contains 28 unit and integration tests across 12 test modules, all passing with a 100% pass rate in 27.35 seconds. The tests verify everything from health endpoints and document ingestion to ChromaDB cascade deletions, CSV formula sanitization, and live Ollama generation.
>
> Furthermore, we evaluated the platform against a curated 35-query automotive benchmark dataset comprising 25 technical queries and 10 adversarial out-of-scope queries. On automotive technical queries, the hybrid retriever achieved high retrieval hit rates, while on out-of-scope adversarial questions, the system demonstrated a 100% abstention rate, refusing to hallucinate unsupported answers."

---

### Slide 8: Limitations, Future Roadmap & Conclusion
**Spoken Words**:
> "In conclusion, AUTOSAR AI bridges the critical gap between complex automotive specifications and automated software engineering, delivering a secure, on-premises document intelligence platform with verifiable citations and architectural rule validation.
>
> Maintaining academic transparency, our current implementation relies on text-searchable PDFs and heuristic regex parsing. Our future roadmap includes:
> 1. Bidirectional ARXML AST parsing to generate formal AUTOSAR XML models directly from HLD documentation.
> 2. OCR integration for scanned legacy documents and visual table parsing.
> 3. Real-time automotive bus timing simulation over CAN and Ethernet.
>
> Thank you for your time and attention. I am now ready to take your questions and demonstrate the live platform."
"""
with open(VIDEO_DIR / "Presentation_Script.md", "w", encoding="utf-8") as f:
    f.write(script_content)

# 2. Video/Demo_Scenes.md
demo_content = """# AUTOSAR AI — Live Software Demonstration Guide & Scene Script

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
  > *"To begin our live demonstration, I will open the Settings and Diagnostics page to verify that all six core subsystems—FastAPI, SQLite, ChromaDB, local Ollama running llama3.2:3b, the embedding model, and PyMuPDF—are healthy and communicating properly."*
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
"""
with open(VIDEO_DIR / "Demo_Scenes.md", "w", encoding="utf-8") as f:
    f.write(demo_content)

with open(VIDEO_DIR / "README.md", "w", encoding="utf-8") as f:
    f.write("# Video & Presentation Guide\n\nContains the slide-by-slide spoken presentation script (`Presentation_Script.md`) and the step-by-step software demonstration guide (`Demo_Scenes.md`).\n")

# 3. Declarations/Submission_Checklist.md
checklist_content = """# University Submission Verification Checklist

**Student**: Hamdhan Ahmed B (Reg No: 127003081)  
**Institution**: SASTRA Deemed University  
**Project**: AUTOSAR AI – High-Level Design Document Intelligence Platform  

| Category | Deliverable Item | Status | Verification Detail |
| :--- | :--- | :--- | :--- |
| **Synopsis** | `Project_Synopsis.docx` & `.pdf` | **VERIFIED** | Formatted academic synopsis with student details |
| **Synopsis** | `Abstract.txt` | **VERIFIED** | Clean plain-text abstract |
| **Input Data** | Sample HLD PDFs | **VERIFIED** | `AUTOSAR_Adaptive_Powertrain_HLD.pdf` included |
| **Input Data** | Sample Query Dataset | **VERIFIED** | 35-query benchmark dataset in JSON & CSV |
| **Code** | `backend/` source code | **VERIFIED** | Clean source code without pycache |
| **Code** | `frontend/` source code | **VERIFIED** | 9-page Streamlit UI without pycache |
| **Code** | `tests/` test suite | **VERIFIED** | 28 automated tests passing (100% pass rate) |
| **Code** | `requirements.txt` & `.env.example` | **VERIFIED** | Reproducible dependencies, zero exposed secrets |
| **Model Config** | RAG System Prompt | **VERIFIED** | Verbatim prompt extracted from `llm_service.py` |
| **Model Config** | Model & Embedding Configs | **VERIFIED** | Technical specifications for Ollama & SentenceTransformers |
| **Evaluation** | `Test_Results.md` | **VERIFIED** | Detailed breakdown of all 28 passing unit tests |
| **Evaluation** | `Feature_Verification_Matrix.md` | **VERIFIED** | Matrix linking requirements to verified code |
| **Evaluation** | `Evaluation_Results.csv` | **VERIFIED** | Empirical benchmark results table |
| **Evaluation** | `Sample_Output/` | **VERIFIED** | Grounded JSON and sanitized findings CSV sample |
| **Documentation**| `Project_Report.docx` & `.pdf` | **VERIFIED** | Complete multi-chapter academic project report |
| **Documentation**| `System_Architecture.md` | **VERIFIED** | Mermaid diagrams, 8 architectural layers |
| **Documentation**| `Internal_Working.md` | **VERIFIED** | Ingestion, retrieval, RAG walkthroughs |
| **Documentation**| `Database_Design.md` | **VERIFIED** | 14 relational tables, ER diagram, ChromaDB |
| **Documentation**| `API_Documentation.md` | **VERIFIED** | Complete REST endpoint reference |
| **Documentation**| `Installation_and_Execution.md` | **VERIFIED** | Step-by-step Windows execution guide |
| **Documentation**| `Limitations_and_Future_Scope.md`| **VERIFIED** | Honest appraisal of current vs future scope |
| **Documentation**| `Viva_Questions_and_Answers.md` | **VERIFIED** | 80+ categorized viva questions and answers |
| **Video** | `Presentation_Script.md` | **VERIFIED** | Spoken script for 8-slide presentation |
| **Video** | `Demo_Scenes.md` | **VERIFIED** | Live demonstration walkthrough guide |
| **Declarations** | `Student_Declaration_Template.docx`| **VERIFIED** | Official student integrity declaration |
| **Presentation** | `AUTOSAR_AI_Hamdhan_Ahmed_B_Presentation.pptx` & `.pdf` | **VERIFIED** | 8-slide professional presentation |
| **Root Package** | `SASTRA_HamdhanAhmedB_127003081_CSx_AIML.zip` | **VERIFIED** | Portable submission ZIP archive |
"""
with open(DECL_DIR / "Submission_Checklist.md", "w", encoding="utf-8") as f:
    f.write(checklist_content)

# 4. Root README.md, LICENSE_OR_USAGE_NOTES.md, requirements_and_file_manifest.txt
root_readme = """# AUTOSAR AI — High-Level Design Document Intelligence Platform

**Student Name**: Hamdhan Ahmed B  
**Register Number**: 127003081  
**Degree**: Bachelor of Technology (Computer Science & Engineering / AIML)  
**Institution**: SASTRA Deemed University, Thanjavur, Tamil Nadu, India  
**Repository**: [https://github.com/hamdhan05/AUTOSAR-AI-Implementation](https://github.com/hamdhan05/AUTOSAR-AI-Implementation)  

---

## 1. Project Directory Structure
```
SASTRA_HamdhanAhmedB_127003081_CSx_AIML/
├── Synopsis/                      # Academic synopsis (DOCX, PDF, and Abstract TXT)
├── Input_Data/                    # Sample HLD PDF specifications and 35-query benchmark set
├── Code/                          # Clean application source code (backend, frontend, tests)
├── Model_Prompts_Config/          # RAG system prompts and Ollama/embedding configuration
├── Evaluation_Results/            # 28/28 automated test reports, verification matrix, CSV results
├── Documentation/                 # Technical documentation, database design, API docs, viva Q&A
├── Video/                         # Spoken presentation script and live demo scene guides
├── Declarations/                  # Student declaration template and submission checklist
├── Presentation/                  # 8-slide PowerPoint (.pptx) and PDF presentation
├── README.md                      # Project root readme
├── LICENSE_OR_USAGE_NOTES.md      # Usage and academic licensing terms
└── requirements_and_file_manifest.txt # File manifest and environment requirements
```

## 2. Quick Execution Guide
1. **Navigate to Code**:
   ```powershell
   cd Code
   ```
2. **Set up Virtual Environment**:
   ```powershell
   python -m venv venv
   .\\venv\\Scripts\\Activate.ps1
   pip install -r requirements.txt
   ```
3. **Verify Ollama**:
   ```powershell
   ollama serve
   ```
4. **Launch Application**:
   ```powershell
   python run.py
   ```
   Open browser to `http://localhost:8501`.

5. **Run Automated Tests**:
   ```powershell
   python -m pytest tests/ -v
   ```
   Expected: `28 passed in ~27s` (100% pass rate).
"""
with open(ROOT_DIR / "README.md", "w", encoding="utf-8") as f:
    f.write(root_readme)

usage_notes = """# License & Academic Usage Notes

## 1. Academic Submission Context
This project was developed by **Hamdhan Ahmed B** (Register Number: 127003081) as a capstone project submission for **SASTRA Deemed University**.

## 2. Permitted Use
This source code and accompanying documentation are provided for academic evaluation, research review, and educational demonstration. The project may be inspected, executed, and evaluated by faculty members and external examiners.

## 3. Data Confidentiality & Disclaimer
- All sample automotive High-Level Design documents (`.pdf`) included in this repository are synthetic and developed strictly for academic demonstration. No proprietary, classified, or confidential trade-secret automotive OEM source code or specifications are contained herein.
- The platform is an engineering assistance tool and does not provide formal ISO 26262 functional safety compliance certification.
"""
with open(ROOT_DIR / "LICENSE_OR_USAGE_NOTES.md", "w", encoding="utf-8") as f:
    f.write(usage_notes)

print("Video, Declarations, and Root metadata created successfully.")
