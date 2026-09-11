# Lesson 06：Top-K 文档片段检索

本项目是 Stage 3 RAG 学习路线中的 Lesson 06 示例，用于手写一个最小版本的向量检索器。

本示例不调用真实 LLM API，也不调用 embedding API，而是使用固定的二维向量来理解 RAG 中的核心检索流程。

## 学习目标

通过本示例理解：

- 什么是余弦相似度
- 如何比较查询向量和文档向量
- 什么是 top-k 检索
- 为什么检索结果需要包含原始文本和 metadata
- 相似度阈值如何过滤低相关结果

## 核心流程

RAG 中的检索阶段可以简化为：

```text
用户问题
→ 问题向量
→ 和文档 chunk 向量计算相似度
→ 按相似度从高到低排序
→ 返回 top-k 文档片段
→ 将文本片段放入 prompt
本项目实现的是其中的：
计算相似度
→ 排序
→ 阈值过滤
→ 返回 top-k
文件说明
simple_retriever.py
test_simple_retriever.py
README.md
simple_retriever.py
包含两个核心函数：
cosine_similarity(vector_a, vector_b)
用于计算两个向量之间的余弦相似度。
retrieve_top_k(query_vector, documents, k, score_threshold=None)
用于从多个文档 chunk 中检索最相关的前 k 个结果。
test_simple_retriever.py
使用 Python 内置的 unittest 对检索逻辑进行测试。
测试内容包括：
- 相同方向向量的相似度
- 垂直方向向量的相似度
- top-k 排序是否正确
- 相似度阈值是否生效
- 没有结果时是否返回空列表
- k <= 0 时是否抛出异常
- k 大于文档数量时是否正常返回全部结果
数据结构
每个文档 chunk 使用字典表示：
{
    "id": "chunk-a",
    "vector": [1, 0],
    "text": "requests 网络请求失败时，可以捕获 ConnectionError。",
    "metadata": {
        "source": "02-llm-api/README.md",
        "chunk_id": 1
    }
}
字段含义：
- id：文档片段的唯一标识
- vector：文档片段对应的向量
- text：原始文本内容，用于后续放入 prompt
- metadata：来源信息，用于引用、调试和追踪
余弦相似度
余弦相似度用于衡量两个向量方向是否接近。
公式：
cosine_similarity(A, B) = A · B / (|A| × |B|)
含义：
- 相似度越高，通常表示语义越相关
- 相似度越低，通常表示语义越不相关
在本示例中：
[1, 0] 和 [1, 0] 的相似度是 1.0
[1, 0] 和 [0, 1] 的相似度是 0.0
[1, 0] 和 [0.8, 0.6] 的相似度是 0.8
Top-K 检索
top-k 表示返回相似度排名最靠前的 k 个结果。
例如：
results = retrieve_top_k(query_vector, documents, k=2)
表示返回最相关的 2 个文档片段。
需要注意：
top-k 只保证返回排名靠前的结果，不保证这些结果一定足够相关。
相似度阈值
为了避免低相关内容进入 prompt，可以使用相似度阈值：
results = retrieve_top_k(
    query_vector,
    documents,
    k=3,
    score_threshold=0.7
)
含义是：
只返回相似度大于等于 0.7 的结果，最多返回 3 条。
如果所有结果都低于阈值，则返回空列表。
如何运行
进入项目目录：
cd "C:\Users\Eason\Documents\AI开发学习\ai-agent-learning\03-rag\lesson06-top-k-retrieval"
运行示例程序：
python simple_retriever.py
预期可以看到类似输出：
排名 1：chunk-a，相似度 1.00
排名 2：chunk-b，相似度 0.80

不使用阈值：
排名 1：chunk-a，相似度 1.00
排名 2：chunk-b，相似度 0.80
排名 3：chunk-c，相似度 0.00

使用阈值 0.7：
排名 1：chunk-a，相似度 1.00
排名 2：chunk-b，相似度 0.80
如何运行测试
在当前目录运行：
python -m unittest -v
预期结果：
OK
当前限制
本项目是为了理解检索原理，因此做了简化：
- 使用固定二维向量，没有调用真实 embedding API
- 使用 Python 列表保存文档，没有使用向量数据库
- 使用暴力遍历计算相似度，没有使用 FAISS、Qdrant 等索引
- 文档数据是手写的，没有接入真实知识库文件
- 暂时没有把检索结果放入 prompt
这些限制会在后续课程中逐步改进。
在 RAG 流程中的位置
本项目对应 RAG 流程中的检索阶段：
文档读取
→ 文本清洗
→ chunk 分块
→ embedding
→ 向量检索 ← 当前项目
→ 构造 prompt
→ LLM 生成答案

本项目手写实现了一个最小 top-k 检索器。系统会将用户问题向量和文档 chunk 向量逐个计算余弦相似度，然后按相似度从高到低排序，返回最相关的前 k 个结果。同时，检索结果保留了原始文本和 metadata，方便后续将文本放入 prompt，并使用 metadata 标注来源。为了减少无关内容进入 prompt，还加入了相似度阈值过滤。