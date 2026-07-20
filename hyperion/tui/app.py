"""HYPERION TUI App — clean rebuild per spec.

No monkey-patches. No CSS hacks. No splash screen.
Single session screen with animated logo, log stream, and persistent prompt.
"""

from __future__ import annotations

from typing import Any

from textual.app import App

from hyperion.tui.theme import HYPERION_THEME, register_theme
from hyperion.tui.screens.session import SessionScreen


class HyperionApp(App):
    """The HYPERION TUI — a command bridge, not a chatbot.

    Spec: HYPERION_INTERFACE_SPEC.md §6 layout anatomy.
    - Header (pinned top): traffic-light dots + version + session ID
    - Identity block: animated ASCII logo + banner (collapsible)
    - Log stream: badge-tagged scrollable agent output
    - Prompt (pinned bottom): ◈ hyperion@orchestrator ~ ❯ █
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def on_mount(self) -> None:
        # Register theme
        register_theme(self)
        # Single session screen — no splash, no transitions
        self.push_screen(SessionScreen())
