import json

from modules.llm import extract_concept_relationships


# Load previously processed document
with open("data/vector_store.json", "r", encoding="utf-8") as file:
    data = json.load(file)

chunks = data["chunks"]


# Concepts identified from your document
concepts = [
    "technical",
    "java",
    "sdlc",
    "retrieval",
    "leadership",
    "pipeline",
    "python",
    "software",
    "full",
    "stack",
    "intelligence",
    "engineering"
]


print("Extracting AI Relationships...")

relationships = extract_concept_relationships(
    chunks,
    concepts
)


print("\nAI-Generated Relationships:\n")

for item in relationships:

    print(
        item["source"],
        "-->",
        item["relationship"],
        "-->",
        item["target"]
    )