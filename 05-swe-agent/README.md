# Stage 5：minimal SWE Agent

本项目在已有工具调用与 Agent 循环基础上，实现一个能够读取练习代码、修改指定文件、运行固定测试，并根据执行反馈继续行动的最小 SWE Agent。

练习任务：修复 average(values)，使非空数字列表返回平均值，空列表返回 0。

当前练习文件已完成一次真实模型修复，三个业务用例通过。验证范围有限，尚未完成多任务、重复运行的系统化评估。

## 工作流程

用户任务
→ 模型选择工具并生成参数
→ Python 校验并执行工具
→ 工具结果回传
→ 模型根据反馈继续行动或给出最终文本
→ 程序根据 trace 核验测试通过证据
→ 运行入口保存返回结果与 trace

模型使用 DeepSeek Chat Completions，本地注册表负责执行函数。

工具参数 arguments 是 JSON 字符串，经 json.loads 转为 Python 字典。
工具返回 Python 字典，经 json.dumps 转成 JSON 字符串，放入 role="tool" 消息的 content。
tool_call_id 用于对应原工具调用。

## 工具与访问范围

练习根目录：05-swe-agent/practice/。

| 工具 | 范围与限制 |
| --- | --- |
| read_file(path) | 只读 solution.py、test_solution.py；最多返回 8000 个字符，并标记截断 |
| write_file(path, content) | 只覆盖已有的 solution.py；内容非空、最多 8000 字符，通过 Python 语法解析后写入 |
| run_tests() | 无命令参数；在练习目录运行固定 unittest 命令；超时 10 秒 |

文件工具拒绝绝对路径，并在解析路径后检查目录范围和白名单。
读取与写入权限分别控制，测试文件不在写入白名单中。

测试使用当前 Python 解释器，以 -B -X utf8 -m unittest -v test_solution 运行。
stdout、stderr 各最多回传 4000 个字符。

这些规则是工具层的约束。测试会执行练习代码，目前没有操作系统级沙箱，不适合运行不可信代码。

## 文件职责

| 文件 | 职责 |
| --- | --- |
| lesson02_read_file.py | 路径校验与受限读取 |
| lesson03_write_file.py | 写入权限、内容及语法检查 |
| lesson04_run_tests.py | 固定测试命令、超时与输出处理 |
| lesson05_swe_agent.py | 工具 schema、异常包装、SWE 入口 |
| lesson05_real_run.py | 真实模型运行入口、核验结果展示与记录保存 |
| lesson06_agent_loop.py | 基于 Stage 4 扩展的循环，增加工具预算 |
| lesson06_run_record.py | 保存返回结果和 trace |
| lesson05_mock_test.py | 模拟工具往返与异常包装测试 |
| lesson06_budget_test.py | 工具预算测试 |
| lesson06_record_test.py | JSON 记录保存测试 |
| lesson07_acceptance_test.py | 文件边界、超时与模型轮数测试 |
| lesson08_verification.py | 根据 trace 顺序核验测试通过证据 |
| lesson08_verification_test.py | 核验事件顺序与入口接入测试 |
| practice/solution.py | 当前已修复的练习实现 |
| practice/test_solution.py | 三个业务测试 |

模型请求函数仍复用 04-agent/lesson03_api_roundtrip.py。
当前使用 sys.path 复用课程模块，尚未整理成可安装的 Python 包。

## 环境与配置

以下命令均在仓库根目录执行，使用已有 .venv。

依赖：requests、python-dotenv；测试框架 unittest 来自 Python 标准库。

真实运行入口从仓库根目录 .env 加载 DEEPSEEK_API_KEY。
不要提交 .env 或真实密钥。

当前模型配置：

- 地址：https://api.deepseek.com/chat/completions
- 模型：deepseek-flash
- stream=False
- thinking={"type": "disabled"}
- tool_choice="auto"

模型配置定义在复用的 API 请求模块中。

## 离线验收

运行 Agent 测试：

```powershell
& .\.venv\Scripts\python.exe -B -X utf8 -m unittest discover -s .\05-swe-agent -p "lesson*_test.py" -v
```

2026-11-20 本地复核结果：11 项测试全部通过，包含 Lesson 08 新增的两个测试方法。事件顺序测试中的多个 subTest 场景不单独计入测试方法总数。

覆盖：

- 模拟读取、测试失败、修改、测试通过的消息往返。
- 语法异常转换为结构化工具反馈。
- 同一响应中的工具调用逐条检查预算。
- 工具额度刚好用完后仍能给出最终文本。
- JSON 保存后完整读回，连续保存不覆盖。
- 越界读取、修改测试文件在打开文件前被拒绝。
- 模拟测试进程超时及输出截断。
- 模型请求超时后停止。
- 达到模型请求轮数上限后停止。
- 根据测试、写入等事件的先后顺序更新核验状态。
- 模型直接声称修好但没有测试时，completed 与 not_verified 可以同时出现。

模型与工具执行相关场景主要使用 Mock。
记录测试会在自动清理的临时目录真实写入和读取文件。
Mock 通过不代表真实模型能够自主修复其他任务。

运行业务测试：

```powershell
& .\.venv\Scripts\python.exe -B -X utf8 .\05-swe-agent\lesson04_run_tests.py
```

2026-11-20 本地复核：3 项通过，exit_code=0，未超时、未截断。

业务用例：

- [2, 4, 6] → 4
- [-4, -2] → -3
- [] → 0

## 真实运行

```powershell
& .\.venv\Scripts\python.exe -B -X utf8 .\05-swe-agent\lesson05_real_run.py
```

该命令会请求真实 API，发送练习文件内容和工具反馈，并可能修改 solution.py。

当前实现已修复。入口要求模型先检查和测试，满足要求时无需修改。

## 一次真实修复记录

依据真实终端日志和后续文件复查：

| 模型轮次 | 动作与结果 |
| --- | --- |
| 1 | 读取实现与测试，一轮生成两个读取请求 |
| 2 | 测试复现空列表 ZeroDivisionError |
| 3 | 写入空值判断，保留原函数说明 |
| 4 | 重新测试，3 项通过 |
| 5 | 给出最终文本，循环返回 completed |

本次共 5 轮模型请求、5 次工具调用。
测试文件内容与修复前一致，独立复查测试通过。

该记录来自增加工具预算、JSON 保存和测试证据核验功能之前的一次运行，不能作为这些新增功能的真实运行证据。

模型最终说明曾错误地声称 None 会抛 TypeError。
实际 if not values 也匹配 None，因此 average(None) 返回 0。
None 不在本练习的输入约定内，但这个例子说明最终文字说明仍需核对。

## 状态与工具反馈

| Agent 状态 | 含义 |
| --- | --- |
| completed | 模型给出有效最终文本 |
| step_limit | 模型请求轮数用完，未获得最终文本 |
| tool_limit | 下一条工具请求因额度不足而被拒绝 |
| api_error | 模型请求发生被捕获的网络或 HTTP 异常 |
| tool_error | 工具请求解析或执行发生循环捕获的异常 |

工具包装层返回：

- ok=True：工具正常返回，具体结果在 result 中。
- ok=False：发生被包装的异常，错误类型和说明在 error 中。

ok=True 与测试 exit_code=1 可以同时出现：
测试工具正常完成，但测试没有通过。

completed 不代表修复正确。
tool_limit、step_limit 不会撤销之前已经完成的文件修改。

run_swe_agent 返回时，会附加独立的 verification 字段，包含 status 和 reason：

| verification.status | 含义 |
| --- | --- |
| passed | 最近一次测试工具反馈为 ok=True、整数退出码为 0、timed_out=False，之后没有新的写入记录 |
| not_verified | 本次 trace 尚不能确认当前代码有测试通过证据 |

程序按 trace 顺序核验：

- 写入相关的 tool_result 或 tool_error 会使旧证据失效，包括写入失败的情况。
- 后续测试失败、超时或工具报错，也会使旧证据失效。
- 测试重新通过后，可以恢复为 passed。
- 模型的最终文本不改变核验结果。

终端分别展示循环状态、核验状态及核验原因。
passed 只表示指定测试的通过证据，不代表所有业务行为正确，也不代表整个任务已完成人工验收。

## 预算与记录

真实入口设置：

- max_steps=8：模型请求轮数上限。
- max_tool_calls=8：工具调用尝试额度。

每条工具请求执行前检查额度；已进入处理流程的失败尝试也消耗额度。
这两个限制不等于 token、费用或整次任务的总时间限制。

trace 事件包括：
model_request、tool_attempt、tool_result、final_answer、
tool_limit、api_error、tool_error。

tool_result 表示记录了工具返回值，内部仍可能是 ok=False。
trace 不会自动发送给模型，也不是模型的私有思考。

运行入口将返回结果保存至 `logs/run_<随机标识>.json`。
新运行记录包含 UTC 保存时间，以及 status、answer、steps、reason、trace、verification。
已有历史日志不会自动补充 verification。logs/ 已加入 .gitignore。

## 已知边界

- 尚未完整校验模型响应结构，部分异常响应可能直接抛错。
- 已根据本次 trace 核验测试证据，但不会自动追加测试、阻止模型声称成功或验证测试覆盖是否充分。
- 核验依赖现有 trace 结构，不检测工具之外的文件修改，也不检测运行结束后文件是否再次变化。
- 文件写入使用直接覆盖，写入中途失败可能破坏原内容，未提供自动回滚。
- capture_output 会先捕获完整输出；截断只限制回传长度，不限制捕获时的内存。
- 测试子进程没有系统级隔离；固定命令不能限制被执行代码的全部行为。
- 超时处理不保证清理测试进程另行启动的所有后代进程。
- 记录在循环返回后保存，中途崩溃或强制退出时不保证留有完整记录。
- 日志没有自动脱敏，不应包含密钥或其他敏感资料。
- 只有一道任务的一次真实修复记录，不能报告总体修复成功率。

## 官方资料

- unittest：阅读测试发现、TestCase 与断言。
  https://docs.python.org/zh-cn/3/library/unittest.html
- subprocess：阅读 run、CompletedProcess、TimeoutExpired。
  https://docs.python.org/zh-cn/3/library/subprocess.html
