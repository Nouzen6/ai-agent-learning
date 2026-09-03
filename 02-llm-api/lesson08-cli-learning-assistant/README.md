# 命令行 AI 学习助手

这是 Stage 2 的综合项目：使用 Python 调用大模型 API，实现支持流式输出、上下文记忆和学习记录分析的命令行 AI 助手。

## 功能

- 在命令行中连续提问
- 使用 SSE 实时显示模型回答
- 保存当前会话的上下文
- 使用 `/analyze` 分析学习记录
- 校验模型返回的 JSON 结构
- 将分析结果保存为本地 JSON 文件
- 处理超时、网络错误和响应格式错误
- 使用 Mock 完成不消耗 API 费用的单元测试

## 文件说明

```text
lesson08-cli-learning-assistant/
├── cli_learning_assistant.py
├── cli_learning_assistant_memory.py
├── test_cli_learning_assistant.py
└── README.md
```

- `cli_learning_assistant.py`：基础流式学习助手
- `cli_learning_assistant_memory.py`：支持上下文和学习分析的完整版本
- `test_cli_learning_assistant.py`：项目单元测试
- `learning_analysis.json`：运行时生成的分析结果，不提交到 Git

## 环境要求

- Python 3.9 或更高版本
- DeepSeek API key
- `requests`
- `python-dotenv`

安装依赖：

```powershell
pip install requests python-dotenv
```

## 配置 API Key

在仓库根目录创建 `.env`：

```env
DEEPSEEK_API_KEY=你的真实密钥
```

`.env` 包含敏感信息，必须由 `.gitignore` 忽略。不要把真实密钥提交到 GitHub。

## 运行程序

在仓库根目录执行：

```powershell
python .\02-llm-api\lesson08-cli-learning-assistant\cli_learning_assistant_memory.py
```

普通对话：

```text
你：什么是 RAG？
```

分析学习记录：

```text
你：/analyze 我已经学会 Python、requests 和 JSON，现在开始学习 RAG。
```

退出程序：

```text
你：exit
```

## 运行测试

```powershell
python .\02-llm-api\lesson08-cli-learning-assistant\test_cli_learning_assistant.py -v
```

项目包含 9 个测试，覆盖：

- 普通文本提取
- 多段文本拼接
- 空响应处理
- SSE 流式输出
- 学习分析成功响应
- 非法 JSON
- 缺少必要字段
- 字段类型错误
- JSON 文件保存

所有 API 测试均使用 Mock，不会发送真实请求或消耗 API 额度。

## 主要知识点

- HTTP POST、headers 和 JSON body
- 环境变量与 API key 安全
- LLM messages 对话上下文
- SSE 流式响应
- JSON 解析和字段校验
- 文件持久化
- 异常处理
- `unittest`、Mock 和 patch
