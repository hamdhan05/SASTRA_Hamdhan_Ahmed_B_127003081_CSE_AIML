import re
from typing import List, Dict, Any, Optional

def segment_answer_into_claims(answer: str) -> List[str]:
    """
    Decomposes an engineering answer into individual verifiable claims.
    Preserves original answer semantics and ignores structural formatting.
    """
    if not answer or not answer.strip():
        return []

    # Detect if answer is an explicit abstention
    abstention_patterns = [
        r'do(?:es)? not provide sufficient evidence',
        r'insufficient evidence',
        r'not mentioned in the (?:provided|available) documents',
        r'no relevant document passages were retrieved'
    ]
    for pat in abstention_patterns:
        if re.search(pat, answer, re.IGNORECASE):
            return [answer.strip()]

    # Normalize newlines
    lines = [l.strip() for l in answer.split('\n') if l.strip()]
    raw_sentences = []
    
    for line in lines:
        # Strip markdown bullets or numbers at start of line
        cleaned = re.sub(r'^(?:[-*•]|\d+\.)\s*', '', line)
        if not cleaned:
            continue
        # Split by periods, exclamation, or semicolons that end sentences
        parts = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', cleaned)
        for p in parts:
            p_str = p.strip()
            # Ignore markdown headers or very short fragments
            if len(p_str) > 15 and not p_str.startswith("#"):
                raw_sentences.append(p_str)

    return raw_sentences if raw_sentences else [answer.strip()]

def verify_claims_against_evidence(
    claims: List[str],
    citations: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Independently validates each claim against the retrieved evidence chunks.
    Assigns: Grounded, Unverified, or Needs Review.
    """
    results = []
    
    # Pre-extract terms from citations
    citation_pool = []
    for idx, c in enumerate(citations):
        c_text = (c.get("content") or "").lower()
        c_doc = c.get("document_name") or f"Doc #{c.get('document_id')}"
        c_page = f"Page {c.get('page_start', 1)}-{c.get('page_end', 1)}"
        c_ver = c.get("version_label", "1.0")
        citation_pool.append({
            "citation_id": idx + 1,
            "document_name": c_doc,
            "page": c_page,
            "version": c_ver,
            "text": c_text,
            "raw": c.get("content", "")
        })

    for c_idx, claim_text in enumerate(claims):
        claim_lower = claim_text.lower()
        
        # Check if abstention statement
        if any(w in claim_lower for w in ["insufficient evidence", "not provide sufficient evidence", "not mentioned in"]):
            results.append({
                "claim_id": c_idx + 1,
                "claim_text": claim_text,
                "status": "Grounded",
                "verification_reason": "Appropriate abstention statement aligned with lack of evidence.",
                "supporting_citation_ids": [],
                "supporting_excerpts": [],
                "document_name": "N/A",
                "page": "N/A",
                "version": "N/A"
            })
            continue

        # Extract technical identifiers (SWCs, ports, signals, capitalized words)
        tech_terms = re.findall(r'\b[A-Z][A-Za-z0-9_]{3,}\b|\b[a-z0-9_]+_[a-z0-9_]+\b|\b\d+\s*(?:ms|kb|mb|hz|v)\b', claim_text)
        
        matched_citations = []
        best_match_excerpt = ""
        best_doc = ""
        best_page = ""
        best_ver = ""

        for cit in citation_pool:
            c_text = cit["text"]
            # Count how many key technical terms appear in this citation chunk
            matches = [t for t in tech_terms if t.lower() in c_text]
            
            # If at least one specific technical term or high phrase overlap
            if (tech_terms and len(matches) >= max(1, len(tech_terms) // 2)) or (any(len(term) > 6 and term.lower() in c_text for term in tech_terms)):
                matched_citations.append(cit["citation_id"])
                if not best_match_excerpt:
                    best_match_excerpt = cit["raw"][:200]
                    best_doc = cit["document_name"]
                    best_page = cit["page"]
                    best_ver = cit["version"]

        if matched_citations:
            status = "Grounded"
            reason = f"Verified against retrieved evidence from {best_doc} ({best_page})."
        else:
            status = "Unverified"
            reason = "No matching architectural entity or assertion found in retrieved document excerpts."

        results.append({
            "claim_id": c_idx + 1,
            "claim_text": claim_text,
            "status": status,
            "verification_reason": reason,
            "supporting_citation_ids": matched_citations,
            "supporting_excerpts": [best_match_excerpt] if best_match_excerpt else [],
            "document_name": best_doc or "Unknown",
            "page": best_page or "Unknown",
            "version": best_ver or "Unknown"
        })

    return results

def compute_grounding_score(
    verified_claims: List[Dict[str, Any]],
    citations_count: int
) -> Dict[str, Any]:
    """
    Computes Grounding Score, Confidence Level, and Review Recommendation.
    Score = (verified grounded claims / total eligible claims) * 100
    """
    if not verified_claims:
        return {
            "grounding_score": None,
            "grounding_score_display": "N/A",
            "confidence_level": "LOW",
            "review_recommendation": "ENGINEERING REVIEW REQUIRED",
            "grounded_count": 0,
            "total_claims": 0
        }

    total_claims = len(verified_claims)
    grounded_count = sum(1 for c in verified_claims if c["status"] == "Grounded")
    
    score = round((grounded_count / total_claims) * 100.0, 1)

    # Classify confidence and review recommendation
    if score >= 80.0 and citations_count > 0:
        confidence = "HIGH"
        review = "STANDARD REVIEW"
    elif score >= 50.0:
        confidence = "MEDIUM"
        review = "ENGINEERING REVIEW REQUIRED"
    else:
        confidence = "LOW"
        review = "ENGINEERING REVIEW REQUIRED"

    return {
        "grounding_score": score,
        "grounding_score_display": f"{score}%",
        "confidence_level": confidence,
        "review_recommendation": review,
        "grounded_count": grounded_count,
        "total_claims": total_claims
    }
