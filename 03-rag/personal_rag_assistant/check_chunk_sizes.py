from pathlib import Path

from text_chunker import clean_text, split_text


project_dir = Path(__file__).resolve().parent
file_path = project_dir / "knowledge_base" / "llm_api_notes.txt"

text = clean_text(file_path.read_text(encoding="utf-8"))
chunks = text.split("\n\n")

for index, chunk in enumerate(chunks):
    print(f"\n=== 片段 {index}，长度 {len(chunk)} ===")
    print(chunk)