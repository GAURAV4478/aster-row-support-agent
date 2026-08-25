"""
Ingestion pipeline: loads knowledge-base markdown files, chunks them,
embeds each chunk, and stores everything in ChromaDB - WITH their
frontmatter metadata (status, policy_authority, supersedes) attached.

This metadata preservation is the single most important thing this file
does for solving Challenge 1 and Challenge 4. Without it, a chunk from
the superseded 45-day policy and a chunk from the current 30-day policy
look nearly identical to a similarity search - there'd be no way to tell
them apart at query time. Same for the poisoned draft doc (14-internal-
content-migration-notes.md, policy_authority: none) - if we don't carry
that tag through, retrieval.py has nothing to filter on later.

Run once (and again any time knowledge-base/ changes):
    python -m src.ingestion.pipeline
"""

import os
import glob
import frontmatter

from src.ingestion.chunker import chunk_by_heading
from src.ingestion.embedder import embed_document
from src.ingestion.vectorstore import reset_collection, add_chunks

KB_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "knowledge-base")


def build_index():
    reset_collection()
    files = sorted(glob.glob(os.path.join(KB_DIR, "*.md")))
    print(f"Found {len(files)} knowledge-base files.")

    ids, docs, metadatas, embeddings = [], [], [], []

    for filepath in files:
        filename = os.path.basename(filepath)
        post = frontmatter.load(filepath)
        meta = dict(post.metadata)
        body = post.content

        chunks = chunk_by_heading(body)
        print(f"  {filename}: {len(chunks)} chunk(s) | status={meta.get('status')} authority={meta.get('policy_authority')}")

        for i, chunk in enumerate(chunks):
            chunk_id = f"{filename}::{i}::{chunk['heading']}"
            # Chroma metadata values must be str/int/float/bool - flatten and stringify
            chunk_meta = {
                "filename": filename,
                "heading": chunk["heading"],
                "document_id": str(meta.get("document_id", "")),
                "title": str(meta.get("title", "")),
                "status": str(meta.get("status", "")),
                "policy_authority": str(meta.get("policy_authority", "")),
                "audience": str(meta.get("audience", "")),
                "supersedes": str(meta.get("supersedes", "")),
                "superseded_by": str(meta.get("superseded_by", "")),
                "effective_date": str(meta.get("effective_date", "")),
            }
            embedding = embed_document(chunk["text"])

            ids.append(chunk_id)
            docs.append(chunk["text"])
            metadatas.append(chunk_meta)
            embeddings.append(embedding)

    add_chunks(ids, docs, metadatas, embeddings)
    print(f"\nIndexed {len(ids)} chunks into ChromaDB.")


if __name__ == "__main__":
    build_index()