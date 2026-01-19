"""
Tests for contract analysis API
"""
import pytest
from fastapi.testclient import TestClient
from app.api.v1.contracts import (
    router,
    ContractAnalysisRequest,
    ContractAnalysisResponse,
    AnalysisResult,
)
from app.task_storage import TaskStatus, create_task, get_task
from app.agents import create_contract_analysis_graph, create_initial_state, ContractType


@pytest.fixture
def client():
    """Create test client"""
    from app.main import app
    return TestClient(app)


@pytest.fixture
def sample_contract():
    """Sample contract for testing"""
    return """
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


def test_contract_analysis_request():
    """Test contract analysis request model"""
    request = ContractAnalysisRequest(
        contract_id="CONTRACT_001",
        contract_text="Contract content...",
        contract_type="employment",
        user_query="What is the termination clause?",
    )
    
    assert request.contract_id == "CONTRACT_001"
    assert request.contract_type == "employment"
    assert request.user_query == "What is the termination clause?"


def test_contract_analysis_response():
    """Test contract analysis response model"""
    response = ContractAnalysisResponse(
        task_id="TASK-123",
        status=TaskStatus.PROCESSING,
        message="Contract analysis started",
    )
    
    assert response.task_id == "TASK-123"
    assert response.status == TaskStatus.PROCESSING


def test_analysis_result():
    """Test analysis result model"""
    result = AnalysisResult(
        task_id="TASK-123",
        contract_id="CONTRACT_001",
        contract_type="employment",
        task_status=TaskStatus.COMPLETED,
        agent_history=["coordinator", "retrieval"],
        analysis_confidence=0.92,
        overall_risk="high",
        validation_confidence=0.85,
        final_answer="Analysis complete",
        report={"summary": "Test"},
    )
    
    assert result.task_id == "TASK-123"
    assert result.analysis_confidence == 0.92
    assert result.overall_risk == "high"


@pytest.mark.asyncio
async def test_analyze_contract_endpoint(sample_contract):
    """Test analyze contract endpoint"""
    # Create test client using router directly
    from fastapi import FastAPI
    test_app = FastAPI()
    test_app.include_router(router)
    
    client = TestClient(test_app)
    
    # Create request
    request_data = {
        "contract_id": "TEST_CONTRACT",
        "contract_text": sample_contract,
        "contract_type": "employment",
        "user_query": None,
    }
    
    # Call endpoint
    response = client.post("/contracts/analyze", json=request_data)
    
    # Check response
    assert response.status_code == 202
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "processing"
    assert "message" in data


@pytest.mark.asyncio
async def test_get_analysis_result_endpoint(sample_contract):
    """Test get analysis result endpoint"""
    from fastapi import FastAPI
    test_app = FastAPI()
    test_app.include_router(router)
    
    client = TestClient(test_app)
    
    # First, create a task
    request_data = {
        "contract_id": "TEST_CONTRACT",
        "contract_text": sample_contract,
        "contract_type": "employment",
    }
    
    create_response = client.post("/contracts/analyze", json=request_data)
    task_id = create_response.json()["task_id"]
    
    # Wait for background task to complete (simple delay)
    import asyncio
    await asyncio.sleep(1)
    
    # Get result
    result_response = client.get(f"/contracts/analysis/{task_id}")
    
    # Check response
    assert result_response.status_code in [200, 404]  # 200 if completed, 404 if not found yet
    
    if result_response.status_code == 200:
        data = result_response.json()
        assert data["task_id"] == task_id
        assert "analysis_confidence" in data
        assert "final_answer" in data


@pytest.mark.asyncio
async def test_get_task_status_endpoint(sample_contract):
    """Test get task status endpoint"""
    from fastapi import FastAPI
    test_app = FastAPI()
    test_app.include_router(router)
    
    client = TestClient(test_app)
    
    # Create a task
    request_data = {
        "contract_id": "TEST_CONTRACT",
        "contract_text": sample_contract,
        "contract_type": "employment",
    }
    
    create_response = client.post("/contracts/analyze", json=request_data)
    task_id = create_response.json()["task_id"]
    
    # Get status
    status_response = client.get(f"/contracts/tasks/{task_id}")
    
    # Check response
    assert status_response.status_code == 200
    data = status_response.json()
    assert data["task_id"] == task_id
    assert "status" in data
    assert "input_data" in data


@pytest.mark.asyncio
async def test_invalid_contract_type(sample_contract):
    """Test with invalid contract type"""
    from fastapi import FastAPI
    test_app = FastAPI()
    test_app.include_router(router)
    
    client = TestClient(test_app)
    
    # Create request with invalid contract type
    request_data = {
        "contract_id": "TEST_CONTRACT",
        "contract_text": sample_contract,
        "contract_type": "invalid_type",  # Invalid type
    }
    
    # Call endpoint
    response = client.post("/contracts/analyze", json=request_data)
    
    # Check response
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid contract type" in data["detail"]


def test_generate_task_id():
    """Test task ID generation"""
    from app.api.v1.contracts import generate_task_id
    
    task_id1 = generate_task_id()
    task_id2 = generate_task_id()
    
    # Check format
    assert task_id1.startswith("TASK-")
    assert task_id2.startswith("TASK-")
    
    # Check uniqueness
    assert task_id1 != task_id2


if __name__ == "__main__":
    import asyncio
    
    print("Running contract API tests...\n")
    
    print("Test 1: Request model")
    test_contract_analysis_request()
    print("✅ Passed\n")
    
    print("Test 2: Response model")
    test_contract_analysis_response()
    print("✅ Passed\n")
    
    print("Test 3: Result model")
    test_analysis_result()
    print("✅ Passed\n")
    
    print("Test 4: Analyze endpoint")
    asyncio.run(test_analyze_contract_endpoint(""))
    print("✅ Passed\n")
    
    print("Test 5: Get result endpoint")
    asyncio.run(test_get_analysis_result_endpoint(""))
    print("✅ Passed\n")
    
    print("Test 6: Task status endpoint")
    asyncio.run(test_get_task_status_endpoint(""))
    print("✅ Passed\n")
    
    print("Test 7: Invalid contract type")
    asyncio.run(test_invalid_contract_type(""))
    print("✅ Passed\n")
    
    print("Test 8: Task ID generation")
    test_generate_task_id()
    print("✅ Passed\n")
    
    print("\n✅ All contract API tests passed!")
