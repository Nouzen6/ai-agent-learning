# Stage 4：知识库 Agent 与验收记录

本阶段在已有个人知识库 RAG 项目上，实现一个能够调用检索工具的 Agent。模型决定是否检索、生成搜索词，并根据工具返回的资料继续检索或给出答案；Python 程序负责执行工具、维护消息历史和控制停止条件。

当前已完成 Stage 4 的学习目标：工具调用协议、Agent 执行循环、状态与 trace、RAG 工具接入、Mock 测试和命令行交互。验收基于 4 个自动化测试、少量真实问答与 CLI 手工检查，尚未完成系统化质量评估。

## 功能与配置

- 使用 DeepSeek Chat Completions，通过 `tool_calls` 请求工具。
- 使用本地注册表执行允许的工具，不执行模型生成的任意代码。
- 将工具结果通过 `role="tool"` 消息回传，以 `tool_call_id` 关联原调用。
- 复用 Stage 3 的 JSON 索引、Embedding 客户端和余弦检索。
- 每个问题最多请求模型 6 轮，返回执行状态和 trace。
- CLI 支持反复输入问题、空输入提示和 `exit` 退出。

| 配置项 | 当前值 |
| --- | --- |
| 模型地址 | `https://api.deepseek.com/chat/completions` |
| 模型名称 | `deepseek-flash`，在请求模块中定义 |
| 模型请求方式 | `stream=False`、`thinking={"type": "disabled"}` |
| 工具选择 | `tool_choice="auto"` |
| 知识库 Agent 的工具 | `search_knowledge_base` |
| 检索参数 | `k=3`、`score_threshold=0.6` |
| 模型调用上限 | `max_steps=6`，按模型请求轮数计算 |
| 索引位置 | `03-rag/personal_rag_assistant/data/index.json` |

`add` 是早期课程中的演示工具。知识库 CLI 显式传入自己的 schema 和注册表，因此运行时只向模型提供 `search_knowledge_base`，不会自动合并 `add`。

Stage 3 的生成回答接口保留原有 Responses 风格；Stage 4 使用 Chat Completions，并复用 Stage 3 的检索部分。当前 Agent 检索工具未接入可选 Rerank。

## 文件职责

| 文件 | 用途 |
| --- | --- |
| `lesson02_tool_call.py` | `add` 函数、工具注册表与本地执行器 |
| `lesson03_mock_model.py` | 早期模拟模型响应的教学示例 |
| `lesson03_message_protocol.py` | 展示 assistant 工具调用、tool 结果和调用 ID 的对应关系 |
| `lesson03_api_roundtrip.py` | Chat Completions 请求函数及加法工具往返演示 |
| `lesson04_agent_loop.py` | 基础 Agent 执行循环 |
| `lesson05_agent_state.py` | 支持传入 schema、注册表和系统提示词的循环，以及状态、异常处理与 trace |
| `lesson06_rag_tool.py` | 检索工具 schema、检索结果封装与最终 CLI 入口 |
| `lesson07_agent_test.py` | 4 个离线 Mock 测试 |

Lesson 01 为概念学习；Lesson 08 的 CLI 实现在 `lesson06_rag_tool.py`，没有单独的 Lesson 08 脚本。

## 运行准备

以下 PowerShell 命令均在仓库根目录执行。

使用现有 `.venv`。如果尚未安装依赖，执行：

```powershell
& .\.venv\Scripts\python.exe -m pip install requests python-dotenv
```

本地根目录 `.env` 需要包含以下配置；下面只有变量名称和占位值，不是真实密钥：

```dotenv
DEEPSEEK_API_KEY=your_deepseek_api_key
EMBEDDING_API_URL=your_embedding_api_url
EMBEDDING_MODEL=your_embedding_model
EMBEDDING_API_KEY=your_embedding_api_key
```

请在已有 `.env` 中补齐所需项，保留 Stage 3 的其他配置。不要提交 `.env` 或真实密钥。

知识库 Agent 直接使用请求模块中的模型地址与名称，不读取 Stage 3 的 `LLM_API_URL`、`LLM_MODEL`。Embedding 配置由 Stage 3 的 `load_embedding_config()` 加载。

运行前需已有 Stage 3 的 `data/index.json`。如果索引缺失或需要重建，请按 [Stage 3 README](../03-rag/personal_rag_assistant/README.md) 操作；查询向量与索引向量应使用兼容的 Embedding 模型。

## 启动 CLI

```powershell
& .\.venv\Scripts\python.exe .\04-agent\lesson06_rag_tool.py
```

交互示例：

```text
知识库 Agent 已启动，输入 exit 退出。

你：请检索我的学习路线，说明 Stage 4 和 Stage 5 分别学什么，并标注片段 ID。
……模型请求与工具执行日志……
执行状态： completed
模型调用轮数： ……
AI：……

你：exit
已退出。
```

真实提问可能产生多轮模型请求和多次 Embedding 请求。空输入和 `exit` 不触发这两类请求，但程序启动时仍会加载索引并检查配置。

每次提问都会创建新的 `messages` 和 `trace`。同一个问题内部保留工具调用历史，不同问题之间没有对话记忆。

## 数据传输流程

```text
启动：index.json → Python 片段列表，准备检索工具

用户问题 + 系统提示词 + 工具 schema
    ↓ Chat Completions 请求
模型返回 assistant 消息和 tool_calls
    ↓ json.loads(arguments)：JSON 字符串 → Python 字典
注册表根据工具名称找到 search_tool(query)
    ↓
搜索词 → Embedding API → 问题向量
    ↓
本地余弦检索 → 阈值过滤 → 最多 3 条片段
    ↓
返回 Python 字典：query、matches，以及片段 ID、正文、分数和来源
    ↓ json.dumps：Python 字典 → JSON 字符串
追加 role="tool" 消息，tool_call_id 对应原调用 ID
    ↓ 再次发送完整消息历史
模型继续请求工具，或给出最终回答
```

工具 schema 是模型看到的说明书；注册表保存可调用的 Python 函数，函数本身不会发送给模型。索引保留在本地，工具回传命中的文字资料，不回传片段向量。

`messages` 是发给模型的对话历史；`trace` 是程序维护的可观察执行记录，不是模型的私有思考，也不会自动发送给模型。

一次模型响应可以包含多条工具调用，程序逐个执行。这些调用在模型看到本轮结果之前就已生成，不能视为模型根据第一条结果再决定第二条调用。

## 状态与停止条件

`run_agent()` 的正常状态返回包含 `status`、`answer`、`steps`、`reason` 和 `trace`。

| 状态 | 含义 |
| --- | --- |
| `completed` | 模型给出有效文本，任务循环结束；不代表答案一定正确 |
| `step_limit` | 用完模型请求轮数，仍未得到最终答案 |
| `api_error` | 请求模型时发生被捕获的网络或 HTTP 异常 |
| `tool_error` | 工具参数解析或执行发生被捕获的异常，包括检索工具中的请求超时 |

trace 事件包括 `model_request`、`tool_result`、`final_answer`、`api_error` 和 `tool_error`。只有模型返回有效最终文本时，才记录 `final_answer`。

资料不足时，模型明确说明无法确认，也可以返回 `completed`。`steps` 记录模型请求轮数，不是工具调用次数；一轮多次工具调用会增加实际请求开销。

## 自动化验收

```powershell
& .\.venv\Scripts\python.exe -B .\04-agent\lesson07_agent_test.py
```

2026-11-07 在本地执行，结果为：

```text
Ran 4 tests
OK
```

| 测试 | 验证内容 |
| --- | --- |
| `test_tool_result_is_returned_to_model` | 解析参数、调用工具，并将匹配调用 ID 的结果加入第二次模型请求 |
| `test_stops_at_step_limit` | 达到上限后返回 `step_limit`，调用次数受限且不记录最终回答 |
| `test_model_timeout_stops_agent` | 模型超时后返回 `api_error`，记录错误且不调用工具 |
| `test_tool_timeout_stops_agent` | 工具超时后返回 `tool_error`，记录失败工具并停止后续模型请求 |

测试使用虚构密钥和 Mock，不读取真实密钥，不访问模型或 Embedding API。它们主要验证 Agent 循环及消息协议，没有覆盖真实 HTTP schema 校验、真实 Embedding 返回值或答案质量。

## 人工验收记录

以下问答来自 CLI 改造前同一 Agent 循环的真实运行日志；工具调用次数按日志计数。当前 CLI 的空输入与退出另行手工验证。

| 场景 | 输入或操作 | 观察结果 | 结论 |
| --- | --- | --- | --- |
| 资料充分 | 检索学习路线，说明 Stage 4 和 Stage 5 内容并标注 ID | 2 轮模型请求、2 次检索；返回内容与学习路线一致，引用 `learning_path.md::chunk-0000` | 核心事实及引用通过，部分扩展概括仍需人工判断 |
| 资料不足 | 询问 Stage 4 课程节数与每节学习时长 | 3 轮模型请求、4 次检索；明确缺少相关记录，没有虚构课时数字 | 资料不足处理通过；存在过强措辞，见下文 |
| CLI 退出 | 输入 `exit` | 打印“已退出。”并结束程序 | 通过 |
| CLI 空输入 | 直接按 Enter | 提示“请输入问题。”并继续等待 | 用户手工验证通过 |

资料不足样例中的“检索了知识库中与 Stage 4 相关的全部内容”超出了相似度检索能够证明的范围。更严谨的表述是“根据本次检索到的资料，无法确认课程节数和学习时长”。

回答质量采用以下标准：

1. 流程是否完成，或给出明确停止状态。
2. 核心事实是否正确，有无遗漏问题要求。
3. 知识库事实是否有工具返回的资料支持。
4. 引用 ID 是否出现在本次检索结果中，并支持对应表述。
5. 资料不足时是否明确说明，避免编造数字或来源。

单次成功不能证明稳定性；当前记录属于少量人工验收，不报告总体准确率。

## 已知边界与后续方向

- 轮数上限只限制模型请求次数，没有单独限制工具调用总数、token 或费用，也没有自动重试。
- 不同问题之间没有对话记忆；trace 保留在本次返回值中，未持久化保存。
- 可能重复检索同一片段，没有缓存或去重；Agent 工具尚未启用 Rerank。
- `score_threshold=0.6` 可能过滤掉内容相关的片段。曾观察到网络异常处理问题的相关片段约为 `0.5856`；临时关闭阈值只用于诊断，正式配置已恢复。
- schema 声明参数要求，程序另有部分校验，但尚未实现完整的模型响应结构验证。空回答、缺失调用 ID 等异常数据仍可能直接抛错。
- CLI 尚未统一处理启动配置错误、索引错误、输入中断和所有未捕获异常。
- 引用由模型生成，尚未自动逐句验证支持关系；没有完成系统化质量评估或资料指令注入的专项验证。
- 使用 `sys.path` 复用 Stage 3 模块，尚未整理成可安装的 Python 包。编辑器可能需要额外配置模块搜索路径。

下一阶段是 minimal SWE Agent：将当前的工具注册、消息回传和停止机制应用到读取代码、修改文件、运行命令及检查执行结果。

## 官方资料

- [DeepSeek 工具调用](https://api-docs.deepseek.com/zh-cn/guides/tool_calls)：阅读工具定义、调用 ID 和工具结果回传示例。
- [Python unittest.mock](https://docs.python.org/zh-cn/3/library/unittest.mock.html)：阅读 `patch`、`side_effect` 与调用次数断言。
