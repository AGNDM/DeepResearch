from langgraph.graph import StateGraph, START, END
from src.state import ResearchState
from src.agents.planner import llm_planner


def mock_researcher(state: ResearchState, task_index: int = None) -> dict:
    """执行研究任务并收集数据
    
    Args:
        state: 当前状态
        task_index: 任务索引，用于并行处理不同任务
    """
    plan = state.get("plan", [])
    
    # 如果指定了任务索引，执行该任务；否则执行下一个未完成的任务
    if task_index is not None and task_index < len(plan):
        current_task = plan[task_index]
        researcher_id = f"Researcher-{task_index + 1}"
    else:
        completed = state.get("completed_tasks", [])
        if len(completed) < len(plan):
            task_index = len(completed)
            current_task = plan[task_index]
            researcher_id = f"Researcher-{task_index + 1}"
        else:
            return {}
    
    print(f"\n🤖 {researcher_id}: 正在检索资料...")
    print(f"   🔍 执行任务: {current_task}")
    
    return {
        "completed_tasks": [current_task],
        "research_data": {current_task: f"[{researcher_id}搜到的关于该任务的总结资料]"}
    }


def mock_researcher_parallel(state: ResearchState) -> dict:
    """并行执行所有未完成的任务"""
    plan = state.get("plan", [])
    completed = state.get("completed_tasks", [])
    
    remaining_indices = list(range(len(completed), min(len(completed) + 3, len(plan))))
    if not remaining_indices:
        return {}
    
    print(f"\n🚀 并行 Researchers: 同时处理 {len(remaining_indices)} 个任务...")
    
    # 并行收集所有任务的结果
    all_completed_tasks = []
    all_research_data = {}
    
    for i, task_idx in enumerate(remaining_indices):
        task = plan[task_idx]
        researcher_id = f"Researcher-{task_idx + 1}"
        print(f"   ⚡ {researcher_id}: 🔍 执行任务: {task}")
        
        all_completed_tasks.append(task)
        all_research_data[task] = f"[{researcher_id}搜到的关于该任务的总结资料]"
    
    return {
        "completed_tasks": all_completed_tasks,
        "research_data": all_research_data
    }


def mock_reporter(state: ResearchState) -> dict:
    """生成报告草稿"""
    print("\n🤖 Reporter: 正在撰写报告草稿...")
    research_data = state.get("research_data", {})
    feedback = state.get("feedback", "")
    previous_draft = state.get("draft", "")
    revision_count = state.get("revision_count", 0)
    draft_history = state.get("draft_history", [])
    num_sources = len(research_data)
    
    # 在生成新草稿前，保存旧草稿到历史
    if previous_draft:
        draft_history.append({
            "revision": revision_count,
            "draft": previous_draft,
            "feedback": feedback or "初稿"
        })
        print(f"   💾 已保存第 {revision_count} 版本到历史")
    
    draft = f"# 研究报告\n\n## 摘要\n这是基于 {num_sources} 份资料写的草稿。\n\n## 主要发现\n\n"
    for task, data in research_data.items():
        draft += f"### {task}\n{data}\n\n"
    
    print(f"   📝 草稿已生成 ({num_sources} 个数据源)")
    
    # 如果用户给了反馈（要求修改），清除反馈以触发下一轮人工审核
    result = {
        "draft": draft,
        "draft_history": draft_history  # 返回更新后的历史
    }
    if feedback:
        result["feedback"] = ""  # 清除反馈以触发下一轮 HITL
    
    return result


def coordinator_router(state: ResearchState):
    """协调器：根据状态决定下一步操作"""
    plan = state.get("plan", [])
    completed = state.get("completed_tasks", [])
    draft = state.get("draft", "")
    feedback = state.get("feedback", "")

    print("\n📍 Coordinator Router 决策:")
    feedback_preview = feedback[:30] + "..." if len(feedback) > 30 else feedback
    print(f"   当前状态: plan={len(plan)}, completed={len(completed)}, feedback='{feedback_preview}', draft={'有' if draft else '无'}")
    
    # 优先级 1: 如果审核通过，结束
    if feedback == "approve":
        print("   → 决定: 审核通过 ✓，结束流程")
        return END
    
    # 优先级 2: 无计划→规划
    if not plan:
        print("   → 决定: 未制定计划，转向 Planner")
        return "planner"
    
    # 优先级 3: 有未完成任务→并行研究
    if len(completed) < len(plan):
        remaining = len(plan) - len(completed)
        print(f"   → 决定: 还有 {remaining} 个任务，转向并行研究处理")
        return "research_parallel"
    
    # 优先级 4: 任务全部完成后才检查反馈
    if feedback and "补充" in feedback:
        print(f"   → 决定: 反馈请求补充资料，转向 Reporter 用新数据重写")
        return "reporter"
    
    # 优先级 5: 有其他反馈，不需要补充资料 -> 只需修改内容
    if feedback and feedback != "approve":
        print(f"   → 决定: 反馈仅需修改内容，转向 Reporter")
        return "reporter"
    
    # 优先级 6: 任务完成但无草稿→报告
    if not draft:
        print(f"   → 决定: 任务全部完成，但草稿未生成，转向 Reporter")
        return "reporter"
    
    # 优先级 7: 默认结束（任务完成+草稿已生成+无反馈）→等待人工审核
    print("   → 决定: 进入人工审核阶段，结束自动流程")
    return END


def build_graph() -> StateGraph:
    """构建 Langgraph StateGraph，支持并行处理多个任务"""
    workflow = StateGraph(ResearchState)
    
    # 添加节点
    workflow.add_node("planner", llm_planner)
    workflow.add_node("research_parallel", mock_researcher_parallel)  # 并行处理多个任务
    workflow.add_node("reporter", mock_reporter)
    
    # 从 START 开始，路由到第一个适当的节点
    workflow.add_conditional_edges(
        START,
        coordinator_router,
        {
            "planner": "planner",
            "research_parallel": "research_parallel",
            "reporter": "reporter",
            END: END,
        }
    )
    
    # Planner 执行后回到路由器
    workflow.add_conditional_edges(
        "planner",
        coordinator_router,
        {
            "planner": "planner",
            "research_parallel": "research_parallel",
            "reporter": "reporter",
            END: END,
        }
    )
    
    # research_parallel 执行后回到路由器
    workflow.add_conditional_edges(
        "research_parallel",
        coordinator_router,
        {
            "planner": "planner",
            "research_parallel": "research_parallel",
            "reporter": "reporter",
            END: END,
        }
    )
    
    # Reporter 执行后回到路由器
    workflow.add_conditional_edges(
        "reporter",
        coordinator_router,
        {
            "planner": "planner",
            "research_parallel": "research_parallel",
            "reporter": "reporter",
            END: END,
        }
    )
    
    return workflow.compile()


# 导出编译后的图
graph = build_graph()