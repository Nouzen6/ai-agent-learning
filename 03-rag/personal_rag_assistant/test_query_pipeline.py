import unittest
from unittest.mock import Mock

from query_pipeline import retrieve_for_query


class TestQueryPipeline(unittest.TestCase):

    def test_embeds_question_and_returns_retrieved_chunks(self):
        embedded_chunks = [
            {
                "id": "chunk-a",
                "text": "网络请求失败时，可以捕获 ConnectionError。",
                "embedding": [1.0, 0.0],
                "metadata": {
                    "source": "llm_api_notes.txt",
                },
            },
            {
                "id": "chunk-b",
                "text": "SSE 可以逐行处理流式响应。",
                "embedding": [0.0, 1.0],
                "metadata": {
                    "source": "llm_api_notes.txt",
                },
            },
        ]

        mock_embed_text = Mock(return_value=[1.0, 0.0])

        results = retrieve_for_query(
            question="如何处理网络请求失败？",
            embedded_chunks=embedded_chunks,
            embed_text=mock_embed_text,
            k=1,
        )

        self.assertEqual(
            [result["id"] for result in results],
            ["chunk-a"],
        )
        mock_embed_text.assert_called_once_with(
            "如何处理网络请求失败？"
        )

    def test_rejects_empty_question_before_embedding(self):
        mock_embed_text = Mock()

        with self.assertRaises(ValueError):
            retrieve_for_query(
                question="   ",
                embedded_chunks=[],
                embed_text=mock_embed_text,
            )

        mock_embed_text.assert_not_called()


if __name__ == "__main__":
    unittest.main()