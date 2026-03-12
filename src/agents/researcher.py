from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from src.state import ResearchState
from src.prompts import RESEARCHER_SYSTEM_MESSAGE, RESEARCHER_HUMAN_MESSAGE
from src.tools import research_tools
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM for researcher
_llm_researcher = ChatOpenAI(
    model="stepfun/step-3.5-flash:free",
    api_key=os.getenv("LLM_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0.2
)

# Bind tools to the LLM
_llm_with_tools = _llm_researcher.bind_tools(research_tools)


def llm_researcher(state: ResearchState) -> dict:
    """Execute research tasks using LLM and tools"""
    print("\n[Researcher] Starting research with tools...")
    
    plan = state.get("plan", [])
    completed_tasks = state.get("completed_tasks", [])
    research_data = state.get("research_data", {})
    
    # Determine which tasks to process (next 3 uncompleted tasks)
    remaining_tasks = [task for task in plan if task not in completed_tasks]
    tasks_to_process = remaining_tasks[:3]
    
    if not tasks_to_process:
        print("   [WARN] No tasks to process")
        return {}
    
    print(f"   [PLAN] Preparing to process {len(tasks_to_process)} tasks")
    
    newly_completed = []
    newly_gathered_data = {}
    
    for idx, task in enumerate(tasks_to_process, 1):
        try:
            task_num = len(completed_tasks) + idx
            researcher_id = f"Researcher-{task_num}"
            print(f"   [EXEC] {researcher_id}: Executing task: {task[:60]}...")
            
            # Prepare the research query
            research_query = RESEARCHER_HUMAN_MESSAGE.format(current_task=task)
            
            # Create messages for the LLM with tool calling
            messages = [
                SystemMessage(content=RESEARCHER_SYSTEM_MESSAGE),
                HumanMessage(content=research_query)
            ]
            
            # Call the LLM with tools
            response = _llm_with_tools.invoke(messages)
            
            # Debug: Check if tools were called
            if hasattr(response, 'tool_calls') and response.tool_calls:
                print(f"      [TOOLS] Tool calls detected: {len(response.tool_calls)}")
                for tool_call in response.tool_calls:
                    tool_name = tool_call.get('name', 'unknown')
                    tool_args = tool_call.get('args', {})
                    print(f"         [TOOL] Tool: {tool_name}")
                    print(f"            Args: {json.dumps(tool_args, ensure_ascii=False)[:100]}...")
            
            # Extract the response content
            if hasattr(response, 'content') and response.content:
                output = response.content
            elif hasattr(response, 'tool_calls'):
                # If tool calls were made, collect the call information
                output = f"Used {len(response.tool_calls)} tools: {[tc.get('name', 'unknown') for tc in response.tool_calls]}"
            else:
                output = str(response)
            
            # Store the research data
            data_summary = output[:200] if len(output) > 200 else output
            newly_gathered_data[task] = f"[{researcher_id}] {data_summary}..."
            print(f"      [OK] Data collected (length: {len(output)} chars)")
            
            newly_completed.append(task)
            
        except Exception as e:
            print(f"      [ERROR] Error during research: {str(e)}")
            newly_gathered_data[task] = f"[{researcher_id}] Research execution error: {str(e)[:100]}"
            newly_completed.append(task)
    
    result_dict = {}
    # Return accumulated completed_tasks (existing + newly completed)
    if newly_completed:
        accumulated_completed = completed_tasks + newly_completed
        result_dict["completed_tasks"] = accumulated_completed
    if newly_gathered_data:
        result_dict["research_data"] = newly_gathered_data
    
    # Clear feedback processing fields (NOT refined_feedback - let reporter use it)
    result_dict["feedback_target_agent"] = None
    result_dict["feedback_analysis_reason"] = ""
    # Note: DO NOT clear refined_feedback or feedback
    
    if newly_completed:
        print(f"   [DONE] {len(newly_completed)} tasks completed")
    
    return result_dict
