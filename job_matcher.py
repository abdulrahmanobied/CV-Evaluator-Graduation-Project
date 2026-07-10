"""
===========================================
 Job Matcher
 Compares extracted CV data with job requirements
 and returns a match score (0 - 100%)
===========================================
"""

from cv_extractor import extract_all


def define_job_requirements():
    """
    Define the job requirements for the position
    This is what we compare each CV against
    """
    job = {
        "title": "AI & Data Science Engineer",
        "required_skills": [
            "python", "machine learning", "deep learning",
            "sql", "tensorflow", "pytorch", "nlp", "pandas", "numpy"
        ],
        "preferred_skills": [
            "docker", "git", "scikit-learn", "data analysis",
            "computer vision", "aws", "flask", "django"
        ],
        "min_experience_years": 2,
        "required_education": ["Bachelor's", "Master's", "PhD"],
    }
    return job


def calculate_skill_score(candidate_skills, required_skills, preferred_skills):
    """
    Calculate skill match score
    - Required skills = 70% of score
    - Preferred skills = 30% of score
    """
    # Required skills score
    if required_skills:
        required_matches = [s for s in required_skills if s in candidate_skills]
        required_score = len(required_matches) / len(required_skills) * 70
    else:
        required_score = 70

    # Preferred skills score
    if preferred_skills:
        preferred_matches = [s for s in preferred_skills if s in candidate_skills]
        preferred_score = len(preferred_matches) / len(preferred_skills) * 30
    else:
        preferred_score = 30

    return round(required_score + preferred_score, 2), required_matches, preferred_matches


def calculate_experience_score(candidate_years, required_years):
    """
    Calculate experience score out of 100
    """
    if candidate_years >= required_years:
        return 100
    elif candidate_years == 0:
        return 0
    else:
        return round((candidate_years / required_years) * 100, 2)


def calculate_education_score(candidate_education, required_education):
    """
    Calculate education score
    """
    if candidate_education in required_education:
        return 100
    else:
        return 50  # Partial credit


def match_cv_to_job(cv_text):
    """
    Main function - takes CV text and returns full match report
    """
    # Step 1: Extract CV info
    candidate = extract_all(cv_text)

    # Step 2: Get job requirements
    job = define_job_requirements()

    # Step 3: Calculate individual scores
    skill_score, required_matches, preferred_matches = calculate_skill_score(
        candidate["skills"],
        job["required_skills"],
        job["preferred_skills"]
    )

    experience_score = calculate_experience_score(
        candidate["experience_years"],
        job["min_experience_years"]
    )

    education_score = calculate_education_score(
        candidate["education"],
        job["required_education"]
    )

    # Step 4: Calculate final score (weighted average)
    # Skills = 60%, Experience = 30%, Education = 10%
    final_score = round(
        (skill_score * 0.60) +
        (experience_score * 0.30) +
        (education_score * 0.10),
        2
    )

    # Step 5: Determine suitability level
    if final_score >= 75:
        level = "🟢 Highly Suitable"
    elif final_score >= 50:
        level = "🟡 Moderately Suitable"
    else:
        level = "🔴 Not Suitable"

    # Step 6: Build report
    report = {
        "candidate_name":       candidate["name"],
        "candidate_email":      candidate["email"],
        "job_title":            job["title"],
        "final_score":          final_score,
        "suitability":          level,
        "skill_score":          skill_score,
        "experience_score":     experience_score,
        "education_score":      education_score,
        "matched_required":     required_matches,
        "matched_preferred":    preferred_matches,
        "missing_skills":       [s for s in job["required_skills"] if s not in candidate["skills"]],
    }

    return report


def print_report(report):
    """Print the match report in a clean format"""
    print("\n" + "=" * 55)
    print("           CANDIDATE MATCH REPORT")
    print("=" * 55)
    print(f"  Candidate:    {report['candidate_name']}")
    print(f"  Email:        {report['candidate_email']}")
    print(f"  Position:     {report['job_title']}")
    print("-" * 55)
    print(f"  Skill Score:       {report['skill_score']}%")
    print(f"  Experience Score:  {report['experience_score']}%")
    print(f"  Education Score:   {report['education_score']}%")
    print("-" * 55)
    print(f"  ⭐ FINAL SCORE:    {report['final_score']}%")
    print(f"  {report['suitability']}")
    print("-" * 55)
    print(f"  ✅ Matched Required Skills:  {', '.join(report['matched_required']) or 'None'}")
    print(f"  ➕ Matched Preferred Skills: {', '.join(report['matched_preferred']) or 'None'}")
    print(f"  ❌ Missing Skills:           {', '.join(report['missing_skills']) or 'None'}")
    print("=" * 55)


# ==========================================
# Test the code
# ==========================================
if __name__ == "__main__":

    # Sample CV text for testing
    sample_cv = """
    John Smith
    Email: john.smith@email.com
    Phone: +1-555-123-4567

    Summary:
    Experienced Data Science Engineer with 5 years of experience
    in building AI and machine learning applications.

    Skills:
    Python, Machine Learning, TensorFlow, SQL, Docker, Git, NLP, Pandas

    Education:
    Bachelor's Degree in Computer Science - 2018

    Experience:
    - Senior ML Engineer at Tech Corp (2020 - Present)
    - Junior Developer at StartUp Inc (2018 - 2020)
    """

    report = match_cv_to_job(sample_cv)
    print_report(report)