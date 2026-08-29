import json
import os

import requests
from dotenv import load_dotenv
from validate_json import validate_learning_result

API_URL = "https://api.deepseek.com/responses"
MODEL = "deepseek-v4-flash"
INSTRUCTION = (
    "你是一个学习分析助手。"
    "请只返回合法 JSON，不要返回 Markdown、解释文字或代码块。"
)


def extract_output_text(data):
    texts = []

    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                texts.append(content.get("text", ""))

    return "".join(texts)


def call_llm(api_key, learning_record):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    body = {
        "model": MODEL,
        "instructions": INSTRUCTION,
        "input": (
            "请分析下面的学习记录，并严格返回一个 JSON 对象。\n"
            "JSON 必须包含 topic、level、next_step 三个字符串字段。\n"
            "学习记录：\n"
            f"{learning_record}"
        ),
        "stream": False,
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=body,
        timeout=60,
    )

    response.raise_for_status()

    data = response.json()
    answer_text = extract_output_text(data)

    if not answer_text:
        raise ValueError("API 响应中没有找到文本回答")

    return answer_text

def parse_learning_result(answer_text):
    try:
        result = json.loads(answer_text)
    except json.JSONDecodeError as error:
        raise ValueError("模型返回的内容不是合法 JSON") from error

    return validate_learning_result(result)

def main():
    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        raise ValueError("请在环境变量中设置 DEEPSEEK_API_KEY")

    learning_record = (
        "我已经学会 Python 基础、文件读写和 JSON，"
        "现在开始学习 LLM API。"
    )

    answer_text = call_llm(api_key, learning_record)

    print("模型原始回答：")
    print(answer_text)

    try:
        result = json.loads(answer_text)
    except json.JSONDecodeError as error:
        raise ValueError("模型返回的内容不是合法 JSON") from error

    result = validate_learning_result(result)

    print("\n解析后的主题：", result["topic"])
    print("解析后的水平：", result["level"])
    print("解析后的下一步：", result["next_step"])


if __name__ == "__main__":
    main()