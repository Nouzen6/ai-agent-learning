import requests

url = "https://postman-echo.com/post"

headers = {
    "Content-Type": "application/json"
}

body = {
    "topic": "LLM API",
    "question": "什么是 POST 请求？"
}

response = requests.post(url, headers=headers, json=body, timeout=10)

print("状态码：", response.status_code)
print("Content-Type：", response.headers.get("Content-Type"))
print("原始内容：", response.text)

if response.status_code == 200 and "application/json" in response.headers.get("Content-Type", ""):
    print("JSON解析结果：")
    print(response.json())
else:
    print("返回内容不是可解析的 JSON")