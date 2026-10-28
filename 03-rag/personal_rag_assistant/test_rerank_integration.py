import unittest
from unittest.mock import Mock, patch

from answer_question import answer_question
from cli import run_cli
from config import load_rerank_config


def make_chunks():
    return [
        {
            "id": "A",
            "text": "片段 A 正文",
            "embedding": [1.0, 0.0],
            "metadata": {"source": "a.txt", "chunk_index": 0},
        },
        {
            "id": "B",
            "text": "片段 B 正文",
            "embedding": [0.8, 0.6],
            "metadata": {"source": "b.txt", "chunk_index": 0},
        },
    ]


class TestRerankIntegration(unittest.TestCase):

    @patch("config.load_dotenv")
    def test_loads_rerank_config(self, mock_load_dotenv):
        fake_env = {
            "RERANK_API_URL": "https://example.com/v1/rerank",
            "RERANK_MODEL": "test-model",
            "RERANK_API_KEY": "fake-key",
        }

        with patch.dict("os.environ", fake_env, clear=True):
            config = load_rerank_config()

        self.assertEqual(config, {
            "api_url": "https://example.com/v1/rerank",
            "model": "test-model",
            "api_key": "fake-key",
        })

    @patch("config.load_dotenv")
    def test_rejects_missing_rerank_key(self, mock_load_dotenv):
        fake_env = {
            "RERANK_API_URL": "https://example.com/v1/rerank",
            "RERANK_MODEL": "test-model",
        }

        with patch.dict("os.environ", fake_env, clear=True):
            with self.assertRaisesRegex(
                ValueError, "缺少环境变量：RERANK_API_KEY"
            ):
                load_rerank_config()

    def test_only_final_results_enter_prompt(self):
        mock_llm = Mock(return_value="测试回答")
        mock_score = Mock(side_effect=[0.40, 0.92])

        result = answer_question(
            question="测试问题",
            embedded_chunks=make_chunks(),
            embed_text=Mock(return_value=[1.0, 0.0]),
            llm_call=mock_llm,
            score_func=mock_score,
            candidate_k=2,
            k=1,
            score_threshold=0.6,
        )

        self.assertEqual(
            result["sources"],
            [
                {
                    "citation": "[资料 1]",
                    "source": "b.txt",
                    "chunk_index": 0,
                }
            ],
        )
        self.assertEqual(mock_score.call_count, 2)
        mock_llm.assert_called_once()

        prompt = mock_llm.call_args.args[0]
        self.assertIn("片段 B 正文", prompt)
        self.assertNotIn("片段 A 正文", prompt)

    @patch("cli.load_index")
    def test_cli_continues_after_scoring_error(self, mock_load_index):
        mock_load_index.return_value = make_chunks()
        mock_llm = Mock(return_value="恢复成功。")
        mock_score = Mock(
            side_effect=[
                ValueError("评分格式错误"),
                0.40,
                0.92,
            ]
        )
        output_lines = []

        run_cli(
            index_path="unused.json",
            embed_text=Mock(return_value=[1.0, 0.0]),
            llm_call=mock_llm,
            input_func=Mock(
                side_effect=["第一个问题", "第二个问题", "exit"]
            ),
            output_func=output_lines.append,
            score_func=mock_score,
            candidate_k=2,
        )

        self.assertIn("处理失败：评分格式错误", output_lines)
        self.assertIn("AI：恢复成功。", output_lines)
        self.assertIn("已退出。", output_lines)
        self.assertEqual(mock_score.call_count, 3)
        mock_llm.assert_called_once()


if __name__ == "__main__":
    unittest.main()