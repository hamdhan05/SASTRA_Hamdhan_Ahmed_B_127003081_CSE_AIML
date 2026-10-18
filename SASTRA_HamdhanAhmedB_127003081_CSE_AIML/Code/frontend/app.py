import streamlit as st
import os
import sys

# Ensure backend imports can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from frontend.utils.ui import inject_custom_css, render_header

st.set_page_config(
    page_title="AUTOSAR AI - Engineering Intelligence",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()

render_header("⚙️ AUTOSAR AI", "Engineering Intelligence Platform")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    Welcome to **AUTOSAR AI**. This platform assists automotive software engineers with intelligent document analysis.
    
    ### Capabilities
    - **Intelligent RAG**: Query HLDs, ICDs, and SRS documents with contextual AI.
    - **Entity Extraction**: Automatically extract Software Components, Runnables, and Interfaces from specifications.
    - **Traceability**: Validate component dependencies against enterprise rules.
    - **Automated Validation**: Flag insecure IPCs, missing bounds, and circular dependencies automatically.
    
    👈 **Select a workspace from the sidebar to begin.**
    """)

with col2:
    with st.container(border=True):
        st.subheader("Quick Actions")
        if st.button("Upload Specification Document", use_container_width=True):
            st.switch_page("pages/2_Documents.py")
        if st.button("Ask AI Assistant", use_container_width=True):
            st.switch_page("pages/4_AI_Assistant.py")

# Decorative footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #9CA3AF; margin-top: 40px; font-size: 0.85rem;'>AUTOSAR AI Engine | Engineered for Automotive Excellence</div>", unsafe_allow_html=True)
