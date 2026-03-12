# Multi-Agent Research System

A LangGraph-based multi-agent research workflow that breaks down research queries, conducts research, generates reports, and refines them based on human feedback.

## Features

- **Planner Agent**: Decomposes research queries into actionable tasks
- **Researcher Agent**: Executes tasks using web search and APIs
- **Reporter Agent**: Synthesizes findings into markdown reports
- **Feedback Analyzer**: Routes user feedback to appropriate agents
- **Human-in-the-Loop**: Iterative refinement through feedback

## Quick Start

### Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configuration

Create a `.env` file with your API keys:

```bash
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://openrouter.ai/api/v1  # or your provider
LLM_MODEL=stepfun/step-3.5-flash:free      # or your model
TAVILY_API_KEY=your_tavily_key
```

### Run

```bash
python3 main.py
```

## Workflow

```
User Query
   ↓
[Planner] → Create research plan
   ↓
[Researcher] → Gather data
   ↓
[Reporter] → Generate report
   ↓
[Review] → Provide feedback (or type 'approve')
   ↓
[Route] → Process feedback or finalize
```

## Project Structure

```
MultiagentLLM/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── .env                    # API keys
├── reports/               # Generated reports (auto-created)
└── src/
    ├── state.py           # ResearchState definition
    ├── prompts.py         # LLM prompts
    ├── tools.py           # Tool configurations
    ├── workflow.py        # LangGraph workflow
    └── agents/
        ├── planner.py
        ├── researcher.py
        ├── reporter.py
        └── feedback_analyzer.py
```

## Usage Example

```bash
$ python3 main.py

Enter your research query: Machine Learning in Healthcare

[START] Starting Research Workflow
[PLAN] Creating research plan...
[RESEARCH] Gathering data...
[REPORTER] Generating report...

[FINAL] Final Report
...report content...

Please provide your feedback (or type 'approve'):
>> approve
```

## Feedback Types

- **"approve"** - Finalize the report
- **"..."** - Any other text triggers feedback analysis and processing

## Report Output

Reports are saved in: `reports/report_YYYYMMDD_HHMMSS/`

- `final_report.md` - Final report
- `drafts/` - All intermediate versions
