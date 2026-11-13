
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
import streamlit as st

# ======================================
# LOAD ENVIRONMENT VARIABLES
# ======================================

env_path = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(dotenv_path=env_path, override=True)

# First check local .env / environment variables
api_key = os.getenv("GEMINI_API_KEY", "").strip()

# If not found, check Streamlit Secrets
if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"].strip()
    except Exception:
        api_key = ""

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found. Configure it in .env "
        "or Streamlit Secrets."
    )

client = genai.Client(api_key=api_key)


# ======================================
# DOCUMENT EMBEDDINGS
# ======================================

def generate_embeddings(chunks):

    embeddings = []
    batch_size = 100

    for i in range(0, len(chunks), batch_size):

        batch = chunks[i:i + batch_size]

        for attempt in range(3):

            try:

                response = client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=batch,
                    config=types.EmbedContentConfig(
                        task_type="RETRIEVAL_DOCUMENT",
                        output_dimensionality=768
                    )
                )

                batch_embeddings = [
                    item.values for item in response.embeddings
                ]

                embeddings.extend(batch_embeddings)

                print(
                    f"Generated embeddings: "
                    f"{len(embeddings)}/{len(chunks)}"
                )

                break

            except Exception as e:

                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):

                    if attempt < 2:
                        print(
                            "Gemini rate limit reached. "
                            "Waiting 10 seconds..."
                        )
                        time.sleep(10)
                    else:
                        raise

                else:
                    raise

        time.sleep(2)

    return embeddings


# ======================================
# QUERY EMBEDDINGS
# ======================================

def generate_query_embedding(query):

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=query,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=768
        )
    )

    return response.embeddings[0].values
