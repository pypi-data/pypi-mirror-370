from __future__ import annotations
from typing import Any, Iterable, Dict

from .counter import count_text, count_messages
from .limits import get_context_limit
from .analytics import analyze_messages, split_prompt_completion, summarize_provider_usage

class ContextInspector:
    def __init__(self, provider: str | None = None, gemini_overrides: dict | None = None):
        self.provider = provider
        self._gemini_overrides = gemini_overrides or {}

    def get_limit(self, model: str) -> int | None:
        return get_context_limit(model, provider=self.provider, gemini_overrides=self._gemini_overrides)

    def count_text(self, text: str, model: str | None = None) -> int:
        return count_text(text, model=model, provider=self.provider)

    def count_messages(self, messages: Iterable[Dict[str, Any]], model: str | None = None) -> int:
        return count_messages(messages, model=model, provider=self.provider)

    def will_exceed(self, tokens: int, model: str, reserve: int = 1024) -> bool | None:
        limit = self.get_limit(model)
        return None if limit is None else (tokens + reserve > limit)

__all__ = [
    "ContextInspector",
    "count_text",
    "count_messages",
    "get_context_limit",
    "analyze_messages",
    "split_prompt_completion",
    "summarize_provider_usage",
]
