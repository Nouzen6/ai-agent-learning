import os
import requests
from dotenv import load_dotenv

def extract_output_text(data):
    text=[]

    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                text.append(content.get("text", ""))

    return "".join(text)

load_dotenv()
url = "https://api.deepseek.com/responses"
api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError("没有找到环境变量 DEEPSEEK_API_KEY")

headers = {
    "Authorization":f"Bearer {api_key}",
    "Content-Type":"application/json"
}

question = input("你：")

body ={
    "model": "deepseek-v4-flash",
    "instrutions": "你是一名 AI 学习助手，请使用中文并从基础开始讲解。",
    "input": question
}

response = requests.post(url, headers=headers, json=body, timeout=60)

response.raise_for_status()

data = response.json()
answer = extract_output_text(data)

print("AI：", answer)