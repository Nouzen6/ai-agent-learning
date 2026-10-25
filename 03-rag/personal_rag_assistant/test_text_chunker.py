import unittest

from text_chunker import clean_text, chunk_documents, split_text


class TestCleanText(unittest.TestCase):

    def test_normalizes_line_endings_and_trailing_spaces(self):
        raw_text = "第一行  \r\n第二行\r第三行\n"

        cleaned_text = clean_text(raw_text)

        self.assertEqual(
            cleaned_text,
            "第一行\n第二行\n第三行",
        )

    def test_preserves_paragraph_boundary(self):
        raw_text = "\n\n第一段\n\n\n\n第二段\n\n"

        cleaned_text = clean_text(raw_text)

        self.assertEqual(
            cleaned_text,
            "第一段\n\n第二段",
        )
    def test_splits_text_into_fixed_size_chunks(self):
        chunks = split_text("abcdefghij", 4)

        self.assertEqual(
            chunks,
            ["abcd", "efgh", "ij"],
        )


    def test_returns_empty_list_for_empty_text(self):
        self.assertEqual(split_text("", 4), [])


    def test_returns_one_chunk_when_text_is_shorter_than_chunk_size(self):
         self.assertEqual(
            split_text("abc", 4),
            ["abc"],
        )


    def test_rejects_non_positive_chunk_size(self):
        with self.assertRaises(ValueError):
            split_text("abc", 0)

    def test_splits_text_with_overlap(self):
        chunks = split_text("abcdefghij", 4, overlap=1)

        self.assertEqual(
        chunks,
        ["abcd", "defg", "ghij", ],
    )


    def test_rejects_negative_overlap(self):
        with self.assertRaises(ValueError):
            split_text("abcdefghij", 4, overlap=-1)


    def test_rejects_overlap_equal_to_chunk_size(self):
        with self.assertRaises(ValueError):
            split_text("abcdefghij", 4, overlap=4)

    def test_chunk_documents_adds_ids_and_metadata(self):
        documents = [
            {
            "text": "abcdefghij",
            "metadata": {
                "source": "notes.md",
                "file_type": ".md",
                },
            }
        ]
        chunks = chunk_documents(
            documents,
            chunk_size=4,
            overlap=1,
        )

        self.assertEqual(
            [chunk["text"] for chunk in chunks],
            ["abcd", "defg", "ghij"],
        )
        self.assertEqual(
            [chunk["id"] for chunk in chunks],
            [
            "notes.md::chunk-0000",
            "notes.md::chunk-0001",
            "notes.md::chunk-0002",
            ],
    )
        self.assertEqual(
            chunks[0]["metadata"],
        {
            "source": "notes.md",
            "file_type": ".md",
            "chunk_index": 0,
        },
    )
        self.assertNotIn("chunk_index", documents[0]["metadata"])






if __name__ == "__main__":
    unittest.main()