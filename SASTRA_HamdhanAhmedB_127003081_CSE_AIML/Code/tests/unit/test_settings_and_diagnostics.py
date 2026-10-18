import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database.connection import SessionLocal
from backend.models import domain as models

client = TestClient(app)

def test_settings_validation_and_persistence():
    # 1. Fetch current settings
    resp = client.get("/api/v1/settings")
    assert resp.status_code == 200
    cfg = resp.json()
    assert "chunk_size" in cfg
    assert "chunk_overlap" in cfg
    
    # 2. Reject invalid settings: overlap >= chunk_size
    bad_resp = client.post("/api/v1/settings", json={
        "chunk_size": 500,
        "chunk_overlap": 600,
        "enable_table_extraction": True,
        "ocr_enabled": False,
        "flag_circular_dependencies": True,
        "enforce_secure_ipc": True,
        "require_boundary_definitions": True
    })
    assert bad_resp.status_code == 400
    assert "strictly less" in bad_resp.json()["detail"]
    
    # 3. Save valid settings
    good_resp = client.post("/api/v1/settings", json={
        "chunk_size": 1200,
        "chunk_overlap": 180,
        "enable_table_extraction": True,
        "ocr_enabled": False,
        "flag_circular_dependencies": True,
        "enforce_secure_ipc": True,
        "require_boundary_definitions": True
    })
    assert good_resp.status_code == 200
    assert good_resp.json()["chunk_size"] == 1200
    assert good_resp.json()["chunk_overlap"] == 180

def test_system_diagnostics_endpoint():
    resp = client.get("/api/v1/diagnostics")
    assert resp.status_code == 200
    data = resp.json()
    assert "overall_status" in data
    assert "subsystems" in data
    sub = data["subsystems"]
    
    # Check all key subsystems are audited
    assert "backend_api" in sub
    assert "database" in sub
    assert "vector_store" in sub
    assert "llm_provider" in sub
    assert "pdf_engine" in sub
    
    # Verify local Ollama model llama3.2:3b is verified PASS
    assert sub["llm_provider"]["status"] == "PASS"
    assert "llama3.2:3b" in sub["llm_provider"]["model"]
    assert sub["llm_provider"]["test_generation_ok"] is True

def test_findings_and_entity_review():
    db = SessionLocal()
    try:
        proj = models.Project(name="Review Test Project")
        db.add(proj)
        db.commit()
        db.refresh(proj)
        
        # Test finding review
        fnd = models.Finding(
            project_id=proj.id,
            finding_type="Insecure IPC",
            severity="High",
            description="IPC communication without RTE filter",
            review_status="open"
        )
        db.add(fnd)
        db.commit()
        db.refresh(fnd)
        
        # Patch finding status
        patch_resp = client.patch(f"/api/v1/findings/{fnd.id}", json={
            "review_status": "confirmed",
            "reviewer_comments": "Verified in architecture review"
        })
        assert patch_resp.status_code == 200
        assert patch_resp.json()["review_status"] == "confirmed"
        assert patch_resp.json()["reviewer_comments"] == "Verified in architecture review"
        
        # Test entity review
        ent = models.ArchitectureEntity(
            project_id=proj.id,
            entity_type="Runnable",
            name="Runnable_Throttle",
            review_status="pending"
        )
        db.add(ent)
        db.commit()
        db.refresh(ent)
        
        rev_resp = client.post(f"/api/v1/entities/{ent.id}/review", json={"status": "confirmed"})
        assert rev_resp.status_code == 200
        assert rev_resp.json()["review_status"] == "confirmed"
        
    finally:
        db.close()
