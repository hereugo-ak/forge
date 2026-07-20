---
title: "Source Credibility Scoring Reference"
created: "2026-07-19"
tags: [reference, sources, credibility, fact-checking, evidence-chain]
framework_type: "reference"
primary_agent: "fact_checker"
---

# Source Credibility Scoring Reference

## Credibility Hierarchy (§4.5, Agent 15)

| Tier | Label | Description | Weight | Examples |
|---|---|---|---|---|
| 1 | Peer-Reviewed | Academic papers, journal articles, systematic reviews | 1.00 | Nature, JAMA, Cochrane, NBER |
| 2 | Government | Official government data, statistics, regulatory filings | 0.90 | Census, SEC filings, FRED, FDA, RBI |
| 3 | Industry Report | Established analyst firms, market research | 0.75 | Gartner, IDC, McKinsey, BCG, Deloitte |
| 4 | Vendor | Vendor pricing/feature pages — factual but biased | 0.50 | AWS pricing page, Stripe API docs |
| 5 | News | Established news organizations | 0.40 | Reuters, Bloomberg, FT, WSJ, NYT |
| 6 | Blog | Individual or company blogs, opinion pieces | 0.20 | Medium, Substack, company engineering blogs |
| 7 | Social Media | User-generated content, forums, social posts | 0.10 | Reddit, Twitter, LinkedIn posts, Hacker News |

## Verification Rules (Agent 16 — Fact Checker)

### Claim Verification Status
| Status | Criteria | Action |
|---|---|---|
| **VERIFIED** | 2+ independent sources agree, at least one Tier 1-3 | Include with full confidence |
| **PLAUSIBLE** | 1 source Tier 1-3, or 2+ sources Tier 4-5 | Include with caveat |
| **UNVERIFIED** | Only Tier 5-7 sources, or single source | Flag to specialist for re-research |
| **CONTRADICTED** | Sources disagree | Flag to Synthesis Lead for reconciliation |

### Evidence Chain Validation
For each claim, trace: **claim → source → original data**
- If source doesn't contain the data → hallucinated citation (critical)
- If data doesn't support the claim → misinterpretation (major)
- If chain is incomplete → unverified (moderate)

### Statistical Sanity Checks
- Numbers too round (e.g., exactly $1B market) → suspicious
- Growth rates >100% CAGR without explanation → flag
- Market sizes that don't reconcile across agents → flag
- Percentages that don't sum to 100% → flag

## HYPERION Application
The Fact Checker (Agent 16, FAST tier on Cerebras) runs in parallel with late-stage specialists. It must finish before the Synthesis Lead starts. It catches hallucinated citations — the #1 quality risk in LLM-generated reports. The Research Librarian (Agent 15) formats citations according to this hierarchy and deduplicates sources.
