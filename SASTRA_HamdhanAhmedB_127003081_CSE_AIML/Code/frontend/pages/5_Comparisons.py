import streamlit as st
import os
import sys
import json
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from frontend.utils.ui import inject_custom_css, render_header

st.set_page_config(page_title="Document Comparison - AUTOSAR AI", page_icon="⚖️", layout="wide")
inject_custom_css()

render_header("Document Comparison", "Compare baseline and modified architectural specifications, detect renames & evaluate change impact")

project_id = 1
api_base = "http://127.0.0.1:8000/api/v1"

# Fetch documents for selection
docs = []
try:
    res = requests.get(f"{api_base}/projects/{project_id}/documents")
    if res.status_code == 200:
        docs = res.json()
except Exception:
    pass
    
doc_options = {f"{d['original_filename']} (v{d.get('version_label', '1.0')})": d["id"] for d in docs if d["status"] == "READY"}

tab_compare, tab_history = st.tabs(["Document Comparison", "Comparison History"])

with tab_compare:
    with st.container(border=True):
        st.subheader("Run Document Revision Comparison")
        st.caption("Select baseline and comparison specifications to detect added, removed, modified, and renamed architectural entities.")
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            base_doc_name = st.selectbox("Baseline Document", list(doc_options.keys()) if doc_options else ["No processed docs available"], key="sel_base")
        with c2:
            comp_doc_name = st.selectbox("Comparison Document", list(doc_options.keys()) if doc_options else ["No processed docs available"], key="sel_comp")
        with c3:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            can_run = bool(doc_options and len(doc_options) >= 2)
            if st.button("Compare Documents", use_container_width=True, disabled=not can_run):
                if base_doc_name == comp_doc_name:
                    st.error("Cannot compare a document to itself. Please choose two distinct documents.")
                else:
                    with st.spinner("Analyzing architectural differences & renames..."):
                        payload = {
                            "baseline_document_id": doc_options[base_doc_name],
                            "comparison_document_id": doc_options[comp_doc_name]
                        }
                        res = requests.post(f"{api_base}/projects/{project_id}/comparisons", json=payload)
                        if res.status_code == 200:
                            comp_data = res.json()
                            st.session_state.current_comparison = comp_data
                            st.success("Comparison completed successfully!")
                        else:
                            st.error(f"Comparison failed: {res.text}")

    if "current_comparison" in st.session_state:
        comp_data = st.session_state.current_comparison
        try:
            results = json.loads(comp_data.get("results_json", "{}"))
        except Exception:
            results = {"added": [], "removed": [], "modified": [], "renamed": []}
            
        added_list = results.get("added", [])
        removed_list = results.get("removed", [])
        modified_list = results.get("modified", [])
        renamed_list = results.get("renamed", [])
        impact_analysis = results.get("impact_analysis", {})

        st.markdown(f"### Revision Diff: `{results.get('baseline_filename')} (v{results.get('baseline_version', '1.0')})` ➔ `{results.get('comparison_filename')} (v{results.get('comparison_version', '2.0')})`")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Added Entities", len(added_list))
        m2.metric("Removed Entities", len(removed_list))
        m3.metric("Modified Entities", len(modified_list))
        m4.metric("Renamed Entities", len(renamed_list))

        if not added_list and not removed_list and not modified_list and not renamed_list:
            st.info("No architectural differences detected between the selected specifications.")
        else:
            # 1. Renamed Entities
            if renamed_list:
                st.markdown("#### 🏷️ Renamed Entities (Deterministic Matching)")
                for item in renamed_list:
                    st.markdown(f"""
                    <div style='background:#F0FDF4; border:1px solid #BBF7D0; border-radius:6px; padding:10px 14px; margin-bottom:8px;'>
                        <b>[{item['type']}]</b> <code>{item['old_name']}</code> ➔ <b><code>{item['new_name']}</code></b><br>
                        <span style='color:#16A34A; font-size:0.85rem;'><b>Matching Basis:</b> {item.get('matching_basis')}</span> • 
                        <span style='color:#6B7280; font-size:0.85rem;'>Baseline Page {item.get('baseline_page', 1)} ➔ Comparison Page {item.get('comparison_page', 1)}</span>
                    </div>
                    """, unsafe_allow_html=True)

            # 2. Modified Components (Data type diffs, direction diffs)
            if modified_list:
                st.markdown("#### 🔄 Modified Architectural Attributes")
                for item in modified_list:
                    with st.expander(f"[{item['type']}] {item['name']}  —  {item.get('change_summary', 'Modified')}"):
                        if item.get("change_summary"):
                            st.warning(f"**Changes:** {item['change_summary']}")
                        
                        col_dt1, col_dt2 = st.columns(2)
                        with col_dt1:
                            st.write(f"**Baseline Definition (Page {item.get('baseline_page', 1)}):**")
                            if item.get("baseline_data_type"):
                                st.write(f"- Signal Type: `{item['baseline_data_type']}`")
                            if item.get("baseline_direction"):
                                st.write(f"- Port Direction: `{item['baseline_direction']}`")
                            if item.get("baseline_interface"):
                                st.write(f"- Interface: `{item['baseline_interface']}`")
                            st.code(item.get('baseline_excerpt', ''), language='text')
                            
                        with col_dt2:
                            st.write(f"**Comparison Definition (Page {item.get('comparison_page', 1)}):**")
                            if item.get("comparison_data_type"):
                                st.write(f"- Signal Type: `{item['comparison_data_type']}`")
                            if item.get("comparison_direction"):
                                st.write(f"- Port Direction: `{item['comparison_direction']}`")
                            if item.get("comparison_interface"):
                                st.write(f"- Interface: `{item['comparison_interface']}`")
                            st.code(item.get('comparison_excerpt', ''), language='text')

            # 3. Added Entities
            if added_list:
                st.markdown("#### ➕ Added Components")
                for item in added_list:
                    st.markdown(f"- **[{item['type']}]** `{item['name']}` (Page {item.get('source_page', 1)}) — *{item.get('description', '')}*")
            
            # 4. Removed Entities
            if removed_list:
                st.markdown("#### ➖ Removed Components")
                for item in removed_list:
                    st.markdown(f"- **[{item['type']}]** `{item['name']}` (Page {item.get('source_page', 1)}) — *{item.get('description', '')}*")

            # 5. Integrated Change Impact Traversal
            if impact_analysis:
                st.markdown("---")
                st.markdown("#### 💥 Downstream Change Impact Traversal")
                st.caption("Components affected downstream across dependency relationships by these revision changes:")
                for cname, imp in impact_analysis.items():
                    with st.expander(f"⚠️ Impact for modified component: {cname} ({imp.get('total_impacted_count', 0)} affected)"):
                        if imp.get("direct_dependents"):
                            st.write(f"**Direct Dependents (1-hop):** {', '.join([f'`{d}`' for d in imp['direct_dependents']])}")
                        if imp.get("transitive_dependents"):
                            st.write(f"**Transitive Downstream Dependents (>1 hops):** {', '.join([f'`{td}`' for td in imp['transitive_dependents']])}")
                        if imp.get("impact_paths"):
                            st.write("**Impact Traversal Paths:**")
                            for p in imp["impact_paths"]:
                                st.code(p, language="text")

with tab_history:
    with st.container(border=True):
        st.subheader("Saved Comparison Runs")
        
        past_comps = []
        try:
            hist_res = requests.get(f"{api_base}/projects/{project_id}/comparisons")
            if hist_res.status_code == 200:
                past_comps = hist_res.json()
        except Exception as e:
            st.error(f"Failed to fetch history: {str(e)}")
            
        if past_comps:
            for pc in past_comps:
                b_name = pc.get('baseline_document_name')
                b_ver = pc.get('baseline_version', '1.0')
                c_name = pc.get('comparison_document_name')
                c_ver = pc.get('comparison_version', '2.0')
                ts = pc.get('created_at', '')[:19]
                with st.expander(f"⚖️ Baseline: {b_name} (v{b_ver}) vs {c_name} (v{c_ver}) — {ts}", expanded=False):
                    st.write(f"**Added:** {pc.get('added_count', 0)} | **Removed:** {pc.get('removed_count', 0)} | **Modified:** {pc.get('modified_count', 0)} | **Renamed:** {pc.get('renamed_count', 0)}")
                    if st.button("Load This Result", key=f"load_comp_{pc['id']}"):
                        st.session_state.current_comparison = pc
                        st.success("Loaded into Comparison view!")
                        st.rerun()
        else:
            st.info("No comparison history saved yet.")
