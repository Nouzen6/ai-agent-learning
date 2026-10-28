import math

import requests


def score_text(question, text, api_url, model, api_key):
    """调用重排接口，为问题与单个片段取得相关性评分。"""
    if not question.strip() or not text.strip():
        raise ValueError("question 和 text 不能为空")

    response = requests.post(
        api_url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "query": question,
            "documents": [text],
            "top_n": 1,
            "return_documents": False,
        },
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()

    try:
        result = data["results"][0]
        index = result["index"]
        score = result["relevance_score"]
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError("Rerank API 返回的数据格式不正确") from error

    if index != 0:
        raise ValueError("Rerank API 返回的片段位置不正确")

    if type(score) not in (int, float) or not math.isfinite(score):
        raise ValueError("relevance_score 必须是有限数字")

    return score