# src/tools.py - Research tools for information gathering
from langchain_tavily import TavilySearch
from langchain_community.tools.arxiv.tool import ArxivQueryRun
import os

# Initialize tools - Tavily and ArXiv for research
research_tools = []

# Try to add Tavily search if API key is available
try:
    if os.getenv("TAVILY_API_KEY"):
        tavily_tool = TavilySearch()
        research_tools.append(tavily_tool)
        print("Tavily search tool loaded")
except Exception as e:
    print(f"Warning: Tavily search tool not available: {str(e)}")

# Try to add ArXiv search 
try:
    arxiv_tool = ArxivQueryRun()
    research_tools.append(arxiv_tool)
    print("ArXiv search tool loaded")
except Exception as e:
    print(f"Warning: ArXiv tool not available: {str(e)}")

# If no tools available, create dummy tools for demonstration
if not research_tools:
    from langchain_core.tools import tool
    
    @tool
    def search_web(query: str) -> str:
        """Search the web for information"""
        return f"Demo search results for: {query}"
    
    @tool
    def search_papers(query: str) -> str:
        """Search academic papers for information"""
        return f"Demo paper results for: {query}"
    
    research_tools = [search_web, search_papers]
    print("✓ Demo tools loaded (no real tools available)")

print(f"Total research tools available: {len(research_tools)}")