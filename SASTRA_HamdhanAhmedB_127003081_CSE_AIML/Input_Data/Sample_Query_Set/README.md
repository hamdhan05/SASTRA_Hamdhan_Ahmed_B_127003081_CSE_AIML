# Standardized Query Benchmark Dataset (`Input_Data/Sample_Query_Set/`)

This directory contains the standardized 35-query benchmark dataset used to evaluate the retrieval accuracy, citation precision, and hallucination abstention capabilities of **AUTOSAR AI**.

---

## 1. Dataset Files

| File | Format | Queries | Description |
| :--- | :---: | :---: | :--- |
| [`benchmark_dataset_35.json`](benchmark_dataset_35.json) | JSON | 35 | Structured benchmark dataset containing query strings, category tags (`technical` vs `adversarial`), expected entity targets, and ground-truth validation criteria. |
| [`sample_queries_35.csv`](sample_queries_35.csv) | CSV | 35 | Tabular representation of the benchmark queries suitable for spreadsheet inspection, automated batch runs, and reporting. |

---

## 2. Query Distribution

1. **25 Automotive Technical Queries (In-Scope):**
   - Targets specific Software Components (`PowertrainManager`, `SensorManager`, `DiagnosticManager`), Runnables, Ports (`pp_MotorTorque`, `rp_VehicleSpeed`), and carried Signals.
   - Evaluates: Dense semantic retrieval, sparse BM25 token matching, and RRF ranking fusion.
2. **10 Adversarial & Out-of-Scope Queries (Negative Tests):**
   - Targets unanswerable questions, out-of-scope automotive queries (e.g., flight control systems), and general world-knowledge distractors.
   - Evaluates: Grounded prompt compliance and 100% honest abstention (the system must explicitly state that the documents do not provide evidence rather than hallucinating an answer).
