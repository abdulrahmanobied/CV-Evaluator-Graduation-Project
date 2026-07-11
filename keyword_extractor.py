"""
===========================================
 Keyword Extractor (NLTK)
 Extracts meaningful keywords from CV text
 dynamically, instead of relying only on a
 fixed skills list. Uses NLTK to remove
 common "stop words" (the, and, with...)
 and keep only meaningful terms.
===========================================
"""

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

# Download required NLTK data (only happens once, cached after that)
for resource in ["punkt", "punkt_tab", "stopwords"]:
    try:
        nltk.data.find(f"tokenizers/{resource}" if "punkt" in resource else f"corpora/{resource}")
    except LookupError:
        nltk.download(resource, quiet=True)

_stop_words = set(stopwords.words("english"))


def extract_keywords(text, top_n=15):
    """
    Extract the most meaningful keywords from CV text.
    Removes common stop words and punctuation, keeping only
    substantive terms that could indicate skills, tools, or topics
    not already covered by our fixed skills list.
    """
    text_lower = text.lower()
    tokens = word_tokenize(text_lower)

    keywords = [
        word for word in tokens
        if word.isalpha()                  # letters only (skip numbers/punctuation)
        and word not in _stop_words        # skip "the", "and", "with", etc.
        and len(word) > 2                  # skip very short tokens
    ]

    # Count frequency and return the most common unique keywords
    from collections import Counter
    counts = Counter(keywords)
    most_common = [word for word, _ in counts.most_common(top_n)]
    return most_common


if __name__ == "__main__":
    print("=" * 60)
    print("  Keyword Extractor (NLTK) - Test Run")
    print("=" * 60)

    sample_cv = """
    John Smith is a Software Engineer with experience in Kubernetes,
    Terraform, and cloud infrastructure automation. He has worked
    with distributed systems and has led several DevOps initiatives
    at his previous company. He is passionate about automation,
    scalability, and building reliable infrastructure.
    """

    keywords = extract_keywords(sample_cv)
    print("\n📄 Sample CV text analyzed.")
    print(f"\n🔑 Top keywords found (via NLTK): {keywords}")
    print("\nNotice: 'kubernetes' and 'terraform' are detected here even though")
    print("they are NOT in our fixed SKILLS_LIST inside cv_extractor.py.")
    print("=" * 60)