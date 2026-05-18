from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

def generate_answer(query: str, chunks: list[Document], past_messages: list[BaseMessage] = None) -> dict:
    
    context_string = ""
    for i in chunks:
        context_string += f"[Source: {i.metadata["source"]}, Page {i.metadata["page"]}]\n{i.page_content}" + "\n"
    
    llm = ChatOpenAI(model='gpt-5-nano', temperature=0)
    
    system_message = SystemMessage(content="You are a RAG assistant. Answer the question using ONLY the provided context. If the answer isn't in the context, say \"I don't know based on the provided documents\"")
    human_message = HumanMessage(content=f"Context:\n{context_string}\n\nQuestion: {query}")
    
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
