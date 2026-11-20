import contextlib
import copy
import io
import json
import unittest
from unittest.mock import Mock, patch

import lesson05_swe_agent as swe


def tool_message(call_id, name, arguments):
    return {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": call_id,
                "type": "function",
                "function": {
                    "name": name,
                    "arguments": json.dumps(
                        arguments,
                        ensure_ascii=False,
                    ),
                },
            },
        ],
    }


class TestSWEAgent(unittest.TestCase):
    def test_mock_repair_roundtrip(self):
        proposed_code = (
            "def average(values):\n"
            "    if not values:\n"
            "        return 0\n"
            "    return sum(values) / len(values)\n"
        )

        failed_test = {
            "exit_code": 1,
            "stdout": "",
            "stderr": "ZeroDivisionError: division by zero",
            "timed_out": False,
            "truncated": False,
        }

        passed_test = {
            "exit_code": 0,
            "stdout": "",
            "stderr": "Ran 3 tests\nOK\n",
            "timed_out": False,
            "truncated": False,
        }

        replies = iter([
            tool_message(
                "read_1",
                "read_file",
                {"path": "solution.py"},
            ),
            tool_message(
                "read_2",
                "read_file",
                {"path": "test_solution.py"},
            ),
            tool_message("test_1", "run_tests", {}),
            tool_message(
                "write_1",
                "write_file",
                {
                    "path": "solution.py",
                    "content": proposed_code,
                },
            ),
            tool_message("test_2", "run_tests", {}),
            {
                "role": "assistant",
                "content": "模拟修复流程结束。",
            },
        ])

        requests = []

        def fake_model(messages, api_key, tool_choice, api_tools=None):
            requests.append({
                "messages": copy.deepcopy(messages),
                "api_tools": copy.deepcopy(api_tools),
            })
            return next(replies)

        read_results = [
            {
                "path": "solution.py",
                "content": (
                    "def average(values):\n"
                    "    return sum(values) / len(values)\n"
                ),
                "truncated": False,
            },
            {
                "path": "test_solution.py",
                "content": "# Mock 测试文件内容\n",
                "truncated": False,
            },
        ]

        with (
            patch.object(
                swe.agent_state,
                "call_chat_model",
                side_effect=fake_model,
            ) as model,
            patch.object(
                swe,
                "read_file",
                side_effect=read_results,
            ) as reader,
            patch.object(
                swe,
                "write_file",
                return_value={
                    "path": "solution.py",
                    "status": "written",
                    "written_chars": len(proposed_code),
                },
            ) as writer,
            patch.object(
                swe,
                "run_tests",
                side_effect=[failed_test, passed_test],
            ) as tester,
            patch(
                "requests.sessions.Session.request",
                side_effect=AssertionError("离线测试禁止 HTTP 请求"),
            ),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            result = swe.run_swe_agent(
                user_prompt="修复空列表平均值问题。",
                api_key="mock-key",
            )

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["steps"], 6)
        self.assertEqual(model.call_count, 6)
        self.assertEqual(reader.call_count, 2)
        self.assertEqual(tester.call_count, 2)
        writer.assert_called_once_with(
            path="solution.py",
            content=proposed_code,
        )

        self.assertEqual(
            requests[0]["api_tools"],
            swe.SWE_API_TOOLS,
        )

        tool_results = [
            message
            for message in requests[-1]["messages"]
            if message["role"] == "tool"
        ]

        self.assertEqual(
            [message["tool_call_id"] for message in tool_results],
            ["read_1", "read_2", "test_1", "write_1", "test_2"],
        )

        first_test = json.loads(tool_results[2]["content"])
        last_test = json.loads(tool_results[4]["content"])

        self.assertTrue(first_test["ok"])
        self.assertEqual(first_test["result"], failed_test)
        self.assertTrue(last_test["ok"])
        self.assertEqual(last_test["result"], passed_test)

        self.assertEqual(
            [
                record["tool"]
                for record in result["trace"]
                if record["event"] == "tool_result"
            ],
            [
                "read_file",
                "read_file",
                "run_tests",
                "write_file",
                "run_tests",
            ],
        )

    def test_syntax_error_becomes_feedback(self):
        tool = Mock(side_effect=SyntaxError("缺少冒号"))

        result = swe.call_swe_tool(
            tool,
            path="solution.py",
            content="无效代码",
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["type"], "SyntaxError")
        self.assertIn("缺少冒号", result["error"]["message"])


if __name__ == "__main__":
    unittest.main()