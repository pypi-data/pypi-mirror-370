import hashlib
import json
from functools import wraps
from typing import Callable

from pydantic_ai import ModelRetry
from pydantic_ai.messages import ModelMessage, ToolCallPart, UserPromptPart, ModelRequest

from django_ai_agent.models import Tool


def with_circuit_breaker(func: Callable) -> Callable:
    """
    Circuit breaker decorator that prevents agents from getting stuck in tool calling loops.

    Tracks sequential calls across different LLM responses:
    - max_calls: Maximum sequential calls to the same tool (any parameters)
    - max_identical_calls: Maximum sequential calls with identical parameters (stricter)

    Parallel calls (multiple tools in same LLM response) are always allowed.

    Args:
        func: The tool function to wrap

    Returns:
        Wrapped function with circuit breaker logic
    """

    @wraps(func)
    def wrapper(ctx, *args, **kwargs):
        tool_name = getattr(func, 'name', func.__name__)

        if not (tool_model := Tool.objects.filter(name=tool_name).first()):
            return func(ctx, *args, **kwargs)

        agent_run_messages = _get_agent_run_messages(ctx.messages)
        sequential_calls, sequential_identical_calls = _count_sequential_tool_calls(
            agent_run_messages, tool_name, args, kwargs
        )

        if max_calls := tool_model.max_calls:
            if sequential_calls > max_calls:
                raise ModelRetry(
                    f'Circuit breaker triggered: Tool "{tool_name}" has been called sequentially '
                    f'{sequential_calls} times across different responses. This appears to be a loop. '
                    f'Please try a different approach or ask for help.'
                )

        if max_identical_calls := tool_model.max_identical_calls:
            if sequential_identical_calls > max_identical_calls:
                raise ModelRetry(
                    f'Circuit breaker triggered: Tool "{tool_name}" has been called sequentially with identical '
                    f'parameters {sequential_identical_calls} times across different responses. This appears to be a loop. '
                    f'Please try different parameters or a different approach.'
                )

        return func(ctx, *args, **kwargs)

    return wrapper


def _get_agent_run_messages(messages: list[ModelMessage]) -> list[ModelMessage]:
    """
    Extract messages from the current agent run.

    Finds the last ModelRequest that has UserPrompt part and returns all messages after that.

    Args:
        messages: All conversation messages

    Returns:
        Messages from the current agent run
    """
    if not messages:
        return []

    last_user_prompt_index = -1
    for i in range(len(messages) - 1, -1, -1):
        message = messages[i]
        if isinstance(message, ModelRequest):
            for part in message.parts:
                if isinstance(part, UserPromptPart):
                    last_user_prompt_index = i
                    break
        if last_user_prompt_index != -1:
            break

    if last_user_prompt_index == -1:
        return messages

    return messages[last_user_prompt_index:]


def _count_sequential_tool_calls(
    messages: list[ModelMessage], tool_name: str, args: tuple, kwargs: dict
) -> tuple[int, int]:
    """
    Count sequential calls to the same tool across different LLM responses.

    Parallel calls (multiple tools in same response) don't count toward limits.
    Only sequential calls (same tool across different responses) are counted.

    Args:
        messages: Messages to analyze
        tool_name: Name of the tool to count
        args: Current call arguments
        kwargs: Current call keyword arguments

    Returns:
        Tuple of (sequential_calls, sequential_identical_calls)
    """
    current_params_hash = _hash_parameters(args, kwargs)

    responses_with_tool = []

    for message in messages:
        if not hasattr(message, 'kind') or message.kind != 'response' or not hasattr(message, 'parts'):
            continue

        tool_calls_in_response = []
        for part in message.parts:
            if isinstance(part, ToolCallPart) and part.tool_name == tool_name:
                try:
                    call_args = part.args_as_dict() if part.args else {}
                    call_params_hash = _hash_parameters((), call_args)
                    tool_calls_in_response.append(call_params_hash)
                except Exception:
                    tool_calls_in_response.append(None)

        if tool_calls_in_response:
            responses_with_tool.append(tool_calls_in_response)

    sequential_calls = len(responses_with_tool)

    sequential_identical_calls = 0
    for response_calls in responses_with_tool:
        if current_params_hash in response_calls:
            sequential_identical_calls += 1

    return sequential_calls, sequential_identical_calls


def _hash_parameters(args: tuple, kwargs: dict) -> str:
    """
    Create a hash of the function parameters to identify identical calls.

    Args:
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        SHA256 hash of the parameters
    """
    params_dict = {'args': args, 'kwargs': dict(sorted(kwargs.items()))}
    params_json = json.dumps(params_dict, sort_keys=True, default=str)
    return hashlib.sha256(params_json.encode()).hexdigest()[:16]  # Use first 16 chars for brevity
