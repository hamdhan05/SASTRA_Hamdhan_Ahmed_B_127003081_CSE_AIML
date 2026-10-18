import os
import chromadb
from backend.core.config import settings

# Initialize ChromaDB client
os.makedirs(settings.VECTOR_STORE_DIR, exist_ok=True)
chroma_client = chromadb.PersistentClient(path=settings.VECTOR_STORE_DIR)

def get_collection(project_id: int):
    collection_name = f"project_{project_id}"
    return chroma_client.get_or_create_collection(name=collection_name)

def add_chunks(project_id: int, document_id: int, chunks: list[dict]):
    collection = get_collection(project_id)
    
    ids = []
    documents = []
    metadatas = []
    
    for chunk in chunks:
        ids.append(f"{document_id}_{chunk['chunk_index']}")
        documents.append(chunk['text_content'])
        metadatas.append({
            "document_id": document_id,
            "chunk_index": chunk['chunk_index'],
            "page_start": chunk.get('page_start', 0),
            "page_end": chunk.get('page_end', 0),
            "version_label": chunk.get('version_label', '1.0'),
            "section_heading": chunk.get('section_heading', '')
        })
        
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

def delete_chunks_by_document(project_id: int, document_id: int):
    try:
        collection = get_collection(project_id)
        collection.delete(where={"document_id": document_id})
    except Exception:
        pass

def search_chunks(project_id: int, query: str, top_k: int = 5, document_ids: list[int] = None, version_label: str = None):
    try:
        collection = get_collection(project_id)
        filters = []
        if document_ids and len(document_ids) == 1:
            filters.append({"document_id": document_ids[0]})
        elif document_ids and len(document_ids) > 1:
            filters.append({"document_id": {"$in": document_ids}})
            
        if version_label and version_label.strip() and version_label not in ("All", "All Versions"):
            filters.append({"version_label": version_label.strip()})

        where_filter = None
        if len(filters) == 1:
            where_filter = filters[0]
        elif len(filters) > 1:
            where_filter = {"$and": filters}
            
        kwargs = {"query_texts": [query], "n_results": top_k}
        if where_filter:
            kwargs["where"] = where_filter
            
        results = collection.query(**kwargs)
        return results
    except Exception as e:
        return {"documents": [[]], "metadatas": [[]], "error": str(e)}
