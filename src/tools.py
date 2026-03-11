# src/tools.py 示例
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools.arxiv.tool import ArxivQueryRun

tavily_tool = TavilySearchResults(max_results=3)
arxiv_tool = ArxivQueryRun()
research_tools =[tavily_tool, arxiv_tool]