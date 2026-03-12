# src/state.py 
from typing import TypedDict, List, Dict, Annotated, Optional
import operator

class ResearchState(TypedDict):
    query: str
    plan: List[str]
    completed_tasks: List[str]  # Regular list - will be replaced, not concatenated
    research_data: Annotated[Dict[str, str], operator.ior] # Automatically merge research data dictionaries
    draft: str
    feedback: str
    revision_count: int
    draft_history: List[Dict[str, str]]  # Store revision history {revision: ..., draft: ...}
    refined_feedback: str  # Refined human feedback
    feedback_target_agent: Optional[str]  # Target agent for feedback: "planner", "reporter", "end"
    feedback_analysis_reason: str  # Reason for feedback analysis