"""This module defines the data structures for chat messages.

The data structures are used to define the data structures for chat messages.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Literal

from pydantic import BaseModel, Field


class ChatRole(str, Enum):
    """The role of a message."""

    HUMAN = "human"
    AI = "ai"
    SYSTEM = "system"
    TOOL = "tool"


class ChatRequest(BaseModel):
    """A request for a chat, which has a thread_id and a list of messages."""

    locale: str | None = Field(default="ko_KR")
    timezone: str | None = Field(default="Asia/Seoul")
    files: List[str] | None = Field(default=None)
    prompt: str | None = Field(default=None)
    llm_model: str | None = Field(default="openai/gpt-4o")
    project_id: str | None = Field(
        default=None,
        description="The project ID. If the conversation is the project chat, the project ID is required.",
    )
    base_url: str | None = Field(
        default=None,
        description="The base URL for the chat. If the conversation uses a private LLM, the base URL is required.",
    )


class AIOpsChatRequest(BaseModel):
    """A request for a chat, which has a thread_id and a list of messages."""

    # thread_id: str | None = Field(default=None, description="Thread ID")
    alert_id: str = Field(..., description="Alert ID")
    alert_message: str = Field(..., description="Alert message")
    alert_priority: str = Field(..., description="Alert priority")


class EventStreamDataType(str, Enum):
    """The type of a message."""

    MESSAGE_START = "message_start"
    MESSAGE_STOP = "message_stop"
    # MESSAGE_DELTA = "message_delta"
    CONTENT_BLOCK_START = "content_block_start"
    CONTENT_BLOCK_STOP = "content_block_stop"
    CONTENT_BLOCK_DELTA = "content_block_delta"


class EventStreamMessage(BaseModel):
    """A message in a stream."""

    thread_id: str = Field(..., description="Thread ID", min_length=1, max_length=255)
    type: Literal["message"] = Field(default="message")
    role: ChatRole | None = Field(default=ChatRole.AI)
    model: str | None = Field(default=None)
    parent_uuid: str | None = Field(default=None)
    uuid: str | None = Field(default=None)
    content: List[str] = Field(default_factory=list)
    stop_reason: str | None = Field(default=None)
    stop_sequence: str | None = Field(default=None)


class BlockType(str, Enum):
    """The type of a content block."""

    TEXT = "text"
    IMAGE = "image"
    FILE = "file"


class ContentBlock(BaseModel):
    """A content block, which has a type and a content."""

    start_timestamp: datetime | None = Field(default=None)
    stop_timestamp: datetime | None = Field(default=None)
    type: BlockType = Field(default=BlockType.TEXT)
    text: str | None = Field(default=None)
    citations: List[str] = Field(default_factory=list)


class DeltaType(str, Enum):
    """The type of a delta."""

    AI_MESSAGE = "ai_message"
    TOOL_MESSAGE = "tool_message"
    TOOL_CALLS = "tool_calls"


class BaseDelta(BaseModel):
    """A delta for a content block."""

    type: DeltaType
    text: str | None = Field(default=None)


class AIMessageDelta(BaseDelta):
    """A delta for a text content block."""

    type: DeltaType = Field(default=DeltaType.AI_MESSAGE)


class ToolCallsDelta(BaseDelta):
    """A tool call."""

    type: DeltaType = Field(default=DeltaType.TOOL_CALLS)
    tool_call_id: str | None = Field(default=None)
    name: str | None = Field(default=None)
    args: str | None = Field(default=None)
    index: int | None = Field(default=None)


class ToolMessageDelta(BaseDelta):
    """A delta for a tool call content block."""

    type: DeltaType = Field(default=DeltaType.TOOL_MESSAGE)
    tool_call_id: str | None = Field(default=None)
    status: str | None = Field(default=None)
    result: str | None = Field(default=None)


class ChatStreamResponse(BaseModel):
    """A response for a chat stream, which has a type, index, delta, content_block, and message."""

    type: EventStreamDataType
    index: int | None = Field(default=None)
    delta: AIMessageDelta | ToolMessageDelta | ToolCallsDelta | None = Field(
        default=None
    )  # for type is content_block_delta
    content_block: ContentBlock | None = Field(
        default=None
    )  # for type is content_block_start or content_block_stop
    message: EventStreamMessage | None = Field(
        default=None
    )  # for type is message_start or message_stop


class EventStreamResponse(BaseModel):
    """A response for an event stream, which has an event and data."""

    event: EventStreamDataType
    data: ChatStreamResponse
