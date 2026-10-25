import json

import requests


def call_llm(prompt, api_url, model, api_key):
    """发送 Prompt，收集流式答案并返回字符串。"""
    if not prompt.strip():
        raise ValueError("prompt 不能为空")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model,
        "input": prompt,
        "stream": True,
    }

    chunks = []

    with requests.post(
        api_url,
        headers=headers,
        json=body,
        stream=True,
        timeout=60,
    ) as response:
        response.raise_for_status()
        response.encoding = "utf-8"

        for line in response.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue

            json_text = line.removeprefix("data: ")
            if json_text == "[DONE]":
                break

            data = json.loads(json_text)
            if data.get("type") == "response.output_text.delta":
                chunks.append(data.get("delta", ""))

    answer = "".join(chunks)
    if not answer.strip():
        raise ValueError("LLM API 没有返回有效答案")

    return answer