import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from cli_learning_assistant_memory import (
    analyze_learning_record,
    extract_output_text,
    save_analysis,
    stream_answer,
)


class TestExtractOutputText(unittest.TestCase):
    def test_extract_one_text(self):
        data = {
            "output": [
                {
                    "content": [
                        {
                            "type": "output_text",
                            "text": "测试回答",
                        }
                    ]
                }
            ]
        }

        actual = extract_output_text(data)

        self.assertEqual(actual, "测试回答")

    def test_extract_multiple_texts(self):
        data = {
            "output": [
                {
                    "content": [
                        {
                            "type": "output_text",
                            "text": "第一段",
                        },
                        {
                            "type": "output_text",
                            "text": "第二段",
                        },
                    ]
                }
            ]
        }

        actual = extract_output_text(data)

        self.assertEqual(actual, "第一段第二段")

    def test_empty_output(self):
        data = {
            "output": []
        }

        actual = extract_output_text(data)

        self.assertEqual(actual, "")


class TestStreamAnswer(unittest.TestCase):
    @patch("cli_learning_assistant_memory.requests.post")
    def test_stream_answer_success(self, mock_post):
        mock_response = MagicMock()

        mock_response.raise_for_status.return_value = None
        mock_response.iter_lines.return_value = [
            "",
            "event: response.output_text.delta",
            (
                'data: {"type": "response.output_text.delta", '
                '"delta": "你好"}'
            ),
            (
                'data: {"type": "response.output_text.delta", '
                '"delta": "，Eason"}'
            ),
            'data: {"type": "response.completed"}',
        ]

        mock_post.return_value.__enter__.return_value = mock_response

        messages = [
            {
                "role": "user",
                "content": "你好",
            }
        ]

        with patch("builtins.print") as mock_print:
            actual = stream_answer(
                "fake-key",
                messages,
            )

        self.assertEqual(actual, "你好，Eason")

        mock_print.assert_any_call(
            "你好",
            end="",
            flush=True,
        )
        mock_print.assert_any_call(
            "，Eason",
            end="",
            flush=True,
        )

        mock_post.assert_called_once()

        call_args, call_kwargs = mock_post.call_args

        self.assertEqual(call_args[0], (
            "https://api.deepseek.com/responses"
        ))
        self.assertEqual(
            call_kwargs["json"]["input"],
            messages,
        )
        self.assertTrue(call_kwargs["json"]["stream"])
        self.assertTrue(call_kwargs["stream"])


class TestAnalyzeLearningRecord(unittest.TestCase):
    @patch("cli_learning_assistant_memory.requests.post")
    def test_analyze_success(self, mock_post):
        mock_response = Mock()

        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "output": [
                {
                    "content": [
                        {
                            "type": "output_text",
                            "text": (
                                '{"topic": "RAG", '
                                '"level": "beginner", '
                                '"next_step": "学习 embedding"}'
                            ),
                        }
                    ]
                }
            ]
        }

        mock_post.return_value = mock_response

        result = analyze_learning_record(
            "fake-key",
            "我正在学习 RAG",
        )

        expected = {
            "topic": "RAG",
            "level": "beginner",
            "next_step": "学习 embedding",
        }

        self.assertEqual(result, expected)
        mock_post.assert_called_once()

    @patch("cli_learning_assistant_memory.requests.post")
    def test_analyze_invalid_json(self, mock_post):
        mock_response = Mock()

        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "output": [
                {
                    "content": [
                        {
                            "type": "output_text",
                            "text": "这不是 JSON",
                        }
                    ]
                }
            ]
        }

        mock_post.return_value = mock_response

        with self.assertRaises(json.JSONDecodeError):
            analyze_learning_record(
                "fake-key",
                "我正在学习 RAG",
            )

    @patch("cli_learning_assistant_memory.requests.post")
    def test_analyze_missing_field(self, mock_post):
        mock_response = Mock()

        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "output": [
                {
                    "content": [
                        {
                            "type": "output_text",
                            "text": (
                                '{"topic": "RAG", '
                                '"level": "beginner"}'
                            ),
                        }
                    ]
                }
            ]
        }

        mock_post.return_value = mock_response

        with self.assertRaisesRegex(
            ValueError,
            "next_step",
        ):
            analyze_learning_record(
                "fake-key",
                "我正在学习 RAG",
            )

    @patch("cli_learning_assistant_memory.requests.post")
    def test_analyze_wrong_field_type(self, mock_post):
        mock_response = Mock()

        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "output": [
                {
                    "content": [
                        {
                            "type": "output_text",
                            "text": (
                                '{"topic": "RAG", '
                                '"level": "beginner", '
                                '"next_step": ["学习 embedding"]}'
                            ),
                        }
                    ]
                }
            ]
        }

        mock_post.return_value = mock_response

        with self.assertRaisesRegex(
            TypeError,
            "next_step",
        ):
            analyze_learning_record(
                "fake-key",
                "我正在学习 RAG",
            )

    @patch("cli_learning_assistant_memory.requests.post")
    def test_analyze_empty_answer(self, mock_post):
        mock_response = Mock()

        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "output": []
        }

        mock_post.return_value = mock_response

        with self.assertRaisesRegex(
            ValueError,
            "没有返回分析结果",
        ):
            analyze_learning_record(
                "fake-key",
                "我正在学习 RAG",
            )


class TestSaveAnalysis(unittest.TestCase):
    def test_save_analysis(self):
        result = {
            "topic": "RAG",
            "level": "beginner",
            "next_step": "学习 embedding",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = (
                Path(temp_dir) / "learning_analysis.json"
            )

            with patch(
                "cli_learning_assistant_memory.RESULT_FILE",
                test_file,
            ):
                save_analysis(result)

            self.assertTrue(test_file.exists())

            saved_text = test_file.read_text(
                encoding="utf-8",
            )
            saved_result = json.loads(saved_text)

            self.assertEqual(saved_result, result)


if __name__ == "__main__":
    unittest.main()