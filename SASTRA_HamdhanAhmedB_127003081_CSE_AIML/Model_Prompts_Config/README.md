# Model Prompts & Configuration (`Model_Prompts_Config/`)

This directory contains the formal technical configurations, prompt templates, embedding parameter definitions, and environment templates governing the generative AI and retrieval subsystems of **AUTOSAR AI**.

---

## 1. Directory Overview & Deliverables

| File | Type | Purpose & Scope |
| :--- | :---: | :--- |
| [`RAG_System_Prompt.md`](RAG_System_Prompt.md) | Markdown | Production system prompt extracted verbatim from `backend/services/llm_service.py`. Enforces strict automotive domain rules: factual citations, page number provenance, and honest abstention on missing evidence. |
| [`Model_Configuration.md`](Model_Configuration.md) | Markdown | Technical specifications for the local Ollama LLM provider (`llama3.2:3b`), quantization format (`Q4_K_M`), context window limits (128k context), temperature (0.1), and zero-leakage offline guarantee. |
| [`Embedding_Configuration.md`](Embedding_Configuration.md) | Markdown | Detailed documentation of SentenceTransformers (`all-MiniLM-L6-v2`), vector dimensionality (384-d), cosine distance metric, ChromaDB collection parameters, and HNSW indexing thresholds. |
| [`Retrieval_Configuration.md`](Retrieval_Configuration.md) | Markdown | Algorithmic configuration of the two-stage hybrid retrieval engine: Dense vector similarity threshold ($0.35$), Sparse BM25 tokenization, and Reciprocal Rank Fusion ($k=60$). |
| [`.env.example`](.env.example) | Environment Template | Sanitized production environment template documenting all runtime flags with zero exposed secrets. |

---

## 2. Live Code Correspondence

| Configuration Document | Live Implementation Source | Functional Role in Pipeline |
| :--- | :--- | :--- |
| [`RAG_System_Prompt.md`](RAG_System_Prompt.md) | `backend/services/llm_service.py` | Sets system instructions for Ollama: enforces evidence-based answering and exact citation format `[Page X]`. |
| [`Model_Configuration.md`](Model_Configuration.md) | `backend/core/config.py` & `backend/services/llm_service.py` | Configures model parameters: `OLLAMA_MODEL="llama3.2:3b"`, `OLLAMA_BASE_URL="http://127.0.0.1:11434"`. |
| [`Embedding_Configuration.md`](Embedding_Configuration.md) | `backend/services/vector_store_service.py` | Configures `SentenceTransformer("all-MiniLM-L6-v2")` and persistent ChromaDB storage in `data/vector_store/`. |
| [`Retrieval_Configuration.md`](Retrieval_Configuration.md) | `backend/services/retrieval_service.py` | Fuses Top-5 dense ChromaDB results with sparse BM25 scores via Reciprocal Rank Fusion. |
| [`.env.example`](.env.example) | `backend/core/config.py` | Loaded via Pydantic `BaseSettings` on startup to parameterize ports, paths, and timeouts. |

---

## 3. Hardware Requirements & Performance Metrics

- **LLM RAM Footprint:** ~2.2 GB (runs smoothly on any modern laptop or workstation with 8GB+ RAM).
- **GPU Acceleration:** Optional. Leverages CPU AVX2 instructions or CUDA if an NVIDIA GPU is present.
- **Inference Latency:**
  - Dense Embedding Generation: $15 - 25\text{ ms}$ per chunk.
  - Hybrid RRF Retrieval: $< 10\text{ ms}$ for 500 chunks.
  - Ollama `llama3.2:3b` Generation: $1.2 - 2.8\text{ s}$ per query.
  - Grounding Claim Decomposition: $40 - 70\text{ ms}$.
- **Data Privacy Guarantee:** Zero external API calls during operation. 100% of PDF processing, embeddings, vector queries, and LLM inferences execute strictly on-premises on `localhost`.
