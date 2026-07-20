"""HYPERION log stream — spec §6 + §7.

Badge-tagged scrollable log rows with timestamps.
Each row: [HH:MM:SS]  BADGE   content
Nested details with ├─ and └─ tree glyphs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from textual.widget import Widget
from rich.text import Text

from hyperion.tui.theme import (
    TEXT_DIM,
    TEXT_PRIMARY,
    TEXT_GHOST,
    BADGE_COLORS,
)


@dataclass
class LogEntry:
    timestamp: str
    badge: str
    content: str
    nested: list[str] = field(default_factory=list)


class LogStream(Widget):
    """Scrollable badge-tagged log stream."""

    DEFAULT_CSS = ""
    can_focus = True

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._entries: list[LogEntry] = []
        self._scroll = 0
        self._max_visible = 20

    def add_entry(self, badge: str, content: str, nested: list[str] | None = None) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        entry = LogEntry(
            timestamp=ts,
            badge=badge.upper(),
            content=content,
            nested=nested or [],
        )
        self._entries.append(entry)
        # Auto-scroll to bottom
        total_lines = sum(1 + len(e.nested) for e in self._entries)
        self._scroll = max(0, total_lines - self._max_visible)
        self.refresh()

    def clear(self) -> None:
        self._entries.clear()
        self._scroll = 0
        self.refresh()

    def render(self) -> Any:
        if not self._entries:
            return Text("", style=TEXT_DIM)

        # Flatten entries into lines
        all_lines: list[tuple[str, str, str, int]] = []
        for entry in self._entries:
            all_lines.append((entry.timestamp, entry.badge, entry.content, 0))
            for i, detail in enumerate(entry.nested):
                glyph = "\u2514\u2500" if i == len(entry.nested) - 1 else "\u251c\u2500"
                all_lines.append((entry.timestamp, entry.badge, f"{glyph} {detail}", 1))

        # Apply scroll
        visible = all_lines[self._scroll : self._scroll + self._max_visible]

        raw_lines: list[str] = []
        for ts, badge, content, indent in visible:
            badge_color = BADGE_COLORS.get(badge, TEXT_PRIMARY)
            ts_hex = _h(TEXT_DIM)
            badge_hex = _h(badge_color)
            content_hex = _h(TEXT_PRIMARY)
            ghost_hex = _h(TEXT_GHOST)

            if indent > 0:
                line = f"\x1b[38;2;{ts_hex}m      \x1b[0m  \x1b[38;2;{ghost_hex}m{content}\x1b[0m"
            else:
                badge_padded = badge.ljust(10)
                line = (
                    f"\x1b[38;2;{ts_hex}m[{ts}]\x1b[0m  "
                    f"\x1b[38;2;{badge_hex}m{badge_padded}\x1b[0m "
                    f"\x1b[38;2;{content_hex}m{content}\x1b[0m"
                )
            raw_lines.append(line)

        full = "\n".join(raw_lines)
        return Text.from_ansi(full)

    def on_key(self, event: Any) -> None:
        total_lines = sum(1 + len(e.nested) for e in self._entries)
        if event.key == "up":
            self._scroll = max(0, self._scroll - 1)
            self.refresh()
            event.prevent_default()
        elif event.key == "down":
            self._scroll = min(max(0, total_lines - self._max_visible), self._scroll + 1)
            self.refresh()
            event.prevent_default()
        elif event.key == "page_up":
            self._scroll = max(0, self._scroll - self._max_visible)
            self.refresh()
            event.prevent_default()
        elif event.key == "page_down":
            self._scroll = min(max(0, total_lines - self._max_visible), self._scroll + self._max_visible)
            self.refresh()
            event.prevent_default()


def _h(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"{r};{g};{b}"
