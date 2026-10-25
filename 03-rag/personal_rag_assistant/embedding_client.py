import requests


def embed_text(text, api_url, model, api_key):
    """调用 Embedding API，将文本转换为向量。"""
    if not text.strip():
        raise ValueError("text 不能为空")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    body = {
        "model": model,
        "input": text,
    }

    response = requests.post(
        api_url,
        headers=headers,
        json=body,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()

    try:
        embedding = data["data"][0]["embedding"]
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError("Embedding API 返回的数据格式不正确") from error

    if not isinstance(embedding, list) or not embedding:
        raise ValueError("API 返回的 embedding 必须是非空列表")

    if not all(isinstance(value, (int, float)) for value in embedding):
        raise ValueError("embedding 中的元素必须是数字")

    return embedding