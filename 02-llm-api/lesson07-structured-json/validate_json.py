def validate_learning_result(data):
    required_fields = [
        "topic",
        "level",
        "next_step",
    ]

    for field in required_fields:
        if field not in data:
            raise ValueError(f"缺少字段：{field}")

        if not isinstance(data[field], str):
            raise TypeError(f"字段 {field} 必须是字符串")

    return data


if __name__ == "__main__":
    valid_data = {
    "topic": "LLM API",
    "level": 1,
    "next_step": "学习 API",
}
   

    print(validate_learning_result(valid_data))