
from src.ingestion.embedder import embed_query
from src.ingestion.vectorstore import query

def retrieve_context(user_message: str, top_k: int = 5) -> str:
    """
    Embeds the user's message, searches ChromaDB, and formats the retrieved chunks.
    It explicitly marks superseded documents so the LLM knows not to use them as active policy.
    """
    # 1. Embed the user's question
    query_embedding = embed_query(user_message)
    
    # 2. Query the vector store
    results = query(query_embedding, n_results=top_k)
    
    if not results['documents'] or not results['documents'][0]:
        return "No relevant context found in the knowledge base."

    formatted_chunks = []
    
    # 3. Format the results, paying attention to the metadata
    for i in range(len(results['documents'][0])):
        doc_text = results['documents'][0][i]
        meta = results['metadatas'][0][i]
        
        status = meta.get('status', 'unknown')
        supersedes = meta.get('supersedes', 'None')
        superseded_by = meta.get('superseded_by', 'None')
        filename = meta.get('filename', 'unknown')
        
        # Build a clear context block for the LLM
        chunk_header = f"--- Document: {filename} (Status: {status}) ---"
        
        # Add warnings if the policy is outdated
        if status.lower() == 'superseded':
            chunk_header += f"\nWARNING: THIS POLICY IS SUPERSEDED BY {superseded_by}. DO NOT ADVISE BASED ON THIS."
            
        chunk_body = f"{chunk_header}\n{doc_text}\n"
        formatted_chunks.append(chunk_body)
        
    return "\n".join(formatted_chunks)

if __name__ == "__main__":
    # Test the retrieval to see if it catches the dishwasher conflict
    test_query = "What is the policy on dishwashers?"
    print(f"Testing Query: '{test_query}'\n")
    print(retrieve_context(test_query))