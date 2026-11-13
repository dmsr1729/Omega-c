from modules.embeddings import generate_query_embedding

# Sample user question
query = "What programming languages are mentioned?"

# Generate query embedding
embedding = generate_query_embedding(query)

# Display results
print("Query Embedding Generated Successfully!")

print("Embedding Dimensions:", len(embedding))

print("First 5 Values:", embedding[:5])