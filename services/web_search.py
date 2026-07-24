"""
网络搜索模块 - 通过AI工具搜索试卷资源
"""
from __future__ import annotations

import time
from duckduckgo_search import DDGS
from config import SEARCH_CONFIG
from services.ai_service import chat


def search_papers(query: str, max_results: int | None = None) -> list[dict]:
    """
    搜索试卷相关资源（带重试机制）
    :param query: 搜索关键词
    :param max_results: 最大结果数
    :return: 搜索结果列表
    """
    max_results = max_results or SEARCH_CONFIG["max_results"]

    # 尝试多次搜索
    for attempt in range(3):
        try:
            results = DDGS().text(
                query,
                region=SEARCH_CONFIG["region"],
                max_results=max_results,
            )
            if results:
                return results
            # 如果结果为空，换用全球区域重试
            results = DDGS().text(
                query,
                region="wt-wt",
                max_results=max_results,
            )
            if results:
                return results
        except Exception as e:
            if attempt < 2:
                time.sleep(1)
                continue
            return [{"title": "搜索出错", "body": str(e), "href": ""}]

    return []


def search_and_summarize(query: str) -> str:
    """
    搜索并用AI总结结果。如果搜索失败，让AI根据自身知识提供建议。
    :param query: 搜索关键词
    :return: AI整理后的搜索结果摘要
    """
    results = search_papers(query)

    if not results:
        # 搜索无结果时，让AI根据自身知识推荐
        system_prompt = """你是一位教育资源推荐专家。用户想查找试卷资源但搜索未返回结果。
请根据你的知识，为用户推荐可能找到相关试卷的网站和途径，并给出搜索建议。"""
        user_prompt = f"用户想查找：{query}\n\n请推荐获取此类试卷的途径和建议。"
        return chat(system_prompt, user_prompt)

    # 整理搜索结果
    results_text = ""
    for i, r in enumerate(results, 1):
        title = r.get("title", "无标题")
        body = r.get("body", "无摘要")
        href = r.get("href", "")
        results_text += f"{i}. 【{title}】\n   {body}\n   链接：{href}\n\n"

    # 用AI总结
    system_prompt = """你是一位教育资源检索助手。请对搜索结果进行整理和总结，
帮助用户快速了解找到了哪些有用的试卷资源。如果有可下载的链接，请特别标出。"""

    user_prompt = f"搜索关键词：{query}\n\n搜索结果：\n{results_text}\n\n请整理这些结果。"

    return chat(system_prompt, user_prompt)


def ai_find_papers(subject: str, grade: str, exam_type: str = "") -> str:
    """
    AI辅助查找试卷
    :param subject: 科目
    :param grade: 年级
    :param exam_type: 考试类型（期中/期末/模拟/真题等）
    :return: 查找结果与建议
    """
    query_parts = [grade, subject]
    if exam_type:
        query_parts.append(exam_type)
    query_parts.append("试卷")

    query = " ".join(query_parts)
    return search_and_summarize(query)
