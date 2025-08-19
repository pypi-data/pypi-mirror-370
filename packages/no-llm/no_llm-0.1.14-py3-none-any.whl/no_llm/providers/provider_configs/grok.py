from __future__ import annotations

from typing import Literal
from urllib.parse import urljoin

import httpx
from loguru import logger
from pydantic import Field
from pydantic_ai.providers.openai import OpenAIProvider as PydanticOpenAIProvider

from no_llm.providers.env_var import EnvVar
from no_llm.providers.provider_configs.openai import OpenAIProvider


class GrokProvider(OpenAIProvider):
    """Grok provider configuration"""

    type: Literal["grok"] = "grok"  # type: ignore
    id: str = "grok"
    name: str = "Grok"
    api_key: EnvVar[str] = Field(
        default_factory=lambda: EnvVar[str]("$GROK_API_KEY"),
        description="Name of environment variable containing API key",
    )
    base_url: str | None = Field(default="https://api.x.ai/v1", description="Base URL for Grok API")

    async def test(self) -> bool:
        try:
            base_url = str(self.base_url)
            if not base_url.endswith("/"):
                base_url += "/"
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    urljoin(base_url, "api-key"), headers={"Authorization": f"Bearer {self.api_key!s}"}
                )
                return response.status_code == 200
        except Exception as e:
            logger.opt(exception=e).error(f"Failed to test connectivity to {self.__class__.__name__}")
            return False

    def to_pydantic(self) -> PydanticOpenAIProvider:
        return PydanticOpenAIProvider(
            api_key=str(self.api_key),
            base_url=str(self.base_url),
        )
