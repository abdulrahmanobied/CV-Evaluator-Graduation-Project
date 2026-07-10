"""
===========================================
 Semantic Matcher
 Hybrid skill matching (3 layers):
 1) Abbreviation dictionary  -> expands known
    short forms (ai, ml, db...) to full terms
 2) Exact text match         -> fast, precise
 3) AI semantic similarity   -> for anything not
    matched exactly (understands meaning,
    e.g. "deep learning" ~ "neural networks")
===========================================
"""

from sentence_transformers import SentenceTransformer, util

print("⏳ Loading AI matching model (only happens once)...")
_model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ AI matching model ready!")

SIMILARITY_THRESHOLD = 0.55  # how "close in meaning" two skills must be to count as a match

# Common tech abbreviations -> full term.
# This handles short, ambiguous abbreviations that AI similarity
# alone struggles with (e.g. "ml" is only 2 letters -- not enough
# context for the model to reliably link it to "machine learning").
ABBREVIATIONS = {
    "ai": "artificial intelligence",
    "ml": "machine learning",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "db": "database",
    "dbs": "databases",
    "js": "javascript",
    "ts": "typescript",
    "k8s": "kubernetes",
    "ci/cd": "continuous integration continuous deployment",
    "oop": "object oriented programming",
    "os": "operating systems",
    "ui": "user interface",
    "ux": "user experience",
    "api": "application programming interface",
    "sre": "site reliability engineering",
}


def normalize_skill(skill):
    """Expand a skill to its full form if it's a known abbreviation"""
    skill_clean = skill.strip().lower()
    return ABBREVIATIONS.get(skill_clean, skill_clean)


def calculate_semantic_skill_score(candidate_skills, required_skills, preferred_skills):
    """
    Hybrid skill score:
    - Required skills = 70% of score
    - Preferred skills = 30% of score
    - A skill counts as matched if:
        a) it's a known abbreviation of the other, OR
        b) it's an exact text match, OR
        c) its AI similarity to any candidate skill is above the threshold
    Returns: score, matched_required, matched_preferred, similarity_details
    """
    similarity_details = []

    # Normalize (expand abbreviations) for comparison, but keep originals for display
    candidate_normalized = [normalize_skill(s) for s in candidate_skills]

    def find_matches(job_skills, candidate_skills, candidate_normalized):
        matches = []
        if not candidate_skills:
            return matches

        candidate_embeddings = _model.encode(candidate_normalized, convert_to_tensor=True)

        for job_skill in job_skills:
            job_skill_norm = normalize_skill(job_skill)

            # 1) Abbreviation / exact match (case-insensitive, using normalized forms)
            if job_skill_norm in candidate_normalized:
                matches.append(job_skill)
                matched_candidate = candidate_skills[candidate_normalized.index(job_skill_norm)]
                if job_skill.lower() == matched_candidate.lower():
                    similarity_details.append(f"{job_skill} = exact match")
                else:
                    similarity_details.append(f"{job_skill} = abbreviation match ({matched_candidate})")
                continue

            # 2) Fall back to semantic (AI) similarity
            job_embedding = _model.encode(job_skill_norm, convert_to_tensor=True)
            similarities = util.cos_sim(job_embedding, candidate_embeddings)[0]
            best_score = float(similarities.max())
            best_idx = int(similarities.argmax())

            if best_score >= SIMILARITY_THRESHOLD:
                matches.append(job_skill)
                similarity_details.append(
                    f"{job_skill} ~ {candidate_skills[best_idx]} (similarity: {best_score:.2f})"
                )

        return matches

    required_matches = find_matches(required_skills, candidate_skills, candidate_normalized) if required_skills else []
    preferred_matches = find_matches(preferred_skills, candidate_skills, candidate_normalized) if preferred_skills else []

    required_score = (len(required_matches) / len(required_skills) * 70) if required_skills else 70
    preferred_score = (len(preferred_matches) / len(preferred_skills) * 30) if preferred_skills else 30

    final_score = round(required_score + preferred_score, 2)

    return final_score, required_matches, preferred_matches, similarity_details


if __name__ == "__main__":
    print("=" * 60)
    print("  Semantic Matcher - Test Run")
    print("=" * 60)

    candidate_skills = ["python", "ml", "ai", "db", "docker", "git"]
    required_skills = ["python", "machine learning", "database", "tensorflow"]
    preferred_skills = ["docker", "git"]

    score, req_matches, pref_matches, details = calculate_semantic_skill_score(
        candidate_skills, required_skills, preferred_skills
    )

    print(f"\nCandidate skills:  {candidate_skills}")
    print(f"Required skills:   {required_skills}")
    print(f"Preferred skills:  {preferred_skills}")
    print(f"\n✅ Matched required: {req_matches}")
    print(f"✅ Matched preferred: {pref_matches}")
    print(f"⭐ Final skill score: {score}%")
    print("\n🔍 Match details:")
    for d in details:
        print(f"   - {d}")
    print("=" * 60)