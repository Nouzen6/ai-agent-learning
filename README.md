# AI Agent Learning

This repository records my learning path from Python basics to AI Agent development.

## Roadmap

- Stage 0: Python, Git, environment, HTTP/API basics
- Stage 1: AI tools and prompt engineering
- Stage 2: LLM API application development
- Stage 3: RAG knowledge base project
- Stage 4: Agent development
- Stage 5: Minimal SWE Agent

## Current Progress

Stage 0 is nearly complete.

Completed lessons:

- Lesson 01: Variables, data types, and print
- Lesson 02: File reading, text statistics, and JSON output
- Lesson 03: Command-line arguments and keyword statistics
- Lesson 04: Error handling and function splitting
- Lesson 05: Conda environment and pip
- Lesson 06: HTTP/API requests
- Lesson 07: Learning log analyzer project

## Stage 0 Project

The main project of Stage 0 is a learning log analyzer.

It can:

- Read `learning-log.md`
- Count characters and lines
- Count learning entries
- Count keywords
- Save summary as JSON
- Save summary as Markdown

Run:

Run:

```bash
conda activate ai-agent
python 00-python-basic/project/learning_log_analyzer.py learning-log.md python agent json git api
```

Outputs:

```text
00-python-basic/project/learning_summary.json
00-python-basic/project/learning_summary.md
```

## Repository Structure

```text
ai-agent-learning/
├── learning-log.md
├── resources.md
├── 00-python-basic/
│   ├── practice/
│   └── project/
├── 01-command-line-git/
├── 02-llm-api/
├── 03-rag/
├── 04-agent/
└── 05-swe-agent/
```

## Notes

This repository is for learning and practice. API keys, passwords, `.env` files, and private data should never be committed.