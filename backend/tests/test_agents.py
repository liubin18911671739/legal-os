"""
Tests for multi-agent workflow
"""
import pytest
from app.agents import (
    AgentState,
    WorkflowNodes,
    create_contract_analysis_graph,
    create_initial_state,
    should_continue,
    TaskStatus,
    AgentStatus,
    ContractType,
)
from app.agents.coordinator import coordinator_node
from app.agents.retrieval import retrieval_node
from app.agents.analysis import analysis_node
from app.agents.review import review_node
from app.agents.validation import validation_node
from app.agents.report import report_node


def test_workflow_nodes_enum():
    """Test WorkflowNodes enum has all expected values"""
    assert WorkflowNodes.COORDINATOR.value == "coordinator"
    assert WorkflowNodes.RETRIEVAL.value == "retrieval"
    assert WorkflowNodes.ANALYSIS.value == "analysis"
    assert WorkflowNodes.REVIEW.value == "review"
    assert WorkflowNodes.VALIDATION.value == "validation"
    assert WorkflowNodes.REPORT.value == "report"
    assert WorkflowNodes.ERROR_HANDLER.value == "error_handler"


def test_create_initial_state():
    """Test initial state creation"""
    state = create_initial_state(
        contract_id="test_123",
        contract_text="Test contract content",
        contract_type=ContractType.SALES,
    )
    
    assert state["contract_id"] == "test_123"
    assert state["contract_text"] == "Test contract content"
    assert state["contract_type"] == ContractType.SALES
    assert state["task_status"] == TaskStatus.PENDING
    assert state["current_agent"] is None
    assert state["agent_history"] == []
    assert state["error_message"] is None
    assert state["retry_count"] == 0
    assert state["requires_human_intervention"] is False


def test_should_continue():
    """Test should_continue decision function"""
    state = create_initial_state(
        contract_id="test",
        contract_text="Test",
        contract_type=ContractType.OTHER,
    )
    
    # Should continue if pending
    state["task_status"] = TaskStatus.PENDING
    assert should_continue(state) == "continue"
    
    # Should continue if processing
    state["task_status"] = TaskStatus.PROCESSING
    assert should_continue(state) == "continue"
    
    # Should stop if completed with final answer
    state["task_status"] = TaskStatus.COMPLETED
    state["final_answer"] = "Test answer"
    assert should_continue(state) == "stop"
    
    # Should stop if failed
    state["task_status"] = TaskStatus.FAILED
    assert should_continue(state) == "stop"
    
    # Should stop if human intervention required
    state["task_status"] = TaskStatus.PROCESSING
    state["requires_human_intervention"] = True
    assert should_continue(state) == "stop"
    
    # Should stop if max retries reached
    state["requires_human_intervention"] = False
    state["retry_count"] = 3
    state["max_retries"] = 3
    assert should_continue(state) == "stop"


def test_create_workflow_graph():
    """Test workflow graph creation"""
    graph = create_contract_analysis_graph()
    
    assert graph is not None
    assert len(graph.nodes) > 0
    assert "coordinator" in graph.nodes
    assert "retrieval" in graph.nodes


def test_workflow_info():
    """Test workflow info function"""
    from app.agents import get_workflow_info
    
    info = get_workflow_info()
    
    assert info["name"] == "Contract Analysis Multi-Agent Workflow"
    assert info["version"] == "1.0.0"
    assert "coordinator" in info["flow"]
    assert "retrieval" in info["flow"]


@pytest.mark.asyncio
async def test_coordinator_node():
    """Test coordinator node"""
    
    state = create_initial_state(
        contract_id="test",
        contract_text="Test contract text",
        contract_type=ContractType.OTHER,
        user_query="What is the contract about?",
    )
    
    result = await coordinator_node(state)
    
    assert result["contract_type"] == ContractType.OTHER
    assert WorkflowNodes.COORDINATOR in result["agent_history"]
    assert result["current_agent"] == WorkflowNodes.COORDINATOR
    assert result["execution_plan"] is not None
    assert result["agent_sequence"] is not None
    assert result["task_status"] == TaskStatus.PROCESSING


@pytest.mark.asyncio
async def test_retrieval_node():
    """Test retrieval node"""
    
    state = create_initial_state(
        contract_id="test",
        contract_text="Test contract text",
        contract_type=ContractType.OTHER,
        user_query="Test query",
    )
    
    result = await retrieval_node(state)
    
    assert WorkflowNodes.RETRIEVAL in result["agent_history"]
    assert result["current_agent"] == WorkflowNodes.RETRIEVAL
    assert result["retrieved_docs"] is not None
    assert len(result["retrieved_docs"]) > 0
    assert result["retrieval_count"] > 0
    assert result["retrieval_success"] is True


@pytest.mark.asyncio
async def test_analysis_node():
    """Test analysis node"""
    
    state = create_initial_state(
        contract_id="test",
        contract_text="Test contract text",
        contract_type=ContractType.EMPLOYMENT,
    )
    
    result = await analysis_node(state)
    
    assert WorkflowNodes.ANALYSIS in result["agent_history"]
    assert result["current_agent"] == WorkflowNodes.ANALYSIS
    assert result["analysis_result"] is not None
    assert result["entities"] is not None
    assert result["clause_classifications"] is not None
    assert result["analysis_confidence"] > 0
    assert result["analysis_agent_status"] == AgentStatus.COMPLETED


@pytest.mark.asyncio
async def test_review_node():
    """Test review node"""
    
    state = create_initial_state(
        contract_id="test",
        contract_text="Test contract text",
        contract_type=ContractType.EMPLOYMENT,
    )
    state["entities"] = {"parties": [{"name": "甲方"}]}
    state["clause_classifications"] = [{"type": "payment", "text": "Test clause"}]
    
    result = await review_node(state)
    
    assert WorkflowNodes.REVIEW in result["agent_history"]
    assert result["current_agent"] == WorkflowNodes.REVIEW
    assert result["review_result"] is not None
    assert result["compliance_issues"] is not None
    assert result["risk_assessments"] is not None
    assert result["suggestions"] is not None
    assert result["review_agent_status"] == AgentStatus.COMPLETED


@pytest.mark.asyncio
async def test_validation_node():
    """Test validation node"""
    
    state = create_initial_state(
        contract_id="test",
        contract_text="Test contract text",
        contract_type=ContractType.EMPLOYMENT,
    )
    state["analysis_result"] = {"clause_count": 4}
    state["review_result"] = {"issue_count": 3, "risk_count": 2, "overall_risk": "high"}
    state["retrieved_docs"] = [{"content": "Test doc"}]
    
    result = await validation_node(state)
    
    assert WorkflowNodes.VALIDATION in result["agent_history"]
    assert result["current_agent"] == WorkflowNodes.VALIDATION
    assert result["validation_result"] is not None
    assert result["citation_accuracy"] > 0
    assert result["hallucination_score"] >= 0
    assert result["validation_agent_status"] == AgentStatus.COMPLETED


@pytest.mark.asyncio
async def test_report_node():
    """Test report node"""
    
    state = create_initial_state(
        contract_id="test",
        contract_text="Test contract text",
        contract_type=ContractType.EMPLOYMENT,
    )
    state["analysis_result"] = {"clause_count": 4, "entities": {}}
    state["review_result"] = {"issue_count": 3, "risk_count": 2, "overall_risk": "high"}
    state["validation_result"] = {"overall_confidence": 0.85}
    
    result = await report_node(state)
    
    assert WorkflowNodes.REPORT in result["agent_history"]
    assert result["current_agent"] == WorkflowNodes.REPORT
    assert result["report"] is not None
    assert result["risk_matrix"] is not None
    assert result["export_formats"] is not None
    assert "markdown" in result["export_formats"]
    assert "json" in result["export_formats"]
    assert result["final_answer"] is not None
    assert result["task_status"] == TaskStatus.COMPLETED
    assert result["report_agent_status"] == AgentStatus.COMPLETED


@pytest.mark.asyncio
async def test_full_workflow():
    """Test complete workflow from start to finish"""
    state = create_initial_state(
        contract_id="test_123",
        contract_text="Test contract content for analysis",
        contract_type=ContractType.EMPLOYMENT,
    )
    
    # Execute all agents in sequence
    state = await coordinator_node(state)
    assert state["task_status"] == TaskStatus.PROCESSING
    
    state = await retrieval_node(state)
    assert state["retrieval_success"] is True
    
    state = await analysis_node(state)
    assert state["analysis_confidence"] > 0
    
    state = await review_node(state)
    assert state["review_agent_status"] == AgentStatus.COMPLETED
    
    state = await validation_node(state)
    assert state["validation_agent_status"] == AgentStatus.COMPLETED
    
    state = await report_node(state)
    assert state["task_status"] == TaskStatus.COMPLETED
    assert state["final_answer"] is not None
    
    # Verify all agents ran
    assert len(state["agent_history"]) == 6
    assert WorkflowNodes.COORDINATOR in state["agent_history"]
    assert WorkflowNodes.RETRIEVAL in state["agent_history"]
    assert WorkflowNodes.ANALYSIS in state["agent_history"]
    assert WorkflowNodes.REVIEW in state["agent_history"]
    assert WorkflowNodes.VALIDATION in state["agent_history"]
    assert WorkflowNodes.REPORT in state["agent_history"]
