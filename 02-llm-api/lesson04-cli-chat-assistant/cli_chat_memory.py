import os

import requests
from dotenv import load_dotenv


def extract_output_text(data):
    texts = []

    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                texts.append(content.get("text", ""))

    return "".join(texts)


load_dotenv()

url = "https://api.deepseek.com/responses"
api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError("没有找到环境变量 DEEPSEEK_API_KEY")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

messages = []

print("AI 学习助手已启动，输入 exit 退出。")

while True:
    question = input("你：").strip()

    if question.lower() == "exit":
        print("对话已结束。")
        break

    if not question:
        print("请输入内容。")
        continue

    messages.append({
        "role": "user",
        "content": question
    })
    
    body = {
        "model": "deepseek-v4-flash",
        "instructions": "你是一名 AI 学习助手，请使用中文并从基础开始讲解。",
        "input": messages
    }

    response = requests.post(
        url,
        headers=headers,
        json=body,
        timeout=60
    )

    response.raise_for_status()

    data = response.json()
    answer = extract_output_text(data)
    messages.append({
        "role": "assistant",
        "content": answer
    })
    print("AI：", answer)