"""
========================================================================================
GENAI MINI PROJECT: PROBLEM STATEMENT 37
Title: Previous Year Question Paper Analyzer
Student Name: Omkar Gaikwad
Roll No: 37
ER No: ADT23SOCB0679
========================================================================================
Workflow:
1. Upload multiple previous year question papers (PDF / TXT).
2. Extract text from papers using PyPDF.
3. LLM extracts and tags each question with topic, subtopic, marks & difficulty in JSON.
4. Pandas aggregates topic frequencies, marks weightage, and year-wise trends.
5. Interactive visualizations: Top topics bar chart, marks distribution & revision guide.
========================================================================================
"""

import os
import io
import json
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from analyzer_engine import (
    extract_text_from_file,
    detect_year_from_filename,
    build_analysis_prompt,
    call_gemini_api,
    compute_topic_analytics,
    BENCHMARK_TAGGED_DATA,
    HAS_GENAI,
)

# -----------------------------------------------------------------------------
# Page Configuration & Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="PYQ Analyzer | Roll No 37",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 28px;
        font-weight: 700;
    }
    .main-header p {
        color: #E0E7FF;
        margin-top: 6px;
        margin-bottom: 12px;
        font-size: 14px;
    }
    .badge-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }
    .badge {
        background: rgba(255, 255, 255, 0.2);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    .metric-val {
        font-size: 26px;
        font-weight: 700;
        color: #1E3A8A;
    }
    .metric-lbl {
        font-size: 13px;
        color: #64748B;
        margin-top: 4px;
    }
    .question-card {
        border-left: 4px solid #3B82F6;
        padding: 12px 16px;
        background: #F8FAFC;
        margin-bottom: 10px;
        border-radius: 0 8px 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Header Banner with Student Identification
# -----------------------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>📚 Previous Year Question Paper Analyzer</h1>
    <p>AI-Powered Syllabus Topic Extraction, Frequency Weightage & Examination Trend Analysis</p>
    <div class="badge-container">
        <span class="badge">👤 <b>Student:</b> Omkar Gaikwad</span>
        <span class="badge">🔢 <b>Roll No:</b> 37</span>
        <span class="badge">🎓 <b>ER No:</b> ADT23SOCB0679</span>
        <span class="badge">📌 <b>Problem Statement:</b> #37</span>
        <span class="badge">🤖 <b>Model:</b> Gemini 2.5 Flash / 1.5 Flash</span>
        <span class="badge">⚡ <b>Stack:</b> Streamlit • Pandas • PyPDF</span>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Sidebar Configuration
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ Configuration & Model")

# Mode Selection
run_mode = st.sidebar.radio(
    "Choose Execution Mode:",
    ["⚡ Benchmark Demo (Instant University Papers)", "🚀 Live Gemini LLM API (Analyze Uploads)"],
    index=0
)

api_key = ""
model_choice = "gemini-2.5-flash"

if "Live" in run_mode:
    # Check environment variable first
    default_key = os.environ.get("GEMINI_API_KEY", "")
    api_key = st.sidebar.text_input(
        "Enter Gemini API Key:",
        value=default_key,
        type="password",
        help="Get a free key from Google AI Studio (aistudio.google.com)"
    )
    model_choice = st.sidebar.selectbox(
        "Gemini Model:",
        ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
        index=0
    )
    if not api_key:
        st.sidebar.warning("⚠️ Enter an API key above, or switch to 'Benchmark Demo' mode for instant offline testing!")
else:
    st.sidebar.success("✅ Demo Mode Active: Using 3 pre-loaded university exam papers (DBMS 2022, 2023, 2024).")

st.sidebar.markdown("---")
st.sidebar.subheader("📁 Sample Question Papers")
st.sidebar.info("Sample papers included in `./sample_papers/`: \n- DBMS 2022 EndSem \n- DBMS 2023 EndSem \n- DBMS 2024 EndSem")

# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if "tagged_questions" not in st.session_state:
    st.session_state.tagged_questions = []
if "analyzed_papers_summary" not in st.session_state:
    st.session_state.analyzed_papers_summary = []

# Quick Load Demo Button
col_quick1, col_quick2 = st.columns([2, 1])
with col_quick1:
    st.write("Analyze multiple examination papers to identify **high-frequency topics**, **marks allocation**, and **exam recurrence patterns**.")
with col_quick2:
    if st.button("📂 Load Pre-parsed DBMS Sample Papers (3 Years)", use_container_width=True):
        st.session_state.tagged_questions = BENCHMARK_TAGGED_DATA
        st.success("Loaded 29 questions across 3 years of DBMS university exams!")

# -----------------------------------------------------------------------------
# File Upload Section
# -----------------------------------------------------------------------------
st.markdown("### 1. Upload Question Papers")
uploaded_files = st.file_uploader(
    "Upload 2 or more Question Papers (.pdf or .txt):",
    type=["pdf", "txt"],
    accept_multiple_files=True,
    help="Upload semester question papers across different years (e.g., 2022, 2023, 2024)"
)

# If files uploaded, show summary
if uploaded_files:
    st.write(f"📎 **{len(uploaded_files)} file(s) uploaded:** " + ", ".join([f.name for f in uploaded_files]))

# -----------------------------------------------------------------------------
# Run Analysis Action
# -----------------------------------------------------------------------------
col_btn1, col_btn2 = st.columns([1, 3])
with col_btn1:
    run_analysis_clicked = st.button("🔍 Run Topic Analysis", type="primary", use_container_width=True)

if run_analysis_clicked:
    if "Benchmark" in run_mode:
        # Load benchmark data directly
        st.session_state.tagged_questions = BENCHMARK_TAGGED_DATA
        st.toast("Analysis completed successfully using benchmark university dataset!", icon="✅")
    else:
        # Live LLM Mode
        if not api_key:
            st.error("❌ Please provide a Google Gemini API Key in the sidebar to run Live LLM Analysis.")
        elif not uploaded_files:
            st.warning("⚠️ Please upload at least one question paper or switch to Demo Mode.")
        else:
            all_extracted_questions = []
            progress_bar = st.progress(0)
            status_text = st.empty()

            for idx, file in enumerate(uploaded_files):
                status_text.text(f"Extracting text from {file.name} ({idx+1}/{len(uploaded_files)})...")
                raw_text = extract_text_from_file(file, file.name)

                if not raw_text or len(raw_text.strip()) < 20:
                    st.warning(f"Could not extract sufficient text from {file.name}. Skipping.")
                    continue

                status_text.text(f"Analyzing topics with {model_choice} for {file.name}...")
                prompt = build_analysis_prompt(file.name, raw_text)

                try:
                    tagged = call_gemini_api(api_key, prompt, model_name=model_choice)
                    all_extracted_questions.extend(tagged)
                except Exception as e:
                    st.error(f"Error analyzing {file.name}: {str(e)}")

                progress_bar.progress((idx + 1) / len(uploaded_files))

            status_text.text("Completed analysis!")
            if all_extracted_questions:
                st.session_state.tagged_questions = all_extracted_questions
                st.success(f"Successfully extracted and tagged {len(all_extracted_questions)} questions from {len(uploaded_files)} papers!")
            else:
                st.error("No questions could be extracted. Please check file format.")

# -----------------------------------------------------------------------------
# Results & Visualizations Section
# -----------------------------------------------------------------------------
if st.session_state.tagged_questions:
    df_questions = pd.DataFrame(st.session_state.tagged_questions)
    analytics = compute_topic_analytics(df_questions)
    topic_summary = analytics["topic_summary"]
    year_pivot = analytics["year_pivot"]

    st.markdown("---")
    st.markdown("### 2. Analysis Dashboard & Examination Insights")

    # Metrics Summary Row
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{analytics['total_papers']}</div>
            <div class="metric-lbl">Papers Analyzed</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{analytics['total_questions']}</div>
            <div class="metric-lbl">Total Questions</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{analytics['total_marks_all']}</div>
            <div class="metric-lbl">Total Marks Covered</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{len(topic_summary)}</div>
            <div class="metric-lbl">Syllabus Topics</div>
        </div>
        """, unsafe_allow_html=True)
    with m5:
        top_topic_name = topic_summary.iloc[0]['topic'] if not topic_summary.empty else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val" style="font-size:16px; padding-top:4px;">{top_topic_name[:20]}...</div>
            <div class="metric-lbl">#1 Most Frequent Topic</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # Visual Tabs
    tab_chart, tab_recurrence, tab_revision, tab_explorer, tab_export = st.tabs([
        "📊 Topic Frequency Chart",
        "📈 Year-Wise Recurrence",
        "🎯 High-Yield Revision Guide",
        "🔍 Question Explorer",
        "📥 Export Report & Data"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: Topic Frequency Chart (Main PS #37 Requirement)
    # -------------------------------------------------------------------------
    with tab_chart:
        st.subheader("Frequently Asked Topics Breakdown")
        st.write("Bar chart showing topics ranked by total number of questions asked across all uploaded examination papers:")

        col_c1, col_c2 = st.columns([3, 2])

        with col_c1:
            # Matplotlib horizontal bar chart with professional styling
            fig, ax = plt.subplots(figsize=(8, 4.8))
            plot_df = topic_summary.sort_values(by="question_count", ascending=True)
            bars = ax.barh(plot_df["topic"], plot_df["question_count"], color="#3B82F6", edgecolor="#1E3A8A", height=0.6)
            
            # Annotate bar counts
            for bar in bars:
                w = bar.get_width()
                ax.text(w + 0.1, bar.get_y() + bar.get_height()/2, f"{int(w)} Qs", 
                        ha='left', va='center', fontsize=9, fontweight='bold', color="#1E3A8A")

            ax.set_xlabel("Question Count (Frequency)", fontsize=11, fontweight='bold')
            ax.set_title("Top Syllabus Topics by Question Frequency", fontsize=12, fontweight='bold', color="#1E3A8A")
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(axis='x', linestyle='--', alpha=0.5)
            plt.tight_layout()
            st.pyplot(fig)

        with col_c2:
            st.write("#### 📋 Topic Frequency & Marks Table")
            st.dataframe(
                topic_summary.rename(columns={
                    "topic": "Syllabus Topic",
                    "question_count": "Questions",
                    "total_marks": "Total Marks",
                    "avg_marks_per_q": "Avg Marks/Q"
                }),
                use_container_width=True,
                hide_index=True
            )

        # Marks Weightage Distribution Chart
        st.markdown("#### 💰 Marks Weightage per Topic")
        fig2, ax2 = plt.subplots(figsize=(10, 3.5))
        plot_marks_df = topic_summary.sort_values(by="total_marks", ascending=False)
        ax2.bar(plot_marks_df["topic"], plot_marks_df["total_marks"], color="#10B981", edgecolor="#065F46", width=0.55)
        ax2.set_ylabel("Total Marks Allocated", fontsize=10, fontweight='bold')
        ax2.set_title("Total Marks Weightage across Uploaded Papers", fontsize=11, fontweight='bold')
        plt.xticks(rotation=30, ha='right', fontsize=9)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.grid(axis='y', linestyle='--', alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig2)

    # -------------------------------------------------------------------------
    # TAB 2: Year-Wise Recurrence Matrix
    # -------------------------------------------------------------------------
    with tab_recurrence:
        st.subheader("Year-over-Year Topic Recurrence Matrix")
        st.write("Identifies topics that recur consistently year after year versus one-off topics:")

        if not year_pivot.empty:
            st.dataframe(year_pivot, use_container_width=True, hide_index=True)

            # Highlight 100% recurring topics
            if "years_appeared" in year_pivot.columns and len(analytics["years_present"]) > 1:
                max_yrs = len(analytics["years_present"])
                recurring = year_pivot[year_pivot["years_appeared"] == max_yrs]
                st.success(f"🔥 **100% Guaranteed Recurring Topics** (Appeared in all {max_yrs} examination papers):")
                for _, r in recurring.iterrows():
                    st.markdown(f"- **{r['topic']}** (Consistently tested every year)")
        else:
            st.info("Upload papers with clear year labels to view multi-year recurrence.")

    # -------------------------------------------------------------------------
    # TAB 3: High-Yield Revision Guide
    # -------------------------------------------------------------------------
    with tab_revision:
        st.subheader("🎯 High-Yield Exam Preparation Blueprint")
        st.write("Optimized study priority list based on frequency count and marks weightage:")

        col_p1, col_p2 = st.columns(2)

        with col_p1:
            st.markdown("#### 🔴 Tier 1: High Priority (Must Master)")
            for item in analytics["top_must_study"][:3]:
                st.markdown(f"""
                <div class="question-card" style="border-left-color: #EF4444;">
                    <b>{item['topic']}</b><br>
                    <span>Frequency: <b>{item['question_count']} questions</b> | Marks Weightage: <b>{item['total_marks']} marks</b></span><br>
                    <small><i>Recommendation: Master all definitions, diagrams, and numerical problems for this topic.</i></small>
                </div>
                """, unsafe_allow_html=True)

        with col_p2:
            st.markdown("#### 🟡 Tier 2: Medium Priority (Core Scoring)")
            for item in analytics["top_must_study"][3:6]:
                st.markdown(f"""
                <div class="question-card" style="border-left-color: #F59E0B;">
                    <b>{item['topic']}</b><br>
                    <span>Frequency: <b>{item['question_count']} questions</b> | Marks Weightage: <b>{item['total_marks']} marks</b></span><br>
                    <small><i>Recommendation: Revise core concepts and standard short/long answer questions.</i></small>
                </div>
                """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TAB 4: Question Explorer
    # -------------------------------------------------------------------------
    with tab_explorer:
        st.subheader("🔍 Explore Tagged Questions")

        # Filters
        c_f1, c_f2, c_f3 = st.columns([2, 1, 1])
        with c_f1:
            selected_topic = st.selectbox(
                "Filter by Topic:",
                ["All Topics"] + list(topic_summary["topic"].unique())
            )
        with c_f2:
            diff_filter = st.selectbox("Difficulty:", ["All", "Easy", "Medium", "Hard"])
        with c_f3:
            search_kw = st.text_input("Keyword Search:", "")

        filtered_df = df_questions.copy()
        if selected_topic != "All Topics":
            filtered_df = filtered_df[filtered_df["topic"] == selected_topic]
        if diff_filter != "All":
            filtered_df = filtered_df[filtered_df["difficulty"] == diff_filter]
        if search_kw:
            filtered_df = filtered_df[filtered_df["question_text"].str.contains(search_kw, case=False, na=False)]

        st.write(f"Showing **{len(filtered_df)}** matching questions:")

        for _, row in filtered_df.iterrows():
            with st.expander(f"{row.get('paper', 'Paper')} | {row.get('question_no', 'Q')} - {row.get('topic')} ({row.get('marks', 5)} Marks)"):
                st.markdown(f"**Question:** {row.get('question_text')}")
                st.markdown(f"- **Subtopic:** `{row.get('subtopic', 'N/A')}`")
                st.markdown(f"- **Difficulty:** `{row.get('difficulty', 'Medium')}` | **Cognitive Level:** `{row.get('cognitive_level', 'Understand')}`")

    # -------------------------------------------------------------------------
    # TAB 5: Export Report & Data
    # -------------------------------------------------------------------------
    with tab_export:
        st.subheader("📥 Export Analysis Reports")
        st.write("Download data for viva presentation, assignment submission, or personal exam revision:")

        csv_questions = df_questions.to_csv(index=False).encode('utf-8')
        csv_summary = topic_summary.to_csv(index=False).encode('utf-8')
        json_questions = json.dumps(st.session_state.tagged_questions, indent=2).encode('utf-8')

        c_d1, c_d2, c_d3 = st.columns(3)
        with c_d1:
            st.download_button(
                label="📄 Download All Tagged Questions (CSV)",
                data=csv_questions,
                file_name="tagged_questions_analysis.csv",
                mime="text/csv",
                use_container_width=True
            )
        with c_d2:
            st.download_button(
                label="📊 Download Topic Summary (CSV)",
                data=csv_summary,
                file_name="topic_frequency_summary.csv",
                mime="text/csv",
                use_container_width=True
            )
        with c_d3:
            st.download_button(
                label="📦 Download Raw JSON Output",
                data=json_questions,
                file_name="tagged_questions.json",
                mime="application/json",
                use_container_width=True
            )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748B; font-size: 13px;'>"
    "GenAI Mini Project | Roll No: <b>37</b> | Name: <b>Omkar Gaikwad</b> | ER No: <b>ADT23SOCB0679</b>"
    "</div>",
    unsafe_allow_html=True
)
