from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.documents import Document
from backend.retriever import retrieve_chunks
from backend.generator import generate_answer
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

TOP_K = 4

memory = MemorySaver()

class RAGState(TypedDict):
    query: str
    user_id: str
    chunks: list[Document]
    answer: str
    sources: list[dict]
    messages: Annotated[list[BaseMessage], add_messages]
    
def retriever_node(state: RAGState) -> dict:
    chunks = retrieve_chunks(state["query"], state["user_id"], TOP_K)
    return {"chunks": chunks}

def generator_node(state: RAGState) -> dict:
    past_messages = state.get("messages", [])
    result = generate_answer(state["query"], state["chunks"], past_messages)
    new_messages = [HumanMessage(content=state["query"]), AIMessage(content=result["answer"])]
    return {"answer": result["answer"], "sources": result["sources"], "messages": new_messages}

builder = StateGraph(RAGState)
builder.add_node("retriever", retriever_node)
builder.add_node("generator", generator_node)
builder.add_edge(START, "retriever")
builder.add_edge("retriever", "generator")
builder.add_edge("generator", END)

graph = builder.compile(checkpointer=memory)