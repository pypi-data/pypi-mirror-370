from __future__ import annotations

from typing import Literal
from urllib.parse import urljoin

import httpx
from loguru import logger
from pydantic import Field
from pydantic_ai.providers.openai import OpenAIProvider as PydanticOpenAIProvider

from no_llm.providers.config import ProviderConfiguration
from no_llm.providers.env_var import EnvVar


class OpenAIProvider(ProviderConfiguration):
    """OpenAI provider configuration"""

    type: Literal["openai"] = "openai"  # type: ignore
    id: str = "openai"
    name: str = "OpenAI"
    api_key: EnvVar[str] = Field(
        default_factory=lambda: EnvVar[str]("$OPENAI_API_KEY"),
        description="Name of environment variable containing API key",
    )
    base_url: str | None = Field(default="https://api.openai.com/v1/", description="Optional base URL override")

    async def test(self) -> bool:
        try:
            base_url = str(self.base_url)
            if not base_url.endswith("/"):
                base_url += "/"
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    urljoin(base_url, "models"), headers={"Authorization": f"Bearer {self.api_key!s}"}
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
