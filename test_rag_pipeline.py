import os

from modules.document_processor import process_document
from modules.vector_store import (
    create_vector_store,
    save_vector_store,
    load_vector_store
)
from modules.embeddings import generate_query_embedding
from modules.llm import generate_answer

# Step 1: Check whether vector store exists
if os.path.exists("data/vector_store.json"):

    print("Loading Existing Vector Store...")

    store = load_vector_store("data/vector_store.json")

else:

    print("Creating New Vector Store...")

    chunks, embeddings = process_document("data/mohan_sameer.pdf")

    store = create_vector_store(chunks, embeddings)

    save_vector_store(store, "data/vector_store.json")


print("\nOmega-C RAG Chatbot Ready!")
print("Type 'exit' to stop.")

# Step 2: Chat Loop
while True:

    query = input("\nYou: ")

    if query.lower() == "exit":
        print("Chatbot stopped.")
        break

    # Generate query embedding
    query_embedding = generate_query_embedding(query)

    # Retrieve relevant chunks
    results = store.search(query_embedding, top_k=3)

    # Combine context
    context = "\n".join(
        result["text"] for result in results
    )

    # Generate answer
    answer = generate_answer(query, context)

    print("\nOmega-C:", answer)