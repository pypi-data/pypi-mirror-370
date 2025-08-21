"""Graph Stream Utils."""

from typing import AsyncGenerator, AsyncIterator, Literal

from langchain_core.messages import (
    AIMessageChunk,
    ToolMessage,
    ToolMessageChunk,
)
from langchain_core.runnables.schema import StreamEvent


async def sse_astream(
    response: AsyncIterator[StreamEvent], stream_mode: str
) -> AsyncGenerator[str, None]:
    """SSE stream the async stream event."""
    async for chunk_msg, metadata in response:
        # print(f"chunk_msg ::: {type(chunk_msg)}, type ::: {chunk_msg.type}")
        message_type: Literal["ai_message", "tool_calls", "tool_message"] | None = None

        # yield ai_message in tuple (type, key, chunk, index)
        if isinstance(chunk_msg, AIMessageChunk):
            ai_message_chunk: AIMessageChunk = chunk_msg

            if ai_message_chunk.content:
                message_type = "ai_message"
                if isinstance(ai_message_chunk.content, str):
                    yield (message_type, None, ai_message_chunk.content, None)
                elif isinstance(ai_message_chunk.content, list):
                    for content in ai_message_chunk.content:
                        if isinstance(content, dict):
                            if content.get("type") == "text":
                                yield (message_type, None, content["text"], None)
                        else:
                            yield (message_type, None, content, None)

            if ai_message_chunk.tool_call_chunks:
                message_type = "tool_calls"
                for tool_call_chunk in ai_message_chunk.tool_call_chunks:
                    if tool_call_chunk["id"]:
                        yield (
                            message_type,
                            "tool_call_id",
                            tool_call_chunk["id"],
                            tool_call_chunk["index"],
                        )
                    if tool_call_chunk["name"]:
                        yield (
                            message_type,
                            "name",
                            tool_call_chunk["name"],
                            tool_call_chunk["index"],
                        )
                    if tool_call_chunk["args"]:
                        yield (
                            message_type,
                            "args",
                            tool_call_chunk["args"],
                            tool_call_chunk["index"],
                        )

        elif isinstance(chunk_msg, ToolMessageChunk):
            # tool_message_chunk: ToolMessageChunk = chunk_msg
            # yield (tool_message_chunk.type, tool_message_chunk.content)
            ...
        elif isinstance(chunk_msg, ToolMessage):
            message_type = "tool_message"
            tool_message: ToolMessage = chunk_msg
            yield (message_type, "tool_call_id", tool_message.tool_call_id, None)
            yield (message_type, "status", tool_message.status, None)
            yield (message_type, "result", tool_message.content, None)
