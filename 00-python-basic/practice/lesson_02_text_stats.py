from pathlib import Path
import json

text_path=Path("learning-log.md")

text=text_path.read_text(encoding="utf-8")

result={
    "file" : str(text_path),
    "characters" : len(text),
    "lines" : len(text.splitlines()),
    "python_count" : text.lower().count("python"),
    "agent_count" : text.lower().count("agent")
}

output_path=Path("00-python-basic/practice/text_stats_result.json")
output_path.write_text(
    json.dumps(result,ensure_ascii=False,indent=2),
    encoding="utf-8"
)

print(result)
print(f"Saved result to {output_path}")