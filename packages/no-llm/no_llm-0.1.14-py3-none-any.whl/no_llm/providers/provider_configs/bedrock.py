from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import Field, PrivateAttr
from pydantic_ai.providers.bedrock import BedrockProvider as PydanticBedrockProvider

from no_llm.providers.config import ProviderConfiguration
from no_llm.providers.env_var import EnvVar

if TYPE_CHECKING:
    from collections.abc import Iterator


class BedrockProvider(ProviderConfiguration):
    """AWS Bedrock provider configuration"""

    type: Literal["bedrock"] = "bedrock"  # type: ignore
    id: str = "bedrock"
    name: str = "Bedrock"
    region: EnvVar[str] = Field(default_factory=lambda: EnvVar[str]("$BEDROCK_REGION"), description="AWS region")
    locations: list[str] = Field(default=["us-east-1"], min_length=1, description="AWS regions")
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

    def to_pydantic(self) -> PydanticBedrockProvider:
        return PydanticBedrockProvider(
            region_name=str(self.region),
        )
