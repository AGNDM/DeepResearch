from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from src.state import ResearchState
from src.prompts import FEEDBACK_ANALYZER_SYSTEM_MESSAGE, FEEDBACK_ANALYZER_HUMAN_MESSAGE
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM for feedback analyzer
_llm_feedback_analyzer = ChatOpenAI(
    model=os.getenv("LLM_MODEL", "stepfun/step-3.5-flash:free"),
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1"),
    temperature=0.2
)


def llm_feedback_analyzer(state: ResearchState) -> dict:
    """Use LLM to analyze human feedback and determine target agent"""
    feedback = state.get("feedback", "")
    
    # If no feedback, return original values
    if not feedback:
        return {
            "refined_feedback": "",
            "feedback_target_agent": None,
            "feedback_analysis_reason": ""
        }
    
    print("\n[Analyzer] Analyzing human feedback...")
    
    query = state.get("query", "")
    draft = state.get("draft", "")
    
    # Create structured messages with system and human roles
    messages = [
        SystemMessage(content=FEEDBACK_ANALYZER_SYSTEM_MESSAGE),
        HumanMessage(content=FEEDBACK_ANALYZER_HUMAN_MESSAGE.format(
            query=query,
            draft=draft,
            feedback=feedback
        ))
    ]
    
    try:
        response = _llm_feedback_analyzer.invoke(messages)
        response_text = response.content.strip()
        
        # Try to parse JSON from response
        try:
            # Handle case where response might have markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            
            target_agent = result.get("target_agent", "reporter")
            refined_feedback = result.get("refined_feedback", feedback)
            reason = result.get("reason", "")
            
            print(f"   [RESULT] Analysis Result: Target={target_agent}, Reason={reason}")
            print(f"   [REFINED] Refined Feedback: {refined_feedback[:80]}..." if len(refined_feedback) > 80 else f"   [REFINED] Refined Feedback: {refined_feedback}")
            
            result_dict = {
                "refined_feedback": refined_feedback,
                "feedback_target_agent": target_agent,
                "feedback_analysis_reason": reason,
                "feedback": ""  # Clear original feedback to avoid re-analysis
            }
            
            # If routing back to planner for re-research, clear completed tasks
            if target_agent == "planner":
                result_dict["completed_tasks"] = []
                print(f"   [CLEAR] Cleared completed tasks, ready for planning stage")
            
            return result_dict
            
        except (json.JSONDecodeError, ValueError, IndexError) as e:
            print(f"   [WARN] JSON parsing failed, using human feedback as refined feedback: {str(e)}")
            
            # Fallback: Use heuristic method to determine target
            feedback_lower = feedback.lower()
            if feedback == "approve":
                target_agent = "end"
            elif any(word in feedback_lower for word in ["supplement", "more", "additional", "add", "extra", "deeper", "research"]):
                target_agent = "planner"
            else:
                target_agent = "reporter"
            
            result_dict = {
                "refined_feedback": feedback,
                "feedback_target_agent": target_agent,
                "feedback_analysis_reason": "Using heuristic rules to analyze feedback",
                "feedback": ""  # Clear original feedback to avoid re-analysis
            }
            
            # If routing back to planner for re-research, clear completed tasks
            if target_agent == "planner":
                result_dict["completed_tasks"] = []
                print(f"   [CLEAR] Cleared completed tasks, ready for planning stage")
            
            return result_dict
    
    except Exception as e:
        print(f"   [ERROR] Feedback Analyzer error: {str(e)}")
        # Fallback: Use heuristic method to determine target
        feedback_lower = feedback.lower()
        if feedback == "approve":
            target_agent = "end"
        elif any(word in feedback_lower for word in ["supplement", "more", "additional", "add", "extra", "deeper", "research"]):
            target_agent = "planner"
        else:
            target_agent = "reporter"
        
        result_dict = {
            "refined_feedback": feedback,
            "feedback_target_agent": target_agent,
            "feedback_analysis_reason": "Using heuristic rules to analyze feedback (exception occurred)",
            "feedback": ""  # Clear original feedback to avoid re-analysis
        }
        
        # If routing back to planner for re-research, clear completed tasks
        if target_agent == "planner":
            result_dict["completed_tasks"] = []
            print(f"   [CLEAR] Cleared completed tasks, ready for planning stage")
        
        return result_dict
