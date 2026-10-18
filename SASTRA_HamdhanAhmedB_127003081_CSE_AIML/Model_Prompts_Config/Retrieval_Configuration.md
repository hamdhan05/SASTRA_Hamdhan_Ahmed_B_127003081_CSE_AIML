# Retrieval Configuration & Hybrid Fusion Pipeline

## 1. Overview
AUTOSAR AI implements a two-stage retrieval pipeline combining **Dense Semantic Vector Search** and **Sparse BM25 Keyword Search** using **Reciprocal Rank Fusion (RRF)**.

## 2. Dense Semantic Vector Search
- **Query Vectorization**: User queries are transformed into 384-dimensional dense vectors using `all-MiniLM-L6-v2`.
- **Top-K Selection**: Default retrieval retrieves the Top 5 most semantically proximate chunks based on cosine distance.
- **Collection Partitioning**: ChromaDB partitions collections by project (`project_{project_id}`) to ensure strict multi-project data isolation.

## 3. Sparse BM25 Keyword Search
- **Rationale**: Dense semantic search excels at conceptual matching but frequently struggles with exact automotive identifiers (e.g., `CanIf_Transmit`, `RPort_VehicleSpeed`, `ASIL_D`).
- **Tokenizer**: Alphanumeric regex tokenizer: `re.findall(r'\b[a-zA-Z0-9_]+\b', text.lower())`.
- **BM25 Parameters**:
  - $k_1 = 1.5$ (Term frequency saturation factor)
  - $b = 0.75$ (Document length normalization factor)
  - Inverted index built over candidate document chunks.

## 4. Reciprocal Rank Fusion (RRF)
To merge rankings from Dense and BM25 retrievers without score calibration mismatch, AUTOSAR AI implements Reciprocal Rank Fusion:

$$RRF\_Score(d) = \sum_{m \in \{	ext{Dense}, 	ext{BM25}\}} rac{1}{k + 	ext{Rank}_m(d)}$$

Where:
- $k = 60$ (Standard RRF smoothing constant)
- $	ext{Rank}_m(d)$ is the 1-based ordinal rank of chunk $d$ in retrieval method $m$.
- Final Top-$K$ chunks are sorted by descending $RRF\_Score$.

## 5. Metadata Filtering
The retrieval engine natively supports metadata filtering:
- Document Filter: `where={"document_id": document_id}`
- Version Filter: `where={"version_label": version_label}`
