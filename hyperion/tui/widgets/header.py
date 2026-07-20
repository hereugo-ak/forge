"""HYPERION header widget — spec §6 header row.

Traffic-light dots (decorative) + product name + version + session ID.
Pinned at top of the session frame.
"""

from __future__ import annotations

from typing import Any

from textual.widget import Widget
from rich.text import Text

from hyperion.tui.theme import SIG_ERROR, SIG_WARN, SIG_SUCCESS, TEXT_SECONDARY


class HeaderBar(Widget):
    """Pinned top header: ● ● ●  HYPERION · v1.0.0 · SESSION 0x7F3A"""

    DEFAULT_CSS = ""
    can_focus = False

    def __init__(self, *, version: str = "v1.0.0", session_id: str = "0x7F3A", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._version = version
        self._session_id = session_id

    def render(self) -> Text:
        dots = (
            Text("  ")
            + Text("\u25cf", style=SIG_ERROR) + " "
            + Text("\u25cf", style=SIG_WARN) + " "
            + Text("\u25cf", style=SIG_SUCCESS)
        )
        center = f"HYPERION \u00b7 {self._version} \u00b7 SESSION {self._session_id}"
        w = self.size.width if self.size else 80
        pad = max(0, (w - 7 - len(center) - 4) // 2)
        return dots + Text(" " * pad) + Text(center, style=TEXT_SECONDARY)
