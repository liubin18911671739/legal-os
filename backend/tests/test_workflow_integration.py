"""
Integration test for multi-agent workflow
"""
import pytest
from app.agents import (
    create_contract_analysis_graph,
    create_initial_state,
    ContractType,
    TaskStatus,
)


@pytest.mark.asyncio
async def test_workflow_execution():
    """Test complete workflow execution through graph"""
    graph = create_contract_analysis_graph()
    
    # Create initial state
    state = create_initial_state(
        contract_id="test_contract_001",
        contract_text="""
劳动合同

甲方：北京科技有限公司
乙方：张三

第一条 合同期限
本合同期限为三年，自2024年1月1日起至2027年1月1日止。

第二条 工作内容
乙方担任软件工程师岗位，负责系统开发和维护工作。

第三条 工作时间和休息休假
乙方实行标准工时制，每日工作8小时，每周工作40小时。

第四条 劳动报酬
乙方的月工资为10000元，甲方于每月15日支付上月工资。

第五条 保密义务
乙方应当保守甲方的商业秘密和技术秘密，不得泄露给第三方。

第六条 违约责任
任何一方违反本合同约定，应向对方支付5000元违约金。
""",
        contract_type=ContractType.EMPLOYMENT,
    )
    
    # Execute workflow
    result = await graph.ainvoke(state)
    
    # Verify workflow completed
    assert result["task_status"] == TaskStatus.COMPLETED
    assert result["contract_id"] == "test_contract_001"
    
    # Verify all agents ran
    assert len(result["agent_history"]) == 6
    assert "coordinator" in result["agent_history"]
    assert "retrieval" in result["agent_history"]
    assert "analysis" in result["agent_history"]
    assert "review" in result["agent_history"]
    assert "validation" in result["agent_history"]
    assert "report" in result["agent_history"]
    
    # Verify analysis results
    assert result["analysis_result"] is not None
    assert result["entities"] is not None
    assert result["clause_classifications"] is not None
    assert result["analysis_confidence"] > 0
    
    # Verify review results
    assert result["review_result"] is not None
    assert result["compliance_issues"] is not None
    assert result["risk_assessments"] is not None
    assert result["suggestions"] is not None
    
    # Verify validation results
    assert result["validation_result"] is not None
    assert result["citation_accuracy"] > 0
    assert result["hallucination_score"] >= 0
    
    # Verify report generated
    assert result["report"] is not None
    assert result["risk_matrix"] is not None
    assert result["export_formats"] is not None
    assert "markdown" in result["export_formats"]
    assert "json" in result["export_formats"]
    
    # Verify final answer
    assert result["final_answer"] is not None
    assert "合同分析报告" in result["final_answer"]
    
    print("✅ Complete workflow executed successfully")
    print(f"   Task status: {result['task_status']}")
    print(f"   Agents executed: {len(result['agent_history'])}")
    print(f"   Analysis confidence: {result['analysis_confidence']:.2f}")
    print(f"   Validation confidence: {result['validation_result']['overall_confidence']:.2f}")


@pytest.mark.asyncio
async def test_workflow_with_user_query():
    """Test workflow with user query (direct retrieval path)"""
    graph = create_contract_analysis_graph()
    
    # Create initial state with user query
    state = create_initial_state(
        contract_id="test_contract_002",
        contract_text="Test contract text",
        contract_type=ContractType.OTHER,
        user_query="What is the termination clause?",
    )
    
    # Execute workflow
    result = await graph.ainvoke(state)
    
    # Verify workflow completed
    assert result["task_status"] == TaskStatus.COMPLETED
    
    # Verify coordinator chose direct retrieval path
    assert result["execution_plan"] is not None
    assert len(result["execution_plan"]) > 0
    assert result["execution_plan"][0]["agent"] == "retrieval"
    
    print("✅ Workflow with user query executed successfully")
    print(f"   Execution plan: {result['execution_plan'][0]}")


if __name__ == "__main__":
    import asyncio
    
    print("Running integration tests...\n")
    
    print("Test 1: Full contract analysis workflow")
    asyncio.run(test_workflow_execution())
    
    print("\nTest 2: User query workflow")
    asyncio.run(test_workflow_with_user_query())
    
    print("\n✅ All integration tests passed!")
