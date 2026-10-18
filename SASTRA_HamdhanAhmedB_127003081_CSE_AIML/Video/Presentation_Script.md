# AUTOSAR AI â€” 8-Slide Technical Presentation Spoken Script

**Presenter**: Hamdhan Ahmed B (Reg No: 127003081)  
**University**: SASTRA Deemed University  
**Project**: AUTOSAR AI â€“ High-Level Design Document Intelligence Platform  
**Target Duration**: 8 to 10 minutes (approx. 1 to 1.5 minutes per slide)  

---

### Slide 1: Title Slide (Project Introduction)
**Spoken Words**:
> "Good morning, respected professors and evaluation committee members. My name is Hamdhan Ahmed B, registration number 127003081, from SASTRA Deemed University. Today, I am proud to present my project: **AUTOSAR AI â€“ High-Level Design Document Intelligence Platform**.
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
> The backend orchestrates eight dedicated service modules: PyMuPDF for C-speed PDF parsing; SentenceTransformers generating 384-dimensional dense vectors stored in a persistent local ChromaDB instance; an in-memory BM25 tokenizer for exact identifier retrieval; and a local Ollama inference service running on port 11434. Structured dataâ€”including 14 relational tables covering users, entities, sessions, and audit trailsâ€”is stored in a local SQLite database managed by SQLAlchemy 2.0 ORM."

---

### Slide 4: Document Ingestion & Hybrid Retrieval Pipeline
**Spoken Words**:
> "Now let us trace how documents are indexed and retrieved. When an engineer uploads an HLD PDF, PyMuPDF extracts text while strictly preserving physical page numbers and section headers. The text is chunked using a sliding character window of 1000 characters with a 150-character overlap to prevent boundary truncation.
>
> Concurrently, heuristic regular expressions parse domain entitiesâ€”including Software Components, Runnables, Interfaces, Ports, and Signals with their data types.
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
