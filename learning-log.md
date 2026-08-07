# Learning Log

## 2026-07-26

### Today I Learned

- Started the AI Agent learning path from Python basics.
- Created a learning repository structure.

### Code I Wrote

- Not yet.

### Problems

- Not yet.

### Solutions

- Not yet.

### Tomorrow / Next Step

- Learn Python variables, data types, and `print`.
- Finish the first practice file in `00-python-basic/practice`.

## 2026-08-01

### Today I Learned
- 学会了用 pathlib 读取文本文件
- 学会了统计字符数、行数和关键词出现次数
- 学会了把 Python 字典保存成 JSON 文件

### Code I Wrote
- 新增 lesson_02_text_stats.py
- 生成 text_stats_result.json

### Problems
- 暂无

### Solutions
- 暂无

### Next Step
- 把统计逻辑封装成函数

## 2026-08-01

### Today I Learned
- 学会了用 sys.argv 接收命令行参数
- 学会了用 args[2:] 接收多个关键词
- 学会了用 for 循环统计多个关键词
- 学会了把统计逻辑封装成函数

### Code I Wrote
- 新增 lesson_03_log_analyzer.py
- 生成 log_analysis_result.json

### Problems
- 直接输入文件夹路径会被 PowerShell 当成命令执行

### Solutions
- 使用 cd 命令进入文件夹

### Next Step
- 给脚本增加更友好的错误提示git status

## 2026-08-02

### Today I Learned
- 学会了用 try/except 处理文件读取错误
- 学会了用 FileNotFoundError 处理文件不存在的情况
- 学会了用 UnicodeDecodeError 处理文件编码错误
- 学会了把读取文件、分析文本、保存 JSON 拆成不同函数
- 学会了用返回值判断程序是否继续执行

### Code I Wrote
- 新增 lesson_04_error_handling.py
- 生成 error_handling_result.json
- 测试了正常输入和错误输入

### Problems
- 直接点击 VS Code 运行按钮时，没有传入命令行参数，只显示 Usage 提示

### Solutions
- 在终端手动运行带参数的命令
- 正常运行示例：python 00-python-basic\practice\lesson_04_error_handling.py learning-log.md python agent json
- 错误测试示例：python 00-python-basic\practice\lesson_04_error_handling.py not-exist.md python

### Next Step
- 学习虚拟环境和 pip

## 2026-08-03

### Today I Learned
- 学会了用 conda 创建独立 Python 环境
- 学会了激活和退出 conda 环境
- 学会了用 pip 安装第三方库
- 学会了用 where.exe python 检查当前 Python 来自哪个环境
- 学会了用 python -c 快速测试库是否安装成功

### Commands I Ran
- conda create -n ai-agent python=3.11 pip -y
- conda activate ai-agent
- python --version
- where.exe python
- pip install requests
- python -c "import requests; print(requests.__version__)"
- conda deactivate

### Problems
- 暂无

### Solutions
- 暂无

### Next Step
- 学习 HTTP/API 请求

## 2026-08-03

### Today I Learned
- 学会了用 requests.get 发送 HTTP GET 请求
- 学会了查看 response.status_code
- 学会了用 response.json() 解析 API 返回的 JSON
- 学会了用 headers 告诉服务器希望接收什么格式的数据
- 理解了 application/json 和 application/vnd.github+json 的区别
- 理解了 User-Agent 是告诉服务器当前请求来自哪个程序
- 理解了 403 可能是 API 限流，换代理后请求成功

### Code I Wrote
- 新增 lesson_06_http_api.py
- 新增 lesson_06_httpbin_api.py
- 生成 github_user_result.json

### Problems
- GitHub API 一开始返回 403
- httpbin 返回 503

### Solutions
- 给请求添加 headers
- 换代理节点后 GitHub API 请求成功

### Next Step
- 开始 lesson 07：第 0 阶段综合项目

## 2026-08-04

### Today I Learned
- 学会了用函数把程序拆成多个部分
- 学会了统计学习记录数量
- 学会了用字典和列表生成总结内容
- 学会了把 Python 数据保存成 JSON
- 学会了把总结内容保存成 Markdown 文件
- 理解了 `.md` 文件和 `.txt` 文件本质上都是文本文件

### Code I Wrote
- 新增 `lesson_07_learning_log_analyzer.py`
- 生成 `learning_summary.json`
- 生成 `learning_summary.md`

### Problems
- 前面写代码时出现过变量名写错的问题，比如 `argv`、`text_path`
- 运行时需要注意命令行参数是否传入完整

### Solutions
- 统一使用 `args = sys.argv`
- 统一使用 `file_path` 作为读取文件的变量名
- 通过终端手动传入文件路径和关键词参数
- 先生成 JSON，再生成 Markdown，总结结果更清晰

### Next Step
- 开始 lesson 08：整理第 0 阶段项目和 README


**第四步：更新 learning-log.md**

在最后追加：

```markdown
## 2026-08-07

### Today I Learned
- 整理了第 0 阶段学习成果
- 更新了项目 README
- 梳理了 Python 基础阶段完成的 lesson
- 明确了学习日志分析器的运行方式和输出结果

### Code I Wrote
- 暂无新代码，主要进行项目整理

### Problems
- 需要把零散练习整理成 GitHub 上容易阅读的项目说明

### Solutions
- 更新根目录 README.md
- 更新 00-python-basic/README.md
- 写清楚项目结构、运行命令和阶段成果

### Next Step
- 进入第 1 阶段：AI 工具使用和 Prompt
