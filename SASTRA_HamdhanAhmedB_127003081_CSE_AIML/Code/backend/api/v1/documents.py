from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import os
import shutil
import hashlib

from backend.database.connection import get_db
from backend.models import domain as models
from backend.schemas import domain as schemas
from backend.core.config import settings
from backend.services.document_service import process_document
from backend.services.vector_store_service import delete_chunks_by_document

router = APIRouter()

class GovernanceUpdateRequest(BaseModel):
    governance_state: str
    version_label: Optional[str] = None

@router.get("/projects/{project_id}/documents", response_model=List[schemas.DocumentResponse])
def get_documents(project_id: int, db: Session = Depends(get_db)):
    return db.query(models.Document).filter(models.Document.project_id == project_id).all()

@router.post("/projects/{project_id}/documents", response_model=schemas.DocumentResponse)
def upload_document(
    project_id: int, 
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...), 
    version_label: str = Form("1.0"),
    governance_state: str = Form("DRAFT"),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    # Check project exists
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    max_bytes = getattr(settings, "MAX_UPLOAD_MB", 50) * 1024 * 1024
    
    # Calculate sha256 while saving and enforce size limit
    sha256_hash = hashlib.sha256()
    file_path = os.path.join(settings.UPLOAD_DIR, f"{project_id}_{file.filename}")
    total_bytes = 0
    
    with open(file_path, "wb") as buffer:
        while chunk := file.file.read(8192):
            total_bytes += len(chunk)
            if total_bytes > max_bytes:
                buffer.close()
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise HTTPException(status_code=413, detail=f"File exceeds maximum upload limit of {settings.MAX_UPLOAD_MB}MB.")
            sha256_hash.update(chunk)
            buffer.write(chunk)
            
    # Check if this exact file was already uploaded to this project
    file_hash = sha256_hash.hexdigest()
    existing_doc = db.query(models.Document).filter(
        models.Document.project_id == project_id,
        models.Document.sha256_hash == file_hash
    ).first()
    
    clean_version = version_label.strip() if version_label and version_label.strip() else "1.0"
    clean_governance = governance_state.strip().upper() if governance_state and governance_state.strip() else "DRAFT"

    if existing_doc:
        os.remove(file_path)
        # Update version / governance if provided
        existing_doc.version_label = clean_version
        existing_doc.governance_state = clean_governance
        db.commit()
        return existing_doc
        
    db_document = models.Document(
        project_id=project_id,
        original_filename=file.filename,
        storage_path=file_path,
        sha256_hash=file_hash,
        version_label=clean_version,
        governance_state=clean_governance,
        status="UPLOADED"
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    # Process in background with a self-managed DB session
    background_tasks.add_task(process_document, db_document.id)
    
    return db_document

@router.patch("/documents/{document_id}/governance", response_model=schemas.DocumentResponse)
def update_document_governance(document_id: int, req: GovernanceUpdateRequest, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    valid_states = ["DRAFT", "IN_REVIEW", "APPROVED", "SUPERSEDED"]
    clean_state = req.governance_state.strip().upper()
    if clean_state not in valid_states:
        raise HTTPException(status_code=400, detail=f"Invalid governance state '{req.governance_state}'. Must be one of: {valid_states}")
    doc.governance_state = clean_state
    if req.version_label:
        doc.version_label = req.version_label.strip()
    db.commit()
    db.refresh(doc)
    return doc

@router.get("/documents/{document_id}", response_model=schemas.DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.get("/documents/{document_id}/status")
def get_document_status(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"id": doc.id, "status": doc.status, "error_message": doc.error_message}

@router.post("/documents/{document_id}/reprocess")
def reprocess_document(document_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    doc.status = "PROCESSING"
    doc.error_message = None
    db.commit()
    
    background_tasks.add_task(process_document, doc.id)
    return {"message": "Document reprocessing started", "id": doc.id, "status": "PROCESSING"}

@router.delete("/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # 1. Delete associated chunks from SQLite
    db.query(models.DocumentChunk).filter(models.DocumentChunk.document_id == document_id).delete()
    
    # 2. Delete associated entities and findings from SQLite
    db.query(models.ArchitectureEntity).filter(models.ArchitectureEntity.document_id == document_id).delete()
    db.query(models.ArchitectureRelationship).filter(models.ArchitectureRelationship.document_id == document_id).delete()
    db.query(models.Finding).filter(models.Finding.document_id == document_id).delete()
    
    # 3. Clean up vector embeddings in ChromaDB
    delete_chunks_by_document(doc.project_id, document_id)
    
    # 4. Delete physical file
    if os.path.exists(doc.storage_path):
        os.remove(doc.storage_path)
        
    db.delete(doc)
    db.commit()
    return {"message": "Document and all associated assets deleted successfully"}
