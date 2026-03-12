# Multi-Agent Research System

A LangGraph-based multi-agent research workflow that breaks down research queries, conducts research, generates reports, and refines them based on human feedback.

## Features

- **Planner Agent**: Decomposes research queries into actionable tasks
- **Researcher Agent**: Executes tasks using web search and APIs
- **Reporter Agent**: Synthesizes findings into markdown reports
- **Feedback Analyzer**: Routes user feedback to appropriate agents
- **Human-in-the-Loop**: Iterative refinement through feedback

## Installation

Choose one of the two methods below:

### Method 1: Using pip

Install directly from GitHub Release:

```bash
pip install https://github.com/AGNDM/DeepResearch/releases/download/v0.1.0/multiagent_llm-0.1.0-py3-none-any.whl
```

### Method 2: Clone from Source

Clone the repository and install from source:

```bash
# Clone the repository
git clone https://github.com/AGNDM/DeepResearch.git
cd DeepResearch

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

After installation, configure your API keys:

### 1. Create `.env` file

```bash
cp .env.example .env
```

### 2. Get your API keys

You need API keys from two services:

**LLM Provider**(Example):

- [OpenRouter](https://openrouter.ai)
- [OpenAI](https://platform.openai.com/api-keys)

**Search API**:

- [Tavily](https://tavily.com) - Web search capabilities

### 3. Edit `.env` file

```bash
LLM_API_KEY=sk-or-v1-xxxxxxxxxxxx        # Your LLM API key
LLM_BASE_URL=https://openrouter.ai/api/v1 # API endpoint
LLM_MODEL=stepfun/step-3.5-flash:free     # Model name
TAVILY_API_KEY=tvly-xxxxxxxxxxxx         # Your Tavily API key
```

## Quick Start

After completing the configuration above, run the system:

**If you used `pip install` (Method 1):**

```bash
python3 main.py
```

**If you cloned from source (Method 2):**

```bash
# Activate virtual environment first
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Then run
python3 main.py
```

You'll be prompted to enter a research query, and the system will generate a report with feedback refinement.

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
├── pyproject.toml          # Project metadata (for packaging)
├── setup.py                # Setup script (for compatibility)
├── requirements.txt        # Dependencies
├── .env.example            # Environment variables template
├── LICENSE                 # MIT License
├── README.md              # This file
├── reports/               # Generated reports (auto-created)
├── dist/                  # Built packages (.whl, .tar.gz)
└── src/
    ├── __init__.py        # Package initialization
    ├── state.py           # ResearchState definition
    ├── prompts.py         # LLM prompts
    ├── tools.py           # Tool configurations
    ├── workflow.py        # LangGraph workflow
    └── agents/
        ├── __init__.py
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
