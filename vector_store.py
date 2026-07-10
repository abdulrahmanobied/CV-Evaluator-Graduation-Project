"""
===========================================
 Vector Store
 Stores each candidate's skill profile in
 ChromaDB (a Vector Database) so we can
 semantically search candidates later.
 E.g. searching "AI experience" can find a
 candidate who never wrote the words "AI".
===========================================
"""

import chromadb
import os

# Persistent storage on disk (not in-memory), so data survives between runs
DB_FOLDER = os.path.join(os.path.dirname(__file__), "vector_db")

_client = chromadb.PersistentClient(path=DB_FOLDER)
_collection = _client.get_or_create_collection(name="candidates")


def add_candidate_to_vector_store(candidate_id, name, email, skills, summary_text=""):
    """
    Store one candidate's profile in the vector database.
    - candidate_id: a unique string (e.g. database row id)
    - skills: list of skill strings
    - summary_text: optional extra text (e.g. job title, experience) for richer search
    """
    profile_text = f"{summary_text}. Skills: {', '.join(skills)}".strip()

    _collection.upsert(
        documents=[profile_text],
        ids=[str(candidate_id)],
        metadatas=[{"name": name, "email": email, "skills": ", ".join(skills)}]
    )


def search_candidates_semantic(query, n_results=5):
    """
    Search stored candidates by meaning (not exact keywords).
    Returns a list of dicts: name, email, skills, match_distance
    """
    count = _collection.count()
    if count == 0:
        return []

    n_results = min(n_results, count)
    results = _collection.query(query_texts=[query], n_results=n_results)

    matches = []
    for metadata, distance in zip(results["metadatas"][0], results["distances"][0]):
        matches.append({
            "name": metadata["name"],
            "email": metadata["email"],
            "skills": metadata["skills"],
            "distance": round(distance, 3),
        })
    return matches


def clear_vector_store():
    """Delete all stored candidate profiles (useful for testing)"""
    global _collection
    _client.delete_collection(name="candidates")
    _collection = _client.get_or_create_collection(name="candidates")


if __name__ == "__main__":
    print("=" * 60)
    print("  Vector Store - Test Run")
    print("=" * 60)

    clear_vector_store()

    add_candidate_to_vector_store(
        candidate_id="1", name="Ahmad Khalil", email="ahmad.khalil@email.com",
        skills=["python", "machine learning", "deep learning", "tensorflow"],
        summary_text="AI Engineer with 6 years experience"
    )
    add_candidate_to_vector_store(
        candidate_id="2", name="Lina Youssef", email="lina.youssef@email.com",
        skills=["python", "sql", "html", "css"],
        summary_text="Junior web developer with 1 year experience"
    )
    add_candidate_to_vector_store(
        candidate_id="3", name="Omar Hassan", email="omar.hassan@email.com",
        skills=["python", "scikit-learn", "pandas", "data analysis"],
        summary_text="Data scientist with 4 years experience"
    )
    print("✅ 3 sample candidates stored in the vector database\n")

    query = "someone experienced in artificial intelligence and neural networks"
    print(f"🔍 Searching for: '{query}'\n")

    results = search_candidates_semantic(query, n_results=3)
    for i, r in enumerate(results, 1):
        print(f"#{i} — {r['name']} (distance: {r['distance']})")
        print(f"     Email:  {r['email']}")
        print(f"     Skills: {r['skills']}")
        print("-" * 50)

    print("=" * 60)