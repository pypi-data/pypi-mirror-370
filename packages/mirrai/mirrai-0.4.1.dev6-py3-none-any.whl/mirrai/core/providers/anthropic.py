import os
from typing import Any, Dict, List, Optional

from anthropic import AsyncAnthropic
from anthropic.types.beta import (
    BetaImageBlockParam,
    BetaMessageParam,
    BetaTextBlock,
    BetaTextBlockParam,
    BetaToolComputerUse20250124Param,
    BetaToolResultBlockParam,
    BetaToolUseBlock,
    BetaToolUseBlockParam,
)

from mirrai.core.constants import (
    ANTHROPIC_COMPUTER_TOOL_TYPE,
    ANTHROPIC_COMPUTER_USE_BETA,
    PROVIDER_DEFAULT_MODELS,
)
from mirrai.core.providers.base import (
    AIProvider,
    MessageRole,
    ProviderMessage,
    ProviderResponse,
    ProviderToolDefinition,
    ToolCall,
)


class AnthropicProvider(AIProvider):
    """Anthropic provider with native computer-use support."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize Anthropic provider."""
        super().__init__(api_key, **kwargs)

        if not self.api_key:
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY not found. "
                    "Please set it as an environment variable or pass it to the provider."
                )

        self.client = AsyncAnthropic(api_key=self.api_key)

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
        """Create completion using Anthropic's beta computer-use API."""
        anthropic_messages = self._convert_messages(messages)
        anthropic_tools = self._prepare_tools(tools)
        response = await self.client.beta.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=anthropic_messages,
            system=system_prompt or "",
            tools=anthropic_tools,
            betas=[ANTHROPIC_COMPUTER_USE_BETA],
            temperature=temperature,
        )
        return self._process_response(response)

    def format_tool_definition(self, display_width: int, display_height: int) -> Dict[str, Any]:
        """Format computer-use tool for Anthropic's beta API."""
        return dict(
            BetaToolComputerUse20250124Param(
                type=ANTHROPIC_COMPUTER_TOOL_TYPE,
                name="computer",
                display_width_px=display_width,
                display_height_px=display_height,
                display_number=1,
            )
        )

    def supports_computer_use(self) -> bool:
        """Anthropic has native computer-use support via beta."""
        return True

    def get_default_model(self) -> str:
        """Get default Anthropic model."""
        return PROVIDER_DEFAULT_MODELS["anthropic"]

    def _convert_tool_result_to_content(self, item: Dict[str, Any]) -> BetaToolResultBlockParam:
        """Convert a tool result dictionary to Anthropic's format."""
        tool_call_id = item["tool_call_id"]
        if "error" in item:
            return BetaToolResultBlockParam(
                type="tool_result",
                tool_use_id=tool_call_id,
                content=item["error"],
                is_error=True,
            )
        elif "content" in item:
            content = item["content"]
            if isinstance(content, dict) and content.get("type") == "image":
                return BetaToolResultBlockParam(
                    type="tool_result",
                    tool_use_id=tool_call_id,
                    content=[
                        BetaImageBlockParam(
                            type="image",
                            source={
                                "type": "base64",
                                "media_type": "image/png",
                                "data": content["data"],
                            },
                        )
                    ],
                    is_error=False,
                )
            else:
                return BetaToolResultBlockParam(
                    type="tool_result",
                    tool_use_id=tool_call_id,
                    content=str(content),
                    is_error=False,
                )
        else:
            return BetaToolResultBlockParam(
                type="tool_result",
                tool_use_id=tool_call_id,
                content="",
                is_error=False,
            )

    def _convert_user_message(self, msg: ProviderMessage) -> BetaMessageParam:
        """Convert a user message to Anthropic format."""
        if isinstance(msg.content, str):
            return BetaMessageParam(
                role="user", content=[BetaTextBlockParam(type="text", text=msg.content)]
            )
        elif isinstance(msg.content, list):
            content_blocks = []
            for item in msg.content:
                if isinstance(item, dict) and "tool_call_id" in item:
                    content_blocks.append(self._convert_tool_result_to_content(item))
            return BetaMessageParam(role="user", content=content_blocks)
        else:
            return BetaMessageParam(
                role="user", content=[BetaTextBlockParam(type="text", text=str(msg.content))]
            )

    def _convert_assistant_message(self, msg: ProviderMessage) -> BetaMessageParam:
        """Convert an assistant message to Anthropic format."""
        content_blocks = []

        if msg.content and isinstance(msg.content, str):
            content_blocks.append(BetaTextBlockParam(type="text", text=msg.content))

        if msg.tool_calls:
            for tool_call in msg.tool_calls:
                content_blocks.append(
                    BetaToolUseBlockParam(
                        type="tool_use",
                        id=tool_call.id,
                        name=tool_call.name,
                        input=tool_call.arguments,
                    )
                )

        return BetaMessageParam(role="assistant", content=content_blocks)

    def _convert_messages(self, messages: List[ProviderMessage]) -> List[BetaMessageParam]:
        """Convert ProviderMessages to Anthropic's BetaMessageParam format."""
        anthropic_messages = []

        for msg in messages:
            if msg.role == MessageRole.USER:
                anthropic_messages.append(self._convert_user_message(msg))
            elif msg.role == MessageRole.ASSISTANT:
                anthropic_messages.append(self._convert_assistant_message(msg))
            # Skip SYSTEM messages, they're handled separately

        return anthropic_messages

    def _prepare_tools(
        self, tools: Optional[List[ProviderToolDefinition]]
    ) -> List[BetaToolComputerUse20250124Param]:
        """Prepare tools for Anthropic API."""
        if not tools:
            return []

        anthropic_tools = []
        for tool in tools:
            # Anthropic provider tools are always dicts
            if isinstance(tool, dict) and tool.get("type") == ANTHROPIC_COMPUTER_TOOL_TYPE:
                # Cast to Any to satisfy type checker. We know the structure is correct.
                anthropic_tools.append(BetaToolComputerUse20250124Param(**tool))  # type: ignore
        return anthropic_tools

    def _process_response(self, response) -> ProviderResponse:
        """Process Anthropic API response into ProviderResponse."""
        text_content = []
        tool_calls = []
        for block in response.content:
            if isinstance(block, BetaTextBlock):
                text_content.append(block.text)
            elif isinstance(block, BetaToolUseBlock):
                tool_calls.append(self._extract_tool_call(block))
        return ProviderResponse(
            content="\n".join(text_content) if text_content else None,
            tool_calls=tool_calls if tool_calls else None,
            raw_response=response,
        )

    def _extract_tool_call(self, block: BetaToolUseBlock) -> ToolCall:
        """Extract a ToolCall from a BetaToolUseBlock."""
        args: Dict[str, Any] = {}
        if block.input and isinstance(block.input, dict):
            # Cast keys to strings to ensure proper type
            args = {str(k): v for k, v in block.input.items()}
        return ToolCall(
            id=block.id,
            name=block.name,
            arguments=args,
        )
