# HYPERION Font Assets

## Required Fonts (ARCHITECTURE.md §7.4)

HYPERION uses exactly two fonts. No more, no less.

### 1. Instrument Serif (Header Font)
- **Used for**: All headings, cover page title, section titles
- **Source**: Google Fonts (free, open source)
- **URL**: https://fonts.google.com/specimen/Instrument+Serif
- **Files needed**:
  - `InstrumentSerif-Regular.ttf`
  - `InstrumentSerif-Italic.ttf`

### 2. JetBrains Mono (Body Font)
- **Used for**: Body text, tables, captions, footers, code blocks
- **Source**: JetBrains (free, open source)
- **URL**: https://www.jetbrains.com/lp/mono/
- **Files needed**:
  - `JetBrainsMono-Regular.ttf`
  - `JetBrainsMono-Medium.ttf`
  - `JetBrainsMono-Bold.ttf`

## Installation

### Option A: Manual download
1. Download from the URLs above
2. Place .ttf files in this directory (`assets/fonts/`)

### Option B: Automated (requires internet)
```bash
# Instrument Serif
curl -L -o InstrumentSerif-Regular.ttf "https://github.com/google/fonts/raw/main/ofl/instrumentserif/InstrumentSerif%5Bwght%5D.ttf"

# JetBrains Mono
curl -L -o JetBrainsMono-Regular.ttf "https://github.com/JetBrains/typography/raw/main/fonts/ttf/JetBrainsMono-Regular.ttf"
curl -L -o JetBrainsMono-Bold.ttf "https://github.com/JetBrains/typography/raw/main/fonts/ttf/JetBrainsMono-Bold.ttf"
```

## Why These Two Fonts

**Instrument Serif** conveys authority — it's a classic transitional serif
used by premium publications. It signals that this is a considered, expert
document, not a quick AI dump.

**JetBrains Mono** is technical, precise, and aligns numbers perfectly in
tables. It's a monospace font that makes financial models and data tables
read like engineering specs, not marketing slides.

This two-font system is a design constraint, not a limitation — it creates
visual consistency across every HYPERION report. (§7.4)

## Embedding

Both fonts are embedded in the PDF by WeasyPrint via `@font-face` in
`hyperion.css`. This ensures identical rendering on any system, regardless
of whether the fonts are installed on the viewer's machine.
