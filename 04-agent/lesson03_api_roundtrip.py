import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

from lesson02_tool_call import execute_tool


API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-flash"

API_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "计算两个整数的和。",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"},
                },
                "required": ["a", "b"],
            },
        },
    }
]

def call_chat_model(
    messages,
    api_key,
    tool_choice,
    api_tools=None,
):
    if api_tools is None:
        api_tools = API_TOOLS

    request_body = {
        "model": MODEL,
        "messages": messages,
        "tools": api_tools,
        "tool_choice": tool_choice,
        "thinking": {"type": "disabled"},
        "stream": False,
    }
    response = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=request_body,
        timeout=60,
    )
    response.raise_for_status()

    response_data = response.json()
    return response_data["choices"][0]["message"]

def main():
    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(repo_root / ".env")

    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise ValueError("缺少 DEEPSEEK_API_KEY，请检查本地配置")

    messages = [
        {"role": "user", "content": "请计算 37 + 58"}
    ]

    # 第一次请求：让模型生成工具调用。
    assistant_message = call_chat_model(
        messages, api_key, tool_choice="required"
    )

    tool_calls = assistant_message.get("tool_calls")
    if not tool_calls:
        raise ValueError("模型没有返回工具调用")

    messages.append(assistant_message)

    # 执行模型请求的工具，逐个追加执行结果。
    for raw_call in tool_calls:
        function_data = raw_call["function"]

        tool_call = {
            "name": function_data["name"],
            "arguments": json.loads(function_data["arguments"]),
        }

        tool_result = execute_tool(tool_call)

        messages.append({
            "role": "tool",
            "tool_call_id": raw_call["id"],
            "content": json.dumps(tool_result, ensure_ascii=False),
        })

        print(f"工具 {tool_call['name']} 返回：{tool_result}")

    # 第二次请求：模型根据工具结果生成最终回答。
    final_message = call_chat_model(
        messages, api_key, tool_choice="none"
    )
    print("模型最终回答：", final_message["content"])


if __name__ == "__main__":
    main()