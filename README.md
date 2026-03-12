# Multi-Agent Research System

A sophisticated **LangGraph-based multi-agent research workflow** that automatically breaks down research queries, conducts research, generates reports, and iteratively refines them based on human feedback.

## Features

### 🤖 Intelligent Multi-Agent Architecture

- **Planner Agent**: Decomposes research queries into specific, actionable tasks
- **Researcher Agent**: Executes tasks in parallel using web search and APIs
- **Reporter Agent**: Synthesizes research data into well-structured markdown reports
- **Feedback Analyzer**: Intelligently routes user feedback to appropriate agents
- **Coordinator Router**: Dynamically decides the next action based on workflow state

### 💬 Human-in-the-Loop (HITL) Workflow

- **Interactive User Input**: Real-time feedback instead of mock data
- **Intelligent Feedback Routing**:
  - "Expand research" → Re-plan tasks with feedback incorporated
  - "Improve writing" → Revise report with feedback
  - "approve" → Finalize and save the report
- **Iterative Refinement**: Support multiple rounds of feedback and revisions
- **Conversation History**: Maintains draft history and revision tracking

### 📁 Automatic Report Management

- **Timestamped Reports**: `reports/report_YYYYMMDD_HHMMSS.md`
- **Persistent Storage**: All reports saved for future reference

### 📋 Clean Output Format

- **Emoji-Free Labels**: Uses `[LABEL]` format for universal terminal compatibility
- **Structured Messages**: Clear, organized output for easy reading
- **Status Indicators**: `[START]`, `[DONE]`, `[ERROR]`, `[ROUTE]`, etc.

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd MultiagentLLM

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys (OpenRouter, Tavily, etc.)
```

### Run

```bash
python3 main.py
```

### Interactive Flow

```
[1] Enter your research topic when prompted
    >> Machine Learning in Healthcare

[2] System runs automatically
    [PLANNER] Creates research plan
    [RESEARCHER] Gathers data
    [REPORTER] Generates report

[3] Review the generated report

[4] Provide feedback (or type 'approve')
    >> Add more recent examples
    OR
    >> approve

[5] System responds to feedback
    [Routes back to Planner for more research]
    OR
    [Routes to Reporter for revision]
    OR
    [Finalizes and saves]

[6] Report automatically saved
    reports/report_20260312_145230.md
```

---

## Architecture & Workflow

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│  User Input (Query & Feedback)                          │
└────────────────────┬────────────────────────────────────┘
                     ↓
        ┌────────────────────────┐
        │  Coordinator Router    │
        └────────────────────────┘
         ↙  ↙  ↙  ↙  ↙  ↙  ↙
    ┌────────┐  ┌──────────┐  ┌────────┐  ┌──────────────┐
    │ Planner│  │Researcher│  │Reporter│  │Feedback      │
    │        │  │          │  │        │  │Analyzer      │
    └────────┘  └──────────┘  └────────┘  └──────────────┘
         │         │             │             │
         └─────────┴─────────────┴─────────────┘
                     ↓
              State Updates
              (LangGraph)
```

### State Management

**ResearchState** (TypedDict with automatic merging):

```python
class ResearchState:
    query: str                              # Original research query
    plan: List[str]                         # Task breakdown (cleared when replanned)
    completed_tasks: List[str]              # Tracks completed research tasks
    research_data: Dict[str, str]           # Research findings (cleared when re-planning)
    draft: str                              # Generated markdown report (cleared when re-planning)
    feedback: str                           # Raw user feedback
    refined_feedback: str                   # Polished feedback (shared across agents)
    feedback_target_agent: str              # Route destination ("planner", "reporter", "end")
    revision_count: int                     # Tracks improvement iterations
    draft_history: List[Dict]               # Maintains all previous versions
    feedback_analysis_reason: str           # Explains routing decision
```

### Routing Logic (Coordinator Router)

**Priority Decision Tree**:

1. **Approve Signal** → Direct END (skip workflow)
2. **Raw Feedback** → Feedback Analyzer (LLM analysis)
3. **Analyzed Feedback** → Route to target agent (Planner/Reporter/End)
4. **No Plan** → Planner
5. **Incomplete Tasks** → Researcher (parallel execution)
6. **No Draft** → Reporter
7. **Default** → END (await human review)

### Agent Responsibilities

| Agent                 | Input                              | Processing               | Output                     |
| --------------------- | ---------------------------------- | ------------------------ | -------------------------- |
| **Planner**           | Query + Refined Feedback           | Break down into tasks    | Task list + Clear old data |
| **Researcher**        | Tasks + Feedback                   | Execute tasks with tools | Research findings per task |
| **Reporter**          | Research data + Feedback + History | Synthesize into report   | Markdown report            |
| **Feedback Analyzer** | User feedback + Draft              | Classify & refine        | Target agent + Analysis    |

---

## Interactive Features

### Feedback Types & Routing

#### Type 1: Request More Research

**User Input**: "Add information about X", "Include recent studies", "Expand on Y"

```
Flow: Feedback → Analyzer → Planner → Researcher → Reporter → Save
Effect: New research conducted, old data cleared, new report generated
```

#### Type 2: Request Report Revision

**User Input**: "Better summary", "Improve wording", "Add examples", "Reorganize"

```
Flow: Feedback → Analyzer → Reporter → Save
Effect: Report rewritten with same research data, previous version visible to LLM
```

#### Type 3: Approve & Finalize

**User Input**: "approve"

```
Flow: Rule-based check → Direct END → Save final report
Effect: Workflow terminates immediately, report finalized
```

### Reporter Behavior with Context

The reporter generates reports differently based on available context:

| Scenario      | Previous Draft | User Feedback | Behavior                                     |
| ------------- | -------------- | ------------- | -------------------------------------------- |
| Initial       | No             | No            | Basic report from research data              |
| Feedback only | No             | Yes           | New report incorporating feedback            |
| Revision      | Yes            | Yes           | Show previous version + incorporate feedback |
| New data      | Yes            | No            | Improve report while maintaining strengths   |

---

## Output Format

### Console Labels

All system messages use `[LABEL]` format:

```
[START]      - Workflow initialization
[TOPIC]      - Research topic confirmation
[PLAN]       - Planning stage updates
[EXEC]       - Task execution status
[TOOLS]      - Tool calls and results
[RESEARCH]   - Research progress
[REPORTER]   - Report generation
[FEEDBACK]   - User feedback reception
[PROCESS]    - Feedback processing
[ROUTE]      - Routing decisions
[COMPLETE]   - Task/workflow completion
[DONE]       - Final completion
[ERROR]      - Error messages
[WARN]       - Warning messages
[SAVED]      - File save confirmation
```

### Generated Reports

Each report includes:

- **Timestamp**: Auto-generated, e.g., `report_20260312_145230.md`
- **Format**: Markdown with:
  - Executive summary
  - Main findings by topic
  - Key insights and analysis
  - Recommendations
  - References section

---

## File Structure

```
MultiagentLLM/
├── .env                      # Environment variables (API keys)
├── .gitignore                # Git ignore rules (includes /reports/)
├── requirements.txt          # Project dependencies
├── README.md                 # This file
│
├── main.py                   # Entry point with HITL loop
│
├── reports/                  # Auto-created for saving reports
│   └── report_*.md           # Generated markdown reports
│
└── src/                      # Core source code
    ├── __init__.py           # Package exports
    ├── state.py              # ResearchState TypedDict
    ├── prompts.py            # Centralized LLM prompt templates
    ├── tools.py              # Tool configurations (Tavily, etc.)
    ├── workflow.py           # LangGraph StateGraph construction
    │
    └── agents/               # Agent implementations
        ├── __init__.py       # Agent exports
        ├── planner.py        # Task planning with feedback
        ├── researcher.py     # Task execution with tools
        ├── reporter.py       # Report generation (4 scenarios)
        └── feedback_analyzer.py  # Feedback classification & routing
```

---

## Setup & Configuration

### Environment Variables (.env)

```bash
# LLM Configuration
LLM_API_KEY=your_openrouter_api_key
LLM_MODEL=stepfun/step-3.5-flash:free

# Search Tools
TAVILY_API_KEY=your_tavily_api_key

# Optional
OPENAI_API_KEY=your_openai_key  # If using direct OpenAI
ARXIV_API_KEY=your_arxiv_key    # For paper citations
```

### Dependencies

```
langchain>=0.1.0
langgraph>=0.0.1
langchain-openai>=0.0.5
langchain-community>=0.0.10
tavily-python>=0.1.0
python-dotenv>=1.0.0
```

---

## Usage Guide

### Basic Workflow

```bash
$ python3 main.py

[START] Starting Research Workflow
[TOPIC] Research Topic: Impact of AI on Healthcare

[PLAN] Preparing to process 5 tasks
[EXEC] Executing research tasks in parallel...
[TOOLS] Tool calls detected: 3
[DONE] 5 tasks completed

[REPORTER] Generating report draft...
[GENERATED] Draft created from 5 data sources

[REVIEW] Entering Human Review Stage

[REPORT] Generated Report Draft:
────────────────────────────────────────────────────────
[Report content displayed here]
────────────────────────────────────────────────────────

==================================================
Please provide your feedback (or type 'approve'):
==================================================
>> Include cost-benefit analysis
```

### Feedback Examples

**For More Research**:

```
>> Add case studies from Asia
>> Include more recent papers (2024+)
>> Expand on ethical implications
```

**For Report Revision**:

```
>> Improve the executive summary
>> Add more concrete examples
>> Better organization of findings
```

**To Finalize**:

```
>> approve
```

---

## Advanced Features

### Revision History

The system maintains a complete revision history:

```
Version 0 (Initial draft)
  └─ Feedback: "Add more examples"
  └─ Version 1 (Revised report)
     └─ Feedback: "Include statistics"
     └─ Version 2 (Final report)
```

### Feedback Context

Agents have access to:

- **Previous Versions**: Reporter can see what changed and improve accordingly
- **Feedback History**: All feedback tracked for reference
- **Execution History**: Task completion status and research data collected

### Data Persistence

- Reports auto-save with timestamped filenames
- No loss of work between sessions

---

## Troubleshooting

### Common Issues

**Q: Report is empty**

- Check if research data was collected (look for [DONE] messages)
- Verify API keys in .env file

**Q: Feedback not being processed**

- Ensure feedback is typed while system waits for input
- Valid options: any text (triggers analysis) or "approve"

**Q: Reports not saving**

- Check if `reports/` directory has write permissions
- Verify disk space is available

### Debug Tips

- Check output labels (`[ERROR]`, `[WARN]`) for issues
- Read draft history to understand revision progress

---

## Project Specifications

### Technologies Used

- **LangGraph**: Multi-agent workflow orchestration
- **LangChain**: LLM integration and tool management
- **OpenRouter**: LLM provider (cost-effective)
- **Tavily**: Web search for research data

### Design Patterns

- **State Machine**: LangGraph StateGraph with conditional edges
- **Multi-Agent**: Specialized agents for different tasks
- **Tool Use**: Integration with external APIs and search engines
- **Human-in-the-Loop**: Interactive feedback integration

### Key Implementations

- ✅ Automatic task decomposition
- ✅ Parallel research execution
- ✅ Intelligent feedback routing
- ✅ Dynamic report generation
- ✅ Complete conversation history
- ✅ Persistent report storage
- ✅ Clean, structured output

---

## License

© 2026 Multi-Agent Research System. All rights reserved.

---

## Contact & Support

For issues, questions, or contributions, please refer to the documentation or contact the development team.
