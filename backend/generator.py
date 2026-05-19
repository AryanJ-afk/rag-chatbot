from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

def generate_answer(query: str, chunks: list[Document], past_messages: list[BaseMessage] = None, faithful=True, feedback=None) -> dict:
    past_messages = past_messages or []
    context_string = ""
    for i in chunks:
        context_string += f"[Source: {i.metadata["source"]}, Page {i.metadata["page"]}]\n{i.page_content}" + "\n"
    
    llm = ChatOpenAI(model='gpt-5-nano', temperature=0)
    
    system_message = SystemMessage(content="You are a RAG assistant. Answer the question using ONLY the provided context. If the answer isn't in the context, say \"I don't know based on the provided documents\". Answer in complete sentences and avoid bullet points unless explicitly asked.")
    if not faithful:
        human_message = HumanMessage(content=f"Context:\n{context_string}\n\nQuestion: {query}.\n\nNote: Your previous answer was flagged as not faithful to the context. Feedback: {feedback}. Try again, being strictly grounded in the provided sources.")
    else:
        human_message = HumanMessage(content=f"Context:\n{context_string}\n\nQuestion: {query}.")

    response = llm.invoke([system_message, *past_messages, human_message])
    answer = response.content
    
    seen = set()
    sources = []
    for chunk in chunks:
        key = (chunk.metadata['source'], chunk.metadata['page'])
        if key not in seen:
            seen.add(key)
            sources.append({"source": chunk.metadata['source'], "page": chunk.metadata['page']})
        
    return {"answer": answer, "sources": sources}
