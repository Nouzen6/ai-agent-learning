def rerank_results(question, candidates, score_func, final_k=3):
    """对候选重新评分，并选择排名靠前的片段。"""
    if final_k <= 0:
        raise ValueError("final_k 必须大于 0")

    scored_results = []

    for candidate in candidates:
        result = candidate.copy()
        result["rerank_score"] = score_func(
            question,
            candidate["text"],
        )
        scored_results.append(result)

    scored_results.sort(
        key=lambda item: item["rerank_score"],
        reverse=True,
    )

    return scored_results[:final_k]