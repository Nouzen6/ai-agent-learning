import unittest
from unittest.mock import Mock, patch

from streaming_function import stream_answer


class TestStreamAnswer(unittest.TestCase):

    @patch("streaming_function.requests.post")
    def test_stream_answer_success(self, mock_post):
        mock_response = Mock()

        mock_response.raise_for_status.return_value = None

        mock_response.iter_lines.return_value = [
            "",
            "event: response.created",
            'data: {"type":"response.created"}',
            'data: {"type":"response.reasoning_text.delta","delta":"内部内容"}',
            'data: {"type":"response.output_text.delta","delta":"你好"}',
            'data: {"type":"response.output_text.delta","delta":"，世界"}',
            'data: {"type":"response.output_text.done","text":"你好，世界"}',
        ]

        mock_post.return_value.__enter__.return_value = mock_response

        actual = stream_answer("fake-key", "测试问题")
        expected = "你好，世界"

        self.assertEqual(actual, expected)
        mock_post.assert_called_once()

    @patch("streaming_function.requests.post")
    def test_stream_answer_http_error(self, mock_post):
        mock_response = Mock()

        mock_response.raise_for_status.side_effect = RuntimeError(
            "模拟 HTTP 错误"
        )

        mock_post.return_value.__enter__.return_value = mock_response

        with self.assertRaises(RuntimeError):
            stream_answer("fake-key", "测试问题")


if __name__ == "__main__":
    unittest.main()