"""
Multi-Agent Research System Package

A LangGraph-based multi-agent research workflow that breaks down research queries,
conducts research, generates reports, and refines them based on human feedback.
"""

__version__ = "0.1.0"
__author__ = "AGNDM"
__all__ = [
    "workflow",
    "state",
    "tools",
    "prompts",
    "agents",
]

# Import main modules for easier access
from . import workflow
from . import state
from . import tools
from . import prompts
from . import agents

# Optional: expose key classes directly
try:
    from .workflow import graph
    from .state import ResearchState
except ImportError:
    pass
