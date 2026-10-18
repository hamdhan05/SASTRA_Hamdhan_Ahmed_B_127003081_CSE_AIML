import streamlit as st
import os
import sys
import pandas as pd
import requests
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from frontend.utils.ui import inject_custom_css, render_header

st.set_page_config(page_title="Evaluation - AUTOSAR AI", page_icon="📈", layout="wide")
inject_custom_css()

render_header("Engineering Evaluation", "Reproducible RAG benchmark evaluation across technical AUTOSAR queries and adversarial abstentions")

project_id = 1
api_base = "http://127.0.0.1:8000/api/v1"

tab_run, tab_history = st.tabs(["🚀 Benchmark Execution", "📜 Benchmark Run History"])

with tab_run:
    with st.container(border=True):
        st.subheader("Evaluation Dataset & Configuration")
        
        # Fetch dataset metadata
        ds_info = {}
        try:
            ds_res = requests.get(f"{api_base}/projects/{project_id}/evaluation/dataset")
            if ds_res.status_code == 200:
                ds_info = ds_res.json()
        except Exception:
            pass

        d_col1, d_col2 = st.columns([2, 1])
        with d_col1:
            st.write(f"**Curated Benchmark:** {ds_info.get('name', 'AUTOSAR HLD Technical Benchmark')}")
            st.write(f"**Dataset Version:** `{ds_info.get('dataset_version', '1.0')}` | **Total Queries:** `{ds_info.get('total_queries', 35)}` (25 technical + 10 adversarial)")
            st.caption(f"**Provenance:** {ds_info.get('provenance', 'Curated from AUTOSAR Adaptive and Classic specifications.')}")
        with d_col2:
            st.markdown("""
            <div style='background-color: #EFF6FF; border: 1px solid #DBEAFE; border-radius: 8px; padding: 10px 14px;'>
                <span style='color: #1D4ED8; font-weight: 600; font-size: 0.85rem;'>Evaluator Engine</span><br>
                <span style='color: #4B5563; font-size: 0.82rem;'>Ollama llama3.2:3b • Read-only Safe Execution</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            strategy_choice = st.selectbox("Retrieval Strategy", ["Dense Semantic", "Hybrid (Dense + BM25 + RRF)"])
            selected_strat = "hybrid" if "Hybrid" in strategy_choice else "dense"
        with c2:
            top_k_val = st.slider("Top-K Evidence Chunks", min_value=1, max_value=10, value=5)
        with c3:
            query_sample = st.selectbox("Queries to Evaluate", ["5 (Quick Diagnostic)", "10 (Sample Run)", "35 (Full Benchmark)"], index=0)
            sample_count = int(query_sample.split()[0])
        with c4:
            st.write("")
            st.write("")
            run_btn = st.button("▶️ Execute Benchmark", use_container_width=True)

    if run_btn:
        with st.spinner(f"Executing {selected_strat.upper()} benchmark across {sample_count} queries via Ollama (llama3.2:3b)..."):
            try:
                b_payload = {
                    "strategy": selected_strat,
                    "top_k": top_k_val,
                    "max_queries": sample_count
                }
                b_res = requests.post(f"{api_base}/projects/{project_id}/evaluation/run", json=b_payload, timeout=300)
                if b_res.status_code == 200:
                    st.session_state.latest_benchmark = b_res.json()
                    st.success(f"Benchmark completed successfully! Run ID: #{st.session_state.latest_benchmark.get('run_id')}")
                else:
                    st.error(f"Benchmark run failed: {b_res.text}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")

    if "latest_benchmark" in st.session_state:
        bm = st.session_state.latest_benchmark
        st.markdown("---")
        st.subheader("Benchmark Performance Metrics")
        
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("MRR", f"{bm.get('mrr', 0.0)}")
        m2.metric("Hit Rate @ 1", f"{bm.get('hit_rate_at_1', 0.0)}%")
        m3.metric("Citation Precision", f"{bm.get('citation_precision', 0.0)}%")
        m4.metric("Supported Claims", f"{bm.get('supported_claim_rate', 0.0)}%")
        m5.metric("Abstention Acc.", f"{bm.get('abstention_accuracy', 0.0)}%")
        m6.metric("Avg Latency", f"{bm.get('avg_latency_ms', 0.0)} ms")

        # Per query breakdown
        queries_res = bm.get("per_query_results", [])
        if queries_res:
            st.markdown("#### Query-by-Query Evaluation Breakdown")
            df_q = pd.DataFrame([{
                "ID": q["id"],
                "Query": q["query"],
                "Unanswerable?": "Yes (Adversarial)" if q.get("is_unanswerable") else "No",
                "Hit Rank": q.get("hit_rank") or "N/A",
                "MRR": q.get("reciprocal_rank") or "N/A",
                "Abstention Correct?": "✅ Correct" if q.get("abstention_correct") == 1.0 else ("❌ Failed" if q.get("abstention_correct") == 0.0 else "N/A"),
                "Claim Rate": f"{round(q['supported_claim_rate'] * 100)}%" if q.get("supported_claim_rate") is not None else "N/A",
                "Latency (ms)": q.get("latency_ms")
            } for q in queries_res])
            st.dataframe(df_q, use_container_width=True, hide_index=True)

with tab_history:
    with st.container(border=True):
        st.subheader("Historical Benchmark Runs")
        st.caption("Inspect and compare past benchmark runs across Dense and Hybrid retrieval strategies:")
        
        hist_runs = []
        try:
            h_res = requests.get(f"{api_base}/projects/{project_id}/evaluation/history")
            if h_res.status_code == 200:
                hist_runs = h_res.json()
        except Exception as e:
            st.error(f"Error fetching history: {str(e)}")

        if hist_runs:
            df_hist = pd.DataFrame([{
                "Run ID": r["id"],
                "Date": r["created_at"][:19],
                "Strategy": r["strategy"].upper(),
                "Top-K": r["top_k"],
                "Queries": r["total_queries"],
                "MRR": r["mrr"],
                "Hit Rate @ 1": f"{r['hit_rate_at_1']}%",
                "Citation Prec.": f"{r['citation_precision']}%",
                "Supported Claims": f"{r['supported_claim_rate']}%",
                "Abstention Acc.": f"{r['abstention_accuracy']}%",
                "Avg Latency": f"{r['avg_latency_ms']} ms"
            } for r in hist_runs])
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
        else:
            st.info("No benchmark runs recorded yet. Execute a benchmark in the tab above to record results.")
