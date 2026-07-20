"""
HYPERION Mistral Provider.

Mistral AI provides the largest free-tier token budget (~1B tokens/month)
via their Experiment plan. OpenAI-compatible API at api.mistral.ai/v1.
This is our volume provider — 7 models across all 5 tiers, with the
highest TPM (500K) and no daily request cap. (§2.5)

Models on this provider:
- mistral-large-latest: STRONG — planning, writing, synthesis, quality gate
- mistral-medium-latest: STANDARD — research, analysis, structured output
- magistral-medium-latest: STRONG — reasoning (DCF, risk, game theory)
- magistral-small-latest: STANDARD — reasoning (fact-check, quality scoring)
- mistral-small-latest: FAST — fast extraction, sub-agent research
- devstral-latest: DEEP — 256K context, tool orchestration
- ministral-3b-latest: MICRO — quick lookups, simple classification

This is NOT a generic OpenAI client wrapper. It is the Mistral-specific
implementation that leverages Mistral's unique model diversity — the
reasoning models (Magistral) provide chain-of-thought capabilities that
no other free-tier provider offers, and Devstral's 256K context window
is the longest available on any free tier. The wait gate routes
reasoning-heavy tasks to Magistral and long-context tasks to Devstral.

Note: The free Experiment tier requires opting into data training. This
is acceptable for research and prototyping but should not be used with
sensitive client data. (§2.5)
"""

from __future__ import annotations

from hyperion.config import ProviderType
from hyperion.router.providers.base import BaseProvider


class MistralProvider(BaseProvider):
    """Mistral provider — Mistral, Magistral, Devstral, Ministral (all tiers).

    The volume provider. 7 models give the wait gate maximum flexibility:

    - STRONG reasoning: magistral-medium-latest (chain-of-thought for DCF, risk)
    - STRONG general: mistral-large-latest (flagship for synthesis, quality gate)
    - STANDARD reasoning: magistral-small-latest (fact-check logic, scoring)
    - STANDARD general: mistral-medium-latest (research, structured output)
    - FAST: mistral-small-latest (fast extraction, sub-agent tasks)
    - DEEP: devstral-latest (256K context — longest free-tier context window)
    - MICRO: ministral-3b-latest (quick lookups, simple classification)

    Mistral's ~1B tokens/month free quota is the largest of any provider.
    With 500K TPM and no RPD cap, this provider can absorb high-volume
    workloads that would exhaust Groq or Cerebras daily limits.
    """

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.MISTRAL
