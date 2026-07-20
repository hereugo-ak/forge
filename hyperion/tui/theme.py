"""HYPERION TUI theme — spec §4 color palette.

All colors are 24-bit truecolor hex strings. No pure white, no pure black.
Designated as Textual design tokens so widgets reference them by name.
"""

from __future__ import annotations

from textual.design import ColorSystem

# ── §4.1 Palette ────────────────────────────────────────────────────────────

BG_CANVAS    = "#0A0E1A"
BG_SURFACE   = "#111629"
BORDER_SUBTLE = "#2A3350"
BORDER_BRAND  = "#8B5CF6"

TEXT_PRIMARY   = "#E4E9F2"
TEXT_SECONDARY = "#A8B3CF"
TEXT_DIM       = "#6B7A99"
TEXT_GHOST     = "#4A5878"

BRAND_CYAN    = "#00D9FF"
BRAND_VIOLET  = "#8B5CF6"
BRAND_MAGENTA = "#F0ABFC"

SIG_SUCCESS = "#10D9A0"
SIG_WARN    = "#FFB627"
SIG_ERROR   = "#FF5C7A"
SIG_INFO    = "#7EE5FF"

# ── Logo gradient stops (§3.1) ──────────────────────────────────────────────

LOGO_GRADIENT = [BRAND_CYAN, BRAND_VIOLET, BRAND_MAGENTA]
LOGO_DIM      = "#3A4670"

# ── Badge colors (§7) ───────────────────────────────────────────────────────

BADGE_COLORS = {
    "READY":      SIG_SUCCESS,
    "THINKING":   BRAND_VIOLET,
    "PLAN":       BRAND_VIOLET,
    "AGENT":      BRAND_CYAN,
    "TOOL":       SIG_WARN,
    "STREAM":     SIG_INFO,
    "DONE":       SIG_SUCCESS,
    "WARN":       SIG_WARN,
    "ERROR":      SIG_ERROR,
    "HANDOFF":    BRAND_MAGENTA,
    "ANALYST":    BRAND_CYAN,
    "RESEARCHER": "#7EE5FF",
    "STRATEGIST": BRAND_VIOLET,
    "CRITIC":     SIG_ERROR,
    "SYNTHESIZER": BRAND_MAGENTA,
    "ORCHESTRATOR": BRAND_VIOLET,
}

# ── Textual color system ────────────────────────────────────────────────────

def build_color_system() -> ColorSystem:
    """Build a Textual ColorSystem from the HYPERION palette."""
    return ColorSystem(
        background=BG_CANVAS,
        surface=BG_SURFACE,
        panel=BG_SURFACE,
        dark=True,
        primary=BRAND_VIOLET,
        secondary=BRAND_CYAN,
        warning=SIG_WARN,
        error=SIG_ERROR,
        success=SIG_SUCCESS,
        accent=BRAND_MAGENTA,
        foreground=TEXT_PRIMARY,
    )


HYPERION_THEME = {
    "background": BG_CANVAS,
    "surface": BG_SURFACE,
    "panel": BG_SURFACE,
    "primary": BRAND_VIOLET,
    "secondary": BRAND_CYAN,
    "accent": BRAND_MAGENTA,
    "warning": SIG_WARN,
    "error": SIG_ERROR,
    "success": SIG_SUCCESS,
    "foreground": TEXT_PRIMARY,
    "text-primary": TEXT_PRIMARY,
    "text-secondary": TEXT_SECONDARY,
    "text-dim": TEXT_DIM,
    "text-ghost": TEXT_GHOST,
    "border-subtle": BORDER_SUBTLE,
    "border-brand": BORDER_BRAND,
    "brand-cyan": BRAND_CYAN,
    "brand-violet": BRAND_VIOLET,
    "brand-magenta": BRAND_MAGENTA,
    "sig-success": SIG_SUCCESS,
    "sig-warn": SIG_WARN,
    "sig-error": SIG_ERROR,
    "sig-info": SIG_INFO,
}


def register_theme(app: object) -> None:
    """Register the HYPERION theme with a Textual app."""
    from textual.app import App
    assert isinstance(app, App)
    app.dark = True
    for name, value in HYPERION_THEME.items():
        try:
            app.design.color_system.set_color(name, value)
        except Exception:
            pass
