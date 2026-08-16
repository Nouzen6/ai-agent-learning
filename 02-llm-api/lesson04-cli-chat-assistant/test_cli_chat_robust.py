import unittest
from unittest.mock import patch,Mock
import requests

from cli_chat_robust import call_llm,main,extract_output_text

class TestExtractOutputText(unittest.TestCase):
    def test_extract_one_text(self):
        data = {
            "output": [
                {
                    "content": [
                        {
                            "type": "output_text",
                            "text": "你好，Eason"
                        }
                    ]
                }
            ]
        }

        actual = extract_output_text(data)
        expected = "你好，Eason"

        self.assertEqual(actual, expected)

    def test_extract_multiple_texts(self):
        data = {
            "output": [
                {
                    "content": [
                        {
                            "type": "output_text",
                            "text": "你好"
                        },
                        {
                            "type": "output_text",
                            "text": "，Eason"
                        }
                    ]
                }
            ]
        }

        actual = extract_output_text(data)
        expected = "你好，Eason"

        self.assertEqual(actual, expected)

    def test_empty_output(self):
        data = {
            "output": []
        }

        actual = extract_output_text(data)
        expected = ""

        self.assertEqual(actual, expected)

class TestCallLlm(unittest.TestCase):
    @patch("cli_chat_robust.requests.post")
    def test_success(self,mock_post):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "output": [
                {
                    "content": [
                        {
                            "type": "output_text",
                            "text": "这是测试回答"
                        }
                    ]
                }
            ]
        }

        mock_post.return_value = mock_response

        messages = [
            {
                "role": "user",
                "content": "这是测试问题"
            }
        ]

        actual = call_llm(messages, "fake-key")
        expected = "这是测试回答"

        self.assertEqual(actual, expected)
        mock_post.assert_called_once()

    @patch("cli_chat_robust.requests.post")
    def test_timeout(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout()

        with self.assertRaises(requests.exceptions.Timeout):
            call_llm([], "fake-key")

    @patch("cli_chat_robust.requests.post")
    def test_connection_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.ConnectionError()

        with self.assertRaises(requests.exceptions.ConnectionError):
            call_llm([], "fake-key")

    @patch("cli_chat_robust.requests.post")
    def test_http_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "请求过于频繁"
        mock_response.raise_for_status.side_effect = (
            requests.exceptions.HTTPError()
        )

        mock_post.return_value = mock_response

        with self.assertRaises(RuntimeError) as context:
            call_llm([], "fake-key")

        error_message = str(context.exception)

        self.assertIn("429", error_message)
        self.assertIn("请求过于频繁", error_message)

    @patch("cli_chat_robust.requests.post")
    def test_empty_answer(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "output": []
        }

        mock_post.return_value = mock_response

        with self.assertRaises(ValueError) as context:
            call_llm([], "fake-key")

        error_message = str(context.exception)

        self.assertIn("没有找到文本回答", error_message)


if __name__ == "__main__":
    unittest.main()