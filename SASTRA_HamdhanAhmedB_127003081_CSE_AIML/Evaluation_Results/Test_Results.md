# AUTOSAR AI — Automated Test Suite Results

## 1. Test Execution Metadata
- **Test Framework**: Pytest 9.1.1
- **Python Version**: Python 3.11.9
- **Platform**: Windows 11 (win32)
- **Execution Date**: October 13, 2026
- **Test Command**: `.\venv\Scripts\python.exe -m pytest tests/ -v`
- **Execution Time**: 27.35 seconds
- **Total Test Cases**: **28**
- **Passed**: **28 (100%)**
- **Failed**: **0 (0%)**
- **Warnings**: 3 (Pydantic v2 migration deprecation warnings)

---

## 2. Complete Automated Test Case Register

| Module | Test Function Name | Subsystem Tested | Status | Latency / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `test_comparison_and_reports.py` | `test_csv_formula_injection_sanitization` | Security / CSV Export | **PASSED** | Validates formula sanitization (`=`, `+`, `-`, `@`) |
| `test_comparison_and_reports.py` | `test_document_comparison_and_history` | Architecture Comparison | **PASSED** | Validates entity diff & comparison history |
| `test_comparison_and_reports.py` | `test_report_generation_and_download` | Reporting Engine | **PASSED** | Verifies CSV creation & download endpoint |
| `test_comparisons_and_renames.py` | `test_rename_detection_and_data_type_diff` | Revision Comparison | **PASSED** | Detects component renames & signal data type deltas |
| `test_docs.py` | `test_create_project` | Project Management API | **PASSED** | Creates project in SQLite with metadata |
| `test_docs.py` | `test_get_projects` | Project Management API | **PASSED** | Retrieves project listing |
| `test_docs.py` | `test_upload_invalid_file` | Input Validation | **PASSED** | Rejects non-PDF upload with 400 Bad Request |
| `test_document_pipeline.py` | `test_chunking_and_entity_extraction` | Ingestion / Regex Heuristics | **PASSED** | Verifies chunking & entity parsing (SWC, Runnable, Interface) |
| `test_document_pipeline.py` | `test_full_document_ingestion_and_cleanup` | End-to-End Pipeline | **PASSED** | Multi-page PDF ingestion, ChromaDB vector indexing, cascade delete |
| `test_grounding_and_traceability.py` | `test_claim_segmentation` | Claim Decomposition | **PASSED** | Splits engineering answer into verifiable claims |
| `test_grounding_and_traceability.py` | `test_evidence_verification_grounded_vs_unverified` | Grounding Verification | **PASSED** | Verifies claims against citation excerpts |
| `test_grounding_and_traceability.py` | `test_grounding_score_and_confidence_classification` | Grounding Metric | **PASSED** | Calculates numerical score & confidence rating |
| `test_grounding_and_traceability.py` | `test_abstention_claim_handling` | Abstention Logic | **PASSED** | Accurately classifies negative evidence abstentions |
| `test_hybrid_retrieval_and_eval.py` | `test_bm25_tokenization_and_scoring` | Sparse Retrieval / BM25 | **PASSED** | Validates BM25 index scoring against keyword queries |
| `test_hybrid_retrieval_and_eval.py` | `test_evaluation_dataset_structure` | Benchmark Data | **PASSED** | Validates 35 queries (25 technical + 10 adversarial) |
| `test_hybrid_retrieval_and_eval.py` | `test_evaluation_benchmark_run` | Evaluation Service | **PASSED** | Runs benchmark & verifies `BenchmarkRun` DB persistence |
| `test_main.py` | `test_health_check` | Core Health API | **PASSED** | Verifies `/health` returns status `ok` |
| `test_main.py` | `test_health_check_v1` | Core Health API v1 | **PASSED** | Verifies `/api/v1/health` returns status `ok` |
| `test_ollama_llm.py` | `test_active_provider_info` | LLM Service | **PASSED** | Confirms provider `ollama`, model `llama3.2:3b`, local mode |
| `test_ollama_llm.py` | `test_ollama_connection_diagnostic` | Live LLM Connectivity | **PASSED** | Live HTTP probe to Ollama server & test generation |
| `test_ollama_llm.py` | `test_ask_question_insufficient_evidence` | Grounded Prompt | **PASSED** | Asserts non-empty abstention message on zero evidence |
| `test_ports_signals_relationships.py` | `test_ports_and_signals_extraction` | Entity Extraction | **PASSED** | Validates regex extraction of PPorts, RPorts, and Signals |
| `test_ports_signals_relationships.py` | `test_mermaid_generation_and_dependency_traversal` | Topology Visualization | **PASSED** | Generates Mermaid syntax from component relationships |
| `test_reviews_and_audit.py` | `test_query_review_submission_and_audit_log` | Review & Governance | **PASSED** | Validates engineer feedback & audit trail logging |
| `test_settings_and_diagnostics.py` | `test_settings_validation_and_persistence` | Settings Engine | **PASSED** | Rejects invalid overlap bounds & saves configuration |
| `test_settings_and_diagnostics.py` | `test_system_diagnostics_endpoint` | Diagnostics Subsystem | **PASSED** | Probes all 6 core subsystems returning overall PASS |
| `test_settings_and_diagnostics.py` | `test_findings_and_entity_review` | Findings Workflow | **PASSED** | Updates review status and engineer comments |
| `test_versioning_and_governance.py` | `test_document_governance_and_versioning` | Document Governance | **PASSED** | Tests version transitions (DRAFT -> IN_REVIEW -> APPROVED) |

---

## 3. Test Coverage & Subsystem Health Summary
- **API Routers Tested**: 10 of 10 routers covered.
- **Service Modules Tested**: 8 of 8 service modules covered.
- **ORM Models Tested**: 14 of 14 database models validated.
- **Security Protections**: CSV formula injection sanitization and path traversal safeguards verified.
