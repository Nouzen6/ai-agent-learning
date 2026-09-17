# Lesson 07：将检索结果放入 Prompt

## 学习目标

- 将 top-k 检索结果整理为上下文
- 在上下文中保留资料编号、正文和来源
- 构造要求 LLM 基于资料回答的 Prompt
- 在没有检索结果时拒绝调用 LLM
- 使用 Mock 测试回答流程
- 理解检索内容中的 Prompt 注入风险

## RAG 流程位置

用户问题
→ Embedding
→ Top-k 检索
→ 构造上下文
→ 构造 Prompt
→ LLM 生成答案

## 文件说明

- `rag_prompt_builder.py`：构造上下文、Prompt 并协调回答流程
- `test_rag_prompt_builder.py`：单元测试

## 核心函数

### build_context

将检索结果中的正文、编号和来源整理为上下文。

### build_prompt

将回答规则、检索上下文和用户问题组成最终 Prompt。

### can_generate_answer

判断是否存在支持回答的检索结果。

### answer_question

没有检索结果时直接拒答；有结果时构造 Prompt 并调用 LLM。

## 运行测试

```powershell
python -m unittest -v