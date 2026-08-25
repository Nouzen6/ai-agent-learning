import json
import os

import requests
from dotenv import load_dotenv


API_URL = "https://api.deepseek.com/responses"
MODEL = "deepseek-v4-flash"
INSTRUCTION = "请使用中文回答"


def stream_answer(api_key, prompt):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    body = {
        "model": MODEL,
        "instructions": INSTRUCTION,
        "input": prompt,
        "stream": True,
    }

    chunks = []

    with requests.post(
        API_URL,
        headers=headers,
        json=body,
        stream=True,
        timeout=60,
    ) as response:
        response.raise_for_status()
        response.encoding = "utf-8"

        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue

            if not line.startswith("data: "):
                continue

            json_text = line.removeprefix("data: ")
            data = json.loads(json_text)

            if data.get("type") != "response.output_text.delta":
                continue

            delta = data.get("delta", "")

            print(delta, end="", flush=True)
            chunks.append(delta)

    print()

    return "".join(chunks)


def main():
    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        raise ValueError("请在环境变量中设置 DEEPSEEK_API_KEY")

    answer = stream_answer(
        api_key,
        "请用一句话解释什么是流式输出。",
    )

    print("完整回答长度：", len(answer))


if __name__ == "__main__":
    main()