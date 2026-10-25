import unittest
from unittest.mock import Mock

from embedding_pipeline import add_embeddings


class TestEmbeddingPipeline(unittest.TestCase):

    def test_adds_embedding_to_each_chunk(self):
        chunks = [
            {
                "id": "notes.md::chunk-0000",
                "text": "第一段文本",
                "metadata": {
                    "source": "notes.md",
                    "chunk_index": 0,
                },
            },
            {
                "id": "notes.md::chunk-0001",
                "text": "第二段文本",
                "metadata": {
                    "source": "notes.md",
                    "chunk_index": 1,
                },
            },
        ]

        mock_embed_text = Mock(
            side_effect=[
                [0.1, 0.2, 0.3],
                [0.4, 0.5, 0.6],
            ]
        )

        embedded_chunks = add_embeddings(
            chunks,
            mock_embed_text,
        )

        self.assertEqual(
            embedded_chunks[0]["embedding"],
            [0.1, 0.2, 0.3],
        )
        self.assertEqual(
            embedded_chunks[1]["embedding"],
            [0.4, 0.5, 0.6],
        )
        self.assertEqual(
            embedded_chunks[0]["metadata"]["source"],
            "notes.md",
        )
        self.assertNotIn("embedding", chunks[0])
        self.assertEqual(mock_embed_text.call_count, 2)

    def test_rejects_empty_embedding(self):
        chunks = [
            {
                "id": "notes.md::chunk-0000",
                "text": "第一段文本",
                "metadata": {},
            }
        ]

        mock_embed_text = Mock(return_value=[])

        with self.assertRaises(ValueError):
            add_embeddings(chunks, mock_embed_text)


if __name__ == "__main__":
    unittest.main()