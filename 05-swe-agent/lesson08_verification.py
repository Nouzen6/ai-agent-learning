def verify_trace(trace):
    verification = {
        "status": "not_verified",
        "reason": "本次运行没有测试通过的证据",
    }

    for record in trace:
        event = record["event"]
        tool = record.get("tool")

        if event not in ("tool_result", "tool_error"):
            continue

        if tool == "write_file":
            verification = {
                "status": "not_verified",
                "reason": "发生过写入尝试，需要重新测试",
            }

        elif tool == "run_tests":
            verification = {
                "status": "not_verified",
                "reason": "最近一次测试未能确认通过",
            }

            if event == "tool_error":
                continue

            feedback = record["result"]

            if feedback.get("ok") is not True:
                continue

            test_result = feedback["result"]
            exit_code = test_result.get("exit_code")

            if (
                type(exit_code) is int
                and exit_code == 0
                and test_result.get("timed_out") is False
            ):
                verification = {
                    "status": "passed",
                    "reason": (
                        "本次记录中最近一次测试通过，"
                        "之后没有新的写入记录"
                    ),
                }

    return verification