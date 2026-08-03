from pathlib import Path
import json

import requests


def fetch_json(url):
    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException as error:
        print(f"Error: request failed: {error}")
        return None

    if response.status_code != 200:
        print(f"Error: API returned status code {response.status_code}")
        return None

    return response.json()


def save_json(data, output_path):
    output_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main():
    url = "https://httpbin.org/json"

    data = fetch_json(url)

    if data is None:
        return

    result = {
        "source_url": url,
        "title": data["slideshow"]["title"],
        "author": data["slideshow"]["author"],
        "slide_count": len(data["slideshow"]["slides"]),
    }

    output_path = Path("00-python-basic/practice/httpbin_result.json")
    save_json(result, output_path)

    print(result)
    print(f"Saved result to {output_path}")


if __name__ == "__main__":
    main()