import json
import os

import requests
from dotenv import load_dotenv

API_URL="https://api.deepseek.com/responses"
MODEL="deepseek-v4-flash"
INSTRUCTION="你是一名中文 AI 学习助手，请从基础开始，通俗地解释问题。"

def stream_answer(api_key,prompt):
    headers={
        "Authorization":f"Bearer {api_key}",
        "Content-Type":"application/json"
    }

    body={
        "model": MODEL,
        "instructions": INSTRUCTION,
        "input": prompt,
        "stream": True,
    }

    chunks = []

    with requests.post(API_URL,headers=headers,json=body,stream=True,timeout=60) as response:
        response.raise_for_status()
        response.encoding = "utf-8"

        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            if not line.startswith("data: "):
                continue

            json_text=line.removeprefix("data: ")
            data=json.loads(json_text)

            if data.get("type") != "response.output_text.delta":
                continue

            delta=data.get("delta","")

            print(delta,end="",flush=True)
            chunks.append(delta)

    print()

    return "".join(chunks)

def main():
    load_dotenv()

    api_key=os.getenv("DEEPSEEK_API_KEY")
    print("是否读取到密钥：", bool(api_key))
    print("密钥长度：", len(api_key) if api_key else 0)

    if not api_key:
        raise ValueError("请在环境变量中设置 DEEPSEEK_API_KEY")

    print("AI学习助手已启动，输入exit退出。")

    while True:
        prompt=input("\n你：").strip()

        if prompt.lower()=="exit":
            print("已退出AI学习助手")
            break

        if not prompt:
            print("请输入问题。")
            continue

        try:
            print("AI:",end="")
            stream_answer(api_key,prompt)
        except requests.exceptions.Timeout:
            print("\n请求超时，请稍后重试。")
        except requests.exceptions.ConnectionError:
            print("\n无法连接 API，请检查网络。")
        except requests.exceptions.RequestException as error:
            print(f"\nAPI 请求失败：{error}")
        except json.JSONDecodeError:
            print("\n服务器返回的数据格式异常。")

if __name__ == "__main__":
    main()
        


