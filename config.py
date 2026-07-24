"""
配置文件 - AI试卷分析Agent
支持从 .env 文件或 Streamlit Cloud Secrets 读取配置
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 尝试从 Streamlit Secrets 读取（云端部署时）
def _get_secret(key: str, default: str = "") -> str:
    """优先从 Streamlit Secrets 读取，其次从环境变量"""
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.environ.get(key, default)


# ============ AWS Bedrock 配置 ============
AWS_CONFIG = {
    "region": _get_secret("AWS_DEFAULT_REGION", "us-west-2"),
    "model_id": _get_secret("BEDROCK_MODEL_ID", "anthropic.claude-sonnet-4-6"),
    "temperature": 0.7,
    "max_tokens": 4096,
}

# 设置 AWS 环境变量（供 boto3 使用）
_aws_keys = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN", "AWS_DEFAULT_REGION"]
for key in _aws_keys:
    val = _get_secret(key)
    if val:
        os.environ[key] = val

# ============ 应用配置 ============
APP_CONFIG = {
    "title": "AI试卷分析Agent",
    "page_icon": "📝",
    "max_upload_size_mb": 20,
    "supported_formats": [".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"],
}

# ============ 搜索配置 ============
SEARCH_CONFIG = {
    "max_results": 5,
    "region": "cn-zh",
}
