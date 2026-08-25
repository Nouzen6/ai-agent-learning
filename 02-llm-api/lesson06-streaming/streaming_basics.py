import time

text = "你好，我是一个正在逐步输出内容的 AI 助手。"

for character in text:
    print(character, end="", flush=True)
    time.sleep(0.05)

print()