## 1. 本课目标

理解 system、user、assistant 三种消息角色的作用。

## 2. messages 是什么

messages 是发送给大模型的一组消息。
每条消息通常包含：
- role
- content

## 3. 三种角色

| role | 作用 |
|---|---|
| system | 设定 AI 的身份、规则和边界 |
| user | 用户当前的问题或任务 |
| assistant | AI 之前的回答，用来保存对话历史 |

## 4. system

system 适合放长期规则，例如：
- 你是什么角色
- 用什么语言回答
- 回答要多详细
- 不要做什么

## 5. user

user 适合放当前任务，例如：
- 解释一个概念
- 写一段代码
- 总结一篇文章
- 根据资料回答问题

## 6. assistant

assistant 用来保存 AI 之前的回答。
多轮对话时，需要把之前的 user 和 assistant 消息一起发送给模型。

## 7. 我的理解

messages 结构把 Prompt 拆成不同角色。
system 负责规则，user 负责当前问题，assistant 负责历史回答。
后面的聊天助手、RAG 和 Agent 都需要管理这些消息。

## 8. 练习

1. system 和 user 有什么区别？
system是长期的约束，设定了ai的身份，边界和规则
user是用户当前的问题

2. assistant 消息为什么对多轮对话重要？
assistant消息保存 AI 之前的回答。多轮对话时，把之前的 user 和 assistant 消息一起发送给模型，模型才能理解对话上下文。

3. 如果我要让 AI 始终用中文、从基础讲解，这句话应该放到 system 还是 user？为什么？
system，因为system是长期的约束，定义了ai的身份和边界

messages=[
     {"role":"system","content":"这里写规则"},
     {"role":"user","content":"这里写问题"}
]