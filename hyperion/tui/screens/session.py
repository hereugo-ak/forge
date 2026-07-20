"""HYPERION session screen — spec §6 layout anatomy.

Header (pinned top) → Identity block (collapsible) → Log stream (scrollable) → Prompt (pinned bottom).
No CSS. All layout via Textual's built-in compose + DEFAULT_CSS-free rendering.
"""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static
from textual.containers import Vertical, VerticalScroll
from textual.binding import Binding

from hyperion.tui.theme import (
    BORDER_SUBTLE,
    TEXT_DIM,
    TEXT_SECONDARY,
    BRAND_VIOLET,
    SIG_SUCCESS,
)
from hyperion.tui.widgets.header import HeaderBar
from hyperion.tui.widgets.logo import HyperionLogo, BANNER_LINE, SUBBANNER_LINE, HR_LINE
from hyperion.tui.widgets.log_stream import LogStream
from hyperion.tui.widgets.prompt import PromptBar, PromptSubmitted, ClearScrollback, CancelTurn
from hyperion.tui.widgets.spinner import Spinner
from hyperion.tui.widgets.progress import ProgressBar, AuroraBar


class SessionScreen(Screen):
    """Main HYPERION session screen — the command bridge."""

    DEFAULT_CSS = """
    SessionScreen {
        layout: vertical;
        background: #0A0E1A;
    }

    #hdr {
        height: 1;
        dock: top;
    }

    #hdr-rule {
        height: 1;
        dock: top;
    }

    #identity-block {
        height: auto;
        dock: top;
        padding: 0 1;
    }

    #logo {
        height: 10;
        content-align: center middle;
    }

    #identity-spacer {
        height: 1;
    }

    #pre-log-rule {
        height: 1;
        dock: top;
    }

    #log-stream {
        height: 1fr;
        min-height: 3;
        padding: 0 1;
        scrollbar-size: 0 0;
    }

    #pre-prompt-rule {
        height: 1;
        dock: bottom;
    }

    #prompt {
        height: 1;
        dock: bottom;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "cancel", "Cancel", show=False),
        Binding("ctrl+l", "clear", "Clear", show=False),
        Binding("ctrl+d", "quit", "Quit", show=False),
        Binding("f1", "help", "Help", show=False),
    ]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._collapsed = False
        self._session_id = "0x" + f"{id(self) & 0xFFFF:04X}".upper()

    def compose(self) -> ComposeResult:
        # Pinned header
        yield HeaderBar(version="v1.0.0", session_id=self._session_id, id="hdr")

        # Horizontal rule under header
        yield Static(_hr(), id="hdr-rule")

        # Identity block (logo + banner) — collapses after first turn
        with Vertical(id="identity-block"):
            yield HyperionLogo(id="logo", animated=True)
            yield Static("", id="identity-spacer")

        # Rule before log stream
        yield Static(_hr(), id="pre-log-rule")

        # Log stream (scrollable middle)
        yield LogStream(id="log-stream")

        # Rule before prompt
        yield Static(_hr(), id="pre-prompt-rule")

        # Pinned prompt at bottom
        yield PromptBar(id="prompt")

    def on_mount(self) -> None:
        # Focus the prompt immediately
        self.query_one("#prompt", PromptBar).focus()

        # Simulate first-run experience (§19)
        self.set_timer(1.2, self._show_ready)

    def _show_ready(self) -> None:
        """Show READY status after intro animation completes."""
        log = self.query_one("#log-stream", LogStream)
        log.add_entry("READY", "7 specialist agents online \u00b7 context primed")

    def on_prompt_submitted(self, event: PromptSubmitted) -> None:
        """Handle prompt submission."""
        log = self.query_one("#log-stream", LogStream)

        # Echo user input
        log.add_entry("\u276f", f"analyze: {event.value}")  # ❯

        # Collapse identity block after first turn
        if not self._collapsed:
            self._collapse_identity()
            self._collapsed = True

        # Handle commands
        cmd = event.value.strip().lower()
        if cmd in ("/help", "help"):
            self._show_help()
        elif cmd in ("/clear", "clear"):
            self.action_clear()
        elif cmd.startswith("/consult") or cmd.startswith("analyze"):
            self._simulate_engagement(event.value)
        elif cmd == "/providers":
            log.add_entry("READY", "Google \u00b7 Nvidia \u00b7 Cerebras \u00b7 Groq \u2014 all online")
        elif cmd == "/vault":
            log.add_entry("READY", "Vault: 0 entries (empty)")
        elif cmd == "/export":
            log.add_entry("DONE", "\u2713 Session exported to markdown")
        else:
            log.add_entry("READY", f"Unknown command: {event.value}")

    def on_clear_scrollback(self, event: ClearScrollback) -> None:
        self.action_clear()

    def on_cancel_turn(self, event: CancelTurn) -> None:
        log = self.query_one("#log-stream", LogStream)
        log.add_entry("WARN", "Agent turn cancelled")

    def _collapse_identity(self) -> None:
        """Collapse identity block to single line (§6)."""
        try:
            block = self.query_one("#identity-block", Vertical)
            block.display = False
            # Show collapsed line
            collapsed = self.query_one("#hdr", HeaderBar)
        except Exception:
            pass

    def _show_help(self) -> None:
        log = self.query_one("#log-stream", LogStream)
        log.add_entry("READY", "Commands: /consult <q>  /providers  /vault  /export  /clear  /help")
        log.add_entry("READY", "Keys: Ctrl+L clear  Ctrl+C cancel  Ctrl+D exit  F1 help overlay")

    def _simulate_engagement(self, question: str) -> None:
        """Simulate a multi-agent engagement for demo purposes."""
        log = self.query_one("#log-stream", LogStream)

        # THINKING phase
        log.add_entry("THINKING", "decomposing objective into 4 workstreams", [
            "market sizing        \u2192 delegated to ANALYST",
            "competitor landscape \u2192 RESEARCHER",
            "regulatory mapping   \u2192 STRATEGIST",
            "synthesis            \u2192 ORCHESTRATOR",
        ])

        # Simulate agent activity
        self.set_timer(0.5, lambda: log.add_entry("ANALYST", "\u280b fetching TAM/SAM data from 12 sources"))
        self.set_timer(1.0, lambda: log.add_entry("TOOL", 'web.search("brazil fintech regulation 2026") \u2192 8 results'))
        self.set_timer(1.5, lambda: log.add_entry("RESEARCHER", "\u2713 identified 23 competitors \u00b7 scoring..."))
        self.set_timer(2.0, lambda: log.add_entry("ANALYST", "fetching sources  ████████████░░░░░░░░  68%   (14 / 22)"))
        self.set_timer(3.0, lambda: log.add_entry("HANDOFF", "ANALYST \u2192 SYNTHESIZER"))
        self.set_timer(3.5, lambda: log.add_entry("STREAM", "\u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588\u2587\u2586\u2585\u2584\u2583\u2582\u2581  drafting executive summary"))
        self.set_timer(4.5, lambda: log.add_entry("DONE", "\u2713 3 recommendations \u00b7 12 citations \u00b7 1.4k tokens"))

    def action_clear(self) -> None:
        log = self.query_one("#log-stream", LogStream)
        log.clear()
        # Redraw identity block
        try:
            block = self.query_one("#identity-block", Vertical)
            block.display = True
            self._collapsed = False
        except Exception:
            pass

    def action_cancel(self) -> None:
        log = self.query_one("#log-stream", LogStream)
        log.add_entry("WARN", "Agent turn cancelled")

    def action_help(self) -> None:
        self._show_help()

    def action_quit(self) -> None:
        self.app.exit()


def _hr() -> str:
    """Horizontal rule in border.subtle color."""
    h = BORDER_SUBTLE.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"\x1b[38;2;{r};{g};{b}m{'\u2500' * 69}\x1b[0m"
