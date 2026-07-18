"""
===========================================
 Skill Utils
 Shared abbreviation dictionary + helpers,
 used by BOTH:
   - cv_extractor.py   (extraction stage)
   - semantic_matcher.py (matching stage)

 Single source of truth: if you need to add
 a new abbreviation, add it HERE only.
===========================================
"""

import re

# Common tech abbreviations -> full term.
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


def find_abbreviations_in_text(text):
    """
    Scan raw CV text for known abbreviations as WHOLE WORDS
    (not substrings — e.g. must NOT match "ai" inside "email").
    Returns a list of expanded skill names found, e.g. ["machine learning"].

    This is used by cv_extractor.py during the extraction stage,
    since the fixed SKILLS_LIST alone misses short abbreviations.
    """
    text_lower = text.lower()
    found = []

    for abbr, full_term in ABBREVIATIONS.items():
        # \b = word boundary -> "ai" won't match inside "email" or "aim"
        # re.escape handles special chars like "ci/cd"
        pattern = r'\b' + re.escape(abbr) + r'\b'
        if re.search(pattern, text_lower):
            found.append(full_term)

    return found