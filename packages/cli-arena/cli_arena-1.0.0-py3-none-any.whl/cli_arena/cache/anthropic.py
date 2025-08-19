import copy
from typing import Any, Dict, List

try:
    from litellm import Message  # type: ignore
except Exception:
    class Message:  # minimal placeholder for type
        content: str


def add_ephemeral_cache_controls(messages: List[Dict[str, Any] | Message], model_name: str) -> List[Dict[str, Any] | Message]:
    """Add ephemeral cache control annotations to the last few Anthropic messages.

    Mirrors previous utils/anthropic_caching.add_anthropic_caching behavior, now unified under cache/.
    """
    if not ("anthropic" in model_name.lower() or "claude" in model_name.lower()):
        return messages

    cached_messages = copy.deepcopy(messages)
    for n in range(len(cached_messages)):
        if n >= len(cached_messages) - 3:
            msg = cached_messages[n]
            if isinstance(msg, dict):
                if isinstance(msg.get("content"), str):
                    msg["content"] = [{"type": "text", "text": msg["content"], "cache_control": {"type": "ephemeral"}}]
                elif isinstance(msg.get("content"), list):
                    for content_item in msg["content"]:
                        if isinstance(content_item, dict) and "type" in content_item:
                            content_item["cache_control"] = {"type": "ephemeral"}
            elif hasattr(msg, "content"):
                if isinstance(msg.content, str):  # type: ignore[attr-defined]
                    msg.content = [{"type": "text", "text": msg.content, "cache_control": {"type": "ephemeral"}}]  # type: ignore[attr-defined]
                elif isinstance(msg.content, list):
                    for content_item in msg.content:  # type: ignore[attr-defined]
                        if isinstance(content_item, dict) and "type" in content_item:
                            content_item["cache_control"] = {"type": "ephemeral"}
    return cached_messages


