"""
HYPERION NVIDIA NIM Provider.

NVIDIA NIM provides Nemotron models via an OpenAI-compatible API. This is
our SCARCE provider — ~1,000 credits/month → ~33/day. It serves the
STRONG tier (Nemotron Super 120B for planning, writing, design) and the
DEEP tier (Nemotron Ultra 550B for ultra-long context). (§2.2)

Models on this provider:
- nvidia/nemotron-3-super-120b-a12b: STRONG — planning, writing, design
- nvidia/nemotron-3-ultra-550b-a55b: DEEP — deep reserve, ultra-long context
- nvidia/nemotron-3-nano-30b-a3b: STANDARD — research, sub-agents
- nvidia/llama-3.3-nemotron-super-49b-v1.5: STANDARD — backup standard

This is NOT a generic OpenAI client wrapper. It is the NVIDIA-specific
implementation that enforces scarcity-aware routing — the budget planner
preserves NVIDIA credits for STRONG/DEEP tier tasks only, and LOW urgency
tasks are routed to Google/Groq instead.
"""

from __future__ import annotations

from hyperion.config import ProviderType
from hyperion.router.providers.base import BaseProvider


class NvidiaProvider(BaseProvider):
    """NVIDIA NIM provider — Nemotron (STRONG, DEEP, STANDARD).

    The scarce provider. ~33 credits/day means every request is precious.
    The budget planner preserves this provider for STRONG and DEEP tier
    tasks — Engagement Director planning, Synthesis Lead reconciliation,
    Quality Gate scoring, and ultra-long context synthesis.

    STANDARD tier models (Nemotron Nano 30B, Llama-3.3 Nemotron Super 49B)
    are available but should only be used when Google/Groq STANDARD models
    are at capacity or the context window requires it.
    """

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.NVIDIA
