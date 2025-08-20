from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletionToolParam

ProviderToolDefinition = Union[
    Dict[str, Any],  # Anthropic returns a dict version of BetaToolComputerUse20250124Param
    "ChatCompletionToolParam",  # OpenRouter/OpenAI type
]


class MessageRole(str, Enum):
    """Message roles in conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ToolCall:
    """Represents a tool call request from the AI."""

    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class ProviderMessage:
    """Provider-agnostic message format."""

    role: MessageRole
    content: Union[str, List[Dict[str, Any]]]  # Text or structured content
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None  # For tool responses


@dataclass
class ProviderResponse:
    """Provider-agnostic response format."""

    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    raw_response: Optional[Any] = None  # Original provider response for debugging


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize provider with API key and additional config."""
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    async def create_completion(
        self,
        messages: List[ProviderMessage],
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.0,
        tools: Optional[List[ProviderToolDefinition]] = None,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> ProviderResponse:
        """Create a completion with the provider.

        Args:
            messages: Conversation history
            model: Model identifier
            max_tokens: Maximum response tokens
            temperature: Sampling temperature
            tools: Tool definitions (provider-specific format)
            system_prompt: System prompt
            **kwargs: Provider-specific parameters

        Returns:
            ProviderResponse with content and/or tool calls
        """
        pass

    @abstractmethod
    def format_tool_definition(
        self, display_width: int, display_height: int
    ) -> ProviderToolDefinition:
        """Format computer use tool definition for this provider.

        Args:
            display_width: Screen width in pixels
            display_height: Screen height in pixels

        Returns:
            Provider-specific tool definition. Each provider returns their own type:
            - Anthropic: Dict matching BetaToolComputerUse20250124Param
            - OpenRouter: ChatCompletionToolParam from OpenAI SDK
            The return value is used as-is by the provider's create_completion method.
        """
        pass

    @abstractmethod
    def supports_computer_use(self) -> bool:
        """Check if provider supports native computer use tools.

        Returns:
            True if provider has native computer-use support (like Anthropic's beta),
            False if we need to use custom tool definitions.
        """
        pass

    @abstractmethod
    def get_default_model(self) -> str:
        """Get default model for this provider."""
        pass
