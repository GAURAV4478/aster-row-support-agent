"""
Thin wrapper around Gemini's embedding API using the new google-genai SDK.
"""
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Keeping the exact model you used for ingestion
EMBED_MODEL = "models/gemini-embedding-001" 

# The new SDK automatically picks up GEMINI_API_KEY from the environment
client = genai.Client()

def embed_document(text: str) -> list[float]:
    """Embed a knowledge-base chunk for storage."""
    response = client.models.embed_content(
        model=EMBED_MODEL,
        contents=text,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
    )
    return response.embeddings[0].values

def embed_query(text: str) -> list[float]:
    """Embed a user question for searching against stored documents."""
    response = client.models.embed_content(
        model=EMBED_MODEL,
        contents=text,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
    )
    return response.embeddings[0].values