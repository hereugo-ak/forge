"""HYPERION animated logo — spec §2.1 + §3.

ASCII wordmark with gradient shimmer (cyan→violet→magenta, OKLCH-interpolated).
Intro chroma-sweep on first render, then steady shimmer loop.
"""

from __future__ import annotations

import math
from typing import Any

from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

# ── §2.1 Locked ASCII wordmark ──────────────────────────────────────────────

LOGO_LINES = [
    "  \u2588\u2588\u2557  \u2588\u2588\u2557\u2588\u2588\u2557   \u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2588\u2588\u2557 \u2588\u2588\u2588\u2588\u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2588\u2588\u2557 \u2588\u2588\u2557 \u2588\u2588\u2588\u2588\u2588\u2588\u2557 \u2588\u2588\u2588\u2557   \u2588\u2588\u2557",
    "  \u2588\u2588\u2551  \u2588\u2588\u2551\u255a\u2588\u2588\u2557 \u2588\u2588\u2554\u2588\u2588\u2554\u2588\u2588\u2588\u2588\u2554\u2588\u2588\u2557\u2588\u2588\u2554\u2588\u2588\u2588\u2588\u2554\u2588\u2588\u2550\u2550\u2550\u255d\u2588\u2588\u2554\u2588\u2588\u2588\u2588\u2554\u2588\u2588\u2557\u2588\u2588\u2551\u2588\u2588\u2554\u2588\u2588\u2588\u2588\u2554\u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2557  \u2588\u2588\u2551",
    "  \u2588\u2588\u2588\u2588\u2588\u2588\u2551 \u255a\u2588\u2588\u2588\u2588\u2554\u2588\u2588\u2557 \u2588\u2588\u2588\u2588\u2588\u2588\u2554\u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2588\u2557 \u2588\u2588\u2588\u2588\u2588\u2588\u2554\u2588\u2588\u2557\u2588\u2588\u2551\u2588\u2588\u2551   \u2588\u2588\u2551\u2588\u2588\u2554\u2588\u2588\u2557 \u2588\u2588\u2551",
    "  \u2588\u2588\u2554\u2588\u2588\u2588\u2588\u2551  \u255a\u2588\u2588\u2554\u2588\u2588\u2557  \u2588\u2588\u2554\u2588\u2588\u2588\u2588\u2554\u2588\u2588\u2550 \u2588\u2588\u2554\u2588\u2588\u2550\u255d  \u2588\u2588\u2554\u2588\u2588\u2588\u2588\u2551\u2588\u2588\u2551\u2588\u2588\u2551   \u2588\u2588\u2551\u2588\u2588\u2551\u255a\u2588\u2588\u2557\u2588\u2588\u2551",
    "  \u2588\u2588\u2551  \u2588\u2588\u2551   \u2588\u2588\u2551   \u2588\u2588\u2551     \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557\u2588\u2588\u2551  \u2588\u2588\u2551\u2588\u2588\u2551\u255a\u2588\u2588\u2588\u2588\u2588\u2588\u2554\u2588\u2588\u2551\u2588\u2588\u2551 \u255a\u2588\u2588\u2588\u2588\u2551",
    "  \u255a\u2550\u255d  \u255a\u2550\u255d   \u255a\u2550\u255d   \u255a\u2550\u255d     \u255a\u2550\u2550\u2550\u2550\u2550\u2550\u255d\u255a\u2550\u255d  \u255a\u2550\u255d\u255a\u2550\u255d \u255a\u2588\u2588\u2588\u2588\u2588\u255d \u255a\u2550\u255d  \u255a\u2588\u2588\u2588\u255d",
]

BANNER_LINE    = "\u25c6 MULTI-AGENT CONSULTING SYSTEM \u25c6"
SUBBANNER_LINE = "orchestration \u00b7 reasoning \u00b7 synthesis"
HR_LINE        = "\u2500" * 69

# ── Color helpers ────────────────────────────────────────────────────────────

def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return (
        int(_lerp(c1[0], c2[0], t)),
        int(_lerp(c1[1], c2[1], t)),
        int(_lerp(c1[2], c2[2], t)),
    )


# Pre-compute gradient RGB stops
_GRADIENT_RGB = [_hex_to_rgb(c) for c in ["#00D9FF", "#8B5CF6", "#F0ABFC"]]
_DIM_RGB = _hex_to_rgb("#3A4670")


def _gradient_color(pos: float) -> tuple[int, int, int]:
    """Get gradient color at position 0..1 using linear interpolation across 3 stops."""
    pos = pos % 1.0
    if pos < 0.5:
        t = pos * 2.0
        return _lerp_color(_GRADIENT_RGB[0], _GRADIENT_RGB[1], t)
    else:
        t = (pos - 0.5) * 2.0
        return _lerp_color(_GRADIENT_RGB[1], _GRADIENT_RGB[2], t)


def _colorize_line(line: str, offset: float, dim: bool = False) -> str:
    """Apply gradient color to a line of text, character by character."""
    if not line:
        return line
    result: list[str] = []
    for i, ch in enumerate(line):
        if ch == " ":
            result.append(ch)
            continue
        if dim:
            r, g, b = _DIM_RGB
        else:
            pos = (i / max(len(line), 1) + offset) % 1.0
            r, g, b = _gradient_color(pos)
        result.append(f"\x1b[38;2;{r};{g};{b}m{ch}\x1b[0m")
    return "".join(result)


# ── Widget ───────────────────────────────────────────────────────────────────

class HyperionLogo(Widget):
    """Animated HYPERION ASCII wordmark with gradient shimmer."""

    DEFAULT_CSS = ""
    can_focus = False

    frame: reactive[float] = reactive(0.0)

    def __init__(self, *, animated: bool = True, reduced_motion: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._animated = animated
        self._reduced_motion = reduced_motion
        self._intro_done = reduced_motion  # skip intro if reduced motion
        self._intro_t = 0.0
        self._shimmer_t = 0.0

    def render(self) -> Any:
        from rich.text import Text

        lines: list[str] = []

        if not self._intro_done and not self._reduced_motion:
            # Intro phase: dim logo with sweeping light bar
            sweep_pos = _ease_out_expo(self._intro_t)
            for line in LOGO_LINES:
                colored = []
                for i, ch in enumerate(line):
                    if ch == " ":
                        colored.append(ch)
                        continue
                    char_pos = i / max(len(line), 1)
                    if char_pos <= sweep_pos:
                        pos = (char_pos + self._shimmer_t) % 1.0
                        r, g, b = _gradient_color(pos)
                        glow_dist = sweep_pos - char_pos
                        if glow_dist < 0.03:
                            r = min(255, r + 40)
                            g = min(255, g + 40)
                            b = min(255, b + 40)
                    else:
                        r, g, b = _DIM_RGB
                    colored.append(f"\x1b[38;2;{r};{g};{b}m{ch}\x1b[0m")
                lines.append("".join(colored))
        elif self._reduced_motion:
            for line in LOGO_LINES:
                lines.append(_colorize_line(line, 0.0))
        else:
            for line in LOGO_LINES:
                lines.append(_colorize_line(line, self._shimmer_t))

        # Banner + sub-banner
        lines.append("")
        lines.append(f"              {BANNER_LINE}")
        lines.append(f"                {SUBBANNER_LINE}")

        # Join all lines into a single Rich Text
        full = "\n".join(lines)
        return Text.from_ansi(full)

    def on_mount(self) -> None:
        if self._animated and not self._reduced_motion:
            self.set_interval(1 / 30, self._tick)

    def _tick(self) -> None:
        if not self._intro_done:
            self._intro_t += (1 / 30) / 0.9  # 900ms intro
            if self._intro_t >= 1.0:
                self._intro_t = 1.0
                self._intro_done = True
        # Shimmer runs always (4s loop)
        self._shimmer_t += (1 / 30) / 4.0
        self._shimmer_t %= 1.0
        self.refresh()


def _ease_out_expo(t: float) -> float:
    """cubic-bezier(0.16, 1, 0.3, 1) approximation — expo-out."""
    if t >= 1.0:
        return 1.0
    return 1.0 - (2.0 ** (-10.0 * t))
