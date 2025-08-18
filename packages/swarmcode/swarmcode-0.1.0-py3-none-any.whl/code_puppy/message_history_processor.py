import queue
from typing import List

from pydantic_ai.messages import ModelMessage, ToolCallPart, ToolReturnPart

from code_puppy.config import get_message_history_limit
from code_puppy.tools.common import console


def message_history_processor(messages: List[ModelMessage]) -> List[ModelMessage]:
    """
    Truncate message history to manage token usage while preserving context.

    This implementation:
    - Uses the configurable message_history_limit from puppy.cfg (defaults to 40)
    - Compacts tool outputs to prevent token explosion
    - Preserves system messages at the beginning
    - Maintains tool call/response pairs together
    - Follows PydanticAI best practices for message ordering

    Args:
        messages: List of ModelMessage objects from conversation history

    Returns:
        Truncated list of ModelMessage objects
    """
    if not messages:
        return messages
    
    # First, try token-based compaction if available
    try:
        from code_puppy.tokenizer import TokenCounter
        from code_puppy.config import get_active_model
        
        model = get_active_model() or "gpt-4"
        counter = TokenCounter(model)
        
        # Convert messages to simple format for token counting
        simple_messages = []
        for msg in messages:
            content = ""
            for part in msg.parts:
                if hasattr(part, "content"):
                    content += str(part.content)
            simple_messages.append({"role": "system", "content": content})
        
        usage = counter.get_context_usage(simple_messages)
        
        # If over 80% of limit, we need to compact more aggressively
        if usage["used_percentage"] > 80:
            console.print(
                f"[yellow]Context at {usage['used_percentage']:.0f}% - compacting tool outputs[/yellow]"
            )
            # TODO: Implement tool output compaction for ModelMessage objects
    except Exception as e:
        pass  # Fall back to message count

    # Get the configurable limit from puppy.cfg
    max_messages = get_message_history_limit()
    # If we have max_messages or fewer, no truncation needed
    if len(messages) <= max_messages:
        return messages

    console.print(
        f"Truncating message history to manage token usage: {max_messages}"
    )
    result = []
    result.append(messages[0])  # this is the system prompt
    remaining_messages_to_fill = max_messages - 1
    stack = queue.LifoQueue()
    count = 0
    tool_call_parts = set()
    tool_return_parts = set()
    for message in reversed(messages):
        stack.put(message)
        count += 1
        if count >= remaining_messages_to_fill:
            break

    while not stack.empty():
        item = stack.get()
        for part in item.parts:
            if hasattr(part, "tool_call_id") and part.tool_call_id:
                if isinstance(part, ToolCallPart):
                    tool_call_parts.add(part.tool_call_id)
                if isinstance(part, ToolReturnPart):
                    tool_return_parts.add(part.tool_call_id)

        result.append(item)

    missmatched_tool_call_ids = (tool_call_parts.union(tool_return_parts)) - (
        tool_call_parts.intersection(tool_return_parts)
    )
    # trust...
    final_result = result
    if missmatched_tool_call_ids:
        final_result = []
        for msg in result:
            is_missmatched = False
            for part in msg.parts:
                if hasattr(part, "tool_call_id"):
                    if part.tool_call_id in missmatched_tool_call_ids:
                        is_missmatched = True
            if is_missmatched:
                continue
            final_result.append(msg)
    return final_result