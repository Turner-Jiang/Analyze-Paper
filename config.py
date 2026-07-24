"""
配置文件 - AI试卷分析Agent
在这里配置你的AWS Bedrock参数
"""

import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# ============ AWS Bedrock 配置 ============
AWS_CONFIG = {
    "region": os.environ.get("AWS_DEFAULT_REGION", "us-west-2"),
    "model_id": os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"),
    "temperature": 0.7,
    "max_tokens": 4096,
}

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
