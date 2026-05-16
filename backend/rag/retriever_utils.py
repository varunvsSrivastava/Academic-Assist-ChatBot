def retrieve_documents(query, vector_store, k=3):
    docs = vector_store.similarity_search(query, k=k)
    
    context = [doc.page_content for doc in docs]
    sources = [doc.metadata.get("source", "unknown") for doc in docs]

    return context, sources