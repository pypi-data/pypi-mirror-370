from typing import Dict, Optional, Type

from mirrai.core.logger import logger
from mirrai.core.providers.anthropic import AnthropicProvider
from mirrai.core.providers.base import AIProvider
from mirrai.core.providers.openrouter import OpenRouterProvider


class ProviderFactory:
    """Factory for creating and managing AI providers."""

    _providers: Dict[str, Type[AIProvider]] = {
        "anthropic": AnthropicProvider,
        "openrouter": OpenRouterProvider,
    }

    _instances: Dict[str, AIProvider] = {}

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[AIProvider]) -> None:
        """Register a new provider type.

        Args:
            name: Provider identifier
            provider_class: Provider class
        """
        cls._providers[name] = provider_class
        logger.debug(f"Registered provider: {name}")

    @classmethod
    def create_provider(
        cls, provider_type: str, api_key: Optional[str] = None, **kwargs
    ) -> AIProvider:
        """Create a provider instance.

        Args:
            provider_type: Type of provider (anthropic, openrouter, etc.)
            api_key: API key for the provider
            **kwargs: Additional provider-specific configuration

        Returns:
            Provider instance
        """
        if provider_type not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unknown provider type: {provider_type}. " f"Available providers: {available}"
            )

        cache_key = f"{provider_type}:{api_key or 'default'}"
        if cache_key in cls._instances:
            return cls._instances[cache_key]

        provider_class = cls._providers[provider_type]
        provider = provider_class(api_key=api_key, **kwargs)

        cls._instances[cache_key] = provider

        logger.debug(f"Created {provider_type} provider")
        return provider
