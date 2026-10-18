import streamlit as st
import os
import sys
import requests

# Ensure backend imports can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from frontend.utils.ui import inject_custom_css, render_header

st.set_page_config(page_title="Dashboard - AUTOSAR AI", page_icon="📊", layout="wide")
inject_custom_css()

render_header("Overview", "AUTOSAR High-Level Design Intelligence & System Status")

project_id = 1
api_base = "http://127.0.0.1:8000/api/v1"

# Fetch project metrics
metrics = {
    "total_documents": 0, 
    "processed_documents": 0, 
    "total_chunks": 0,
    "total_entities": 0, 
    "total_ports": 0,
    "total_signals": 0,
    "total_relationships": 0,
    "open_findings": 0
}
try:
    res = requests.get(f"{api_base}/projects/{project_id}/metrics")
    if res.status_code == 200:
        metrics.update(res.json())
except Exception:
    pass

# Row 1: High-level document and architectural metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Processed Specifications", f"{metrics['processed_documents']} / {metrics['total_documents']}")
m2.metric("Indexed Chunks", str(metrics.get("total_chunks", 0)))
m3.metric("Architectural Entities", str(metrics["total_entities"]))
m4.metric("Open Rule Findings", str(metrics["open_findings"]))

# Row 2: Secondary architectural telemetry
st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
sm1, sm2, sm3, sm4 = st.columns(4)
sm1.metric("Extracted Ports", str(metrics.get("total_ports", 0)))
sm2.metric("Extracted Signals", str(metrics.get("total_signals", 0)))
sm3.metric("Dependency Edges", str(metrics.get("total_relationships", 0)))
sm4.metric("Active LLM Engine", "Ollama 3.2:3b")

st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

col_act, col_sys = st.columns([2, 1])

with col_act:
    with st.container(border=True):
        st.subheader("Specification Repository")
        st.caption("Recently ingested AUTOSAR architecture specifications:")
        
        docs = []
        try:
            res = requests.get(f"{api_base}/projects/{project_id}/documents")
            if res.status_code == 200:
                docs = res.json()
        except Exception:
            pass
        
        if docs:
            table_html = """<table style="width: 100%; text-align: left; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #E5E7EB; color: #6B7280; font-size: 0.85rem;">
                    <th style="padding: 10px 0;">Specification Document</th>
                    <th style="padding: 10px 0;">Version</th>
                    <th style="padding: 10px 0;">Governance</th>
                    <th style="padding: 10px 0;">Processing Status</th>
                </tr>"""
            for d in docs[:6]:
                status_class = "badge-success" if d['status'] == 'READY' else ("badge-processing" if d['status'] == 'PROCESSING' else "badge-pending")
                gov_lbl = d.get('governance_state', 'DRAFT')
                gov_color = "#2563EB" if gov_lbl == "APPROVED" else ("#D97706" if gov_lbl == "IN_REVIEW" else "#4B5563")
                ver_val = d.get('version_label', '1.0') or '1.0'
                table_html += f"""
                <tr style="border-bottom: 1px solid #F3F4F6; font-size: 0.92rem;">
                    <td style="padding: 10px 0; color: #111827; font-weight: 500;">📄 {d['original_filename']}</td>
                    <td style="padding: 10px 0; color: #4B5563;"><code>v{ver_val}</code></td>
                    <td style="padding: 10px 0;"><span style='color:{gov_color}; font-weight:600;'>{gov_lbl}</span></td>
                    <td style="padding: 10px 0;"><span class="{status_class}">{d['status']}</span></td>
                </tr>"""
            table_html += "</table>"
            st.markdown(table_html, unsafe_allow_html=True)
        else:
            st.info("No documents uploaded yet. Go to Documents to upload your first AUTOSAR specification.")

with col_sys:
    with st.container(border=True):
        st.subheader("Subsystem Diagnostics")
        st.caption("Live telemetry across offline core services:")
        
        # Load or refresh diagnostics
        diag_data = None
        try:
            d_res = requests.get(f"{api_base}/diagnostics", timeout=10)
            if d_res.status_code == 200:
                diag_data = d_res.json()
        except Exception:
            pass

        if diag_data:
            subsystems = diag_data.get("subsystems", {})
            for key, sub in subsystems.items():
                badge = "badge-success" if sub["status"] == "PASS" else ("badge-error" if sub["status"] == "FAIL" else "badge-pending")
                st.markdown(f"""
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; font-size:0.88rem;'>
                    <span style='color:#374151; font-weight:500;'>{sub.get('service', key)}</span>
                    <span class='{badge}'>{sub['status']}</span>
                </div>
                """, unsafe_allow_html=True)
            
            llm_info = diag_data.get("active_provider_info", {})
            st.caption(f"LLM: **{llm_info.get('provider', 'ollama')}** ({llm_info.get('model', 'llama3.2:3b')}) | **Local Offline**")
        else:
            st.warning("Diagnostics check is running or API is temporarily busy.")

        if st.button("🔄 Refresh Subsystem Diagnostics", use_container_width=True):
            st.rerun()
