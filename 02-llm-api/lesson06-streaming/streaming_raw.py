import os
import requests
from dotenv import load_dotenv

API_URL = "https://api.deepseek.com/responses"
MODEL = "deepseek-v4-flash"
INSTRUCTION = "请使用中文回答"

def main():
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        raise ValueError("请在环境变量中设置 DEEPSEEK_API_KEY")
    print("是否读取到密钥：", bool(api_key))
    print("密钥长度：", len(api_key) if api_key else 0)
    headers = {
        "Authorization":f"Bearer {api_key}",

        "Content-Type":"application/json"

    }

    body={
        "model":MODEL,
        "instructions":INSTRUCTION,
        "input":"请用一句话解释什么是流式输出。",
        "stream":True
    }

    with requests.post(
        API_URL,
        headers=headers,
        json=body,
        stream=True,
        timeout=60
    ) as response:
        response.raise_for_status()
        response.encoding = "utf-8"
        for line in response.iter_lines(decode_unicode=True):
            if line:
                print(repr(line))


if __name__ == "__main__":
    main()