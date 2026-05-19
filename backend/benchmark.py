import requests
import json

URL = "http://localhost:8000/query"
USER_ID = "aryan_jha"
QUERIES = [
    "What is the difference between MLlib and Spark ML?",
    "What is a LabeledPoint?",
    "How does the Random Forest algorithm work?",
    "What is the F-measure and how is it calculated?",
    "What's the difference between supervised and unsupervised learning?",
    "What does the Tokenizer transformer do?",
    "How does k-fold cross validation work in Spark ML?",
    "What is the ALS algorithm used for?",
    "What is the difference between a Transformer and an Estimator?",
    "What evaluation metric does the BinaryClassificationMetrics class compute?",
]

for q in QUERIES:
    r = requests.post(URL, json={"query": q, "user_id": USER_ID, "thread_id": "bench-1"})

faithfulness_scores = []
response_relevancy_scores = []

with open("logs/results.jsonl", "r") as f:
    for line in f:
        if not line.strip():
            continue

        obj = json.loads(line)

        faithfulness_scores.append(obj["faithfulness"])
        response_relevancy_scores.append(obj["response_relevancy"])

avg_faithfulness = sum(faithfulness_scores) / len(faithfulness_scores)
avg_response_relevancy = sum(response_relevancy_scores) / len(response_relevancy_scores)

print("Average faithfulness:", avg_faithfulness)
print("Average response relevancy:", avg_response_relevancy)