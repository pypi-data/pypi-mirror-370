import asyncio
from typing import Awaitable, Callable, Generic, List, TypeVar

from mirrai.core.execution.events.types import (
    ErrorEvent,
    ExecutionEvent,
    IterationEvent,
    MessageEvent,
    StatusChangeEvent,
    ToolUseEvent,
)

T = TypeVar("T", bound=ExecutionEvent)


class TypedEventEmitter(Generic[T]):
    """Type-safe event emitter for a specific event type."""

    def __init__(self):
        self._sync_handlers: List[Callable[[T], None]] = []
        self._async_handlers: List[Callable[[T], Awaitable[None]]] = []

    def on(self, handler: Callable[[T], None]) -> None:
        """Register a synchronous event handler."""
        self._sync_handlers.append(handler)

    def on_async(self, handler: Callable[[T], Awaitable[None]]) -> None:
        """Register an async event handler."""
        self._async_handlers.append(handler)

    def off(self, handler: Callable[[T], None]) -> None:
        """Unregister a synchronous event handler."""
        if handler in self._sync_handlers:
            self._sync_handlers.remove(handler)

    def off_async(self, handler: Callable[[T], Awaitable[None]]) -> None:
        """Unregister an async event handler."""
        if handler in self._async_handlers:
            self._async_handlers.remove(handler)

    def emit(self, event: T) -> None:
        """Emit an event to all synchronous handlers."""
        for handler in self._sync_handlers:
            handler(event)

    async def emit_async(self, event: T) -> None:
        """Emit an event to all async handlers."""
        if not self._async_handlers:
            return

        tasks = [handler(event) for handler in self._async_handlers]
        await asyncio.gather(*tasks, return_exceptions=True)


class ExecutionEventEmitter:
    """Manages typed event emitters for execution updates."""

    def __init__(self):
        self.all: TypedEventEmitter[ExecutionEvent] = TypedEventEmitter()
        self.messages: TypedEventEmitter[MessageEvent] = TypedEventEmitter()
        self.tool_uses: TypedEventEmitter[ToolUseEvent] = TypedEventEmitter()
        self.status_changes: TypedEventEmitter[StatusChangeEvent] = TypedEventEmitter()
        self.errors: TypedEventEmitter[ErrorEvent] = TypedEventEmitter()
        self.iterations: TypedEventEmitter[IterationEvent] = TypedEventEmitter()

    def emit(self, event: ExecutionEvent) -> None:
        """Emit an event to the appropriate typed emitter (and 'all' emitter)."""
        if isinstance(event, MessageEvent):
            self.messages.emit(event)
        elif isinstance(event, ToolUseEvent):
            self.tool_uses.emit(event)
        elif isinstance(event, StatusChangeEvent):
            self.status_changes.emit(event)
        elif isinstance(event, ErrorEvent):
            self.errors.emit(event)
        elif isinstance(event, IterationEvent):
            self.iterations.emit(event)

        self.all.emit(event)

    async def emit_async(self, event: ExecutionEvent) -> None:
        """Emit an event to the appropriate typed emitter (and 'all' emitter) asynchronously."""
        tasks = []

        if isinstance(event, MessageEvent):
            tasks.append(self.messages.emit_async(event))
        elif isinstance(event, ToolUseEvent):
            tasks.append(self.tool_uses.emit_async(event))
        elif isinstance(event, StatusChangeEvent):
            tasks.append(self.status_changes.emit_async(event))
        elif isinstance(event, ErrorEvent):
            tasks.append(self.errors.emit_async(event))
        elif isinstance(event, IterationEvent):
            tasks.append(self.iterations.emit_async(event))

        tasks.append(self.all.emit_async(event))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
