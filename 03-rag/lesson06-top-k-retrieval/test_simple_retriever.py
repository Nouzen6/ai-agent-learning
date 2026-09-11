import unittest

from simple_retriever import cosine_similarity, retrieve_top_k


class TestSimpleRetriever(unittest.TestCase):
    def setUp(self):
        self.documents = [
            {
                "id": "chunk-a",
                "vector": [1, 0],
                "text": "requests 网络请求失败时，可以捕获 ConnectionError。",
                "metadata": {
                    "source": "02-llm-api/README.md",
                    "chunk_id": 1,
                },
            },
            {
                "id": "chunk-b",
                "vector": [0.8, 0.6],
                "text": "JSON 文件可以使用 json.dump() 保存。",
                "metadata": {
                    "source": "00-python-basic/README.md",
                    "chunk_id": 2,
                },
            },
            {
                "id": "chunk-c",
                "vector": [0, 1],
                "text": "虚拟环境可以使用 venv 创建。",
                "metadata": {
                    "source": "00-python-basic/README.md",
                    "chunk_id": 3,
                },
            },
        ]

        self.query_vector = [1, 0]

    def test_cosine_similarity_same_direction(self):
        score = cosine_similarity([1, 0], [1, 0])

        self.assertAlmostEqual(score, 1.0)

    def test_cosine_similarity_vertical_direction(self):
        score = cosine_similarity([1, 0], [0, 1])

        self.assertAlmostEqual(score, 0.0)

    def test_retrieve_top_k_returns_most_similar_documents(self):
        results = retrieve_top_k(
            self.query_vector,
            self.documents,
            k=2,
        )

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], "chunk-a")
        self.assertEqual(results[1]["id"], "chunk-b")
        self.assertAlmostEqual(results[0]["score"], 1.0)
        self.assertAlmostEqual(results[1]["score"], 0.8)

    def test_retrieve_top_k_filters_by_score_threshold(self):
        results = retrieve_top_k(
            self.query_vector,
            self.documents,
            k=3,
            score_threshold=0.7,
        )

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], "chunk-a")
        self.assertEqual(results[1]["id"], "chunk-b")

    def test_retrieve_top_k_returns_empty_list_when_no_score_passes_threshold(self):
        results = retrieve_top_k(
            self.query_vector,
            self.documents,
            k=3,
            score_threshold=1.1,
        )

        self.assertEqual(results, [])

    def test_retrieve_top_k_raises_error_when_k_is_not_positive(self):
        with self.assertRaises(ValueError):
            retrieve_top_k(
                self.query_vector,
                self.documents,
                k=0,
            )

    def test_retrieve_top_k_returns_all_documents_when_k_is_larger_than_documents(self):
        results = retrieve_top_k(
            self.query_vector,
            self.documents,
            k=10,
        )

        self.assertEqual(len(results), 3)


if __name__ == "__main__":
    unittest.main()