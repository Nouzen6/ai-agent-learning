import json
import os
from pathlib import Path

from dotenv import load_dotenv

from lesson02_tool_call import execute_tool
from lesson03_api_roundtrip import call_chat_model


def run_agent(user_prompt, api_key, max_steps=6):
    messages = [
        {
            "role": "system",
            "content": (
                "你是一个中文计算助手。"
                "涉及加法时使用 add 工具，以工具返回结果为准。"
                "后一步依赖前一步时，先取得前一步的工具结果。"
                "任务完成后，向用户给出最终答案。"
            ),
        },
        {"role": "user", "content": user_prompt},
    ]

    for step in range(1, max_steps + 1):
        print(f"\n第 {step} 轮：请求模型")

        assistant_message = call_chat_model(
            messages,
            api_key,
            tool_choice="auto",
        )

        messages.append(assistant_message)
        tool_calls = assistant_message.get("tool_calls")

        # 没有工具调用：本轮应当是最终回答。
        if not tool_calls:
            answer = assistant_message.get("content")

            if not isinstance(answer, str) or not answer.strip():
                raise ValueError("模型未返回工具调用或有效回答")

            return answer

        # 有工具调用：执行并把结果加入历史。
        for raw_call in tool_calls:
            function_data = raw_call["function"]

            tool_call = {
                "name": function_data["name"],
                "arguments": json.loads(
                    function_data["arguments"]
                ),
            }

            print(
                f"执行工具：{tool_call['name']}，"
                f"参数：{tool_call['arguments']}"
            )

            tool_result = execute_tool(tool_call)
            print(f"工具结果：{tool_result}")

            messages.append({
                "role": "tool",
                "tool_call_id": raw_call["id"],
                "content": json.dumps(
                    tool_result,
                    ensure_ascii=False,
                ),
            })

    raise RuntimeError(
        f"已达到 {max_steps} 轮模型调用上限，任务尚未完成"
    )


def main():
    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(repo_root / ".env")

    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise ValueError("缺少 DEEPSEEK_API_KEY，请检查本地配置")

    answer = run_agent(
        user_prompt=(
            "先用 add 计算 37 + 58，"
            "拿到工具结果后，再用 add 把该结果加上 26。"
            "最后告诉我答案。"
        ),
        api_key=api_key,
    )

    print("\n最终回答：", answer)


if __name__ == "__main__":
    main()