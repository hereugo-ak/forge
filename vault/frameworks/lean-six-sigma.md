---
title: "Lean / Six Sigma Process Framework"
created: "2026-07-19"
tags: [framework, operations, lean, six-sigma, sipoc, value-stream, bottleneck, capacity]
framework_type: "operations"
primary_agent: "operations_analyst"
---

# Lean / Six Sigma Process Framework

## Purpose
Map processes, identify bottlenecks, and drive operational improvement using Lean (eliminate waste) and Six Sigma (reduce variation).

## SIPOC (Supplier-Input-Process-Output-Customer)

| Step | Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|---|
| 1 | [Who] | [What] | [How] | [What] | [Who] |
| 2 | [Who] | [What] | [How] | [What] | [Who] |
| 3 | [Who] | [What] | [How] | [What] | [Who] |

## Value Stream Mapping
1. Map current state (all steps, delays, inventories)
2. Identify non-value-adding steps (the 8 wastes: DOWNTIME)
   - **D**efects
   - **O**verproduction
   - **W**aiting
   - **N**on-utilized talent
   - **T**ransportation
   - **I**nventory
   - **M**otion
   - **E**xcess processing
3. Design future state (eliminate waste)
4. Calculate cycle time efficiency: Value-added time / Total cycle time

## Six Sigma Metrics
- **DPMO**: Defects Per Million Opportunities
- **Process Sigma**: (1 - CDF(DPMO/1,000,000)) × shift factor
- Target: 6σ = 3.4 DPMO

| Sigma Level | DPMO | Yield |
|---|---|---|
| 1σ | 691,462 | 30.85% |
| 2σ | 308,538 | 69.15% |
| 3σ | 66,807 | 93.32% |
| 4σ | 6,210 | 99.38% |
| 5σ | 233 | 99.977% |
| 6σ | 3.4 | 99.99966% |

## Theory of Constraints
1. Identify the binding constraint (bottleneck)
2. Exploit it (maximize throughput at bottleneck)
3. Subordinate everything else to the bottleneck
4. Elevate the bottleneck (add capacity)
5. Repeat (the constraint moves)

## HYPERION Application
The Operations Analyst (Agent 8, STANDARD tier) uses SIPOC for process mapping, identifies bottlenecks using theory of constraints, and calculates process sigma levels. It designs KPI dashboards specific to the business — not generic metrics, but the 5-7 metrics that actually drive performance for this specific operational model.
