"""
HYPERION Cerebras Provider.

Cerebras provides GPT-OSS 120B and Gemma 4 31B via an OpenAI-compatible
API. This is our FAST tier provider — 3000 TPS and 1850 TPS respectively,
making it the fastest inference option. However, it has strict limits:
5 RPM and 30K TPM per model, with 1M TPD. (§2.3)

Models on this provider:
- gpt-oss-120b: FAST — 3000 TPS, real-time extraction validation
- gemma-4-31b: FAST — 1850 TPS, backup fast

This is NOT a generic OpenAI client wrapper. It is the Cerebras-specific
implementation optimized for speed-aware routing. The wait gate's scoring
formula factors in the 3000 TPS speed when selecting between FAST tier
candidates — Cerebras wins on latency for time-critical tasks like
inline fact verification and real-time extraction validation.
"""

from __future__ import annotations

from hyperion.config import ProviderType
from hyperion.router.providers.base import BaseProvider


class CerebrasProvider(BaseProvider):
    """Cerebras provider — GPT-OSS 120B + Gemma 4 31B (FAST tier).

    The fastest inference provider. 3000 TPS on GPT-OSS 120B makes it
    ideal for the FAST tier — real-time extraction validation, inline
    fact verification, and any task where latency is critical.

    The 5 RPM limit is the binding constraint — the wait gate tracks this
    closely and routes to Groq or Google when Cerebras RPM is exhausted.
    The 1M TPD limit is generous and rarely binding.
    """

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.CEREBRAS
