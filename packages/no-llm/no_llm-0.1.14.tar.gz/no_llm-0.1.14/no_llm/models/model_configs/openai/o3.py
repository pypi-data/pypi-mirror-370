from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from pydantic import Field

from no_llm.models.config import (
    ConfigurableModelParameters,
    IntegrationAliases,
    ModelCapability,
    ModelConstraints,
    ModelIdentity,
    ModelMetadata,
    ModelMode,
    ModelPricing,
    ModelProperties,
    ParameterValue,
    ParameterVariant,
    PrivacyLevel,
    QualityProperties,
    SpeedProperties,
    TokenPrices,
)
from no_llm.models.config.parameters import NOT_GIVEN, NotGiven
from no_llm.models.model_configs.openai.base import OpenaiBaseConfiguration
from no_llm.providers import (
    AzureProvider,
    OpenAIProvider,
    OpenRouterProvider,
    Providers,
)


class O3Configuration(OpenaiBaseConfiguration):
    """Configuration for O3 model"""

    identity: ModelIdentity = ModelIdentity(
        id="o3",
        name="O3",
        version="2024.04",
        description="Newest and most advanced model from OpenAI with the most advanced performance and speed.",
        creator="OpenAI",
    )

    providers: Sequence[Providers] = [
        AzureProvider(),
        OpenRouterProvider(),
        OpenAIProvider(),
    ]

    mode: ModelMode = ModelMode.CHAT

    capabilities: set[ModelCapability] = {
        ModelCapability.JSON_MODE,
        ModelCapability.REASONING,
        ModelCapability.FUNCTION_CALLING,
        ModelCapability.TOOLS,
        ModelCapability.VISION,
    }

    constraints: ModelConstraints = ModelConstraints(max_input_tokens=200000, max_output_tokens=100000)

    properties: ModelProperties | None = ModelProperties(
        speed=SpeedProperties(score=42.0, label="High", description="Average (1-3 seconds)"),
        quality=QualityProperties(score=82.0, label="Very High", description="Very High Quality"),
    )

    metadata: ModelMetadata = ModelMetadata(
        privacy_level=[PrivacyLevel.BASIC],
        pricing=ModelPricing(token_prices=TokenPrices(input_price_per_1k=0.002, output_price_per_1k=0.008)),
        release_date=datetime(2024, 9, 12),
        data_cutoff_date=datetime(2023, 10, 1),
    )

    integration_aliases: IntegrationAliases | None = IntegrationAliases(
        pydantic_ai="o3-2025-04-16",
        litellm="o3-2025-04-16",
        langfuse="o3",
        openrouter="openai/o3",
    )

    class Parameters(ConfigurableModelParameters):
        model_config = ConfigurableModelParameters.model_config
        temperature: ParameterValue[float | NotGiven] = Field(
            default_factory=lambda: ParameterValue[float | NotGiven](variant=ParameterVariant.FIXED, value=1.0)
        )
        top_p: ParameterValue[float | NotGiven] = Field(
            default_factory=lambda: ParameterValue[float | NotGiven](variant=ParameterVariant.FIXED, value=1.0)
        )
        top_k: ParameterValue[int | NotGiven] = Field(
            default_factory=lambda: ParameterValue[int | NotGiven](
                variant=ParameterVariant.UNSUPPORTED, value=NOT_GIVEN
            )
        )
        frequency_penalty: ParameterValue[float | NotGiven] = Field(
            default_factory=lambda: ParameterValue[float | NotGiven](variant=ParameterVariant.FIXED, value=0.0)
        )
        presence_penalty: ParameterValue[float | NotGiven] = Field(
            default_factory=lambda: ParameterValue[float | NotGiven](
                variant=ParameterVariant.UNSUPPORTED, value=NOT_GIVEN
            )
        )

    parameters: Parameters = Field(default_factory=Parameters)  # type: ignore
