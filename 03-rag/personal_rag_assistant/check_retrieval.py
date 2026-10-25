from functools import partial
from pathlib import Path

from config import load_embedding_config
from embedding_client import embed_text
from index_storage import load_index
from query_pipeline import retrieve_for_query


def main():
    project_dir = Path(__file__).resolve().parent
    chunks = load_index(project_dir / "data" / "index.json")

    config = load_embedding_config()
    embed = partial(embed_text, **config)

    results = retrieve_for_query(
        question="LLM API 请求失败时应该如何处理？",
        embedded_chunks=chunks,
        embed_text=embed,
        k=3,
        score_threshold=None,
    )

    for rank, result in enumerate(results, start=1):
        print(f"排名：{rank}，分数：{result['score']:.4f}")
        print("来源：", result["metadata"]["source"])
        print("内容：", result["text"])
        print()


if __name__ == "__main__":
    main()