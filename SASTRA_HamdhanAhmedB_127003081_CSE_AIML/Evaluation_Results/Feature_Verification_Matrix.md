# Feature Verification Matrix

| Requirement / Subsystem | Implemented Component | Verification Method | Status | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **PDF Ingestion & Text Extraction** | PyMuPDF (`fitz`) in `document_service.py` | Automated Unit Test `test_full_document_ingestion_and_cleanup` | **VERIFIED** | Preserves page numbering and bounds |
| **Character Chunking & Overlap** | Sliding window in `document_service.py` | Automated Unit Test `test_chunking_and_entity_extraction` | **VERIFIED** | Default 1000 chars, 150 overlap |
| **Vector Embedding Storage** | SentenceTransformers + ChromaDB | Automated Unit Test `test_full_document_ingestion_and_cleanup` | **VERIFIED** | Persistent vector store on local disk |
| **Relational Database Management** | SQLite 3 + SQLAlchemy ORM (14 models) | Automated Unit Test `test_create_project`, DB migrations | **VERIFIED** | Full foreign-key referential integrity |
| **Entity Extraction (SWCs, Runnables)** | Regex heuristics in `document_service.py` | Automated Unit Test `test_chunking_and_entity_extraction` | **VERIFIED** | Extracts components with source page metadata |
| **Ports & Signals Extraction** | Regex parser in `document_service.py` | Automated Unit Test `test_ports_and_signals_extraction` | **VERIFIED** | Extracts PPorts, RPorts, and signal types |
| **Architecture Topology Generation** | Mermaid generator in `graph_service.py` | Automated Unit Test `test_mermaid_generation_and_dependency_traversal` | **VERIFIED** | Dynamic component dependency graphs |
| **Architectural Rules & Findings** | Rule evaluator in `document_service.py` | Automated Unit Test `test_full_document_ingestion_and_cleanup` | **VERIFIED** | Flags circular dependencies & missing ports |
| **Local LLM Inference** | Ollama (`llama3.2:3b`) in `llm_service.py` | Automated Unit Test `test_ollama_connection_diagnostic` | **VERIFIED** | 100% on-premises offline execution |
| **Grounded Prompting & Abstention** | Custom system prompt in `llm_service.py` | Automated Unit Test `test_ask_question_insufficient_evidence` | **VERIFIED** | Abstains when evidence is insufficient |
| **Claim Decomposition & Verification** | Claim splitter in `grounding_service.py` | Automated Unit Test `test_claim_segmentation` | **VERIFIED** | Segments answers into verifiable propositions |
| **Grounding Score Metric** | Numerical evaluator in `grounding_service.py` | Automated Unit Test `test_grounding_score_and_confidence_classification` | **VERIFIED** | Produces Grounding Score (0.0 to 1.0) |
| **BM25 Sparse Retrieval** | In-memory BM25 index in `retrieval_service.py` | Automated Unit Test `test_bm25_tokenization_and_scoring` | **VERIFIED** | Keyword search for technical identifiers |
| **Reciprocal Rank Fusion (RRF)** | Hybrid rank fusion in `retrieval_service.py` | Automated Unit Test `test_hybrid_retrieval_and_eval.py` | **VERIFIED** | Merges Dense + BM25 rankings (k=60) |
| **HLD Revision Comparison** | Diff engine in `comparisons.py` | Automated Unit Test `test_document_comparison_and_history` | **VERIFIED** | Entity additions, removals, modifications |
| **Rename Detection & Type Diffs** | Heuristic matcher in `comparisons.py` | Automated Unit Test `test_rename_detection_and_data_type_diff` | **VERIFIED** | Identifies renamed SWCs & signal alterations |
| **CSV Export & Security Sanitization** | `report_generator.py` | Automated Unit Test `test_csv_formula_injection_sanitization` | **VERIFIED** | Neutralizes `=cmd`, `+`, `-`, `@` triggers |
| **Document Governance & Audit Trail** | Governance lifecycle & `AuditLog` model | Automated Unit Test `test_document_governance_and_versioning` | **VERIFIED** | Full audit tracking of review decisions |
| **System Diagnostics** | Multi-subsystem probe in `diagnostics.py` | Automated Unit Test `test_system_diagnostics_endpoint` | **VERIFIED** | Probes FastAPI, SQLite, ChromaDB, Ollama |
| **Benchmark Evaluation Engine** | 35-query evaluation in `evaluation_service.py`| Automated Unit Test `test_evaluation_benchmark_run` | **VERIFIED** | Computes MRR, Hit Rate@1, Latency |
