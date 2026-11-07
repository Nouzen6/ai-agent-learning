import json
import os
from pathlib import Path

from dotenv import load_dotenv

import requests

from lesson02_tool_call import execute_tool
from lesson03_api_roundtrip import call_chat_model


def run_agent(
    user_prompt,
    api_key,
    max_steps=6,
    *,
    api_tools=None,
    tools=None,
    system_prompt=None,
):
    if type(max_steps) is not int or max_steps < 1:
        raise ValueError("max_steps 必须是正整数")

    if system_prompt is None:
        system_prompt = (
            "你是一个中文计算助手。"
            "涉及加法时使用 add 工具，以工具返回结果为准。"
            "后一步依赖前一步时，先取得前一步的工具结果。"
            "任务完成后，向用户给出最终答案。"
        )

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]

    trace = []

    for step in range(1, max_steps + 1):
        trace.append({
            "step": step,
            "event": "model_request",
        })

        print(f"\n第 {step} 轮：请求模型")
        try:
            assistant_message = call_chat_model(
                messages,
                api_key,
                tool_choice="auto",
                api_tools=api_tools,
            )
        except requests.exceptions.RequestException as error:
            trace.append({
                "step": step,
                "event": "api_error",
                "error": str(error),
            })

            return {
                "status": "api_error",
                "answer": None,
                "steps": step,
                "reason": f"LLM API 请求失败：{error}",
                "trace": trace,
            }

        messages.append(assistant_message)
        tool_calls = assistant_message.get("tool_calls")

        # 模型没有请求工具：检查回答并返回完成状态。
        if not tool_calls:
            answer = assistant_message.get("content")

            if not isinstance(answer, str) or not answer.strip():
                raise ValueError("模型未返回工具调用或有效回答")

            trace.append({
                "step": step,
                "event": "final_answer",
            })

            return {
                "status": "completed",
                "answer": answer,
                "steps": step,
                "reason": None,
                "trace": trace,
            }

        # 模型请求了工具：逐个执行，并回传结果。
        for raw_call in tool_calls:
            tool_name = "未知工具"

            try:
                function_data = raw_call["function"]
                tool_name = function_data["name"]

                tool_call = {
                    "name": tool_name,
                    "arguments": json.loads(
                        function_data["arguments"]
                    ),
                }

                print(
                    f"执行工具：{tool_name}，"
                    f"参数：{tool_call['arguments']}"
                )

                if tools is None:
                    tool_result = execute_tool(tool_call)
                else:
                    if tool_name not in tools:
                        raise ValueError(f"未知工具：{tool_name}")

                    arguments = tool_call["arguments"]

                    if not isinstance(arguments, dict):
                        raise ValueError("工具参数必须是 JSON 对象")

                    tool_result = tools[tool_name](**arguments)

            except (
                KeyError,
                TypeError,
                ValueError,
                requests.exceptions.RequestException,
            ) as error:
                trace.append({
                    "step": step,
                    "event": "tool_error",
                    "tool": tool_name,
                    "error": str(error),
                })

                return {
                    "status": "tool_error",
                    "answer": None,
                    "steps": step,
                    "reason": (
                        f"工具 {tool_name} 解析或执行失败：{error}"
                    ),
                    "trace": trace,
                }

            print(f"工具结果：{tool_result}")

            trace.append({
                "step": step,
                "event": "tool_result",
                "tool": tool_name,
                "arguments": tool_call["arguments"],
                "result": tool_result,
            })

            messages.append({
                "role": "tool",
                "tool_call_id": raw_call["id"],
                "content": json.dumps(
                    tool_result,
                    ensure_ascii=False,
                ),
            })


    # 循环全部执行完仍未返回答案：返回预算停止状态。
    return {
        "status": "step_limit",
        "answer": None,
        "steps": max_steps,
        "reason": "达到模型调用轮数上限，任务尚未完成",
        "trace": trace,
    }


def main():
    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(repo_root / ".env")

    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise ValueError("缺少 DEEPSEEK_API_KEY，请检查本地配置")

    result = run_agent(
        user_prompt=(
            "先用 add 计算 37 + 58，"
            "拿到工具结果后，再用 add 把该结果加上 26。"
            "最后告诉我答案。"
        ),
        api_key=api_key,
        max_steps=6,
    )

    print("\n执行状态：", result["status"])
    print("模型调用轮数：", result["steps"])

    if result["status"] == "completed":
        print("最终回答：", result["answer"])
    else:
        print("停止原因：", result["reason"])


if __name__ == "__main__":
    main()