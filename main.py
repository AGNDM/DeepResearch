#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序：运行多代理研究工作流
"""

from src.workflow import graph
from src.state import ResearchState


def print_section(title: str):
    """打印分隔符"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def run_workflow_with_hitl(query: str):
    """运行工作流并模拟人类反馈循环"""
    
    # 初始化状态
    state: ResearchState = {
        "query": query,
        "plan": [],
        "completed_tasks": [],
        "research_data": {},
        "draft": "",
        "feedback": "",
        "revision_count": 0,
        "draft_history": [],  # 初始化修改历史
    }
    
    print_section("🚀 开始研究工作流")
    print(f"📌 研究主题: {query}\n")
    
    # 运行工作流（带人工反馈循环）
    iteration = 0
    max_iterations = 5
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n{'─' * 60}")
        print(f"循环 #{iteration}")
        print(f"{'─' * 60}")
        
        # 调用图（仅当未得到 "approve" 反馈时）
        result = graph.invoke(state, config={"recursion_limit": 50})
        state.update(result)
        
        # 检查是否到达人工审核阶段
        # 条件：有草稿且无反馈，或反馈是修改意见（需要再次调整）
        if state.get("draft") and not state.get("feedback"):
            # 生成了草稿，需要人工审核
            print_section("👤 进入人工审核阶段 (Human-in-the-Loop)")
            print("\n📄 生成的报告草稿:")
            print("─" * 60)
            print(state["draft"])
            print("─" * 60)
            
            # 模拟用户反馈
            feedback = simulate_user_feedback(state.get("revision_count", 0))
            print(f"\n👤 用户反馈: {feedback}")
            
            # 更新反馈到状态
            state["feedback"] = feedback
            state["revision_count"] = state.get("revision_count", 0) + 1
            
            # 如果用户要求补充资料，清除已完成的任务以便重新研究
            if "补充" in feedback:
                state["completed_tasks"] = []  # 清除已完成任务，重新研究
                print("   📋 已清除已完成任务列表，准备重新执行研究...")
            
            # 如果用户批准，下一次循环会在 router 逻辑中返回 END
            if feedback == "approve":
                print("\n✅ 用户已批准，处理中...")
                # 再执行一次以便根据新的 feedback 做决策
                result = graph.invoke(state, config={"recursion_limit": 50})
                state.update(result)
                break
            else:
                # 用户给出修改意见，继续循环让 router 决定下一步
                print("\n🔄 根据反馈继续调整...")
                continue
        
        # 检查是否已完成（feedback == "approve"）
        if state.get("feedback") == "approve":
            print("✅ 流程已完成！")
            break
    
    # 输出最终结果
    print_section("✅ 工作流完成")
    
    # 显示修改历史
    draft_history = state.get("draft_history", [])
    if draft_history:
        print("\n📖 报告修改历史:")
        print("─" * 60)
        for i, history_item in enumerate(draft_history, 1):
            revision = history_item.get("revision", i)
            feedback = history_item.get("feedback", "未知反馈")
            print(f"\n第 {revision} 版本 (反馈: {feedback}):")
            print("─" * 40)
            draft_content = history_item.get("draft", "")
            # 显示前200个字符作为预览
            preview = draft_content[:200] + "..." if len(draft_content) > 200 else draft_content
            print(preview)
    
    print("\n" + "─" * 60)
    print(f"\n🎯 最终报告 (第 {state.get('revision_count', 0)} 版本):\n")
    print(state.get("draft", "[无草稿]"))
    print(f"\n📊 统计信息:")
    print(f"  - 计划任务数: {len(state.get('plan', []))}")
    print(f"  - 完成任务数: {len(state.get('completed_tasks', []))}")
    print(f"  - 数据源数: {len(state.get('research_data', {}))}")
    print(f"  - 审核轮次: {state.get('revision_count', 0)}")
    print(f"  - 修改版本数: {len(draft_history)}")
    print(f"  - 流程循环数: {iteration}")


def simulate_user_feedback(revision_count: int) -> str:
    """模拟用户反馈（实际应用中应改为真实用户输入）"""
    
    if revision_count == 0:
        # 第一次审核：要求补充资料
        return "这个报告不错，但需要补充更多背景信息。请修改并补充。"
    elif revision_count == 1:
        # 第二次审核：只需要重写部分内容
        return "更好了。请改进摘要部分的表述。"
    else:
        # 第三次及以后：通过审核
        return "approve"


def main():
    """主函数"""
    # 测试查询
    test_query = "人工智能在医疗领域的应用"
    
    # 运行工作流
    run_workflow_with_hitl(test_query)


if __name__ == "__main__":
    main()
