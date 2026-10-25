from pathlib import Path


SUPPORTED_SUFFIXES = {".md", ".txt"}


def load_documents(knowledge_base_dir):
    """读取知识库中的 Markdown 和 TXT 文档。"""
    knowledge_base_path = Path(knowledge_base_dir)

    if not knowledge_base_path.exists():
        raise FileNotFoundError(
            f"知识库目录不存在：{knowledge_base_path}"
        )

    documents = []

    for file_path in sorted(knowledge_base_path.rglob("*")):
        if not file_path.is_file():
            continue

        suffix = file_path.suffix.lower()
        if suffix not in SUPPORTED_SUFFIXES:
            continue

        text = file_path.read_text(encoding="utf-8")
        source = file_path.relative_to(knowledge_base_path).as_posix()

        documents.append(
            {
                "text": text,
                "metadata": {
                    "source": source,
                    "file_type": suffix,
                },
            }
        )

    return documents