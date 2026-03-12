from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from src.state import ResearchState
from src.prompts import (
    PLANNER_SYSTEM_MESSAGE, 
    PLANNER_HUMAN_MESSAGE,
    PLANNER_HUMAN_MESSAGE_WITH_FEEDBACK
)
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM for planner
_llm_planner = ChatOpenAI(
    model=os.getenv("LLM_MODEL", "stepfun/step-3.5-flash:free"),
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1"),
    temperature=0.2
)


def llm_planner(state: ResearchState) -> dict:
    """Use LLM to generate research plan"""
    print("\n[Planner] Generating plan...")
    query = state.get("query", "")
    refined_feedback = state.get("refined_feedback", "")
    
    # Choose appropriate prompt template based on whether there's feedback
    if refined_feedback:
        planner_prompt = PLANNER_HUMAN_MESSAGE_WITH_FEEDBACK.format(
            query=query,
            refined_feedback=refined_feedback
        )
        print(f"   [FEEDBACK] Incorporating user feedback into planning...")
    else:
        planner_prompt = PLANNER_HUMAN_MESSAGE.format(query=query)
    
    # Create structured messages with system and human roles
    messages = [
        SystemMessage(content=PLANNER_SYSTEM_MESSAGE),
        HumanMessage(content=planner_prompt)
    ]
    
    try:
        response = _llm_planner.invoke(messages)
        response_text = response.content.strip()
        
        # Try to parse JSON from response
        try:
            # Handle case where response might have markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            plan = result.get("tasks", [])
            
            if not isinstance(plan, list) or len(plan) == 0:
                raise ValueError("Invalid plan format")
                
        except (json.JSONDecodeError, ValueError, IndexError):
            # Fallback: try to extract tasks line by line
            plan = [line.strip() for line in response_text.split('\n') 
                   if line.strip() and not line.strip().startswith('{') and not line.strip().startswith('}')]
            if not plan:
                # Ultimate fallback
                plan = ["Task 1: Gather background information", "Task 2: Search recent research", "Task 3: Identify applications"]
        
        print(f"   [TASKS] Generated tasks: {plan}")
        return {
            "plan": plan,
            "completed_tasks": [],
            "research_data": {},  # Clear old research data to enable fresh research on new tasks
            "draft": "",  # Clear old draft to prepare for new report generation
            # DO NOT clear refined_feedback - let reporter and others use it too
            "feedback_target_agent": None,  # Clear feedback target agent after execution
            "feedback_analysis_reason": ""  # Clear analysis reason
        }
        
    except Exception as e:
        print(f"   [ERROR] LLM call error: {str(e)}, using fallback plan")
        # Fallback to mock plan if LLM fails
        plan = ["Task 1: Gather background information", "Task 2: Search recent research", "Task 3: Identify applications"]
        print(f"   [FALLBACK] Fallback tasks: {plan}")
        return {
            "plan": plan,
            "completed_tasks": [],
            "research_data": {},  # Clear old research data to enable fresh research on new tasks
            "draft": "",  # Clear old draft to prepare for new report generation
            # DO NOT clear refined_feedback - let reporter and others use it too
            "feedback_target_agent": None,
            "feedback_analysis_reason": ""
            # Note: DO NOT clear "feedback" - let reporter preserve user feedback
        }
