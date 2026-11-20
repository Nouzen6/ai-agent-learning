import os
from pathlib import Path

from dotenv import load_dotenv

from lesson05_swe_agent import run_swe_agent
from lesson06_run_record import save_run_record


REPO_ROOT = Path(__file__).resolve().parents[1]
MAX_STEPS = 8
MAX_TOOL_CALLS = 8


def main():
    load_dotenv(REPO_ROOT / ".env")

    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()

    if not api_key:
        raise ValueError("缺少 DEEPSEEK_API_KEY，请检查本地配置")

    result = run_swe_agent(
        user_prompt=(
            "请检查 solution.py 中 average(values) 的实现。"
            "要求：非空数字列表返回平均值，空列表返回 0。"
            "先读取实现和测试，再运行测试。"
            "如果已有实现满足要求，不要为了修改而修改。"
            "如果需要修复，只能修改 solution.py，"
            "保留已有函数说明，不能修改 test_solution.py。"
            "修改后重新运行测试。"
            "最后根据实际工具结果，用中文说明检查与验证情况。"
        ),
        api_key=api_key,
        max_steps=MAX_STEPS,
        max_tool_calls=MAX_TOOL_CALLS,
    )

    print("\n执行状态：", result["status"])
    print("模型调用轮数：", result["steps"])

    verification = result["verification"]
    print("测试证据核验：", verification["status"])
    print("核验说明：", verification["reason"])

    if result["reason"] is not None:
        print("停止原因：", result["reason"])

    if result["answer"] is not None:
        print("\n模型最终回答：", result["answer"])
    try:
        record_path = save_run_record(result)
    except (OSError, TypeError, ValueError) as error:
        print("执行记录保存失败：", error)
    else:
        print("执行记录已保存：", record_path)


if __name__ == "__main__":
    main()