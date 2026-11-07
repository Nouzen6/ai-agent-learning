from lesson02_tool_call import execute_tool
import json

def mock_llm_response():
    return {
        "type": "tool_call",
        "tool_call": {
            "name": "add",
            "arguments": {"a": 3,"b": 4},
        },
    }

def parse_api_tool_call(api_response):
    message = api_response["choices"][0]["message"]
    raw_tool_call = message["tool_calls"][0]
    function_data = raw_tool_call["function"]

    try:
        arguments = json.loads(function_data["arguments"])
    except json.JSONDecodeError as error:
        raise ValueError("工具参数不是合法 JSON") from error

    return {
        "name": function_data["name"],
        "arguments": arguments,
        "call_id": raw_tool_call["id"],
    }

def validate_tool_call(tool_call, schema):
    if tool_call["name"] != schema["name"]:
        raise ValueError(f"工具名称与说明不一致：{tool_call['name']}")

    arguments = tool_call["arguments"]

    for parameter_name in schema["parameters"]["required"]:
        if parameter_name not in arguments:
            raise ValueError(f"缺少必需参数：{parameter_name}")

TOOL_SCHEMA = {
    "name": "add",
    "description": "计算两个整数的和。",
    "parameters": {
        "type": "object",
        "properties": {
            "a": {"type": "integer", "description": "第一个整数"},
            "b": {"type": "integer", "description": "第二个整数"},
        },
        "required": ["a", "b"],
    },
}

API_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": TOOL_SCHEMA["name"],
            "description": TOOL_SCHEMA["description"],
            "parameters": TOOL_SCHEMA["parameters"],
        },
    }
]

CHAT_COMPLETION_BODY = {
    "model": "deepseek-flash",
    "messages": [
        {
            "role": "user",
            "content": "请计算 3 + 4",
        }
    ],
    "tools": API_TOOLS,
}

MOCK_API_RESPONSE = {
    "choices": [
        {
            "message": {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_001",
                        "type": "function",
                        "function": {
                            "name": "add",
                            "arguments": '{"a": 3, "b": 4}',
                        },
                    }
                ],
            }
        }
    ]
}

normalized_tool_call = parse_api_tool_call(MOCK_API_RESPONSE)

print("转换后的工具名称：", normalized_tool_call["name"])
print("转换后的参数：", normalized_tool_call["arguments"])
print("调用 ID：", normalized_tool_call["call_id"])
validate_tool_call(normalized_tool_call, TOOL_SCHEMA)

api_tool_result = execute_tool(normalized_tool_call)

print("API 工具执行结果：", api_tool_result)
message = MOCK_API_RESPONSE["choices"][0]["message"]
api_tool_call = message["tool_calls"][0]

print("API 响应角色：", message["role"])
print("API 工具名称：", api_tool_call["function"]["name"])
print("API 原始参数：", api_tool_call["function"]["arguments"])
print("请求模型：", CHAT_COMPLETION_BODY["model"])
print("用户问题：", CHAT_COMPLETION_BODY["messages"][0]["content"])
print(
    "可用工具：",
    CHAT_COMPLETION_BODY["tools"][0]["function"]["name"],
)
print("API 工具类型：", API_TOOLS[0]["type"])
print("API 工具名称：", API_TOOLS[0]["function"]["name"])

print("工具说明：", TOOL_SCHEMA["description"])
print("必需参数：", TOOL_SCHEMA["parameters"]["required"])

response = mock_llm_response()

print("响应类型：", response["type"])


if response["type"] == "tool_call":
    print("工具名称：", response["tool_call"]["name"])
    print("工具参数：", response["tool_call"]["arguments"])
    validate_tool_call(response["tool_call"], TOOL_SCHEMA)
    tool_result = execute_tool(response["tool_call"])
    print(f"工具执行结果：{tool_result}")
else:
    print("模型普通回答：", response.get("text", ""))