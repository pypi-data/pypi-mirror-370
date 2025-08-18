"""Global Anthropic client singleton."""

import os
from typing import Optional

from anthropic import AsyncAnthropic

from mirrai.core.utils import Singleton


class AnthropicClient(metaclass=Singleton):
    """Singleton Anthropic client for global usage."""

    def __init__(self):
        """Initialize the client, loading API key from environment."""
        self._client: Optional[AsyncAnthropic] = None
        self._api_key: Optional[str] = None
        self._initialize()

    def _initialize(self) -> None:
        """Initialize the client from environment."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in environment. "
                "Please set it as an environment variable."
            )

        self._api_key = api_key
        self._client = AsyncAnthropic(api_key=api_key)

    def get_client(self) -> AsyncAnthropic:
        """Get the Anthropic client instance."""
        if self._client is None:
            self._initialize()
        assert self._client is not None  # For type checker
        return self._client

    def set_api_key(self, api_key: str) -> None:
        """Manually set the API key and reinitialize client."""
        self._api_key = api_key
        self._client = AsyncAnthropic(api_key=api_key)

    @property
    def is_initialized(self) -> bool:
        """Check if client is initialized."""
        return self._client is not None


client = AnthropicClient()  # global singleton
