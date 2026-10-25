import unittest
from unittest.mock import MagicMock, patch
import requests
from llm_client import call_llm
from functools import partial

class TestLlmClient(unittest.TestCase):

    @patch("llm_client.requests.post")
    def test_joins_streamed_text(self, mock_post):
        mock_response = MagicMock()
        mock_post.return_value.__enter__.return_value = mock_response

        mock_response.iter_lines.return_value = [
            "",
            'data: {"type": "response.output_text.delta", '
            '"delta": "可以捕获"}',
            'data: {"type": "response.output_text.delta", '
            '"delta": " ConnectionError。"}',
            'data: {"type": "response.completed"}',
        ]

        answer = call_llm(
            prompt="网络请求失败怎么办？",
            api_url="https://example.com/responses",
            model="test-model",
            api_key="fake-key",
        )

        self.assertEqual(answer, "可以捕获 ConnectionError。")
        mock_post.assert_called_once()
        mock_response.raise_for_status.assert_called_once()
        mock_response.iter_lines.assert_called_once_with(
            decode_unicode=True
        )
    @patch("llm_client.requests.post")
    def test_empty_answer_raises_error(self, mock_post):
        mock_response = MagicMock()
        mock_post.return_value.__enter__.return_value = mock_response

        mock_response.iter_lines.return_value = [
            'data: {"type": "response.completed"}',
        ]

        with self.assertRaisesRegex(ValueError, "没有返回有效答案"):
            call_llm(
                prompt="什么是 RAG？",
                api_url="https://example.com/responses",
                model="test-model",
                api_key="fake-key",
            )

    @patch("llm_client.requests.post")
    def test_timeout_is_propagated(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout(
            "模拟请求超时"
        )

        with self.assertRaises(requests.exceptions.Timeout):
            call_llm(
                prompt="什么是 RAG？",
                api_url="https://example.com/responses",
                model="test-model",
                api_key="fake-key",
            )

    @patch("llm_client.requests.post")
    def test_bound_llm_accepts_only_prompt(self, mock_post):
        mock_response = MagicMock()
        mock_post.return_value.__enter__.return_value = mock_response
        mock_response.iter_lines.return_value = [
            'data: {"type": "response.output_text.delta", '
            '"delta": "RAG 是检索增强生成。"}',
        ]

        llm_call = partial(
            call_llm,
            api_url="https://example.com/responses",
            model="test-model",
            api_key="fake-key",
        )

        answer = llm_call("什么是 RAG？")

        self.assertEqual(answer, "RAG 是检索增强生成。")
        mock_post.assert_called_once_with(
            "https://example.com/responses",
            headers={
                "Authorization": "Bearer fake-key",
                "Content-Type": "application/json",
            },
            json={
                "model": "test-model",
                "input": "什么是 RAG？",
                "stream": True,
            },
            stream=True,
            timeout=60,
        )
if __name__ == "__main__":
    unittest.main()