"""HYPERION progress bars — spec §8.1 Tier 2 & Tier 3.

Tier 2: Determinate gradient progress bar (cyan→violet per-cell).
Tier 3: Indeterminate aurora bar (sliding Gaussian pulse).
"""

from __future__ import annotations

import math
from typing import Any

from textual.reactive import reactive
from textual.widget import Widget
from rich.text import Text

from hyperion.tui.theme import BORDER_SUBTLE, SIG_WARN, TEXT_DIM, BRAND_CYAN, BRAND_VIOLET


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _lerp_rgb(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return int(_lerp(c1[0], c2[0], t)), int(_lerp(c1[1], c2[1], t)), int(_lerp(c1[2], c2[2], t))


_CYAN_RGB = _hex_to_rgb(BRAND_CYAN)
_VIOLET_RGB = _hex_to_rgb(BRAND_VIOLET)
_SUBTLE_RGB = _hex_to_rgb(BORDER_SUBTLE)


def _h(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"{r};{g};{b}"


class ProgressBar(Widget):
    """Tier 2 — determinate progress bar with gradient fill."""

    DEFAULT_CSS = ""
    can_focus = False

    progress: reactive[float] = reactive(0.0)
    label: reactive[str] = reactive("")
    total: reactive[int] = reactive(0)

    def __init__(self, *, width: int = 20, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._bar_width = width

    def render(self) -> Any:
        p = min(max(self.progress, 0.0), 1.0)
        filled = int(p * self._bar_width)
        empty = self._bar_width - filled

        parts: list[str] = []
        for i in range(filled):
            t = i / max(self._bar_width - 1, 1)
            r, g, b = _lerp_rgb(_CYAN_RGB, _VIOLET_RGB, t)
            parts.append(f"\x1b[38;2;{r};{g};{b}m\u2588\x1b[0m")
        for i in range(empty):
            parts.append(f"\x1b[38;2;{_SUBTLE_RGB[0]};{_SUBTLE_RGB[1]};{_SUBTLE_RGB[2]}m\u2591\x1b[0m")

        bar = "".join(parts)
        pct = int(p * 100)
        ratio = f"({self.progress * self.total:.0f} / {self.total})" if self.total > 0 else ""
        warn_hex = _h(SIG_WARN)
        dim_hex = _h(TEXT_DIM)
        line = f"{self.label}  {bar}  \x1b[38;2;{warn_hex}m{pct}%\x1b[0m   \x1b[38;2;{dim_hex}m{ratio}\x1b[0m"
        return Text.from_ansi(line)


class AuroraBar(Widget):
    """Tier 3 — indeterminate aurora bar with sliding Gaussian pulse."""

    DEFAULT_CSS = ""
    can_focus = False

    active: reactive[bool] = reactive(False)
    label: reactive[str] = reactive("")

    def __init__(self, *, track_width: int = 40, reduced_motion: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._track = track_width
        self._reduced_motion = reduced_motion
        self._t = 0.0

    def render(self) -> Any:
        heights = "\u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588"
        parts: list[str] = []
        for i in range(self._track):
            # Gaussian pulse centered at position sliding across track
            pulse_pos = (self._t % 1.0) * (self._track + 16) - 8
            dist = abs(i - pulse_pos)
            intensity = math.exp(-(dist ** 2) / 12.0)
            intensity = min(intensity, 1.0)
            if intensity < 0.05:
                parts.append(" ")
            else:
                h_idx = min(int(intensity * 7), 7)
                # Color: cyan at edges, violet at peak
                t = intensity
                r, g, b = _lerp_rgb(_CYAN_RGB, _VIOLET_RGB, t)
                # Leading edge slightly brighter
                if i < pulse_pos + 1 and i > pulse_pos - 2:
                    r = min(255, r + 20)
                    g = min(255, g + 20)
                    b = min(255, b + 20)
                parts.append(f"\x1b[38;2;{r};{g};{b}m{heights[h_idx]}\x1b[0m")

        bar = "".join(parts)
        line = f"{self.label}  {bar}"
        return Text.from_ansi(line)

    def watch_active(self, active: bool) -> None:
        if active and not self._reduced_motion:
            self.set_interval(1 / 30, self._tick)
        else:
            self._reset_timer()

    def _tick(self) -> None:
        self._t += (1 / 30) / 1.6  # 1.6s loop
        self.refresh()

    def start(self) -> None:
        self.active = True

    def stop(self) -> None:
        self.active = False
