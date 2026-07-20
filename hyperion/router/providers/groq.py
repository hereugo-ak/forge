"""
HYPERION Groq Provider.

Groq provides Llama, GPT-OSS, and Qwen models via an OpenAI-compatible
API. This is our versatile provider — 6 models across MICRO and STANDARD
tiers, with varying RPM/TPM/RPD limits. It serves as the primary STANDARD
tier provider for research and analysis, and a MICRO backup. (§2.4)

Models on this provider:
- gpt-oss-120b: STANDARD — research, analysis (30 RPM, 8K TPM, 1K RPD)
- llama-3.3-70b-versatile: STANDARD — standard alt, higher TPM (12K TPM)
- llama-3.1-8b-instant: MICRO — micro backup, 14.4K RPD
- llama-4-scout-17b: STANDARD — high TPM tasks (30K TPM)
- qwen-3-32b: STANDARD — high RPM tasks (60 RPM)
- gpt-oss-20b: STANDARD — lightweight reasoning

This is NOT a generic OpenAI client wrapper. It is the Groq-specific
implementation that leverages Groq's model diversity — the wait gate
selects between Groq models based on the task's specific RPM vs TPM
requirements (qwen-3-32b for high-RPM tasks, llama-4-scout-17b for
high-TPM tasks, llama-3.3-70b for balanced workloads).
"""

from __future__ import annotations

from hyperion.config import ProviderType
from hyperion.router.providers.base import BaseProvider


class GroqProvider(BaseProvider):
    """Groq provider — Llama, GPT-OSS, Qwen (MICRO + STANDARD).

    The versatile provider. 6 models give the wait gate flexibility to
    match the right model to the task's RPM/TPM profile:

    - High RPM (many small requests): qwen-3-32b (60 RPM)
    - High TPM (large context): llama-4-scout-17b (30K TPM)
    - Balanced: gpt-oss-120b or llama-3.3-70b-versatile
    - MICRO backup: llama-3.1-8b-instant (14.4K RPD)

    Groq is the second-most abundant provider by RPD (~18,400/day) and
    serves as the primary STANDARD tier workhorse alongside NVIDIA.
    """

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.GROQ
