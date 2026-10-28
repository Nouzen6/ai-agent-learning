import os
from pathlib import Path

from dotenv import load_dotenv


def load_llm_config():
    """读取并检查 LLM 配置。"""
    repo_root = Path(__file__).resolve().parents[2]
    load_dotenv(repo_root / ".env")

    env_names = {
        "api_url": "LLM_API_URL",
        "model": "LLM_MODEL",
        "api_key": "DEEPSEEK_API_KEY",
    }

    config = {}

    for parameter, env_name in env_names.items():
        value = os.getenv(env_name, "").strip()

        if not value:
            raise ValueError(f"缺少环境变量：{env_name}")

        config[parameter] = value

    return config

def load_embedding_config():
    """读取并检查 Embedding API 配置。"""
    repo_root = Path(__file__).resolve().parents[2]
    load_dotenv(repo_root / ".env")

    env_names = {
        "api_url": "EMBEDDING_API_URL",
        "model": "EMBEDDING_MODEL",
        "api_key": "EMBEDDING_API_KEY",
    }

    config = {}

    for parameter, env_name in env_names.items():
        value = os.getenv(env_name, "").strip()

        if not value:
            raise ValueError(f"缺少环境变量：{env_name}")

        config[parameter] = value

    return config

def load_rerank_config():
    """读取并检查 Rerank API 配置。"""
    repo_root = Path(__file__).resolve().parents[2]
    load_dotenv(repo_root / ".env")

    env_names = {
        "api_url": "RERANK_API_URL",
        "model": "RERANK_MODEL",
        "api_key": "RERANK_API_KEY",
    }

    config = {}

    for parameter, env_name in env_names.items():
        value = os.getenv(env_name, "").strip()

        if not value:
            raise ValueError(f"缺少环境变量：{env_name}")

        config[parameter] = value

    return config