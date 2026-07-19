import marimo

app = marimo.App()

@app.cell
def __():
    import sys
    sys.path.insert(0, "..")
    return

@app.cell
def __():
    mo.md("# Retrieval Evaluation — Portuguese Food & Wine Guide")
    return

@app.cell
def __():
    questions = [t["question"] for t in TEST_SET]
    expected = [t["source"] for t in TEST_SET]
    print(f"Test set: {len(TEST_SET)} questions")
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
    print(f"Loaded {len(docs)} documents from Qdrant")
    return

@app.cell
def __():
    def hit_rate(results, expected_source, k):
        top = results[:k]
        return 1.0 if any(r["metadata"].get("source") == expected_source for r in top) else 0.0

    def mrr(results, expected_source, k):
        for i, r in enumerate(results[:k]):
            if r["metadata"].get("source") == expected_source:
                return 1.0 / (i + 1)
        return 0.0
    return

@app.cell
def __():
    K_VALUES = [1, 3, 5, 10]
    strategies = {"dense": [], "sparse": [], "hybrid": [], "hybrid+rerank": []}

    for q, src in zip(questions, expected):
        if src == "none":
            for k in K_VALUES:
                strategies["dense"].append({"hit": 0, "mrr": 0})
                strategies["sparse"].append({"hit": 0, "mrr": 0})
                strategies["hybrid"].append({"hit": 0, "mrr": 0})
                strategies["hybrid+rerank"].append({"hit": 0, "mrr": 0})
            continue
        vec = embed_query(q)
        dense_r = dr.search(vec, k=20)
        sparse_r = bm25.search(q, k=20)
        hybrid_r = hybrid_fusion(dense_r, sparse_r, k=20)
        reranked_r = reranker.rerank(q, hybrid_r, top_k=10)

        for k_val in K_VALUES:
            strategies["dense"].append({"hit": hit_rate(dense_r, src, k_val), "mrr": mrr(dense_r, src, k_val)})
            strategies["sparse"].append({"hit": hit_rate(sparse_r, src, k_val), "mrr": mrr(sparse_r, src, k_val)})
            strategies["hybrid"].append({"hit": hit_rate(hybrid_r, src, k_val), "mrr": mrr(hybrid_r, src, k_val)})
            strategies["hybrid+rerank"].append({"hit": hit_rate(reranked_r, src, k_val), "mrr": mrr(reranked_r, src, k_val)})

    def avg_metrics(strat_list, k_vals, metric):
        return [np.mean([strat_list[i][metric] for i in range(k, len(strat_list), len(k_vals))]) for k in range(len(k_vals))]

    rows = []
    for name, data in strategies.items():
        for i, k in enumerate(K_VALUES):
            hits = [data[j]["hit"] for j in range(i, len(data), len(K_VALUES))]
            mrrs = [data[j]["mrr"] for j in range(i, len(data), len(K_VALUES))]
            rows.append({"Strategy": name, "k": k, "Hit Rate": np.mean(hits), "MRR": np.mean(mrrs)})

    results_df = pd.DataFrame(rows)
    print(results_df.to_string(index=False))
    return

@app.cell
def __():
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for metric, ax in zip(["Hit Rate", "MRR"], axes):
        for strat in strategies:
            subset = results_df[results_df["Strategy"] == strat]
            ax.plot(subset["k"], subset[metric], marker="o", label=strat)
        ax.set_xlabel("k")
        ax.set_ylabel(metric)
        ax.set_title(f"{metric} @ k")
        ax.legend()
        ax.grid(True)
    plt.tight_layout()
    plt.show()
    return

@app.cell
def __():
    best_hr = results_df.loc[results_df.groupby("k")["Hit Rate"].idxmax()]
    best_mrr = results_df.loc[results_df.groupby("k")["MRR"].idxmax()]
    mo.md(f"""
    ### Best Strategy by k
    **Hit Rate**: {best_hr[['k','Strategy','Hit Rate']].to_string(index=False)}
    **MRR**: {best_mrr[['k','Strategy','MRR']].to_string(index=False)}
    """)
    return

if __name__ == "__main__":
    app.run()
