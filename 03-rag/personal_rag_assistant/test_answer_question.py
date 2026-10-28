import unittest
from unittest.mock import Mock

from answer_question import (
    INSUFFICIENT_ANSWER,
    answer_question,
)


class TestAnswerQuestion(unittest.TestCase):

    def test_retrieves_context_and_calls_llm(self):
        embedded_chunks = [
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

        result = answer_question(
            question="如何处理网络请求失败？",
            embedded_chunks=embedded_chunks,
            embed_text=mock_embed_text,
            llm_call=mock_llm_call,
            k=1,
        )

        self.assertEqual(
            result["answer"],
            "可以捕获 ConnectionError。",
        )
        self.assertEqual(
            result["sources"],
            [
                {
                    "citation": "[资料 1]",
                    "source": "llm_api_notes.txt",
                    "chunk_index": 0,
                }
            ],
        )

        mock_llm_call.assert_called_once()
        prompt = mock_llm_call.call_args.args[0]
        self.assertIn(
            "在对应句子后标注资料编号",
            prompt,
        )
        self.assertIn(
            "[资料 1]\n"
            "来源：llm_api_notes.txt\n"
            "片段编号：0\n"
            "内容：\n"
            "网络请求失败时，可以捕获 ConnectionError。",
            prompt,
        )
        self.assertIn("如何处理网络请求失败？", prompt)
        self.assertIn("ConnectionError", prompt)
        self.assertIn("llm_api_notes.txt", prompt)

    def test_does_not_call_llm_when_no_result_passes_threshold(self):
        embedded_chunks = [
            {
                "id": "chunk-a",
                "text": "与问题无关的内容。",
                "embedding": [0.0, 1.0],
                "metadata": {
                    "source": "unrelated.txt",
                    "chunk_index": 0,
                },
            }
        ]

        mock_embed_text = Mock(return_value=[1.0, 0.0])
        mock_llm_call = Mock()

        result = answer_question(
            question="如何处理网络请求失败？",
            embedded_chunks=embedded_chunks,
            embed_text=mock_embed_text,
            llm_call=mock_llm_call,
            score_threshold=0.8,
        )

        self.assertEqual(
            result,
            {
                "answer": INSUFFICIENT_ANSWER,
                "sources": [],
            },
        )
        mock_llm_call.assert_not_called()