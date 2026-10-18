import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database.connection import SessionLocal
from backend.models import domain as models

client = TestClient(app)

def test_rename_detection_and_data_type_diff():
    db = SessionLocal()
    try:
        # Create project
        proj = models.Project(name="Rename Test Project")
        db.add(proj)
        db.commit()
        db.refresh(proj)

        # Baseline doc v1
        doc1 = models.Document(
            project_id=proj.id,
            original_filename="spec_v1.pdf",
            storage_path="data/uploads/spec_v1.pdf",
            sha256_hash="hash_v1",
            version_label="1.0",
            status="READY"
        )
        # Comparison doc v2
        doc2 = models.Document(
            project_id=proj.id,
            original_filename="spec_v2.pdf",
            storage_path="data/uploads/spec_v2.pdf",
            sha256_hash="hash_v2",
            version_label="2.0",
            status="READY"
        )
        db.add_all([doc1, doc2])
        db.commit()
        db.refresh(doc1)
        db.refresh(doc2)

        # In baseline: EngineCtrl_SWC with Signal_Speed: float32
        ent1 = models.ArchitectureEntity(
            project_id=proj.id,
            document_id=doc1.id,
            entity_type="Software Component",
            name="EngineCtrl_SWC",
            source_excerpt="Controls engine ignition and speed."
        )
        ent_sig1 = models.ArchitectureEntity(
            project_id=proj.id,
            document_id=doc1.id,
            entity_type="Signal",
            name="Signal_Speed",
            signal_data_type="float32",
            source_excerpt="Signal_Speed: float32"
        )

        # In comparison: Renamed to EngineController_SWC, and Signal_Speed changed to float64
        ent2 = models.ArchitectureEntity(
            project_id=proj.id,
            document_id=doc2.id,
            entity_type="Software Component",
            name="EngineController_SWC",
            source_excerpt="Controls engine ignition and speed."
        )
        ent_sig2 = models.ArchitectureEntity(
            project_id=proj.id,
            document_id=doc2.id,
            entity_type="Signal",
            name="Signal_Speed",
            signal_data_type="float64",
            source_excerpt="Signal_Speed: float64"
        )
        db.add_all([ent1, ent_sig1, ent2, ent_sig2])
        db.commit()

        # Run comparison via API
        resp = client.post(
            f"/api/v1/projects/{proj.id}/comparisons",
            json={
                "baseline_document_id": doc1.id,
                "comparison_document_id": doc2.id
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        import json
        res_detail = json.loads(data["results_json"])

        # 1. Verify rename detection
        renamed = res_detail.get("renamed", [])
        assert len(renamed) >= 1
        assert renamed[0]["old_name"] == "EngineCtrl_SWC"
        assert renamed[0]["new_name"] == "EngineController_SWC"

        # 2. Verify signal data-type diff detection (float32 -> float64)
        modified = res_detail.get("modified", [])
        assert any(m["name"] == "Signal_Speed" for m in modified)
        sig_mod = next(m for m in modified if m["name"] == "Signal_Speed")
        assert sig_mod["baseline_data_type"] == "float32"
        assert sig_mod["comparison_data_type"] == "float64"

    finally:
        db.close()
