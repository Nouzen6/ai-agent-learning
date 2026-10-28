import tempfile
import unittest
from pathlib import Path
import requests
from unittest.mock import Mock, patch
from cli import run_cli
from index_storage import save_index


class TestCli(unittest.TestCase):

    def test_runs_question_and_displays_answer_and_source(self):
        chunks = [
            {
                "id": "chunk-a",
                "text": "网络请求失败时，可以捕获 ConnectionError。",
                "embedding": [1.0, 0.0],
                "metadata": {
                    "source": "llm_api_notes.txt",
                    "chunk_index": 0,
                },
            }
        ]

        mock_embed_text = Mock(return_value=[1.0, 0.0])
        mock_llm_call = Mock(
            return_value="可以捕获 ConnectionError。"
        )
        mock_input = Mock(
            side_effect=[
                "如何处理网络请求失败？",
                "exit",
            ]
        )
        output_lines = []

        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index.json"
            save_index(chunks, index_path)

            run_cli(
                index_path=index_path,
                embed_text=mock_embed_text,
                llm_call=mock_llm_call,
                input_func=mock_input,
                output_func=output_lines.append,
            )

        self.assertIn(
            "AI：可以捕获 ConnectionError。",
            output_lines,
        )
        self.assertIn(
            "提供给模型的资料：",
            output_lines,
        )
        self.assertIn(
            "[资料 1] llm_api_notes.txt，片段 0",
            output_lines,
        )
        mock_llm_call.assert_called_once()

    def test_empty_question_is_rejected(self):
        mock_input = Mock(
            side_effect=[
                "   ",
                "exit",
            ]
        )
        output_lines = []

        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index.json"
            save_index(
    [
        {
            "id": "test-chunk",
            "text": "测试资料",
            "embedding": [1.0, 0.0],
            "metadata": {
                "source": "test.txt",
                "chunk_index": 0,
            },
        }
    ],
            index_path,
)

            run_cli(
                index_path=index_path,
                embed_text=Mock(),
                llm_call=Mock(),
                input_func=mock_input,
                output_func=output_lines.append,
            )

        self.assertIn("请输入问题。", output_lines)

    @patch("cli.answer_question")
    def test_continues_after_timeout(self, mock_answer):
        mock_answer.side_effect = [
            requests.exceptions.Timeout("模拟超时"),
            {"answer": "第二次问答成功。", "sources": []},
        ]
        mock_input = Mock(
            side_effect=["第一个问题", "第二个问题", "exit"]
        )
        output_lines = []

        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index.json"
            save_index(
    [
        {
            "id": "test-chunk",
            "text": "测试资料",
            "embedding": [1.0, 0.0],
            "metadata": {
                "source": "test.txt",
                "chunk_index": 0,
            },
        }
    ],
            index_path,
)

            run_cli(
                index_path=index_path,
                embed_text=Mock(),
                llm_call=Mock(),
                input_func=mock_input,
                output_func=output_lines.append,
            )

        self.assertIn("请求超时，请稍后重新提问。", output_lines)
        self.assertIn("AI：第二次问答成功。", output_lines)
        self.assertIn("已退出。", output_lines)
        self.assertEqual(mock_answer.call_count, 2)

    @patch("cli.answer_question")
    def test_continues_after_connection_and_http_errors(
        self, mock_answer
    ):
        mock_answer.side_effect = [
            requests.exceptions.ConnectionError("模拟连接失败"),
            requests.exceptions.HTTPError("模拟 HTTP 错误"),
            {"answer": "恢复成功。", "sources": []},
        ]
        mock_input = Mock(
            side_effect=["问题一", "问题二", "问题三", "exit"]
        )
        output_lines = []

        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index.json"
            save_index(
    [
        {
            "id": "test-chunk",
            "text": "测试资料",
            "embedding": [1.0, 0.0],
            "metadata": {
                "source": "test.txt",
                "chunk_index": 0,
            },
        }
    ],
            index_path,
)

            run_cli(
                index_path=index_path,
                embed_text=Mock(),
                llm_call=Mock(),
                input_func=mock_input,
                output_func=output_lines.append,
            )

        self.assertIn(
            "无法连接 API，请检查网络后重新提问。", output_lines
        )
        self.assertIn(
            "API 返回 HTTP 错误，请检查配置或服务状态。", output_lines
        )
        self.assertIn("AI：恢复成功。", output_lines)
        self.assertIn("已退出。", output_lines)
        self.assertEqual(mock_answer.call_count, 3)

    def test_missing_index_shows_setup_instruction(self):
        mock_input = Mock()
        output_lines = []

        with tempfile.TemporaryDirectory() as temp_dir:
            missing_index = Path(temp_dir) / "missing_index.json"

            run_cli(
                index_path=missing_index,
                embed_text=Mock(),
                llm_call=Mock(),
                input_func=mock_input,
                output_func=output_lines.append,
            )

        self.assertTrue(
            any("索引文件不存在" in line for line in output_lines)
        )
        self.assertTrue(
            any("python index_documents.py" in line
                for line in output_lines)
        )
        mock_input.assert_not_called()

    def test_empty_index_shows_setup_instruction(self):
        mock_input = Mock()
        mock_embed = Mock()
        output_lines = []

        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index.json"
            save_index([], index_path)

            run_cli(
                index_path=index_path,
                embed_text=mock_embed,
                llm_call=Mock(),
                input_func=mock_input,
                output_func=output_lines.append,
            )

        self.assertTrue(
            any("没有可用的文档片段" in line for line in output_lines)
        )
        mock_input.assert_not_called()
        mock_embed.assert_not_called()

if __name__ == "__main__":
    unittest.main()