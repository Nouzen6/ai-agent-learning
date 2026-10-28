import unittest
from unittest.mock import Mock, patch

import requests

from rerank_client import score_text


class TestRerankClient(unittest.TestCase):

    def call_score(self, question="测试问题", text="片段正文"):
        return score_text(
            question=question,
            text=text,
            api_url="https://example.com/v1/rerank",
            model="test-reranker",
            api_key="test-key",
        )

    @patch("rerank_client.requests.post")
    def test_returns_score_and_sends_expected_request(self, mock_post):
        response = Mock()
        response.json.return_value = {
            "results": [{"index": 0, "relevance_score": 0.92}]
        }
        mock_post.return_value = response

        score = self.call_score()

        self.assertEqual(score, 0.92)
        response.raise_for_status.assert_called_once_with()
        mock_post.assert_called_once_with(
            "https://example.com/v1/rerank",
            headers={
                "Authorization": "Bearer test-key",
                "Content-Type": "application/json",
            },
            json={
                "model": "test-reranker",
                "query": "测试问题",
                "documents": ["片段正文"],
                "top_n": 1,
                "return_documents": False,
            },
            timeout=30,
        )

    @patch("rerank_client.requests.post")
    def test_rejects_empty_input_before_request(self, mock_post):
        for question, text in [
            ("   ", "片段正文"),
            ("测试问题", "   "),
        ]:
            with self.subTest(question=question, text=text):
                with self.assertRaises(ValueError):
                    self.call_score(question=question, text=text)

        mock_post.assert_not_called()

    @patch("rerank_client.requests.post")
    def test_rejects_invalid_response(self, mock_post):
        invalid_responses = [
            {},
            {"results": []},
            {"results": [{"index": 1, "relevance_score": 0.92}]},
            {"results": [{"index": 0, "relevance_score": "wrong"}]},
            {"results": [{"index": 0, "relevance_score": True}]},
            {"results": [{"index": 0, "relevance_score": float("nan")}]},
        ]

        for data in invalid_responses:
            with self.subTest(data=data):
                response = Mock()
                response.json.return_value = data
                mock_post.return_value = response

                with self.assertRaises(ValueError):
                    self.call_score()

    @patch("rerank_client.requests.post")
    def test_propagates_timeout(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout("测试超时")

        with self.assertRaises(requests.exceptions.Timeout):
            self.call_score()

    @patch("rerank_client.requests.post")
    def test_propagates_http_error(self, mock_post):
        response = Mock()
        response.raise_for_status.side_effect = (
            requests.exceptions.HTTPError("测试 HTTP 错误")
        )
        mock_post.return_value = response

        with self.assertRaises(requests.exceptions.HTTPError):
            self.call_score()

        response.json.assert_not_called()


if __name__ == "__main__":
    unittest.main()