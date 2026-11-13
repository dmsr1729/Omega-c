import json
import re

from modules.embeddings import client


def generate_answer(query, context):

    prompt = f"""
    You are a helpful AI assistant.

    Answer the user's question using only the
    information provided in the context.

    If the answer is not available in the context,
    say "The information is not available in the document."

    Context:
    {context}

    Question:
    {query}

    Answer:
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text

def extract_concept_relationships(chunks, concepts):

    context = "\n".join(chunks)

    prompt = f"""
    You are an expert knowledge graph builder.

    Analyze the document and identify meaningful
    relationships between the given concepts.

    Concepts:
    {concepts}

    Document:
    {context}

    Return only valid JSON in this format:

    [
        {{
            "source": "Python",
            "relationship": "is a",
            "target": "Programming Language"
        }}
    ]

    Rules:
    1. Use only the provided concepts.
    2. Identify only meaningful relationships.
    3. Do not invent relationships.
    4. Return a maximum of 15 relationships.
    5. Return an empty JSON array if no relationships exist.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    result = response.text.strip()

    # Remove Markdown formatting if Gemini adds it
    result = re.sub(r"```json|```", "", result).strip()

    relationships = json.loads(result)

    return relationships