# AUTOSAR AI — Internal Working & End-to-End Walkthroughs

## 1. Document Ingestion & Indexing Pipeline

When an automotive engineer uploads a High-Level Design (HLD) PDF, the platform executes the following sequential steps:

1. **Upload & Validation**:
   - The frontend submits the file via `POST /api/v1/documents/upload`.
   - The backend validates the MIME type and extension (`.pdf`). Non-PDF files are rejected with `400 Bad Request`.
   - The document is saved to disk (`data/uploads/<filename>`) and its SHA-256 hash is computed to prevent duplicate processing.
   - An entry is created in the SQLite `documents` table with status `UPLOADED`.

2. **Text Extraction via PyMuPDF**:
   - `backend/services/document_service.py` opens the PDF using `fitz.open(storage_path)`.
   - The total page count is recorded.
   - Text is extracted page-by-page, preserving page numbering (`page_start`, `page_end`) and section headings.

3. **Text Chunking**:
   - A sliding character window extracts chunks of **1000 characters** with an overlap of **150 characters**.
   - Overlap ensures that architectural definitions spanning chunk boundaries are not fragmented.
   - Each chunk receives a deterministic content hash and is written to the SQLite `document_chunks` table.

4. **Heuristic Architecture Entity Extraction**:
   - During chunk iteration, regex patterns identify AUTOSAR domain entities:
     - Software Components (`[A-Za-z0-9_]+_(?:SWC|Component|Manager|Controller)`)
     - Runnables (`Runnable_[A-Za-z0-9_]+|re_[A-Za-z0-9_]+`)
     - Interfaces (`[A-Za-z0-9_]+_IF|[A-Za-z0-9_]+_Interface`)
     - Ports (`PPort_[A-Za-z0-9_]+`, `RPort_[A-Za-z0-9_]+`)
     - Signals (`sig_[A-Za-z0-9_]+` with data types like `float32`, `uint16`, `boolean`)
   - Entities are stored in the SQLite `architecture_entities` table with source page numbers and confidence scores.

5. **Dense Vector Embedding & ChromaDB Storage**:
   - `vector_store_service.add_chunks` passes the chunk text strings to the ChromaDB collection `project_{project_id}`.
   - ChromaDB uses SentenceTransformers (`all-MiniLM-L6-v2`) to produce 384-dimensional dense vectors.
   - Vectors and metadata (`document_id`, `chunk_index`, `page_start`, `page_end`, `version_label`) are saved to disk.

6. **Status Finalization**:
   - The document status in SQLite transitions to `INDEXED`.
   - The frontend updates the document badge to green `INDEXED`.

---

## 2. Retrieval-Augmented Generation (RAG) Workflow

When a user asks a question in the AI Assistant:

1. **Query Entry**:
   - The user enters a question (e.g., *"Which component arbitrates motor torque?"*).
   - Streamlit calls `POST /api/v1/sessions/{session_id}/query`.

2. **Hybrid Retrieval (Dense + BM25)**:
   - **Dense Search**: ChromaDB searches the 384-dimensional vector space using cosine similarity, returning the Top-K chunks.
   - **BM25 Search**: An in-memory inverted index tokenizes the query and candidate documents, calculating BM25 relevance scores.
   - **Reciprocal Rank Fusion**: RRF merges the dense and sparse candidate rankings with smoothing constant $k=60$.

3. **Context Assembly**:
   - The top candidate chunks are concatenated into a structured evidence string:
     ```text
     [Document: Powertrain_HLD.pdf, Pages: 4-5, Version: 1.0]
     "The PowertrainManager SWC performs supervisory control and torque arbitration..."
     ```

4. **Local LLM Prompt Formulation & Inference**:
   - The backend constructs the prompt inserting the retrieved context into `{context}` and the user query into `{query}`.
   - A POST request is dispatched to local Ollama (`http://localhost:11434/api/generate`):
     ```json
     {
       "model": "llama3.2:3b",
       "prompt": "<Grounded Prompt>",
       "stream": false
     }
     ```
   - Ollama generates the response within ~2.5 to 4.0 seconds.

5. **Claim Decomposition & Verification**:
   - `grounding_service.py` decomposes the generated answer into individual sentences/claims.
   - Each claim is verified against citation text to ensure factual grounding.
   - Claims are categorized as **Grounded**, **Unverified**, or **Needs Review**.
   - A numerical **Grounding Score** (0.0 to 1.0) and confidence level are calculated.

6. **Persistence & Display**:
   - The query and answer are saved in `analysis_messages` with citation links and grounding metadata.
   - Streamlit displays the response with clickable citation cards, claim tags, and Grounding Score indicators.

---

## 3. Architecture Comparison & Revision Diffing

When an updated revision of an HLD is uploaded:

1. **Selection**:
   - The engineer selects a **Baseline Document** (e.g., v1.0) and a **Revised Document** (e.g., v1.1) in `5_Comparisons.py`.
   - Streamlit triggers `POST /api/v1/comparisons`.

2. **Entity Set Diffing**:
   - The backend loads entities from both documents:
     - Set $B = 	ext{Entities in Baseline}$
     - Set $R = 	ext{Entities in Revision}$
   - **Added Entities**: $R \setminus B$
   - **Removed Entities**: $B \setminus R$
   - **Common Entities**: $B \cap R$

3. **Attribute & Rename Detection**:
   - For common entities, attribute differences (description, ports, signals, data types) are analyzed.
   - Heuristic string similarity detects candidate renamed components (e.g., `Battery_Mgr` renamed to `BatteryManagement_SWC`).

4. **Persistence & Presentation**:
   - The comparison outcome is saved in the `document_comparisons` table as JSON.
   - The UI presents additions in green, deletions in red, and modifications with before/after comparisons.

---

## 4. End-to-End Walkthrough Scenarios

### Walkthrough 1: Ingesting a Powertrain HLD
1. Navigate to **Documents** (`2_Documents.py`).
2. Select project `Default Project`.
3. Upload `AUTOSAR_Adaptive_Powertrain_HLD.pdf`.
4. Observe real-time progress: PyMuPDF extracts 12 pages, creates 38 chunks, identifies 15 SWCs and 8 Interfaces, generates embeddings, and marks the document `INDEXED`.
5. Check **Architecture Explorer** (`3_Architecture_Explorer.py`) to inspect extracted components and the Mermaid topology diagram.

### Walkthrough 2: Querying with Grounded Evidence
1. Open **AI Assistant** (`4_AI_Assistant.py`).
2. Submit query: *"What data type is used for vehicle speed and motor torque signals?"*
3. View response:
   - Generated answer explicitly states `float32` and `uint16`.
   - Citation box displays `Powertrain_HLD.pdf`, Page 6.
   - Claim verification chip displays: `Grounded (Score: 0.94 - High Confidence)`.

### Walkthrough 3: Rule Violation Finding Resolution
1. Open **Findings** (`6_Findings.py`).
2. Observe finding `F002: CIRCULAR_DEPENDENCY between BatteryManagement and PowertrainManager`.
3. Change review status from `Open` to `Confirmed`.
4. Enter engineer remarks: *"Decoupling buffer queue approved for Sprint 14."*
5. Submit review. Verification is written to `findings` table and logged in `audit_logs`.
