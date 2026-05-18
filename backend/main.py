from fastapi import FastAPI, UploadFile, HTTPException, File, Form
from backend.s3_client import upload_file_to_s3
from backend.ingest import ingest_pdf
from backend.vector_store import vector_store
from backend.retriever import retrieve_chunks
from backend.generator import generate_answer
from backend.graph import graph
from pydantic import BaseModel

app = FastAPI()

TOP_K = 3
class QueryRequest(BaseModel):
    query: str
    user_id: str
    thread_id: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/upload")
async def upload(file: UploadFile = File(...), user_id: str = Form(...)):
    
    if file.content_type != "application/pdf":
        raise HTTPException(400, detail="Invalid document type")

    file_bytes = await file.read()
    response = upload_file_to_s3(file_bytes, file.filename, user_id)
    response["messaage"] = "success"
    
    response2 = ingest_pdf(response["s3_key"], user_id)
    print(response2)
    return response

@app.post("/query")
def post_query(req: QueryRequest) -> dict:
    
    config = {"configurable": {"thread_id": req.thread_id}}
    initial_state = {"query": req.query, "user_id": req.user_id}
    
    final_state = graph.invoke(initial_state, config=config)
    
    return {
        "answer": final_state["answer"],
        "sources": final_state["sources"]
    }

@app.get("/debug/count")
def debug_count():
    print(vector_store._collection.count())