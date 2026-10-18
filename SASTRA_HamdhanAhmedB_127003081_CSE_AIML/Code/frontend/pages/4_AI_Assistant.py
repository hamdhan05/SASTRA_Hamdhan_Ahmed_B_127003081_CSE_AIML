import streamlit as st
import os
import sys
import json
import time
from datetime import datetime
import requests

# Ensure backend imports can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from frontend.utils.ui import inject_custom_css, render_header

st.set_page_config(page_title="AI Assistant - AUTOSAR AI", page_icon="🤖", layout="wide")
inject_custom_css()

render_header("AI Assistant", "Grounded automotive engineering document intelligence & claim-level traceability")

project_id = 1
api_base = "http://127.0.0.1:8000/api/v1"

# Fetch project documents for scoping
docs = []
try:
    d_res = requests.get(f"{api_base}/projects/{project_id}/documents")
    if d_res.status_code == 200:
        docs = d_res.json()
except Exception:
    pass

doc_options = {d["original_filename"]: d["id"] for d in docs if d["status"] == "READY"}
all_versions = sorted(list({d.get("version_label") or "1.0" for d in docs}))
version_options = ["All Versions"] + all_versions

if "messages" not in st.session_state:
    st.session_state.messages = []

# Top Configuration & Engine Banner
with st.container(border=True):
    col_b1, col_b2 = st.columns([1.5, 1])
    with col_b1:
        st.markdown("""
        <div style='background-color: #EFF6FF; border: 1px solid #DBEAFE; border-radius: 8px; padding: 10px 14px;'>
            <span style='color: #1D4ED8; font-weight: 600; font-size: 0.92rem;'>🤖 Active Engine: Ollama llama3.2:3b</span>
            <span style='color: #4B5563; font-size: 0.85rem; margin-left: 12px;'>• Local Offline Inference • Zero Data Leakage</span>
        </div>
        """, unsafe_allow_html=True)
    with col_b2:
        st.caption("Active Retrieval Pipeline")
        st.markdown("<span style='font-size: 0.85rem; color: #1E40AF; font-weight: 500;'>ChromaDB Dense Semantic Index + BM25 Lexical + RRF</span>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    c_ctrl1, c_ctrl2, c_ctrl3, c_ctrl4 = st.columns([2, 1.5, 1.5, 1])
    with c_ctrl1:
        selected_doc_name = st.selectbox(
            "Document Scope",
            ["All Project Documents"] + list(doc_options.keys()),
            help="Filter retrieval to a specific uploaded specification"
        )
    with c_ctrl2:
        selected_version = st.selectbox(
            "Specification Version",
            version_options,
            help="Filter retrieval by specification version"
        )
    with c_ctrl3:
        retrieval_strategy_raw = st.selectbox(
            "Retrieval Strategy",
            ["Dense Semantic", "Hybrid (Dense + BM25 + RRF)"],
            help="Dense vector search alone vs. Reciprocal Rank Fusion hybrid retrieval"
        )
        selected_strategy = "hybrid" if "Hybrid" in retrieval_strategy_raw else "dense"
    with c_ctrl4:
        selected_top_k = st.slider("Top-K Evidence", min_value=1, max_value=10, value=5, help="Number of evidence chunks to retrieve")

selected_doc_ids = []
if selected_doc_name != "All Project Documents" and selected_doc_name in doc_options:
    selected_doc_ids = [doc_options[selected_doc_name]]

effective_version = None if selected_version == "All Versions" else selected_version

col_chat, col_sidebar = st.columns([3, 1])

def generate_markdown_report(msg_data: dict) -> str:
    """Generates an engineering review markdown document from the query and response."""
    md = []
    md.append(f"# AUTOSAR AI — Engineering Design Query Report")
    md.append(f"**Generated At:** {msg_data.get('timestamp', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))}")
    md.append(f"**Message ID:** {msg_data.get('message_id', 'N/A')} | **Session ID:** {msg_data.get('session_id', 'N/A')}")
    md.append(f"**Grounding Score:** {msg_data.get('grounding_score', 'N/A')}% | **Confidence:** {msg_data.get('confidence_level', 'N/A')}")
    md.append(f"**Review Recommendation:** {msg_data.get('review_recommendation', 'N/A')}")
    md.append(f"\n---\n")
    md.append(f"## 1. Technical Query\n> {msg_data.get('query_text', '')}\n")
    md.append(f"## 2. Assistant Response\n{msg_data.get('content', '')}\n")
    
    claims = msg_data.get("claims", [])
    if claims:
        md.append(f"## 3. Claim-Level Traceability Analysis\n")
        md.append("| Claim ID | Claim Text | Status | Evidence Source | Verification Reason |")
        md.append("|:---:|:---|:---:|:---|:---|")
        for cl in claims:
            src = f"{cl.get('document_name', 'N/A')} ({cl.get('page', 'N/A')})"
            md.append(f"| {cl.get('claim_id')} | {cl.get('claim_text', '').replace('|', '-')} | `{cl.get('status')}` | {src} | {cl.get('verification_reason', '')} |")
        md.append("\n")

    citations = msg_data.get("citations", [])
    if citations:
        md.append(f"## 4. Stored Document Evidence Records\n")
        for idx, cit in enumerate(citations):
            md.append(f"### Evidence #{idx + 1}: {cit.get('document_name')} ({cit.get('page_start')}-{cit.get('page_end')})")
            if cit.get('section_heading'):
                md.append(f"**Section:** {cit['section_heading']}")
            md.append(f"```text\n{cit.get('content', '')}\n```\n")

    if msg_data.get("review_decision"):
        md.append(f"## 5. Engineering Sign-Off & Review Record\n")
        md.append(f"- **Decision:** `{msg_data.get('review_decision')}`")
        md.append(f"- **Reviewer:** {msg_data.get('reviewer_id')}")
        md.append(f"- **Feedback:** {msg_data.get('review_feedback', 'None')}")
        md.append(f"- **Corrected Facts:** {msg_data.get('corrected_facts', 'None')}")
        md.append(f"- **Review Timestamp:** {msg_data.get('reviewed_at', 'N/A')}\n")

    return "\n".join(md)

def generate_json_report(msg_data: dict) -> str:
    """Generates structured JSON representation of the query and response."""
    export_payload = {
        "metadata": {
            "platform": "AUTOSAR AI Engineering Intelligence Platform",
            "message_id": msg_data.get("message_id"),
            "session_id": msg_data.get("session_id"),
            "timestamp": msg_data.get("timestamp", datetime.utcnow().isoformat()),
            "engine": "Ollama llama3.2:3b",
            "retrieval_strategy": msg_data.get("strategy", "dense"),
            "top_k": msg_data.get("top_k", 5)
        },
        "query": msg_data.get("query_text", ""),
        "response": msg_data.get("content", ""),
        "evaluation_metrics": {
            "grounding_score": msg_data.get("grounding_score"),
            "confidence_level": msg_data.get("confidence_level"),
            "review_recommendation": msg_data.get("review_recommendation")
        },
        "claims_traceability": msg_data.get("claims", []),
        "evidence_citations": msg_data.get("citations", []),
        "latencies": msg_data.get("latencies", {}),
        "engineering_sign_off": {
            "review_decision": msg_data.get("review_decision"),
            "reviewer_id": msg_data.get("reviewer_id"),
            "feedback": msg_data.get("review_feedback"),
            "corrected_facts": msg_data.get("corrected_facts"),
            "reviewed_at": msg_data.get("reviewed_at")
        }
    }
    return json.dumps(export_payload, indent=2)

with col_chat:
    if not st.session_state.messages:
        st.markdown("""
        <div style='text-align: center; padding: 40px 20px; color: #6B7280;'>
            <div style='font-size: 2.5rem; margin-bottom: 10px;'>💬</div>
            <h4 style='color: #111827; margin-bottom: 6px;'>Engineering Assistant Ready</h4>
            <p style='font-size: 0.95rem;'>Ask about software components, runnables, ports, signals, or architectural safety compliance.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for m_idx, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(message["content"])
            else:
                with st.chat_message("assistant"):
                    # Metric cards row
                    grounding_val = message.get("grounding_score")
                    grounding_disp = f"{grounding_val}%" if grounding_val is not None else "N/A"
                    conf_level = message.get("confidence_level", "STANDARD")
                    rev_rec = message.get("review_recommendation", "STANDARD REVIEW")
                    cit_count = len(message.get("citations", []))

                    m1, m2, m3, m4 = st.columns(4)
                    with m1:
                        conf_color = "#16A34A" if conf_level == "HIGH" else ("#D97706" if conf_level == "MEDIUM" else "#DC2626")
                        st.markdown(f"<div style='background:#F8FAFC; border:1px solid #E5E7EB; border-radius:6px; padding:8px 12px; text-align:center;'><span style='font-size:0.75rem; color:#6B7280; font-weight:600;'>CONFIDENCE</span><br><b style='color:{conf_color}; font-size:1.05rem;'>{conf_level}</b></div>", unsafe_allow_html=True)
                    with m2:
                        rev_color = "#2563EB" if rev_rec == "STANDARD REVIEW" else "#D97706"
                        st.markdown(f"<div style='background:#F8FAFC; border:1px solid #E5E7EB; border-radius:6px; padding:8px 12px; text-align:center;'><span style='font-size:0.75rem; color:#6B7280; font-weight:600;'>ENGINEER REVIEW</span><br><b style='color:{rev_color}; font-size:0.92rem;'>{rev_rec}</b></div>", unsafe_allow_html=True)
                    with m3:
                        g_color = "#16A34A" if (grounding_val and grounding_val >= 80) else "#D97706"
                        st.markdown(f"<div style='background:#F8FAFC; border:1px solid #E5E7EB; border-radius:6px; padding:8px 12px; text-align:center;'><span style='font-size:0.75rem; color:#6B7280; font-weight:600;'>GROUNDING SCORE</span><br><b style='color:{g_color}; font-size:1.05rem;'>{grounding_disp}</b></div>", unsafe_allow_html=True)
                    with m4:
                        st.markdown(f"<div style='background:#F8FAFC; border:1px solid #E5E7EB; border-radius:6px; padding:8px 12px; text-align:center;'><span style='font-size:0.75rem; color:#6B7280; font-weight:600;'>EVIDENCE RECORDS</span><br><b style='color:#111827; font-size:1.05rem;'>{cit_count} Chunks</b></div>", unsafe_allow_html=True)

                    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                    st.markdown(message["content"])

                    # 1. Claim-Level Traceability Expander
                    claims = message.get("claims", [])
                    if claims:
                        with st.expander(f"🔍 Claim-Level Traceability ({len(claims)} Claims Analyzed)", expanded=False):
                            for cl in claims:
                                is_grounded = cl.get("status") == "Grounded"
                                badge_color = "#16A34A" if is_grounded else "#D97706"
                                st.markdown(f"""
                                <div style='border-left: 3px solid {badge_color}; padding-left: 10px; margin-bottom: 10px;'>
                                    <b>Claim {cl.get('claim_id')}:</b> {cl.get('claim_text')}<br>
                                    <span style='background:{badge_color}22; color:{badge_color}; padding:2px 6px; border-radius:4px; font-weight:600; font-size:0.75rem;'>{cl.get('status')}</span>
                                    <span style='color:#6B7280; font-size:0.85rem; margin-left:8px;'>{cl.get('verification_reason')}</span>
                                </div>
                                """, unsafe_allow_html=True)
                                if cl.get("supporting_excerpts") and cl["supporting_excerpts"][0]:
                                    st.caption(f"> \"{cl['supporting_excerpts'][0][:200]}...\"")

                    # 2. Source Citations Expander
                    citations = message.get("citations", [])
                    if citations:
                        with st.expander(f"📚 Stored Evidence Citations ({len(citations)})", expanded=False):
                            for c in citations:
                                doc_title = c.get('document_name') or f"Doc #{c.get('document_id')}"
                                p_start = c.get('page_start', 1)
                                p_end = c.get('page_end', 1)
                                v_lbl = c.get('version_label', '1.0')
                                sec = f" • Section: {c['section_heading']}" if c.get('section_heading') else ""
                                st.markdown(f"**{doc_title}** — *Page {p_start} to {p_end} (v{v_lbl})*{sec}")
                                if c.get("content"):
                                    st.caption(f"> \"{c['content'][:250]}...\"")

                    # 3. Inline Download Reports (Markdown & JSON)
                    btn_col1, btn_col2, btn_col3 = st.columns([1.2, 1.2, 2.6])
                    with btn_col1:
                        md_content = generate_markdown_report(message)
                        st.download_button(
                            label="📥 Download Markdown Report",
                            data=md_content,
                            file_name=f"report_message_{message.get('message_id', m_idx)}.md",
                            mime="text/markdown",
                            key=f"dl_md_{m_idx}",
                            use_container_width=True
                        )
                    with btn_col2:
                        json_content = generate_json_report(message)
                        st.download_button(
                            label="📥 Download JSON Report",
                            data=json_content,
                            file_name=f"report_message_{message.get('message_id', m_idx)}.json",
                            mime="application/json",
                            key=f"dl_json_{m_idx}",
                            use_container_width=True
                        )

                    # 4. Engineer Review & Sign-Off Card
                    with st.expander("✍️ Engineer Review & Sign-Off", expanded=bool(message.get("review_decision"))):
                        if message.get("review_decision"):
                            st.success(f"✅ Signed off by **{message.get('reviewer_id')}** as **{message.get('review_decision')}** on {message.get('reviewed_at', 'N/A')}")
                            if message.get("review_feedback"):
                                st.info(f"Feedback: {message['review_feedback']}")
                            if message.get("corrected_facts"):
                                st.warning(f"Corrected Facts: {message['corrected_facts']}")
                        else:
                            st.caption("Perform formal human-in-the-loop engineering validation for this AI-generated answer:")
                            r_col1, r_col2 = st.columns(2)
                            with r_col1:
                                rev_decision = st.selectbox(
                                    "Review Decision",
                                    ["Accepted", "Rejected", "Needs Modification"],
                                    key=f"dec_{m_idx}"
                                )
                            with r_col2:
                                rev_id = st.text_input("Engineer / Reviewer ID", value="ENG-01", key=f"revid_{m_idx}")
                            
                            rev_feedback = st.text_area("Engineering Feedback", placeholder="Detailed feedback or comments...", key=f"fb_{m_idx}")
                            rev_corrections = st.text_area("Corrected Architecture Facts (if modified)", placeholder="Specific architectural correction...", key=f"corr_{m_idx}")
                            
                            if st.button("Submit Formal Review", key=f"btn_rev_{m_idx}", use_container_width=True):
                                if not rev_id.strip():
                                    st.error("Reviewer ID is required.")
                                else:
                                    s_id = message.get("session_id", 1)
                                    m_id = message.get("message_id")
                                    if m_id:
                                        try:
                                            rev_res = requests.post(
                                                f"{api_base}/sessions/{s_id}/messages/{m_id}/review",
                                                json={
                                                    "decision": rev_decision,
                                                    "reviewer_id": rev_id.strip(),
                                                    "feedback": rev_feedback.strip(),
                                                    "corrected_facts": rev_corrections.strip()
                                                }
                                            )
                                            if rev_res.status_code == 200:
                                                message["review_decision"] = rev_decision
                                                message["reviewer_id"] = rev_id.strip()
                                                message["review_feedback"] = rev_feedback.strip()
                                                message["corrected_facts"] = rev_corrections.strip()
                                                message["reviewed_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                                                st.success("Review persisted successfully to database and audit logs!")
                                                st.rerun()
                                            else:
                                                st.error(f"Review submission failed: {rev_res.text}")
                                        except Exception as e:
                                            st.error(f"Error submitting review: {str(e)}")

    def handle_query(query_text: str):
        st.session_state.messages.append({
            "role": "user",
            "content": query_text
        })
        
        with st.chat_message("assistant"):
            with st.spinner("Analyzing document evidence via Ollama (llama3.2:3b)..."):
                try:
                    payload = {
                        "query": query_text,
                        "document_ids": selected_doc_ids,
                        "version_label": effective_version,
                        "strategy": selected_strategy,
                        "top_k": selected_top_k
                    }
                    res = requests.post(f"{api_base}/projects/{project_id}/ask", json=payload, timeout=125)
                    if res.status_code == 200:
                        data = res.json()
                        answer = data.get("answer", "No answer returned.")
                        citations = data.get("citations", [])
                        claims = data.get("claims", [])
                        grounding_score = data.get("grounding_score")
                        confidence_level = data.get("confidence_level", "LOW")
                        review_recommendation = data.get("review_recommendation", "ENGINEERING REVIEW REQUIRED")
                        message_id = data.get("message_id")
                        session_id = data.get("session_id")
                        latencies = data.get("latencies", {})
                    else:
                        answer = f"Ollama / API Error ({res.status_code}): {res.text}"
                        citations = []
                        claims = []
                        grounding_score = None
                        confidence_level = "LOW"
                        review_recommendation = "ENGINEERING REVIEW REQUIRED"
                        message_id = None
                        session_id = None
                        latencies = {}
                except requests.exceptions.Timeout:
                    answer = "Ollama model generation timed out. The local model is busy or processing large contexts."
                    citations = []
                    claims = []
                    grounding_score = None
                    confidence_level = "LOW"
                    review_recommendation = "ENGINEERING REVIEW REQUIRED"
                    message_id = None
                    session_id = None
                    latencies = {}
                except Exception as e:
                    answer = f"Failed to communicate with backend: {str(e)}"
                    citations = []
                    claims = []
                    grounding_score = None
                    confidence_level = "LOW"
                    review_recommendation = "ENGINEERING REVIEW REQUIRED"
                    message_id = None
                    session_id = None
                    latencies = {}
                    
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "citations": citations,
            "claims": claims,
            "grounding_score": grounding_score,
            "confidence_level": confidence_level,
            "review_recommendation": review_recommendation,
            "message_id": message_id,
            "session_id": session_id,
            "strategy": selected_strategy,
            "top_k": selected_top_k,
            "latencies": latencies,
            "query_text": query_text,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        })
        st.rerun()

    # Chat prompt input
    if prompt := st.chat_input("Ask about software components, ports, interfaces, or design decisions..."):
        handle_query(prompt)

with col_sidebar:
    with st.container(border=True):
        st.subheader("Suggested Questions")
        st.caption("Click any prompt below to query your uploaded specifications:")
        
        suggested = [
            "Summarize the AUTOSAR architecture.",
            "List all extracted Software Components.",
            "Which interfaces, ports, and runnables are defined?",
            "What signals and data types are transmitted?",
            "Are there any circular dependencies detected?",
            "Explain any insecure IPC communication patterns."
        ]
        for idx, sq in enumerate(suggested):
            if st.button(sq, key=f"sq_{idx}", use_container_width=True):
                handle_query(sq)
                
        st.markdown("---")
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
