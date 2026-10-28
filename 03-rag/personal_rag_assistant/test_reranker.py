import unittest
from unittest.mock import Mock
from copy import deepcopy
from reranker import rerank_results


class TestReranker(unittest.TestCase):

    def test_reranks_and_returns_top_two(self):
        candidates = [
            {"id": "A", "text": "片段 A", "score": 0.85},
            {"id": "B", "text": "片段 B", "score": 0.78},
            {"id": "C", "text": "片段 C", "score": 0.70},
        ]

        mock_score = Mock(side_effect=[0.40, 0.92, 0.60])

        results = rerank_results(
            question="测试问题",
            candidates=candidates,
            score_func=mock_score,
            final_k=2,
        )

        self.assertEqual(
            [result["id"] for result in results],
            ["B", "C"],
        )
        self.assertEqual(
            [result["rerank_score"] for result in results],
            [0.92, 0.60],
        )
    def test_keeps_original_candidates_unchanged(self):
        candidates = [
            {"id": "A", "text": "片段 A", "score": 0.85},
            {"id": "B", "text": "片段 B", "score": 0.78},
        ]
        original = deepcopy(candidates)
        mock_score = Mock(side_effect=[0.40, 0.92])

        results = rerank_results(
            question="测试问题",
            candidates=candidates,
            score_func=mock_score,
            final_k=2,
        )

        self.assertEqual(candidates, original)
        self.assertEqual(
            [result["score"] for result in results],
            [0.78, 0.85],
        )
    def test_empty_candidates_skip_scoring(self):
        mock_score = Mock()

        results = rerank_results(
            question="测试问题",
            candidates=[],
            score_func=mock_score,
            final_k=3,
        )

        self.assertEqual(results, [])
        mock_score.assert_not_called()

    def test_rejects_non_positive_final_k(self):
        for final_k in (0, -1):
            with self.subTest(final_k=final_k):
                mock_score = Mock()

                with self.assertRaises(ValueError):
                    rerank_results(
                        question="测试问题",
                        candidates=[{"text": "片段 A"}],
                        score_func=mock_score,
                        final_k=final_k,
                    )

                mock_score.assert_not_called()

    def test_fewer_candidates_and_correct_scoring_arguments(self):
        mock_score = Mock(return_value=0.90)

        results = rerank_results(
            question="如何处理网络异常？",
            candidates=[
                {
                    "id": "A",
                    "text": "捕获异常并返回清晰的错误信息。",
                    "score": 0.75,
                },
            ],
            score_func=mock_score,
            final_k=3,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "A")
        self.assertEqual(results[0]["rerank_score"], 0.90)

        mock_score.assert_called_once_with(
            "如何处理网络异常？",
            "捕获异常并返回清晰的错误信息。",
        )

if __name__ == "__main__":
    unittest.main()