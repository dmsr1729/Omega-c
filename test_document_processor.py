from modules.document_processor import process_document

# Step 1: Process the PDF
chunks, embeddings = process_document("data/mohan_sameer.pdf")

# Step 2: Display results
print("Document Processing Successful!")

print("Total Chunks:", len(chunks))
print("Total Embeddings:", len(embeddings))

print("Embedding Dimensions:", len(embeddings[0]))

print("\nFirst Text Chunk:")
print(chunks[0])