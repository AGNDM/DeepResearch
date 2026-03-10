# Deep Research Multiagent System
## File Structure
DRMS/
│
├── .env                    # Environment variables (API Keys: OpenAI, Tavily, etc.)
├── .gitignore              # Files/folders ignored by Git
├── requirements.txt        # Project dependencies (langgraph, langchain, tavily-python, etc.)
├── README.md               # Project documentation and setup guide
│
├── main.py                 # Entry point (CLI interface, execution trigger, Human-in-the-loop)
│
└── src/                    # Core source code directory
    ├── __init__.py         # Package initialization (exports ResearchState and Workflow)
    ├── state.py            # Global State definition (ResearchState TypedDict)
    ├── prompts.py          # Centralized LLM prompt templates
    ├── tools.py            # Tool configurations (Tavily search, arXiv API, etc.)
    │
    ├── agents/             # Agent logic implementations
    │   ├── __init__.py     # Exports specific Agent nodes (Planner, Researcher, etc.)
    │   ├── planner.py      # Planner Agent (Task decomposition logic)
    │   ├── researcher.py   # Researcher Agent (Tool execution & data gathering)
    │   └── reporter.py     # Reporter Agent (Markdown report generation)
    │
    └── workflow.py         # Graph construction (StateGraph definition & compilation)
