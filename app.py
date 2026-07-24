"""
AI试卷分析Agent - 主应用
功能：分析试卷、比较试卷、生成试卷、搜索试卷
"""

import streamlit as st
from config import APP_CONFIG, AWS_CONFIG

# 页面配置
st.set_page_config(
    page_title=APP_CONFIG["title"],
    page_icon=APP_CONFIG["page_icon"],
    layout="wide",
    initial_sidebar_state="expanded",
)

# 侧边栏 - 配置
with st.sidebar:
    st.title(f"{APP_CONFIG['page_icon']} {APP_CONFIG['title']}")
    st.markdown("---")

    # AWS Bedrock设置
    with st.expander("⚙️ AWS Bedrock 设置", expanded=False):
        region = st.text_input(
            "AWS Region",
            value=AWS_CONFIG["region"],
            help="AWS区域，如 us-west-2",
        )
        model_id = st.text_input(
            "模型ID",
            value=AWS_CONFIG["model_id"],
            help="Bedrock模型ID，如 anthropic.claude-3-5-sonnet-20241022-v2:0",
        )

        if region:
            AWS_CONFIG["region"] = region
        if model_id:
            AWS_CONFIG["model_id"] = model_id

        st.info("AWS凭证从环境变量/.env文件读取")

    st.markdown("---")
    st.markdown("### 功能导航")
    page = st.radio(
        "选择功能",
        ["📊 试卷分析", "🔍 试卷比较", "✍️ 试卷生成", "🌐 搜索试卷"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        """
    **使用说明**
    - 📊 分析：上传试卷，AI深度分析
    - 🔍 比较：上传多份试卷进行比较
    - ✍️ 生成：根据要求生成新试卷
    - 🌐 搜索：AI辅助查找试卷资源
    """
    )

# 检查AWS配置
def check_api_config():
    import os
    if not os.environ.get("AWS_ACCESS_KEY_ID") and not os.environ.get("AWS_SESSION_TOKEN"):
        st.warning("⚠️ 未检测到AWS凭证，请确保.env文件已正确配置")
        return False
    return True


# ==================== 试卷分析页面 ====================
if page == "📊 试卷分析":
    st.header("📊 试卷分析")
    st.markdown("上传试卷文件，AI将对其进行深度分析")

    uploaded_file = st.file_uploader(
        "上传试卷",
        type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
        help="支持PDF、Word、文本文件和图片格式",
    )

    # 或者直接输入文本
    text_input = st.text_area(
        "或直接粘贴试卷内容",
        height=200,
        placeholder="将试卷文本粘贴到这里...",
    )

    col1, col2 = st.columns(2)
    with col1:
        analyze_full = st.button("📋 详细分析", use_container_width=True)
    with col2:
        analyze_quick = st.button("⚡ 快速分析", use_container_width=True)

    if analyze_full or analyze_quick:
        if not check_api_config():
            st.stop()

        paper_content = ""

        if uploaded_file:
            from services.file_parser import parse_file
            with st.spinner("正在解析文件..."):
                file_bytes = uploaded_file.read()
                paper_content = parse_file(uploaded_file.name, file_bytes)
        elif text_input:
            paper_content = text_input
        else:
            st.error("请上传文件或输入试卷内容")
            st.stop()

        if paper_content:
            st.markdown("---")
            st.subheader("📄 解析内容预览")
            with st.expander("点击查看原文", expanded=False):
                st.text(paper_content[:3000] + ("..." if len(paper_content) > 3000 else ""))

            from services.paper_analyzer import analyze_paper, analyze_paper_quick

            with st.spinner("AI正在分析试卷..."):
                if analyze_full:
                    result = analyze_paper(paper_content)
                else:
                    result = analyze_paper_quick(paper_content)

            st.subheader("📊 分析结果")
            st.markdown(result)


# ==================== 试卷比较页面 ====================
elif page == "🔍 试卷比较":
    st.header("🔍 试卷比较")
    st.markdown("上传多份试卷，AI将进行对比分析")

    num_papers = st.number_input("比较试卷数量", min_value=2, max_value=5, value=2)

    papers = []
    cols = st.columns(num_papers)

    for i in range(num_papers):
        with cols[i]:
            st.markdown(f"**试卷 {i + 1}**")
            file = st.file_uploader(
                f"上传试卷{i + 1}",
                type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
                key=f"compare_file_{i}",
            )
            text = st.text_area(
                f"或粘贴内容",
                height=150,
                key=f"compare_text_{i}",
                placeholder=f"试卷{i + 1}内容...",
            )
            papers.append({"file": file, "text": text})

    # 比较维度选择
    aspect = st.selectbox(
        "选择比较维度（可选）",
        ["全面比较", "难度对比", "知识点覆盖", "题型结构", "能力考查"],
    )

    if st.button("🔍 开始比较", use_container_width=True):
        if not check_api_config():
            st.stop()

        from services.file_parser import parse_file

        parsed_papers = []
        for i, p in enumerate(papers):
            content = ""
            name = f"试卷{i + 1}"
            if p["file"]:
                with st.spinner(f"解析试卷{i + 1}..."):
                    file_bytes = p["file"].read()
                    content = parse_file(p["file"].name, file_bytes)
                    name = p["file"].name
            elif p["text"]:
                content = p["text"]

            if content:
                parsed_papers.append({"name": name, "content": content})

        if len(parsed_papers) < 2:
            st.error("请至少提供2份试卷内容进行比较")
            st.stop()

        from services.paper_comparator import compare_papers, compare_papers_aspect

        with st.spinner("AI正在比较分析..."):
            if aspect == "全面比较":
                result = compare_papers(parsed_papers)
            else:
                result = compare_papers_aspect(parsed_papers, aspect)

        st.markdown("---")
        st.subheader("📊 比较结果")
        st.markdown(result)


# ==================== 试卷生成页面 ====================
elif page == "✍️ 试卷生成":
    st.header("✍️ 试卷生成")
    st.markdown("根据你的需求生成全新试卷")

    tab1, tab2, tab3 = st.tabs(["📝 自定义生成", "📄 参考试卷生成", "🎯 单项出题"])

    # --- 自定义生成 ---
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            subject = st.text_input("科目", placeholder="如：数学、语文、英语...")
            grade = st.text_input("年级/适用对象", placeholder="如：高三、初二...")
            difficulty = st.select_slider(
                "难度等级",
                options=["简单", "较简单", "中等", "较难", "困难"],
                value="中等",
            )
        with col2:
            duration = st.number_input("考试时长（分钟）", min_value=30, max_value=300, value=120)
            total_score = st.number_input("总分", min_value=50, max_value=200, value=100)

        question_types = st.multiselect(
            "题型要求",
            ["选择题", "填空题", "判断题", "简答题", "计算题", "论述题", "作文题", "应用题", "证明题"],
        )

        knowledge_points_text = st.text_input(
            "知识点（逗号分隔）",
            placeholder="如：函数,导数,积分",
        )
        knowledge_points = [k.strip() for k in knowledge_points_text.split(",") if k.strip()] if knowledge_points_text else None

        extra_req = st.text_area("其他要求", placeholder="如：注重基础题，少出偏题...")

        if st.button("✍️ 生成试卷", use_container_width=True, key="gen_custom"):
            if not check_api_config():
                st.stop()
            if not subject or not grade:
                st.error("请至少填写科目和年级")
                st.stop()

            from services.paper_generator import generate_paper

            with st.spinner("AI正在生成试卷，请稍候..."):
                result = generate_paper(
                    subject=subject,
                    grade=grade,
                    difficulty=difficulty,
                    duration=duration,
                    total_score=total_score,
                    question_types=question_types or None,
                    knowledge_points=knowledge_points,
                    extra_requirements=extra_req,
                )

            st.markdown("---")
            st.subheader("📄 生成的试卷")
            st.markdown(result)

            # 下载按钮
            st.download_button(
                "📥 下载试卷（Markdown）",
                data=result,
                file_name=f"{subject}_{grade}_试卷.md",
                mime="text/markdown",
            )

    # --- 参考试卷生成 ---
    with tab2:
        st.markdown("上传一份参考试卷，AI将生成一份类似的新试卷")

        ref_file = st.file_uploader(
            "上传参考试卷",
            type=["pdf", "docx", "txt"],
            key="ref_file",
        )
        ref_text = st.text_area(
            "或粘贴参考试卷内容",
            height=200,
            key="ref_text",
            placeholder="粘贴参考试卷内容...",
        )
        modifications = st.text_area(
            "调整要求（可选）",
            placeholder="如：难度提高一些，增加应用题...",
        )

        if st.button("✍️ 根据参考生成", use_container_width=True, key="gen_ref"):
            if not check_api_config():
                st.stop()

            ref_content = ""
            if ref_file:
                from services.file_parser import parse_file
                ref_content = parse_file(ref_file.name, ref_file.read())
            elif ref_text:
                ref_content = ref_text

            if not ref_content:
                st.error("请提供参考试卷")
                st.stop()

            from services.paper_generator import generate_paper_from_reference

            with st.spinner("AI正在生成新试卷..."):
                result = generate_paper_from_reference(ref_content, modifications)

            st.markdown("---")
            st.subheader("📄 生成的新试卷")
            st.markdown(result)

            st.download_button(
                "📥 下载试卷（Markdown）",
                data=result,
                file_name="生成试卷.md",
                mime="text/markdown",
                key="dl_ref",
            )

    # --- 单项出题 ---
    with tab3:
        st.markdown("快速生成特定类型的题目")

        col1, col2 = st.columns(2)
        with col1:
            q_subject = st.text_input("科目", key="q_subject", placeholder="数学")
            q_type = st.selectbox(
                "题目类型",
                ["选择题", "填空题", "判断题", "简答题", "计算题", "论述题", "应用题"],
            )
        with col2:
            q_count = st.number_input("题目数量", min_value=1, max_value=20, value=5)
            q_difficulty = st.select_slider(
                "题目难度",
                options=["简单", "较简单", "中等", "较难", "困难"],
                value="中等",
                key="q_diff",
            )
        q_knowledge = st.text_input("知识点（可选）", placeholder="如：二次函数")

        if st.button("🎯 生成题目", use_container_width=True, key="gen_q"):
            if not check_api_config():
                st.stop()
            if not q_subject:
                st.error("请填写科目")
                st.stop()

            from services.paper_generator import generate_questions

            with st.spinner("AI正在出题..."):
                result = generate_questions(
                    subject=q_subject,
                    question_type=q_type,
                    count=q_count,
                    difficulty=q_difficulty,
                    knowledge_point=q_knowledge,
                )

            st.markdown("---")
            st.subheader("🎯 生成的题目")
            st.markdown(result)


# ==================== 搜索试卷页面 ====================
elif page == "🌐 搜索试卷":
    st.header("🌐 搜索试卷")
    st.markdown("通过AI辅助搜索网上的试卷资源")

    tab1, tab2 = st.tabs(["🔎 关键词搜索", "🤖 AI智能查找"])

    with tab1:
        search_query = st.text_input("搜索关键词", placeholder="如：2024年高考数学真题")

        if st.button("🔎 搜索", use_container_width=True, key="search_btn"):
            if not search_query:
                st.error("请输入搜索关键词")
                st.stop()

            from services.web_search import search_papers, search_and_summarize

            with st.spinner("正在搜索..."):
                # 先展示原始结果
                results = search_papers(search_query)

            if results:
                st.subheader("搜索结果")
                for i, r in enumerate(results, 1):
                    title = r.get("title", "无标题")
                    body = r.get("body", "")
                    href = r.get("href", "")
                    with st.expander(f"{i}. {title}"):
                        st.write(body)
                        if href:
                            st.markdown(f"[打开链接]({href})")

                # AI总结
                if check_api_config():
                    with st.spinner("AI正在整理结果..."):
                        summary = search_and_summarize(search_query)
                    st.markdown("---")
                    st.subheader("🤖 AI整理")
                    st.markdown(summary)
            else:
                st.info("未找到相关结果，请尝试其他关键词")

    with tab2:
        st.markdown("告诉AI你需要什么类型的试卷，AI帮你查找")

        col1, col2, col3 = st.columns(3)
        with col1:
            s_subject = st.text_input("科目", key="s_subject", placeholder="数学")
        with col2:
            s_grade = st.text_input("年级", key="s_grade", placeholder="高三")
        with col3:
            s_type = st.text_input("考试类型", key="s_type", placeholder="期末/模拟/真题")

        if st.button("🤖 AI查找", use_container_width=True, key="ai_find_btn"):
            if not s_subject or not s_grade:
                st.error("请至少填写科目和年级")
                st.stop()
            if not check_api_config():
                st.stop()

            from services.web_search import ai_find_papers

            with st.spinner("AI正在查找试卷资源..."):
                result = ai_find_papers(s_subject, s_grade, s_type)

            st.markdown("---")
            st.subheader("🤖 查找结果")
            st.markdown(result)
