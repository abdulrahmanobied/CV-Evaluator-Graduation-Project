"""
===========================================
 Test ChromaDB
 Verifies that ChromaDB starts up locally
 and can store + semantically search skills
===========================================
"""

import chromadb

print("⏳ Starting local ChromaDB instance...")
client = chromadb.Client()  # in-memory, no server needed

collection = client.create_collection(name="test_skills")
print("✅ Collection created!")

collection.add(
    documents=["machine learning", "cooking recipes", "deep learning", "gardening tips"],
    ids=["1", "2", "3", "4"]
)
print("✅ Test data inserted!")

# Semantic search: does ChromaDB understand "AI" is close to "machine learning"?
results = collection.query(
    query_texts=["AI and neural networks"],
    n_results=2
)

print("\n🔍 Searching for something close in meaning to: 'AI and neural networks'")
print("Top matches found:")
for doc, distance in zip(results["documents"][0], results["distances"][0]):
    print(f"   - {doc}  (distance: {distance:.3f})")

print("\n🎉 ChromaDB is working correctly!")