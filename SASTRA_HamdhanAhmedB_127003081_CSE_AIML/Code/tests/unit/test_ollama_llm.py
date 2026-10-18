import pytest
from backend.services.llm_service import get_active_provider_info, test_llm_connection as run_llm_diag, ask_question
from backend.core.config import settings

def test_active_provider_info():
    info = get_active_provider_info()
    assert info["provider"] == "ollama"
    assert "llama3.2:3b" in info["model"]
    assert info["is_local"] is True
    assert "11434" in info["base_url"]

def test_ollama_connection_diagnostic():
    diag = run_llm_diag()
    assert diag["provider"] == "ollama"
    # Verify reachable and status is PASS
    assert diag["status"] == "PASS"
    assert diag["reachable"] is True
    assert diag["model_exists"] is True
    assert diag["test_generation_ok"] is True
    assert diag["latency_ms"] > 0

def test_ask_question_insufficient_evidence():
    # If no evidence is provided, the grounded system instructions should answer appropriately
    response = ask_question(
        query="What is the baud rate of the CAN bus?",
        context="[No relevant document passages were retrieved for this query.]"
    )
    assert isinstance(response, str)
    assert len(response) > 0
    # Must not crash and should indicate lack of evidence or context-based answer
