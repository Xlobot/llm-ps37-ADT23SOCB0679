"""
Generates visual figures and screenshots for the PYQ Analyzer project.
Roll No: 37 | Omkar Gaikwad | ADT23SOCB0679
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd
from analyzer_engine import BENCHMARK_TAGGED_DATA, compute_topic_analytics

# Ensure screenshots directory exists
os.makedirs("screenshots", exist_ok=True)

df = pd.DataFrame(BENCHMARK_TAGGED_DATA)
analytics = compute_topic_analytics(df)
topic_summary = analytics["topic_summary"]
year_pivot = analytics["year_pivot"]

# -----------------------------------------------------------------------------
# 1. Topic Frequency Bar Chart
# -----------------------------------------------------------------------------
plt.figure(figsize=(9, 5), dpi=300)
plot_df = topic_summary.sort_values(by="question_count", ascending=True)
bars = plt.barh(plot_df["topic"], plot_df["question_count"], color="#2563EB", edgecolor="#1E3A8A", height=0.6)

for bar in bars:
    w = bar.get_width()
    plt.text(w + 0.1, bar.get_y() + bar.get_height()/2, f" {int(w)} Questions", 
             ha='left', va='center', fontsize=10, fontweight='bold', color="#1E3A8A")

plt.xlabel("Question Frequency across University Papers", fontsize=11, fontweight='bold')
plt.title("Top Frequently Asked Syllabus Topics (DBMS 2022-2024)\nStudent: Omkar Gaikwad | Roll: 37 | PS #37", 
          fontsize=12, fontweight='bold', color="#1E3A8A", pad=12)
plt.xlim(0, max(plot_df["question_count"]) + 1.2)
plt.grid(axis='x', linestyle='--', alpha=0.4)
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.tight_layout()
chart_path1 = os.path.join("screenshots", "01_topic_frequency_barchart.png")
plt.savefig(chart_path1, dpi=300)
plt.close()
print(f"Saved: {chart_path1}")

# -----------------------------------------------------------------------------
# 2. Marks Weightage Bar Chart
# -----------------------------------------------------------------------------
plt.figure(figsize=(10, 5), dpi=300)
plot_marks = topic_summary.sort_values(by="total_marks", ascending=False)
bars2 = plt.bar(plot_marks["topic"], plot_marks["total_marks"], color="#059669", edgecolor="#064E3B", width=0.55)

for bar in bars2:
    h = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, h + 0.5, f"{int(h)} M", 
             ha='center', va='bottom', fontsize=9, fontweight='bold', color="#064E3B")

plt.ylabel("Total Marks Allocated", fontsize=11, fontweight='bold')
plt.title("Examination Marks Weightage by Topic\nPrevious Year Question Paper Analyzer", 
          fontsize=12, fontweight='bold', color="#064E3B", pad=12)
plt.xticks(rotation=28, ha='right', fontsize=9)
plt.ylim(0, max(plot_marks["total_marks"]) + 4)
plt.grid(axis='y', linestyle='--', alpha=0.4)
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.tight_layout()
chart_path2 = os.path.join("screenshots", "02_marks_weightage_distribution.png")
plt.savefig(chart_path2, dpi=300)
plt.close()
print(f"Saved: {chart_path2}")

# -----------------------------------------------------------------------------
# 3. Year-over-Year Recurrence Heatmap / Matrix
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
ax.axis('tight')
ax.axis('off')

# Prepare clean table data
table_data = []
header = ["Topic Name", "2022", "2023", "2024", "Years Present", "Recurrence Status"]
table_data.append(header)

for _, r in year_pivot.iterrows():
    y22 = r.get("2022", 0)
    y23 = r.get("2023", 0)
    y24 = r.get("2024", 0)
    yrs = r.get("years_appeared", 0)
    status = "Guaranteed (100%)" if yrs == 3 else ("High (66%)" if yrs == 2 else "Occasional (33%)")
    table_data.append([r["topic"], f"{y22} Qs", f"{y23} Qs", f"{y24} Qs", f"{yrs}/3 Yrs", status])

table = ax.table(cellText=table_data, loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(8.5)
table.scale(1.2, 1.4)

# Format header & rows
for (row, col), cell in table.get_celld().items():
    if row == 0:
        cell.set_facecolor('#1E3A8A')
        cell.set_text_props(color='white', fontweight='bold')
    else:
        if "Guaranteed" in table_data[row][5]:
            cell.set_facecolor('#DCFCE7') # Light green
        elif row % 2 == 0:
            cell.set_facecolor('#F8FAFC')
        else:
            cell.set_facecolor('#FFFFFF')

plt.title("Year-Wise Topic Recurrence & Trend Matrix\nRoll No: 37 | Omkar Gaikwad", fontsize=11, fontweight='bold', pad=15)
plt.tight_layout()
chart_path3 = os.path.join("screenshots", "03_year_recurrence_matrix.png")
plt.savefig(chart_path3, dpi=300)
plt.close()
print(f"Saved: {chart_path3}")

# -----------------------------------------------------------------------------
# 4. Streamlit App Overview / Dashboard Visual Mockup
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
ax.axis('off')

# Create a clean infographic diagram summarizing the UI
plt.text(0.5, 0.92, "Previous Year Question Paper Analyzer - Application UI", 
         ha='center', va='center', fontsize=14, fontweight='bold', color='#1E3A8A')
plt.text(0.5, 0.85, "Student: Omkar Gaikwad | Roll No: 37 | ER No: ADT23SOCB0679 | Problem Statement #37", 
         ha='center', va='center', fontsize=10, color='#475569')

# Metric Boxes
metrics = [
    ("3 Papers", "Exam Papers Analyzed"),
    ("29 Questions", "Total Qs Extracted"),
    ("150 Marks", "Total Marks Covered"),
    ("8 Topics", "Core Syllabus Topics"),
    ("Architecture & ER", "#1 High Yield Topic")
]

for i, (val, lbl) in enumerate(metrics):
    x = 0.1 + i * 0.19
    rect = FancyBboxPatch((x - 0.08, 0.65), 0.16, 0.12, boxstyle="round,pad=0.01", facecolor='#F1F5F9', edgecolor='#CBD5E1')
    ax.add_patch(rect)
    plt.text(x, 0.73, val, ha='center', va='center', fontsize=11, fontweight='bold', color='#1E3A8A')
    plt.text(x, 0.68, lbl, ha='center', va='center', fontsize=7.5, color='#64748B')

# Feature highlights box
box_text = (
    "- Core Feature: Multi-paper PDF text extraction with PyPDF & automated Question Segmentation.\n"
    "- LLM Prompt Design: Google Gemini 2.5 Flash tags each question with Topic, Subtopic, Marks, & Difficulty in JSON.\n"
    "- Pandas Processing: Aggregates question frequency, total marks weightage, and computes multi-year recurrence.\n"
    "- Interactive Visualizations: High-resolution horizontal bar charts of frequently asked topics & marks distribution.\n"
    "- Examination Revision Strategy: Segregates syllabus into Tier 1 (Must-Study), Tier 2 (Core), and Tier 3 (Specialized).\n"
    "- Data Export: Complete export functionality for Tagged Questions (CSV/JSON) and Topic Frequency Summary (CSV)."
)
rect_features = FancyBboxPatch((0.05, 0.12), 0.9, 0.46, boxstyle="round,pad=0.02", facecolor='#EFF6FF', edgecolor='#3B82F6')
ax.add_patch(rect_features)
plt.text(0.08, 0.52, "KEY IMPLEMENTATION FEATURES & ARCHITECTURE", fontsize=11, fontweight='bold', color='#1E3A8A')
plt.text(0.08, 0.31, box_text.strip(), fontsize=9, color='#1E293B', linespacing=1.6)

plt.tight_layout()
chart_path4 = os.path.join("screenshots", "04_dashboard_overview.png")
plt.savefig(chart_path4, dpi=300)
plt.close()
print(f"Saved: {chart_path4}")
