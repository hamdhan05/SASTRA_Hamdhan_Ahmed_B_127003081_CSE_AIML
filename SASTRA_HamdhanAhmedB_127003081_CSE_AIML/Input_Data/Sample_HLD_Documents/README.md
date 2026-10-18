# Sample Automotive HLD Documents (`Input_Data/Sample_HLD_Documents/`)

This directory contains realistic and synthetic High-Level Design (HLD) specifications designed to evaluate the **AUTOSAR AI** platform across diverse automotive domains.

---

## 1. Document Inventory

| File | Domain Scope | Purpose in Benchmark |
| :--- | :--- | :--- |
| [`AUTOSAR_Adaptive_Powertrain_HLD.pdf`](AUTOSAR_Adaptive_Powertrain_HLD.pdf) | Powertrain, Battery Management, & Torque Control | Realistic multi-page specification containing Software Components (`PowertrainManager`, `BatteryManagement`), Runnables, PPorts/RPorts, carried Signals, and communication interfaces. Used for live demonstrations and integration testing. |
| [`1_Synthetic_Automotive_Architecture_RAG_Test.pdf`](1_Synthetic_Automotive_Architecture_RAG_Test.pdf) | Synthetic Multi-ECU Control Architecture | Synthetic benchmark blueprint containing structured entity tables and intentional architectural patterns (including circular dependencies) to validate automated findings detection and hybrid retrieval precision. |

---

## 2. Evaluation Usage
- **Uploading in UI:** Navigate to **Documents** (`frontend/pages/2_Documents.py`), select your active project, and upload either document to test PyMuPDF text parsing, 1000/150-char chunking, entity extraction, and ChromaDB vector indexing.
- **Automated Tests:** Ingested during integration tests (`tests/unit/test_document_pipeline.py`) to verify end-to-end indexing and cascade deletion.
