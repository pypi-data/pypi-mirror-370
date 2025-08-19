from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import Field, PrivateAttr
from pydantic_ai.providers.azure import AzureProvider as PydanticAzureProvider

from no_llm.providers.config import ProviderConfiguration
from no_llm.providers.env_var import EnvVar

if TYPE_CHECKING:
    from collections.abc import Iterator


class AzureProvider(ProviderConfiguration):
    """Azure provider configuration"""

    type: Literal["azure"] = "azure"  # type: ignore
    id: str = "azure"
    name: str = "Azure"
    api_key: EnvVar[str] = Field(
        default_factory=lambda: EnvVar[str]("$AZURE_API_KEY"),
        description="Name of environment variable containing API key",
    )
    base_url: EnvVar[str] = Field(
        default_factory=lambda: EnvVar[str]("$AZURE_BASE_URL"),
        description="Optional base URL override",
    )
    api_version: str = Field(default="2025-05-01-preview", description="Azure API version")
    locations: list[str] = Field(default=["eastus", "eastus2"], min_length=1, description="Azure regions")
    _value: str | None = PrivateAttr(default=None)

    def iter(self) -> Iterator[ProviderConfiguration]:
        """Yield provider variants for each location"""
        if not self.has_valid_env():
            return
        for location in self.locations:
            provider = self.model_copy()
            provider._value = location  # noqa: SLF001
            yield provider

    @property
    def current(self) -> str:
        """Get current value, defaulting to first location if not set"""
        return self._value or self.locations[0]

    def reset_variants(self) -> None:
        self._value = None

    def to_pydantic(self) -> PydanticAzureProvider:
        return PydanticAzureProvider(
            api_key=str(self.api_key),
            azure_endpoint=str(self.base_url),
            api_version=self.api_version,
        )

    async def test(self) -> bool:
        try:
            req = await self.to_pydantic().client.models.list()
        except Exception:
            return False
        return True
