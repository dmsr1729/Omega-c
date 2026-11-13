from modules.pdf_processor import extract_pages
from modules.text_chunker import chunk_pages
from modules.embeddings import generate_embeddings


def process_document(pdf_path):

    # Step 1: Extract text with page numbers
    pages = extract_pages(pdf_path)

    # Step 2: Create chunks while preserving page numbers
    chunks = chunk_pages(
        pages,
        chunk_size=1000,
        overlap=100
    )

    # Step 3: Extract only text for embedding generation
    chunk_texts = [
        chunk["text"] for chunk in chunks
    ]

    # Step 4: Generate embeddings
    embeddings = generate_embeddings(chunk_texts)

    return chunks, embeddings