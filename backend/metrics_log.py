from datetime import datetime, timezone
import json
import os

def log_metrics(query: str, answer: str, scores: dict, user_id: str, thread_id: str):
    os.makedirs("logs", exist_ok=True)
    
    data = {"timestamp": datetime.now(timezone.utc).isoformat(), 
            "user_id": user_id, 
            "thread_id": thread_id, 
            "query": query, 
            "answer": answer, 
            "faithfulness": scores["faithfulness"], 
            "response_relevancy": scores["response_relevancy"]}
    
    with open("logs/results.jsonl", "a") as f:
        f.write(json.dumps(data) + "\n")
        f.close()
    
    