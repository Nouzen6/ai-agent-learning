import math


def cosine_similarity(vector_a, vector_b):
    """计算两个向量的余弦相似度。"""
    if len(vector_a) != len(vector_b):
        raise ValueError("向量长度必须相同")

    if len(vector_a) == 0:
        raise ValueError("向量不能为空")

    dot_product = sum(
        value_a * value_b
        for value_a, value_b in zip(vector_a, vector_b)
    )

    norm_a = math.sqrt(
        sum(value * value for value in vector_a)
    )

    norm_b = math.sqrt(
        sum(value * value for value in vector_b)
    )

    if norm_a == 0 or norm_b == 0:
        raise ValueError("零向量不能计算余弦相似度")

    return dot_product / (norm_a * norm_b)

def retrieve_top_k(query_vector, documents, k, score_threshold=None):
    """根据余弦相似度返回最相关的前 k 个文档。"""
    if k <= 0:
        raise ValueError("k 必须大于 0")

    scored_documents = []

    for document in documents:
        score = cosine_similarity(
            query_vector,
            document["vector"],
        )

        if score_threshold is not None and score < score_threshold:
            continue

        scored_documents.append(
            {
                "id": document["id"],
                "score": score,
                "text": document["text"],
                "metadata": document["metadata"],
            }
        )

    scored_documents.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return scored_documents[:k]

if __name__ == "__main__":
    documents = [
        {
            "id": "chunk-a",
            "vector": [1, 0],
            "text": "requests 网络请求失败时，可以捕获 ConnectionError。",
            "metadata": {
                "source": "02-llm-api/README.md",
                "chunk_id": 1,
            },
        },
        {
            "id": "chunk-b",
            "vector": [0.8, 0.6],
            "text": "JSON 文件可以使用 json.dump() 保存。",
            "metadata": {
                "source": "00-python-basic/README.md",
                "chunk_id": 2,
            },
        },
        {
            "id": "chunk-c",
            "vector": [0, 1],
            "text": "虚拟环境可以使用 venv 创建。",
            "metadata": {
                "source": "00-python-basic/README.md",
                "chunk_id": 3,
            },
        },
    ]

    query_vector = [1, 0]
    results = retrieve_top_k(query_vector, documents, k=2)

    for rank, result in enumerate(results, start=1):
        print(
            f"排名 {rank}："
            f"{result['id']}，"
            f"相似度 {result['score']:.2f}"
        )
        print(f"文本：{result['text']}")
        print(f"来源：{result['metadata']['source']}")
        print()

    print("不使用阈值：")
    results = retrieve_top_k(query_vector, documents, k=3)

    for rank, result in enumerate(results, start=1):
        print(
            f"排名 {rank}："
            f"{result['id']}，"
            f"相似度 {result['score']:.2f}"
        )

    print()

    print("使用阈值 0.7：")
    filtered_results = retrieve_top_k(
        query_vector,
        documents,
        k=3,
        score_threshold=0.7,
    )

    for rank, result in enumerate(filtered_results, start=1):
        print(
            f"排名 {rank}："
            f"{result['id']}，"
            f"相似度 {result['score']:.2f}"
        )