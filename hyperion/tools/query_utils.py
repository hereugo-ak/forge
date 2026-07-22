"""HYPERION — Query hygiene utilities.

Normalizes search queries before they hit the search stack, rejecting
junk queries (agent-name suffixes, number-only, currency-only, <3 tokens)
that leak from agent internals.

D3 fix: normalize_query() called before every search.
"""

from __future__ import annotations

import re

_INTERNAL_TOKENS = {
    "risk analyst", "technology analyst", "financial analyst", "market analyst",
    "competitive intel", "operations analyst", "regulatory analyst",
    "sustainability analyst", "innovation analyst", "consumer insights",
    "strategy analyst", "ma analyst",
}

_STOPISH = re.compile(r"^[\s\W\d%$.,]+$")


def normalize_query(q: str) -> str:
    """Normalize a search query — strip junk, reject thin queries.

    Returns empty string if the query is too thin to be a real search.
    """
    if not q:
        return ""
    s = q.strip()
    low = s.lower()

    # Strip agent-name suffixes that leaked in
    for tok in _INTERNAL_TOKENS:
        if low.endswith(tok):
            s = s[: len(s) - len(tok)].strip()
            low = s.lower()

    # Remove standalone currency/percent tokens
    s = re.sub(r"[$\u20ac\u00a3]\s?\d[\d,.\-\u2013\u2014]*\s?(?:[mbtk]|bn|billion|million|trillion)?", " ", s, flags=re.I)
    s = re.sub(r"\b\d[\d,.\-\u2013\u2014]*\s?%?\b", " ", s)
    s = re.sub(r"\s+", " ", s).strip()

    tokens = [t for t in s.split() if len(t) > 1]
    if len(tokens) < 3:
        return ""
    if _STOPISH.match(s):
        return ""

    return " ".join(tokens)[:256]
