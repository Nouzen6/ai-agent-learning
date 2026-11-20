import contextlib
import io
import unittest
from unittest.mock import patch

import lesson05_swe_agent as swe
from lesson05_mock_test import tool_message


class TestToolBudget(unittest.TestCase):
    def test_stops_before_second_tool_in_same_response(self):
        response = tool_message(
            "read_1",
            "read_file",
            {"path": "solution.py"},
        )

        response["tool_calls"].extend(
            tool_message(
                "test_1",
                "run_tests",
                {},
            )["tool_calls"]
        )

        with (
            patch.object(
                swe.agent_state,
                "call_chat_model",
                return_value=response,
            ) as model,
            patch.object(
                swe,
                "read_file",
                return_value={"content": "模拟文件内容"},
            ) as reader,
            patch.object(swe, "run_tests") as tester,
            patch(
                "requests.sessions.Session.request",
                side_effect=AssertionError("离线测试禁止 HTTP 请求"),
            ),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            result = swe.run_swe_agent(
                user_prompt="离线预算测试",
                api_key="mock-key",
                max_tool_calls=1,
            )

        self.assertEqual(result["status"], "tool_limit")
        self.assertEqual(result["steps"], 1)
        self.assertIsNone(result["answer"])

        model.assert_called_once()
        reader.assert_called_once_with(path="solution.py")
        tester.assert_not_called()

        self.assertEqual(
            result["trace"][-1],
            {
                "step": 1,
                "event": "tool_limit",
                "used": 1,
                "limit": 1,
            },
        )

    def test_can_finish_after_using_exact_budget(self):
        replies = [
            tool_message(
                "read_1",
                "read_file",
                {"path": "solution.py"},
            ),
            {
                "role": "assistant",
                "content": "模拟任务结束。",
            },
        ]

        with (
            patch.object(
                swe.agent_state,
                "call_chat_model",
                side_effect=replies,
            ) as model,
            patch.object(
                swe,
                "read_file",
                return_value={"content": "模拟文件内容"},
            ) as reader,
            patch(
                "requests.sessions.Session.request",
                side_effect=AssertionError("离线测试禁止 HTTP 请求"),
            ),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            result = swe.run_swe_agent(
                user_prompt="离线边界测试",
                api_key="mock-key",
                max_tool_calls=1,
            )

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["steps"], 2)
        self.assertEqual(model.call_count, 2)
        reader.assert_called_once_with(path="solution.py")

        events = [
            record["event"]
            for record in result["trace"]
        ]

        self.assertEqual(events.count("tool_attempt"), 1)
        self.assertNotIn("tool_limit", events)


if __name__ == "__main__":
    unittest.main()