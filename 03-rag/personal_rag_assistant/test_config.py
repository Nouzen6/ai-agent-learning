import unittest
from unittest.mock import patch

from config import load_llm_config
from config import load_embedding_config, load_llm_config
from functools import partial
class TestConfig(unittest.TestCase):

    @patch("config.load_dotenv")
    def test_loads_complete_config(self, mock_load_dotenv):
        fake_env = {
            "LLM_API_URL": "https://example.com/responses",
            "LLM_MODEL": "test-model",
            "DEEPSEEK_API_KEY": "fake-key",
        }

        with patch.dict("os.environ", fake_env, clear=True):
            config = load_llm_config()

        self.assertEqual(config, {
            "api_url": "https://example.com/responses",
            "model": "test-model",
            "api_key": "fake-key",
        })

    @patch("config.load_dotenv")
    def test_missing_api_key_raises_error(self, mock_load_dotenv):
        fake_env = {
            "LLM_API_URL": "https://example.com/responses",
            "LLM_MODEL": "test-model",
        }

        with patch.dict("os.environ", fake_env, clear=True):
            with self.assertRaisesRegex(
                ValueError, "缺少环境变量：DEEPSEEK_API_KEY"
            ):
                load_llm_config()

    @patch("config.load_dotenv")
    def test_loads_complete_embedding_config(self, mock_load_dotenv):
        fake_env = {
            "EMBEDDING_API_URL": "https://example.com/v1/embeddings",
            "EMBEDDING_MODEL": "test-embedding-model",
            "EMBEDDING_API_KEY": "fake-embedding-key",
        }

        with patch.dict("os.environ", fake_env, clear=True):
            config = load_embedding_config()

        self.assertEqual(config, {
            "api_url": "https://example.com/v1/embeddings",
            "model": "test-embedding-model",
            "api_key": "fake-embedding-key",
        })

    @patch("config.load_dotenv")
    def test_missing_embedding_api_key_raises_error(self, mock_load_dotenv):
        fake_env = {
            "EMBEDDING_API_URL": "https://example.com/v1/embeddings",
            "EMBEDDING_MODEL": "test-embedding-model",
        }

        with patch.dict("os.environ", fake_env, clear=True):
            with self.assertRaisesRegex(
                ValueError,
                "缺少环境变量：EMBEDDING_API_KEY",
            ):
                load_embedding_config()


if __name__ == "__main__":
    unittest.main()