from pathlib import Path
import json
import sys

def read_text_file(file_path):
    try:
        return file_path.read_text(encoding='utf-8')
    except FileNotFoundError:
        print(f"Error:file not found:{file_path}")
        return None
    except UnicodeDecodeError:
        print(f"Error: Could not decode the file {file_path}. Please ensure it is a valid UTF-8 encoded text file.")
        return None


def count_entries(text):
    lines = text.splitlines()
    count = 0

    for line in lines:
        if line.startswith("## ") and line[3:4].isdigit():
            count += 1

    return count

def count_keywords(text, keywords):
    lower_text = text.lower()
    result = {}

    for keyword in keywords:
        result[keyword] = lower_text.count(keyword.lower())

    return result

def build_summary(file_path, text, keywords):
    return {
        "file": str(file_path),
        "characters": len(text),
        "lines": len(text.splitlines()),
        "entry_count": count_entries(text),
        "keywords": count_keywords(text, keywords),
    }

def save_json(data,output_path):
    try:
        output_path.write_text(json.dumps(data,ensure_ascii=False, indent=2),encoding='utf-8')
        return True
    except OSError as error:
        print(f"Error : failed to write JSON: {error}")
        return False

def save_markdown(summary, output_path):
    lines = [
        "# Learning Summary",
        "",
        f"- File: {summary['file']}",
        f"- Characters: {summary['characters']}",
        f"- Lines: {summary['lines']}",
        f"- Entry Count: {summary['entry_count']}",
        "",
        "## Keywords",
        "",
    ]

    for keyword, count in summary["keywords"].items():
        lines.append(f"- {keyword}: {count}")

    content = "\n".join(lines)

    try:
        output_path.write_text(content, encoding="utf-8")
        return True
    except OSError as error:
        print(f"Error: failed to write Markdown: {error}")
        return False

    
def main():
    args=sys.argv

    if len(args)<3:
         print("Usage: python learning_log_analyzer.py <file_path> <keyword1> [keyword2 ...]")
         return

    file_path = Path(args[1])
    keywords = args[2:]

    text = read_text_file(file_path)

    if text is None:
        return

    summary = build_summary(file_path, text, keywords)

    output_path = Path("00-python-basic/project/learning_summary.json")

    if save_json(summary, output_path):
        print(summary)
        print(f"Summary saved to {output_path}")

    markdown_output_path = Path("00-python-basic/project/learning_summary.md")

    if save_markdown(summary, markdown_output_path):
        print(f"Markdown summary saved to {markdown_output_path}")
if __name__ == "__main__":
    main()