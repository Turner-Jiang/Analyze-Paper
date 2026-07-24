"""
试卷比较模块 - 比较多份试卷的异同
"""
from __future__ import annotations

from services.ai_service import chat

COMPARISON_SYSTEM_PROMPT = """你是一位资深的教育专家和试卷比较分析师。你的任务是对多份试卷进行对比分析。

请从以下维度进行比较：

1. **基本信息对比**：科目、适用对象、总分、题量
2. **题型结构对比**：
   - 各试卷的题型构成差异
   - 题型比例的异同
3. **难度对比**：
   - 各试卷的整体难度评级
   - 难度梯度设计对比
   - 区分度分析
4. **知识点覆盖对比**：
   - 共同覆盖的知识点
   - 各自独有的知识点
   - 知识点覆盖广度与深度对比
5. **能力考查对比**：
   - 各试卷侧重的能力维度
   - 考查深度差异
6. **综合评价**：
   - 各试卷的优势与不足
   - 哪份更适合什么场景（期中/期末/模拟/竞赛）
   - 总体推荐与建议

请用对比表格和分析文字相结合的方式呈现，使用Markdown格式。"""


def compare_papers(papers: list[dict]) -> str:
    """
    比较多份试卷
    :param papers: 试卷列表 [{"name": "试卷名称", "content": "试卷内容"}, ...]
    :return: 比较分析结果（Markdown格式）
    """
    papers_text = ""
    for i, paper in enumerate(papers, 1):
        papers_text += f"\n{'='*50}\n【试卷{i}】{paper['name']}\n{'='*50}\n{paper['content']}\n"

    user_prompt = f"""请比较分析以下{len(papers)}份试卷：

{papers_text}

请提供详细的对比分析报告。"""

    return chat(COMPARISON_SYSTEM_PROMPT, user_prompt)


def compare_papers_aspect(papers: list[dict], aspect: str) -> str:
    """
    按特定维度比较试卷
    :param papers: 试卷列表
    :param aspect: 比较维度（如"难度"、"知识点"、"题型"等）
    :return: 比较结果
    """
    papers_text = ""
    for i, paper in enumerate(papers, 1):
        papers_text += f"\n【试卷{i}】{paper['name']}\n{paper['content']}\n\n"

    system_prompt = f"""你是试卷比较专家。请专门从"{aspect}"这个维度对以下试卷进行深入对比分析。
用表格和分析文字相结合的方式呈现结果。"""

    return chat(system_prompt, papers_text)
