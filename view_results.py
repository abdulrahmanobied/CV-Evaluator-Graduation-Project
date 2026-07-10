"""
===========================================
 View Results
 Displays all saved candidate evaluations
 in a clean, organized table format
===========================================
"""

from database import get_all_results


def print_clean_table():
    """Print all saved results as a neat, aligned table"""
    results = get_all_results()

    if not results:
        print("📭 No results saved yet. Evaluate some candidates first.")
        return

    print("\n" + "=" * 110)
    print("                                   CANDIDATE EVALUATION HISTORY")
    print("=" * 110)

    header = f"{'ID':<4}{'Name':<20}{'Job Title':<28}{'Score':<8}{'Suitability':<22}{'Date':<20}"
    print(header)
    print("-" * 110)

    for r in results:
        # Strip emoji from suitability for cleaner column alignment, keep text
        suitability_text = r['suitability'].split(" ", 1)[-1] if " " in r['suitability'] else r['suitability']

        row = (
            f"{r['id']:<4}"
            f"{(r['name'] or 'Unknown')[:18]:<20}"
            f"{(r['job_title'] or 'N/A')[:26]:<28}"
            f"{str(r['final_score']) + '%':<8}"
            f"{suitability_text:<22}"
            f"{r['created_at']:<20}"
        )
        print(row)

    print("-" * 110)
    print(f"Total records: {len(results)}")
    print("=" * 110)

    # Detailed view per candidate
    print("\n📋 DETAILED VIEW\n")
    for r in results:
        print(f"#{r['id']} — {r['name']} ({r['final_score']}%) — {r['suitability']}")
        print(f"    Email:            {r['email']}")
        print(f"    Job Title:        {r['job_title']}")
        print(f"    Skill Score:      {r['skill_score']}%")
        print(f"    Experience Score: {r['experience_score']}%")
        print(f"    Education Score:  {r['education_score']}%")
        print(f"    Matched Skills:   {r['matched_skills'] or 'None'}")
        print(f"    Missing Skills:   {r['missing_skills'] or 'None'}")
        print(f"    Evaluated At:     {r['created_at']}")
        print("-" * 60)


if __name__ == "__main__":
    print_clean_table()