from modules.pdf_processor import extract_text
from modules.text_chunker import chunk_text

# Step 1: Extract text from PDF
pdf_path = "data/mohan_sameer.pdf"

text = extract_text(pdf_path)

# Step 2: Divide extracted text into chunks
chunks = chunk_text(text, chunk_size=500, overlap=50)

# Step 3: Display the chunks
print("Total Chunks:", len(chunks))

for i, chunk in enumerate(chunks):

    print(f"\nCHUNK {i+1}")
    print(chunk)
