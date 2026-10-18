from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database.connection import get_db
from backend.models import domain as models
from backend.schemas import domain as schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).all()

@router.post("/", response_model=schemas.ProjectResponse)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.patch("/{project_id}", response_model=schemas.ProjectResponse)
def update_project(project_id: int, project_update: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
        
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Simple archive for now
    project.status = "archived"
    db.commit()
    return {"message": "Project archived successfully"}

@router.get("/{project_id}/metrics")
def get_project_metrics(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    doc_count = db.query(models.Document).filter(models.Document.project_id == project_id).count()
    proc_doc_count = db.query(models.Document).filter(models.Document.project_id == project_id, models.Document.status == "READY").count()
    chunk_count = db.query(models.DocumentChunk).filter(models.DocumentChunk.project_id == project_id).count()
    entity_count = db.query(models.ArchitectureEntity).filter(models.ArchitectureEntity.project_id == project_id).count()
    port_count = db.query(models.ArchitectureEntity).filter(models.ArchitectureEntity.project_id == project_id, models.ArchitectureEntity.entity_type == "Port").count()
    signal_count = db.query(models.ArchitectureEntity).filter(models.ArchitectureEntity.project_id == project_id, models.ArchitectureEntity.entity_type == "Signal").count()
    rel_count = db.query(models.ArchitectureRelationship).filter(models.ArchitectureRelationship.project_id == project_id).count()
    finding_count = db.query(models.Finding).filter(models.Finding.project_id == project_id).count()
    
    return {
        "total_documents": doc_count,
        "processed_documents": proc_doc_count,
        "total_chunks": chunk_count,
        "total_entities": entity_count,
        "total_ports": port_count,
        "total_signals": signal_count,
        "total_relationships": rel_count,
        "open_findings": finding_count
    }
