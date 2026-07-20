---
title: "DCF Valuation Framework"
created: "2026-07-19"
tags: [framework, financial, dcf, valuation, wacc, terminal-value]
framework_type: "financial"
primary_agent: "financial_analyst"
---

# Discounted Cash Flow (DCF) Valuation

## Purpose
Estimate the value of an investment based on its expected future cash flows, discounted to present value using the weighted average cost of capital (WACC).

## Steps

### 1. Project Free Cash Flows (5-10 years)
```
FCF = EBIT × (1 - Tax Rate) + D&A - CapEx - ΔWorking Capital
```

### 2. Calculate WACC
```
WACC = (E/V × Cost of Equity) + (D/V × Cost of Debt × (1 - Tax Rate))
```
- Cost of Equity: CAPM = Risk-free rate + β × Equity risk premium
- Risk-free rate: 10-year Treasury (pull from FRED)
- Equity risk premium: 4-6% (Damodaran estimates)
- Beta: Industry beta or regression of stock vs. market

### 3. Calculate Terminal Value
**Gordon Growth Method:**
```
TV = FCF_final × (1 + g) / (WACC - g)
```
- g: Long-term growth rate (2-3%, GDP-like)

**Exit Multiple Method:**
```
TV = EBITDA_final × Exit Multiple
```

### 4. Discount to Present Value
```
Enterprise Value = Σ (FCF_t / (1 + WACC)^t) + TV / (1 + WACC)^n
```

### 5. Bridge to Equity Value
```
Equity Value = Enterprise Value - Debt + Cash
Per Share = Equity Value / Shares Outstanding
```

## Sensitivity Analysis
Always run sensitivity on:
- WACC (±1-2%)
- Terminal growth rate (±0.5-1%)
- Revenue growth (±2-5%)

## HYPERION Application
The Financial Analyst (Agent 5, STANDARD+ tier) uses FRED for risk-free rates and macro data. Alpha Vantage provides financial statements. The DCF is always run with sensitivity analysis — a single point estimate is useless without understanding the range.
