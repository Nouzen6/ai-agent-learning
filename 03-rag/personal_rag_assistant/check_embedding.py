from functools import partial

from config import load_embedding_config
from embedding_client import embed_text


def main():
    config = load_embedding_config()

    embed = partial(
        embed_text,
        api_url=config["api_url"],
        model=config["model"],
        api_key=config["api_key"],
    )

    vector = embed("网络请求失败时，可以捕获 ConnectionError。")

    print("Embedding 请求成功。")
    print("向量维度：", len(vector))
    print("前 5 个数字：", vector[:5])


if __name__ == "__main__":
    main()