import tempfile
import unittest
from pathlib import Path

from index_storage import load_index, save_index


class TestIndexStorage(unittest.TestCase):

    def test_saves_and_loads_index(self):
        chunks = [
            {
                "id": "notes.md::chunk-0000",
                "text": "Python 支持异常处理。",
                "embedding": [0.1, 0.2, 0.3],
                "metadata": {
                    "source": "notes.md",
                    "chunk_index": 0,
                },
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "data" / "index.json"

            save_index(chunks, index_path)
            loaded_chunks = load_index(index_path)

        self.assertEqual(loaded_chunks, chunks)

    def test_raises_when_index_does_not_exist(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "missing.json"

            with self.assertRaises(FileNotFoundError):
                load_index(index_path)

    def test_rejects_index_that_is_not_a_list(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "index.json"
            index_path.write_text(
                '{"invalid": true}',
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                load_index(index_path)


if __name__ == "__main__":
    unittest.main()