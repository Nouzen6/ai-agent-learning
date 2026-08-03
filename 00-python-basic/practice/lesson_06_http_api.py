from pathlib import Path
import json
import sys

import requests


def fetch_github_user(username):
    url = f"https://api.github.com/users/{username}"

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ai-agent-learning",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.RequestException as error:
        print(f"Error: request failed: {error}")
        return None

    if response.status_code != 200:
        print(f"Error: GitHub API returned status code {response.status_code}")

        try:
            error_data = response.json()
            print(f"Message: {error_data.get('message')}")
        except ValueError:
            print(response.text[:200])

        return None

    return response.json()

def save_json(data, output_path):
    output_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main():
    args = sys.argv

    if len(args) != 2:
        print("Usage: python lesson_06_http_api.py <github_username>")
        return

    username = args[1]

    user_data = fetch_github_user(username)

    if user_data is None:
        return

    result = {
        "login": user_data.get("login"),
        "name": user_data.get("name"),
        "public_repos": user_data.get("public_repos"),
        "followers": user_data.get("followers"),
        "following": user_data.get("following"),
        "html_url": user_data.get("html_url"),
        "created_at": user_data.get("created_at"),
    }

    output_path = Path("00-python-basic/practice/github_user_result.json")
    save_json(result, output_path)

    print(result)
    print(f"Saved result to {output_path}")


if __name__ == "__main__":
    main()