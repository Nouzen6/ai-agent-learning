from pathlib import Path


PRACTICE_ROOT = (
    Path(__file__).resolve().parent / "practice"
).resolve()

READABLE_FILES = {
    "solution.py",
    "test_solution.py",
}

MAX_READ_CHARS = 8000


def resolve_read_path(path):
    if not isinstance(path, str) or not path.strip():
        raise ValueError("path 必须是非空字符串")

    requested_path = Path(path)

    if requested_path.drive or requested_path.root:
        raise ValueError("只允许相对于练习目录的路径")

    target_path = (PRACTICE_ROOT / requested_path).resolve()

    try:
        relative_path = target_path.relative_to(PRACTICE_ROOT)
    except ValueError:
        raise ValueError("目标路径超出练习目录") from None

    if relative_path.as_posix() not in READABLE_FILES:
        raise ValueError("该文件不在允许读取的列表中")

    return target_path


def read_file(path):
    target_path = resolve_read_path(path)

    with target_path.open("r", encoding="utf-8") as file:
        content = file.read(MAX_READ_CHARS + 1)

    truncated = len(content) > MAX_READ_CHARS

    return {
        "path": target_path.relative_to(PRACTICE_ROOT).as_posix(),
        "content": content[:MAX_READ_CHARS],
        "truncated": truncated,
    }


def main():
    example_paths = [
        "solution.py",
        "../../04-agent/lesson05_agent_state.py",
        str(Path(__file__).resolve()),
    ]

    for path in example_paths:
        print(f"\n请求路径：{path}")

        try:
            result = read_file(path)
            print(result)
        except (ValueError, OSError, UnicodeError) as error:
            print(f"读取失败：{error}")


if __name__ == "__main__":
    main()