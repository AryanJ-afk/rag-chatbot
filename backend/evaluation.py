from langchain_core.documents import Document
from ragas import evaluate, EvaluationDataset
from ragas.metrics import Faithfulness, ResponseRelevancy
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


def score_response(query: str, answer: str, chunks: list[Document]) -> dict:

    judge_llm = LangchainLLMWrapper(
        ChatOpenAI(model="gpt-4o-mini", temperature=0)
    )

    judge_embeddings = LangchainEmbeddingsWrapper(
        OpenAIEmbeddings(model="text-embedding-3-small")
    )

    dataset = EvaluationDataset.from_list([{
        "user_input": query,
        "response": answer,
        "retrieved_contexts": [c.page_content for c in chunks],
    }])

    result = evaluate(
        dataset=dataset,
        metrics=[Faithfulness(), ResponseRelevancy()],
        llm=judge_llm,
        embeddings=judge_embeddings,
    )

    df = result.to_pandas()

    scores = {
        "faithfulness": float(df.loc[0, "faithfulness"]),
        "response_relevancy": float(df.loc[0, "answer_relevancy"]),
    }

    return scores