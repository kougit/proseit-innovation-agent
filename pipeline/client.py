"""Thin wrapper around the Anthropic Claude SDK."""
from __future__ import annotations
import anthropic

_DEFAULT_MODEL = "claude-sonnet-4-6"
_MAX_TOKENS = 8192


def call_claude(
    prompt: str,
    system: str = "",
    api_key: str = "",
    model: str = _DEFAULT_MODEL,
) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    kwargs: dict = {
        "model": model,
        "max_tokens": _MAX_TOKENS,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system
    msg = client.messages.create(**kwargs)
    return msg.content[0].text
