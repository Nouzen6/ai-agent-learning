# 个人知识库问答助手

一个使用 Python 手写核心流程的命令行 RAG 项目。

程序读取本地 Markdown 和 TXT 文档，清洗并切分文本，调用 Embedding API 建立索引。用户提问时，程序检索相关片段，将资料交给 LLM 生成回答，并显示检索到的资料来源。

## 功能

- 读取 `.md` 和 `.txt` 知识库文件
- 清洗文本并切分为 chunks，默认 `chunk_size=500`、`overlap=50`
- 调用 Embedding API 将文档和问题转换为向量
- 将文本、向量和 metadata 保存到 JSON 索引
- 使用向量相似度进行 top-k 检索，并按分数阈值过滤
- 将检索结果放入 Prompt，调用 LLM 生成回答
- 显示检索结果对应的资料来源
- 处理索引缺失、空索引、空问题以及常见网络异常
- 使用 Mock 编写单元测试，避免测试依赖真实 API

## RAG 流程

### 建立索引

```text
读取 knowledge_base/ 中的文档
→ 清洗文本
→ 将文本切分为 chunks
→ 调用 Embedding API 生成向量
→ 将文本、向量和 metadata 保存到 data/index.json
```

### 回答问题

```text
接收用户问题
→ 调用 Embedding API 将问题转换为向量
→ 检索相关文档片段并进行阈值过滤
→ 将检索结果放入 Prompt
→ 调用 LLM 生成答案
→ 显示答案和资料来源
```

如果没有片段通过相似度阈值，程序会返回资料不足的提示，不调用 LLM。

## 技术实现

- 开发语言：Python
- HTTP 请求：requests
- 环境变量加载：python-dotenv
- Embedding 服务：SiliconFlow，使用 BAAI/bge-m3
- 回答生成：DeepSeek API
- 索引存储：本地 JSON 文件
- 向量检索：手写余弦相似度计算与排序
- 单元测试：unittest、Mock 和 patch

项目使用 JSON 保存索引，没有接入专门的向量数据库，也没有使用 LangChain 或 LlamaIndex 等框架。

## 环境准备

在仓库根目录打开 PowerShell。

如果已经有可用的虚拟环境，直接启用即可；否则先创建：

```powershell
python -m venv .venv
```

启用虚拟环境：

```powershell
.\.venv\Scripts\Activate.ps1
```

安装依赖：

```powershell
python -m pip install requests python-dotenv
```

## 配置环境变量

在仓库根目录创建 `.env` 文件。

目录位置如下：

```text
ai-agent-learning/
├── .env
└── 03-rag/
    └── personal_rag_assistant/
```

在 `.env` 中填写以下配置：

```dotenv
LLM_API_URL=
LLM_MODEL=
DEEPSEEK_API_KEY=

EMBEDDING_API_URL=
EMBEDDING_MODEL=
EMBEDDING_API_KEY=
```

各配置项的含义：

| 变量 | 用途 |
| --- | --- |
| `LLM_API_URL` | LLM 聊天接口的完整请求地址 |
| `LLM_MODEL` | 用于生成回答的模型名称 |
| `DEEPSEEK_API_KEY` | 调用 LLM 服务使用的 API key |
| `EMBEDDING_API_URL` | Embedding 接口的完整请求地址 |
| `EMBEDDING_MODEL` | 用于生成向量的模型名称 |
| `EMBEDDING_API_KEY` | 调用 Embedding 服务使用的 API key |

请根据服务商文档填写接口地址、模型名称和自己的密钥。

安全要求：

- 不要将真实 API key 写入 Python 代码或 README。
- 不要将 `.env` 提交到 Git 仓库。
- 确保 `.gitignore` 已忽略 `.env`。
- 不要在截图或日志中展示真实 API key。

## 添加知识库文档

将 `.md` 或 `.txt` 文件放入项目的 `knowledge_base/` 目录：

```text
knowledge_base/
├── llm_api_notes.txt
└── learning_path.md
```

真实运行时，文档片段和用户问题会发送给所配置的 Embedding 服务；检索片段及问题会发送给所配置的 LLM 服务。因此，知识库应使用适合发送给这些服务的资料。

## 建立索引

从仓库根目录进入项目目录：

```powershell
cd 03-rag/personal_rag_assistant
```

运行建索引程序：

```powershell
python index_documents.py
```

程序会读取知识库、清洗和切分文本、调用 Embedding API，并保存索引：

```text
data/index.json
```

每个索引片段包含：

- `id`：片段标识
- `text`：片段原文
- `embedding`：片段对应的向量
- `metadata`：来源文件、片段序号等信息

程序会输出 chunk 数量，以及保存前后数据是否一致。

### 更新索引

当前程序会阻止直接覆盖已有索引，以避免误操作和重复调用 API。

修改知识库后，需要先备份或移走原来的 `data/index.json`，再运行：

```powershell
python index_documents.py
```

文档向量和问题向量需要使用一致的 Embedding 模型及配置。如果更换 Embedding 模型，应重新生成整个索引。

建立索引会调用真实 Embedding API，可能产生费用。

## 启动问答助手

在项目目录运行：

```powershell
python cli.py
```

启动后输入问题，例如：

```text
网络请求失败时应该如何处理？
```

程序会检索相关资料，生成回答，并显示资料来源。

输入以下内容退出：

```text
exit
```

当前 CLI 的检索参数为：

- `k=3`：最多返回 3 个符合条件的片段
- `score_threshold=0.6`：过滤低于该分数的片段

相似度分数不是答案正确率。阈值需要结合实际知识库和测试问题调整。

## 异常处理

当前程序覆盖以下情况：

| 情况 | 处理方式 |
| --- | --- |
| 索引文件不存在 | 提示先运行建索引程序并退出 |
| 索引中没有文档片段 | 提示检查知识库并重新建立索引 |
| 用户输入空问题 | 提示输入问题并继续等待 |
| 没有片段通过检索阈值 | 提示资料不足，不调用 LLM |
| API 请求超时 | 显示提示，允许继续提问 |
| API 连接失败 | 显示提示，允许继续提问 |
| API 返回 HTTP 错误 | 显示提示，允许继续提问 |

没有片段通过阈值，只能说明当前检索没有找到符合条件的资料，并不能证明知识库中一定不存在答案。

## 运行测试

在项目目录运行全部单元测试：

```powershell
python -m unittest discover -v
```

只运行命令行相关测试：

```powershell
python -m unittest -v test_cli.py
```

当前已通过 46 个单元测试，覆盖：

- 文档读取
- 文本清洗与切块
- Embedding 响应解析与校验
- 索引保存和加载
- 向量检索与阈值过滤
- 问题检索流程
- Prompt 与回答生成流程
- LLM 流式响应处理
- 环境变量配置检查
- 命令行交互与常见异常处理

API 相关测试使用 Mock，不发送真实 API 请求。测试通过说明所覆盖的程序行为符合预期，不代表真实服务始终可用，也不代表回答质量已经完成评估。

## 项目结构

```text
personal_rag_assistant/
├── knowledge_base/          # Markdown 和 TXT 知识文档
├── data/
│   └── index.json           # 生成的文档索引
├── answer_question.py       # 组织检索、Prompt 和回答生成
├── cli.py                   # 命令行问答入口
├── config.py                # 读取并检查环境变量
├── document_loader.py       # 文档读取
├── embedding_client.py      # Embedding API 客户端
├── embedding_pipeline.py    # 为文档片段添加向量
├── index_documents.py       # 建立索引的入口
├── index_storage.py         # 保存和加载 JSON 索引
├── llm_client.py            # LLM API 客户端
├── query_pipeline.py        # 问题向量化与检索流程
├── text_chunker.py          # 文本清洗和切块
├── vector_search.py         # 向量相似度检索
├── check_embedding.py       # Embedding 调试脚本
├── check_retrieval.py       # 检索调试脚本
└── test_*.py                # 单元测试
```

## 当前限制

- 索引保存在 JSON 文件中，向量检索采用逐个比较的方式，适合学习和小型知识库。
- 文档读取器目前支持 Markdown 和 TXT，尚未实现 PDF 解析和 OCR。
- 使用固定长度切块，可能将完整语义切开。
- 尚未加入关键词与向量混合检索、rerank 或系统化回答质量评估。
- 当前显示的是检索资料的来源文件，不是经过逐句验证的答案引用。
- RAG 可以提供参考资料，但仍可能出现漏检、无关片段干扰或回答不忠于资料等问题。

## 后续改进

- 建立包含问题、参考答案和来源的评估集
- 分别评估检索是否命中、回答是否忠于资料
- 比较不同 chunk 长度和 overlap 的效果
- 调整 top-k 与相似度阈值
- 引入 rerank，提高片段排序质量
- 完善片段级引用和来源定位
- 根据知识库规模考虑使用专门的向量数据库