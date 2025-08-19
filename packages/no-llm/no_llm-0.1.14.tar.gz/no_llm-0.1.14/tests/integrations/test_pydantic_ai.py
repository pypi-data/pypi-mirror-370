import pytest
from no_llm.integrations.pydantic_ai import NoLLMModel
from no_llm.models.registry import ModelRegistry
from pydantic_ai import Agent
from vcr import VCR


@pytest.fixture
def openai_model(monkeypatch, builtin_model_registry: ModelRegistry, vcr: VCR):
    if vcr.record_mode not in ['all', 'new_episodes']:
        monkeypatch.setenv('OPENAI_API_KEY', 'test-value')
    model = builtin_model_registry.get_model("gpt-4o")
    return NoLLMModel(model)

@pytest.mark.asyncio
@pytest.mark.vcr
@pytest.mark.skip
async def test_async_chat(openai_model: NoLLMModel):
    """Test async chat completion."""
    agent = Agent(openai_model)
    result = await agent.run("What is the capital of France?")
    assert "paris" in result.output.lower()

@pytest.mark.vcr
@pytest.mark.skip
def test_sync_chat(openai_model: NoLLMModel):
    """Test sync chat completion."""
    agent = Agent(openai_model)
    result = agent.run_sync("What is the capital of Italy??")
    assert "rome" in result.output.lower()

@pytest.mark.asyncio
@pytest.mark.vcr
@pytest.mark.skip
async def test_stream_chat(openai_model: NoLLMModel):
    """Test streaming chat completion."""
    agent = Agent(openai_model)
    async with agent.run_stream("What is the capital of the UK?") as response:
        data = await response.get_output()
        assert "london" in data.lower()
