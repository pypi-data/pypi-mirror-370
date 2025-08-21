"""This module contains the functions to generate the SSE response for the conversation."""

import logging
from datetime import datetime
from typing import Any, AsyncIterator

from axmp_ai_conversation_completor.scheme.chat_messages import (
    AIMessageDelta,
    BlockType,
    ChatRole,
    ChatStreamResponse,
    ContentBlock,
    DeltaType,
    EventStreamDataType,
    EventStreamMessage,
    EventStreamResponse,
    ToolCallsDelta,
    ToolMessageDelta,
)
from axmp_ai_conversation_completor.util.graph_stream_utils import sse_astream

logger = logging.getLogger(__name__)


async def generate_sse_response(
    response: AsyncIterator[dict[str, Any] | Any],
    thread_id: str,
    /,
    *,
    llm_model: str | None = None,
    stream_mode: str = "messages",
) -> AsyncIterator[EventStreamResponse]:
    """Generate the SSE response for the conversation."""
    try:
        yield EventStreamResponse(
            event=EventStreamDataType.MESSAGE_START,
            data=ChatStreamResponse(
                type=EventStreamDataType.MESSAGE_START,
                message=EventStreamMessage(
                    thread_id=thread_id,
                    type="message",
                    role=ChatRole.AI,
                    model=llm_model or "",
                    parent_uuid=None,
                    uuid=None,
                    content=[],
                    stop_reason=None,
                    stop_sequence=None,
                ),
            ),
        ).model_dump(mode="json", exclude_none=True)

        yield EventStreamResponse(
            event=EventStreamDataType.CONTENT_BLOCK_START,
            data=ChatStreamResponse(
                type=EventStreamDataType.CONTENT_BLOCK_START,
                content_block=ContentBlock(
                    type=BlockType.TEXT,
                    start_timestamp=datetime.now(),
                    stop_timestamp=None,
                    text=None,
                    citations=[],
                ),
            ),
        ).model_dump(mode="json", exclude_none=True)

        async for type, key, chunk, index in sse_astream(
            response, stream_mode=stream_mode
        ):
            if type == "ai_message":
                yield EventStreamResponse(
                    event=EventStreamDataType.CONTENT_BLOCK_DELTA,
                    data=ChatStreamResponse(
                        type=EventStreamDataType.CONTENT_BLOCK_DELTA,
                        delta=AIMessageDelta(
                            ai_message_type=type,
                            text=chunk,
                        ),
                    ),
                ).model_dump(mode="json", exclude_none=True)
            elif type == "tool_calls":
                if key == "tool_call_id":
                    yield EventStreamResponse(
                        event=EventStreamDataType.CONTENT_BLOCK_DELTA,
                        data=ChatStreamResponse(
                            type=EventStreamDataType.CONTENT_BLOCK_DELTA,
                            delta=ToolCallsDelta(
                                type=type,
                                tool_call_id=chunk,
                                index=index,
                            ),
                        ),
                    ).model_dump(mode="json", exclude_none=True)
                elif key == "name":
                    yield EventStreamResponse(
                        event=EventStreamDataType.CONTENT_BLOCK_DELTA,
                        data=ChatStreamResponse(
                            type=EventStreamDataType.CONTENT_BLOCK_DELTA,
                            delta=ToolCallsDelta(
                                type=type,
                                name=chunk,
                                index=index,
                            ),
                        ),
                    ).model_dump(mode="json", exclude_none=True)
                elif key == "args":
                    yield EventStreamResponse(
                        event=EventStreamDataType.CONTENT_BLOCK_DELTA,
                        data=ChatStreamResponse(
                            type=EventStreamDataType.CONTENT_BLOCK_DELTA,
                            delta=ToolCallsDelta(
                                type=type,
                                args=chunk,
                                index=index,
                            ),
                        ),
                    ).model_dump(mode="json", exclude_none=True)
            elif type == "tool_message":
                if key == "tool_call_id":
                    yield EventStreamResponse(
                        event=EventStreamDataType.CONTENT_BLOCK_DELTA,
                        data=ChatStreamResponse(
                            type=EventStreamDataType.CONTENT_BLOCK_DELTA,
                            delta=ToolMessageDelta(
                                ai_message_type=type,
                                tool_call_id=chunk,
                            ),
                        ),
                    ).model_dump(mode="json", exclude_none=True)
                elif key == "status":
                    yield EventStreamResponse(
                        event=EventStreamDataType.CONTENT_BLOCK_DELTA,
                        data=ChatStreamResponse(
                            type=EventStreamDataType.CONTENT_BLOCK_DELTA,
                            delta=ToolMessageDelta(
                                ai_message_type=type,
                                status=chunk,
                            ),
                        ),
                    ).model_dump(mode="json", exclude_none=True)
                elif key == "result":
                    yield EventStreamResponse(
                        event=EventStreamDataType.CONTENT_BLOCK_DELTA,
                        data=ChatStreamResponse(
                            type=EventStreamDataType.CONTENT_BLOCK_DELTA,
                            delta=ToolMessageDelta(
                                ai_message_type=type,
                                result=chunk,
                            ),
                        ),
                    ).model_dump(mode="json", exclude_none=True)

        yield EventStreamResponse(
            event=EventStreamDataType.CONTENT_BLOCK_STOP,
            data=ChatStreamResponse(
                type=EventStreamDataType.CONTENT_BLOCK_STOP,
                content_block=ContentBlock(
                    start_timestamp=None,
                    stop_timestamp=datetime.now(),
                    text=None,
                    citations=[],
                ),
            ),
        ).model_dump(mode="json", exclude_none=True)

        yield EventStreamResponse(
            event=EventStreamDataType.MESSAGE_STOP,
            data=ChatStreamResponse(
                type=EventStreamDataType.MESSAGE_STOP,
                message=EventStreamMessage(
                    thread_id=thread_id, type="message", role=ChatRole.AI
                ),
            ),
        ).model_dump(mode="json", exclude_none=True)

    except Exception as e:
        logger.error(f"Error in response_generator: {e}")

        yield EventStreamResponse(
            event=EventStreamDataType.CONTENT_BLOCK_DELTA,
            data=ChatStreamResponse(
                type=EventStreamDataType.CONTENT_BLOCK_DELTA,
                delta=AIMessageDelta(
                    type=DeltaType.AI_MESSAGE,
                    text=str(e),
                ),
            ),
        ).model_dump(mode="json", exclude_none=True)

        yield EventStreamResponse(
            event=EventStreamDataType.CONTENT_BLOCK_STOP,
            data=ChatStreamResponse(
                type=EventStreamDataType.CONTENT_BLOCK_STOP,
                content_block=ContentBlock(
                    start_timestamp=None,
                    stop_timestamp=datetime.now(),
                    text=None,
                    citations=[],
                ),
            ),
        ).model_dump(mode="json", exclude_none=True)

        yield EventStreamResponse(
            event=EventStreamDataType.MESSAGE_STOP,
            data=ChatStreamResponse(
                type=EventStreamDataType.MESSAGE_STOP,
                message=EventStreamMessage(
                    thread_id=thread_id, type="message", role=ChatRole.AI
                ),
            ),
        ).model_dump(mode="json", exclude_none=True)
