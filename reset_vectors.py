"""
One-time cleanup script:
Clears all old/test data from the vector database.
Run this once, then delete this file.
"""

from vector_store import clear_vector_store

clear_vector_store()
print("✅ Vector database cleared. All old test data removed.")
print("   Now re-evaluate your real candidates through the app to repopulate it.")