---
title: "Quality Gate 10-Dimension Rubric"
created: "2026-07-19"
tags: [framework, quality, rubric, scoring, quality-gate, 10-dimensions]
framework_type: "quality"
primary_agent: "quality_gate"
---

# Quality Gate — 10-Dimension Rubric

## Purpose
Score every report on 10 dimensions before approval. If the weighted score is below the threshold (default 4.0/5.0), the report goes back for iteration (max 3 iterations).

## The 10 Dimensions

| # | Dimension | Weight | What it measures |
|---|---|---|---|
| 1 | Analytical Rigor | 15% | Are frameworks applied correctly? Is the logic sound? |
| 2 | Evidence Quality | 15% | Are claims backed by credible sources? Are sources cited? |
| 3 | Completeness | 10% | Are all relevant domains covered? Any obvious gaps? |
| 4 | Synthesis Quality | 15% | Does the report reconcile findings across agents? Are contradictions addressed? |
| 5 | Actionability | 10% | Can the client act on this? Are recommendations specific? |
| 6 | Data Accuracy | 10% | Are numbers correct? Do they reconcile across agents? |
| 7 | Visual Quality | 5% | Are charts clear, brand-compliant, 300 DPI? No chartjunk? |
| 8 | Citation Integrity | 5% | Are all sources traceable? Do sources actually contain the claimed data? |
| 9 | Bias Check | 10% | Is the analysis balanced? Does it present counterarguments? |
| 10 | Executive Summary | 5% | Does the summary capture the key recommendation and confidence level? |

## Scoring Scale (1-5 per dimension)

| Score | Label | Description |
|---|---|---|
| 5 | Excellent | Best-in-class, no improvements needed |
| 4 | Good | Meets standard, minor improvements possible |
| 3 | Adequate | Acceptable but with notable gaps |
| 2 | Below Standard | Significant issues that need fixing |
| 1 | Unacceptable | Major problems, report must be redone |

## Weighted Total
```
Weighted Total = Σ (dimension_score × weight) / 5.0
```
- **≥ 4.0**: Approved → proceed to PDF rendering
- **< 4.0**: Rejected → iteration loop (max 3)
- **After 3 iterations**: Escalate to Engagement Director for adaptive replanning

## Iteration Protocol
1. **Iteration 1**: Send back to weakest-scoring specialists with specific feedback
2. **Iteration 2**: Send back to Synthesis Lead with targeted re-synthesis instructions
3. **Iteration 3**: Full re-engagement with adapted DAG (Engagement Director intervention)
4. **After 3**: Escalate — deliver best-effort report with quality caveats

## HYPERION Application
The Quality Gate (Agent 18, STRONG tier) runs this rubric after the Synthesis Lead produces the FinalReport and the Fact Checker produces the FactCheckReport. It never approves a report below threshold without explicit escalation. The rubric is non-negotiable — no rubber-stamping.
