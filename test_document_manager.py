from modules.document_manager import (
    initialize_storage,
    get_all_documents
)
from modules.document_manager import remove_duplicate_documents

remove_duplicate_documents()
print("Initializing Omega-C Storage...")

initialize_storage()

print("\nStorage initialized successfully!")

print("\nSaved Documents:")

documents = get_all_documents()

if documents:

    for document in documents:
        print(document["name"], "-", document["status"])

else:

    print("No documents found.")
