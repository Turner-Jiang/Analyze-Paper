# AI试卷分析Agent

一个基于大语言模型的智能试卷分析工具，支持试卷分析、比较、生成和搜索功能。

## 功能特性

- **📊 试卷分析**：上传试卷文件或粘贴内容，AI深度分析题型结构、难度分布、知识点覆盖等
- **🔍 试卷比较**：对比多份试卷的异同，支持按维度比较
- **✍️ 试卷生成**：根据科目、年级、难度等参数自动生成试卷，支持参考试卷生成
- **🌐 搜索试卷**：通过网络搜索和AI辅助查找试卷资源

## 支持的文件格式

- PDF (.pdf)
- Word文档 (.docx)
- 文本文件 (.txt)
- 图片 (.png, .jpg, .jpeg)

## 快速开始

### 1. 安装依赖

```bash
# 激活虚拟环境
.venv\Scripts\activate    # Windows
source .venv/bin/activate # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API

你可以通过以下方式配置API：

**方式一：环境变量**
```bash
set OPENAI_API_KEY=你的API密钥
set OPENAI_BASE_URL=https://api.openai.com/v1
set AI_MODEL=gpt-4o-mini
```

**方式二：在应用界面左侧边栏配置**

### 3. 运行应用

```bash
streamlit run app.py
```

## 支持的AI模型

兼容所有OpenAI接口格式的模型：

| 服务商 | Base URL | 模型示例 |
|--------|----------|----------|
| OpenAI | https://api.openai.com/v1 | gpt-4o-mini, gpt-4o |
| DeepSeek | https://api.deepseek.com/v1 | deepseek-chat |
| 智谱AI | https://open.bigmodel.cn/api/paas/v4 | glm-4 |
| 通义千问 | https://dashscope.aliyuncs.com/compatible-mode/v1 | qwen-plus |

## 项目结构

```
.
├── app.py                    # Streamlit主应用
├── config.py                 # 配置文件
├── requirements.txt          # Python依赖
├── README.md                 # 说明文档
└── services/
    ├── __init__.py
    ├── ai_service.py         # AI模型调用封装
    ├── file_parser.py        # 文件解析（PDF/DOCX/TXT/图片）
    ├── paper_analyzer.py     # 试卷分析
    ├── paper_comparator.py   # 试卷比较
    ├── paper_generator.py    # 试卷生成
    └── web_search.py         # 网络搜索
```
