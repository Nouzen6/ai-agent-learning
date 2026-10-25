import unittest
from unittest.mock import Mock, patch

from embedding_client import embed_text
from functools import partial
from config import load_embedding_config

class TestEmbeddingClient(unittest.TestCase):

    @patch("embedding_client.requests.post")
    def test_embed_text_returns_embedding(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "embedding": [0.1, 0.2, 0.3],
                }
            ]
        }
        mock_post.return_value = mock_response

        embedding = embed_text(
            text="Python 异常处理",
            api_url="https://example.com/v1/embeddings",
            model="test-embedding-model",
            api_key="test-key",
        )

        self.assertEqual(
            embedding,
            [0.1, 0.2, 0.3],
        )

        mock_response.raise_for_status.assert_called_once_with()
        mock_response.json.assert_called_once_with()

        mock_post.assert_called_once_with(
            "https://example.com/v1/embeddings",
            headers={
                "Authorization": "Bearer test-key",
                "Content-Type": "application/json",
            },
            json={
                "model": "test-embedding-model",
                "input": "Python 异常处理",
            },
            timeout=30,
        )

    def test_rejects_empty_text_before_request(self):
        with patch("embedding_client.requests.post") as mock_post:
            with self.assertRaises(ValueError):
                embed_text(
                    text="   ",
                    api_url="https://example.com/v1/embeddings",
                    model="test-embedding-model",
                    api_key="test-key",
                )

            mock_post.assert_not_called()

    @patch("embedding_client.requests.post")
    def test_rejects_invalid_response_structure(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        with self.assertRaises(ValueError):
            embed_text(
                text="Python 异常处理",
                api_url="https://example.com/v1/embeddings",
                model="test-embedding-model",
                api_key="test-key",
            )

    @patch("embedding_client.requests.post")
    def test_rejects_empty_embedding(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                "embedding": [],
                }
            ]
       }
        mock_post.return_value = mock_response

        with self.assertRaises(ValueError):
            embed_text(
                text="Python 异常处理",
                api_url="https://example.com/v1/embeddings",
                model="test-embedding-model",
                api_key="test-key",
            )

    @patch("embedding_client.requests.post")
    def test_rejects_non_numeric_embedding(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
        "data": [
                {
                "embedding": [0.1, "wrong", 0.3],
                }
            ]
        }
        mock_post.return_value = mock_response

        with self.assertRaises(ValueError):
            embed_text(
                text="Python 异常处理",
                api_url="https://example.com/v1/embeddings",
                model="test-embedding-model",
                api_key="test-key",
            )
    @patch("embedding_client.requests.post")
    def test_bound_embedding_accepts_only_text(self, mock_post):
        mock_response = Mock()
        mock_post.return_value = mock_response
        mock_response.json.return_value = {
            "data": [
                {"embedding": [0.1, 0.2, 0.3]}
            ]
        }

        config = {
            "api_url": "https://example.com/v1/embeddings",
            "model": "test-embedding-model",
            "api_key": "fake-key",
        }

        embed = partial(
            embed_text,
            api_url=config["api_url"],
            model=config["model"],
            api_key=config["api_key"],
        )

        vector = embed("网络请求失败时，可以捕获 ConnectionError。")

        self.assertEqual(vector, [0.1, 0.2, 0.3])
        mock_post.assert_called_once_with(
            config["api_url"],
            headers={
                "Authorization": "Bearer fake-key",
                "Content-Type": "application/json",
            },
            json={
                "model": config["model"],
                "input": "网络请求失败时，可以捕获 ConnectionError。",
            },
            timeout=30,
        )



if __name__ == "__main__":
    unittest.main()