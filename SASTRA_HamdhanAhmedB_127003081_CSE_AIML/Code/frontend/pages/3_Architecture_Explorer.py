import streamlit as st
import os
import sys
import pandas as pd
import requests

# Ensure backend imports can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import streamlit.components.v1 as components
from frontend.utils.ui import inject_custom_css, render_header

def render_mermaid(code: str, height: int = 520):
    """Renders a Mermaid diagram inside a sandboxed HTML component with full SVG rendering."""
    clean_code = code.strip()

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <style>
            * {{
                box-sizing: border-box;
            }}
            body {{
                margin: 0;
                padding: 12px;
                background-color: #FAFAFA;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                overflow: auto;
            }}
            #mermaid-wrapper {{
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: {height - 40}px;
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                overflow: auto;
            }}
            .mermaid {{
                width: 100%;
                text-align: center;
            }}
            svg {{
                max-width: 100% !important;
                height: auto !important;
            }}
        </style>
    </head>
    <body>
        <div id="mermaid-wrapper">
            <pre class="mermaid">
{clean_code}
            </pre>
        </div>
        <script>
            try {{
                mermaid.initialize({{
                    startOnLoad: true,
                    theme: 'base',
                    themeVariables: {{
                        primaryColor: '#EFF6FF',
                        primaryTextColor: '#1E3A8A',
                        primaryBorderColor: '#2563EB',
                        lineColor: '#64748B',
                        secondaryColor: '#ECFDF5',
                        tertiaryColor: '#FEF3C7',
                        fontFamily: 'Inter, sans-serif',
                        fontSize: '13px'
                    }},
                    securityLevel: 'loose',
                    flowchart: {{
                        useMaxWidth: false,
                        htmlLabels: true,
                        curve: 'basis'
                    }}
                }});
            }} catch (e) {{
                document.getElementById('mermaid-wrapper').innerHTML = 
                    '<div style="color: #DC2626; font-size: 14px; font-weight: 500;">Failed to render Mermaid diagram: ' + e.message + '</div>';
            }}
        </script>
    </body>
    </html>
    """
    components.html(html_content, height=height, scrolling=True)

st.set_page_config(page_title="Architecture Explorer - AUTOSAR AI", page_icon="🧩", layout="wide")
inject_custom_css()

render_header("Architecture Explorer", "AUTOSAR component inventory, port/signal definitions, topology graph & change impact")

project_id = 1
api_base = "http://127.0.0.1:8000/api/v1"

tab_swc, tab_ports, tab_graph = st.tabs([
    "🧩 SWCs & Interfaces", 
    "🚪 Ports & Signals", 
    "🗺️ Architecture Topology & Change Impact"
])

# ==============================================================================
# TAB 1: SWCs & Interfaces
# ==============================================================================
with tab_swc:
    with st.container(border=True):
        col_f1, col_f2 = st.columns([1, 3])
        with col_f1:
            type_filter = st.selectbox("Entity Type", ["All", "Software Component", "Runnable", "Interface"])
        with col_f2:
            search_q = st.text_input("Search Components", placeholder="e.g. PowertrainManager_SWC")

    entities = []
    try:
        res = requests.get(f"{api_base}/projects/{project_id}/entities")
        if res.status_code == 200:
            entities = res.json()
    except Exception:
        pass

    # Filter out Ports & Signals from SWC tab
    swc_entities = [e for e in entities if e.get("entity_type") in ["Software Component", "Runnable", "Interface"]]

    if type_filter != "All":
        swc_entities = [e for e in swc_entities if e.get("entity_type") == type_filter]
    if search_q:
        swc_entities = [e for e in swc_entities if search_q.lower() in e.get("name", "").lower()]

    if swc_entities:
        for e in swc_entities:
            etype = e.get("entity_type", "Component")
            r_status = e.get("review_status", "pending")
            status_badge = "badge-success" if r_status == 'confirmed' else ("badge-error" if r_status == 'rejected' else "badge-pending")
            with st.expander(f"🧩 [{etype}] {e.get('name', 'Unknown')}  —  {r_status.upper()}", expanded=False):
                info_c1, info_c2 = st.columns(2)
                with info_c1:
                    st.write(f"**Entity Type:** `{etype}`")
                    st.write(f"**Name:** `{e.get('name')}`")
                    st.write(f"**Confidence:** {round(e.get('confidence', 0.9) * 100)}%")
                    st.write(f"**Source Page:** Page {e.get('source_page') or 'N/A'}")
                with info_c2:
                    st.write(f"**Review Status:** <span class='{status_badge}'>{r_status}</span>", unsafe_allow_html=True)
                    st.write(f"**Extraction Method:** {e.get('extraction_method', 'engineering_heuristics')}")
                    
                if e.get("source_excerpt"):
                    st.markdown("**Source Excerpt:**")
                    st.code(e["source_excerpt"], language="text")
                    
                # Entity Review Actions
                st.markdown("**Review Verification:**")
                rev_c1, rev_c2, rev_c3 = st.columns(3)
                with rev_c1:
                    if st.button("✅ Confirm", key=f"conf_{e['id']}", use_container_width=True):
                        requests.post(f"{api_base}/entities/{e['id']}/review", json={"status": "confirmed"})
                        st.success("Marked as Confirmed!")
                        st.rerun()
                with rev_c2:
                    if st.button("❌ Reject", key=f"rej_{e['id']}", use_container_width=True):
                        requests.post(f"{api_base}/entities/{e['id']}/review", json={"status": "rejected"})
                        st.warning("Marked as Rejected.")
                        st.rerun()
                with rev_c3:
                    if st.button("⏳ Reset Pending", key=f"rst_{e['id']}", use_container_width=True):
                        requests.post(f"{api_base}/entities/{e['id']}/review", json={"status": "pending"})
                        st.info("Reset to Pending.")
                        st.rerun()
    else:
        st.info("No software components or interfaces found matching current filters.")

# ==============================================================================
# TAB 2: Ports & Signals
# ==============================================================================
with tab_ports:
    with st.container(border=True):
        st.subheader("Port & Signal Definitions")
        st.caption("Inspect extracted AUTOSAR Ports (PPort/RPort), directions, associated interfaces, and carried signal data types.")

        # Fetch ports and signals from dedicated endpoint
        ps_data = []
        try:
            ps_res = requests.get(f"{api_base}/projects/{project_id}/ports_and_signals")
            if ps_res.status_code == 200:
                ps_data = ps_res.json()
        except Exception:
            pass

        # Filter controls
        f_p1, f_p2, f_p3 = st.columns(3)
        available_comps = sorted(list({p.get("component") for p in ps_data if p.get("component") and p.get("component") != "Unassigned"}))
        comp_filter = f_p1.selectbox("Filter Component", ["All"] + available_comps)
        dir_filter = f_p2.selectbox("Port Direction", ["All", "Input", "Output", "InOut", "N/A"])
        search_ps = f_p3.text_input("Search Port or Signal", placeholder="e.g. Port_VehicleSpeed")

        filtered_ps = ps_data
        if comp_filter != "All":
            filtered_ps = [p for p in filtered_ps if p.get("component") == comp_filter]
        if dir_filter != "All":
            filtered_ps = [p for p in filtered_ps if p.get("direction") == dir_filter]
        if search_ps:
            filtered_ps = [p for p in filtered_ps if search_ps.lower() in p.get("name", "").lower() or search_ps.lower() in (p.get("carried_signals") or "").lower()]

        if filtered_ps:
            df_ps = pd.DataFrame([{
                "ID": p.get("id"),
                "Type": p.get("type"),
                "Name": p.get("name"),
                "Component": p.get("component"),
                "Direction": p.get("direction"),
                "Interface": p.get("interface"),
                "Carried Signals": p.get("carried_signals"),
                "Signal Data Type": p.get("signal_data_type"),
                "Version": p.get("version"),
                "Page": p.get("source_page"),
                "Status": p.get("review_status")
            } for p in filtered_ps])
            st.dataframe(df_ps, use_container_width=True, hide_index=True)
            st.caption(f"Showing {len(filtered_ps)} of {len(ps_data)} architectural port and signal records.")
        else:
            st.info("No port or signal definitions found for this project. Upload an AUTOSAR specification with port declarations (e.g. PPort_*, RPort_*, Signal_*) to populate this table.")

# ==============================================================================
# TAB 3: Topology Graph & Dependency Change Impact
# ==============================================================================
with tab_graph:
    with st.container(border=True):
        st.subheader("Architectural Topology Graph")
        st.caption("Visual representation of validated component dependencies, interfaces, and port linkages.")

        topo_data = {}
        try:
            topo_res = requests.get(f"{api_base}/projects/{project_id}/topology")
            if topo_res.status_code == 200:
                topo_data = topo_res.json()
        except Exception:
            pass

        mermaid_code = topo_data.get("mermaid_code", "graph TD;\n    empty[No graph data]")

        # Orientation & Canvas controls
        ctrl_c1, ctrl_c2, ctrl_c3 = st.columns([1, 1, 2])
        with ctrl_c1:
            graph_dir = st.selectbox("Diagram Orientation", ["Left to Right (LR)", "Top to Bottom (TD)"], index=0)
        with ctrl_c2:
            diagram_height = st.slider("Canvas Height", min_value=350, max_value=850, value=520, step=50)

        # Apply user-chosen orientation
        if "Top to Bottom" in graph_dir and mermaid_code.startswith("graph LR"):
            active_mermaid = mermaid_code.replace("graph LR", "graph TD", 1)
        elif "Left to Right" in graph_dir and mermaid_code.startswith("graph TD"):
            active_mermaid = mermaid_code.replace("graph TD", "graph LR", 1)
        else:
            active_mermaid = mermaid_code

        # Render visual interactive diagram
        render_mermaid(active_mermaid, height=diagram_height)

        with st.expander("📋 View Raw Mermaid Definition", expanded=False):
            st.code(active_mermaid, language="mermaid")

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
    
    col_edges, col_impact = st.columns([1, 1])

    with col_edges:
        with st.container(border=True):
            st.subheader("Directed Graph Edges")
            st.caption("Explicit architectural relationships stored in SQLite:")
            edges = topo_data.get("edges", [])
            if edges:
                df_edges = pd.DataFrame([{
                    "Source Entity": e.get("source"),
                    "Relationship": e.get("relationship_type"),
                    "Target Entity": e.get("target"),
                    "Page": e.get("source_page"),
                    "Status": e.get("review_status")
                } for e in edges])
                st.dataframe(df_edges, use_container_width=True, hide_index=True)
            else:
                st.info("No relationship edges extracted yet.")

    with col_impact:
        with st.container(border=True):
            st.subheader("🔍 Change Impact Analysis")
            st.caption("Select a component to trace direct and transitive downstream dependents:")
            
            all_swc_names = [e.get("name") for e in entities if e.get("entity_type") == "Software Component"]
            if all_swc_names:
                selected_root = st.selectbox("Select Modified Component", all_swc_names)
                if st.button("Run Impact Traversal", use_container_width=True):
                    try:
                        imp_res = requests.get(f"{api_base}/projects/{project_id}/impact", params={"root_entity_name": selected_root})
                        if imp_res.status_code == 200:
                            imp = imp_res.json()
                            tot_impacted = imp.get("total_impacted_count", 0)
                            st.write(f"**Total Impacted Dependents:** `{tot_impacted}`")
                            
                            if imp.get("direct_dependents"):
                                st.markdown(f"**Direct Dependents (1-hop):**")
                                for d in imp["direct_dependents"]:
                                    st.markdown(f"- 🔴 `{d}`")
                            else:
                                st.markdown("*(No direct dependents)*")

                            if imp.get("transitive_dependents"):
                                st.markdown(f"**Transitive Downstream Dependents (>1 hops):**")
                                for td in imp["transitive_dependents"]:
                                    st.markdown(f"- 🟠 `{td}`")

                            if imp.get("impact_paths"):
                                with st.expander("Dependency Impact Traversal Paths", expanded=True):
                                    for p in imp["impact_paths"]:
                                        st.code(p, language="text")

                            if imp.get("cycle_detected"):
                                st.warning("⚠️ Circular dependency detected during graph traversal. Protected against infinite loop.")
                    except Exception as e:
                        st.error(f"Impact calculation error: {str(e)}")
            else:
                st.info("No software components available for impact analysis.")
