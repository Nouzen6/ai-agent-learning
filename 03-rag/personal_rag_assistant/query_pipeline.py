from vector_search import search_chunks


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