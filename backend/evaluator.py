from pydantic import BaseModel
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from typing import Literal
from langchain_openai import ChatOpenAI

class EvaluationResult(BaseModel):
    faithful: bool
    feedback: str
    
def evaluate_answer(query: str, response: str, chunks: list[Document]) -> dict:
    
    context_string = ""
    for i in chunks:
        context_string += f"[Source: {i.metadata["source"]}, Page {i.metadata["page"]}]\n{i.page_content}" + "\n"
    
    llm = ChatOpenAI(model='gpt-5-nano', temperature=0)
    llm_with_schema = llm.with_structured_output(EvaluationResult)
    
    system_message = SystemMessage(content="You are a RAG response evaluator. You must verify the answer to the query is correct and it sourced accurately. If faithful=false, feedback must explain which specific claim is unsupported by the context. If faithful=true, feedback can be empty or a brief confirmation.")
    human_message = HumanMessage(content=f"Context:\n{context_string}\n\nQuery: {query}\nResponse: {response}")
    
    feedback = llm_with_schema.invoke([system_message, human_message])
    
    return {"faithful": feedback.faithful, "feedback": feedback.feedback}
    