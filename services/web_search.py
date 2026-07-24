"""
网络搜索模块 - 通过搜索引擎和教育网站获取试卷资源
"""
from __future__ import annotations

import time
import requests
from duckduckgo_search import DDGS
from config import SEARCH_CONFIG
from services.ai_service import chat

# 中国教育资源网站列表
EDUCATION_SITES = {
    "中国教育考试网": "https://www.neea.edu.cn",
    "学科网": "https://www.zxxk.com",
    "中学学科网": "https://www.xuekewang.com",
    "组卷网": "https://www.zujuan.com",
    "知乎-高考": "https://www.zhihu.com/search?type=content&q=",
    "百度文库": "https://wenku.baidu.com/search?word=",
    "全国卷网": "https://www.quanguo.cn",
    "高考网": "https://www.gaokao.com",
    "教育部阳光高考平台": "https://gaokao.chsi.com.cn",
}


def fetch_page_content(url: str, timeout: int = 10) -> str:
    """
    抓取网页内容
    :param url: 网址
    :param timeout: 超时时间
    :return: 网页文本内容
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.encoding = resp.apparent_encoding
        # 只取前面一部分，避免太长
        return resp.text[:5000]
    except Exception as e:
        return f"[抓取失败: {e}]"


def search_education_sites(query: str) -> str:
    """
    从中国教育网站搜索相关内容
    :param query: 搜索关键词
    :return: 抓取到的内容摘要
    """
    results = []

    # 知乎搜索
    zhihu_url = f"https://www.zhihu.com/search?type=content&q={query}"
    results.append(f"【知乎搜索】链接：{zhihu_url}")

    # 百度文库搜索
    baidu_url = f"https://wenku.baidu.com/search?word={query}"
    results.append(f"【百度文库】链接：{baidu_url}")

    # 组卷网搜索
    zujuan_url = f"https://www.zujuan.com/search?keyword={query}"
    results.append(f"【组卷网】链接：{zujuan_url}")

    # 学科网搜索
    xkw_url = f"https://www.zxxk.com/search?keyword={query}"
    results.append(f"【学科网】链接：{xkw_url}")

    # 全国卷网
    quanguo_url = f"https://www.quanguo.cn"
    results.append(f"【全国卷网】链接：{quanguo_url}")

    # 高考网
    gaokao_url = f"https://www.gaokao.com/search?q={query}"
    results.append(f"【高考网】链接：{gaokao_url}")

    # 教育部阳光高考平台
    chsi_url = f"https://gaokao.chsi.com.cn"
    results.append(f"【教育部阳光高考平台】链接：{chsi_url}")

    # 用DuckDuckGo限定教育网站搜索
    site_query = f"{query} site:zhihu.com OR site:zujuan.com OR site:zxxk.com OR site:neea.edu.cn OR site:gaokao.com OR site:quanguo.cn"
    try:
        ddg_results = DDGS().text(site_query, region="wt-wt", max_results=5)
        if ddg_results:
            for r in ddg_results:
                title = r.get("title", "")
                href = r.get("href", "")
                body = r.get("body", "")
                results.append(f"【{title}】\n  {body}\n  链接：{href}")
    except Exception:
        pass

    return "\n\n".join(results)


def search_papers(query: str, max_results: int | None = None) -> list[dict]:
    """
    搜索试卷相关资源（带重试机制）
    :param query: 搜索关键词
    :param max_results: 最大结果数
    :return: 搜索结果列表
    """
    max_results = max_results or SEARCH_CONFIG["max_results"]

    for attempt in range(3):
        try:
            results = DDGS().text(
                query,
                region=SEARCH_CONFIG["region"],
                max_results=max_results,
            )
            if results:
                return results
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
    综合搜索：DDG + 教育网站，然后AI总结
    :param query: 搜索关键词
    :return: AI整理后的结果
    """
    # 1. 从教育网站获取资源链接
    edu_results = search_education_sites(query)

    # 2. DDG通用搜索
    ddg_results = search_papers(query)
    ddg_text = ""
    if ddg_results:
        for i, r in enumerate(ddg_results, 1):
            title = r.get("title", "无标题")
            body = r.get("body", "无摘要")
            href = r.get("href", "")
            ddg_text += f"{i}. 【{title}】\n   {body}\n   链接：{href}\n\n"

    # 3. AI整合所有结果
    system_prompt = """你是一位中国教育资源检索专家。请根据以下搜索结果，为用户整理出有用的试卷资源信息。

要求：
1. 优先推荐可直接访问的链接
2. 按照资源类型分类整理（官方网站、在线题库、社区讨论等）
3. 给出每个资源的简要说明
4. 如果搜索结果不理想，请根据你的知识补充推荐

常用中国教育资源网站：
- 中国教育考试网 (neea.edu.cn) - 官方考试信息
- 学科网 (zxxk.com) - 试卷下载
- 组卷网 (zujuan.com) - 在线组卷
- 全国卷网 (quanguo.cn) - 全国卷真题资源
- 高考网 (gaokao.com) - 高考资源汇总
- 教育部阳光高考平台 (gaokao.chsi.com.cn) - 官方高考信息
- 知乎 (zhihu.com) - 学习经验和资源分享
- 百度文库 (wenku.baidu.com) - 文档资源"""

    user_prompt = f"""搜索关键词：{query}

===== 教育网站资源 =====
{edu_results}

===== 通用搜索结果 =====
{ddg_text if ddg_text else "无相关结果"}

请整理以上信息，为用户提供获取"{query}"相关试卷的最佳途径。"""

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
