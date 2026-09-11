"""
EcoRecycle Finder — Rewards Dashboard Module
Displays accumulated points, history, and equivalent value.
"""

import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt
from rich import box
from rich.rule import Rule

console = Console()

ACCOUNT_PATH = Path(__file__).parent.parent / "data" / "user_account.json"

POINTS_TO_INR_RATIO = 0.10   # 1 point = ₹0.10  →  100 points = ₹10
TIER_THRESHOLDS = [
    (0,    "🌱 Seedling",   "dim green"),
    (250,  "🌿 Sprout",     "green"),
    (750,  "🍃 Green Hero", "bright_green"),
    (2000, "🌳 Eco Warrior","bold bright_green"),
    (5000, "🌍 Planet Saver","bold bright_cyan"),
]


def load_account() -> dict:
    with open(ACCOUNT_PATH, "r") as f:
        return json.load(f)


def get_tier(points: int) -> tuple[str, str]:
    """Return tier name and color style for given points total."""
    tier_name, tier_color = TIER_THRESHOLDS[0][1], TIER_THRESHOLDS[0][2]
    for threshold, name, color in TIER_THRESHOLDS:
        if points >= threshold:
            tier_name, tier_color = name, color
    return tier_name, tier_color


def next_tier_info(points: int) -> tuple[str, int] | None:
    """Return next tier name and points needed, or None if max."""
    for i, (threshold, name, _) in enumerate(TIER_THRESHOLDS):
        if points < threshold:
            return name, threshold - points
    return None, 0


def rewards_dashboard_menu() -> None:
    """Display the rewards dashboard."""
    account = load_account()
    total_points = account.get("total_points", 0)
    total_devices = account.get("total_devices_recycled", 0)
    member_since = account.get("member_since", "2026-01-01")
    history = account.get("devices_submitted", [])

    tier_name, tier_color = get_tier(total_points)
    next_tier, pts_needed = next_tier_info(total_points)
    inr_value = round(total_points * POINTS_TO_INR_RATIO, 2)

    # ── Header / Summary Panel ──────────────────────────────────────────────
    progress_bar_len = 30
    if next_tier and pts_needed is not None:
        current_threshold = total_points
        # Find current tier threshold
        ct = 0
        for thr, name, _ in TIER_THRESHOLDS:
            if total_points >= thr:
                ct = thr
        nt = ct + pts_needed
        ratio = (total_points - ct) / (nt - ct) if nt != ct else 1.0
        filled = int(ratio * progress_bar_len)
        bar = "[bold green]" + "█" * filled + "[/bold green]" + "[dim]" + "░" * (progress_bar_len - filled) + "[/dim]"
        progress_str = f"\n  Progress to {next_tier}: {bar} [dim]{pts_needed} pts to go[/dim]"
    else:
        progress_str = "\n  [bold bright_cyan]🏆 Maximum tier achieved![/bold bright_cyan]"

    summary_content = (
        f"  [bold white]👤 Account:[/bold white]  [bright_white]{account.get('username', 'EcoUser')}[/bright_white]   "
        f"[dim]Member since {member_since}[/dim]\n\n"
        f"  [{tier_color}]🎖  Tier: {tier_name}[/{tier_color}]\n"
        f"{progress_str}\n\n"
        f"  [bold white]💚 Total Points:[/bold white]  [{tier_color}][bold]{total_points:,}[/bold][/{tier_color}]  pts\n"
        f"  [bold white]💰 Cash Equiv.:[/bold white]  [bold yellow]₹{inr_value:,.2f}[/bold yellow]  [dim](@ ₹0.10/point)[/dim]\n"
        f"  [bold white]♻  Devices Recycled:[/bold white]  [bold bright_green]{total_devices}[/bold bright_green]  device(s)"
    )

    console.print(
        Panel(
            summary_content,
            title="[bold green]🏆 My EcoRewards Dashboard[/bold green]",
            border_style="green",
            padding=(1, 2),
            expand=True,
        )
    )

    # ── Tier Guide ──────────────────────────────────────────────────────────
    tier_table = Table(
        title="[bold green]🎖  Tier Guide[/bold green]",
        box=box.SIMPLE,
        border_style="dim green",
        header_style="bold green",
        padding=(0, 2),
        show_lines=False,
    )
    tier_table.add_column("Tier", style="bold white", min_width=20)
    tier_table.add_column("Points Required", style="cyan", justify="right", min_width=18)
    tier_table.add_column("Cash Value (equiv.)", style="yellow", justify="right", min_width=20)
    tier_table.add_column("Status", width=10, justify="center")

    for threshold, name, color in TIER_THRESHOLDS:
        status = "[bold green]✔ Achieved[/bold green]" if total_points >= threshold else "[dim]Locked[/dim]"
        tier_table.add_row(
            f"[{color}]{name}[/{color}]",
            f"{threshold:,}+",
            f"₹{threshold * POINTS_TO_INR_RATIO:,.0f}+",
            status,
        )

    console.print()
    console.print(tier_table)

    # ── Device Submission History ───────────────────────────────────────────
    console.print()
    if history:
        history_table = Table(
            title=f"[bold green]📋 Recycling History ({len(history)} submission(s))[/bold green]",
            box=box.ROUNDED,
            border_style="green",
            header_style="bold bright_green on dark_green",
            show_lines=True,
            padding=(0, 1),
        )
        history_table.add_column("#", style="dim cyan", width=3, justify="center")
        history_table.add_column("Device", style="bold white", min_width=20)
        history_table.add_column("Qty", style="cyan", width=5, justify="center")
        history_table.add_column("Points", style="bold green", width=10, justify="right")
        history_table.add_column("Value (₹)", style="yellow", width=12, justify="right")
        history_table.add_column("Redemption Code", style="dim bright_yellow", min_width=20)
        history_table.add_column("Date", style="dim white", min_width=18)

        for idx, entry in enumerate(reversed(history[-10:]), start=1):  # Show last 10
            history_table.add_row(
                str(idx),
                entry.get("device", "—"),
                str(entry.get("quantity", 1)),
                f"+{entry.get('points_earned', 0):,}",
                f"₹{entry.get('value_inr', 0):,.2f}",
                entry.get("code", "—"),
                entry.get("date", "—"),
            )

        console.print(history_table)
    else:
        console.print(
            Panel(
                "[dim]No recycling history yet.\nUse [bold]Option 3 — Calculate Recycling Points[/bold] to get started![/dim]",
                border_style="dim green",
                padding=(1, 2),
            )
        )

    # ── Redemption Info ─────────────────────────────────────────────────────
    console.print(
        Panel(
            "  [bold white]💡 How to Redeem:[/bold white]\n"
            "  [green]•[/green] Visit any [bold]EcoRecycle certified[/bold] facility.\n"
            "  [green]•[/green] Show your [bold bright_yellow]Redemption Code[/bold bright_yellow] at the counter.\n"
            "  [green]•[/green] Points are converted to [bold yellow]₹ discount vouchers or store credit[/bold yellow].\n"
            "  [green]•[/green] Minimum redemption: [bold]100 points (₹10)[/bold]",
            title="[bold yellow]🎁 Redemption Guide[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        )
    )

    Prompt.ask("\n[dim]Press Enter to return to main menu[/dim]", default="")
