# AI Agent Learning

从 Python 基础到 RAG、工具调用与代码修复 Agent 的学习实践仓库。**Stage 0–5 六个阶段的课程、练习与阶段项目均已完成**，成果以 Python 命令行应用、Prompt 模板和项目验收记录为主。

**项目状态：阶段项目已完成 · 本次验收：2026-11-23**

核心实践包括：文档检索与问答、模型 API 接入、Tool Calling、任务状态与 trace、执行约束，以及基于测试反馈的结果核验。

**建议阅读顺序：**[个人知识库 RAG](03-rag/personal_rag_assistant/README.md) → [检索 Agent](04-agent/README.md) → [受限代码修复 Agent](05-swe-agent/README.md)。

## 主要项目

### 个人知识库 RAG 问答与检索 Agent

面向个人 Markdown/TXT 学习笔记，实现检索资料后生成答案的问答助手，并将检索能力接入 Agent 工具循环。

- **文档与索引：**清洗、固定长度重叠切块，调用 Embedding API，将文本、向量与来源保存至本地 JSON。
- **检索与生成：**手写余弦相似度 top-k 检索、阈值过滤，支持可选 Rerank；维护资料编号与文件、片段的映射。
- **工具调用：**通过 Chat Completions 请求检索工具，使用注册表执行函数、按 `tool_call_id` 回传结果，维护单次任务消息历史、状态与 trace。
- **验证：**62 项 RAG 单元测试、4 项检索 Agent Mock 测试通过；另归档覆盖 4 个不同问题的 7 次 RAG 真实问答，人工检查证据、忠实度、完整性与来源标注。

```text
建立索引：文档 → 清洗与切块 → Embedding → JSON 索引

普通问答：问题 → Embedding → 检索与阈值过滤 → 可选重排
        → 组织上下文和来源编号 → LLM → 答案与资料映射

检索 Agent：问题与工具说明 → 模型请求检索 → Python 执行
           → 工具结果回传 → 继续调用或给出最终回答
```

当前检索 Agent 复用 RAG 的检索部分，尚未启用 Rerank；单次任务内部保留消息历史，不同问题之间没有对话记忆。

[RAG 使用说明](03-rag/personal_rag_assistant/README.md) · [人工评估记录](03-rag/personal_rag_assistant/EVALUATION.md) · [检索 Agent 使用与验收](04-agent/README.md)

### 受限代码修复 Agent

提供读取代码、修改指定实现文件、运行固定测试三个工具，根据执行反馈继续修复。已完成的练习任务是修复 `average(values)` 的空列表除零问题。

- **执行范围：**解析路径并检查目录与读写白名单；实现文件可写、测试文件只读。
- **工具约束：**写入前检查内容长度和 Python 语法；固定测试命令与工作目录，配置超时及输出截断。
- **调用预算与记录：**分别限制模型请求轮数和工具调用尝试次数，保存 JSON 执行记录。
- **测试证据核验：**按 trace 顺序检查测试结果；后续写入尝试使旧证据失效，重新测试通过后恢复验证状态，区分循环结束与指定测试通过。
- **验证：**11 项 Agent 测试、3 项业务测试通过；有一道任务的一次真实修复记录，共 5 轮模型请求、5 次工具调用。

```text
任务 → 模型选择工具 → 参数校验与执行 → 反馈回传 → 继续行动或结束
                                                      ↓
                           按 trace 核验测试证据 → 保存执行记录
```

真实修复案例发生在增加工具预算、JSON 保存和测试证据核验功能之前，不作为这些新增功能的真实运行证据。工具层约束不等于系统级沙箱，当前仅用于受限练习任务。

[项目说明、工具边界与真实案例](05-swe-agent/README.md) · [测试证据核验源码](05-swe-agent/lesson08_verification.py)

### 命令行 AI 学习助手

Stage 2 综合项目，通过模型 API 实现连续对话和学习记录分析。

- **连续对话：**解析 SSE 文本增量并实时打印，在当前进程内维护会话消息历史。
- **学习分析：**通过 `/analyze` 分析学习记录，校验 `topic`、`level`、`next_step` 三个字符串字段，将结果保存为本地 JSON。
- **异常处理与验证：**处理网络、超时、JSON 格式、字段校验和文件保存异常；10 项 Mock 单元测试通过。

[项目说明与使用方式](02-llm-api/lesson08-cli-learning-assistant/README.md) · [完整实现](02-llm-api/lesson08-cli-learning-assistant/cli_learning_assistant_memory.py)

### 学习日志分析器与 Prompt 模板库

- **Stage 0 日志分析器：**读取 UTF-8 文本，统计字符、行数、日期条目与关键词，生成 JSON 和 Markdown 总结，包含文件不存在、编码和写入异常处理。[项目说明](00-python-basic/README.md) · [实现源码](00-python-basic/project/learning_log_analyzer.py)
- **Stage 1 Prompt 实践：**整理任务拆解、结构化输出、AI 辅助学习与编程、结果核验等笔记，形成可复用的 [Prompt 模板库](01-ai-tools-prompt/lesson08-prompt-template-library/prompt_templates.md) 与 [AI 学习工作流](01-ai-tools-prompt/lesson08-prompt-template-library/ai_learning_workflow.md)。

## 验证结果

2026-11-23 在本地重新运行以下五组测试，**共 90 项全部通过**。API 相关测试使用 Mock，本次复核未请求真实模型或 Embedding 服务。

| 范围 | 测试数量 | 验证内容 |
| --- | ---: | --- |
| CLI 学习助手 | 10 | 文本提取、SSE 增量打印、学习分析、JSON 校验与保存 |
| RAG | 62 | 文档处理、向量与索引、检索、重排、响应解析及异常分支等程序行为 |
| 检索 Agent | 4 | 工具结果回传、模型轮数限制、模型与工具超时 |
| SWE Agent | 11 | 工具往返、调用预算、记录保存、执行边界与测试证据核验等 |
| 业务函数 | 3 | 正数平均值、负数平均值、空列表返回 0 |

测试数量代表所覆盖的程序行为，不代表模型回答准确率、总体修复成功率或生产稳定性。真实问答与修复记录的范围、配置和限制见各项目说明。

## 快速开始

以下命令在仓库根目录使用 **Windows PowerShell** 执行。已有可用 `.venv` 时跳过环境创建。

### 1. 准备环境

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install requests python-dotenv
```

### 2. 先运行离线测试

不需要真实 API 密钥；不会触发模型调用或让 Agent 修改练习实现。

```powershell
# CLI 学习助手：10 项
& .\.venv\Scripts\python.exe -B -X utf8 .\02-llm-api\lesson08-cli-learning-assistant\test_cli_learning_assistant.py

# RAG：62 项
& .\.venv\Scripts\python.exe -B -X utf8 -m unittest discover -s .\03-rag\personal_rag_assistant -p "test_*.py"

# 检索 Agent：4 项
& .\.venv\Scripts\python.exe -B -X utf8 .\04-agent\lesson07_agent_test.py

# SWE Agent：11 项
& .\.venv\Scripts\python.exe -B -X utf8 -m unittest discover -s .\05-swe-agent -p "lesson*_test.py"

# 业务测试：3 项，执行当前练习代码
& .\.venv\Scripts\python.exe -B -X utf8 .\05-swe-agent\lesson04_run_tests.py
```

### 3. 配置真实 API

在仓库根目录创建或编辑 `.env`，按所运行的项目补齐配置。现有 `.env.example` 仅包含 `DEEPSEEK_API_KEY`，运行 RAG 和检索 Agent 还需要下列其他项。

```dotenv
# 各阶段客户端使用此变量名读取模型密钥
DEEPSEEK_API_KEY=

# Stage 3：RAG 回答生成，需使用与客户端兼容的 Responses 风格接口
LLM_API_URL=
LLM_MODEL=

# Stage 3 建索引与问答、Stage 4 检索 Agent
EMBEDDING_API_URL=
EMBEDDING_MODEL=
EMBEDDING_API_KEY=

# 仅 Stage 3 启用 --rerank 时需要
RERANK_API_URL=
RERANK_MODEL=
RERANK_API_KEY=
```

Stage 4/5 使用 Chat Completions，其模型地址与名称在复用的[请求模块](04-agent/lesson03_api_roundtrip.py)中定义，不读取 Stage 3 的 `LLM_API_URL` 和 `LLM_MODEL`。各接口的请求和响应结构需与当前客户端匹配，具体配置见项目说明。

### 4. 运行 RAG 问答

将可用于外部 API 处理的 Markdown/TXT 文档放入 `03-rag/personal_rag_assistant/knowledge_base/`，然后执行：

```powershell
# 首次建索引：调用真实 Embedding API
& .\.venv\Scripts\python.exe -B -X utf8 .\03-rag\personal_rag_assistant\index_documents.py

# 普通知识库问答
& .\.venv\Scripts\python.exe -B -X utf8 .\03-rag\personal_rag_assistant\cli.py

# 可选：配置 RERANK_* 后启用重排
& .\.venv\Scripts\python.exe -B -X utf8 .\03-rag\personal_rag_assistant\cli.py --rerank
```

若索引已存在，建索引程序会拒绝覆盖。更新文档或更换 Embedding 模型时，按 [RAG 说明](03-rag/personal_rag_assistant/README.md#更新索引)备份并重建索引；查询与索引应使用一致或兼容的向量表示。

### 5. 运行检索 Agent 或代码修复 Agent

```powershell
# 需要前一步建立的 RAG 索引，以及模型与 Embedding 配置
& .\.venv\Scripts\python.exe -B -X utf8 .\04-agent\lesson06_rag_tool.py

# 需要模型密钥；可能修改 05-swe-agent/practice/solution.py
& .\.venv\Scripts\python.exe -B -X utf8 .\05-swe-agent\lesson05_real_run.py
```

真实运行会产生 API 请求与相应费用。文档、问题、代码或工具反馈会按调用链发送给所配置的服务；不要使用不适合发送给这些服务的资料。当前练习函数已修复，SWE 入口检查后可能无需修改文件。

### 6. 运行基础项目

```powershell
# 日志分析器：无需 API；更新项目内的 learning_summary.json 和 learning_summary.md
& .\.venv\Scripts\python.exe -B -X utf8 .\00-python-basic\project\learning_log_analyzer.py learning-log.md python agent json git api

# CLI 学习助手：需要 DEEPSEEK_API_KEY
& .\.venv\Scripts\python.exe -B -X utf8 .\02-llm-api\lesson08-cli-learning-assistant\cli_learning_assistant_memory.py
```

CLI 学习助手支持普通提问、`/analyze 学习记录` 和 `exit`。其模型地址与名称在脚本中定义，不读取 Stage 3 的 `LLM_API_URL` 和 `LLM_MODEL`。

## 学习阶段与目录

| 阶段 | 状态 | 主要内容与成果 | 入口 |
| --- | --- | --- | --- |
| Stage 0 | 已完成 | Python、Git、环境与 HTTP 基础；学习日志分析器 | [基础练习与日志分析器](00-python-basic/README.md) |
| Stage 1 | 已完成 | AI 工具、任务拆解、结构化输出与结果核验；Prompt 模板库 | [学习笔记与模板](01-ai-tools-prompt/) |
| Stage 2 | 已完成 | 模型 API、会话历史、SSE 与 JSON；CLI 学习助手 | [课程目录](02-llm-api/) · [CLI 学习助手](02-llm-api/lesson08-cli-learning-assistant/README.md) |
| Stage 3 | 已完成 | 文档索引、向量检索、可选重排、编号来源与人工评估 | [个人知识库 RAG](03-rag/personal_rag_assistant/README.md) |
| Stage 4 | 已完成 | Tool Calling、Agent 循环、状态与 trace；知识库检索 Agent | [检索 Agent](04-agent/README.md) |
| Stage 5 | 已完成 | 受限文件工具、测试反馈、调用预算与证据核验；代码修复 Agent | [代码修复 Agent](05-swe-agent/README.md) |

```text
ai-agent-learning/
├── 00-python-basic/       # Python 练习与学习日志分析器
├── 01-ai-tools-prompt/    # AI 工具与 Prompt 实践
├── 02-llm-api/            # 模型 API 与 CLI 应用
├── 03-rag/               # RAG 课程与个人知识库问答
├── 04-agent/             # 工具调用与检索 Agent
├── 05-swe-agent/         # 受限代码修复与测试证据核验
├── .env.example          # 基础密钥变量示例，完整配置见上文
├── .gitignore
├── learning-log.md
├── resources.md
└── README.md
```

## 当前版本范围

本仓库已完成从 Python 基础、模型 API、RAG 到 Agent 与受限代码修复的学习实践。当前成果按课程与阶段项目验收，使用范围如下：

- RAG 使用本地 JSON 索引和逐个向量比较，未接入专门的向量数据库；文档格式暂限 Markdown/TXT。
- Stage 2 CLI 学习助手实时打印 SSE 文本增量；Stage 3 RAG 客户端将增量拼接后返回完整答案；Stage 4/5 Agent 请求使用非流式方式。
- 来源编号支持追溯，但未自动逐句验证答案与证据的支持关系；人工评估样本有限。
- SWE 只有一道任务的一次真实修复记录，没有系统级沙箱、自动回滚或多任务成功率验证。

- 交互入口以命令行为主；当前版本未提供 Web 页面、FastAPI 服务或问答记录数据库。

`.env`、真实密钥、私密资料与含敏感内容的运行日志不应提交到仓库。
