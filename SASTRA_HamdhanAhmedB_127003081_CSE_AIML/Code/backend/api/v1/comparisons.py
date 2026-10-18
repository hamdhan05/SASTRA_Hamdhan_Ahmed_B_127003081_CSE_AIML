import json
from difflib import SequenceMatcher
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel

from backend.database.connection import get_db
from backend.models import domain as models
from backend.services.graph_service import analyze_dependency_impact

class ComparisonCreate(BaseModel):
    baseline_document_id: int
    comparison_document_id: int

router = APIRouter()

@router.get("/projects/{project_id}/comparisons")
def get_project_comparisons(project_id: int, db: Session = Depends(get_db)):
    comps = db.query(models.DocumentComparison).filter(
        models.DocumentComparison.project_id == project_id
    ).order_by(models.DocumentComparison.created_at.desc()).all()
    
    doc_cache = {}
    enriched = []
    for c in comps:
        for d_id in [c.baseline_document_id, c.comparison_document_id]:
            if d_id not in doc_cache:
                doc = db.query(models.Document).filter(models.Document.id == d_id).first()
                doc_cache[d_id] = (doc.original_filename if doc else f"Doc #{d_id}", doc.version_label if doc else "1.0")
                
        try:
            results = json.loads(c.results_json or "{}")
        except Exception:
            results = {"added": [], "removed": [], "modified": [], "renamed": []}
            
        base_name, base_ver = doc_cache.get(c.baseline_document_id, ("", "1.0"))
        comp_name, comp_ver = doc_cache.get(c.comparison_document_id, ("", "1.0"))

        enriched.append({
            "id": c.id,
            "project_id": c.project_id,
            "baseline_document_id": c.baseline_document_id,
            "baseline_document_name": base_name,
            "baseline_version": base_ver,
            "comparison_document_id": c.comparison_document_id,
            "comparison_document_name": comp_name,
            "comparison_version": comp_ver,
            "status": c.status,
            "added_count": len(results.get("added", [])),
            "removed_count": len(results.get("removed", [])),
            "modified_count": len(results.get("modified", [])),
            "renamed_count": len(results.get("renamed", [])),
            "created_at": str(c.created_at),
            "results_json": c.results_json
        })
    return enriched

@router.post("/projects/{project_id}/comparisons")
def create_comparison(project_id: int, comp: ComparisonCreate, db: Session = Depends(get_db)):
    if comp.baseline_document_id == comp.comparison_document_id:
        raise HTTPException(status_code=400, detail="Baseline and comparison documents must be different.")
        
    doc_base = db.query(models.Document).filter(models.Document.id == comp.baseline_document_id, models.Document.project_id == project_id).first()
    doc_comp = db.query(models.Document).filter(models.Document.id == comp.comparison_document_id, models.Document.project_id == project_id).first()
    
    if not doc_base or not doc_comp:
        raise HTTPException(status_code=404, detail="One or both selected documents not found in project.")

    base_entities = db.query(models.ArchitectureEntity).filter(models.ArchitectureEntity.document_id == comp.baseline_document_id).all()
    comp_entities = db.query(models.ArchitectureEntity).filter(models.ArchitectureEntity.document_id == comp.comparison_document_id).all()

    base_map = {(e.entity_type, e.name): e for e in base_entities}
    comp_map = {(e.entity_type, e.name): e for e in comp_entities}

    added = []
    removed = []
    modified = []
    renamed = []

    # Unmatched candidates for rename detection
    unmatched_base = {}
    unmatched_comp = {}

    for key, ent in comp_map.items():
        if key not in base_map:
            unmatched_comp[key] = ent
        else:
            base_ent = base_map[key]
            # Check for changes in excerpt, data type, direction, or interface
            dt_changed = (ent.signal_data_type or "") != (base_ent.signal_data_type or "")
            dir_changed = (ent.port_direction or "") != (base_ent.port_direction or "")
            if_changed = (ent.interface_name or "") != (base_ent.interface_name or "")
            excerpt_changed = (ent.source_excerpt or "") != (base_ent.source_excerpt or "")

            if dt_changed or dir_changed or if_changed or excerpt_changed:
                mod_desc = []
                if dt_changed:
                    mod_desc.append(f"Signal Data Type changed: '{base_ent.signal_data_type}' -> '{ent.signal_data_type}'")
                if dir_changed:
                    mod_desc.append(f"Port Direction changed: '{base_ent.port_direction}' -> '{ent.port_direction}'")
                if if_changed:
                    mod_desc.append(f"Interface changed: '{base_ent.interface_name}' -> '{ent.interface_name}'")
                if excerpt_changed and not (dt_changed or dir_changed or if_changed):
                    mod_desc.append("Specification excerpt/content updated")

                modified.append({
                    "type": ent.entity_type,
                    "name": ent.name,
                    "change_summary": "; ".join(mod_desc),
                    "baseline_data_type": base_ent.signal_data_type,
                    "comparison_data_type": ent.signal_data_type,
                    "baseline_direction": base_ent.port_direction,
                    "comparison_direction": ent.port_direction,
                    "baseline_interface": base_ent.interface_name,
                    "comparison_interface": ent.interface_name,
                    "baseline_excerpt": base_ent.source_excerpt or "",
                    "comparison_excerpt": ent.source_excerpt or "",
                    "baseline_page": base_ent.source_page or 1,
                    "comparison_page": ent.source_page or 1
                })

    for key, ent in base_map.items():
        if key not in comp_map:
            unmatched_base[key] = ent

    # Deterministic Rename Detection between unmatched entities of the same type
    matched_renames_base = set()
    matched_renames_comp = set()

    for (c_type, c_name), c_ent in unmatched_comp.items():
        for (b_type, b_name), b_ent in unmatched_base.items():
            if b_name in matched_renames_base:
                continue
            if c_type == b_type:
                b_exc = (b_ent.source_excerpt or "").strip()
                c_exc = (c_ent.source_excerpt or "").strip()
                excerpt_sim = SequenceMatcher(None, c_exc[:100], b_exc[:100]).ratio() if (b_exc and c_exc) else 0.0
                name_sim = SequenceMatcher(None, c_name.lower(), b_name.lower()).ratio()
                
                # Check stems without standard architectural suffixes (_SWC, _IF, etc.)
                import re
                stem_c = re.sub(r'_(?:SWC|IF|Port|Runnable)$', '', c_name, flags=re.IGNORECASE).lower()
                stem_b = re.sub(r'_(?:SWC|IF|Port|Runnable)$', '', b_name, flags=re.IGNORECASE).lower()
                stem_sim = SequenceMatcher(None, stem_c, stem_b).ratio()
                
                # Deterministic threshold: strong name similarity, or high excerpt similarity with partial stem match
                is_rename = (name_sim >= 0.88) or (excerpt_sim >= 0.85 and stem_sim >= 0.65)
                if is_rename:
                    renamed.append({
                        "type": c_type,
                        "old_name": b_name,
                        "new_name": c_name,
                        "matching_basis": f"Deterministic similarity score {round(max(name_sim, excerpt_sim) * 100)}%",
                        "baseline_page": b_ent.source_page or 1,
                        "comparison_page": c_ent.source_page or 1
                    })
                    matched_renames_base.add(b_name)
                    matched_renames_comp.add(c_name)
                    break

    # Add remaining unmatched to added / removed
    for (c_type, c_name), c_ent in unmatched_comp.items():
        if c_name not in matched_renames_comp:
            added.append({
                "type": c_ent.entity_type,
                "name": c_ent.name,
                "description": c_ent.description or "",
                "source_page": c_ent.source_page or 1,
                "source_excerpt": c_ent.source_excerpt or ""
            })

    for (b_type, b_name), b_ent in unmatched_base.items():
        if b_name not in matched_renames_base:
            removed.append({
                "type": b_ent.entity_type,
                "name": b_ent.name,
                "description": b_ent.description or "",
                "source_page": b_ent.source_page or 1,
                "source_excerpt": b_ent.source_excerpt or ""
            })

    # Integrated Change Impact Traversal
    impacted_components = {}
    for item in modified + renamed + removed:
        cname = item.get("name") or item.get("old_name")
        if cname and item.get("type") == "Software Component":
            impact = analyze_dependency_impact(db, project_id, cname)
            if impact.get("total_impacted_count", 0) > 0:
                impacted_components[cname] = impact

    results_data = {
        "baseline_filename": doc_base.original_filename,
        "baseline_version": doc_base.version_label or "1.0",
        "comparison_filename": doc_comp.original_filename,
        "comparison_version": doc_comp.version_label or "2.0",
        "added": added,
        "removed": removed,
        "modified": modified,
        "renamed": renamed,
        "impact_analysis": impacted_components
    }

    db_comp = models.DocumentComparison(
        project_id=project_id,
        baseline_document_id=comp.baseline_document_id,
        comparison_document_id=comp.comparison_document_id,
        status="completed",
        results_json=json.dumps(results_data),
        created_by=None
    )
    db.add(db_comp)
    db.commit()
    db.refresh(db_comp)
    return db_comp

@router.get("/comparisons/{comparison_id}")
def get_comparison(comparison_id: int, db: Session = Depends(get_db)):
    comp = db.query(models.DocumentComparison).filter(models.DocumentComparison.id == comparison_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Comparison not found")
    return comp
