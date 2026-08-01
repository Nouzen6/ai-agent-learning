from pathlib import Path
import json
import sys

def analyze_text(text,keywords):
    result={
        "characters": len(text),
        "lines": len(text.splitlines()),
        "keywords" : {},
    }

    lower_text=text.lower()

    for keyword in keywords:
        result["keywords"][keyword]=lower_text.count(keyword.lower())

    return result

def main():
    args=sys.argv

    if len(args) < 3:
        print("Usage: python lesson_03_log_analyzer.py <file_path> <keyword1> [keyword2 ...]")
        return

    file_path=Path(args[1])
    keywords=args[2:]

    if not file_path.exists():
        print(f"File not found: {file_path}")
        return

    text=file_path.read_text(encoding="utf-8")
    result=analyze_text(text,keywords)
    result["file"]=str(file_path)

    output_path=Path("00-python-basic/practice/log_analysis_result.json")
    output_path.write_text(
        json.dumps(result,ensure_ascii=False,indent=2),
        encoding="utf-8"
    )

    print(result)
    print(f"Saved result to {output_path}")

if __name__ == "__main__":
    main()