import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database.connection import SessionLocal
from backend.models import domain as models

client = TestClient(app)

def test_document_governance_and_versioning():
    db = SessionLocal()
    try:
        # 1. Create a test project
        proj = models.Project(name="Governance Test Project")
        db.add(proj)
        db.commit()
        db.refresh(proj)

        # 2. Test document creation with version_label and governance_state
        doc = models.Document(
            project_id=proj.id,
            original_filename="Powertrain_Spec_v2.0.pdf",
            storage_path="data/uploads/dummy_v2.pdf",
            sha256_hash="hash_gov_test_123",
            version_label="2.0",
            governance_state="DRAFT",
            status="UPLOADED"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        assert doc.version_label == "2.0"
        assert doc.governance_state == "DRAFT"

        # 3. Test governance state update via PATCH endpoint
        resp = client.patch(
            f"/api/v1/documents/{doc.id}/governance",
            json={"governance_state": "APPROVED", "version_label": "2.1"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["governance_state"] == "APPROVED"
        assert data["version_label"] == "2.1"

        # 4. Test invalid governance state rejection
        bad_resp = client.patch(
            f"/api/v1/documents/{doc.id}/governance",
            json={"governance_state": "INVALID_STATE"}
        )
        assert bad_resp.status_code == 400

        # 5. Test chunk version propagation
        db.refresh(doc)
        chunk = models.DocumentChunk(
            project_id=proj.id,
            document_id=doc.id,
            chunk_index=0,
            version_label=doc.version_label,
            section_heading="1.0 System Architecture",
            text_content="Powertrain controller specification details.",
            content_hash="chunk_hash_1"
        )
        db.add(chunk)
        db.commit()
        db.refresh(chunk)

        assert chunk.version_label == "2.1"
        assert chunk.section_heading == "1.0 System Architecture"

    finally:
        db.close()
