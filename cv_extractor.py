"""
===========================================
 CV Extractor
 Extracts structured information from CV text
 (Name, Email, Phone, Skills, Experience)
===========================================
"""

import re
import spacy

from skill_utils import find_abbreviations_in_text

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")


def extract_email(text):
    """Extract email address from text"""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.findall(pattern, text)
    return match[0] if match else None


def extract_phone(text):
    """Extract phone number from text"""
    pattern = r'(\+?\d[\d\s\-().]{7,}\d)'
    match = re.findall(pattern, text)
    return match[0].strip() if match else None


def extract_name(text):
    """Extract candidate name using NLP (first PERSON entity found)"""
    # Try the first line first (names are usually at the top of a CV)
    first_line = text.strip().split("\n")[0].strip()
    doc = nlp(first_line)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text

    # Fallback: search a larger chunk if nothing found in the first line
    doc = nlp(text[:500])
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None


def extract_skills(text):
    """
    Extract skills from CV text using two passes:
      1) Predefined SKILLS_LIST, matched as a whole word/phrase
         (e.g. "machine learning" — NOT as a substring, so "r" won't
         match inside "career" and "go" won't match inside "going")
      2) Known abbreviations as WHOLE WORDS (e.g. "ML" -> "machine learning"),
         via skill_utils.find_abbreviations_in_text()

    Both passes feed into ONE final list, de-duplicated, so a skill
    written as "ML" or written out as "Machine Learning" ends up
    represented the same way downstream (matching, storage, display).
    """
    SKILLS_LIST = [
        # Programming Languages
        "python", "java", "javascript", "c++", "c#", "ruby", "swift", "kotlin",
        "php", "typescript", "r", "matlab", "scala", "go", "rust",
        # Web
        "html", "css", "react", "angular", "vue", "node.js", "django", "flask",
        "spring", "express",
        # Data & AI
        "machine learning", "deep learning", "nlp", "computer vision",
        "tensorflow", "pytorch", "scikit-learn", "keras", "pandas", "numpy",
        "data analysis", "data science", "artificial intelligence",
        # Databases
        "sql", "mysql", "postgresql", "mongodb", "sqlite", "oracle",
        "redis", "elasticsearch",
        # Tools & Platforms
        "git", "docker", "kubernetes", "aws", "azure", "gcp", "linux",
        "jenkins", "ci/cd", "agile", "scrum",
    ]

    text_lower = text.lower()

    # Pass 1: predefined list, matched as a WHOLE WORD/PHRASE
    # (not substring match — e.g. "r" must NOT match inside "career",
    # "go" must NOT match inside "going", etc.)
    #
    # We can't use plain \b here because some skills end in
    # non-word characters (e.g. "c++", "c#"), and \b only fires at a
    # transition between a word char and a non-word char — it won't
    # match right after "++" if followed by another non-word char
    # (like a space or period). Instead we manually check that the
    # character immediately before/after the match isn't alphanumeric.
    found_skills = []
    for skill in SKILLS_LIST:
        pattern = r'(?<![a-z0-9])' + re.escape(skill) + r'(?![a-z0-9])'
        if re.search(pattern, text_lower):
            found_skills.append(skill)

    # Pass 2: known abbreviations, matched as whole words only
    # (e.g. "ML" -> "machine learning", "DB" -> "database")
    abbreviation_skills = find_abbreviations_in_text(text)

    # Merge + de-duplicate, keeping first-seen order
    for skill in abbreviation_skills:
        if skill not in found_skills:
            found_skills.append(skill)

    return found_skills


def extract_experience_years(text):
    """Extract years of experience mentioned in the CV"""
    pattern = r'(\d+)\+?\s*years?\s*(of\s*)?(experience|exp)?'
    matches = re.findall(pattern, text.lower())
    if matches:
        years = [int(m[0]) for m in matches]
        return max(years)  # Return the highest number found
    return 0


def extract_education(text):
    """Extract education level from CV"""
    text_lower = text.lower()
    if "phd" in text_lower or "doctorate" in text_lower:
        return "PhD"
    elif "master" in text_lower or "msc" in text_lower or "m.sc" in text_lower:
        return "Master's"
    elif "bachelor" in text_lower or "bsc" in text_lower or "b.sc" in text_lower:
        return "Bachelor's"
    elif "diploma" in text_lower:
        return "Diploma"
    else:
        return "Not specified"


def extract_all(text):
    """
    Main function - extracts all information from CV text
    Returns a dictionary with all extracted fields
    """
    print("🔍 Extracting information from CV...")

    result = {
        "name":             extract_name(text),
        "email":            extract_email(text),
        "phone":            extract_phone(text),
        "skills":           extract_skills(text),
        "experience_years": extract_experience_years(text),
        "education":        extract_education(text),
    }

    print("✅ Extraction complete!")
    return result


# ==========================================
# Test the code
# ==========================================
if __name__ == "__main__":
    print("=" * 50)
    print("  CV Extractor - Test Run")
    print("=" * 50)

    # Sample CV text for testing
    sample_cv = """
    John Smith
    Email: john.smith@email.com
    Phone: +1-555-123-4567

    Summary:
    Experienced Software Engineer with 5 years of experience in
    building AI and data-driven applications.

    Skills:
    Python, Machine Learning, TensorFlow, SQL, Docker, Git, NLP

    Education:
    Bachelor's Degree in Computer Science - 2018

    Experience:
    - Senior Developer at Tech Corp (2020 - Present)
    - Junior Developer at StartUp Inc (2018 - 2020)
    """

    extracted = extract_all(sample_cv)

    print("\n📋 Extracted Information:")
    print("-" * 30)
    print(f"  Name:        {extracted['name']}")
    print(f"  Email:       {extracted['email']}")
    print(f"  Phone:       {extracted['phone']}")
    print(f"  Education:   {extracted['education']}")
    print(f"  Experience:  {extracted['experience_years']} years")
    print(f"  Skills:      {', '.join(extracted['skills'])}")
    print("=" * 50)

    # Extra test: CV written with abbreviations only (like Sara Ibrahim's CV)
    print("\n" + "=" * 50)
    print("  Extra Test - Abbreviations-only CV (Sara style)")
    print("=" * 50)

    sara_cv = """
    Sara Ibrahim
    Email: sara.ibrahim@email.com
    Phone: +962-79-333-2211

    Summary: Engineer with 5 years of experience in AI and databases.

    Skills: Python, ML, AI, DB, Docker, Git

    Education: Bachelor's Degree in Software Engineering - 2020

    Experience: AI Engineer at SmartSoft (2021 - Present)
    """

    sara_extracted = extract_all(sara_cv)
    print(f"  Skills: {', '.join(sara_extracted['skills'])}")
    print("=" * 50)