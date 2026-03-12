from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from src.state import ResearchState
from src.prompts import (
    REPORTER_SYSTEM_MESSAGE,
    REPORTER_HUMAN_MESSAGE,
    REPORTER_HUMAN_MESSAGE_REVISE_WITH_FEEDBACK,
    REPORTER_HUMAN_MESSAGE_WITH_FEEDBACK,
    REPORTER_HUMAN_MESSAGE_NEW_DATA
)
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM for reporter
_llm_reporter = ChatOpenAI(
    model="stepfun/step-3.5-flash:free",
    api_key=os.getenv("LLM_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0.3  # Slightly higher for more creative report writing
)


def llm_reporter(state: ResearchState) -> dict:
    """Generate research report using LLM"""
    print("\n[Reporter] Generating report draft...")
    
    research_data = state.get("research_data", {})
    feedback = state.get("feedback", "")
    refined_feedback = state.get("refined_feedback", "")
    previous_draft = state.get("draft", "")
    revision_count = state.get("revision_count", 0)
    draft_history = state.get("draft_history", [])
    query = state.get("query", "")
    
    # Extract data summary for the prompt
    data_summary = ""
    for idx, (task, data) in enumerate(research_data.items(), 1):
        data_summary += f"{idx}. **{task}**\n   {data}\n\n"
    
    if not data_summary:
        data_summary = "No research data available yet."
    
    # Save previous draft to history if it exists
    if previous_draft:
        draft_history.append({
            "revision": revision_count,
            "draft": previous_draft,
            "feedback": feedback or "Initial draft"
        })
        print(f"   [Saved] Version {revision_count} saved to history")
    
    # Choose appropriate prompt template based on context
    if previous_draft and refined_feedback:
        # Revision scenario: have old draft and user feedback
        reporter_prompt = REPORTER_HUMAN_MESSAGE_REVISE_WITH_FEEDBACK.format(
            query=query,
            research_data=data_summary,
            previous_draft=previous_draft,
            refined_feedback=refined_feedback
        )
    elif refined_feedback:
        # New report with feedback (no previous draft)
        reporter_prompt = REPORTER_HUMAN_MESSAGE_WITH_FEEDBACK.format(
            query=query,
            research_data=data_summary,
            refined_feedback=refined_feedback
        )
    elif previous_draft:
        # Regenerate with new data but no specific feedback
        reporter_prompt = REPORTER_HUMAN_MESSAGE_NEW_DATA.format(
            query=query,
            research_data=data_summary,
            previous_draft=previous_draft
        )
    else:
        # Initial report generation
        reporter_prompt = REPORTER_HUMAN_MESSAGE.format(
            query=query,
            research_data=data_summary
        )
    
    # Create messages for the LLM
    messages = [
        SystemMessage(content=REPORTER_SYSTEM_MESSAGE),
        HumanMessage(content=reporter_prompt)
    ]
    
    try:
        # Call the LLM
        response = _llm_reporter.invoke(messages)
        
        # Extract the draft content
        draft = ""
        if hasattr(response, 'content') and response.content:
            draft = response.content
        else:
            draft = str(response)
        
        print(f"   [Generated] Draft created ({len(research_data)} data sources)")
        
    except Exception as e:
        print(f"   [Error] Report generation failed: {str(e)}")
        # Fallback to simple report if LLM fails
        draft = f"# Research Report\n\n## Summary\nThis is a draft based on {len(research_data)} sources.\n\n## Key Findings\n\n"
        for task, data in research_data.items():
            draft += f"### {task}\n{data}\n\n"
        draft += "\n## References\nPlease consult the research data above for source information."
    
    # Prepare result
    result = {
        "draft": draft,
        "draft_history": draft_history,
        # Clear feedback fields, let coordinator_router re-evaluate state
        "feedback": "",
        "refined_feedback": "",
        "feedback_target_agent": None,
        "feedback_analysis_reason": ""
    }
    # Note: Do not modify revision_count, managed by main.py's HITL loop
    
    return result
