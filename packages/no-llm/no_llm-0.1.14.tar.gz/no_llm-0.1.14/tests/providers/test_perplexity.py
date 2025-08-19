import pytest
from no_llm.providers.provider_configs.perplexity import PerplexityProvider


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_perplexity_provider_connection():
    """Test that Perplexity provider can successfully connect to the API."""
    provider = PerplexityProvider()
    result = await provider.test()
    assert result is True, "Perplexity provider test should return True with valid API key"


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_perplexity_provider_invalid_key(monkeypatch):
    """Test that Perplexity provider returns False with invalid API key."""
    monkeypatch.setenv("INVALID_PERPLEXITY_KEY", "invalid-api-key")
    from no_llm.providers.env_var import EnvVar
    provider = PerplexityProvider(api_key=EnvVar[str]("$INVALID_PERPLEXITY_KEY"))
    result = await provider.test()
    assert result is False, "Perplexity provider test should return False with invalid API key"
