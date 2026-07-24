"""
试卷爬虫模块 - 从教育网站爬取试卷内容
"""
from __future__ import annotations

import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote


# 通用请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def _get_soup(url: str, timeout: int = 15) -> BeautifulSoup | None:
    """获取页面BeautifulSoup对象"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.encoding = resp.apparent_encoding or "utf-8"
        return BeautifulSoup(resp.text, "html.parser")
    except Exception:
        return None


def _clean_text(text: str) -> str:
    """清理HTML提取的文本"""
    # 去除多余空白
    text = re.sub(r'\s+', ' ', text)
    # 去除常见的网页噪音
    noise_patterns = [
        r'©.*?版权所有', r'备案号.*?\d+', r'关注我们',
        r'下载APP', r'微信公众号', r'客服电话',
    ]
    for pattern in noise_patterns:
        text = re.sub(pattern, '', text)
    return text.strip()


# ==================== 各网站爬虫 ====================

def crawl_gaokao_com(query: str) -> list[dict]:
    """
    爬取高考网 (gaokao.com) 试卷内容
    """
    results = []
    search_url = f"https://www.gaokao.com/search?q={quote(query)}"

    soup = _get_soup(search_url)
    if not soup:
        # 尝试直接访问试题频道
        soup = _get_soup("https://www.gaokao.com/gkst/")

    if not soup:
        return results

    # 查找文章链接
    links = soup.find_all("a", href=True)
    paper_links = []
    for link in links:
        href = link.get("href", "")
        text = link.get_text(strip=True)
        if any(kw in text for kw in ["试卷", "真题", "模拟", "试题", query]):
            full_url = urljoin("https://www.gaokao.com", href)
            if full_url not in [p["url"] for p in paper_links]:
                paper_links.append({"title": text, "url": full_url})
        if len(paper_links) >= 5:
            break

    # 抓取每个试卷页面内容
    for item in paper_links[:3]:
        page_soup = _get_soup(item["url"])
        if page_soup:
            # 尝试提取正文
            content_div = (
                page_soup.find("div", class_="content") or
                page_soup.find("div", class_="article") or
                page_soup.find("article") or
                page_soup.find("div", id="content")
            )
            if content_div:
                text = _clean_text(content_div.get_text())
                if len(text) > 50:
                    results.append({
                        "title": item["title"],
                        "url": item["url"],
                        "content": text[:3000],
                    })
        time.sleep(0.5)

    return results


def crawl_zhihu(query: str) -> list[dict]:
    """
    爬取知乎相关试卷讨论和资源分享
    """
    results = []
    search_url = f"https://www.zhihu.com/search?type=content&q={quote(query + ' 试卷')}"

    soup = _get_soup(search_url)
    if not soup:
        return results

    # 提取搜索结果摘要
    items = soup.find_all("div", class_="SearchResult-Card") or soup.find_all("div", class_="List-item")
    for item in items[:5]:
        title_el = item.find("h2") or item.find("a")
        content_el = item.find("span", class_="RichText") or item.find("p")

        title = title_el.get_text(strip=True) if title_el else "知乎讨论"
        content = content_el.get_text(strip=True) if content_el else ""

        link_el = item.find("a", href=True)
        url = ""
        if link_el:
            href = link_el.get("href", "")
            url = urljoin("https://www.zhihu.com", href)

        if content and len(content) > 20:
            results.append({
                "title": title,
                "url": url,
                "content": content[:1500],
            })

    return results


def crawl_zujuan(query: str) -> list[dict]:
    """
    爬取组卷网 (zujuan.com) 试题内容
    """
    results = []
    search_url = f"https://www.zujuan.com/search?keyword={quote(query)}"

    soup = _get_soup(search_url)
    if not soup:
        return results

    # 查找试题列表
    items = soup.find_all("div", class_="question") or soup.find_all("li", class_="question-item")
    if not items:
        # 尝试通用选择器
        items = soup.find_all("div", class_=re.compile(r"item|question|paper"))

    for item in items[:5]:
        title_el = item.find("h3") or item.find("a") or item.find("span", class_="title")
        content_el = item.find("div", class_="content") or item.find("p")

        title = title_el.get_text(strip=True) if title_el else "组卷网试题"
        content = content_el.get_text(strip=True) if content_el else item.get_text(strip=True)

        link_el = item.find("a", href=True)
        url = urljoin("https://www.zujuan.com", link_el["href"]) if link_el else search_url

        if content and len(content) > 20:
            results.append({
                "title": title,
                "url": url,
                "content": _clean_text(content)[:2000],
            })

    return results


def crawl_xkw(query: str) -> list[dict]:
    """
    爬取学科网 (zxxk.com) 试卷资源
    """
    results = []
    search_url = f"https://www.zxxk.com/search?keyword={quote(query)}"

    soup = _get_soup(search_url)
    if not soup:
        return results

    items = soup.find_all("li", class_=re.compile(r"item|result")) or soup.find_all("div", class_=re.compile(r"item|result"))
    if not items:
        items = soup.find_all("a", href=True)
        items = [a for a in items if any(kw in a.get_text() for kw in ["试卷", "试题", "真题", query])]

    for item in items[:5]:
        if item.name == "a":
            title = item.get_text(strip=True)
            url = urljoin("https://www.zxxk.com", item.get("href", ""))
            content = title
        else:
            title_el = item.find("a") or item.find("h3")
            title = title_el.get_text(strip=True) if title_el else "学科网资源"
            link_el = item.find("a", href=True)
            url = urljoin("https://www.zxxk.com", link_el["href"]) if link_el else search_url
            content = _clean_text(item.get_text(strip=True))

        if title and len(title) > 3:
            results.append({
                "title": title,
                "url": url,
                "content": content[:1500],
            })

    return results


def crawl_neea(query: str) -> list[dict]:
    """
    爬取中国教育考试网 (neea.edu.cn)
    """
    results = []
    # 教育考试网没有搜索接口，直接访问高考频道
    urls_to_try = [
        "https://www.neea.edu.cn/html1/category/1507/index.html",
        "https://www.neea.edu.cn",
    ]

    for url in urls_to_try:
        soup = _get_soup(url)
        if not soup:
            continue

        links = soup.find_all("a", href=True)
        for link in links:
            text = link.get_text(strip=True)
            if any(kw in text for kw in ["高考", "考试", "通知", "公告"]):
                full_url = urljoin(url, link["href"])
                results.append({
                    "title": text,
                    "url": full_url,
                    "content": f"来源：中国教育考试网 - {text}",
                })
            if len(results) >= 3:
                break
        if results:
            break

    return results


# ==================== 主爬虫函数 ====================

def crawl_all_sites(query: str) -> dict[str, list[dict]]:
    """
    从所有教育网站爬取试卷相关内容
    :param query: 搜索关键词（如"2024高考数学"）
    :return: {网站名: [{"title": ..., "url": ..., "content": ...}]}
    """
    all_results = {}

    crawlers = [
        ("高考网", crawl_gaokao_com),
        ("知乎", crawl_zhihu),
        ("组卷网", crawl_zujuan),
        ("学科网", crawl_xkw),
        ("中国教育考试网", crawl_neea),
    ]

    for site_name, crawler_func in crawlers:
        try:
            results = crawler_func(query)
            if results:
                all_results[site_name] = results
        except Exception:
            pass
        time.sleep(0.3)  # 礼貌爬取，避免请求过快

    return all_results


def crawl_and_format(query: str) -> str:
    """
    爬取所有网站并格式化为文本，供AI分析使用
    :param query: 搜索关键词
    :return: 格式化的爬取结果
    """
    all_results = crawl_all_sites(query)

    if not all_results:
        return ""

    formatted = ""
    for site_name, items in all_results.items():
        formatted += f"\n{'='*40}\n来源：{site_name}\n{'='*40}\n"
        for item in items:
            formatted += f"\n标题：{item['title']}\n"
            formatted += f"链接：{item['url']}\n"
            if item.get('content'):
                formatted += f"内容：{item['content']}\n"
            formatted += "-" * 30 + "\n"

    return formatted
