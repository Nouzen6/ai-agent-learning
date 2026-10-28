from vector_search import search_chunks
from reranker import rerank_results

def retrieve_for_query(
    question,
    embedded_chunks,
    embed_text,
    k=3,
    score_threshold=None,
):
    """将用户问题向量化，并检索相关 chunks。"""
    if not question.strip():
        raise ValueError("question 不能为空")

    query_embedding = embed_text(question)

    return search_chunks(
        query_embedding=query_embedding,
        embedded_chunks=embedded_chunks,
        k=k,
        score_threshold=score_threshold,
    )

def retrieve_and_rerank(
    question,
    embedded_chunks,
    embed_text,
    score_func,
    candidate_k=10,
    final_k=3,
    score_threshold=None,
):
    """先检索候选，再重排并选择最终片段。"""
    if final_k <= 0:
        raise ValueError("final_k 必须大于 0")

    candidates = retrieve_for_query(
        question=question,
        embedded_chunks=embedded_chunks,
        embed_text=embed_text,
        k=candidate_k,
        score_threshold=score_threshold,
    )

    return rerank_results(
        question=question,
        candidates=candidates,
        score_func=score_func,
        final_k=final_k,
    )