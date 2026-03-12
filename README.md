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

Install directly from GitHub Release and download main.py:

```bash
pip install https://github.com/AGNDM/DeepResearch/releases/download/v0.1.0/multiagent_llm-0.1.0-py3-none-any.whl

curl -o main.py https://raw.githubusercontent.com/AGNDM/DeepResearch/master/main.py
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

## System Architecture

The system follows a **multi-agent workflow** with intelligent routing and human-in-the-loop feedback:

```
                           ┌─────────────────────────────────────────┐
                           │         USER QUERY INPUT                │
                           └──────────────┬──────────────────────────┘
                                          │
                                          ▼
                        ┌──────────────────────────────────┐
                        │  COORDINATOR ROUTER (Decision)  │
                        │  - Analyzes current state        │
                        │  - Routes to next agent          │
                        └──┬──────────┬──────────┬────────┬┘
                           │          │          │        │
                ┌──────────▼┐  ┌──────▼───┐  ┌──▼──────┐ │
                │  PLANNER  │  │RESEARCHER│  │REPORTER│ │
                ├───────────┤  ├──────────┤  ├────────┤ │
                │ Creates   │  │ Executes │  │Generates│ │
                │ research  │  │ research │  │markdown │ │
                │ plan      │  │ in       │  │report   │ │
                │ (tasks)   │  │parallel  │  │from     │ │
                │           │  │using     │  │research │ │
                │           │  │Tavily &  │  │data     │ │
                │           │  │ArXiv     │  │         │ │
                └───────────┘  └──────────┘  └────────┘ │
                                                         │
                                ┌────────────────────────▼──────┐
                                │   HUMAN REVIEW STAGE          │
                                │ (User views report & feedback)│
                                └────────────┬───────────────────┘
                                             │
                                             ▼
                                    ┌──────────────────┐
                                    │  USER FEEDBACK   │
                                    │ - "approve"      │
                                    │ - specific note  │
                                    └────────┬────────┘
                                             │
                                             ▼
                                ┌────────────────────────────┐
                                │  FEEDBACK ANALYZER         │
                                ├────────────────────────────┤
                                │ Uses LLM to:               │
                                │ 1. Parse feedback intent   │
                                │ 2. Classify feedback type  │
                                │ 3. Route to target agent   │
                                │    (Planner/Researcher/    │
                                │     Reporter/End)          │
                                └────────────┬───────────────┘
                                             │
                    ┌────────────────────────┴────────────────────┐
                    │ Routes back to COORDINATOR ROUTER            │
                    └────────────────────────┬────────────────────┘
                                             │
                    ┌────────────────────────┴────────────────────┐
                    │ Iterative Refinement Loop until approved    │
                    └─────────────────────────────────────────────┘
```

### Agent Roles

| Agent                  | Responsibility                                     | Tools                               |
| ---------------------- | -------------------------------------------------- | ----------------------------------- |
| **Planner**            | Break down research query into actionable tasks    | -                                   |
| **Researcher**         | Execute tasks in parallel, gather information      | Tavily (web search), ArXiv (papers) |
| **Reporter**           | Synthesize research data into markdown report      | -                                   |
| **Feedback Analyzer**  | Parse user feedback and route to appropriate agent | LLM analysis                        |
| **Coordinator Router** | Intelligent state-based routing decisions          | Multi-priority decision tree        |

### Workflow Steps

1. **Initial Planning**: User enters query → Planner creates research plan
2. **Parallel Research**: Researcher executes all tasks simultaneously
3. **Report Generation**: Reporter creates markdown report from findings
4. **Human Review**: User reviews report and provides feedback (or approves)
5. **Feedback Analysis**: Feedback Analyzer determines intent and target agent
6. **Iterative Refinement**: Loop back to step 2 or 3 until user approves
7. **Finalization**: Report is saved to `reports/` directory

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
  - Task 1: Find current applications of ML in healthcare
  - Task 2: Research latest ML models for diagnosis
  - Task 3: Explore ethical considerations

[RESEARCH] Gathering data in parallel...
[REPORTER] Generating report...

[FINAL] Final Report
Generated report with 3 sections...

Please provide your feedback (or type 'approve'):
>>
```

## Feedback & Iterative Refinement

The system supports intelligent feedback routing for iterative improvement:

### Feedback Types

| Feedback               | Behavior                    | Routed To                   |
| ---------------------- | --------------------------- | --------------------------- |
| **`approve`**          | Accept report and finalize  | End (Save report)           |
| **Search/data issues** | "Add more recent papers"    | **Researcher** (re-search)  |
| **Planning issues**    | "Find more on ethics"       | **Planner** (revise plan)   |
| **Report issues**      | "Rewrite the intro section" | **Reporter** (revise draft) |
| **General comment**    | "This looks good but..."    | **Analyzer** (parse intent) |

### Example Feedback Flow

```
User: "Add more on ethical implications"
  ↓
[FEEDBACK ANALYZER] Detects: "add" (search) + "ethical" (topic refinement)
  ↓
Routes to: RESEARCHER (with refined tasks)
  ↓
[RESEARCHER] Executes new search with ethical focus
  ↓
Routes to: REPORTER (with new findings)
  ↓
[REPORTER] Generates updated report
  ↓
Back to: HUMAN REVIEW
```

## Report Output

Reports are saved in: `reports/report_YYYYMMDD_HHMMSS/`

- `final_report.md` - Final report
- `drafts/` - All intermediate versions
