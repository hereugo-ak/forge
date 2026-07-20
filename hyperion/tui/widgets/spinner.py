"""HYPERION spinner — spec §8.1 Tier 1.

Braille-dot sequence cycling at 90ms intervals.
"""

from __future__ import annotations

import itertools
from typing import Any

from textual.reactive import reactive
from textual.widget import Widget
from rich.text import Text

from hyperion.tui.theme import BRAND_CYAN

SPINNER_FRAMES = ["\u280b", "\u2819", "\u2839", "\u2838", "\u283c", "\u2834", "\u2826", "\u2827", "\u2807", "\u280f"]


class Spinner(Widget):
    """Braille-dot spinner — 90ms per frame, brand.cyan color."""

    DEFAULT_CSS = ""
    can_focus = False

    active: reactive[bool] = reactive(False)

    def __init__(self, *, reduced_motion: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._reduced_motion = reduced_motion
        self._frame_idx = 0
        self._cycle: Any = itertools.cycle(SPINNER_FRAMES)

    def render(self) -> Any:
        if self._reduced_motion:
            return Text("\u25cf", style=BRAND_CYAN)
        frame = next(self._cycle)
        return Text(frame, style=BRAND_CYAN)

    def watch_active(self, active: bool) -> None:
        if active and not self._reduced_motion:
            self.set_interval(0.09, self._tick)
        else:
            self._reset_timer()

    def _tick(self) -> None:
        self.refresh()

    def start(self) -> None:
        self.active = True

    def stop(self) -> None:
        self.active = False
