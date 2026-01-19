"""
End-to-end test for contract analysis workflow
"""
import pytest
from app.agents import (
    create_contract_analysis_graph,
    create_initial_state,
    ContractType,
)
from app.task_storage import (
    Task as StorageTask,
    TaskStatus,
    TaskType,
    create_task,
    get_task,
    update_task,
    generate_task_id,
)


@pytest.mark.asyncio
async def test_full_contract_analysis():
    """Test complete contract analysis workflow"""
    # Create workflow
    graph = create_contract_analysis_graph()
    
    # Sample contract
    contract_text = """
劳动合同

甲方：北京科技有限公司
乙方：张三

第一条 合同期限
本合同期限为三年，自2024年1月1日起至2027年1月1日止。

第二条 工作内容
乙方担任软件工程师岗位，负责系统开发和维护工作。

第三条 劳动报酬
乙方的月工资为10000元，甲方于每月15日支付上月工资。

第四条 保密义务
乙方应当保守甲方的商业秘密和技术秘密，不得泄露给第三方。

第五条 违约责任
任何一方违反本合同约定，应向对方支付5000元违约金。
"""
    
    # Initialize state
    state = create_initial_state(
        contract_id="CONTRACT_TEST_001",
        contract_text=contract_text,
        contract_type=ContractType.EMPLOYMENT,
    )
    
    # Create task
    task_id = generate_task_id()
    task = StorageTask(
        id=task_id,
        type=TaskType.CONTRACT_ANALYSIS,
        status=TaskStatus.PENDING,
        input_data={
            "contract_id": "CONTRACT_TEST_001",
            "contract_text": contract_text,
            "contract_type": "employment",
        },
    )
    await create_task(task)
    print(f"✅ Created task: {task_id}")
    
    # Update to processing
    await update_task(task_id, status=TaskStatus.PROCESSING)
    print("✅ Task status: processing")
    
    # Execute workflow
    print("🚀 Starting workflow execution...")
    result = await graph.ainvoke(state)
    print("✅ Workflow completed")
    
    # Verify results
    assert result["task_status"] == "completed"
    assert len(result["agent_history"]) == 6
    assert result["analysis_confidence"] > 0
    assert "final_answer" in result
    
    print(f"   Agents executed: {len(result['agent_history'])}")
    print(f"   Analysis confidence: {result['analysis_confidence']:.2%}")
    print(f"   Overall risk: {result.get('review_result', {}).get('overall_risk', 'unknown')}")
    print(f"   Validation confidence: {result.get('validation_result', {}).get('overall_confidence', 0):.2%}")
    
    # Update task with results
    output_data = {
        "agent_history": [str(agent) for agent in result.get("agent_history", [])],
        "analysis_confidence": result.get("analysis_confidence", 0.0),
        "overall_risk": str(result.get("review_result", {}).get("overall_risk", "unknown")),
        "validation_confidence": result.get("validation_result", {}).get("overall_confidence", 0.0),
        "final_answer": result.get("final_answer", ""),
        "report": result.get("report"),
    }
    
    await update_task(
        task_id,
        status=TaskStatus.COMPLETED,
        output_data=output_data,
        result=output_data.get("final_answer", ""),
    )
    print("✅ Task updated with results")
    
    # Verify task
    final_task = await get_task(task_id)
    assert final_task.status == TaskStatus.COMPLETED
    assert final_task.output_data is not None
    assert final_task.result is not None
    print("✅ Task verification complete")


@pytest.mark.asyncio
async def test_contract_analysis_with_user_query():
    """Test contract analysis with user query"""
    graph = create_contract_analysis_graph()
    
    state = create_initial_state(
        contract_id="QUERY_TEST_001",
        contract_text="Simple contract text",
        contract_type=ContractType.OTHER,
        user_query="What is the termination clause?",
    )
    
    result = await graph.ainvoke(state)
    
    assert result["task_status"] == "completed"
    assert "final_answer" in result
    print("✅ User query test passed")


if __name__ == "__main__":
    import asyncio
    
    print("Running end-to-end tests...\n")
    
    print("Test 1: Full contract analysis")
    asyncio.run(test_full_contract_analysis())
    print()
    
    print("Test 2: Contract analysis with user query")
    asyncio.run(test_contract_analysis_with_user_query())
    print()
    
    print("✅ All end-to-end tests passed!")
