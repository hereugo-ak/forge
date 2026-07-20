"""
HYPERION Google AI Studio Provider.

Google AI Studio provides Gemma and Gemini models via an OpenAI-compatible
API. This is our most abundant provider by RPD (~29,460/day) and serves
both the MICRO tier (Gemma workhorses) and the DEEP tier (Gemini long
context models). (§2.1)

Models on this provider:
- gemma-4-31b: MICRO — query gen, fact-check snippets, sub-agent quick tasks
- gemma-4-26b: MICRO — backup workhorse
- gemini-3.1-flash-lite: DEEP — deep context, long doc synthesis (500 RPD)
- gemini-3.5-flash: DEEP — reserve (20 RPD)
- gemini-3-flash: DEEP — reserve (20 RPD)

This is NOT a generic OpenAI client wrapper. It is the Google-specific
implementation that knows about Gemma's high RPD workhorse role and
Gemini's scarce DEEP-tier reserve role.
"""

from __future__ import annotations

from hyperion.config import ProviderType
from hyperion.router.providers.base import BaseProvider


class GoogleProvider(BaseProvider):
    """Google AI Studio provider — Gemma (MICRO) + Gemini (DEEP).

    The most abundant provider by RPD. Gemma models handle the high-volume
    MICRO tier work (query generation, fact-check snippets, sub-agent tasks)
    with 14,400 RPD each. Gemini models serve the DEEP tier for ultra-long
    context synthesis but are scarce (500/20/20 RPD) and must be preserved
    by the budget planner for critical tasks only.
    """

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.GOOGLE
