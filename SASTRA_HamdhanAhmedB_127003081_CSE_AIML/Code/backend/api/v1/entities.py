from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from backend.database.connection import get_db
from backend.models import domain as models
from backend.services.graph_service import build_mermaid_topology, analyze_dependency_impact

class EntityUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    review_status: Optional[str] = None

class EntityReview(BaseModel):
    status: str # "confirmed", "rejected", "pending"

router = APIRouter()

@router.get("/projects/{project_id}/entities")
def get_entities(project_id: int, version_label: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.ArchitectureEntity).filter(models.ArchitectureEntity.project_id == project_id)
    if version_label and version_label not in ("All", "All Versions"):
        # Match via document version
        doc_ids = [d.id for d in db.query(models.Document.id).filter(
            models.Document.project_id == project_id,
            models.Document.version_label == version_label
        ).all()]
        query = query.filter(models.ArchitectureEntity.document_id.in_(doc_ids))
    return query.all()

@router.get("/entities/{entity_id}")
def get_entity(entity_id: int, db: Session = Depends(get_db)):
    entity = db.query(models.ArchitectureEntity).filter(models.ArchitectureEntity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity

@router.patch("/entities/{entity_id}")
def update_entity(entity_id: int, entity_update: EntityUpdate, db: Session = Depends(get_db)):
    entity = db.query(models.ArchitectureEntity).filter(models.ArchitectureEntity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
        
    update_data = entity_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(entity, key, value)
        
    db.commit()
    db.refresh(entity)
    return entity

@router.post("/entities/{entity_id}/review")
def review_entity(entity_id: int, review: EntityReview, db: Session = Depends(get_db)):
    entity = db.query(models.ArchitectureEntity).filter(models.ArchitectureEntity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
        
    entity.review_status = review.status
    db.commit()
    db.refresh(entity)
    return entity

@router.get("/projects/{project_id}/relationships")
def get_relationships(project_id: int, db: Session = Depends(get_db)):
    rels = db.query(models.ArchitectureRelationship).filter(models.ArchitectureRelationship.project_id == project_id).all()
    # Enrich with entity names
    entities = {e.id: e.name for e in db.query(models.ArchitectureEntity).filter(models.ArchitectureEntity.project_id == project_id).all()}
    enriched = []
    for r in rels:
        enriched.append({
            "id": r.id,
            "source_id": r.source_entity_id,
            "source_name": entities.get(r.source_entity_id, f"Entity #{r.source_entity_id}"),
            "target_id": r.target_entity_id,
            "target_name": entities.get(r.target_entity_id, f"Entity #{r.target_entity_id}"),
            "relationship_type": r.relationship_type,
            "source_page": r.source_page,
            "source_excerpt": r.source_excerpt,
            "review_status": r.review_status
        })
    return enriched

@router.get("/projects/{project_id}/ports_and_signals")
def get_ports_and_signals(
    project_id: int, 
    version_label: Optional[str] = None,
    component: Optional[str] = None,
    direction: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Returns dedicated list of extracted Ports and Signals with complete AUTOSAR metadata."""
    query = db.query(models.ArchitectureEntity).filter(
        models.ArchitectureEntity.project_id == project_id,
        models.ArchitectureEntity.entity_type.in_(["Port", "Signal"])
    )
    
    if component and component != "All":
        query = query.filter(models.ArchitectureEntity.owner_component == component)
    if direction and direction != "All":
        query = query.filter(models.ArchitectureEntity.port_direction == direction)

    entities = query.all()
    doc_map = {d.id: (d.original_filename, d.version_label) for d in db.query(models.Document).filter(models.Document.project_id == project_id).all()}

    results = []
    for e in entities:
        doc_name, ver = doc_map.get(e.document_id, ("Unknown", "1.0"))
        if version_label and version_label not in ("All", "All Versions") and ver != version_label:
            continue
        results.append({
            "id": e.id,
            "type": e.entity_type,
            "name": e.name,
            "component": e.owner_component or "Unassigned",
            "direction": e.port_direction or "N/A",
            "interface": e.interface_name or "N/A",
            "carried_signals": e.carried_signals or "N/A",
            "signal_data_type": e.signal_data_type or "N/A",
            "version": ver or "1.0",
            "source_page": e.source_page or 1,
            "source_document": doc_name,
            "review_status": e.review_status,
            "confidence": e.confidence
        })
    return results

@router.get("/projects/{project_id}/topology")
def get_architecture_topology(project_id: int, version_label: Optional[str] = None, db: Session = Depends(get_db)):
    """Generates Mermaid topology graph definition and directed edges table."""
    ent_query = db.query(models.ArchitectureEntity).filter(models.ArchitectureEntity.project_id == project_id)
    if version_label and version_label not in ("All", "All Versions"):
        doc_ids = [d.id for d in db.query(models.Document.id).filter(
            models.Document.project_id == project_id,
            models.Document.version_label == version_label
        ).all()]
        ent_query = ent_query.filter(models.ArchitectureEntity.document_id.in_(doc_ids))
    entities = ent_query.all()

    rel_query = db.query(models.ArchitectureRelationship).filter(models.ArchitectureRelationship.project_id == project_id)
    relationships = rel_query.all()

    mermaid_code = build_mermaid_topology(entities, relationships)

    ent_map = {e.id: e.name for e in entities}
    edges = []
    for r in relationships:
        if r.source_entity_id in ent_map and r.target_entity_id in ent_map:
            edges.append({
                "id": r.id,
                "source": ent_map[r.source_entity_id],
                "relationship_type": r.relationship_type,
                "target": ent_map[r.target_entity_id],
                "source_page": r.source_page,
                "review_status": r.review_status
            })

    return {
        "mermaid_code": mermaid_code,
        "edges": edges,
        "entity_count": len(entities),
        "relationship_count": len(edges)
    }

@router.get("/projects/{project_id}/impact")
def get_dependency_impact(project_id: int, root_entity_name: str = Query(...), db: Session = Depends(get_db)):
    """Computes direct and transitive downstream impact of modifying an architectural component."""
    return analyze_dependency_impact(db, project_id, root_entity_name)
