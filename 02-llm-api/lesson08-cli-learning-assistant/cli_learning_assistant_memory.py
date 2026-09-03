import json
import os

import requests
from dotenv import load_dotenv
from pathlib import Path

API_URL = "https://api.deepseek.com/responses"
MODEL = "deepseek-v4-flash"
INSTRUCTION = (
    "你是一名中文 AI 学习助手，"
    "请结合之前的对话，从基础开始、通俗地回答问题。"
)
RESULT_FILE = Path(__file__).with_name("learning_analysis.json")
ANALYZE_INSTRUCTION = (
    "你是一个学习分析助手。"
    "请只返回合法 JSON，不要返回 Markdown 或解释文字。"
)

def save_analysis(result):
    with RESULT_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            result,
            file,
            ensure_ascii=False,
            indent=2
        )

def extract_output_text(data):
    texts = []

    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                texts.append(content.get("text", ""))

    return "".join(texts)

def stream_answer(api_key, messages):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    body = {
        "model": MODEL,
        "instructions": INSTRUCTION,
        "input": messages,
        "stream": True,
    }

    chunks = []

    with requests.post(
        API_URL,
        headers=headers,
        json=body,
        stream=True,
        timeout=60,
    ) as response:
        response.raise_for_status()
        response.encoding = "utf-8"

        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue

            if not line.startswith("data: "):
                continue

            json_text = line.removeprefix("data: ")
            data = json.loads(json_text)

            if data.get("type") != "response.output_text.delta":
                continue

            delta = data.get("delta", "")

            print(delta, end="", flush=True)
            chunks.append(delta)

    print()

    return "".join(chunks)

def analyze_learning_record(api_key, learning_record):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": MODEL,
        "instructions": ANALYZE_INSTRUCTION,
        "input": (
            "请分析下面的学习记录，并返回 JSON 对象。\n"
            "必须包含 topic、level、next_step 三个字符串字段。\n"
            f"学习记录：{learning_record}"
        ),
        "stream": False,
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=body,
        timeout=60,
    )

    response.raise_for_status()

    data = response.json()
    answer_text = extract_output_text(data)

    if not answer_text:
        raise ValueError("API 没有返回分析结果")

    result = json.loads(answer_text)

    required_fields = [
        "topic",
        "level",
        "next_step",
    ]

    for field in required_fields:
        if field not in result:
            raise ValueError(f"分析结果缺少字段：{field}")

        if not isinstance(result[field], str):
            raise TypeError(f"分析结果字段 {field} 必须是字符串")

    return result



def main():
    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        raise ValueError("请在环境变量中设置 DEEPSEEK_API_KEY")

    messages = []

    print("AI 学习助手已启动，输入 exit 退出。")

    while True:
        prompt = input("\n你：").strip()

        if prompt.lower() == "exit":
            print("已退出 AI 学习助手。")
            break

        if prompt.startswith("/analyze "):
            learning_record = prompt.removeprefix("/analyze ").strip()

            if not learning_record:
                print("请在 /analyze 后输入学习记录。")
                continue

            try:
                result = analyze_learning_record(
                    api_key,
                    learning_record,
                )
                save_analysis(result)
            except requests.exceptions.Timeout:
                print("分析请求超时，请稍后重试。")
                continue
            except requests.exceptions.ConnectionError:
                print("无法连接 API，请检查网络。")
                continue
            except requests.exceptions.RequestException as error:
                print(f"分析请求失败：{error}")
                continue
            except json.JSONDecodeError:
                print("模型返回的不是合法 JSON。")
                continue
            except (ValueError, TypeError) as error:
                print(f"分析结果无效：{error}")
                continue
            except OSError as error:
                print(f"分析结果保存失败：{error}")
                continue

            print("学习分析结果：")
            print("当前主题：", result["topic"])
            print("当前水平：", result["level"])
            print("下一步：", result["next_step"])
            continue


        if not prompt:
            print("请输入问题。")
            continue

        user_message = {
            "role": "user",
            "content": prompt,
        }

        messages.append(user_message)

        try:
            print("AI：", end="")
            answer = stream_answer(api_key, messages)
        except requests.exceptions.Timeout:
            print("\n请求超时，请稍后重试。")
            messages.pop()
            continue
        except requests.exceptions.ConnectionError:
            print("\n无法连接 API，请检查网络。")
            messages.pop()
            continue
        except requests.exceptions.RequestException as error:
            print(f"\nAPI 请求失败：{error}")
            messages.pop()
            continue
        except json.JSONDecodeError:
            print("\n服务器返回的数据格式异常。")
            messages.pop()
            continue

        messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )


if __name__ == "__main__":
    main()