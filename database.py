"""
===========================================
 Database
 Stores candidate evaluation results using SQLite
 so results persist between runs
===========================================
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "candidates.db")


def init_db():
    """Create the candidates table if it doesn't exist yet"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            job_title TEXT,
            skill_score REAL,
            experience_score REAL,
            education_score REAL,
            final_score REAL,
            suitability TEXT,
            matched_skills TEXT,
            missing_skills TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_result(report):
    """Save one candidate's evaluation report into the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO candidates (
            name, email, job_title, skill_score, experience_score,
            education_score, final_score, suitability,
            matched_skills, missing_skills, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        report.get("candidate_name"),
        report.get("candidate_email"),
        report.get("job_title"),
        report.get("skill_score"),
        report.get("experience_score"),
        report.get("education_score"),
        report.get("final_score"),
        report.get("suitability"),
        ", ".join(report.get("matched_required", [])),
        ", ".join(report.get("missing_skills", [])),
        datetime.now().isoformat(timespec="seconds"),
    ))
    conn.commit()
    conn.close()


def get_all_results():
    """Fetch all saved candidate results, most recent first"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates ORDER BY id DESC")
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]


def clear_all_results():
    """Delete all saved results (useful for testing)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidates")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    print("=" * 50)
    print("  Database - Test Run")
    print("=" * 50)

    init_db()
    print("✅ Database initialized (candidates.db created)")

    sample_report = {
        "candidate_name": "John Smith",
        "candidate_email": "john.smith@email.com",
        "job_title": "AI & Data Science Engineer",
        "skill_score": 61.94,
        "experience_score": 100,
        "education_score": 100,
        "final_score": 77.16,
        "suitability": "🟢 Highly Suitable",
        "matched_required": ["python", "sql"],
        "missing_skills": ["pytorch"],
    }
    save_result(sample_report)
    print("✅ Sample result saved")

    print("\n📋 All saved results:")
    for row in get_all_results():
        print(row)
    print("=" * 50)