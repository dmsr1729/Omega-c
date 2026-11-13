from modules.pdf_processor import extract_text
from modules.text_chunker import chunk_text
from modules.embeddings import generate_embeddings

# Step 1: Extract text from PDF
text = extract_text("data/mohan_sameer.pdf")

# Step 2: Divide text into chunks
chunks = chunk_text(text, chunk_size=500, overlap=50)

# Step 3: Generate embeddings for first 3 chunks
embeddings = generate_embeddings(chunks[:3])

# Step 4: Display results
print("Total chunks:", 3)

print("Total embeddings:", len(embeddings))

print("Dimensions per embedding:", len(embeddings[0]))

print("\nFirst chunk embedding:")
print(embeddings[0])