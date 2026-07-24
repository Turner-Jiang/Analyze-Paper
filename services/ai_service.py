"""
AI服务模块 - 封装AWS Bedrock调用
"""
from __future__ import annotations

import json
import boto3
from config import AWS_CONFIG


def get_client():
    """获取Bedrock Runtime客户端"""
    return boto3.client(
        "bedrock-runtime",
        region_name=AWS_CONFIG["region"],
    )


def chat(system_prompt: str, user_prompt: str, temperature: float | None = None) -> str:
    """
    调用Bedrock模型进行对话
    :param system_prompt: 系统提示词
    :param user_prompt: 用户提示词
    :param temperature: 温度参数，None则使用默认值
    :return: AI回复文本
    """
    client = get_client()

    messages = [
        {"role": "user", "content": [{"text": user_prompt}]},
    ]

    system = [{"text": system_prompt}]

    response = client.converse(
        modelId=AWS_CONFIG["model_id"],
        messages=messages,
        system=system,
        inferenceConfig={
            "temperature": temperature or AWS_CONFIG["temperature"],
            "maxTokens": AWS_CONFIG["max_tokens"],
        },
    )

    return response["output"]["message"]["content"][0]["text"]


def chat_with_history(messages: list[dict], temperature: float | None = None) -> str:
    """
    带历史记录的对话
    :param messages: 消息列表 [{"role": "...", "content": "..."}]
    :param temperature: 温度参数
    :return: AI回复文本
    """
    client = get_client()

    # 转换消息格式为Bedrock格式
    bedrock_messages = []
    system_text = ""

    for msg in messages:
        if msg["role"] == "system":
            system_text = msg["content"]
        else:
            bedrock_messages.append({
                "role": msg["role"],
                "content": [{"text": msg["content"]}],
            })

    kwargs = {
        "modelId": AWS_CONFIG["model_id"],
        "messages": bedrock_messages,
        "inferenceConfig": {
            "temperature": temperature or AWS_CONFIG["temperature"],
            "maxTokens": AWS_CONFIG["max_tokens"],
        },
    }

    if system_text:
        kwargs["system"] = [{"text": system_text}]

    response = client.converse(**kwargs)
    return response["output"]["message"]["content"][0]["text"]
