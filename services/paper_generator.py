"""
试卷生成模块 - 根据参数或参考试卷生成新试卷
"""

from services.ai_service import chat

GENERATION_SYSTEM_PROMPT = """你是一位经验丰富的命题教师。你的任务是根据给定的要求生成高质量的试卷。

生成试卷时请注意：
1. 题目表述清晰、准确、无歧义
2. 难度梯度合理，由易到难
3. 知识点覆盖全面均衡
4. 题型搭配合理
5. 分值分配科学
6. 提供标准答案和评分标准

输出格式要求：
- 使用清晰的排版格式
- 标注每道题的分值
- 在试卷末尾附上参考答案和评分标准"""


def generate_paper(
    subject: str,
    grade: str,
    difficulty: str = "中等",
    duration: int = 120,
    total_score: int = 100,
    question_types: list[str] | None = None,
    knowledge_points: list[str] | None = None,
    extra_requirements: str = "",
) -> str:
    """
    根据参数生成试卷
    :param subject: 科目
    :param grade: 年级
    :param difficulty: 难度等级
    :param duration: 考试时长（分钟）
    :param total_score: 总分
    :param question_types: 题型要求列表
    :param knowledge_points: 知识点要求列表
    :param extra_requirements: 额外要求
    :return: 生成的试卷内容（Markdown格式）
    """
    requirements = f"""请生成一份试卷，具体要求如下：

- 科目：{subject}
- 年级/适用对象：{grade}
- 难度：{difficulty}
- 考试时长：{duration}分钟
- 总分：{total_score}分"""

    if question_types:
        requirements += f"\n- 题型要求：{', '.join(question_types)}"

    if knowledge_points:
        requirements += f"\n- 知识点覆盖：{', '.join(knowledge_points)}"

    if extra_requirements:
        requirements += f"\n- 其他要求：{extra_requirements}"

    requirements += "\n\n请生成完整的试卷，包括试题和参考答案。"

    return chat(GENERATION_SYSTEM_PROMPT, requirements, temperature=0.8)


def generate_paper_from_reference(reference_content: str, modifications: str = "") -> str:
    """
    根据参考试卷生成类似试卷
    :param reference_content: 参考试卷内容
    :param modifications: 需要的修改/调整
    :return: 生成的试卷
    """
    system_prompt = """你是一位命题教师。请参考给定的试卷，生成一份类似但不同的新试卷。
保持相同的结构和难度，但使用不同的题目。提供标准答案和评分标准。"""

    user_prompt = f"""参考试卷：
{reference_content}

"""
    if modifications:
        user_prompt += f"调整要求：{modifications}\n\n"

    user_prompt += "请生成新试卷。"

    return chat(system_prompt, user_prompt, temperature=0.85)


def generate_questions(
    subject: str,
    question_type: str,
    count: int = 5,
    difficulty: str = "中等",
    knowledge_point: str = "",
) -> str:
    """
    生成特定类型的题目
    :param subject: 科目
    :param question_type: 题目类型
    :param count: 题目数量
    :param difficulty: 难度
    :param knowledge_point: 知识点
    :return: 生成的题目
    """
    system_prompt = "你是命题教师，请生成高质量的试题，每道题都要有标准答案。"

    user_prompt = f"""请生成{count}道{subject}的{question_type}，要求：
- 难度：{difficulty}
- 知识点：{knowledge_point if knowledge_point else '不限'}

请给出题目和标准答案。"""

    return chat(system_prompt, user_prompt, temperature=0.85)
