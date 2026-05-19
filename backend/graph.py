from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.documents import Document
from backend.retriever import retrieve_chunks
from backend.generator import generate_answer
from backend.evaluator import evaluate_answer
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
    faithful: bool
    feedback: str
    retry_count: int
    
def retriever_node(state: RAGState) -> dict:
    chunks = retrieve_chunks(state["query"], state["user_id"], TOP_K)
    print(f"[retriever] running")
    return {"chunks": chunks}

def generator_node(state: RAGState) -> dict:
    past_messages = state.get("messages", [])
    result = generate_answer(state["query"], state["chunks"], past_messages, state.get("faithful", True), state.get("feedback"))
    new_messages = [HumanMessage(content=state["query"]), AIMessage(content=result["answer"])]
    print(f"[generator] running, retry_count={state.get('retry_count', 0)}, faithful={state.get('faithful', 'N/A')}")
    return {"answer": result["answer"], "sources": result["sources"], "messages": new_messages}

def evaluator_node(state: RAGState) -> dict:
    result = evaluate_answer(state["query"], state["answer"], state["chunks"])
    print(f"[evaluator] faithful={result['faithful']}, retry_count will be {state.get('retry_count', 0) + 1}")
    return {
        "faithful": result["faithful"],
        "feedback": result["feedback"],
        "retry_count": state.get("retry_count", 0) + 1,
    }

def route_after_eval(state: RAGState) -> str:
    if state["faithful"]:
        return "end"
    if state.get("retry_count", 0) >= 2:
        return "end"
    return "generator"

builder = StateGraph(RAGState)
builder.add_node("retriever", retriever_node)
builder.add_node("generator", generator_node)
builder.add_edge(START, "retriever")
builder.add_edge("retriever", "generator")
builder.add_node("evaluator", evaluator_node)
builder.add_edge("generator", "evaluator")
builder.add_conditional_edges(
    "evaluator",
    route_after_eval,
    {"generator": "generator", "end": END}
)

graph = builder.compile(checkpointer=memory)