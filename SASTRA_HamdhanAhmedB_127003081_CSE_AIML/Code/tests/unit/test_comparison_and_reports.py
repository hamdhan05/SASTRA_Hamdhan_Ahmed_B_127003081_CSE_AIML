import json
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database.connection import SessionLocal
from backend.models import domain as models
from backend.api.v1.reports import sanitize_csv_cell

client = TestClient(app)

def test_csv_formula_injection_sanitization():
    # Dangerous formula payloads
    assert sanitize_csv_cell("=1+1") == "'=1+1"
    assert sanitize_csv_cell("+cmd|' /C calc'!A0") == "'+cmd|' /C calc'!A0"
    assert sanitize_csv_cell("-2+3") == "'-2+3"
    assert sanitize_csv_cell("@SUM(1,2)") == "'@SUM(1,2)"
    # Safe text
    assert sanitize_csv_cell("EngineControl_SWC") == "EngineControl_SWC"
    assert sanitize_csv_cell("Normal description") == "Normal description"

def test_document_comparison_and_history():
    db = SessionLocal()
    try:
        # Create project and two distinct documents
        proj = models.Project(name="Comparison Test Project")
        db.add(proj)
        db.commit()
        db.refresh(proj)
        
        doc1 = models.Document(
            project_id=proj.id, original_filename="v1_spec.pdf", storage_path="./dummy1", sha256_hash="h1", status="READY"
        )
        doc2 = models.Document(
            project_id=proj.id, original_filename="v2_spec.pdf", storage_path="./dummy2", sha256_hash="h2", status="READY"
        )
        db.add_all([doc1, doc2])
        db.commit()
        db.refresh(doc1)
        db.refresh(doc2)
        
        # Add distinct entities
        e1 = models.ArchitectureEntity(
            project_id=proj.id, document_id=doc1.id, entity_type="Software Component", name="LegacyController_SWC", review_status="pending"
        )
        e2 = models.ArchitectureEntity(
            project_id=proj.id, document_id=doc2.id, entity_type="Software Component", name="NextGenController_SWC", review_status="pending"
        )
        db.add_all([e1, e2])
        db.commit()
        
        # 1. Reject comparing doc to itself
        same_resp = client.post(f"/api/v1/projects/{proj.id}/comparisons", json={
            "baseline_document_id": doc1.id, "comparison_document_id": doc1.id
        })
        assert same_resp.status_code == 400
        
        # 2. Run valid comparison
        comp_resp = client.post(f"/api/v1/projects/{proj.id}/comparisons", json={
            "baseline_document_id": doc1.id, "comparison_document_id": doc2.id
        })
        assert comp_resp.status_code == 200
        comp_data = comp_resp.json()
        results = json.loads(comp_data["results_json"])
        
        # e2 should be added, e1 should be removed
        added_names = [x["name"] for x in results["added"]]
        removed_names = [x["name"] for x in results["removed"]]
        assert "NextGenController_SWC" in added_names
        assert "LegacyController_SWC" in removed_names
        
        # 3. Retrieve comparison history
        hist_resp = client.get(f"/api/v1/projects/{proj.id}/comparisons")
        assert hist_resp.status_code == 200
        history = hist_resp.json()
        assert len(history) >= 1
        assert history[0]["baseline_document_name"] == "v1_spec.pdf"
        assert history[0]["comparison_document_name"] == "v2_spec.pdf"
        
    finally:
        db.close()

def test_report_generation_and_download():
    db = SessionLocal()
    try:
        proj = models.Project(name="Report Test Project")
        db.add(proj)
        db.commit()
        db.refresh(proj)
        
        # Add finding with potential injection string
        fnd = models.Finding(
            project_id=proj.id,
            document_id=1,
            finding_type="Security Rule",
            severity="High",
            description="=cmd|' /C calc'!A0",
            review_status="open"
        )
        db.add(fnd)
        db.commit()
        
        # 1. Generate CSV report
        csv_resp = client.post(f"/api/v1/projects/{proj.id}/reports", json={
            "report_type": "Findings Report",
            "format": "csv"
        })
        assert csv_resp.status_code == 200
        report_id = csv_resp.json()["id"]
        
        # 2. Download report and check sanitization
        dl_resp = client.get(f"/api/v1/reports/{report_id}/download")
        assert dl_resp.status_code == 200
        content = dl_resp.text
        # Must be escaped with leading apostrophe
        assert "'=cmd|' /C calc'!A0" in content
        
    finally:
        db.close()
