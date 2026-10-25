import tempfile
import unittest
from pathlib import Path

from document_loader import load_documents


class TestDocumentLoader(unittest.TestCase):

    def test_loads_markdown_and_text_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            knowledge_base_dir = Path(temp_dir)
            (knowledge_base_dir / "guide.md").write_text(
                "# 学习指南",
                encoding="utf-8",
            )
            (knowledge_base_dir / "notes.txt").write_text(
                "这是学习笔记。",
                encoding="utf-8",
            )

            documents = load_documents(knowledge_base_dir)

            self.assertEqual(len(documents), 2)

            sources = {
                document["metadata"]["source"]
                for document in documents
            }

            self.assertEqual(sources, {"guide.md", "notes.txt"})

    def test_ignores_unsupported_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            knowledge_base_dir = Path(temp_dir)
            (knowledge_base_dir / "guide.md").write_text(
                "支持的文档",
                encoding="utf-8",
            )
            (knowledge_base_dir / "image.png").write_bytes(
                b"not a real image"
            )

            documents = load_documents(knowledge_base_dir)

            self.assertEqual(len(documents), 1)
            self.assertEqual(
                documents[0]["metadata"]["source"],
                "guide.md",
            )
    def test_raises_file_not_found_when_directory_does_not_exist(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_dir = Path(temp_dir) / "missing"

            with self.assertRaises(FileNotFoundError):
                load_documents(missing_dir)
    def test_returns_empty_list_for_empty_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            documents = load_documents(Path(temp_dir))

            self.assertEqual(documents, [])

if __name__ == "__main__":
    unittest.main()