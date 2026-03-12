#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point: Run multiagent research workflow
"""

from src.workflow import graph
from src.state import ResearchState


def print_section(title: str):
    """Print section separator"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def run_workflow_with_hitl(query: str):
    """Run workflow with human-in-the-loop feedback"""
    
    # Initialize state
    state: ResearchState = {
        "query": query,
        "plan": [],
        "completed_tasks": [],
        "research_data": {},
        "draft": "",
        "feedback": "",
        "revision_count": 0,
        "draft_history": [],  # Initialize revision history
        "refined_feedback": "",  # Initialize refined feedback
        "feedback_target_agent": None,  # Initialize feedback target agent
        "feedback_analysis_reason": "",  # Initialize feedback analysis reason
    }
    
    print_section("[START] Starting Research Workflow")
    print(f"[TOPIC] Research Topic: {query}\n")
    
    # Run workflow with human-in-the-loop feedback
    iteration = 0
    max_iterations = 5
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n{'-' * 60}")
        print(f"Iteration #{iteration}")
        print(f"{'-' * 60}")
        
        # Rule-based check: if feedback is "approve", directly end (skip workflow)
        feedback_lower = state.get("feedback", "").lower().strip()
        if feedback_lower == "approve":
            print("[ROUTER] Rule-based decision: Feedback is 'approve', ending workflow")
            print("[COMPLETE] Process Completed!")
            break
        
        # Invoke workflow
        result = graph.invoke(state, config={"recursion_limit": 50})
        state.update(result)
        
        # Check if completed (feedback_target_agent == "end")
        if state.get("feedback_target_agent") == "end":
            print("[COMPLETE] Process Completed!")
            break
        
        # Check if reached human review stage
        # Condition: has draft + no feedback + no feedback analysis result
        if state.get("draft") and not state.get("feedback") and not state.get("feedback_target_agent"):
            # Draft generated, needs human review
            print_section("[REVIEW] Entering Human Review Stage (Human-in-the-Loop)")
            print("\n[REPORT] Generated Report Draft:")
            print("-" * 60)
            print(state["draft"])
            print("-" * 60)
            
            # Get real user feedback
            feedback = get_user_feedback()
            print(f"\n[FEEDBACK] User Feedback: {feedback}")
            
            # Update feedback to state (handled uniformly by feedback_analyzer in workflow)
            state["feedback"] = feedback
            state["refined_feedback"] = ""  # Clear refined feedback for feedback_analyzer to re-analyze
            state["feedback_target_agent"] = None  # Clear target agent
            state["feedback_analysis_reason"] = ""  # Clear analysis reason
            state["revision_count"] = state.get("revision_count", 0) + 1
            
            # All feedback handled by workflow
            print("\n[PROCESS] Processing Feedback...")
            continue
    
    # Output final results
    print_section("[DONE] Workflow Completed")
    
    # Save final report to file
    save_report_to_file(state)
    
    # Display revision history
    draft_history = state.get("draft_history", [])
    if draft_history:
        print("\n[HISTORY] Report Revision History:")
        print("-" * 60)
        for i, history_item in enumerate(draft_history, 1):
            revision = history_item.get("revision", i)
            feedback = history_item.get("feedback", "Unknown feedback")
            print(f"\nVersion {revision} (Feedback: {feedback}):")
            print("-" * 40)
            draft_content = history_item.get("draft", "")
            # Display first 200 chars as preview
            preview = draft_content[:200] + "..." if len(draft_content) > 200 else draft_content
            print(preview)
    
    print("\n" + "-" * 60)
    print(f"\n[FINAL] Final Report\n")
    print(state.get("draft", "[]"))
    print(f"\n[STATS] Statistics:")
    print(f"  - Planned Tasks: {len(state.get('plan', []))}")
    print(f"  - Completed Tasks: {len(state.get('completed_tasks', []))}")
    print(f"  - Data Sources: {len(state.get('research_data', {}))}")
    print(f"  - Review Rounds: {state.get('revision_count', 0)}")
    print(f"  - Revision Versions: {len(draft_history)}")
    print(f"  - Process Iterations: {iteration}")
    
    # Display research data
    research_data = state.get("research_data", {})
    if research_data:
        print(f"\n[SOURCES] Research Data Summary:")
        print("-" * 60)
        for idx, (task, data) in enumerate(research_data.items(), 1):
            print(f"\n{idx}. [TASK] {task}")
            print("-" * 40)
            # Display first 300 chars as preview
            preview = data[:300] + "..." if len(data) > 300 else data
            print(preview)
    
    # Display feedback analysis info
    analysis_reason = state.get("feedback_analysis_reason", "")
    if analysis_reason:
        print(f"\n[ANALYSIS] Last Feedback Analysis:")
        print(f"  - Analysis Reason: {analysis_reason}")


def save_report_to_file(state: ResearchState) -> None:
    """Save final report to file"""
    import os
    from datetime import datetime
    
    # Create output directory if not exists
    output_dir = "reports"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = os.path.join(output_dir, f"report_{timestamp}.md")
    
    # Save main report
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(state.get("draft", ""))
    
    print(f"\n[SAVED] Report saved to: {report_filename}")
    return


def get_user_feedback() -> str:
    """Get real user feedback from input"""
    print("\n" + "=" * 60)
    print("Please provide your feedback (or type 'approve' to finish):")
    print("=" * 60)
    feedback = input(">> ").strip()
    return feedback


def main():
    """Main function"""
    # Get research query from user input
    print("\n" + "=" * 60)
    print("Welcome to Multi-Agent Research System")
    print("=" * 60)
    research_query = input("\nEnter your research query: ").strip()
    
    if not research_query:
        print("Error: Research query cannot be empty!")
        return
    
    # Run workflow
    run_workflow_with_hitl(research_query)


if __name__ == "__main__":
    main()
