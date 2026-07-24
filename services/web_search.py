"""
网络搜索模块 - 通过AI工具搜索试卷资源
"""

from duckduckgo_search import DDGS
from config import SEARCH_CONFIG
from services.ai_service import chat


def search_papers(query: str, max_results: int | None = None) -> list[dict]:
    """
    搜索试卷相关资源
    :param query: 搜索关键词
    :param max_results: 最大结果数
    :return: 搜索结果列表
    """
    max_results = max_results or SEARCH_CONFIG["max_results"]

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(
                query,
                region=SEARCH_CONFIG["region"],
                max_results=max_results,
            ))
        return results
    except Exception as e:
        return [{"title": "搜索出错", "body": str(e), "href": ""}]


def search_and_summarize(query: str) -> str:
    """
    搜索并用AI总结结果
    :param query: 搜索关键词
    :return: AI整理后的搜索结果摘要
    """
    results = search_papers(query)

    if not results:
        return "未找到相关结果。"

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
