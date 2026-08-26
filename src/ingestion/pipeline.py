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