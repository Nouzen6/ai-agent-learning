import ast

from lesson02_read_file import PRACTICE_ROOT, resolve_read_path


WRITABLE_FILES = {
    "solution.py",
}

MAX_WRITE_CHARS = 8000


def write_file(path, content):
    target_path = resolve_read_path(path)
    relative_path = target_path.relative_to(PRACTICE_ROOT).as_posix()

    if relative_path not in WRITABLE_FILES:
        raise ValueError("该文件不在允许修改的列表中")

    if not isinstance(content, str) or not content.strip():
        raise ValueError("content 必须是非空字符串")

    if len(content) > MAX_WRITE_CHARS:
        raise ValueError(
            f"写入内容不能超过 {MAX_WRITE_CHARS} 个字符"
        )

    ast.parse(content, filename=relative_path)

    if not target_path.is_file():
        raise FileNotFoundError("待修改的文件不存在或不是普通文件")

    with target_path.open("w", encoding="utf-8") as file:
        written_chars = file.write(content)

    return {
        "path": relative_path,
        "status": "written",
        "written_chars": written_chars,
    }


def main():
    new_content = (
        "def average(values):\n"
        '    """计算数字列表的平均值。"""\n'
        "    return sum(values) / len(values)\n"
    )

    result = write_file("solution.py", new_content)
    print(result)


if __name__ == "__main__":
    main()