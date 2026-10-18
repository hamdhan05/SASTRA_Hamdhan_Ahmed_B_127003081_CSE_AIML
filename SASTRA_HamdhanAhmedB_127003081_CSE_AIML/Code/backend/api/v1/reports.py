import os
import csv
import json
import time
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models import domain as models
from backend.core.config import settings
from backend.services.graph_service import analyze_dependency_impact
from backend.services.report_generator import (
    generate_markdown_report,
    generate_pdf_report,
    validate_pdf_file
)
from pydantic import BaseModel

def sanitize_csv_cell(val: Any) -> str:
    """Protects against spreadsheet formula injection vulnerabilities."""
    if val is None:
        return ""
    text = str(val).strip()
    if text and text[0] in ('=', '+', '-', '@', '\t', '\r'):
        return "'" + text
    return text

class ReportCreate(BaseModel):
    report_type: str
    format: str
    component_name: Optional[str] = None
    version_label: Optional[str] = None

router = APIRouter()

@router.get("/projects/{project_id}/reports")
def get_reports(project_id: int, db: Session = Depends(get_db)):
    reports = db.query(models.Report).filter(
        models.Report.project_id == project_id
    ).order_by(models.Report.created_at.desc()).all()
    
    # Enrich response with on-disk validation status
    results = []
    for r in reports:
        is_valid = True
        exists = os.path.exists(r.storage_path) if r.storage_path else False
        if exists and (r.format or "").upper() == "PDF":
            is_valid = validate_pdf_file(r.storage_path)
            
        results.append({
            "id": r.id,
            "project_id": r.project_id,
            "report_type": r.report_type,
            "format": r.format,
            "storage_path": r.storage_path,
            "created_at": str(r.created_at),
            "file_exists": exists,
            "is_valid": is_valid
        })
    return results

@router.post("/projects/{project_id}/reports")
def create_report(project_id: int, report_req: ReportCreate, db: Session = Depends(get_db)):
    os.makedirs(settings.EXPORT_DIR, exist_ok=True)
    
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    raw_fmt = report_req.format.lower().strip()
    if raw_fmt in ("md", "markdown"):
        ext = "md"
        fmt_label = "MD"
    elif raw_fmt == "pdf":
        ext = "pdf"
        fmt_label = "PDF"
    elif raw_fmt == "json":
        ext = "json"
        fmt_label = "JSON"
    elif raw_fmt == "csv":
        ext = "csv"
        fmt_label = "CSV"
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported report format: {report_req.format}. Supported: CSV, JSON, PDF, MD")

    ts = int(time.time())
    safe_type = report_req.report_type.replace(" ", "_").lower()
    comp_slug = f"_{report_req.component_name}" if report_req.component_name else ""
    filename = f"report_proj{project_id}_{safe_type}{comp_slug}_{ts}.{ext}"
    filepath = os.path.join(settings.EXPORT_DIR, filename)

    if report_req.report_type == "Component Specification Report":
        c_name = report_req.component_name or ""
        comp_ent = db.query(models.ArchitectureEntity).filter(
            models.ArchitectureEntity.project_id == project_id,
            models.ArchitectureEntity.entity_type == "Software Component",
            models.ArchitectureEntity.name == c_name
        ).first()

        ports = db.query(models.ArchitectureEntity).filter(
            models.ArchitectureEntity.project_id == project_id,
            models.ArchitectureEntity.entity_type == "Port",
            models.ArchitectureEntity.owner_component == c_name
        ).all()

        findings = db.query(models.Finding).filter(
            models.Finding.project_id == project_id
        ).all()
        related_findings = [f for f in findings if c_name in (f.description or "") or c_name in (f.evidence_json or "")]

        impact = analyze_dependency_impact(db, project_id, c_name) if comp_ent else {}

        comp_data = {
            "project_id": project_id,
            "report_type": "Component Specification Report",
            "component_name": c_name,
            "version_label": report_req.version_label or "Unspecified",
            "summary": comp_ent.description if comp_ent else "No description available.",
            "source_page": comp_ent.source_page if comp_ent else None,
            "ports": [{
                "name": p.name,
                "kind": p.port_kind,
                "direction": p.port_direction,
                "interface": p.interface_name,
                "carried_signals": p.carried_signals
            } for p in ports],
            "related_findings": [{
                "id": f.id,
                "type": f.finding_type,
                "severity": f.severity,
                "description": f.description,
                "status": f.review_status
            } for f in related_findings],
            "downstream_impact": impact
        }

        if ext == "json":
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(comp_data, f, indent=2)
        elif ext == "csv":
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Component", "Port Name", "Kind", "Direction", "Interface", "Signals", "Impacted Dependents Count"])
                if ports:
                    for p in ports:
                        writer.writerow([
                            sanitize_csv_cell(c_name),
                            sanitize_csv_cell(p.name),
                            sanitize_csv_cell(p.port_kind),
                            sanitize_csv_cell(p.port_direction),
                            sanitize_csv_cell(p.interface_name),
                            sanitize_csv_cell(p.carried_signals),
                            impact.get("total_impacted_count", 0)
                        ])
                else:
                    writer.writerow([sanitize_csv_cell(c_name), "None", "N/A", "N/A", "N/A", "N/A", impact.get("total_impacted_count", 0)])
        elif ext == "md":
            md_text = generate_markdown_report("Component Specification Report", project_id, project.name, comp_data)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md_text)
        elif ext == "pdf":
            generate_pdf_report("Component Specification Report", project_id, project.name, comp_data, filepath)

    elif report_req.report_type == "Architecture Summary":
        entities = db.query(models.ArchitectureEntity).filter(models.ArchitectureEntity.project_id == project_id).all()
        ent_data = [{
            "id": e.id,
            "type": e.entity_type,
            "name": e.name,
            "review_status": e.review_status,
            "source_page": e.source_page,
            "description": e.description,
            "source_excerpt": e.source_excerpt
        } for e in entities]
        report_data = {"project_id": project_id, "entities": ent_data}

        if ext == "json":
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2)
        elif ext == "csv":
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Entity Type", "Name", "Review Status", "Source Page", "Description", "Excerpt"])
                for e in entities:
                    writer.writerow([
                        e.id,
                        sanitize_csv_cell(e.entity_type),
                        sanitize_csv_cell(e.name),
                        sanitize_csv_cell(e.review_status),
                        e.source_page or "",
                        sanitize_csv_cell(e.description),
                        sanitize_csv_cell(e.source_excerpt)
                    ])
        elif ext == "md":
            md_text = generate_markdown_report("Architecture Summary", project_id, project.name, report_data)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md_text)
        elif ext == "pdf":
            generate_pdf_report("Architecture Summary", project_id, project.name, report_data, filepath)

    elif report_req.report_type == "Findings Report":
        findings = db.query(models.Finding).filter(models.Finding.project_id == project_id).all()
        f_data = [{
            "id": fnd.id,
            "type": fnd.finding_type,
            "severity": fnd.severity,
            "status": fnd.review_status,
            "description": fnd.description,
            "comments": fnd.reviewer_comments
        } for fnd in findings]
        report_data = {"project_id": project_id, "findings": f_data}

        if ext == "json":
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2)
        elif ext == "csv":
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Finding Type", "Severity", "Status", "Description", "Comments"])
                for fnd in findings:
                    writer.writerow([
                        fnd.id,
                        sanitize_csv_cell(fnd.finding_type),
                        sanitize_csv_cell(fnd.severity),
                        sanitize_csv_cell(fnd.review_status),
                        sanitize_csv_cell(fnd.description),
                        sanitize_csv_cell(fnd.reviewer_comments)
                    ])
        elif ext == "md":
            md_text = generate_markdown_report("Findings Report", project_id, project.name, report_data)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md_text)
        elif ext == "pdf":
            generate_pdf_report("Findings Report", project_id, project.name, report_data, filepath)

    else: # Dependency Matrix
        rels = db.query(models.ArchitectureRelationship).filter(models.ArchitectureRelationship.project_id == project_id).all()
        r_data = [{
            "id": r.id,
            "source": r.source_entity_id,
            "type": r.relationship_type,
            "target": r.target_entity_id,
            "status": r.review_status
        } for r in rels]
        report_data = {"project_id": project_id, "relationships": r_data}

        if ext == "json":
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2)
        elif ext == "csv":
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Relationship Type", "Status"])
                for r in rels:
                    writer.writerow([r.id, sanitize_csv_cell(r.relationship_type), sanitize_csv_cell(r.review_status)])
        elif ext == "md":
            md_text = generate_markdown_report("Dependency Matrix", project_id, project.name, report_data)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md_text)
        elif ext == "pdf":
            generate_pdf_report("Dependency Matrix", project_id, project.name, report_data, filepath)

    # Double check PDF validity if format is PDF
    if ext == "pdf" and not validate_pdf_file(filepath):
        if os.path.exists(filepath):
            os.remove(filepath)
        raise HTTPException(status_code=500, detail="Generated PDF document failed validation.")

    db_report = models.Report(
        project_id=project_id,
        report_type=report_req.report_type,
        format=fmt_label,
        storage_path=filepath,
        generated_by=None
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

@router.get("/reports/{report_id}/download")
def download_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    if not report.storage_path or not os.path.exists(report.storage_path):
        raise HTTPException(status_code=404, detail="Report file not found on disk")

    filename = os.path.basename(report.storage_path)
    fmt = (report.format or "").upper()

    # Determine accurate media type
    if fmt == "PDF" or filename.endswith(".pdf"):
        if not validate_pdf_file(report.storage_path):
            raise HTTPException(
                status_code=422,
                detail="Report PDF on disk is corrupted. Please regenerate this report."
            )
        media_type = "application/pdf"
    elif fmt in ("MD", "MARKDOWN") or filename.endswith(".md"):
        media_type = "text/markdown; charset=utf-8"
    elif fmt == "JSON" or filename.endswith(".json"):
        media_type = "application/json"
    elif fmt == "CSV" or filename.endswith(".csv"):
        media_type = "text/csv"
    else:
        media_type = "application/octet-stream"
        
    return FileResponse(
        path=report.storage_path,
        filename=filename,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.post("/reports/{report_id}/regenerate")
def regenerate_report(report_id: int, db: Session = Depends(get_db)):
    """Regenerates a report file if the previous file was missing or corrupted."""
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Delegate to create_report logic with same parameters
    req = ReportCreate(
        report_type=report.report_type,
        format=report.format.lower()
    )
    new_report = create_report(report.project_id, req, db)
    return new_report
