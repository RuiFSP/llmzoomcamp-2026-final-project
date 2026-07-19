# Evaluation Results

## Retrieval Metrics

| Strategy | Hit Rate@1 | Hit Rate@3 | Hit Rate@5 | MRR@10 |
|---|---|---|---|---|
| Dense only (e5-small) | 11% | 33% | 48% | 0.34 |
| Sparse only (BM25) | 7% | 26% | 41% | 0.28 |
| Hybrid (RRF fusion) | 15% | 37% | 52% | 0.39 |
| Hybrid + Re-ranker | 19% | 44% | 48% | 0.36 |

## LLM Answer Quality

| Metric | Score |
|---|---|
| Relevance (1–5) | 3.04 / 5 |
| Faithfulness (1–5) | 5.00 / 5 |

> Evaluated on a test set of 27 curated QA pairs (Wikipedia, Infovini, MDPI). Retrieval metrics across k=[1,3,5,10]. LLM quality scored by GPT-4o-mini-as-judge. See `notebooks/` for reproduction.
