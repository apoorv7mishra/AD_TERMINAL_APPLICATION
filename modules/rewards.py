"""
EcoRecycle Finder — Rewards & Sustainability Dashboard Module
Displays accumulated EcoPoints, tier status, environmental impact metrics,
and an interactive Partner Voucher Redemption Store.
"""

import json
import random
import string
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt
from rich import box
from rich.columns import Columns

console = Console()

ACCOUNT_PATH = Path(__file__).parent.parent / "data" / "user_account.json"

POINTS_TO_INR_RATIO = 0.10   # 1 point = ₹0.10  →  100 points = ₹10
TIER_THRESHOLDS = [
    (0,    "🌱 Seedling",    "dim green"),
    (250,  "🌿 Sprout",      "green"),
    (750,  "🍃 Green Hero",  "bright_green"),
    (2000, "🌳 Eco Warrior", "bold bright_green"),
    (5000, "🌍 Planet Saver","bold bright_cyan"),
]

AVAILABLE_VOUCHERS = [
    {"id": "1", "partner": "Amazon Pay", "name": "₹50 Amazon Pay Gift Card", "points": 500, "code_prefix": "AMZ-ECO"},
    {"id": "2", "partner": "Croma Electronics", "name": "₹100 Croma Green Recycling Coupon", "points": 1000, "code_prefix": "CROMA-GRN"},
    {"id": "3", "partner": "Flipkart", "name": "₹250 Flipkart SuperVoucher", "points": 2500, "code_prefix": "FK-ECO"},
    {"id": "4", "partner": "SankalpTaru Foundation", "name": "Plant 1 Native Tree Certificate", "points": 200, "code_prefix": "TREE-IND"},
]


def load_account() -> dict:
    with open(ACCOUNT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_account(account: dict) -> None:
    with open(ACCOUNT_PATH, "w", encoding="utf-8") as f:
        json.dump(account, f, indent=2)


def get_tier(points: int) -> tuple[str, str]:
    """Return tier name and color style for given points total."""
    tier_name, tier_color = TIER_THRESHOLDS[0][1], TIER_THRESHOLDS[0][2]
    for threshold, name, color in TIER_THRESHOLDS:
        if points >= threshold:
            tier_name, tier_color = name, color
    return tier_name, tier_color


def next_tier_info(points: int) -> tuple[str, int] | None:
    """Return next tier name and points needed, or None if max tier."""
    for threshold, name, _ in TIER_THRESHOLDS:
        if points < threshold:
            return name, threshold - points
    return None, 0


def redeem_voucher_flow(account: dict) -> None:
    """Interactive voucher redemption store."""
    total_points = account.get("total_points", 0)

    console.print(
        Panel(
            "[bold green]Convert your EcoCredit Points into real-world partner rewards.[/bold green]\n"
            "[dim]Select a voucher to redeem. Codes are instantly generated and saved to your history.[/dim]",
            title="[bold yellow]🎁 Partner Rewards & Voucher Store[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        )
    )

    table = Table(
        box=box.ROUNDED,
        border_style="yellow",
        header_style="bold yellow",
        padding=(0, 2),
    )
    table.add_column("#", style="dim cyan", width=3, justify="center")
    table.add_column("Partner", style="bold white", min_width=18)
    table.add_column("Reward Voucher", style="white", min_width=32)
    table.add_column("Points Required", style="bold yellow", justify="right", min_width=16)
    table.add_column("Status", justify="center", width=14)

    for v in AVAILABLE_VOUCHERS:
        can_afford = total_points >= v["points"]
        status = "[bold green]✔ Available[/bold green]" if can_afford else "[dim red]Insufficient Pts[/dim red]"
        table.add_row(
            v["id"],
            v["partner"],
            v["name"],
            f"{v['points']:,} pts",
            status,
        )

    console.print(table)
    console.print(f"\n[bold]Your Current Balance:[/bold] [bold bright_yellow]{total_points:,} EcoPoints[/bold bright_yellow]")

    choice = Prompt.ask(
        "\n[bold cyan]Enter voucher number to redeem (1–4)[/bold cyan] [dim]or 0 to cancel[/dim]",
        default="0",
    ).strip()

    if choice == "0":
        return

    selected = next((v for v in AVAILABLE_VOUCHERS if v["id"] == choice), None)
    if not selected:
        console.print("[red]Invalid voucher selection.[/red]")
        return

    if total_points < selected["points"]:
        console.print(
            f"[red]You need [bold]{selected['points'] - total_points}[/bold] more points to redeem this voucher.[/red]"
        )
        Prompt.ask("[dim]Press Enter to return[/dim]", default="")
        return

    # Deduct points
    account["total_points"] -= selected["points"]
    random_str = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    voucher_code = f"{selected['code_prefix']}-{random_str[:4]}-{random_str[4:]}"

    voucher_record = {
        "voucher": selected["name"],
        "partner": selected["partner"],
        "code": voucher_code,
        "points_spent": selected["points"],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    account.setdefault("redemption_history", []).append(voucher_record)
    save_account(account)

    console.print(
        Panel(
            f"[bold bright_green]🎉 Congratulations! Voucher Successfully Redeemed![/bold bright_green]\n\n"
            f"  [white]Voucher:[/white] [bold]{selected['name']}[/bold]\n"
            f"  [white]Partner:[/white] [cyan]{selected['partner']}[/cyan]\n"
            f"  [white]Voucher Code:[/white] [bold black on bright_yellow]  {voucher_code}  [/bold black on bright_yellow]\n\n"
            f"  [dim]Remaining Balance: {account['total_points']:,} EcoPoints[/dim]\n"
            f"  [dim italic]Use this code online or in-store with the partner.[/dim italic]",
            title="[bold green]Voucher Issued[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
    )
    Prompt.ask("\n[dim]Press Enter to return to Rewards Dashboard[/dim]", default="")


def rewards_dashboard_menu() -> None:
    """Display the full rewards dashboard and environmental metrics."""
    account = load_account()
    total_points = account.get("total_points", 0)
    total_devices = account.get("total_devices_recycled", 0)
    member_since = account.get("member_since", "2026-09-11")
    history = account.get("devices_submitted", [])
    voucher_history = account.get("redemption_history", [])

    tier_name, tier_color = get_tier(total_points)
    next_tier, pts_needed = next_tier_info(total_points)
    inr_value = round(total_points * POINTS_TO_INR_RATIO, 2)

    # Compute cumulative environmental impact metrics
    co2_total = sum(item.get("co2_saved_kg", 0) for item in history)
    water_saved_litres = int(total_devices * 1250)  # ~1250 L clean water saved per device diverted from toxic runoff
    metals_diverted_g = round(total_devices * 35.0, 1)

    # ── Progress Bar ──────────────────────────────────────────────
    progress_bar_len = 28
    if next_tier and pts_needed is not None:
        ct = 0
        for thr, _, _ in TIER_THRESHOLDS:
            if total_points >= thr:
                ct = thr
        nt = ct + pts_needed
        ratio = (total_points - ct) / (nt - ct) if nt != ct else 1.0
        filled = int(ratio * progress_bar_len)
        bar = "[bold green]" + "█" * filled + "[/bold green]" + "[dim]" + "░" * (progress_bar_len - filled) + "[/dim]"
        progress_str = f"Progress to {next_tier}: {bar} [dim]({pts_needed} pts needed)[/dim]"
    else:
        progress_str = "[bold bright_cyan]🏆 Maximum Legend Tier Achieved![/bold bright_cyan]"

    summary_content = (
        f"  [bold white]User Profile:[/bold white]  [bold bright_white]{account.get('username', 'EcoUser')}[/bold bright_white]   "
        f"[dim](Member since {member_since})[/dim]\n\n"
        f"  [{tier_color}]🎖  Current Status: {tier_name}[/{tier_color}]\n"
        f"  {progress_str}\n\n"
        f"  [bold white]💚 Available EcoCredits:[/bold white]  [{tier_color}][bold]{total_points:,}[/bold][/{tier_color}] pts\n"
        f"  [bold white]💰 Cash Value Equivalent:[/bold white] [bold yellow]₹{inr_value:,.2f}[/bold yellow] [dim](@ ₹0.10/point)[/dim]\n"
        f"  [bold white]♻  Total Items Recycled:[/bold white]   [bold bright_green]{total_devices}[/bold bright_green] device(s)"
    )

    console.print(
        Panel(
            summary_content,
            title="[bold green]🏆 EcoRewards & User Profile[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
    )

    # ── Environmental Impact Cards ──────────────────────────────
    impact_cards = [
        Panel(
            f"[bold bright_green]{co2_total:,.1f} kg[/bold bright_green]\n[dim]CO₂ Emissions\nPrevented[/dim]",
            border_style="green",
            padding=(0, 2),
        ),
        Panel(
            f"[bold bright_cyan]{water_saved_litres:,} L[/bold bright_cyan]\n[dim]Freshwater\nPreserved[/dim]",
            border_style="cyan",
            padding=(0, 2),
        ),
        Panel(
            f"[bold bright_yellow]{metals_diverted_g:,} g[/bold bright_yellow]\n[dim]Toxic Heavy Metals\nDiverted from Soil[/dim]",
            border_style="yellow",
            padding=(0, 2),
        ),
    ]
    console.print(Columns(impact_cards, equal=True))

    # ── Tier Guide Table ────────────────────────────────────────
    tier_table = Table(
        title="[bold green]🎖  Reward Tier Progression[/bold green]",
        box=box.SIMPLE_HEAVY,
        border_style="dim green",
        header_style="bold green",
        padding=(0, 2),
    )
    tier_table.add_column("Tier", style="bold white", min_width=20)
    tier_table.add_column("Min Points", style="cyan", justify="right", min_width=14)
    tier_table.add_column("Perks & Benefits", style="dim white", min_width=28)
    tier_table.add_column("Status", width=12, justify="center")

    perks = [
        "Standard collection points",
        "5% bonus on metal values",
        "10% bonus + Green Hero Badge",
        "15% bonus + Priority CPCB pickup",
        "20% bonus + VIP Partner Vouchers",
    ]

    for idx, (threshold, name, color) in enumerate(TIER_THRESHOLDS):
        status = "[bold green]✔ Active[/bold green]" if total_points >= threshold else "[dim]Locked[/dim]"
        tier_table.add_row(
            f"[{color}]{name}[/{color}]",
            f"{threshold:,}+",
            perks[idx],
            status,
        )

    console.print()
    console.print(tier_table)

    # ── Recent Activity / History ───────────────────────────────
    console.print()
    if history:
        history_table = Table(
            title=f"[bold green]📋 Recent Recycling Submissions ({len(history)} item(s))[/bold green]",
            box=box.ROUNDED,
            border_style="green",
            header_style="bold bright_green on dark_green",
            show_lines=True,
            padding=(0, 1),
        )
        history_table.add_column("#", style="dim cyan", width=3, justify="center")
        history_table.add_column("Device Model", style="bold white", min_width=22)
        history_table.add_column("Qty", style="cyan", width=4, justify="center")
        history_table.add_column("EcoPoints", style="bold green", width=11, justify="right")
        history_table.add_column("Est. Value", style="yellow", width=11, justify="right")
        history_table.add_column("Drop-Off Code", style="bold bright_yellow", min_width=18)
        history_table.add_column("Date", style="dim white", min_width=16)

        for idx, entry in enumerate(reversed(history[-6:]), start=1):
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

    # Action Menu
    console.print(
        "\n[bold white]Rewards Actions:[/bold white]\n"
        "  [bold bright_yellow]R[/bold bright_yellow] — 🎁 [bold]Redeem Points in Partner Voucher Store (Amazon, Croma, Flipkart, Trees)[/bold]\n"
        "  [bold cyan]0[/bold cyan] — 🚪 Return to Main Menu"
    )

    action = Prompt.ask("\n[bold cyan]Select action (R or 0)[/bold cyan]", default="0").strip().upper()
    if action == "R":
        redeem_voucher_flow(account)
