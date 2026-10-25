import unittest

from vector_search import search_chunks


class TestVectorSearch(unittest.TestCase):

    def test_returns_top_k_chunks_by_score(self):
        embedded_chunks = [
            {
                "id": "chunk-a",
                "text": "内容 A",
                "embedding": [1.0, 0.0],
                "metadata": {"source": "a.md"},
            },
            {
                "id": "chunk-b",
                "text": "内容 B",
                "embedding": [0.0, 1.0],
                "metadata": {"source": "b.md"},
            },
            {
                "id": "chunk-c",
                "text": "内容 C",
                "embedding": [0.8, 0.2],
                "metadata": {"source": "c.md"},
            },
        ]

        results = search_chunks(
            query_embedding=[1.0, 0.0],
            embedded_chunks=embedded_chunks,
            k=2,
        )

        self.assertEqual(
            [result["id"] for result in results],
            ["chunk-a", "chunk-c"],
        )
        self.assertEqual(results[0]["text"], "内容 A")
        self.assertNotIn("embedding", results[0])

    def test_filters_results_below_threshold(self):
        embedded_chunks = [
            {
                "id": "chunk-a",
                "text": "内容 A",
                "embedding": [1.0, 0.0],
                "metadata": {"source": "a.md"},
            },
            {
                "id": "chunk-b",
                "text": "内容 B",
                "embedding": [0.0, 1.0],
                "metadata": {"source": "b.md"},
            },
        ]

        results = search_chunks(
            query_embedding=[1.0, 0.0],
            embedded_chunks=embedded_chunks,
            k=3,
            score_threshold=0.8,
        )

        self.assertEqual(
            [result["id"] for result in results],
            ["chunk-a"],
        )

    def test_returns_empty_list_when_no_chunk_passes_threshold(self):
        embedded_chunks = [
            {
                "id": "chunk-a",
                "text": "内容 A",
                "embedding": [0.0, 1.0],
                "metadata": {"source": "a.md"},
            }
        ]

        results = search_chunks(
            query_embedding=[1.0, 0.0],
            embedded_chunks=embedded_chunks,
            score_threshold=0.8,
        )

        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()