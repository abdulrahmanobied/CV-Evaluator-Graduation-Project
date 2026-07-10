"""
===========================================
 Ranker
 Ranks multiple candidates by their match score
 from highest to lowest
===========================================
"""

from job_matcher import match_cv_to_job, print_report


def rank_candidates(cv_texts):
    """
    Takes a list of CV texts, scores each one,
    and returns them sorted from best to worst match
    """
    print(f"\n📂 Processing {len(cv_texts)} candidates...\n")

    results = []
    for i, cv_text in enumerate(cv_texts):
        print(f"--- Evaluating Candidate {i + 1} ---")
        report = match_cv_to_job(cv_text)
        report["candidate_number"] = i + 1
        results.append(report)

    # Sort by final score (highest first)
    ranked = sorted(results, key=lambda x: x["final_score"], reverse=True)

    return ranked


def print_ranking_summary(ranked_candidates):
    """Print a clean ranking summary table"""
    print("\n")
    print("=" * 60)
    print("           CANDIDATE RANKING SUMMARY")
    print("=" * 60)
    print(f"  {'Rank':<6} {'Name':<20} {'Score':<10} {'Suitability'}")
    print("-" * 60)

    for rank, candidate in enumerate(ranked_candidates, start=1):
        name  = candidate["candidate_name"] or "Unknown"
        score = f"{candidate['final_score']}%"
        level = candidate["suitability"]
        print(f"  #{rank:<5} {name:<20} {score:<10} {level}")

    print("=" * 60)
    print(f"\n🏆 Best Candidate: {ranked_candidates[0]['candidate_name']} "
          f"({ranked_candidates[0]['final_score']}%)")


# ==========================================
# Test the code
# ==========================================
if __name__ == "__main__":

    # Sample CVs for testing (3 different candidates)
    cv_1 = """
    John Smith
    Email: john.smith@email.com
    Phone: +1-555-123-4567
    Summary: Data Science Engineer with 5 years of experience.
    Skills: Python, Machine Learning, TensorFlow, SQL, Docker, Git, NLP, Pandas, NumPy
    Education: Master's Degree in Computer Science - 2018
    Experience: Senior ML Engineer at Tech Corp (2020 - Present)
    """

    cv_2 = """
    Sarah Johnson
    Email: sarah.j@email.com
    Phone: +1-555-987-6543
    Summary: Junior developer with 1 year of experience.
    Skills: Python, SQL, Git
    Education: Bachelor's Degree in Information Technology - 2022
    Experience: Junior Developer at StartUp Inc (2023 - Present)
    """

    cv_3 = """
    Michael Lee
    Email: michael.lee@email.com
    Phone: +1-555-456-7890
    Summary: AI researcher with 7 years of experience in deep learning and NLP.
    Skills: Python, Deep Learning, PyTorch, TensorFlow, NLP, Machine Learning,
            SQL, Docker, AWS, Scikit-learn, Pandas, NumPy, Computer Vision
    Education: PhD in Artificial Intelligence - 2017
    Experience: AI Research Lead at AI Labs (2017 - Present)
    """

    # Rank all candidates
    all_cvs = [cv_1, cv_2, cv_3]
    ranked = rank_candidates(all_cvs)

    # Print full report for each candidate
    print("\n\n📋 DETAILED REPORTS:")
    for candidate in ranked:
        print_report(candidate)

    # Print summary table
    print_ranking_summary(ranked)