## 1.本章目标

理解什么是LLM API、API key，以及一次请求的大致流程

## 2.LLM API是什么

LLM API 是大模型提供的接口
我的 Python 程序可以通过HTTP请求，把用户输入发送给大模型，然后接收模型返回的结果。

## 3.请求流程

用户输入
↓
Python程序
↓
HTTP请求
↓
LLM API服务
↓
大模型生成回答
↓
返回JSON
↓
Python程序解析并显示结果

## 4. 一次请求包含什么

| 部分 | 作用 |
|---|---|
| URL | 请求地址 |
| method | 请求方法，通常是 POST |
| headers | 身份认证和数据格式 |
| body | 发送给模型的内容 |

## 5.API KEY是什么

API key 是调用大模型API的凭证
它不能写进 GitHub，也不能直接写死在代码里。/

## 6.我的理解

使用网页聊天时，是我直接和 AI 产品交互。
使用 API 时，是我的程序和大模型服务交互。
这就是开发 AI 应用的开始。

## 7. 练习
1. LLM API 和 ChatGPT 网页聊天有什么区别？
一个是通过python程序和大模型服务交互，一个是在和ai产品交互

2. API key 为什么不能提交到 GitHub？
API key是私人的，API key 如果提交到 GitHub，别人可能拿它调用 API，产生费用或滥用你的账号

3. 一次 API 请求通常包含哪 4 个部分？
URL，method，headers，body

4. 为什么后面的 RAG 和 Agent 都需要会调用 LLM API？
因为 RAG 需要把检索到的资料交给大模型回答问题，Agent 需要让大模型决定下一步行动，所以它们都离不开 LLM API。