from answer_question import answer_question
from index_storage import load_index
import requests

def run_cli(
    index_path,
    embed_text,
    llm_call,
    input_func=input,
    output_func=print,
):
    """运行个人知识库命令行问答。"""
    try:
        embedded_chunks = load_index(index_path)
    except FileNotFoundError as error:
        output_func(
            f"{error}。请先运行 python index_documents.py 建立索引。"
        )
        return

    if not embedded_chunks:
        output_func(
            "索引中没有可用的文档片段，请检查 knowledge_base/，"
            "然后重新运行 python index_documents.py。"
        )
        return

    output_func("个人知识库问答助手已启动，输入 exit 退出。")

    while True:
        question = input_func("你：").strip()

        if question.lower() == "exit":
            output_func("已退出。")
            break

        if not question:
            output_func("请输入问题。")
            continue

        try:
            result = answer_question(
                question=question,
                embedded_chunks=embedded_chunks,
                embed_text=embed_text,
                llm_call=llm_call,
                k=3,
                score_threshold=0.6,
            )

        except requests.exceptions.Timeout:
            output_func("请求超时，请稍后重新提问。")
            continue
        except requests.exceptions.ConnectionError:
            output_func("无法连接 API，请检查网络后重新提问。")
            continue
        except requests.exceptions.HTTPError:
            output_func("API 返回 HTTP 错误，请检查配置或服务状态。")
            continue

        output_func(f"AI：{result['answer']}")

        if result["sources"]:
            output_func(
                "来源：" + "、".join(result["sources"])
            )

def main():
    from functools import partial
    from pathlib import Path

    from config import load_embedding_config, load_llm_config
    from embedding_client import embed_text
    from llm_client import call_llm

    project_dir = Path(__file__).resolve().parent

    embedding_config = load_embedding_config()
    llm_config = load_llm_config()

    embed = partial(
        embed_text,
        api_url=embedding_config["api_url"],
        model=embedding_config["model"],
        api_key=embedding_config["api_key"],
    )

    llm_call = partial(
        call_llm,
        api_url=llm_config["api_url"],
        model=llm_config["model"],
        api_key=llm_config["api_key"],
    )

    run_cli(
        index_path=project_dir / "data" / "index.json",
        embed_text=embed,
        llm_call=llm_call,
    )

if __name__ == "__main__":
    main()