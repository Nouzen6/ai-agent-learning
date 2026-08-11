# Stage 2 Lesson 02：POST 请求、headers、body

## 1. POST 请求

POST 通常用于向服务器提交数据或触发操作。
调用 LLM API 时，需要把模型名称、用户问题和其他参数发送给服务器，所以通常使用 POST。

## 2. headers

headers 是请求头，用来提供额外信息。

常见内容：

- Authorization：身份认证
- Content-Type：请求数据格式

## 3. body

body 是请求体，包含真正要发送给服务器的数据。
在 Python 中，通常使用字典表示，再通过 json=body 发送。

## 4. requests.post 的基本结构

```python
response = requests.post(
    url,
    headers=headers,
    json=body,
    timeout=30
)