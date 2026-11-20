import subprocess
import sys

from lesson02_read_file import PRACTICE_ROOT


TIMEOUT_SECONDS = 10
MAX_OUTPUT_CHARS = 4000


def _to_text(output):
    if output is None:
        return ""

    if isinstance(output, bytes):
        return output.decode("utf-8", errors="replace")

    return output


def _limit_output(output):
    return {
        "text": output[:MAX_OUTPUT_CHARS],
        "truncated": len(output) > MAX_OUTPUT_CHARS,
    }


def run_tests():
    if not PRACTICE_ROOT.is_dir():
        raise FileNotFoundError("练习目录不存在")

    command = [
        sys.executable,
        "-B",
        "-X",
        "utf8",
        "-m",
        "unittest",
        "-v",
        "test_solution",
    ]

    try:
        completed = subprocess.run(
            command,
            cwd=PRACTICE_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        stdout = _limit_output(_to_text(error.stdout))
        stderr = _limit_output(_to_text(error.stderr))

        return {
            "exit_code": None,
            "stdout": stdout["text"],
            "stderr": stderr["text"],
            "timed_out": True,
            "truncated": (
                stdout["truncated"] or stderr["truncated"]
            ),
        }

    stdout = _limit_output(completed.stdout)
    stderr = _limit_output(completed.stderr)

    return {
        "exit_code": completed.returncode,
        "stdout": stdout["text"],
        "stderr": stderr["text"],
        "timed_out": False,
        "truncated": stdout["truncated"] or stderr["truncated"],
    }


def main():
    result = run_tests()
    print(result)


if __name__ == "__main__":
    main()