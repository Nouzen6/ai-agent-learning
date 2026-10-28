from answer_question import answer_question
from index_storage import load_index
import requests


def run_cli(
    index_path,
    embed_text,
    llm_call,
    input_func=input,
    output_func=print,
    score_func=None,
    candidate_k=10,
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
                score_func=score_func,
                candidate_k=candidate_k,
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
        except ValueError as error:
            output_func(f"处理失败：{error}")
            continue

        output_func(f"AI：{result['answer']}")

        if result["sources"]:
            output_func("提供给模型的资料：")

            for source_info in result["sources"]:
                output_func(
                    f"{source_info['citation']} "
                    f"{source_info['source']}，"
                    f"片段 {source_info['chunk_index']}"
                )

def main():
    from functools import partial
    from pathlib import Path

    from config import load_embedding_config, load_llm_config
    from embedding_client import embed_text
    from llm_client import call_llm
    import argparse

    from config import load_rerank_config
    from rerank_client import score_text

    project_dir = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(
        description="个人知识库问答助手"
    )
    parser.add_argument(
        "--rerank",
        action="store_true",
        help="启用第二阶段重排序",
    )

    args = parser.parse_args()
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
    score_func = None

    if args.rerank:
        try:
            rerank_config = load_rerank_config()
        except ValueError as error:
            print(f"配置错误：{error}")
            return

        score_func = partial(
            score_text,
            api_url=rerank_config["api_url"],
            model=rerank_config["model"],
            api_key=rerank_config["api_key"],
        )
    run_cli(
        index_path=project_dir / "data" / "index.json",
        embed_text=embed,
        llm_call=llm_call,
        score_func=score_func,
        candidate_k=10,
    )

if __name__ == "__main__":
    main()