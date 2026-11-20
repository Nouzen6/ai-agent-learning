import contextlib
import io
import subprocess
import unittest
from unittest.mock import patch

from requests.exceptions import Timeout

import lesson05_swe_agent as swe
import lesson04_run_tests as test_runner
from lesson05_mock_test import tool_message


class TestAcceptance(unittest.TestCase):
    def setUp(self):
        network_guard = patch(
            "requests.sessions.Session.request",
            side_effect=AssertionError("离线测试禁止 HTTP 请求"),
        )
        network_guard.start()
        self.addCleanup(network_guard.stop)

    def test_file_boundaries_reject_before_open(self):
        with patch(
            "pathlib.Path.open",
            side_effect=AssertionError("不应打开文件"),
        ) as file_open:
            with self.assertRaises(ValueError):
                swe.read_file(
                    "../../04-agent/lesson05_agent_state.py"
                )

            with self.assertRaises(ValueError):
                swe.write_file(
                    path="test_solution.py",
                    content="x = 1\n",
                )

            file_open.assert_not_called()

    def test_test_timeout_returns_limited_output(self):
        output_size = test_runner.MAX_OUTPUT_CHARS + 1
        timeout = subprocess.TimeoutExpired(
            cmd=["mock-python"],
            timeout=test_runner.TIMEOUT_SECONDS,
            output=b"x" * output_size,
            stderr=None,
        )

        with (
            patch(
                "pathlib.Path.is_dir",
                return_value=True,
            ),
            patch.object(
                test_runner.subprocess,
                "run",
                side_effect=timeout,
            ) as process,
        ):
            result = test_runner.run_tests()

        self.assertIsNone(result["exit_code"])
        self.assertTrue(result["timed_out"])
        self.assertTrue(result["truncated"])
        self.assertEqual(
            result["stdout"],
            "x" * test_runner.MAX_OUTPUT_CHARS,
        )
        self.assertEqual(result["stderr"], "")
        process.assert_called_once()

    def test_model_timeout_stops_before_tools(self):
        with (
            patch.object(
                swe.agent_state,
                "call_chat_model",
                side_effect=Timeout("模拟模型请求超时"),
            ) as model,
            patch.object(swe, "read_file") as reader,
            patch.object(swe, "write_file") as writer,
            patch.object(swe, "run_tests") as tester,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            result = swe.run_swe_agent(
                user_prompt="离线超时测试",
                api_key="mock-key",
            )

        self.assertEqual(result["status"], "api_error")
        self.assertEqual(result["steps"], 1)
        self.assertIsNone(result["answer"])
        self.assertIn("模拟模型请求超时", result["reason"])
        model.assert_called_once()
        reader.assert_not_called()
        writer.assert_not_called()
        tester.assert_not_called()

        self.assertEqual(
            [
                record["event"]
                for record in result["trace"]
            ],
            ["model_request", "api_error"],
        )

    def test_model_round_limit_stops_loop(self):
        replies = [
            tool_message(
                f"read_{number}",
                "read_file",
                {"path": "solution.py"},
            )
            for number in (1, 2)
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
                return_value={"content": "模拟代码"},
            ) as reader,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            result = swe.run_swe_agent(
                user_prompt="离线轮数上限测试",
                api_key="mock-key",
                max_steps=2,
                max_tool_calls=8,
            )

        self.assertEqual(result["status"], "step_limit")
        self.assertEqual(result["steps"], 2)
        self.assertIsNone(result["answer"])
        self.assertEqual(model.call_count, 2)
        self.assertEqual(reader.call_count, 2)

        events = [
            record["event"]
            for record in result["trace"]
        ]

        self.assertNotIn("final_answer", events)
        self.assertNotIn("tool_limit", events)


if __name__ == "__main__":
    unittest.main()