"""Quick test for the HYPERION TUI."""
import asyncio
from hyperion.tui.app import HyperionApp

async def test():
    app = HyperionApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.pause()
        screen = app.screen
        print(f"Screen: {type(screen).__name__}")
        children = list(screen.walk_children())
        print(f"Children: {[(type(w).__name__, w.id) for w in children]}")
        from hyperion.tui.widgets.log_stream import LogStream
        try:
            log = screen.query_one(LogStream)
            print(f"Log entries: {len(log._entries)}")
            for e in log._entries:
                print(f"  [{e.timestamp}] {e.badge} {e.content}")
        except Exception as e:
            print(f"Log error: {e}")
        from hyperion.tui.widgets.prompt import PromptBar
        try:
            prompt = screen.query_one(PromptBar)
            print(f"Prompt focused: {prompt.has_focus}")
        except Exception as e:
            print(f"Prompt error: {e}")
        app.exit()

if __name__ == "__main__":
    asyncio.run(test())
