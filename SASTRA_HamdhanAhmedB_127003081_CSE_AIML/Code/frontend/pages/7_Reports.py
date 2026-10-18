import streamlit as st
import os
import sys
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from frontend.utils.ui import inject_custom_css, render_header

st.set_page_config(page_title="Reports & Exports - AUTOSAR AI", page_icon="📥", layout="wide")
inject_custom_css()

render_header("Reports & Exports", "Generate and download architectural compliance, component specification & traceability reports")

project_id = 1
api_base = "http://127.0.0.1:8000/api/v1"

# Fetch components for per-component reporting
components = []
try:
    c_res = requests.get(f"{api_base}/projects/{project_id}/entities")
    if c_res.status_code == 200:
        components = [e["name"] for e in c_res.json() if e.get("entity_type") == "Software Component"]
except Exception:
    pass

c1, c2 = st.columns([1, 2])

with c1:
    with st.container(border=True):
        st.subheader("Generate New Report")
        st.caption("Select report type, scope, and export format:")
        
        report_type = st.selectbox(
            "Report Type", 
            [
                "Component Specification Report", 
                "Architecture Summary", 
                "Findings Report", 
                "Dependency Matrix"
            ]
        )

        selected_comp = None
        if report_type == "Component Specification Report":
            if components:
                selected_comp = st.selectbox("Target Component", components)
            else:
                st.info("No Software Components extracted yet in this project.")
                selected_comp = st.text_input("Component Name", placeholder="e.g. PowertrainManager_SWC")

        format_choice = st.selectbox(
            "Format", 
            ["CSV", "JSON", "PDF", "Markdown (.md)"]
        )
        
        # Normalize format for API payload
        if "Markdown" in format_choice:
            api_format = "MD"
        else:
            api_format = format_choice
        
        if st.button("Generate Report", use_container_width=True):
            with st.spinner(f"Compiling {api_format} report..."):
                try:
                    payload = {
                        "report_type": report_type, 
                        "format": api_format,
                        "component_name": selected_comp
                    }
                    res = requests.post(f"{api_base}/projects/{project_id}/reports", json=payload)
                    if res.status_code == 200:
                        st.success(f"{api_format} report generated successfully!")
                        st.rerun()
                    else:
                        st.error(f"Generation failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

with c2:
    with st.container(border=True):
        st.subheader("Generated Reports Repository")
        st.caption("Immutable persisted reports available for offline download:")
    
    reports = []
    try:
        r_res = requests.get(f"{api_base}/projects/{project_id}/reports")
        if r_res.status_code == 200:
            reports = r_res.json()
    except requests.exceptions.ConnectionError:
        st.warning("⚠️ Backend API server is currently unavailable. Ensure the backend is running on http://127.0.0.1:8000.")
    except Exception as e:
        st.error(f"Failed to fetch reports: {str(e)}")

    if reports:
        for r in reports:
            created_str = str(r.get('created_at', ''))[:19]
            fname = os.path.basename(r.get('storage_path', f"report_{r['id']}"))
            fmt = (r.get('format') or "").upper()
            is_valid = r.get("is_valid", True)
            file_exists = r.get("file_exists", True)

            # Format icon
            if fmt == "PDF":
                fmt_icon = "📕"
            elif fmt in ("MD", "MARKDOWN"):
                fmt_icon = "📝"
            elif fmt == "JSON":
                fmt_icon = "⚙️"
            else:
                fmt_icon = "📊"

            with st.expander(f"{fmt_icon} {r['report_type']} ({fmt}) — {created_str}", expanded=False):
                st.write(f"**Report ID:** `{r['id']}`")
                st.write(f"**Format:** `{fmt}`")
                st.write(f"**Filename:** `{fname}`")

                # Corrupted legacy PDF check
                if fmt == "PDF" and not is_valid:
                    st.error("⚠️ Corrupted Historical PDF: This file was saved without standard binary PDF headers and cannot be opened by PDF readers.")
                    if st.button(f"🔄 Regenerate Valid PDF Report", key=f"regen_{r['id']}"):
                        try:
                            regen_payload = {
                                "report_type": r['report_type'],
                                "format": "PDF"
                            }
                            regen_res = requests.post(f"{api_base}/projects/{project_id}/reports", json=regen_payload)
                            if regen_res.status_code == 200:
                                st.success("Regenerated valid PDF report successfully!")
                                st.rerun()
                            else:
                                st.error(f"Regeneration failed: {regen_res.text}")
                        except Exception as ex:
                            st.error(f"Regeneration error: {str(ex)}")

                elif not file_exists:
                    st.warning("⚠️ Report file is missing from disk storage.")
                else:
                    try:
                        file_res = requests.get(f"{api_base}/reports/{r['id']}/download")
                        if file_res.status_code == 200:
                            if fmt == "CSV":
                                mime_type = "text/csv"
                            elif fmt == "JSON":
                                mime_type = "application/json"
                            elif fmt == "PDF":
                                mime_type = "application/pdf"
                            elif fmt in ("MD", "MARKDOWN"):
                                mime_type = "text/markdown; charset=utf-8"
                            else:
                                mime_type = "application/octet-stream"

                            st.download_button(
                                label=f"⬇️ Download {fname}",
                                data=file_res.content,
                                file_name=fname,
                                mime=mime_type,
                                key=f"dl_btn_{r['id']}",
                                use_container_width=True
                            )
                        elif file_res.status_code == 422:
                            st.error("⚠️ Server detected invalid file format on disk. Please regenerate.")
                        else:
                            st.warning("Report file is pending or unavailable on disk.")
                    except Exception as e:
                        st.error(f"Could not prepare download: {str(e)}")
    else:
        st.info("No reports generated yet. Use the panel on the left to generate one.")
