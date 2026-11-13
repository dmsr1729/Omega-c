def chunk_text(text, chunk_size=200, overlap=30):

    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Invalid chunk size or overlap")

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start = end - overlap

    return chunks


def chunk_pages(pages, chunk_size=200, overlap=30):

    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Invalid chunk size or overlap")

    chunks = []

    for page_data in pages:

        page_number = page_data["page"]
        text = page_data["text"]

        page_chunks = chunk_text(
            text,
            chunk_size,
            overlap
        )

        for chunk in page_chunks:

            chunks.append({
                "text": chunk,
                "page": page_number
            })

    return chunks