# HYPERION — Vision, Deep Audit & End-to-End Fix Plan
**Date:** 2026-07-23
**Status:** Diagnosis complete · Fix plan ready for implementation
**Constraint:** 100% free / zero-cost tooling (no Tavily, Exa, or any paid search/API). If no single free tool can do a job, compose several free ones.

---

## PART A — WHO WE ARE & WHAT WE WANT

### A.1 Who we are
We are building **Hyperion** — a proprietary, multi-agent AI consulting system that is the engine of a future **Hyperion consulting firm**. Hyperion takes a single strategic question (e.g. *"Should India enter blockchain?"*, *"Should Hexsense Labs vertically integrate raw-material manufacturing?"*) and autonomously runs a full consulting engagement: it plans the work, dispatches specialist agents (technology, financial, regulatory, innovation, market, risk), gathers real-world evidence, synthesizes a recommendation, and delivers a polished report.

### A.2 What we want — the definition of done
We want the output to be an **absolute best-in-class, McKinsey/BCG-grade, deep-context report** — indistinguishable in rigor and polish from what a top-tier MBB (McKinsey, BCG, Bain) engagement team would hand a C-suite client. Concretely, every Hyperion report must be:

1. **Evidence-grounded** — every number, claim, and recommendation traces to a *real, relevant* source with a working URL. Zero fabrication. Zero irrelevant sources (no "Best Buy" as a source for a blockchain report).
2. **Deep & MECE** — genuine analytical depth using real consulting frameworks (Pyramid Principle, SCQA, Porter's Five Forces, VRIO, DCF, sensitivity analysis), structured Mutually Exclusive & Collectively Exhaustive.
3. **Decision-ready** — a single, unambiguous recommendation (GO / CONDITIONAL / NO-GO) that is internally consistent across the cover, executive summary, and body, with honest, evidence-derived confidence.
4. **Pixel-perfect** — delivered as a **true paginated PDF** (not a webpage), with MBB-grade typography, action titles, exhibits/charts, high-contrast text, unique purposeful imagery, and source footnotes.
5. **Free-only** — produced entirely on a zero-cost tool stack.

**Guiding principle: quality over time.** A 30- or 60-minute run that produces a genuinely excellent report beats a fast run that produces fluent-but-fabricated filler. Time is not a constraint; trustworthiness and polish are the bar.

### A.3 Where we are today (the gap)
Two recently generated reports were audited in depth. The prose reads well, but the reports are **fluent English wrapped around missing or fake data**: fabricated numbers, irrelevant sources (Best Buy, MGP Ingredients, a Greek e-shop), leaked raw Python dicts (`{'name':'DCF Valuation','value':'Unknown',...}`), placeholder lines ("So What? No specific implications stated."), a NO-GO-vs-CONDITIONAL self-contradiction, broken `?jurisdiction=None` URLs, repeated cover images, and — critically — the deliverable is a raw HTML webpage, not a PDF. This document explains exactly why, defines the MBB target, and lays out the end-to-end fix.

---

## PART B — THE TARGET: WHAT AN MBB-GRADE REPORT ACTUALLY LOOKS LIKE

This is the concrete standard Hyperion output must match. Sourced from analysis of McKinsey, BCG, and Bain report/deck conventions.

### B.1 Narrative architecture — the Pyramid Principle (Barbara Minto)
MBB communication is **top-down**: state the answer first, then the arguments, then the data.
- **Layer 1 — Governing thought:** the single main recommendation (the report's thesis).
- **Layer 2 — Key arguments:** 3–5 MECE arguments that support the thesis (each becomes a section).
- **Layer 3 — Supporting data:** the evidence, exhibits, and analysis under each argument.
- Every layer **summarizes the layer below it.** The reader can stop at any level and still have a coherent answer.

### B.2 SCQA opening (the executive summary spine)
- **Situation** — the accepted context / status quo.
- **Complication** — what changed or what's at stake (the tension).
- **Question** — the decision the client faces.
- **Answer** — the recommendation (lead with it).

### B.3 Action titles (the single most important habit)
Every section/exhibit headline is a **complete sentence stating the conclusion**, not a topic label.
- ❌ "Market Landscape"  → ✅ "The $2B TAM is only viable above 8% penetration; below that, unit economics collapse."
- ❌ "Financials"        → ✅ "A phased BUY strategy reaches breakeven in 30 months at a 12% discount rate."
Action titles are: complete sentences (subject-verb-object), specific (include numbers), interpretive (say what it means), concise (10–30 words).

### B.4 MECE & real frameworks
Arguments are **Mutually Exclusive, Collectively Exhaustive** — no overlaps, no gaps. Analysis uses genuine frameworks appropriate to the question: Porter's Five Forces, VRIO, PESTEL, BCG growth-share matrix, DCF with sensitivity ranges, scenario/Monte-Carlo, value-driver trees. Frameworks must be *populated with real data*, not name-dropped.

### B.5 Exhibits (charts do the talking)
Each key argument is carried by an **exhibit** (chart/table/framework diagram), not a wall of text. MBB exhibit conventions:
- One message per exhibit; the action title states that message.
- Minimal chart junk: light gray gridlines, small axis labels, direct data labels.
- Charts used: waterfall, Marimekko/Mekko, growth-share matrix, stacked bar, sensitivity tornado, football-field valuation range.
- **Every exhibit has a source footnote.**

### B.6 Visual & typographic standard
| Element | Convention |
|---|---|
| Palette | Restrained, brand-consistent. (McKinsey deep teal `#034641`; BCG navy `#003366`; Bain red `#CC0000`.) Hyperion has its own warm palette — keep it consistent and high-contrast. Red reserved for warnings/negatives. |
| Type scale | Title 28–36pt · Subtitle 18–20pt · Body 11–12pt · Annotation 9–10pt · Footnote 7–8pt |
| Layout | Asymmetric: large exhibit ≈ two-thirds, action title/insight ≈ one-third. Two-column exhibit+bullets also common. |
| White space | Generous; one message per page; no cognitive overload. |
| Contrast | Text must meet **WCAG-AA (≥ 4.5:1)**; never rely on a photo for legibility — use a scrim/solid panel. |
| Sources | Footnoted at the bottom of every page/exhibit that makes a claim. |
| Appendix | Methodology, full source list, detailed models pushed to an appendix so the narrative stays clean. |

### B.7 Structure of a full report (Hyperion target ToC)
1. **Cover** — title = the question; the recommendation badge; date; confidentiality line; one purposeful hero image.
2. **Executive Summary** — SCQA + the recommendation + 3–5 key findings + confidence, all on ~1 page.
3. **Sections (one per key argument)** — each led by an action title, carried by an exhibit, ending with an explicit **"So What?"** (implication + recommended action).
4. **Risk Analysis** — ranked risks, likelihood × impact, mitigations.
5. **Recommendation & Roadmap** — phased plan, decision triggers, what would change the answer.
6. **Methodology** — agents used, frameworks, data-collection approach, limitations.
7. **Appendix** — full source list (with credibility ratings), detailed models, data tables.

---

## PART C — DEEP AUDIT: WHY TODAY'S OUTPUT FAILS THE BAR

Five independent, compounding failures. In severity order.

### C.1 CORE — The web data layer is brittle SERP-scraping, not search
`hyperion/tools/searxng.py` — despite the name — no longer uses SearXNG (lines 214–215: *"SearxNG container and Jina are NOT used — they were unreliable."*). The real chain in `search()` is:
- **Primary:** FlareSolverr → scrapes `google.com/search` & `duckduckgo.com/html`, regex/BS4-parses the SERP HTML.
- **Fallback:** Playwright stealth Bing.
- **Last resort:** Jina.
- **Else:** returns empty `SearchResponse(results=[])`.

**Why it produces garbage:**
- Scraping Google/Bing SERPs is unstable and anti-botted; the HTML parser silently returns ads/shopping tiles (Best Buy, MGP Ingredients) or `[]` when layouts shift.
- Every failure is swallowed (`except Exception: logger.warning`) — the agent above never learns search failed; it just gets nothing and writes around the void.
- No relevance filtering, no domain allow/deny list, no result scoring.
- The real SearXNG is broken anyway: `searxng_settings.yml` uses `use_default_settings: true` but omits `doi_resolvers`/`default_doi_resolver`, so SearXNG `2026.7.19` raises `KeyError: 'default_doi_resolver'` (HTTP 500) on every `/search`.

**This is the root cause of almost everything downstream:** no real data → agents fabricate (Report 1's invented $2B TAM, "Primary Survey Q2 2023") or honestly flag voids but still ship (Report 2's "NO-GO due to critical data voids").

### C.2 The report is delivered as raw HTML, not a PDF
- The delivered file is literally named `..._playwright.html` — produced by one line, `render.py:375` `temp_html = output_path.replace(".pdf", "_playwright.html")`, inside the Playwright **fallback**. You received the **intermediate scratch HTML**, not a PDF.
- `import weasyprint` → **ModuleNotFoundError**. WeasyPrint (declared in `pyproject.toml`) is not installed, so `render_pdf()` Attempt 1 throws instantly and is caught at `render.py:487`.
- Attempt 2 (Playwright Chromium) writes the temp HTML, then `page.pdf()` fails → returns `False`, but the temp `.html` is already on disk and gets handed off.
- The HTML carries print-only CSS (3 `@page` blocks, 11 `A4` refs, `page-break-*`) that **browsers ignore** → it scrolls like a website; the `.cover` div becomes a hero banner.
- Report #2's stylesheet is an absolute `C:\Users\Abuza\CascadeProjects\...css` link that loads on no other machine → unstyled, low-contrast text.

### C.3 Raw schema objects leak into the body
`hyperion/output/markdown.py:176`:
```python
for key, value in metrics.items():
    lines.append(f"| {key} | {value} |")
```
When `value` is a DataPoint dict, `f"{value}"` dumps `{'name':'DCF Valuation','value':'Unknown','unit':'$','low_estimate':None,...}` straight into a table cell — and even into a "So What?" slot (`So What? DCF Valuation: {'name':...}`).

### C.4 Placeholders, `None` URLs, and the verdict contradiction
- Filler survives to delivery: "So What? No specific implications stated.", "Competitive analysis gap — no competitors identified."
- URLs interpolate unset fields: `https://www.govinfo.gov/regulations?jurisdiction=None`, `Regulatory database — None`.
- **Contradiction:** Report #2 cover badge = **CONDITIONAL**, body = **NO-GO**. Two verdict sources, never reconciled. Confidence is labeled "HIGH" even when data is admittedly absent.

### C.5 Repeated images + poor contrast
`presentation_designer.py:987` derives the cover search term from a tiny static dict; on no match it falls back to one generic term (`"modern business abstract"`) and always picks `search_result.images[0]` (line 1008). Same for sections (1061/1072). Result: **the same image every time**, captioned `Source: Unsplash via {photographer}`. Combined with the missing/absolute CSS, text has poor contrast against images.

### C.6 Content verdict (from reading both reports)
- **Report 1 (India/blockchain, 4,521 words):** good prose; **fabricated data**; **5 sources, all irrelevant** (Best Buy, franchise site, Greek e-shop, FRED, MGP Ingredients); duplicated findings; placeholder "So What?".
- **Report 2 (Hexsense Labs, 12,493 words):** excellent framework prose (VRIO, Porter, game theory, ESG); **self-admitted data voids**; **leaked raw dicts**; **CONDITIONAL vs NO-GO contradiction**; broken `=None` URLs.
- **Bottom line:** fluent but **not trustworthy**. An MBB reader rejects both — not for writing, but because the evidence is fake/irrelevant/absent and the artifact leaks internals and contradicts itself.

---

## PART D — END-TO-END FIX PLAN

The fix is organized as **five layers**, mapped to the failures above, then sequenced. Each layer states *goal → concrete changes → files → done-when*.

### Layer 1 — Reliable free data acquisition (the foundation)
**Goal:** every agent gets real, relevant, cited evidence — from free tools only, composed in parallel.

1. **Repair SearXNG** so the hub stops 500-ing.
   - Add to `searxng_settings.yml`:
     ```yaml
     default_doi_resolver: 'oadoi.org'
     doi_resolvers:
       oadoi.org: 'https://oadoi.org/'
     ```
   - Silence botdetection for localhost (trusted proxy / `X-Forwarded-For`) or disable it for the internal client.
   - **Pin the image tag** in `docker-compose.yml` (currently `searxng/searxng:latest` → non-reproducible; the breaking `default_doi_resolver` requirement arrived in a recent build). Pin a known-good tag.
2. **Rewrite `searxng.py` into a true multi-source orchestrator** — SearXNG JSON API first, then fan out **in parallel** to the free specialist APIs already in the repo, then **merge + dedupe + relevance-score**:
   - *Academic/technical:* OpenAlex, Semantic Scholar, arXiv (via SearXNG).
   - *Finance/econ:* SEC EDGAR, FRED, World Bank, Alpha Vantage.
   - *Signal/discussion:* HackerNews, Reddit, Google Trends.
   - *General web + full text:* SearXNG → crawl4ai / jina / scrapling to fetch and extract full page bodies (not just snippets).
   - *CAPTCHA-only fallback:* FlareSolverr used to fetch specific blocked URLs — **not** as the primary SERP source.
3. **Relevance & credibility gate:** score every result against the query (keyword overlap + domain reputation); **drop retail/ad/off-topic domains** (Best Buy, franchise sites auto-rejected). Attach a credibility rating to each accepted source.
4. **Fail loud:** search failures and low-yield queries are surfaced to the orchestrator and quality gate — never silently swallowed.

**Files:** `searxng_settings.yml`, `docker-compose.yml`, `hyperion/tools/searxng.py`, `unified_search.py`, `deep_search.py`, plus glue to the specialist tool clients.
**Done when:** a known query returns ≥ N credible, on-topic results from ≥ 2 independent free sources; retail/ad domains are filtered; failures raise structured errors.

### Layer 2 — Evidence-grounded reasoning (kill hallucination)
**Goal:** agents write *only* what the evidence supports.

5. **Evidence-binding rule:** every quantitative claim and every "Source:" line must map to a real retrieved document with a working URL. No evidence → the claim is **forbidden**, not invented.
6. **Per-section data-completeness score:** if a section's key data points are `Unknown`, the section is **blocked and re-queried** (widen search, add tools) rather than written around with prose.
7. **Framework population check:** frameworks (Porter, VRIO, DCF, etc.) must be filled with real figures; empty frameworks are flagged, not narrated.

**Files:** `hyperion/agents/*` (specialists), `synthesis_lead.py`, `quality_gate.py`, `schemas/models.py`.
**Done when:** a low-data engagement yields explicit "insufficient evidence" handling and re-query attempts — never fabricated numbers or filler.

### Layer 3 — Clean, leak-free output (kill dicts, placeholders, bad URLs)
**Goal:** nothing internal ever reaches the page.

8. **DataPoint formatter + suppression:** a `format_datapoint(dp)` helper renders `value + unit` (or a `low–high` range); if `value in {Unknown, None, ""}` the row is **omitted** or shown as an explicit "insufficient data" note — never a raw dict. Add it as a Jinja filter so templates can't leak objects either.
9. **URL guards:** if a query param is `None`/empty, drop the param or drop the source. Never emit `?jurisdiction=None`.
10. **Ban filler strings:** "So What? No specific implications stated" and "no competitors identified" become **hard quality-gate failures** that trigger re-analysis, not shippable text.

**Files:** `hyperion/output/markdown.py`, `schemas/models.py`, `output/templates/*`, source-builder code.
**Done when:** rendering a report with `Unknown` DataPoints produces no `{'` substring and no `=None` URL anywhere in the output.

### Layer 4 — Consistency & honest confidence (the truth gate)
**Goal:** one recommendation, everywhere, backed by honest confidence.

11. **Single source of truth for the verdict:** compute GO / CONDITIONAL / NO-GO **once** from a data-completeness + evidence-confidence score; render the cover, exec summary, and body from that one field. When completeness is below threshold → force NO-GO / insufficient-data, consistently.
12. **Honest confidence:** confidence is derived from real evidence coverage — a data-void report cannot claim "HIGH".
13. **Quality gate blocks delivery** if: any leaked `{'` / `Unknown` / `=None`, any source fails relevance, any section below completeness threshold, or cover/body verdicts disagree.

**Files:** `hyperion/agents/synthesis_lead.py`, `quality_gate.py`, `engagement_director.py`, `schemas/models.py`.
**Done when:** header/body verdict strings are identical for every report, and confidence tracks evidence coverage.

### Layer 5 — MBB-grade rendering (true PDF, pixel-perfect)
**Goal:** deliver a real, beautiful, paginated PDF that matches PART B.

14. **Working PDF engine:** make **Chromium/Playwright the PRIMARY** renderer (portable, no GTK pain) with WeasyPrint as an optional enhancement; or install WeasyPrint + native deps (`libpango`, `libgdk-pixbuf`, `libffi`, `libcairo2`, fonts). Either way the primary path must actually import and run.
15. **Never deliver the intermediate `_playwright.html`:** delivery returns `result.pdf_path` and **hard-fails** if `success is False`; delete/hide the temp HTML.
16. **Inline CSS** (or pass via WeasyPrint `stylesheets=[CSS(string=...)]`, already supported at `render.py:459`) — never an absolute machine path. Remove any `<link href="C:\...">` generation.
17. **Apply the MBB standard from PART B:**
    - Action titles on every section (generated from the section's real conclusion + numbers).
    - Exhibits: real charts (waterfall, football-field valuation range, tornado sensitivity, growth-share matrix) via the existing Plotly/`charts.py` pipeline, each with a source footnote.
    - **Content-derived, deduplicated imagery:** generate 2–3 concrete visual concepts per section from its title + findings; track used image IDs; never reuse an image; vary orientation.
    - **Contrast:** WCAG-AA enforced in `hyperion.css`; text over images always on a scrim/solid panel.
    - Pyramid/SCQA structure, per-page source footnotes, methodology + full source list in the appendix.
    - `@media screen` fallback so even the debug HTML looks intentional — but the **deliverable is the `.pdf`**.

**Files:** `hyperion/output/render.py`, `agents/delivery/render_engine.py`, `agents/delivery/presentation_designer.py`, `output/images.py`, `output/charts.py`, `output/templates/*`, `output/templates/styles/hyperion.css`.
**Done when:** the deliverable is a `.pdf` that opens in PyMuPDF with > 1 page, embedded fonts, unique images, action titles, exhibits with sources, and AA contrast — and no `_playwright.html` ships.

---

## PART E — SEQUENCING & VERIFICATION

### E.1 Implementation order
| # | Layer / Fix | Why this order |
|---|---|---|
| 1 | **L1.1** SearXNG config + pin image | Tiny change; unblocks the meta-search hub |
| 2 | **L5.14–16** Chromium-primary PDF, stop shipping `_playwright.html`, inline CSS | Immediately turns output into a real PDF — highest-visibility win |
| 3 | **L3** DataPoint formatter, URL guards, ban filler | Fast cleanup; kills leaked dicts / `None` / placeholders you saw |
| 4 | **L1.2–4** Parallel free-API search + relevance gate | THE core data-quality fix (the real depth) |
| 5 | **L4** Single-verdict source + honest confidence + quality gate | Kills contradiction; enforces trust |
| 6 | **L2** Evidence-binding + completeness re-query | Guarantees grounded, deep analysis |
| 7 | **L5.17** Full MBB rendering polish (action titles, exhibits, imagery, contrast) | Final pixel-perfect layer |
| 8 | TUI: "export full transcript / save log to file" | UX pain point (no more scroll-screenshot) |

### E.2 Verification per layer
- **Search (L1):** unit test — a known query returns ≥ N credible, on-topic results from ≥ 2 free sources; retail/ad domains filtered; failures raise structured errors.
- **Reasoning (L2):** feed a low-data engagement → explicit insufficient-evidence handling + re-query, no fabricated numbers.
- **Output cleanliness (L3):** render with `Unknown` DataPoints → assert no `{'` and no `=None` in output.
- **Consistency (L4):** low-data engagement → cover and body verdict strings identical; confidence tracks coverage.
- **Rendering (L5):** assert a `.pdf` (not `.html`) opens in PyMuPDF, > 1 page, fonts embedded, image hashes unique, text-over-image contrast ≥ 4.5:1, every exhibit has a source footnote; assert no `_playwright.html` in the delivered set.

### E.3 The end state
A single strategic question in → a **true PDF report** out that a McKinsey/BCG partner would recognize as their own: answer-first (Pyramid/SCQA), MECE, action-titled, exhibit-driven, every claim cited to a real free source, one consistent evidence-backed recommendation, unique purposeful imagery, AA-contrast typography — produced entirely on a zero-cost stack, taking as long as quality requires.
