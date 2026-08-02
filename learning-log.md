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

