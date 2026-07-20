"""HYPERION prompt line — spec §9.

Persistent bottom prompt: ◈ hyperion@orchestrator ~ ❯ █
Block cursor with blink (1000ms step-end).
"""

from __future__ import annotations

from typing import Any

from textual.reactive import reactive
from textual.widget import Widget
from textual.message import Message
from rich.text import Text

from hyperion.tui.theme import (
    BRAND_CYAN,
    BRAND_VIOLET,
    BRAND_MAGENTA,
    TEXT_DIM,
    TEXT_PRIMARY,
)


def _h(hex_color: str) -> str:
    """Convert #RRGGBB to 'RRR;GGG;BBB' for ANSI escape."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"{r};{g};{b}"


class PromptBar(Widget):
    """Persistent bottom prompt with block cursor."""

    DEFAULT_CSS = ""
    can_focus = True

    cursor_visible: reactive[bool] = reactive(True)
    is_streaming: reactive[bool] = reactive(False)

    def __init__(self, *, context: str = "orchestrator", scope: str = "~", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._agent_context = context
        self._scope = scope
        self._value = ""
        self._history: list[str] = []
        self._history_idx = -1
        self._cursor_pos = 0

    def render(self) -> Any:
        cyan = _h(BRAND_CYAN)
        violet = _h(BRAND_VIOLET)
        magenta = _h(BRAND_MAGENTA)
        dim = _h(TEXT_DIM)
        primary = _h(TEXT_PRIMARY)

        # Build prompt prefix
        prefix = (
            f"\x1b[38;2;{violet}m\u25c8\x1b[0m "  # ◈ violet
            f"\x1b[38;2;{cyan}mhyperion\x1b[0m"     # hyperion cyan
            f"\x1b[38;2;{dim}m@\x1b[0m"             # @ dim
            f"\x1b[38;2;{violet}m{self._agent_context}\x1b[0m "  # orchestrator violet
            f"\x1b[38;2;{dim}m{self._scope}\x1b[0m "       # ~ dim
            f"\x1b[38;2;{magenta}m\u276f\x1b[0m "          # ❯ magenta
        )

        # Input value with cursor
        val = self._value
        if self.cursor_visible and not self.is_streaming:
            # Block cursor at cursor_pos
            before = val[: self._cursor_pos]
            at = val[self._cursor_pos : self._cursor_pos + 1] if self._cursor_pos < len(val) else " "
            after = val[self._cursor_pos + 1 :]
            input_part = (
                f"\x1b[38;2;{primary}m{before}\x1b[0m"
                f"\x1b[48;2;{cyan}m\x1b[38;2;0;14;26m{at}\x1b[0m"
                f"\x1b[38;2;{primary}m{after}\x1b[0m"
            )
        else:
            input_part = f"\x1b[38;2;{primary}m{val}\x1b[0m"

        line = f"{prefix}{input_part}"
        return Text.from_ansi(line)

    def on_mount(self) -> None:
        self.set_interval(0.5, self._blink)

    def _blink(self) -> None:
        if not self.is_streaming:
            self.cursor_visible = not self.cursor_visible
            self.refresh()

    def on_key(self, event: Any) -> None:
        if event.key == "enter":
            if self._value.strip():
                self._history.append(self._value)
                self._history_idx = len(self._history)
                # Emit submit
                self.post_message(PromptSubmitted(self._value))
            self._value = ""
            self._cursor_pos = 0
            event.prevent_default()
            event.stop()
        elif event.key == "backspace":
            if self._cursor_pos > 0:
                self._value = self._value[: self._cursor_pos - 1] + self._value[self._cursor_pos :]
                self._cursor_pos -= 1
            event.prevent_default()
            event.stop()
        elif event.key == "delete":
            if self._cursor_pos < len(self._value):
                self._value = self._value[: self._cursor_pos] + self._value[self._cursor_pos + 1 :]
            event.prevent_default()
            event.stop()
        elif event.key == "left":
            if self._cursor_pos > 0:
                self._cursor_pos -= 1
            event.prevent_default()
            event.stop()
        elif event.key == "right":
            if self._cursor_pos < len(self._value):
                self._cursor_pos += 1
            event.prevent_default()
            event.stop()
        elif event.key == "home" or event.key == "ctrl+a":
            self._cursor_pos = 0
            event.prevent_default()
            event.stop()
        elif event.key == "end" or event.key == "ctrl+e":
            self._cursor_pos = len(self._value)
            event.prevent_default()
            event.stop()
        elif event.key == "up":
            if self._history_idx > 0:
                self._history_idx -= 1
                self._value = self._history[self._history_idx]
                self._cursor_pos = len(self._value)
            event.prevent_default()
            event.stop()
        elif event.key == "down":
            if self._history_idx < len(self._history) - 1:
                self._history_idx += 1
                self._value = self._history[self._history_idx]
                self._cursor_pos = len(self._value)
            else:
                self._history_idx = len(self._history)
                self._value = ""
                self._cursor_pos = 0
            event.prevent_default()
            event.stop()
        elif event.key == "ctrl+l":
            self.post_message(ClearScrollback())
            event.prevent_default()
            event.stop()
        elif event.key == "ctrl+c":
            self.post_message(CancelTurn())
            event.prevent_default()
            event.stop()
        elif event.key == "ctrl+d":
            self.app.exit()
            event.prevent_default()
            event.stop()
        elif event.character and event.key not in ("tab", "escape", "ctrl+c", "ctrl+d", "ctrl+l", "ctrl+a", "ctrl+e", "ctrl+r", "ctrl+p"):
            # Insert character
            self._value = self._value[: self._cursor_pos] + event.character + self._value[self._cursor_pos :]
            self._cursor_pos += 1
            event.prevent_default()
            event.stop()

        self.cursor_visible = True
        self.refresh()

    @property
    def value(self) -> str:
        return self._value

    def set_context(self, ctx: str) -> None:
        self._agent_context = ctx
        self.refresh()


class PromptSubmitted(Message):
    """Posted when user submits the prompt."""

    def __init__(self, value: str) -> None:
        super().__init__()
        self.value = value


class ClearScrollback(Message):
    """Posted when user presses Ctrl+L."""


class CancelTurn(Message):
    """Posted when user presses Ctrl+C."""
