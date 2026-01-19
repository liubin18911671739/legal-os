"""
Tests for ZhipuAI client integration
"""
import pytest
from app.llm_client import (
    ZhipuAIClient,
    TokenUsage,
    CostTracker,
    get_client,
    close_client,
)


def test_token_usage():
    """Test token usage tracking"""
    usage = TokenUsage()
    assert usage.total_tokens == 0

    usage.add(100, 50)
    assert usage.prompt_tokens == 100
    assert usage.completion_tokens == 50
    assert usage.total_tokens == 150

    usage.add(50, 25)
    assert usage.prompt_tokens == 150
    assert usage.completion_tokens == 75
    assert usage.total_tokens == 225


def test_cost_tracker():
    """Test cost tracking"""
    tracker = CostTracker()
    assert tracker.total_cost == 0.0

    # Add usage for different models
    cost1 = tracker.add_usage("glm-4", 1000, 500, "test_agent")
    cost2 = tracker.add_usage("glm-4-flash", 2000, 1000, "test_agent2")

    assert tracker.total_cost > 0
    assert "glm-4" in tracker.model_costs
    assert "glm-4-flash" in tracker.model_costs
    assert "test_agent" in tracker.usage_by_agent

    summary = tracker.get_summary()
    assert "total_cost" in summary
    assert "model_costs" in summary
    assert "usage_by_agent" in summary


def test_zhipu_client_initialization():
    """Test client initialization"""
    # Test with mock mode (no API key)
    client = ZhipuAIClient(enable_tracking=True)
    assert client.mock_mode is True
    assert client.cost_tracker is not None

    # Check agent configurations
    assert "coordinator" in client.AGENT_MODELS
    assert "retrieval" in client.AGENT_MODELS
    assert "analysis" in client.AGENT_MODELS
    assert "review" in client.AGENT_MODELS
    assert "validation" in client.AGENT_MODELS
    assert "report" in client.AGENT_MODELS


@pytest.mark.asyncio
async def test_zhipu_client_mock_generate():
    """Test mock text generation"""
    client = ZhipuAIClient(enable_tracking=False)
    assert client.mock_mode is True

    result = await client.generate(
        agent="analysis",
        prompt="Test prompt",
    )

    assert "mock" in result.lower()
    assert result is not None


@pytest.mark.asyncio
async def test_zhipu_client_mock_generate_json():
    """Test mock JSON generation"""
    client = ZhipuAIClient(enable_tracking=False)

    result = await client.generate_json(
        agent="analysis",
        prompt="Test prompt",
    )

    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_zhipu_client_mock_stream():
    """Test mock streaming"""
    client = ZhipuAIClient(enable_tracking=False)

    chunks = []
    async for chunk in client.stream_generate(
        agent="analysis",
        prompt="Test prompt",
    ):
        chunks.append(chunk)

    assert len(chunks) > 0
    assert "[MOCK STREAM" in "".join(chunks)


@pytest.mark.asyncio
async def test_zhipu_client_mock_with_cost_tracking():
    """Test mock generation with cost tracking"""
    client = ZhipuAIClient(enable_tracking=True)

    # Generate with tracking
    result = await client.generate(
        agent="analysis",
        prompt="Test prompt for cost tracking",
    )

    assert "mock" in result.lower()

    # Check cost summary (mock mode should not add costs)
    summary = client.get_cost_summary()
    assert summary["total_cost"] == 0.0


def test_global_client():
    """Test global client singleton"""
    client1 = get_client()
    client2 = get_client()

    assert client1 is client2


@pytest.mark.asyncio
async def test_agent_model_configs():
    """Test agent-specific model configurations"""
    client = ZhipuAIClient()

    # Check coordinator config
    assert client.AGENT_MODELS["coordinator"]["model"] == "glm-4"
    assert client.AGENT_MODELS["coordinator"]["temperature"] == 0.3
    assert client.AGENT_MODELS["coordinator"]["max_tokens"] == 1024

    # Check retrieval config
    assert client.AGENT_MODELS["retrieval"]["model"] == "glm-4-flash"
    assert client.AGENT_MODELS["retrieval"]["temperature"] == 0.5

    # Check report config
    assert client.AGENT_MODELS["report"]["model"] == "glm-4"
    assert client.AGENT_MODELS["report"]["max_tokens"] == 4096


def test_model_pricing():
    """Test model pricing configuration"""
    assert "glm-4" in CostTracker.MODEL_PRICING
    assert "glm-4-flash" in CostTracker.MODEL_PRICING
    assert CostTracker.MODEL_PRICING["glm-4"]["input"] > 0
    assert CostTracker.MODEL_PRICING["glm-4"]["output"] > 0


@pytest.mark.asyncio
async def test_close_client():
    """Test closing client"""
    client = ZhipuAIClient()
    await client.close()
    # Should not raise exception


@pytest.mark.asyncio
async def test_generate_with_system_prompt():
    """Test generation with system prompt"""
    client = ZhipuAIClient()

    result = await client.generate(
        agent="analysis",
        prompt="Test prompt",
        system_prompt="You are a helpful assistant.",
    )

    assert result is not None


if __name__ == "__main__":
    import asyncio

    print("Running ZhipuAI client tests...\n")

    print("Test 1: Token usage tracking")
    test_token_usage()
    print("✅ Passed\n")

    print("Test 2: Cost tracker")
    test_cost_tracker()
    print("✅ Passed\n")

    print("Test 3: Client initialization")
    test_zhipu_client_initialization()
    print("✅ Passed\n")

    print("Test 4: Mock generate")
    asyncio.run(test_zhipu_client_mock_generate())
    print("✅ Passed\n")

    print("Test 5: Mock generate JSON")
    asyncio.run(test_zhipu_client_mock_generate_json())
    print("✅ Passed\n")

    print("Test 6: Mock stream")
    asyncio.run(test_zhipu_client_mock_stream())
    print("✅ Passed\n")

    print("Test 7: Agent model configs")
    asyncio.run(test_agent_model_configs())
    print("✅ Passed\n")

    print("Test 8: Global client")
    test_global_client()
    print("✅ Passed\n")

    print("✅ All ZhipuAI client tests passed!")
