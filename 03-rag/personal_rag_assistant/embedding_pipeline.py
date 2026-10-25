def add_embeddings(chunks, embed_text):
    """为每个 chunk 生成 embedding，并返回新的 chunk 列表。"""
    embedded_chunks = []

    for chunk in chunks:
        embedding = embed_text(chunk["text"])

        if not isinstance(embedding, list) or not embedding:
            raise ValueError("embed_text 必须返回非空列表")

        if not all(
            isinstance(value, (int, float))
            for value in embedding
        ):
            raise ValueError("embedding 中的元素必须是数字")

        embedded_chunk = chunk.copy()
        embedded_chunk["embedding"] = embedding

        embedded_chunks.append(embedded_chunk)

    return embedded_chunks