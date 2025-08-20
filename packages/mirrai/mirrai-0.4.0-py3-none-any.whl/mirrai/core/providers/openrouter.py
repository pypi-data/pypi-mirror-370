import json
import os
from typing import Any, Dict, List, Optional, Union

from openai import AsyncOpenAI
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionAssistantMessageParam,
    ChatCompletionContentPartImageParam,
    ChatCompletionContentPartTextParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
    ChatCompletionUserMessageParam,
)
from openai.types.shared_params import FunctionDefinition, FunctionParameters

from mirrai.core.constants import PROVIDER_DEFAULT_MODELS
from mirrai.core.providers.base import (
    AIProvider,
    MessageRole,
    ProviderMessage,
    ProviderResponse,
    ProviderToolDefinition,
    ToolCall,
)


class OpenRouterProvider(AIProvider):
    """OpenRouter provider using OpenAI SDK with custom computer-use tool definitions."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize OpenRouter provider with OpenAI SDK client."""
        super().__init__(api_key, **kwargs)

        if not self.api_key:
            self.api_key = os.getenv("OPENROUTER_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "OPENROUTER_API_KEY not found. "
                    "Please set it as an environment variable or pass it to the provider."
                )

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=kwargs.get("base_url", "https://openrouter.ai/api/v1"),
            default_headers={
                "HTTP-Referer": kwargs.get("referer", "https://github.com/ooojustin/mirrai"),
                "X-Title": kwargs.get("app_title", "Mirrai Desktop Automation"),
            },
        )

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
        """Create completion using OpenRouter via OpenAI SDK."""
        openai_messages = self._convert_messages(messages, system_prompt)

        api_kwargs: Dict[str, Any] = {
            "model": model,
            "messages": openai_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if tools:
            api_kwargs["tools"] = [self._dict_to_tool_param(tool) for tool in tools]
            api_kwargs["tool_choice"] = "auto"

        response: ChatCompletion = await self.client.chat.completions.create(**api_kwargs)
        return self._process_response(response)

    def format_tool_definition(
        self, display_width: int, display_height: int
    ) -> ChatCompletionToolParam:
        """Format computer-use tools exactly matching Anthropic's schema for OpenRouter.

        This matches the actions that Anthropic's computer use tool expects,
        ensuring compatibility with our tool handler that expects actions like
        'left_click' instead of 'click', etc.
        """
        parameters: FunctionParameters = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "screenshot",
                        "left_click",
                        "right_click",
                        "double_click",
                        "type",
                        "key",
                        "mouse_move",
                        "scroll",
                        "wait",
                    ],
                    "description": "The action to perform.",
                },
                "coordinate": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 2,
                    "maxItems": 2,
                    "description": "The [x, y] coordinate for click/move actions",
                },
                "text": {"type": "string", "description": "Text to type (for type action)"},
                "key": {
                    "type": "string",
                    "description": "Key to press (for key action). Examples: Return, Tab, Escape, BackSpace, Delete, Home, End, PageUp, PageDown, ArrowUp, ArrowDown, ArrowLeft, ArrowRight, F1-F12, space, a-z, A-Z, 0-9, cmd/ctrl/alt/shift with another key",
                },
                "direction": {
                    "type": "string",
                    "enum": ["up", "down", "left", "right"],
                    "description": "Direction to scroll",
                },
                "amount": {
                    "type": "integer",
                    "description": "Amount to scroll (in pixels for up/down, or clicks for mouse wheel)",
                },
                "delay": {
                    "type": "number",
                    "description": "Time to wait in seconds (for wait action)",
                },
            },
            "required": ["action"],
            "additionalProperties": False,
        }

        function_def: FunctionDefinition = {
            "name": "computer",
            "description": "Use a computer to interact with the screen, keyboard, and mouse. "
            "This tool allows taking screenshots, clicking, typing, and scrolling.",
            "parameters": parameters,
        }

        tool_param: ChatCompletionToolParam = {
            "type": "function",
            "function": function_def,
        }

        return tool_param

    def supports_computer_use(self) -> bool:
        """OpenRouter uses custom tool definitions, not native computer-use."""
        return False

    def get_default_model(self) -> str:
        """Get default model for OpenRouter."""
        return PROVIDER_DEFAULT_MODELS["openrouter"]

    def _dict_to_tool_param(self, tool_def: ProviderToolDefinition) -> ChatCompletionToolParam:
        """Convert a provider tool definition to OpenAI's ChatCompletionToolParam type."""
        if isinstance(tool_def, dict):
            return ChatCompletionToolParam(**tool_def)  # type: ignore
        else:
            return tool_def  # pyright: ignore[reportUnreachable]

    def _convert_messages(
        self, messages: List[ProviderMessage], system_prompt: Optional[str] = None
    ) -> List[ChatCompletionMessageParam]:
        """Convert ProviderMessages to OpenAI SDK format with proper types."""
        openai_messages: List[ChatCompletionMessageParam] = []

        if system_prompt:
            system_msg: ChatCompletionSystemMessageParam = {
                "role": "system",
                "content": system_prompt,
            }
            openai_messages.append(system_msg)

        for msg in messages:
            if msg.role == MessageRole.USER:
                # User messages may contain tool results, which need special handling
                converted = self._convert_user_message(msg)
                if isinstance(converted, list):
                    openai_messages.extend(converted)
                else:
                    openai_messages.append(converted)

            elif msg.role == MessageRole.ASSISTANT:
                openai_messages.append(self._convert_assistant_message(msg))

            elif msg.role == MessageRole.SYSTEM:
                system_msg = ChatCompletionSystemMessageParam(
                    role="system", content=str(msg.content)
                )
                openai_messages.append(system_msg)

        return openai_messages

    def _convert_user_message(
        self, msg: ProviderMessage
    ) -> Union[ChatCompletionMessageParam, List[ChatCompletionMessageParam]]:
        """Convert a user message to OpenAI format, handling tool results and images.

        Returns either a single message or a list of messages when tool results
        contain images that need to be sent as separate user messages.
        """
        if isinstance(msg.content, str):
            user_msg: ChatCompletionUserMessageParam = {
                "role": "user",
                "content": msg.content,
            }
            return user_msg

        elif isinstance(msg.content, list):
            result_messages: List[ChatCompletionMessageParam] = []

            for item in msg.content:
                if isinstance(item, dict) and "tool_call_id" in item:
                    content_value = item.get("content", "")

                    if isinstance(content_value, dict) and content_value.get("type") == "image":
                        # OpenRouter/OpenAI doesn't support images in tool messages
                        # Send as tool result + user message with image
                        image_data = content_value.get("data", "")

                        tool_msg: ChatCompletionToolMessageParam = {
                            "role": "tool",
                            "tool_call_id": item["tool_call_id"],
                            "content": "Screenshot captured successfully. Image follows in next message.",
                        }
                        result_messages.append(tool_msg)

                        image_part: ChatCompletionContentPartImageParam = {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}",
                                "detail": "auto",
                            },
                        }

                        text_part: ChatCompletionContentPartTextParam = {
                            "type": "text",
                            "text": "Here is the screenshot that was captured:",
                        }

                        user_msg_with_image: ChatCompletionUserMessageParam = {
                            "role": "user",
                            "content": [text_part, image_part],
                        }
                        result_messages.append(user_msg_with_image)
                    else:
                        tool_msg = ChatCompletionToolMessageParam(
                            role="tool",
                            tool_call_id=item["tool_call_id"],
                            content=str(content_value) if content_value else "Success",
                        )
                        result_messages.append(tool_msg)
                else:
                    regular_user_msg: ChatCompletionUserMessageParam = {
                        "role": "user",
                        "content": str(item),
                    }
                    result_messages.append(regular_user_msg)

            return (
                result_messages
                if result_messages
                else [ChatCompletionUserMessageParam(role="user", content="")]
            )

        return ChatCompletionUserMessageParam(role="user", content=str(msg.content))

    def _convert_assistant_message(
        self, msg: ProviderMessage
    ) -> ChatCompletionAssistantMessageParam:
        """Convert an assistant message to OpenAI format with proper types."""
        assistant_msg: ChatCompletionAssistantMessageParam = {
            "role": "assistant",
            "content": msg.content if isinstance(msg.content, str) else None,
        }

        if msg.tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)},
                }
                for tc in msg.tool_calls
            ]

        return assistant_msg

    def _process_response(self, response: ChatCompletion) -> ProviderResponse:
        """Process OpenAI SDK response into ProviderResponse."""
        message = response.choices[0].message
        text_content = message.content

        tool_calls = None
        if message.tool_calls:
            tool_calls = [self._extract_tool_call(tc) for tc in message.tool_calls]

        return ProviderResponse(
            content=text_content,
            tool_calls=tool_calls,
            raw_response=response,
        )

    def _extract_tool_call(self, tool_call: Any) -> ToolCall:
        """Extract a ToolCall from OpenAI SDK's tool call format."""
        if hasattr(tool_call, "function"):
            arguments = {}
            if tool_call.function.arguments:
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    pass

            return ToolCall(
                id=tool_call.id,
                name=tool_call.function.name,
                arguments=arguments,
            )
        else:
            return ToolCall(
                id=getattr(tool_call, "id", "unknown"),
                name=getattr(tool_call, "name", "unknown"),
                arguments={},
            )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - close OpenAI client."""
        await self.client.close()
