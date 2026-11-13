from modules.vector_store import create_vector_store

# Sample text chunks
chunks = [
    "Python is a programming language.",
    "Java is an object-oriented language.",
    "Machine learning uses data."
]

# Sample embeddings
embeddings = [
    [1, 0, 0],
    [0.9, 0.1, 0],
    [0, 1, 0]
]

# Create vector store
store = create_vector_store(chunks, embeddings)

# Sample query embedding
query_embedding = [1, 0, 0]

# Search for top 2 matching chunks
results = store.search(query_embedding, top_k=2)

# Display results
print("Relevant Document Chunks:")

for result in results:

    print("\nText:", result["text"])
    print("Similarity:", result["score"])