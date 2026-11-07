def add(a, b):
    return a + b


TOOLS = {
    "add": add,
}


def execute_tool(tool_call):
    tool_name = tool_call["name"]
    arguments = tool_call["arguments"]

    if tool_name not in TOOLS:
        raise ValueError(f"未知工具：{tool_name}")

    tool_function = TOOLS[tool_name]
    return tool_function(**arguments)


if __name__ == "__main__":
    tool_call = {
        "name": "add",
        "arguments": {"a": 3, "b": 4},
    }

    result = execute_tool(tool_call)
    print(f"工具执行结果：{result}")