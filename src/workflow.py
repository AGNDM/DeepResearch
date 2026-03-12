from langgraph.graph import StateGraph, START, END
from src.state import ResearchState
from src.agents.planner import llm_planner
from src.agents.researcher import llm_researcher
from src.agents.reporter import llm_reporter
from src.agents.feedback_analyzer import llm_feedback_analyzer


def coordinator_router(state: ResearchState):
    """Coordinator: Decide next action based on state"""
    plan = state.get("plan", [])
    completed = state.get("completed_tasks", [])
    draft = state.get("draft", "")
    feedback = state.get("feedback", "")
    refined_feedback = state.get("refined_feedback", "")
    feedback_target_agent = state.get("feedback_target_agent")

    print("\n[ROUTER] Coordinator Router Decision:")
    feedback_preview = refined_feedback[:30] + "..." if len(refined_feedback) > 30 else refined_feedback
    if not feedback_preview:
        feedback_preview = feedback[:30] + "..." if len(feedback) > 30 else feedback
    print(f"   Current state: plan={len(plan)}, completed={len(completed)}, feedback='{feedback_preview}', draft={'yes' if draft else 'no'}")
    
    # Priority 0: Rule-based check - if feedback is exactly "approve", direct route to END (skip LLM analysis)
    feedback_lower = feedback.lower().strip()
    if feedback_lower == "approve":
        print(f"   [ROUTE] Decision: Feedback is 'approve' (rule-based), direct route to END without LLM analysis")
        return END
    
    # Priority 1: If there's raw feedback but not yet analyzed, route to feedback_analyzer
    if feedback and not feedback_target_agent and not refined_feedback:
        print(f"   [ROUTE] Decision: New feedback needs analysis, routing to Feedback Analyzer")
        return "feedback_analyzer"
    
    # Priority 2: Use feedback analysis result to decide target agent
    if feedback_target_agent:
        print(f"   [ROUTE] Decision: Based on feedback analysis, routing to {feedback_target_agent.upper()}")
        return feedback_target_agent if feedback_target_agent != "end" else END
    
    # Priority 3: If approved (from refined feedback), end
    refined_feedback_lower = refined_feedback.lower()
    if "approve" in refined_feedback_lower or refined_feedback_lower == "approve":
        print("   [ROUTE] Decision: Approved, process complete")
        return END
    
    # Priority 4: No plan → planner
    if not plan:
        print("   [ROUTE] Decision: No plan yet, routing to Planner")
        return "planner"
    
    # Priority 5: Incomplete tasks → parallel research
    if len(completed) < len(plan):
        remaining = len(plan) - len(completed)
        print(f"   [ROUTE] Decision: {remaining} tasks remaining, routing to parallel research")
        return "research_parallel"
    
    # Priority 6: All tasks complete but no draft → reporter
    if not draft:
        print(f"   [ROUTE] Decision: All tasks complete but no draft, routing to Reporter")
        return "reporter"
    
    # Priority 7: Default complete (tasks done + draft exists + no feedback) → await human review
    print("   [ROUTE] Decision: Enter human review stage, ending auto process")
    return END


def build_graph() -> StateGraph:
    """Build Langgraph StateGraph supporting parallel task processing"""
    workflow = StateGraph(ResearchState)
    
    # Add nodes
    workflow.add_node("planner", llm_planner)
    workflow.add_node("research_parallel", llm_researcher)  # Use LLM researcher to process tasks
    workflow.add_node("reporter", llm_reporter)  # Use LLM reporter to generate report
    workflow.add_node("feedback_analyzer", llm_feedback_analyzer)  # Human feedback analysis and refinement
    
    # From START, route to first appropriate node
    workflow.add_conditional_edges(
        START,
        coordinator_router,
        {
            "planner": "planner",
            "research_parallel": "research_parallel",
            "reporter": "reporter",
            "feedback_analyzer": "feedback_analyzer",
            END: END,
        }
    )
    
    # After planner execution, back to coordinator
    workflow.add_conditional_edges(
        "planner",
        coordinator_router,
        {
            "planner": "planner",
            "research_parallel": "research_parallel",
            "reporter": "reporter",
            "feedback_analyzer": "feedback_analyzer",
            END: END,
        }
    )
    
    # After research_parallel execution, back to coordinator
    workflow.add_conditional_edges(
        "research_parallel",
        coordinator_router,
        {
            "planner": "planner",
            "research_parallel": "research_parallel",
            "reporter": "reporter",
            "feedback_analyzer": "feedback_analyzer",
            END: END,
        }
    )
    
    # After reporter execution, back to coordinator (coordinator_router checks for new feedback)
    workflow.add_conditional_edges(
        "reporter",
        coordinator_router,
        {
            "planner": "planner",
            "research_parallel": "research_parallel",
            "reporter": "reporter",
            "feedback_analyzer": "feedback_analyzer",
            END: END,
        }
    )
    
    # After feedback_analyzer execution, back to coordinator
    workflow.add_conditional_edges(
        "feedback_analyzer",
        coordinator_router,
        {
            "planner": "planner",
            "research_parallel": "research_parallel",
            "reporter": "reporter",
            "feedback_analyzer": "feedback_analyzer",
            END: END,
        }
    )
    
    return workflow.compile()


# Export compiled graph
graph = build_graph()