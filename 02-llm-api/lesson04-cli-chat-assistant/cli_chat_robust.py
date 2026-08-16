import os 
import requests
from dotenv import load_dotenv

API_URL = "https://api.deepseek.com/responses"
MODEL = "deepseek-v4-flash"
INSTRUCTIONS = "你是一名 AI 学习助手，请使用中文并从基础开始讲解。"

def extract_output_text(data):
    texts=[]
    for item in data.get("output",[]):
        for content in item.get("content",[]):
            if content.get("type")=="output_text":
                texts.append(content.get("text",""))

    return "".join(texts)

def call_llm(message,api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    body={
        "model":MODEL,
        "instructions": INSTRUCTIONS,
        "input":message
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=body,
        timeout=60
    )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        detail = response.text[:500]
        raise RuntimeError(
            f"API 请求失败，状态码：{response.status_code}，详情：{detail}"
        ) from error

    data=response.json()
    answer=extract_output_text(data)

    if not answer:
        raise ValueError("API响应中没有找到文本回答")

    return answer

def main():
    load_dotenv()

    api_key=os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        raise ValueError("请在环境变量中设置 DEEPSEEK_API_KEY")

    messages=[]

    print("AI 学习助手已启动，输入 exit 退出。")

    while True:
        question=input("你：").strip()

        if question.lower()=="exit":
            print("退出 AI 学习助手。")
            break

        if not question:
            print("请输入问题。")
            continue


        messages.append({"role": "user",
                       "content": question})
        
        try:
            answer = call_llm(messages, api_key)
        except requests.exceptions.Timeout:
            print("请求超时，请检查网络后重试。")
            messages.pop()
            continue
        except requests.exceptions.ConnectionError:
            print("无法连接 API 服务，请检查网络连接。")
            messages.pop()
            continue
        except requests.exceptions.RequestException as error:
            print(f"网络请求失败：{error}")
            messages.pop()
            continue
        except RuntimeError as error:
            print(f"服务请求失败：{error}")
            messages.pop()
            continue
        except ValueError as error:
            print(f"返回数据处理失败：{error}")
            messages.pop()
            continue

        messages.append({
            "role": "assistant",
            "content": answer
        })

        print("AI：", answer)


if __name__=="__main__":
    main()









        