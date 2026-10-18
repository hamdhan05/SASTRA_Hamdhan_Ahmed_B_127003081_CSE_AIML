import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database.connection import SessionLocal
from backend.models import domain as models

client = TestClient(app)

def test_query_review_submission_and_audit_log():
    db = SessionLocal()
    try:
        # Create project and analysis session
        proj = models.Project(name="Review Audit Test Project")
        db.add(proj)
        db.commit()
        db.refresh(proj)

        session = models.AnalysisSession(project_id=proj.id, title="Test Session")
        db.add(session)
        db.commit()
        db.refresh(session)

        # User question & Assistant answer
        msg_user = models.AnalysisMessage(session_id=session.id, role="user", content="How is RTE secured?")
        msg_assist = models.AnalysisMessage(session_id=session.id, role="assistant", content="RTE uses memory partitioning.")
        db.add_all([msg_user, msg_assist])
        db.commit()
        db.refresh(msg_assist)

        # 1. Submit review via API
        rev_payload = {
            "decision": "Accepted",
            "reviewer_id": "ENG-42",
            "feedback": "Fully verified against specification.",
            "corrected_facts": ""
        }
        resp = client.post(
            f"/api/v1/sessions/{session.id}/messages/{msg_assist.id}/review",
            json=rev_payload
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["review_decision"] == "Accepted"
        assert data["reviewer_id"] == "ENG-42"

        # 2. Check persistence in analysis_messages
        db.expire_all()
        refreshed_msg = db.query(models.AnalysisMessage).filter(models.AnalysisMessage.id == msg_assist.id).first()
        assert refreshed_msg.review_decision == "Accepted"
        assert refreshed_msg.reviewer_id == "ENG-42"
        assert refreshed_msg.reviewed_at is not None

        # 3. Check audit log entry creation
        audit_entry = db.query(models.AuditLog).filter(
            models.AuditLog.resource_type == "analysis_message",
            models.AuditLog.resource_id == msg_assist.id
        ).first()
        assert audit_entry is not None
        assert audit_entry.action == "ENGINEERING_REVIEW_SUBMITTED"

        # 4. Fetch reviews list for audit history UI
        hist_resp = client.get(f"/api/v1/projects/{proj.id}/reviews")
        assert hist_resp.status_code == 200
        reviews = hist_resp.json()
        assert len(reviews) == 1
        assert reviews[0]["reviewer_id"] == "ENG-42"
        assert reviews[0]["question"] == "How is RTE secured?"

    finally:
        db.close()
