---
title: "Risk Matrix & Monte Carlo"
created: "2026-07-19"
tags: [framework, risk, monte-carlo, risk-matrix, probability, impact]
framework_type: "risk"
primary_agent: "risk_analyst"
---

# Risk Matrix & Monte Carlo Simulation

## Purpose
Identify, score, and quantify risks. The Risk Matrix provides qualitative assessment; Monte Carlo provides quantitative probability distributions.

## Part 1: Risk Matrix

### Score each risk on two dimensions:

**Probability (1-5):**
| Score | Label | Description |
|---|---|---|
| 1 | Rare | <10% chance in 12 months |
| 2 | Unlikely | 10-30% chance |
| 3 | Possible | 30-50% chance |
| 4 | Likely | 50-70% chance |
| 5 | Almost Certain | >70% chance |

**Impact (1-5):**
| Score | Label | Description |
|---|---|---|
| 1 | Negligible | <1% revenue impact |
| 2 | Minor | 1-5% revenue impact |
| 3 | Moderate | 5-10% revenue impact |
| 4 | Major | 10-20% revenue impact |
| 5 | Severe | >20% revenue impact or existential |

### Risk Score = Probability × Impact (1-25)

| Score | Zone | Action |
|---|---|---|
| 15-25 | Red | Mitigate immediately |
| 8-14 | Amber | Mitigate within 90 days |
| 1-7 | Green | Monitor and accept |

## Part 2: Monte Carlo Simulation

### Steps:
1. Identify key variables (revenue growth, churn, CAC, etc.)
2. Assign probability distributions (normal, triangular, uniform)
3. Run 10,000+ simulations
4. Output: P5, P50, P90 outcomes
5. Report expected value + confidence intervals

### Key outputs:
- **P5 (Worst case)**: 5th percentile outcome
- **P50 (Base case)**: Median outcome
- **P90 (Best case)**: 90th percentile outcome
- **Probability of success**: % of simulations where NPV > 0

## HYPERION Application
The Risk Analyst (Agent 6, STANDARD tier) always runs both qualitative (risk matrix) and quantitative (Monte Carlo) assessments. It identifies the top 5 risks that account for 80% of downside exposure and provides specific mitigation strategies for each.
