from sentence_transformers import SentenceTransformer, util

print("⏳ Loading model (first time will download ~90MB)...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Model loaded!")

# Test: are "ML" and "Machine Learning" similar?
skill1 = "ML"
skill2 = "Machine Learning"
skill3 = "Cooking"

emb1 = model.encode(skill1, convert_to_tensor=True)
emb2 = model.encode(skill2, convert_to_tensor=True)
emb3 = model.encode(skill3, convert_to_tensor=True)

similarity_1_2 = util.cos_sim(emb1, emb2).item()
similarity_1_3 = util.cos_sim(emb1, emb3).item()

print(f"\nSimilarity between 'ML' and 'Machine Learning': {similarity_1_2:.2f}")
print(f"Similarity between 'ML' and 'Cooking': {similarity_1_3:.2f}")