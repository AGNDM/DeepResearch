# src/prompts.py 示例
PLANNER_PROMPT = """你是一个专业的规划师。用户的研究需求是：{query}..."""
RESEARCHER_PROMPT = """你的任务是调研：{current_task}，请使用搜索工具..."""
REPORTER_PROMPT = """请根据以下资料撰写 Markdown 报告：\n{research_data}..."""