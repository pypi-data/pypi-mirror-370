from __future__ import annotations

from typing import Literal
from urllib.parse import urljoin

import httpx
from loguru import logger
from pydantic import Field
from pydantic_ai.providers.anthropic import (
    AnthropicProvider as PydanticAnthropicProvider,
)

from no_llm.providers.config import ProviderConfiguration
from no_llm.providers.env_var import EnvVar


class AnthropicProvider(ProviderConfiguration):
    """Anthropic provider configuration"""

    type: Literal["anthropic"] = "anthropic"  # type: ignore
    id: str = "anthropic"
    name: str = "Anthropic"
    api_key: EnvVar[str] = Field(
        default_factory=lambda: EnvVar[str]("$ANTHROPIC_API_KEY"),
        description="Name of environment variable containing API key",
    )
    base_url: str | None = Field(default=None, description="Optional base URL override")

    async def test(self) -> bool:
        try:
            base_url = str(self.base_url)
            if not base_url.endswith("/"):
                base_url += "/"
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    urljoin(base_url, "models"),
                    headers={"Authorization": f"Bearer {self.api_key!s}"},
                )
                return response.status_code == 200
        except Exception as e:
            logger.opt(exception=e).error(f"Failed to test connectivity to {self.__class__.__name__}")
            return False

    def to_pydantic(self) -> PydanticAnthropicProvider:
        return PydanticAnthropicProvider(
            api_key=str(self.api_key),
        )
