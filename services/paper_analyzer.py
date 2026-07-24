"""
试卷分析模块 - 分析试卷的题目结构、难度分布、知识点覆盖等
"""

from services.ai_service import chat

ANALYSIS_SYSTEM_PROMPT = """你是一位资深的教育专家和试卷分析师。你的任务是对给定的试卷内容进行深入、专业的分析。

请从以下维度进行分析：

1. **基本信息**：科目、年级/适用对象、考试时长（如果有）、总分
2. **题目结构**：
   - 题型分布（选择题、填空题、简答题、计算题、论述题等）
   - 各题型数量和分值
3. **难度分析**：
   - 整体难度评估（简单/中等/较难/困难）
   - 各部分难度分布
   - 难度梯度设计是否合理
4. **知识点覆盖**：
   - 涉及的主要知识点/章节
   - 各知识点的分值占比
   - 重点知识点分析
5. **能力考查**：
   - 考查的能力维度（记忆、理解、应用、分析、评价、创造）
   - 各能力层次的分值占比
6. **试卷质量评价**：
   - 优点
   - 不足之处
   - 改进建议

请用清晰的结构化格式输出分析结果，使用Markdown格式。"""


def analyze_paper(paper_content: str) -> str:
    """
    分析单份试卷
    :param paper_content: 试卷文本内容
    :return: 分析结果（Markdown格式）
    """
    user_prompt = f"""请分析以下试卷内容：

---
{paper_content}
---

请提供详细的分析报告。"""

    return chat(ANALYSIS_SYSTEM_PROMPT, user_prompt)


def analyze_paper_quick(paper_content: str) -> str:
    """
    快速分析试卷（简略版）
    :param paper_content: 试卷文本内容
    :return: 简略分析结果
    """
    system_prompt = """你是试卷分析专家。请对试卷进行简要分析，包括：科目、题型数量、总分、难度评级、主要知识点。
用简洁的表格或列表形式呈现，不超过200字。"""

    return chat(system_prompt, f"试卷内容：\n{paper_content}")
