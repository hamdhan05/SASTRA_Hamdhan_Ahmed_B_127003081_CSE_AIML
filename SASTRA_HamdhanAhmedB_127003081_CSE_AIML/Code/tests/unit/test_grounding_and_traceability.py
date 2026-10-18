import pytest
from backend.services.grounding_service import (
    segment_answer_into_claims,
    verify_claims_against_evidence,
    compute_grounding_score
)

def test_claim_segmentation():
    answer = """
    PowertrainManager_SWC regulates internal combustion engine operations.
    It calls Runnable_MonitorTemp periodically over SensorReceiver_IF.
    BatteryManagement_SWC handles state of charge estimation.
    """
    claims = segment_answer_into_claims(answer)
    assert len(claims) == 3
    assert any("PowertrainManager_SWC" in c for c in claims)
    assert any("Runnable_MonitorTemp" in c for c in claims)

def test_evidence_verification_grounded_vs_unverified():
    claims = [
        "PowertrainManager_SWC regulates engine torque.",
        "Quantum propulsion system hyperdrive is activated at 100km/h."
    ]
    citations = [
        {
            "document_id": 1,
            "document_name": "Powertrain_Spec.pdf",
            "page_start": 2,
            "page_end": 2,
            "version_label": "1.0",
            "content": "The PowertrainManager_SWC component regulates engine torque and throttle actuation."
        }
    ]

    verified = verify_claims_against_evidence(claims, citations)
    assert len(verified) == 2
    
    # Claim 1 matches evidence
    assert verified[0]["status"] == "Grounded"
    assert 1 in verified[0]["supporting_citation_ids"]

    # Claim 2 has no evidence
    assert verified[1]["status"] == "Unverified"
    assert verified[1]["supporting_citation_ids"] == []

def test_grounding_score_and_confidence_classification():
    # 1. Mixed claims (1 grounded, 1 unverified -> 50%)
    claims_mixed = [{"status": "Grounded"}, {"status": "Unverified"}]
    metrics_mixed = compute_grounding_score(claims_mixed, citations_count=1)
    assert metrics_mixed["grounding_score"] == 50.0
    assert metrics_mixed["confidence_level"] == "MEDIUM"
    assert metrics_mixed["review_recommendation"] == "ENGINEERING REVIEW REQUIRED"

    # 2. Perfect claims (2 grounded -> 100%)
    claims_perf = [{"status": "Grounded"}, {"status": "Grounded"}]
    metrics_perf = compute_grounding_score(claims_perf, citations_count=2)
    assert metrics_perf["grounding_score"] == 100.0
    assert metrics_perf["confidence_level"] == "HIGH"
    assert metrics_perf["review_recommendation"] == "STANDARD REVIEW"

    # 3. Empty claims -> N/A
    metrics_empty = compute_grounding_score([], citations_count=0)
    assert metrics_empty["grounding_score"] is None
    assert metrics_empty["grounding_score_display"] == "N/A"

def test_abstention_claim_handling():
    answer = "The available documents do not provide sufficient evidence to answer this question."
    claims = segment_answer_into_claims(answer)
    verified = verify_claims_against_evidence(claims, [])
    assert len(verified) == 1
    assert verified[0]["status"] == "Grounded"
