import json
import uuid
import hashlib
from pathlib import Path
from datetime import datetime


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
VECTOR_STORES_DIR = DATA_DIR / "vector_stores"

METADATA_FILE = DATA_DIR / "document_metadata.json"


# Create required folders
def initialize_storage():

    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    VECTOR_STORES_DIR.mkdir(parents=True, exist_ok=True)

    if not METADATA_FILE.exists():

        with open(METADATA_FILE, "w", encoding="utf-8") as file:
            json.dump({}, file)


# Read document metadata
def load_metadata():

    initialize_storage()

    with open(METADATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# Save document metadata
def save_metadata(metadata):

    with open(METADATA_FILE, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)


# Save uploaded PDF permanently
def save_uploaded_document(uploaded_file):

    initialize_storage()

    # Calculate unique file hash
    file_content = uploaded_file.getvalue()
    file_hash = hashlib.sha256(file_content).hexdigest()

    metadata = load_metadata()

    # Check whether this PDF already exists
    for document in metadata.values():

        if document.get("file_hash") == file_hash:
            return document

    # Generate unique document ID
    document_id = str(uuid.uuid4())

    pdf_path = DOCUMENTS_DIR / f"{document_id}.pdf"

    vector_path = VECTOR_STORES_DIR / f"{document_id}.json"

    # Save PDF permanently
    with open(pdf_path, "wb") as file:
        file.write(file_content)

    metadata[document_id] = {

        "id": document_id,

        "name": uploaded_file.name,

        "file_hash": file_hash,

        "uploaded_at": datetime.now().isoformat(),

        "pdf_path": str(pdf_path.relative_to(BASE_DIR)),

        "vector_store_path": str(vector_path.relative_to(BASE_DIR)),

        "status": "Uploaded"

    }

    save_metadata(metadata)

    return metadata[document_id]
def get_all_documents():

    metadata = load_metadata()

    documents = list(metadata.values())

    documents.sort(
        key=lambda item: item["uploaded_at"],
        reverse=True
    )

    return documents


# Get one document
def get_document(document_id):

    metadata = load_metadata()

    return metadata.get(document_id)


# Update document processing status
def update_document_status(document_id, chunks, dimensions):

    metadata = load_metadata()

    if document_id not in metadata:
        return

    metadata[document_id]["status"] = "Processed"

    metadata[document_id]["total_chunks"] = chunks

    metadata[document_id]["embedding_dimensions"] = dimensions

    save_metadata(metadata)


# Delete a document permanently
def delete_document(document_id):

    metadata = load_metadata()

    if document_id not in metadata:
        return False

    document = metadata[document_id]

    pdf_path = BASE_DIR / document["pdf_path"]

    vector_path = BASE_DIR / document["vector_store_path"]

    if pdf_path.exists():
        pdf_path.unlink()

    if vector_path.exists():
        vector_path.unlink()

    del metadata[document_id]

    save_metadata(metadata)

    return True
def remove_duplicate_documents():

    metadata = load_metadata()

    seen_hashes = set()
    updated_metadata = {}

    # Keep older documents first
    documents = sorted(
        metadata.items(),
        key=lambda item: item[1]["uploaded_at"]
    )

    removed = 0

    for document_id, document in documents:

        pdf_path = BASE_DIR / document["pdf_path"]

        if not pdf_path.exists():
            continue

        with open(pdf_path, "rb") as file:
            file_hash = hashlib.sha256(file.read()).hexdigest()

        # Skip duplicate documents
        if file_hash in seen_hashes:

            vector_path = BASE_DIR / document["vector_store_path"]

            if pdf_path.exists():
                pdf_path.unlink()

            if vector_path.exists():
                vector_path.unlink()

            removed += 1
            continue

        seen_hashes.add(file_hash)

        document["file_hash"] = file_hash

        updated_metadata[document_id] = document

    save_metadata(updated_metadata)

    print(f"Duplicate documents removed: {removed}")