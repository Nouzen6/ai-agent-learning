from document_loader import load_documents
from embedding_pipeline import add_embeddings
from index_storage import save_index
from text_chunker import clean_text, chunk_documents


def build_index(
    knowledge_base_dir,
    index_path,
    embed_text,
    chunk_size=500,
    overlap=50,
):
    """读取知识库，生成并保存带向量的索引。"""
    documents = load_documents(knowledge_base_dir)

    cleaned_documents = [
        {
            "text": clean_text(document["text"]),
            "metadata": document["metadata"].copy(),
        }
        for document in documents
    ]

    chunks = chunk_documents(
        cleaned_documents,
        chunk_size=chunk_size,
        overlap=overlap,
    )
    embedded_chunks = add_embeddings(chunks, embed_text)
    save_index(embedded_chunks, index_path)

    return embedded_chunks

def main():
    from functools import partial
    from pathlib import Path

    from config import load_embedding_config
    from embedding_client import embed_text
    from index_storage import load_index

    project_dir = Path(__file__).resolve().parent
    index_path = project_dir / "data" / "index.json"

    if index_path.exists():
        raise FileExistsError("索引已存在，先不要重复生成。")

    config = load_embedding_config()
    embed = partial(
        embed_text,
        api_url=config["api_url"],
        model=config["model"],
        api_key=config["api_key"],
    )

    chunks = build_index(
        knowledge_base_dir=project_dir / "knowledge_base",
        index_path=index_path,
        embed_text=embed,
    )

    loaded_chunks = load_index(index_path)

    print("chunk 数量：", len(chunks))
    print("保存与加载一致：", chunks == loaded_chunks)

    if loaded_chunks:
        print(
            "全部向量都是 1024 维：",
            all(len(chunk["embedding"]) == 1024
                for chunk in loaded_chunks),
        )
    else:
        print("索引为空，请检查知识库是否包含有效文本。")


if __name__ == "__main__":
    main()