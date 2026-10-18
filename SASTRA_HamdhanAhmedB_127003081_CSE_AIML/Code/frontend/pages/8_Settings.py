import streamlit as st
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from frontend.utils.ui import inject_custom_css, render_header

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")
inject_custom_css()

render_header("Settings", "Configure platform and analysis parameters")

import requests

api_base = "http://127.0.0.1:8000/api/v1"

# Fetch current settings from backend
current_cfg = {
    "chunk_size": 1000,
    "chunk_overlap": 150,
    "enable_table_extraction": True,
    "ocr_enabled": False,
    "flag_circular_dependencies": True,
    "enforce_secure_ipc": True,
    "require_boundary_definitions": True
}
try:
    s_res = requests.get(f"{api_base}/settings", timeout=5)
    if s_res.status_code == 200:
        current_cfg = s_res.json()
except Exception:
    pass

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("Document Extraction Parameters")
        c_size = st.slider("Chunk Size", 200, 2500, int(current_cfg.get("chunk_size", 1000)), step=50, help="Document chunk size in characters")
        c_overlap = st.slider("Chunk Overlap", 0, 500, int(current_cfg.get("chunk_overlap", 150)), step=25, help="Overlap between consecutive chunks")
        c_tables = st.checkbox("Enable Table Extraction", value=bool(current_cfg.get("enable_table_extraction", True)))
        c_ocr = st.checkbox("Enable Optical Character Recognition (OCR)", value=bool(current_cfg.get("ocr_enabled", False)))
        
        if st.button("Save Extraction Parameters", key="save_extraction", use_container_width=True):
            if c_overlap >= c_size:
                st.error("Error: Chunk overlap must be strictly less than chunk size.")
            else:
                payload = {
                    **current_cfg,
                    "chunk_size": c_size,
                    "chunk_overlap": c_overlap,
                    "enable_table_extraction": c_tables,
                    "ocr_enabled": c_ocr
                }
                try:
                    up_res = requests.post(f"{api_base}/settings", json=payload)
                    if up_res.status_code == 200:
                        st.success("Extraction parameters saved and applied to runtime!")
                    else:
                        st.error(f"Failed to save: {up_res.text}")
                except Exception as e:
                    st.error(str(e))

with col2:
    with st.container(border=True):
        st.subheader("Enterprise Validation Rules")
        r_circ = st.checkbox("Flag Circular Dependencies between Components", value=bool(current_cfg.get("flag_circular_dependencies", True)))
        r_ipc = st.checkbox("Enforce Secure IPC strict matching", value=bool(current_cfg.get("enforce_secure_ipc", True)))
        r_bounds = st.checkbox("Require Boundary Definitions on arrays and buffers", value=bool(current_cfg.get("require_boundary_definitions", True)))
        
        st.markdown("<div style='height: 48px;'></div>", unsafe_allow_html=True)
        if st.button("Save Validation Rules", key="save_rules", use_container_width=True):
            payload = {
                **current_cfg,
                "flag_circular_dependencies": r_circ,
                "enforce_secure_ipc": r_ipc,
                "require_boundary_definitions": r_bounds
            }
            try:
                up_res = requests.post(f"{api_base}/settings", json=payload)
                if up_res.status_code == 200:
                    st.success("Enterprise rules saved! Rules will apply to future document uploads.")
                else:
                    st.error(f"Failed to save: {up_res.text}")
            except Exception as e:
                st.error(str(e))

with st.container(border=True):
    st.subheader("Platform Diagnostics & Verification")
    if st.button("Run Diagnostic Self-Test"):
        with st.spinner("Checking subsystems..."):
            try:
                d_res = requests.get(f"{api_base}/diagnostics")
                if d_res.status_code == 200:
                    st.json(d_res.json())
                else:
                    st.error(f"Diagnostic error: {d_res.text}")
            except Exception as e:
                st.error(f"Connection failure: {str(e)}")
