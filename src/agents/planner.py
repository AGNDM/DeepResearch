from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from src.state import ResearchState
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM for planner
_llm_planner = ChatOpenAI(
    model="stepfun/step-3.5-flash:free",
    api_key=os.getenv("LLM_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0.2
)


def llm_planner(state: ResearchState) -> dict:
    """使用LLM生成研究计划"""
    print("\n🤖 Planner (LLM): 正在生成计划...")
    query = state.get("query", "")
    
    prompt = f"""You are an expert research planner. Based on the research query below, break it down into 3-5 specific research tasks that would help answer the query comprehensively.

Query: {query}

Please respond with a JSON object containing a "tasks" key with a list of task strings. Each task should be specific and actionable.
Example format:
{{"tasks": ["Task 1: Find background information", "Task 2: Search recent papers", "Task 3: Analyze applications"]}}

Respond ONLY with valid JSON, no additional text."""
    
    try:
        response = _llm_planner.invoke([HumanMessage(content=prompt)])
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
                plan = ["任务1：查背景", "任务2：查最新论文", "任务3：查临床应用"]
        
        print(f"   📋 生成的任务: {plan}")
        return {"plan": plan}
        
    except Exception as e:
        print(f"   ⚠️  LLM调用出错: {str(e)}, 使用备用计划")
        # Fallback to mock plan if LLM fails
        plan = ["Task 1: Gather background information", "Task 2: Search recent research", "Task 3: Identify applications"]
        print(f"   📋 备用任务: {plan}")
        return {"plan": plan}
