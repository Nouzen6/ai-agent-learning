import json


json_text = """
{
    "topic": "Python",
    "level": "beginner",
    "next_step": "学习 API"
}
"""


data = json.loads(json_text)

print("学习主题：", data["topic"])
print("当前水平：", data["level"])
print("下一步：", data["next_step"])