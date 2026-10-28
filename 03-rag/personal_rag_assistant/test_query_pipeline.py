import unittest
from unittest.mock import Mock

from query_pipeline import retrieve_for_query, retrieve_and_rerank


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
    def test_retrieves_candidates_then_reranks(self):
        embedded_chunks = [
            {
                "id": "A",
                "text": "片段 A",
                "embedding": [1.0, 0.0],
                "metadata": {"source": "notes.txt"},
            },
            {
                "id": "B",
                "text": "片段 B",
                "embedding": [0.8, 0.6],
                "metadata": {"source": "notes.txt"},
            },
            {
                "id": "C",
                "text": "片段 C",
                "embedding": [0.0, 1.0],
                "metadata": {"source": "notes.txt"},
            },
        ]
        mock_embed = Mock(return_value=[1.0, 0.0])
        mock_score = Mock(side_effect=[0.40, 0.92])

        results = retrieve_and_rerank(
            question="测试问题",
            embedded_chunks=embedded_chunks,
            embed_text=mock_embed,
            score_func=mock_score,
            candidate_k=2,
            final_k=1,
            score_threshold=None,
        )

        self.assertEqual(
            [result["id"] for result in results],
            ["B"],
        )
        self.assertEqual(results[0]["rerank_score"], 0.92)
        self.assertEqual(mock_score.call_count, 2)
        mock_embed.assert_called_once_with("测试问题")

    def test_no_candidates_skip_rerank_scoring(self):
        mock_embed = Mock(return_value=[1.0, 0.0])
        mock_score = Mock()

        results = retrieve_and_rerank(
            question="测试问题",
            embedded_chunks=[
                {
                    "id": "C",
                    "text": "片段 C",
                    "embedding": [0.0, 1.0],
                    "metadata": {"source": "notes.txt"},
                },
            ],
            embed_text=mock_embed,
            score_func=mock_score,
            candidate_k=2,
            final_k=1,
            score_threshold=0.6,
        )

        self.assertEqual(results, [])
        mock_score.assert_not_called()
        mock_embed.assert_called_once_with("测试问题")

if __name__ == "__main__":
    unittest.main()