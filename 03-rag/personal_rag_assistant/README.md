# 个人知识库问答助手

一个使用 Python 手写核心流程的命令行 RAG 项目。

程序读取本地 Markdown 和 TXT 文档，清洗并切分文本，调用 Embedding API 建立索引。用户提问时，程序检索相关片段，可选使用 rerank 重新排序，将最终资料交给 LLM 生成带编号引用的回答，并显示资料编号与文件、片段的对应关系。

## 功能

- 读取 `.md` 和 `.txt` 知识库文件
- 清洗文本并切分为 chunks，默认 `chunk_size=500`、`overlap=50`
- 调用 Embedding API 将文档和问题转换为向量
- 将文本、向量和 metadata 保存到 JSON 索引
- 使用向量相似度进行 top-k 检索，并按分数阈值过滤
- 使用 `--rerank` 可选启用 Rerank API，对候选片段重新评分和排序
- 将检索结果放入 Prompt，调用 LLM 生成回答
- 要求模型使用 `[资料 N]` 引用，并由程序维护编号、来源文件、片段编号的映射
- 区分程序行为测试与人工回答质量评估，保留实际运行记录
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
→ 按余弦相似度排序并进行阈值过滤
→ 普通模式直接取前 k 个；rerank 模式先取最多 candidate_k 个候选
→ rerank 模式调用评分服务重新排序，再取前 k 个
→ 按最终片段顺序生成资料编号和来源映射
→ 将最终资料、回答规则和用户问题放入 Prompt
→ 调用 LLM 生成答案
→ 显示答案，以及提供给模型的资料清单
```

如果没有片段通过相似度阈值，程序会返回资料不足的提示，不调用 Rerank API 或生成答案的 LLM；问题向量化仍可能已经调用 Embedding API。rerank 只能重排候选，不能找回被阈值过滤掉的片段。

## 技术实现

- 开发语言：Python
- HTTP 请求：requests
- 环境变量加载：python-dotenv
- Embedding 服务：SiliconFlow，使用 BAAI/bge-m3
- 回答生成：DeepSeek API
- 索引存储：本地 JSON 文件
- 向量检索：手写余弦相似度计算与排序
- 可选重排：通过 HTTP 调用 Rerank API，使用返回的 `relevance_score` 排序
- 引用来源：根据最终上下文维护 `[资料 N]` 与文件、片段编号的映射
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

# 仅在使用 python cli.py --rerank 时需要
RERANK_API_URL=
RERANK_MODEL=
RERANK_API_KEY=
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
| `RERANK_API_URL` | 可选，Rerank 接口的完整请求地址 |
| `RERANK_MODEL` | 可选，用于重新评分的模型名称 |
| `RERANK_API_KEY` | 可选，调用 Rerank 服务使用的 API key |

请根据服务商文档填写接口地址、模型名称和自己的密钥。

普通模式不要求配置 `RERANK_*`。仅在传入 `--rerank` 时，程序才加载并检查这三项。当前客户端使用 `query`、`documents` 等请求字段，并解析 `results` 中的 `index` 和 `relevance_score`；需要选择与当前实现兼容的接口。

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

真实运行时，文档片段和用户问题会发送给所配置的 Embedding 服务；最终检索片段及问题会发送给所配置的 LLM 服务。启用 rerank 时，问题和候选片段还会发送给配置的 Rerank 服务。因此，知识库应使用适合发送给这些服务的资料。

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

正式索引仍采用 `chunk_size=500`、`overlap=50`。`check_chunk_sizes.py` 用于本地观察切块边界，目前包含按双换行预览段落的实验；运行预览不会自动修改正式切块策略或重建索引。

## 启动问答助手

在项目目录运行：

```powershell
python cli.py
```

启用 rerank：

```powershell
python cli.py --rerank
```

查看命令行选项：

```powershell
python cli.py --help
```

启动后输入问题，例如：

```text
网络请求失败时应该如何处理？
```

程序会检索相关资料，生成回答，并显示资料来源。例如，一次已记录的运行输出为：

```text
AI：网络请求可能出现连接失败、请求超时和 HTTP 错误 [资料 1]。程序应该捕获相关异常，并向用户返回清晰的错误信息 [资料 1]。
提供给模型的资料：
[资料 1] llm_api_notes.txt，片段 0
```

该清单列出本次最终送入 Prompt 的全部片段，不等于模型实际引用过的片段清单，也不代表程序已自动验证每句话都有证据支持。当前仍保留生成回答前打印完整上下文的调试输出，便于人工核查。

输入以下内容退出：

```text
exit
```

当前 CLI 的检索参数为：

- `k=3`：最多返回 3 个符合条件的片段
- `score_threshold=0.6`：过滤余弦相似度低于该分数的片段
- `candidate_k=10`：启用 rerank 时，最多取 10 个通过阈值的候选，再选出最终最多 3 个片段

余弦相似度和 rerank 返回的相关性分数属于两次不同的评分；`0.6` 用于前者，不是 rerank 分数阈值。两者都不是答案正确率。阈值需要结合实际知识库和测试问题调整。

当前实现逐个候选请求评分：有 N 个候选就会发送 N 次 Rerank API 请求，尚未批量处理；真实运行可能增加耗时和费用。

## 异常处理

当前程序覆盖以下情况：

| 情况 | 处理方式 |
| --- | --- |
| 索引文件不存在 | 提示先运行建索引程序并退出 |
| 索引中没有文档片段 | 提示检查知识库并重新建立索引 |
| 用户输入空问题 | 提示输入问题并继续等待 |
| 没有片段通过检索阈值 | 提示资料不足，不调用 Rerank API 或生成答案的 LLM |
| 启用 rerank 但缺少必要配置 | 启动时提示缺失配置，不进入问答 |
| rerank 响应缺少结果、索引无效或分数不合法 | 提示数据错误，允许继续提问 |
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

仅检查重排及其检索接入：

```powershell
python -m unittest -v test_reranker test_rerank_client test_rerank_integration test_query_pipeline
```

截至 2026-10-28，当前已通过 62 个单元测试，覆盖：

- 文档读取
- 文本清洗与切块
- Embedding 响应解析与校验
- 索引保存和加载
- 向量检索与阈值过滤
- 问题检索流程
- rerank 排序、最终数量限制及无效参数检查
- Rerank API 请求构造、响应解析、分数校验和网络异常
- rerank 与问题检索流程的组合，包括空检索分支
- Prompt、资料编号映射与回答生成流程
- LLM 流式响应处理
- 环境变量配置检查
- 命令行交互与常见异常处理

API 相关测试使用 Mock，不发送真实 API 请求。测试通过说明所覆盖的程序行为符合预期，不代表真实服务始终可用，也不代表回答质量已经完成评估。

## 回答质量评估

Lesson 09–10 的归档选取了 4 个不同问题的 7 次真实问答运行：前 6 次保留正常问答、空检索兜底、临时关闭阈值实验与完整性检查；第 7 次补充启用 rerank 后的编号引用验收。另行记录切块实验和 Mock 验证，不把它们计入真实问答次数。

详细问题、参考证据、各次配置、实际回答和判断见 [RAG 人工评估记录](EVALUATION.md)。记录分别检查检索命中、回答忠实度、参考答案符合情况、回答完整性和来源标注；不把程序兜底视为模型拒答能力的证明。

目前只有少量人工样例，尚未完成系统化质量评估。临时实验使用的 `score_threshold=None` 与默认 `0.6` 分开记录，不能混为同一配置的结果。

最新样例中，答案覆盖网络异常与处理方式的全部 5 项要点，两个实质性主张均由本次资料支持，编号映射一致。这只能说明该次观察符合标准，不能证明 rerank 普遍提升质量，也不代表已实现自动引用验证。

## 项目结构

```text
personal_rag_assistant/
├── EVALUATION.md            # 人工评估样例、运行记录与结论
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
├── query_pipeline.py        # 问题向量化、候选检索与可选重排
├── reranker.py              # 根据评分函数重排并选取最终片段
├── rerank_client.py         # Rerank API 请求与响应校验
├── text_chunker.py          # 文本清洗和切块
├── vector_search.py         # 向量相似度检索
├── check_embedding.py       # Embedding 调试脚本
├── check_retrieval.py       # 检索调试脚本
├── check_chunk_sizes.py     # 本地切块边界实验预览
├── check_rerank.py          # 使用人工评分演示重排，不调用 API
├── test_reranker.py         # 重排逻辑与参数测试
├── test_rerank_client.py    # Rerank API 的 Mock 测试
├── test_rerank_integration.py # 重排与检索组合的 Mock 测试
└── test_*.py                # 其余单元测试
```

## 当前限制

- 索引保存在 JSON 文件中，向量检索采用逐个比较的方式，适合学习和小型知识库。
- 文档读取器目前支持 Markdown 和 TXT，尚未实现 PDF 解析和 OCR。
- 使用固定长度切块，可能将完整语义切开。
- 已完成少量人工回答质量评估和可选 rerank，尚未形成系统化评估，也未加入关键词与向量混合检索。
- rerank 只处理阈值过滤后的候选；逐个请求尚未批量优化，也没有足够对照样例证明其收益。
- 已实现资料编号与文件、片段的映射，但尚未自动检查模型是否使用合法编号、每个主张是否受支持，或只展示实际引用的资料。
- 部分可回答的问题仍需统一回答策略并增加复测；当前保留完整上下文的调试打印。
- RAG 可以提供参考资料，但仍可能出现漏检、无关片段干扰或回答不忠于资料等问题。

## 后续改进

- 扩展已有人工评估样例，补充问题、参考答案、来源和运行条件
- 分别评估检索是否命中、回答是否忠于资料
- 比较不同 chunk 长度和 overlap 的效果
- 调整 top-k 与相似度阈值
- 扩展普通检索与 rerank 的同条件对照，记录质量、耗时和调用次数
- 优化 rerank 批量请求，减少逐个评分的开销
- 增加引用编号检查、主张与证据核查，并区分已提供资料与实际引用资料
- 明确部分回答策略，整理调试输出开关
- 根据知识库规模考虑使用专门的向量数据库

归档更新日期：2026-10-28。
