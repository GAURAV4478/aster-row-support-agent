"""
Thin wrapper around Gemini's embedding API.

Two separate functions, not one - Gemini embeds text differently depending
on whether it's a document being stored or a query being searched with.
Using the wrong task_type for either side quietly degrades retrieval
accuracy - this directly affects how well we solve Challenge 1 (picking
the RIGHT policy doc), since bad retrieval means the wrong doc gets pulled
in the first place, no amount of downstream filtering fixes that.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

EMBED_MODEL = "models/text-embedding-004"
_configured = False


def _ensure_configured():
    global _configured
    if not _configured:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        _configured = True


def embed_document(text: str) -> list[float]:
    """Embed a knowledge-base chunk for storage."""
    _ensure_configured()
    result = genai.embed_content(
        model=EMBED_MODEL,
        content=text,
        task_type="retrieval_document",
    )
    return result["embedding"]


def embed_query(text: str) -> list[float]:
    """Embed a user question for searching against stored documents."""
    _ensure_configured()
    result = genai.embed_content(
        model=EMBED_MODEL,
        content=text,
        task_type="retrieval_query",
    )
    return result["embedding"]