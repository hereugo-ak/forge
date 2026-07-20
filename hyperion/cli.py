"""
HYPERION CLI — Typer-based command-line interface.

This is NOT a generic CLI wrapper. It implements the exact command structure
from ARCHITECTURE.md §8.4 and §9:

Commands:
    hyperion consult <question>   — Start a new engagement (non-interactive)
    hyperion shell                — Launch the TUI engagement room (interactive)
    hyperion providers            — Show LLM provider status and rate limits
    hyperion vault <query>        — Search the Obsidian vault for prior research
    hyperion export <format>      — Export the most recent report (pdf, markdown, json)
    hyperion resume <id>          — Resume a previous engagement session
    hyperion help                 — Show available commands

The CLI is the primary entry point for users. It can run in two modes:
1. Non-interactive: `hyperion consult "Should we enter...?"` → runs engagement, saves PDF
2. Interactive: `hyperion shell` → launches the Textual TUI

Architecture reference: §8.4 Slash Commands, §9 Project Structure (cli.py)
"""

from __future__ import annotations

import asyncio
import json as json_module
import os
import sys
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from hyperion.config import ProviderType, get_settings

app = typer.Typer(
    name="hyperion",
    help="HYPERION — many minds. one reading. Multi-agent consulting intelligence.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()

# ─────────────────────────────────────────────────────────────────────────────
# Brand constants — TUI palette (§7.1)
# ─────────────────────────────────────────────────────────────────────────────

WORDMARK = "HYPERION"
TAGLINE = "many minds. one reading."

COLOR_OBSIDIAN = "#0C0A08"
COLOR_PARCHMENT = "#EDE4D3"
COLOR_BRONZE = "#C89550"
COLOR_VERDIGRIS = "#4B8F7E"
COLOR_UMBER = "#362E22"
COLOR_OXIDE = "#B5533C"


def _print_banner() -> None:
    """Print the HYPERION banner."""
    banner = Text()
    banner.append(f"  {WORDMARK}\n", style=f"bold {COLOR_BRONZE}")
    banner.append(f"  {TAGLINE}\n", style=f"italic {COLOR_PARCHMENT}")
    console.print(banner)
    console.print()


# ─────────────────────────────────────────────────────────────────────────────
# consult — start a new engagement (non-interactive)
# ─────────────────────────────────────────────────────────────────────────────


@app.command()
def consult(
    question: str = typer.Argument(
        ...,
        help="The business question to analyze.",
    ),
    context: str = typer.Option(
        "",
        "--context",
        "-c",
        help="Additional conversation context for the engagement.",
    ),
    output: str = typer.Option(
        "",
        "--output",
        "-o",
        help="Output file path for the PDF. Default: reports/hyperion_report_<timestamp>.pdf",
    ),
    markdown: bool = typer.Option(
        False,
        "--markdown",
        "-m",
        help="Also export a markdown file alongside the PDF.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed progress output.",
    ),
) -> None:
    """Start a new HYPERION engagement.

    This runs the full 5-stage pipeline:
    Engagement Director → Specialists (parallel) → Fact Checker →
    Synthesis Lead → Quality Gate → Presentation Designer →
    Data Visualizer → Render Engine → PDF

    The engagement runs asynchronously. Progress is printed to the console.
    The final PDF is saved to the reports/ directory.

    Examples:
        hyperion consult "Should we enter the Tier-2 Indian SaaS market?"
        hyperion consult "Compare AWS vs Azure vs GCP for a startup" --context "Series A, 50 engineers"
        hyperion consult "What's the TAM for electric vehicle charging in India by 2030?" -o reports/ev_charging.pdf
    """
    _print_banner()

    console.print(
        Panel(
            f"[bold {COLOR_PARCHMENT}]{question}[/bold {COLOR_PARCHMENT}]",
            title=f"[{COLOR_BRONZE}]Engagement[/{COLOR_BRONZE}]",
            border_style=COLOR_UMBER,
        )
    )
    console.print()

    # Run the engagement asynchronously
    result = asyncio.run(_run_engagement(question, context, output, verbose))

    if result.success:
        console.print()
        console.print(
            Panel(
                f"[bold {COLOR_VERDIGRIS}]Engagement Complete[/bold {COLOR_VERDIGRIS}]\n\n"
                f"  PDF: {result.pdf_path}\n"
                f"  Duration: {result.duration_seconds:.0f}s\n"
                f"  Quality Score: {result.quality_score.weighted_total:.1f}/5.0\n"
                f"  Iterations: {result.quality_iterations}\n"
                f"  Adaptations: {result.adaptation_count}\n"
                f"  Escalations: {result.escalation_count}",
                title=f"[{COLOR_BRONZE}]Result[/{COLOR_BRONZE}]",
                border_style=COLOR_VERDIGRIS,
            )
        )

        if markdown and result.markdown_path:
            console.print(f"  Markdown: {result.markdown_path}")

        if result.final_report:
            console.print()
            console.print(
                Panel(
                    f"[bold]Recommendation:[/bold] {result.final_report.recommendation.value}\n"
                    f"[bold]Confidence:[/bold] {result.final_report.confidence.value}\n\n"
                    f"{result.final_report.recommendation_rationale[:500]}...",
                    title=f"[{COLOR_BRONZE}]Analysis Summary[/{COLOR_BRONZE}]",
                    border_style=COLOR_UMBER,
                )
            )
    else:
        console.print()
        console.print(
            Panel(
                f"[bold {COLOR_OXIDE}]Engagement Failed[/bold {COLOR_OXIDE}]\n\n"
                f"  Error: {result.error}",
                title=f"[{COLOR_OXIDE}]Error[/{COLOR_OXIDE}]",
                border_style=COLOR_OXIDE,
            )
        )
        raise typer.Exit(code=1)


async def _run_engagement(
    question: str,
    context: str,
    output_path: str,
    verbose: bool,
) -> Any:
    """Run the engagement asynchronously with progress output."""
    from hyperion.orchestrator import WorkflowEngine

    engine = WorkflowEngine()

    if verbose:
        console.print(f"[dim]Starting engagement engine...[/dim]")

    try:
        result = await engine.run_engagement(
            question=question,
            conversation_context=context,
        )

        # Override output path if specified
        if output_path and result.pdf_path:
            import shutil
            shutil.move(result.pdf_path, output_path)
            result.pdf_path = output_path

        return result
    finally:
        await engine.close()


# ─────────────────────────────────────────────────────────────────────────────
# shell — launch the TUI (interactive mode)
# ─────────────────────────────────────────────────────────────────────────────


@app.command()
def shell() -> None:
    """Launch the HYPERION TUI — interactive engagement room.

    This starts the Textual-based TUI with:
    - Splash screen with provider status
    - Engagement room with live agent grid, TPM bars, findings stream
    - Slash commands with autocomplete (/consult, /providers, /vault, etc.)
    - Deliverable view with rendered markdown and export options

    The TUI is the primary interactive interface for HYPERION.
    """
    try:
        from hyperion.tui.app import HyperionApp

        tui_app = HyperionApp()
        tui_app.run()
    except ImportError:
        console.print(
            f"[{COLOR_OXIDE}]Textual is not installed. Install with: pip install textual rich[/{COLOR_OXIDE}]"
        )
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[{COLOR_OXIDE}]TUI error: {e}[/{COLOR_OXIDE}]")
        raise typer.Exit(code=1)


@app.command()
def boot() -> None:
    """Boot HYPERION — launch the TUI (alias for 'shell')."""
    shell()


# ─────────────────────────────────────────────────────────────────────────────
# providers — show LLM provider status
# ─────────────────────────────────────────────────────────────────────────────


@app.command()
def providers() -> None:
    """Show LLM provider status and rate limits.

    Displays a table with:
    - Provider name (Google, NVIDIA, Cerebras, Groq)
    - Status (available, unavailable, degraded)
    - Models available per tier
    - TPM usage percentage
    - Budget usage percentage
    - Uptime percentage
    """
    _print_banner()

    from hyperion.router.router import get_router

    router = get_router()

    # Get provider health
    health = router.get_provider_health()
    tpm_status = router.get_tpm_status()
    budget_status = router.get_budget_status()

    table = Table(
        title=f"[{COLOR_BRONZE}]LLM Provider Status[/{COLOR_BRONZE}]",
        border_style=COLOR_UMBER,
        header_style=f"bold {COLOR_PARCHMENT}",
    )

    table.add_column("Provider", style=f"bold {COLOR_BRONZE}")
    table.add_column("Status", justify="center")
    table.add_column("TPM Usage", justify="right")
    table.add_column("Budget Usage", justify="right")
    table.add_column("Uptime", justify="right")
    table.add_column("Requests", justify="right")
    table.add_column("Errors", justify="right")

    for provider_type in ProviderType:
        h = health.get(provider_type, {})
        tpm = tpm_status.get(provider_type, {})
        budget = budget_status.get(provider_type, {})

        status = h.get("status", "unknown")
        available = h.get("available", False)

        # Color-code status
        if available:
            status_str = f"[{COLOR_VERDIGRIS}]● {status.upper()}[/{COLOR_VERDIGRIS}]"
        else:
            status_str = f"[{COLOR_OXIDE}]● {status.upper()}[/{COLOR_OXIDE}]"

        # TPM usage with color coding
        tpm_pct = tpm.get("percentage", 0.0)
        if tpm_pct < 70:
            tpm_str = f"[{COLOR_VERDIGRIS}]{tpm_pct:.0f}%[/{COLOR_VERDIGRIS}]"
        elif tpm_pct < 90:
            tpm_str = f"[{COLOR_BRONZE}]{tpm_pct:.0f}%[/{COLOR_BRONZE}]"
        else:
            tpm_str = f"[{COLOR_OXIDE}]{tpm_pct:.0f}%[/{COLOR_OXIDE}]"

        # Budget usage
        budget_pct = budget.get("percentage", 0.0)
        if budget_pct < 70:
            budget_str = f"[{COLOR_VERDIGRIS}]{budget_pct:.0f}%[/{COLOR_VERDIGRIS}]"
        elif budget_pct < 90:
            budget_str = f"[{COLOR_BRONZE}]{budget_pct:.0f}%[/{COLOR_BRONZE}]"
        else:
            budget_str = f"[{COLOR_OXIDE}]{budget_pct:.0f}%[/{COLOR_OXIDE}]"

        uptime = h.get("uptime_pct", 0.0)
        requests = h.get("total_requests", 0)
        errors = h.get("total_errors", 0)

        table.add_row(
            provider_type.value.upper(),
            status_str,
            tpm_str,
            budget_str,
            f"{uptime:.1f}%",
            str(requests),
            str(errors),
        )

    console.print(table)
    console.print()

    # Show model matrix
    settings = get_settings()
    models_table = Table(
        title=f"[{COLOR_BRONZE}]Model Matrix[/{COLOR_BRONZE}]",
        border_style=COLOR_UMBER,
        header_style=f"bold {COLOR_PARCHMENT}",
    )
    models_table.add_column("Tier", style=f"bold {COLOR_BRONZE}")
    models_table.add_column("Provider", style=COLOR_PARCHMENT)
    models_table.add_column("Model", style=COLOR_PARCHMENT)
    models_table.add_column("RPM", justify="right")
    models_table.add_column("TPM", justify="right")
    models_table.add_column("Speed (TPS)", justify="right")

    for provider_type, provider_config in settings.providers.items():
        for model_spec in provider_config.models:
            if model_spec.deprecated:
                continue
            models_table.add_row(
                model_spec.tier.value.upper(),
                provider_type.value.upper(),
                model_spec.name,
                str(model_spec.rpm),
                f"{model_spec.tpm:,}",
                f"{model_spec.speed_tps:.0f}" if model_spec.speed_tps else "—",
            )

    console.print(models_table)


# ─────────────────────────────────────────────────────────────────────────────
# vault — search the Obsidian vault
# ─────────────────────────────────────────────────────────────────────────────


@app.command()
def vault(
    query: str = typer.Argument(
        ...,
        help="Search query for the Obsidian vault.",
    ),
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        help="Maximum number of results to show.",
    ),
) -> None:
    """Search the HYPERION Second Brain (Obsidian vault) for prior research.

    The vault accumulates knowledge over time — engagement results, market
    research, competitor profiles, and analytical frameworks. This command
    searches the vault using keyword matching with relevance scoring.

    Examples:
        hyperion vault "Indian SaaS market"
        hyperion vault "competitor pricing strategy" -n 20
    """
    _print_banner()

    try:
        from hyperion.tools.second_brain import SecondBrainClient

        settings = get_settings()
        client = SecondBrainClient(settings=settings)

        search_result = asyncio.run(client.search(query))

        if not search_result or not search_result.notes:
            console.print(
                f"[{COLOR_UMBER}]No results found for '{query}'[/{COLOR_UMBER}]"
            )
            return

        table = Table(
            title=f"[{COLOR_BRONZE}]Vault Search: '{query}'[/{COLOR_BRONZE}]",
            border_style=COLOR_UMBER,
            header_style=f"bold {COLOR_PARCHMENT}",
        )
        table.add_column("#", style="dim", justify="right")
        table.add_column("Title", style=f"bold {COLOR_PARCHMENT}")
        table.add_column("Category", style=COLOR_BRONZE)
        table.add_column("Relevance", justify="right")
        table.add_column("Preview", style="dim")

        for i, (note, relevance) in enumerate(search_result.notes[:limit], 1):
            if relevance >= 0.5:
                rel_str = f"[{COLOR_VERDIGRIS}]{relevance:.2f}[/{COLOR_VERDIGRIS}]"
            elif relevance >= 0.25:
                rel_str = f"[{COLOR_BRONZE}]{relevance:.2f}[/{COLOR_BRONZE}]"
            else:
                rel_str = f"[{COLOR_UMBER}]{relevance:.2f}[/{COLOR_UMBER}]"

            title = note.title or "Untitled"
            category = note.category or "unknown"
            preview = note.content[:80].replace("\n", " ").strip()

            table.add_row(str(i), title, category, rel_str, preview + "..." if len(note.content) > 80 else preview)

        console.print(table)

    except ImportError:
        console.print(
            f"[{COLOR_OXIDE}]Second Brain client not available.[/{COLOR_OXIDE}]"
        )
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[{COLOR_OXIDE}]Vault search error: {e}[/{COLOR_OXIDE}]")
        raise typer.Exit(code=1)


# ─────────────────────────────────────────────────────────────────────────────
# export — export the most recent report
# ─────────────────────────────────────────────────────────────────────────────


@app.command()
def export(
    format: str = typer.Argument(
        "pdf",
        help="Export format: pdf, markdown, json.",
    ),
    engagement_id: str = typer.Option(
        "",
        "--engagement-id",
        "-e",
        help="Specific engagement ID to export. Default: most recent.",
    ),
    output: str = typer.Option(
        "",
        "--output",
        "-o",
        help="Output file path. Default: reports/hyperion_export_<format>",
    ),
) -> None:
    """Export a HYPERION report in the specified format.

    Formats:
    - pdf: Print-ready 300 DPI PDF with embedded fonts
    - markdown: Structured markdown for TUI display or documentation
    - json: Full FinalReport model as JSON (for programmatic access)

    Examples:
        hyperion export pdf
        hyperion export markdown -o reports/my_report.md
        hyperion export json -e eng_abc123
    """
    _print_banner()

    format = format.lower().strip()
    if format not in ("pdf", "markdown", "json"):
        console.print(
            f"[{COLOR_OXIDE}]Invalid format '{format}'. Use: pdf, markdown, or json[/{COLOR_OXIDE}]"
        )
        raise typer.Exit(code=1)

    # Find the engagement result
    reports_dir = Path("reports")
    if not reports_dir.exists():
        console.print(
            f"[{COLOR_OXIDE}]No reports directory found. Run an engagement first.[/{COLOR_OXIDE}]"
        )
        raise typer.Exit(code=1)

    # Look for engagement JSON files
    json_files = sorted(reports_dir.glob("hyperion_report_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not json_files:
        # Look for PDF files as fallback
        pdf_files = sorted(reports_dir.glob("hyperion_report_*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not pdf_files:
            console.print(
                f"[{COLOR_OXIDE}]No previous engagements found in reports/.[/{COLOR_OXIDE}]"
            )
            raise typer.Exit(code=1)

    # Load the engagement data
    engagement_data: dict[str, Any] = {}
    if json_files:
        with open(json_files[0], "r", encoding="utf-8") as f:
            engagement_data = json_module.load(f)
    else:
        console.print(
            f"[{COLOR_UMBER}]No JSON export found. Only PDF files available.[/{COLOR_UMBER}]"
        )
        if format != "pdf":
            console.print(
                f"[{COLOR_OXIDE}]Cannot export {format} without JSON data. Run a new engagement.[/{COLOR_OXIDE}]"
            )
            raise typer.Exit(code=1)

    # Generate output
    if format == "pdf":
        if engagement_data and "final_report" in engagement_data:
            # Re-render PDF from the stored FinalReport
            from hyperion.output.render import PDFRenderer

            renderer = PDFRenderer()
            output_path = output or str(reports_dir / f"hyperion_export_{int(__import__('time').time())}.pdf")
            result = renderer.render_from_template(
                report_data=engagement_data["final_report"],
                cover_data=engagement_data.get("cover_data"),
                output_path=output_path,
            )
            if result.success:
                console.print(f"[{COLOR_VERDIGRIS}]PDF exported: {result.pdf_path}[/{COLOR_VERDIGRIS}]")
            else:
                console.print(f"[{COLOR_OXIDE}]PDF export failed: {result.error}[/{COLOR_OXIDE}]")
                raise typer.Exit(code=1)
        else:
            # Just copy the existing PDF
            pdf_files = sorted(reports_dir.glob("hyperion_report_*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
            if pdf_files:
                import shutil
                output_path = output or str(reports_dir / f"hyperion_export_{int(__import__('time').time())}.pdf")
                shutil.copy2(pdf_files[0], output_path)
                console.print(f"[{COLOR_VERDIGRIS}]PDF copied: {output_path}[/{COLOR_VERDIGRIS}]")
            else:
                console.print(f"[{COLOR_OXIDE}]No PDF found to export.[/{COLOR_OXIDE}]")
                raise typer.Exit(code=1)

    elif format == "markdown":
        if not engagement_data or "final_report" not in engagement_data:
            console.print(f"[{COLOR_OXIDE}]No FinalReport data found for markdown export.[/{COLOR_OXIDE}]")
            raise typer.Exit(code=1)

        from hyperion.output.markdown import MarkdownExporter

        exporter = MarkdownExporter()
        result = exporter.export_to_file(
            engagement_data["final_report"],
            file_path=output or "",
        )
        if result.success:
            console.print(f"[{COLOR_VERDIGRIS}]Markdown exported: {result.file_path}[/{COLOR_VERDIGRIS}]")
        else:
            console.print(f"[{COLOR_OXIDE}]Markdown export failed: {result.error}[/{COLOR_OXIDE}]")
            raise typer.Exit(code=1)

    elif format == "json":
        if not engagement_data:
            console.print(f"[{COLOR_OXIDE}]No engagement data found for JSON export.[/{COLOR_OXIDE}]")
            raise typer.Exit(code=1)

        output_path = output or str(reports_dir / f"hyperion_export_{int(__import__('time').time())}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json_module.dump(engagement_data, f, indent=2, ensure_ascii=False)
        console.print(f"[{COLOR_VERDIGRIS}]JSON exported: {output_path}[/{COLOR_VERDIGRIS}]")


# ─────────────────────────────────────────────────────────────────────────────
# resume — resume a previous engagement
# ─────────────────────────────────────────────────────────────────────────────


@app.command()
def resume(
    engagement_id: str = typer.Argument(
        ...,
        help="The engagement ID to resume (e.g., eng_abc123def456).",
    ),
) -> None:
    """Resume a previous HYPERION engagement session.

    Loads the engagement state from the saved session and continues
    execution from where it left off. This is useful if an engagement
    was interrupted (network failure, timeout, etc.).

    The session is loaded from the reports/ directory.
    """
    _print_banner()

    console.print(f"[{COLOR_BRONZE}]Resuming engagement: {engagement_id}[/{COLOR_BRONZE}]")

    # Look for the engagement session file
    reports_dir = Path("reports")
    session_file = reports_dir / f"{engagement_id}_session.json"

    if not session_file.exists():
        # Try to find it by partial match
        matches = list(reports_dir.glob(f"*{engagement_id}*"))
        if matches:
            session_file = matches[0]
        else:
            console.print(
                f"[{COLOR_OXIDE}]No session found for engagement {engagement_id}[/{COLOR_OXIDE}]"
            )
            raise typer.Exit(code=1)

    with open(session_file, "r", encoding="utf-8") as f:
        session_data = json_module.load(f)

    console.print(
        Panel(
            f"[bold]Question:[/bold] {session_data.get('question', 'Unknown')}\n"
            f"[bold]Status:[/bold] {session_data.get('status', 'Unknown')}\n"
            f"[bold]Tasks Completed:[/bold] {session_data.get('tasks_completed', 0)}/{session_data.get('tasks_total', 0)}",
            title=f"[{COLOR_BRONZE}]Session Loaded[/{COLOR_BRONZE}]",
            border_style=COLOR_UMBER,
        )
    )

    # TODO: Implement full session resume logic
    console.print(
        f"[{COLOR_UMBER}]Session resume is not yet fully implemented.[/{COLOR_UMBER}]"
    )
    console.print(
        f"[{COLOR_UMBER}]The engagement will need to be re-run from the start.[/{COLOR_UMBER}]"
    )


# ─────────────────────────────────────────────────────────────────────────────
# help — show available commands
# ─────────────────────────────────────────────────────────────────────────────


@app.command()
def help() -> None:
    """Show available HYPERION commands."""
    _print_banner()

    table = Table(
        title=f"[{COLOR_BRONZE}]Available Commands[/{COLOR_BRONZE}]",
        border_style=COLOR_UMBER,
        header_style=f"bold {COLOR_PARCHMENT}",
    )
    table.add_column("Command", style=f"bold {COLOR_BRONZE}")
    table.add_column("Description", style=COLOR_PARCHMENT)

    table.add_row("consult <question>", "Start a new engagement (non-interactive)")
    table.add_row("shell", "Launch the interactive TUI engagement room")
    table.add_row("providers", "Show LLM provider status and rate limits")
    table.add_row("vault <query>", "Search the Obsidian vault for prior research")
    table.add_row("export <format>", "Export report (pdf, markdown, json)")
    table.add_row("resume <id>", "Resume a previous engagement session")
    table.add_row("help", "Show this help message")

    console.print(table)
    console.print()
    console.print(
        f"[dim]Slash commands in TUI: /consult /providers /vault /export /resume /help /clear[/dim]"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────


def main() -> None:
    """Main entry point for the HYPERION CLI."""
    app()


if __name__ == "__main__":
    main()
