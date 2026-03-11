# src/state.py 
from typing import TypedDict, List, Dict, Annotated
import operator

class ResearchState(TypedDict):
    query: str
    plan: List[str]
    completed_tasks: Annotated[List[str], operator.add]  # Automatically concatenate completed tasks
    research_data: Annotated[Dict[str, str], operator.ior] # Automatically merge research data dictionaries
    draft: str
    feedback: str
    revision_count: int
    draft_history: List[Dict[str, str]]  # 存储每次修改的历史 {revision: ..., draft: ...}