"""
Analyzer Engine for Previous Year Question Paper Analyzer (PS #37)
Roll No: 37 | Omkar Gaikwad | ADT23SOCB0679
"""

import os
import re
import json
import io
import pandas as pd
from typing import List, Dict, Any, Optional
import pypdf

# Try to import Google GenAI SDK
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# Default Pre-tagged Benchmark Data for Instant Demo / Fallback
BENCHMARK_TAGGED_DATA = [
    # 2022
    {
        "paper": "DBMS_2022_EndSem",
        "year": "2022",
        "question_no": "Q1.(a)",
        "question_text": "Define DBMS. Compare File Processing System with Database Management System.",
        "topic": "Architecture & Data Independence",
        "subtopic": "DBMS vs File System",
        "marks": 5,
        "difficulty": "Easy",
        "cognitive_level": "Understand",
        "repetition_weight": 8
    },
    {
        "paper": "DBMS_2022_EndSem",
        "year": "2022",
        "question_no": "Q1.(b)",
        "question_text": "Explain the Three-Schema Architecture of DBMS with a neat diagram.",
        "topic": "Architecture & Data Independence",
        "subtopic": "Three-Schema Architecture",
        "marks": 5,
        "difficulty": "Medium",
        "cognitive_level": "Understand",
        "repetition_weight": 9
    },
    {
        "paper": "DBMS_2022_EndSem",
        "year": "2022",
        "question_no": "Q2.(a)",
        "question_text": "What is an Entity-Relationship (ER) model? Draw an ER diagram for a University Management System.",
        "topic": "ER Modeling & Schema Design",
        "subtopic": "ER Diagram Design",
        "marks": 6,
        "difficulty": "Medium",
        "cognitive_level": "Apply",
        "repetition_weight": 10
    },
    {
        "paper": "DBMS_2022_EndSem",
        "year": "2022",
        "question_no": "Q2.(b)",
        "question_text": "Explain Primary Key, Candidate Key, Foreign Key, and Super Key with examples.",
        "topic": "ER Modeling & Schema Design",
        "subtopic": "Relational Keys",
        "marks": 4,
        "difficulty": "Easy",
        "cognitive_level": "Remember",
        "repetition_weight": 7
    },
    {
        "paper": "DBMS_2022_EndSem",
        "year": "2022",
        "question_no": "Q3.(a)",
        "question_text": "What is Relational Algebra? Explain Selection, Projection, Union, and Cartesian Product operations.",
        "topic": "Relational Algebra & SQL",
        "subtopic": "Relational Algebra Operators",
        "marks": 6,
        "difficulty": "Medium",
        "cognitive_level": "Understand",
        "repetition_weight": 6
    },
    {
        "paper": "DBMS_2022_EndSem",
        "year": "2022",
        "question_no": "Q3.(b)",
        "question_text": "Explain First Normal Form (1NF), Second Normal Form (2NF), and Third Normal Form (3NF) with sample relations.",
        "topic": "Normalization & Functional Dependencies",
        "subtopic": "1NF, 2NF, 3NF Normalization",
        "marks": 6,
        "difficulty": "Hard",
        "cognitive_level": "Apply",
        "repetition_weight": 10
    },
    {
        "paper": "DBMS_2022_EndSem",
        "year": "2022",
        "question_no": "Q4.(a)",
        "question_text": "Explain ACID properties of transactions with suitable real-world banking examples.",
        "topic": "Transaction Management & ACID",
        "subtopic": "ACID Properties",
        "marks": 6,
        "difficulty": "Medium",
        "cognitive_level": "Understand",
        "repetition_weight": 10
    },
    {
        "paper": "DBMS_2022_EndSem",
        "year": "2022",
        "question_no": "Q4.(b)",
        "question_text": "What is Concurrency Control? Explain Two-Phase Locking (2PL) protocol.",
        "topic": "Concurrency Control & Deadlocks",
        "subtopic": "Two-Phase Locking (2PL)",
        "marks": 6,
        "difficulty": "Hard",
        "cognitive_level": "Analyze",
        "repetition_weight": 9
    },
    {
        "paper": "DBMS_2022_EndSem",
        "year": "2022",
        "question_no": "Q5.(a)",
        "question_text": "What is Indexing in databases? Differentiate between Primary Index, Secondary Index, and Clustering Index.",
        "topic": "Indexing & Storage Structures",
        "subtopic": "Primary vs Secondary Indexing",
        "marks": 6,
        "difficulty": "Medium",
        "cognitive_level": "Understand",
        "repetition_weight": 8
    },

    # 2023
    {
        "paper": "DBMS_2023_EndSem",
        "year": "2023",
        "question_no": "Q1.(a)",
        "question_text": "Discuss the advantages of DBMS over traditional file-oriented systems. Explain Data Independence (Logical and Physical).",
        "topic": "Architecture & Data Independence",
        "subtopic": "Data Independence",
        "marks": 6,
        "difficulty": "Medium",
        "cognitive_level": "Understand",
        "repetition_weight": 9
    },
    {
        "paper": "DBMS_2023_EndSem",
        "year": "2023",
        "question_no": "Q1.(b)",
        "question_text": "Explain the role of Database Administrator (DBA) in database architecture.",
        "topic": "Architecture & Data Independence",
        "subtopic": "Role of DBA",
        "marks": 4,
        "difficulty": "Easy",
        "cognitive_level": "Remember",
        "repetition_weight": 5
    },
    {
        "paper": "DBMS_2023_EndSem",
        "year": "2023",
        "question_no": "Q2.(a)",
        "question_text": "Design an ER diagram for a Hospital Management System with entities: Doctor, Patient, and Appointment.",
        "topic": "ER Modeling & Schema Design",
        "subtopic": "ER Diagram Design",
        "marks": 6,
        "difficulty": "Medium",
        "cognitive_level": "Apply",
        "repetition_weight": 10
    },
    {
        "paper": "DBMS_2023_EndSem",
        "year": "2023",
        "question_no": "Q2.(b)",
        "question_text": "Convert an ER diagram construct containing weak entity sets into relational schema.",
        "topic": "ER Modeling & Schema Design",
        "subtopic": "Weak Entity Sets Conversion",
        "marks": 4,
        "difficulty": "Hard",
        "cognitive_level": "Apply",
        "repetition_weight": 7
    },
    {
        "paper": "DBMS_2023_EndSem",
        "year": "2023",
        "question_no": "Q3.(a)",
        "question_text": "Define Functional Dependency. State Armstrong's Axioms.",
        "topic": "Normalization & Functional Dependencies",
        "subtopic": "Functional Dependencies & Armstrong Axioms",
        "marks": 4,
        "difficulty": "Medium",
        "cognitive_level": "Remember",
        "repetition_weight": 7
    },
    {
        "paper": "DBMS_2023_EndSem",
        "year": "2023",
        "question_no": "Q3.(b)",
        "question_text": "What is Normalization? Explain BCNF (Boyce-Codd Normal Form) and compare it with 3NF.",
        "topic": "Normalization & Functional Dependencies",
        "subtopic": "BCNF vs 3NF",
        "marks": 6,
        "difficulty": "Hard",
        "cognitive_level": "Analyze",
        "repetition_weight": 10
    },
    {
        "paper": "DBMS_2023_EndSem",
        "year": "2023",
        "question_no": "Q4.(a)",
        "question_text": "What is a Schedule? Differentiate between Conflict Serializable and View Serializable schedules.",
        "topic": "Concurrency Control & Deadlocks",
        "subtopic": "Conflict vs View Serializability",
        "marks": 6,
        "difficulty": "Hard",
        "cognitive_level": "Analyze",
        "repetition_weight": 8
    },
    {
        "paper": "DBMS_2023_EndSem",
        "year": "2023",
        "question_no": "Q4.(b)",
        "question_text": "State and explain the ACID properties of database transactions. Why is Durability important?",
        "topic": "Transaction Management & ACID",
        "subtopic": "ACID Properties",
        "marks": 6,
        "difficulty": "Medium",
        "cognitive_level": "Understand",
        "repetition_weight": 10
    },
    {
        "paper": "DBMS_2023_EndSem",
        "year": "2023",
        "question_no": "Q5.(a)",
        "question_text": "Explain Log-Based Recovery techniques (Immediate Database Modification vs Deferred Modification).",
        "topic": "Recovery Systems",
        "subtopic": "Log-Based Recovery",
        "marks": 5,
        "difficulty": "Hard",
        "cognitive_level": "Analyze",
        "repetition_weight": 7
    },
    {
        "paper": "DBMS_2023_EndSem",
        "year": "2023",
        "question_no": "Q5.(b)",
        "question_text": "What are B-Trees and B+ Trees? Compare their structure and usage in database indexing.",
        "topic": "Indexing & Storage Structures",
        "subtopic": "B-Tree and B+ Tree Indexing",
        "marks": 5,
        "difficulty": "Medium",
        "cognitive_level": "Understand",
        "repetition_weight": 9
    },

    # 2024
    {
        "paper": "DBMS_2024_EndSem",
        "year": "2024",
        "question_no": "Q1.(a)",
        "question_text": "Explain 3-tier DBMS architecture and describe Physical vs Logical Data Independence.",
        "topic": "Architecture & Data Independence",
        "subtopic": "Three-Schema Architecture",
        "marks": 5,
        "difficulty": "Medium",
        "cognitive_level": "Understand",
        "repetition_weight": 9
    },
    {
        "paper": "DBMS_2024_EndSem",
        "year": "2024",
        "question_no": "Q1.(b)",
        "question_text": "Explain different types of database users and functions of query processor.",
        "topic": "Architecture & Data Independence",
        "subtopic": "Database Users & Query Processor",
        "marks": 5,
        "difficulty": "Easy",
        "cognitive_level": "Remember",
        "repetition_weight": 6
    },
    {
        "paper": "DBMS_2024_EndSem",
        "year": "2024",
        "question_no": "Q2.(a)",
        "question_text": "Draw an ER Diagram for an E-Commerce Online Shopping System showing entities, attributes, and relationships.",
        "topic": "ER Modeling & Schema Design",
        "subtopic": "ER Diagram Design",
        "marks": 6,
        "difficulty": "Medium",
        "cognitive_level": "Apply",
        "repetition_weight": 10
    },
    {
        "paper": "DBMS_2024_EndSem",
        "year": "2024",
        "question_no": "Q2.(b)",
        "question_text": "Explain aggregation and generalization concepts in Enhanced ER (EER) modeling.",
        "topic": "ER Modeling & Schema Design",
        "subtopic": "Enhanced ER Modeling",
        "marks": 4,
        "difficulty": "Hard",
        "cognitive_level": "Understand",
        "repetition_weight": 7
    },
    {
        "paper": "DBMS_2024_EndSem",
        "year": "2024",
        "question_no": "Q3.(a)",
        "question_text": "What are anomalies in database design? Explain insertion, deletion, and update anomalies with examples.",
        "topic": "Normalization & Functional Dependencies",
        "subtopic": "Design Anomalies",
        "marks": 5,
        "difficulty": "Medium",
        "cognitive_level": "Understand",
        "repetition_weight": 8
    },
    {
        "paper": "DBMS_2024_EndSem",
        "year": "2024",
        "question_no": "Q3.(b)",
        "question_text": "Decompose a given relation into 3NF and BCNF. Explain Lossless Join Decomposition.",
        "topic": "Normalization & Functional Dependencies",
        "subtopic": "Decomposition into 3NF and BCNF",
        "marks": 6,
        "difficulty": "Hard",
        "cognitive_level": "Apply",
        "repetition_weight": 10
    },
    {
        "paper": "DBMS_2024_EndSem",
        "year": "2024",
        "question_no": "Q4.(a)",
        "question_text": "Explain ACID properties. Describe the states of a transaction using a transaction state diagram.",
        "topic": "Transaction Management & ACID",
        "subtopic": "ACID Properties & State Diagram",
        "marks": 6,
        "difficulty": "Medium",
        "cognitive_level": "Understand",
        "repetition_weight": 10
    },
    {
        "paper": "DBMS_2024_EndSem",
        "year": "2024",
        "question_no": "Q4.(b)",
        "question_text": "Describe Deadlock handling in Concurrency Control: Deadlock Detection, Prevention (Wait-Die & Wound-Wait), and Recovery.",
        "topic": "Concurrency Control & Deadlocks",
        "subtopic": "Deadlock Handling",
        "marks": 6,
        "difficulty": "Hard",
        "cognitive_level": "Analyze",
        "repetition_weight": 9
    },
    {
        "paper": "DBMS_2024_EndSem",
        "year": "2024",
        "question_no": "Q5.(a)",
        "question_text": "Compare B+ Tree index with Hashing technique for query retrieval efficiency.",
        "topic": "Indexing & Storage Structures",
        "subtopic": "B+ Tree vs Hashing",
        "marks": 5,
        "difficulty": "Medium",
        "cognitive_level": "Analyze",
        "repetition_weight": 8
    },
    {
        "paper": "DBMS_2024_EndSem",
        "year": "2024",
        "question_no": "Q5.(b)",
        "question_text": "Write short notes on: (i) Write-Ahead Logging (WAL) (ii) Checkpoints in recovery.",
        "topic": "Recovery Systems",
        "subtopic": "WAL & Checkpoints",
        "marks": 5,
        "difficulty": "Medium",
        "cognitive_level": "Remember",
        "repetition_weight": 7
    }
]


def extract_text_from_file(file_obj_or_path, filename: str) -> str:
    """Extract raw text from PDF or TXT file."""
    if filename.lower().endswith(".txt"):
        if isinstance(file_obj_or_path, str):
            with open(file_obj_or_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        else:
            return file_obj_or_path.read().decode("utf-8", errors="ignore")

    elif filename.lower().endswith(".pdf"):
        text = ""
        try:
            reader = pypdf.PdfReader(file_obj_or_path)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        except Exception as e:
            text = f"[Error reading PDF: {str(e)}]"
        return text

    return ""


def detect_year_from_filename(filename: str) -> str:
    """Detect academic year from filename (e.g. 2022, 2023, 2024)."""
    match = re.search(r"(20\d\d)", filename)
    if match:
        return match.group(1)
    return "Recent"


def build_analysis_prompt(paper_name: str, raw_text: str) -> str:
    """
    Constructs the prompt for the LLM to extract questions and tag topics as structured JSON.
    PS #37 requirement: 'LLM tags each question with a topic as JSON'.
    """
    prompt = f"""You are an expert Academic Examination and Curriculum Analysis AI.
Analyze the following university question paper and extract every individual question.
For each question, accurately tag it with its primary academic topic, subtopic, marks, difficulty, and cognitive level.

QUESTION PAPER NAME: {paper_name}

RAW TEXT:
\"\"\"
{raw_text}
\"\"\"

Return ONLY a valid JSON array of objects with the exact schema below:
[
  {{
    "paper": "{paper_name}",
    "year": "Year extracted from text or filename (e.g., 2024)",
    "question_no": "Question number (e.g., Q1(a), Q2)",
    "question_text": "Full concise question text",
    "topic": "Standard Core Syllabus Topic Name (e.g., Normalization & Functional Dependencies, Transaction Management & ACID, ER Modeling & Schema Design, Concurrency Control & Deadlocks, Architecture & Data Independence, Indexing & Storage Structures, Relational Algebra & SQL, Recovery Systems)",
    "subtopic": "Specific subtopic or concept",
    "marks": integer marks (e.g. 5, 6; default 5 if not indicated),
    "difficulty": "Easy" or "Medium" or "Hard",
    "cognitive_level": "Remember" or "Understand" or "Apply" or "Analyze",
    "repetition_weight": integer 1-10 (estimation of how standard/essential this is in university exams)
  }}
]

Important rules:
1. Normalize topic names consistently so questions covering the same core subject use identical topic names.
2. Return ONLY the raw JSON array. Do not include markdown preamble or conversational text.
"""
    return prompt


def call_gemini_api(api_key: str, prompt: str, model_name: str = "gemini-2.5-flash") -> List[Dict[str, Any]]:
    """Call Google Gemini API via official google-genai SDK or direct REST fallback."""
    if not api_key:
        raise ValueError("Gemini API Key is required.")

    # 1. Try google-genai SDK
    if HAS_GENAI:
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                )
            )
            raw_output = response.text
            return parse_json_output(raw_output)
        except Exception as e:
            # Fall back to requests REST API
            print(f"SDK call failed ({e}), trying REST fallback...")

    # 2. REST API Fallback
    import requests
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }
    res = requests.post(url, headers=headers, json=payload, timeout=60)
    if res.status_code != 200:
        raise RuntimeError(f"Gemini API returned error {res.status_code}: {res.text}")

    data = res.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError("No response candidate returned by Gemini API.")
    raw_text = candidates[0]["content"]["parts"][0]["text"]
    return parse_json_output(raw_text)


def parse_json_output(text: str) -> List[Dict[str, Any]]:
    """Clean markdown code blocks and parse raw JSON string safely."""
    clean = text.strip()
    # Strip markdown backticks
    if clean.startswith("```json"):
        clean = clean[7:]
    elif clean.startswith("```"):
        clean = clean[3:]
    if clean.endswith("```"):
        clean = clean[:-3]
    clean = clean.strip()

    parsed = json.loads(clean)
    if isinstance(parsed, dict) and "questions" in parsed:
        parsed = parsed["questions"]
    if not isinstance(parsed, list):
        raise ValueError("Expected a JSON list of questions.")
    return parsed


def compute_topic_analytics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Use pandas to calculate topic counts, marks weightage, and trends.
    PS #37 requirement: 'count with pandas -> show a bar chart of top topics.'
    """
    if df.empty:
        return {}

    # 1. Topic frequency count
    topic_counts = df["topic"].value_counts().reset_index()
    topic_counts.columns = ["topic", "question_count"]

    # 2. Total marks per topic
    topic_marks = df.groupby("topic")["marks"].sum().reset_index()
    topic_marks.columns = ["topic", "total_marks"]

    # Merge counts and marks
    topic_summary = pd.merge(topic_counts, topic_marks, on="topic")
    topic_summary["avg_marks_per_q"] = (topic_summary["total_marks"] / topic_summary["question_count"]).round(1)
    topic_summary = topic_summary.sort_values(by=["question_count", "total_marks"], ascending=[False, False])

    # 3. Year-wise topic recurrence
    if "year" in df.columns:
        year_pivot = pd.crosstab(df["topic"], df["year"])
        years_present = [col for col in year_pivot.columns]
        year_pivot["years_appeared"] = (year_pivot > 0).sum(axis=1)
        year_pivot = year_pivot.reset_index()
    else:
        year_pivot = pd.DataFrame()
        years_present = []

    # 4. Difficulty breakdown
    diff_counts = df["difficulty"].value_counts().to_dict()

    # 5. High-Yield Must-Study Topics (High frequency & high marks)
    top_must_study = topic_summary.head(5).to_dict(orient="records")

    return {
        "topic_summary": topic_summary,
        "year_pivot": year_pivot,
        "years_present": years_present,
        "difficulty_counts": diff_counts,
        "top_must_study": top_must_study,
        "total_questions": len(df),
        "total_papers": df["paper"].nunique() if "paper" in df.columns else 1,
        "total_marks_all": int(df["marks"].sum()) if "marks" in df.columns else 0
    }
