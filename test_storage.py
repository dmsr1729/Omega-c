from modules.document_processor import process_document
from modules.vector_store import create_vector_store, save_vector_store, load_vector_store

# Step 1: Process PDF
chunks, embeddings = process_document("data/mohan_sameer.pdf")

# Step 2: Create Vector Store
store = create_vector_store(chunks, embeddings)

# Step 3: Save Vector Store
save_vector_store(store, "data/vector_store.json")

# Step 4: Load Vector Store
loaded_store = load_vector_store("data/vector_store.json")

# Step 5: Verify loaded data
print("\nStorage Test Successful!")

print("Total Chunks:", loaded_store.get_total_vectors())
print("Embedding Dimensions:", loaded_store.get_dimensions())