from __future__ import annotations
from typing import Optional, Dict
from .providers import openai_context_window, anthropic_context_window, gemini_context_window

LOCAL_DEFAULTS: Dict[str, int] = {
    "gpt-4o": 128_000, "gpt-4.1": 128_000, "gpt-4.1-mini": 128_000, "gpt-4o-mini": 128_000, "o3": 200_000,
    "claude-3-7-sonnet": 200_000, "claude-3-5-sonnet": 200_000, "claude-3-5-haiku": 200_000,
}

def _loose(name: str, table: Dict[str,int]) -> Optional[int]:
    if name in table: return table[name]
    lo = name.lower()
    for k, v in table.items():
        if k in lo: return v
    return None

def get_context_limit(model: str, provider: Optional[str] = None, gemini_overrides: Optional[Dict[str,int]] = None) -> Optional[int]:
    prov = (provider or "").lower()
    if prov in {"openai","azure-openai"}:
        n = openai_context_window(model);  return n or _loose(model, LOCAL_DEFAULTS)
    if prov == "anthropic":
        n = anthropic_context_window(model);  return n or _loose(model, LOCAL_DEFAULTS)
    if prov in {"google","vertex","google-vertex"}:
        n = gemini_context_window(model, overrides=gemini_overrides);  return n or _loose(model, LOCAL_DEFAULTS)
    # provider unknown → try all, then fallback
    for fn in (openai_context_window, anthropic_context_window):
        n = fn(model)
        if n: return n
    n = gemini_context_window(model, overrides=gemini_overrides)
    return n or _loose(model, LOCAL_DEFAULTS)
