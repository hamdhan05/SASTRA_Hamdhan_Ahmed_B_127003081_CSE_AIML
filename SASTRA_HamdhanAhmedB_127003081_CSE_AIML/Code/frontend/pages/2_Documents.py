import streamlit as st
import os
import sys
import requests

# Ensure backend imports can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from frontend.utils.ui import inject_custom_css, render_header

st.set_page_config(page_title="Documents - AUTOSAR AI", page_icon="📄", layout="wide")
inject_custom_css()

render_header("Documents", "Manage AUTOSAR specifications, versioning, and lifecycle governance")

project_id = 1
api_base = "http://127.0.0.1:8000/api/v1"

col1, col2 = st.columns([3, 1])

with col1:
    with st.container(border=True):
        st.subheader("Document Repository")
        
        # Filters
        f1, f2, f3, f4 = st.columns(4)
        f1.selectbox("Project", ["Default Project"], disabled=True)
        status_filter = f2.selectbox("Processing Status", ["All", "READY", "PROCESSING", "FAILED", "UPLOADED"])
        gov_filter = f3.selectbox("Governance State", ["All", "DRAFT", "IN_REVIEW", "APPROVED", "SUPERSEDED"])
        search_q = f4.text_input("Search", placeholder="Search documents...")
        
        docs = []
        try:
            res = requests.get(f"{api_base}/projects/{project_id}/documents")
            if res.status_code == 200:
                docs = res.json()
        except Exception:
            pass
            
        if status_filter != "All":
            docs = [d for d in docs if d.get("status") == status_filter]
        if gov_filter != "All":
            docs = [d for d in docs if d.get("governance_state") == gov_filter]
        if search_q:
            docs = [d for d in docs if search_q.lower() in d.get("original_filename", "").lower()]
        
        if docs:
            for d in docs:
                status_label = d.get('status', 'UNKNOWN')
                gov_label = d.get('governance_state', 'DRAFT')
                ver_label = d.get('version_label', '1.0') or '1.0'
                doc_name = d.get('original_filename', f"Document #{d.get('id')}")
                
                # Colors for governance badges
                gov_color = "#2563EB" if gov_label == "APPROVED" else ("#D97706" if gov_label == "IN_REVIEW" else ("#DC2626" if gov_label == "SUPERSEDED" else "#4B5563"))
                
                with st.expander(f"📄 {doc_name}  —  v{ver_label}  [{gov_label}]  [{status_label}]", expanded=False):
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.write(f"**Document ID:** {d.get('id')}")
                        st.write(f"**Specification Version:** `{ver_label}`")
                        st.write(f"**Governance State:** <span style='color: {gov_color}; font-weight: 600;'>{gov_label}</span>", unsafe_allow_html=True)
                        st.write(f"**Processing Status:** `{status_label}`")
                        st.write(f"**Pages:** {d.get('page_count') or 'N/A'}")
                    with col_info2:
                        sha_val = d.get('sha256_hash') or 'N/A'
                        sha_display = f"{sha_val[:16]}..." if len(sha_val) > 16 else sha_val
                        st.write(f"**SHA256:** `{sha_display}`")
                        st.write(f"**Uploaded At:** {d.get('created_at', 'N/A')}")
                        if d.get("error_message"):
                            st.error(f"Error: {d['error_message']}")

                    # Governance update form
                    st.markdown("---")
                    st.caption("⚙️ **Lifecycle Governance Transition**")
                    gov_col1, gov_col2, gov_col3 = st.columns([2, 1, 1])
                    with gov_col1:
                        new_gov = st.selectbox(
                            "Change Governance State", 
                            ["DRAFT", "IN_REVIEW", "APPROVED", "SUPERSEDED"],
                            index=["DRAFT", "IN_REVIEW", "APPROVED", "SUPERSEDED"].index(gov_label) if gov_label in ["DRAFT", "IN_REVIEW", "APPROVED", "SUPERSEDED"] else 0,
                            key=f"gov_sel_{d.get('id')}"
                        )
                    with gov_col2:
                        new_ver = st.text_input("Version", value=ver_label, key=f"ver_input_{d.get('id')}")
                    with gov_col3:
                        st.write("")
                        st.write("")
                        if st.button("Apply State", key=f"btn_gov_{d.get('id')}", use_container_width=True):
                            try:
                                patch_res = requests.patch(
                                    f"{api_base}/documents/{d.get('id')}/governance",
                                    json={"governance_state": new_gov, "version_label": new_ver}
                                )
                                if patch_res.status_code == 200:
                                    st.success(f"Updated governance state to {new_gov}!")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to update: {patch_res.text}")
                            except Exception as e:
                                st.error(str(e))
                            
                    act_col1, act_col2 = st.columns([1, 1])
                    with act_col1:
                        if st.button("🔄 Reprocess", key=f"reprocess_{d.get('id')}", use_container_width=True):
                            try:
                                rep_res = requests.post(f"{api_base}/documents/{d.get('id')}/reprocess")
                                if rep_res.status_code == 200:
                                    st.success(f"Reprocessing started for {doc_name}!")
                                    st.rerun()
                                else:
                                    st.error("Reprocess request failed.")
                            except Exception as e:
                                st.error(str(e))
                                
                    with act_col2:
                        if st.button("🗑️ Delete", key=f"del_{d.get('id')}", use_container_width=True):
                            try:
                                del_res = requests.delete(f"{api_base}/documents/{d.get('id')}")
                                if del_res.status_code == 200:
                                    st.success(f"Deleted {doc_name}")
                                    st.rerun()
                                else:
                                    st.error("Delete request failed.")
                            except Exception as e:
                                st.error(str(e))
        else:
            st.info("No documents found matching the filter.")

with col2:
    with st.container(border=True):
        st.subheader("Upload Document")
        st.caption("Upload an AUTOSAR HLD or specification PDF with explicit version and governance controls.")
        
        uploaded_file = st.file_uploader("Select PDF", type=["pdf"])
        upload_ver = st.text_input("Specification Version", value="1.0", placeholder="e.g. 1.0, 2.0")
        upload_gov = st.selectbox("Governance State", ["DRAFT", "IN_REVIEW", "APPROVED", "SUPERSEDED"], index=0)
        
        if uploaded_file is not None:
            if st.button("Upload & Process", use_container_width=True):
                with st.spinner("Uploading and analyzing document..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                        data = {
                            "version_label": upload_ver.strip() if upload_ver else "1.0",
                            "governance_state": upload_gov
                        }
                        res = requests.post(f"{api_base}/projects/{project_id}/documents", files=files, data=data)
                        if res.status_code == 200:
                            st.success("Uploaded successfully! Background processing initiated.")
                            st.rerun()
                        else:
                            st.error(f"Failed to upload: {res.text}")
                    except Exception as e:
                        st.error(f"Connection error: {str(e)}")
