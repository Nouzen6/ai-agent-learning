## 1. 本课目标

学会控制 AI 的输出格式，让 AI 输出 Markdown、表格或 JSON。

## 2. 重要程度

就业重要度：很高

原因：
后面做 LLM API、RAG、Agent、SWE Agent 时，AI 的输出经常需要被程序继续处理。
如果输出没有结构，程序就很难解析。

## 3. 三种常见结构

| 格式 | 适合场景 | 说明 |
|---|---|---|
| Markdown | 笔记、README、报告 | 适合人阅读 |
| 表格 | 对比、计划、任务拆解 | 适合整理信息 |
| JSON | API、程序解析、Agent 工具调用 | 适合程序读取 |

## 4. Markdown 输出 Prompt

```text
请用 Markdown 输出。
要求包含：
1. 标题
2. 小节
3. 列表
4. 示例
5. 总结
```

## 5. 表格输出 Prompt

```text
请用 Markdown 表格输出。
表格字段包括：
步骤、任务、目的、完成标志。
```

## 6. JSON 输出 Prompt

```text
请只输出 JSON，不要输出额外解释。
字段包括：
{
  "topic": "学习主题",
  "summary": "一句话总结",
  "keywords": ["关键词1", "关键词2"],
  "next_steps": ["下一步1", "下一步2"],
  "completed": true
}
```

## 7. 我的理解

结构化输出就是让 AI 按指定格式回答。
Markdown 和表格主要给人看，JSON 主要给程序处理。
后面做 Agent 时，JSON 会非常重要，因为程序需要读取 AI 的输出并决定下一步动作。

## 8. 结构化输出练习

### 练习 1：Markdown 输出

```text
背景：
我正在学习 AI Agent，目前已经学过 Python、Git、Prompt 基本结构和任务拆解，但还没有系统学习 RAG。

目标：
请帮我总结“什么是 RAG”，让我能理解它为什么对 AI 应用很重要。

限制：
1. 请从初学者角度讲解。
2. 不要使用太多专业术语。
3. 请结合一个个人知识库问答助手的例子说明。
4. 不要只给定义，要解释 RAG 解决了什么问题。

输出格式：
请使用 Markdown 输出，包含：
1. 标题
2. 概念解释
3. 为什么需要 RAG
4. 一个简单例子
5. 3 个自测问题
```

### 练习 2：表格输出

```text
背景：
我正在学习 LLM API 应用开发，已经学过 Python、requests、headers、JSON 和命令行运行 Python 文件。

目标：
请把“做一个命令行 AI 聊天助手”这个任务拆成多个步骤。

限制：
1. 先做最小可用版本。
2. 不要加入 Web 页面、数据库、登录系统等复杂功能。
3. 每一步都要适合初学者完成。
4. 每一步都要有明确的完成标志。

输出格式：
请用 Markdown 表格输出，表格字段包括：
步骤、任务、目的、完成标志。
```

### 练习 3：JSON 输出

```text
背景：
我正在整理自己的 AI Agent 学习记录，希望把自然语言学习记录转换成程序可以处理的 JSON。

输入内容：
今天我学习了 Prompt 的结构化输出，知道了 Markdown 适合写笔记，表格适合做任务拆解，JSON 适合程序解析。

目标：
请把上面的学习记录整理成 JSON。

限制：
1. 只输出 JSON，不要输出解释文字。
2. JSON 必须可以被 Python 的 json.loads() 正常解析。
3. 不要使用 Markdown 代码块。
4. 如果某个字段没有明确内容，请根据输入内容合理概括。
5. completed 字段使用布尔值 true。

输出格式：
{
  "date": "2026-08-09",
  "topic": "",
  "summary": "",
  "formats_learned": [],
  "next_steps": [],
  "completed": true
}
```

示例 AI 输出：

```json
{
  "date": "2026-08-09",
  "topic": "Prompt 结构化输出",
  "summary": "学习了如何让 AI 按 Markdown、表格和 JSON 输出结果，并理解了不同格式的适用场景。",
  "formats_learned": ["Markdown", "表格", "JSON"],
  "next_steps": ["练习让 AI 输出可解析的 JSON", "学习在 Python 中读取 JSON", "了解结构化输出在 LLM API 中的应用"],
  "completed": true
}
```