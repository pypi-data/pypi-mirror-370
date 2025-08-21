# AXMP AI Conversation Completor

A Python library for handling Server-Sent Events (SSE) communication between clients and Large Language Models (LLMs). This library provides a robust way to stream AI responses and handle tool calls in real-time conversations.

## Features

- Server-Sent Events (SSE) streaming support
- Real-time AI message streaming
- Tool calls handling and streaming
- Structured response formatting
- Async/await support
- Type hints and validation using Pydantic models

## Installation

```bash
pip install axmp-ai-conversation-completor
```

## Quick Start

```python
from axmp_ai_conversation_completor import generate_sse_response

@router.post(
    "/conversations/{thread_id}/completion",
    summary="Chat with the alert AI agent",
    response_class=EventSourceResponse,
    response_model=EventStreamResponse,
)
async def conversations_completion(
    request: Request,
    aiops_chat_request: AIOpsChatRequest,
    thread_id: str = Path(..., description="Thread ID"),
) -> EventSourceResponse:
    """docstring..."""
    # some source...
    config = RunnableConfig(
        configurable=Configuration(
            thread_id=thread_id,
            user_id=user_id,
            model=llm_model,
            temperature=temperature,
            max_tokens=aiops_settings.chatops_model_max_tokens,
        ).model_dump(),
        recursion_limit=recursion_limit,
    )

    messages = [chat_request.prompt]

    inputs = ChatOpsState(
        messages=[
            HumanMessage(content=messages[0]),
        ]
    )

    response = chatops_agent.astream(inputs, config, stream_mode=stream_mode)

    return EventSourceResponse(
        generate_sse_response(
            response,
            thread_id,
            llm_model=llm_model,
            stream_mode=stream_mode
        )
    )
```

## API Reference

### `generate_sse_response(response, thread_id, *, llm_model=None, stream_mode="messages")`

Generates Server-Sent Events (SSE) responses for AI conversations.

**Parameters:**
- `response` (AsyncIterator[dict[str, Any] | Any]): The response iterator from the LLM
- `thread_id` (str): Unique identifier for the conversation thread
- `llm_model` (str | None): Name of the LLM model being used
- `stream_mode` (str): Mode of streaming, defaults to "messages"

**Returns:**
- AsyncIterator[EventStreamResponse]: An async iterator yielding SSE events

**Event Types:**
- MESSAGE_START: Indicates the start of a new message
- CONTENT_BLOCK_START: Indicates the start of a content block
- CONTENT_BLOCK_DELTA: Contains incremental updates to the content
- CONTENT_BLOCK_STOP: Indicates the end of a content block
- MESSAGE_STOP: Indicates the end of a message

## Project Structure

```
src/axmp_ai_conversation_completor/
├── __init__.py
├── completion/
│   └── sse_reponse_generator.py
├── scheme/
│   └── chat_messages.py
└── util/
    └── graph_stream_utils.py
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- [GitHub Issues](https://github.com/yourusername/axmp-ai-conversation-completor/issues)

## Authors

- Kilsoo Kang (kilsoo75@gmail.com)

## Acknowledgments

- Thanks to all contributors who have helped shape this library
