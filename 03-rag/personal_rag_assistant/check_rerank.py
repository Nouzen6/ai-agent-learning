candidates = [
    {"id": "A", "score": 0.85, "rerank_score": 0.40},
    {"id": "B", "score": 0.78, "rerank_score": 0.92},
    {"id": "C", "score": 0.70, "rerank_score": 0.60},
]

reranked = sorted(
    candidates,
    key=lambda item: item["rerank_score"],
    reverse=True,
)

print("第一轮排名：", [item["id"] for item in candidates])
print("重排序排名：", [item["id"] for item in reranked])