from pathlib import Path
import json
import sys

def read_file(file_path):
    try:
        return file_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: file not found: {file_path}")
    except UnicodeDecodeError:
        print(f"Error: cannot decode file as UTF-8: {file_path}")


def analyze_text(text, keywords):
    lower_text = text.lower()

    keyword_counts = {}

    for keyword in keywords:
        keyword_counts[keyword] = lower_text.count(keyword.lower())

    return {
        "characters": len(text),
        "lines": len(text.splitlines()),
        "keywords": keyword_counts,
    }


def save_json(data, output_path):
    try:
        output_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return True
    except OSError as error:
        print(f"Error: failed to write JSON file: {error}")
        return False


def main():
    args = sys.argv

    if len(args) < 3:
        print("Usage: python lesson_04_error_handling.py <file_path> <keyword1> [keyword2 ...]")
        return

    file_path = Path(args[1])
    keywords = args[2:]

    text = read_file(file_path)

    if text is None:
        return

    result = analyze_text(text, keywords)
    result["file"] = str(file_path)

    output_path = Path("00-python-basic/practice/error_handling_result.json")

    if save_json(result, output_path):
        print(result)
        print(f"Saved result to {output_path}")


if __name__ == "__main__":
    main()