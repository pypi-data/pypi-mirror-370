"""
Deprecated module. Use cli_arena.cache.anthropic.add_ephemeral_cache_controls instead.
This thin shim preserves backwards compatibility.
"""
from typing import Any, Dict, List

try:
    from litellm import Message  # type: ignore
except Exception:
    class Message:  # minimal placeholder for type
        content: str

from cli_arena.cache.anthropic import add_ephemeral_cache_controls as _impl


def add_anthropic_caching(messages: List[Dict[str, Any] | Message], model_name: str) -> List[Dict[str, Any] | Message]:
    return _impl(messages, model_name)
