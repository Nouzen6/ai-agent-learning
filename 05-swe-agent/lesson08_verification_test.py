import contextlib
import io
import unittest
from unittest.mock import patch

import lesson05_swe_agent as swe
from lesson08_verification import verify_trace


def test_record(exit_code, timed_out=False):
    return {
        "event": "tool_result",
        "tool": "run_tests",
        "result": {
            "ok": True,
            "result": {
                "exit_code": exit_code,
                "timed_out": timed_out,
            },
        },
    }


class TestVerification(unittest.TestCase):
    def test_evidence_order(self):
        write = {
            "event": "tool_result",
            "tool": "write_file",
            "result": {"ok": True},
        }

        failed_write = {
            "event": "tool_result",
            "tool": "write_file",
            "result": {
                "ok": False,
                "error": {"type": "OSError"},
            },
        }

        final_answer = {
            "event": "final_answer",
        }

        cases = [
            ("没有测试", [], "not_verified"),
            ("测试通过", [test_record(0)], "passed"),
            ("测试失败", [test_record(1)], "not_verified"),
            (
                "通过后再写入",
                [test_record(0), write],
                "not_verified",
            ),
            (
                "写入后测试通过",
                [write, test_record(0)],
                "passed",
            ),
            (
                "通过后再次测试失败",
                [test_record(0), test_record(1)],
                "not_verified",
            ),
            (
                "通过后测试超时",
                [test_record(0), test_record(None, True)],
                "not_verified",
            ),
            (
                "通过后写入报错",
                [test_record(0), failed_write],
                "not_verified",
            ),
            (
                "只有最终回答",
                [final_answer],
                "not_verified",
            ),
        ]

        for name, trace, expected in cases:
            with self.subTest(name=name):
                result = verify_trace(trace)
                self.assertEqual(result["status"], expected)

    def test_completed_without_tests_is_not_verified(self):
        final_message = {
            "role": "assistant",
            "content": "我已经修好了。",
        }

        with (
            patch.object(
                swe.agent_state,
                "call_chat_model",
                return_value=final_message,
            ) as model,
            patch(
                "requests.sessions.Session.request",
                side_effect=AssertionError("离线测试禁止 HTTP 请求"),
            ),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            result = swe.run_swe_agent(
                user_prompt="离线核验测试",
                api_key="mock-key",
            )

        model.assert_called_once()
        self.assertEqual(result["status"], "completed")
        self.assertEqual(
            result["verification"]["status"],
            "not_verified",
        )


if __name__ == "__main__":
    unittest.main()