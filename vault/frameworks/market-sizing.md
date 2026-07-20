---
title: "Market Sizing — TAM/SAM/SOM"
created: "2026-07-19"
tags: [framework, market, tam, sam, som, sizing, bottom-up, top-down]
framework_type: "market"
primary_agent: "market_analyst"
---

# Market Sizing: TAM / SAM / SOM

## Purpose
Estimate market size using two independent methods (bottom-up and top-down) and reconcile. Never rely on a single method.

## Definitions

- **TAM (Total Addressable Market)**: Total market demand for the product/service if 100% market share were achieved
- **SAM (Serviceable Addressable Market)**: Portion of TAM that the company's business model can reach
- **SOM (Serviceable Obtainable Market)**: Portion of SAM the company can realistically capture (1-3 year horizon)

## Bottom-Up Approach (Primary)
```
TAM = Number of target customers × Annual revenue per customer
SAM = TAM × % reachable by business model
SOM = SAM × realistic market share % (based on competition, resources, timeline)
```

### Inputs needed:
- Customer count by segment (from census data, industry reports)
- Average spend per customer (from pricing analysis, surveys)
- Geographic filter (SAM only)
- Channel filter (SAM only)

## Top-Down Approach (Validation)
```
TAM = Total market revenue × % applicable to our segment
```
### Inputs needed:
- Industry report market size (Gartner, IDC, Statista, etc.)
- Segment % of total market
- Growth rate (CAGR)

## Reconciliation
- If bottom-up and top-down differ by >20%, investigate the gap
- Bottom-up is usually more accurate but harder to source
- Top-down is easier but less precise
- Present both with confidence intervals

## HYPERION Application
The Market Analyst (Agent 3, STANDARD tier) always runs both methods. It uses SearxNG for industry reports, Jina for extracting market data, and Obscura for scraping paywalled databases. Sub-agents (MICRO tier) handle individual data point collection (e.g., "Find number of SMEs in Tier-2 Indian cities").
