import math


def cosine_similarity(vector_a, vector_b):
    """计算两个向量的余弦相似度。"""
    if len(vector_a) != len(vector_b):
        raise ValueError("两个向量的维度必须相同")

    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )
    norm_a = math.sqrt(sum(value * value for value in vector_a))
    norm_b = math.sqrt(sum(value * value for value in vector_b))

    if norm_a == 0 or norm_b == 0:
        raise ValueError("向量不能是零向量")

    return dot_product / (norm_a * norm_b)


def search_chunks(
    query_embedding,
    embedded_chunks,
    k=3,
    score_threshold=None,
):
    """根据问题向量检索最相关的 chunk。"""
    if k <= 0:
        raise ValueError("k 必须大于 0")

    scored_chunks = []

    for chunk in embedded_chunks:
        score = cosine_similarity(
            query_embedding,
            chunk["embedding"],
        )

        if (
            score_threshold is not None
            and score < score_threshold
        ):
            continue

        result = {
            "id": chunk["id"],
            "score": score,
            "text": chunk["text"],
            "metadata": chunk["metadata"].copy(),
        }
        scored_chunks.append(result)

    scored_chunks.sort(
        key=lambda result: result["score"],
        reverse=True,
    )

    return scored_chunks[:k]