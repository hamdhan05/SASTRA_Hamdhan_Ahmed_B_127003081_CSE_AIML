# Embedding Configuration & Vector Space Parameters

## 1. Embedding Model Specifications
- **Model Name**: `all-MiniLM-L6-v2`
- **Framework**: `sentence-transformers` / Hugging Face
- **Embedding Dimensions**: **384 dimensions**
- **Distance Metric**: **Cosine Similarity** ($1 - 	ext{cosine\_distance}$)
- **Max Sequence Length**: 256 word pieces
- **Memory Footprint**: ~90 MB (highly efficient for local embedded and desktop inference)

## 2. Ingestion & Vector Storage Pipeline
1. **Source Document Text**: PyMuPDF extracts plain text page by page from the HLD PDF.
2. **Chunking Engine**: Document text is split into chunks of **1000 characters** with an overlap of **150 characters**.
3. **Metadata Association**: Each chunk is tagged with `document_id`, `chunk_index`, `page_start`, `page_end`, and `version_label`.
4. **Vector Generation**: SentenceTransformers generates a 384-dimensional dense float vector for each chunk.
5. **ChromaDB Indexing**: Chunks and vectors are stored in persistent disk storage at `./data/vector_store` under project-specific collections (`project_{id}`).

## 3. Vector Database Engine
- **Engine**: ChromaDB 0.4.24
- **Persistence Mechanism**: Persistent local disk storage (`chromadb.PersistentClient(path="./data/vector_store")`)
- **Metadata Indexing**: SQLite backing store (`chroma.sqlite3`) coupled with HNSW vector index files (`data_level0.bin`, `link_lists.bin`).
