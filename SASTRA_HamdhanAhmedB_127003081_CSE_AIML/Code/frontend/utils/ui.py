import streamlit as st

def inject_custom_css():
    st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* Global Font */
        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif !important;
            color: #111827;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #E5E7EB !important;
        }
        
        /* Sidebar Navigation Hover & Active States */
        [data-testid="stSidebarNav"] a:hover {
            background-color: #EFF6FF !important;
        }
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background-color: #EFF6FF !important;
            color: #2563EB !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }

        /* Buttons (Primary - Blue) */
        .stButton>button {
            background-color: #2563EB !important;
            color: #FFFFFF !important;
            border-radius: 8px !important;
            border: 1px solid #2563EB !important;
            font-weight: 500 !important;
            padding: 0.5rem 1.25rem !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
        }
        .stButton>button:hover {
            background-color: #1D4ED8 !important;
            border-color: #1D4ED8 !important;
            box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.1) !important;
        }
        
        /* Secondary Buttons / Streamlit standard elements can be styled here if needed */

        /* Metric Cards */
        [data-testid="stMetricValue"] {
            font-size: 2.2rem !important;
            font-weight: 700 !important;
            color: #111827 !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.95rem !important;
            color: #6B7280 !important;
            font-weight: 500 !important;
            text-transform: uppercase;
            letter-spacing: 0.025em;
        }
        
        /* Metric Cards */
        [data-testid="stMetric"] {
            background-color: #FFFFFF;
            border-radius: 10px;
            padding: 1rem 1.25rem;
            border: 1px solid #E5E7EB;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        }
        
        /* Headings */
        h1, h2, h3, h4, h5 {
            color: #111827 !important;
            font-weight: 600 !important;
            letter-spacing: -0.02em !important;
        }
        
        /* Specific Page Titles */
        .page-header {
            border-bottom: 1px solid #E5E7EB;
            padding-bottom: 1rem;
            margin-bottom: 2rem;
        }

        /* Expander headers */
        .streamlit-expanderHeader {
            background-color: #F8FAFC !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            color: #111827 !important;
            border: 1px solid #E5E7EB !important;
        }
        
        /* DataFrames / Tables */
        [data-testid="stDataFrame"] {
            border-radius: 8px !important;
            border: 1px solid #E5E7EB !important;
        }
        
        /* Alerts */
        .stAlert {
            border-radius: 8px !important;
            border: 1px solid #DBEAFE !important;
            background-color: #EFF6FF !important;
            color: #1D4ED8 !important;
        }
        
        /* Text inputs */
        .stTextInput input, .stTextArea textarea {
            border-radius: 8px !important;
            border: 1px solid #E5E7EB !important;
            background-color: #FFFFFF !important;
            color: #111827 !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #2563EB !important;
            box-shadow: 0 0 0 1px #2563EB !important;
        }
        
        /* Container Cards */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF !important;
            border-radius: 12px !important;
            border: 1px solid #E5E7EB !important;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;
        }
        
        /* Custom UI classes */
        .text-muted { color: #6B7280; }
        .text-primary { color: #2563EB; }
        .badge-success { background-color: #DCFCE7; color: #16A34A; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: 500;}
        .badge-processing { background-color: #DBEAFE; color: #2563EB; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: 500;}
        .badge-pending { background-color: #FEF3C7; color: #D97706; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: 500;}
        .badge-error { background-color: #FEE2E2; color: #DC2626; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: 500;}
        </style>
    """, unsafe_allow_html=True)

def render_header(title: str, subtitle: str = None):
    sub_html = f"<p style='color:#6B7280; font-size:1.05rem; margin-top:-6px; margin-bottom:1rem;'>{subtitle}</p>" if subtitle else ""
    st.markdown(f"""
        <div style='border-bottom: 1px solid #E5E7EB; margin-bottom: 1.5rem; padding-bottom: 0.5rem;'>
            <h1 style='color: #111827; font-weight: 700; font-size: 1.9rem; margin-bottom: 6px; letter-spacing: -0.02em;'>{title}</h1>
            {sub_html}
        </div>
    """, unsafe_allow_html=True)

def render_mermaid(code: str, height: int = 520):
    """Renders a Mermaid diagram inside a sandboxed HTML component with full SVG rendering."""
    import streamlit.components.v1 as components
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

