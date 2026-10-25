import json
from pathlib import Path


def save_index(chunks, path):
    """将带 embedding 的 chunks 保存为 JSON 文件。"""
    index_path = Path(path)
    index_path.parent.mkdir(parents=True, exist_ok=True)

    with index_path.open("w", encoding="utf-8") as file:
        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=2,
        )


def load_index(path):
    """从 JSON 文件加载带 embedding 的 chunks。"""
    index_path = Path(path)

    if not index_path.exists():
        raise FileNotFoundError(
            f"索引文件不存在：{index_path}"
        )

    with index_path.open("r", encoding="utf-8") as file:
        chunks = json.load(file)

    if not isinstance(chunks, list):
        raise ValueError("索引内容必须是列表")

    return chunks