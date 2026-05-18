from langchain_core.documents import Document
from .vector_store import vector_store


def retrieve_chunks(query: str, user_id: str, k: int = 4) -> list[Document]:
    
    results = vector_store.similarity_search(
        query=query,
        k=k,
        filter={"user_id": user_id}
    )
    
    return results