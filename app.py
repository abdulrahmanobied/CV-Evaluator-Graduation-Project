"""
===========================================
 AI Candidate Evaluation System
 Main Application - Streamlit UI
===========================================
"""

import streamlit as st
import pandas as pd
from cv_parser import read_pdf
from cv_extractor import extract_all
from job_matcher import calculate_skill_score, calculate_experience_score, calculate_education_score
from semantic_matcher import calculate_semantic_skill_score
from database import init_db, save_result
from vector_store import add_candidate_to_vector_store, search_candidates_semantic

# ==========================================
# Page Configuration
# ==========================================
init_db()

st.set_page_config(
    page_title="AI Candidate Evaluator",
    page_icon="🤖",
    layout="wide"
)

# ==========================================
# Header
# ==========================================
st.title("🤖 AI Candidate Evaluation System")
st.markdown("Upload multiple CVs and define job requirements to find the best candidate.")
st.divider()

# ==========================================
# Sidebar - Job Requirements Input
# ==========================================
st.sidebar.header("📋 Job Requirements")

job_title = st.sidebar.text_input("Job Title", placeholder="e.g. AI Engineer")

required_skills_input = st.sidebar.text_area(
    "Required Skills (comma separated)",
    placeholder="e.g. python, machine learning, sql"
)

preferred_skills_input = st.sidebar.text_area(
    "Preferred Skills (comma separated)",
    placeholder="e.g. docker, git, aws"
)

min_experience = st.sidebar.number_input(
    "Minimum Years of Experience",
    min_value=0,
    max_value=20,
    value=2
)

education_required = st.sidebar.multiselect(
    "Required Education Level",
    ["Bachelor's", "Master's", "PhD", "Diploma"],
    default=["Bachelor's", "Master's", "PhD"]
)

st.sidebar.divider()

use_smart_matching = st.sidebar.checkbox(
    "🧠 Use Smart AI Matching",
    value=False,
    help='Understands meaning, not just exact text. E.g. "ML" will match "Machine Learning".'
)

st.sidebar.divider()

# ==========================================
# Main Area - Upload CVs
# ==========================================
st.header("📂 Upload Candidate CVs")

uploaded_files = st.file_uploader(
    "Upload PDF files (you can select multiple)",
    type=["pdf"],
    accept_multiple_files=True
)

# ==========================================
# Process & Evaluate
# ==========================================
if st.button("🚀 Evaluate Candidates", type="primary"):

    # Validate inputs
    if not job_title:
        st.error("❌ Please enter a job title.")
    elif not required_skills_input:
        st.error("❌ Please enter at least one required skill.")
    elif not uploaded_files:
        st.error("❌ Please upload at least one CV.")
    else:
        # Parse skills input
        required_skills  = [s.strip().lower() for s in required_skills_input.split(",") if s.strip()]
        preferred_skills = [s.strip().lower() for s in preferred_skills_input.split(",") if s.strip()]

        results = []

        spinner_text = "🧠 Analyzing CVs with Smart AI Matching..." if use_smart_matching else "🔍 Analyzing CVs..."

        with st.spinner(spinner_text):
            for file in uploaded_files:
                # Save uploaded file temporarily
                temp_path = f"temp_{file.name}"
                with open(temp_path, "wb") as f:
                    f.write(file.read())

                # Extract text from PDF
                cv_text = read_pdf(temp_path)

                if cv_text:
                    # Extract candidate info
                    candidate = extract_all(cv_text)

                    # Calculate skill score using the chosen method
                    if use_smart_matching:
                        skill_score, matched_required, matched_preferred, match_details = calculate_semantic_skill_score(
                            candidate["skills"], required_skills, preferred_skills
                        )
                    else:
                        skill_score, matched_required, matched_preferred = calculate_skill_score(
                            candidate["skills"], required_skills, preferred_skills
                        )
                        match_details = None

                    experience_score = calculate_experience_score(
                        candidate["experience_years"], min_experience
                    )
                    education_score = calculate_education_score(
                        candidate["education"], education_required
                    )

                    # Final weighted score
                    final_score = round(
                        (skill_score * 0.60) +
                        (experience_score * 0.30) +
                        (education_score * 0.10), 2
                    )

                    # Suitability level
                    if final_score >= 75:
                        suitability = "🟢 Highly Suitable"
                    elif final_score >= 50:
                        suitability = "🟡 Moderately Suitable"
                    else:
                        suitability = "🔴 Not Suitable"

                    missing_skills = [s for s in required_skills if s not in matched_required]

                    results.append({
                        "File":             file.name,
                        "Name":             candidate["name"] or "Unknown",
                        "Email":            candidate["email"] or "N/A",
                        "Education":        candidate["education"],
                        "Experience (yrs)": candidate["experience_years"],
                        "Matched Skills":   ", ".join(matched_required),
                        "Missing Skills":   ", ".join(missing_skills),
                        "Skill Score":      f"{skill_score}%",
                        "Exp Score":        f"{experience_score}%",
                        "Final Score":      final_score,
                        "Suitability":      suitability,
                        "Match Details":    match_details,
                    })

                    # Save this candidate's result into the SQL database
                    row_id = save_result({
                        "candidate_name": candidate["name"] or "Unknown",
                        "candidate_email": candidate["email"] or "N/A",
                        "job_title": job_title,
                        "skill_score": skill_score,
                        "experience_score": experience_score,
                        "education_score": education_score,
                        "final_score": final_score,
                        "suitability": suitability,
                        "matched_required": matched_required,
                        "missing_skills": missing_skills,
                    })

                    # Also save this candidate's profile into the Vector DB for semantic search
                    add_candidate_to_vector_store(
                        candidate_id=f"{candidate['email'] or file.name}",
                        name=candidate["name"] or "Unknown",
                        email=candidate["email"] or "N/A",
                        skills=candidate["skills"],
                        summary_text=f"{job_title} candidate with {candidate['experience_years']} years experience, {candidate['education']} education"
                    )

                # Clean up temp file
                import os
                os.remove(temp_path)

        # ==========================================
        # Display Results
        # ==========================================
        if results:
            # Sort by final score
            results_sorted = sorted(results, key=lambda x: x["Final Score"], reverse=True)

            st.divider()
            st.header("🏆 Ranking Results")

            if use_smart_matching:
                st.info("🧠 Smart AI Matching was used — skills are matched by meaning, not just exact text.")

            # Top candidate highlight
            best = results_sorted[0]
            st.success(f"🥇 Best Candidate: **{best['Name']}** — Score: **{best['Final Score']}%**")

            # Results table (drop the raw match_details column from the table view)
            st.subheader("📊 All Candidates")
            df = pd.DataFrame(results_sorted).drop(columns=["Match Details"])
            st.dataframe(df, use_container_width=True)

            # Detailed cards
            st.subheader("📋 Detailed Reports")
            for i, r in enumerate(results_sorted):
                with st.expander(f"#{i+1} — {r['Name']} ({r['Final Score']}%) — {r['Suitability']}"):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Final Score",  f"{r['Final Score']}%")
                    col2.metric("Skill Score",  r['Skill Score'])
                    col3.metric("Exp Score",    r['Exp Score'])

                    st.write(f"📧 **Email:** {r['Email']}")
                    st.write(f"🎓 **Education:** {r['Education']}")
                    st.write(f"💼 **Experience:** {r['Experience (yrs)']} years")
                    st.write(f"✅ **Matched Skills:** {r['Matched Skills'] or 'None'}")
                    st.write(f"❌ **Missing Skills:** {r['Missing Skills'] or 'None'}")

                    if r["Match Details"]:
                        st.write("🔍 **AI Match Details:**")
                        for d in r["Match Details"]:
                            st.write(f"   - {d}")
        else:
            st.error("❌ Could not process any of the uploaded CVs.")

# ==========================================
# Semantic Candidate Search (Vector DB)
# ==========================================
st.divider()
st.header("🔍 Semantic Candidate Search")
st.markdown(
    "Search all previously evaluated candidates by **meaning**, not just exact keywords. "
    "E.g. try *\"someone with AI and neural network experience\"*."
)

search_query = st.text_input(
    "Describe the candidate you're looking for",
    placeholder="e.g. someone experienced in databases and backend development"
)

if st.button("🔎 Search Candidates"):
    if not search_query:
        st.error("❌ Please enter a search description.")
    else:
        matches = search_candidates_semantic(search_query, n_results=5)
        if not matches:
            st.warning("📭 No candidates found. Evaluate some candidates first.")
        else:
            st.subheader("Closest Matches")
            for i, m in enumerate(matches, 1):
                st.write(f"**#{i} — {m['name']}** (semantic distance: {m['distance']})")
                st.write(f"   📧 {m['email']}")
                st.write(f"   🛠️ Skills: {m['skills']}")
                st.write("---")