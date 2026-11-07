import json


def build_followup_messages(
    user_prompt,
    normalized_tool_call,
    tool_result,
):
    assistant_message = {
        "role": "assistant",
        "tool_calls": [
            {
                "id": normalized_tool_call["call_id"],
                "type": "function",
                "function": {
                    "name": normalized_tool_call["name"],
                    "arguments": json.dumps(
                        normalized_tool_call["arguments"],
                        ensure_ascii=False,
                    ),
                },
            }
        ],
    }

    tool_message = {
        "role": "tool",
        "tool_call_id": normalized_tool_call["call_id"],
        "content": str(tool_result),
    }

    return [
        {
            "role": "user",
            "content": user_prompt,
        },
        assistant_message,
        tool_message,
    ]


if __name__ == "__main__":
    normalized_tool_call = {
        "name": "add",
        "arguments": {"a": 3, "b": 4},
        "call_id": "call_001",
    }

    messages = build_followup_messages(
        user_prompt="请计算 3 + 4",
        normalized_tool_call=normalized_tool_call,
        tool_result=7,
    )

    print("消息角色：", [message["role"] for message in messages])
    print(
        "调用 ID：",
        messages[1]["tool_calls"][0]["id"],
    )
    print(
        "结果关联 ID：",
        messages[2]["tool_call_id"],
    )

    request_body = {
        "model": "deepseek-flash",
        "messages": messages,
    }

    print("发送前的 JSON：")
    print(json.dumps(request_body, ensure_ascii=False, indent=2))