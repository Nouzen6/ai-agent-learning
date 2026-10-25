def clean_text(text):
    """清洗文本格式，但不改变文本含义。"""
    normalized_text = text.replace("\r\n", "\n").replace("\r", "\n")

    cleaned_lines = [
        line.rstrip()
        for line in normalized_text.split("\n")
    ]

    cleaned_text = "\n".join(cleaned_lines)

    while "\n\n\n" in cleaned_text:
        cleaned_text = cleaned_text.replace("\n\n\n", "\n\n")

    return cleaned_text.strip()

def split_text(text, chunk_size, overlap=0):
    """按固定长度切分文本，并允许相邻 chunk 重叠。"""
    if chunk_size <= 0:
        raise ValueError("chunk_size 必须大于 0")

    if overlap < 0:
        raise ValueError("overlap 不能小于 0")

    if overlap >= chunk_size:
        raise ValueError("overlap 必须小于 chunk_size")

    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(text), step):
        chunk = text[start:start + chunk_size]

        if not chunk:
            break

        chunks.append(chunk)

        if start + chunk_size >= len(text):
            break


    return chunks

def chunk_documents(documents, chunk_size, overlap=0):
    """将文档切成 chunks，并保留来源和片段编号。"""
    all_chunks = []

    for document in documents:
        source = document["metadata"]["source"]
        text_chunks = split_text(
            document["text"],
            chunk_size,
            overlap,
        )

        for chunk_index, chunk_text in enumerate(text_chunks):
            metadata = document["metadata"].copy()
            metadata["chunk_index"] = chunk_index

            all_chunks.append(
                {
                    "id": f"{source}::chunk-{chunk_index:04d}",
                    "text": chunk_text,
                    "metadata": metadata,
                }
            )

    return all_chunks