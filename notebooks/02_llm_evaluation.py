import marimo
app = marimo.App()

@app.cell
def __():
    import sys
    sys.path.insert(0, "..")
    import json
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from openai import OpenAI
    from src.evaluation.test_set import TEST_SET
    from src.search.dense import DenseRetriever
    from src.search.bm25 import BM25Retriever
    from src.search.hybrid import hybrid_fusion
    from src.search.reranker import Reranker
    from src.search.query_rewriter import rewrite_query
    from src.api.answer import generate_answer
    from src.ingestion.embedding import embed_query
    client = OpenAI()
    return

@app.cell
def __():
    mo.md("# LLM Evaluation — Portuguese Food & Wine Guide")
    return

@app.cell
def __():
    dr = DenseRetriever()
    bm25 = BM25Retriever()
    reranker = Reranker()

    points, _ = dr.client.scroll(collection_name=dr.collection, limit=10000)
    docs = [{"id": p.id, "text": p.payload.get("text", ""),
             "metadata": {"source": p.payload.get("source", ""),
                          "title": p.payload.get("title", ""),
                          "language": p.payload.get("language", ""),
                          "url": p.payload.get("url", "")}} for p in points]
    bm25.index(docs)
    print(f"Loaded {len(docs)} documents")
    return

@app.cell
def __():
    def run_rag(question):
        rewritten = rewrite_query(question)
        vec = embed_query(rewritten)
        dense_r = dr.search(vec, k=20)
        sparse_r = bm25.search(rewritten, k=20)
        fused = hybrid_fusion(dense_r, sparse_r, k=20)
        top = reranker.rerank(rewritten, fused, top_k=5)
        if not top:
            return "Não tenho informação suficiente na base de conhecimento para responder a essa pergunta.", [], ""
        answer, citations, *_ = generate_answer(question, top, model="gpt-4o", client=client)
        context = "\n".join(f"[{i+1}] {d['text'][:200]}" for i, d in enumerate(top))
        return answer, citations, context
    return

@app.cell
def __():
    results = []
    for item in TEST_SET:
        q = item["question"]
        expected = item["answer"]
        answer, citations, context = run_rag(q)
        results.append({"question": q, "expected": expected[:100], "answer": answer[:200], "context": context[:500]})
        print(f"  ✓ {q[:50]}...")
    print(f"Evaluated {len(results)} questions")
    return

@app.cell
def __():
    judge_prompt = """You are evaluating a RAG system that answers questions about Portuguese food and wine.
    Rate the following answer on two criteria:
    1. Relevance (1-5): Does the answer directly address the user's question?
    2. Faithfulness (1-5): Does the answer contain information NOT present in the provided context? (5 = fully faithful, 1 = hallucinated)

    Question: {question}
    Context: {context}
    Answer: {answer}

    Respond ONLY with a JSON object: {{"relevance": int, "faithfulness": int}}"""

    scores = []
    for r in results:
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": judge_prompt.format(
                    question=r["question"], context=r["context"][:1000], answer=r["answer"])}],
                response_format={"type": "json_object"}
            )
            score = json.loads(resp.choices[0].message.content)
            scores.append(score)
        except Exception:
            scores.append({"relevance": 0, "faithfulness": 0})
    return

@app.cell
def __():
    df = pd.DataFrame(scores)
    print(f"Average Relevance: {df['relevance'].mean():.2f}/5")
    print(f"Average Faithfulness: {df['faithfulness'].mean():.2f}/5")
    print()
    print(df.describe().to_string())
    return

@app.cell
def __():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, metric in zip(axes, ["relevance", "faithfulness"]):
        ax.hist(df[metric], bins=5, range=(0.5, 5.5), edgecolor="black", alpha=0.7)
        ax.set_title(f"{metric.capitalize()} Distribution")
        ax.set_xlabel("Score")
        ax.set_ylabel("Count")
        ax.set_xticks(range(1, 6))
    plt.tight_layout()
    plt.show()
    return

@app.cell
def __():
    mo.md(f"""
    ### Summary
    - **Relevance**: {df['relevance'].mean():.2f}/5 — {"Good" if df['relevance'].mean() >= 4 else "Needs improvement"}
    - **Faithfulness**: {df['faithfulness'].mean():.2f}/5 — {"Good" if df['faithfulness'].mean() >= 4 else "Needs improvement"}
    - Samples evaluated: {len(results)}
    """)
    return

if __name__ == "__main__":
    app.run()
