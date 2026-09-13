"""
EcoRecycle Finder — Export Module
Exports recycling history and account summary to a CSV file.
"""

import csv
import json
from pathlib import Path
from datetime import datetime

from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich import box
from modules.ui import console

ACCOUNT_PATH = Path(__file__).parent.parent / "data" / "user_account.json"
EXPORTS_DIR  = Path(__file__).parent.parent / "exports"


def load_account() -> dict:
    with open(ACCOUNT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def export_history_to_csv(account: dict) -> Path:
    """
    Write recycling submission history to a timestamped CSV file.
    Returns the Path of the written file.
    """
    EXPORTS_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = EXPORTS_DIR / f"ecorecycle_history_{timestamp}.csv"

    history = account.get("devices_submitted", [])

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # ── Header block ───────────────────────────────────────────
        writer.writerow(["EcoRecycle Finder — Recycling History Export"])
        writer.writerow(["Username",      account.get("username", "EcoUser")])
        writer.writerow(["Member Since",  account.get("member_since", "—")])
        writer.writerow(["Total Points",  account.get("total_points", 0)])
        writer.writerow(["Devices Recycled", account.get("total_devices_recycled", 0)])
        writer.writerow(["Export Date",   datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        writer.writerow([])  # blank separator

        # ── Submission history ──────────────────────────────────────
        if history:
            writer.writerow(["#", "Device", "Qty", "Points Earned",
                             "Est. Metal Value (INR)", "Redemption Code", "Date"])
            for idx, entry in enumerate(history, start=1):
                writer.writerow([
                    idx,
                    entry.get("device", "—"),
                    entry.get("quantity", 1),
                    entry.get("points_earned", 0),
                    entry.get("value_inr", 0),
                    entry.get("code", "—"),
                    entry.get("date", "—"),
                ])
        else:
            writer.writerow(["No recycling submissions found."])

        writer.writerow([])

        # ── Voucher redemption history ──────────────────────────────
        vouchers = account.get("redemption_history", [])
        writer.writerow(["Voucher Redemption History"])
        if vouchers:
            writer.writerow(["#", "Voucher", "Partner", "Points Spent",
                             "Voucher Code", "Date"])
            for idx, v in enumerate(vouchers, start=1):
                writer.writerow([
                    idx,
                    v.get("voucher", "—"),
                    v.get("partner", "—"),
                    v.get("points_spent", 0),
                    v.get("code", "—"),
                    v.get("date", "—"),
                ])
        else:
            writer.writerow(["No vouchers redeemed yet."])

    return filename


def export_menu() -> None:
    """Interactive export flow — called from main menu or --export flag."""
    account = load_account()

    total_submissions = len(account.get("devices_submitted", []))
    total_vouchers    = len(account.get("redemption_history", []))

    console.print(
        Panel(
            f"[bold green]Export your EcoRecycle history to a CSV file.[/bold green]\n\n"
            f"  [bold white]Recycling submissions:[/bold white] [bright_green]{total_submissions}[/bright_green]\n"
            f"  [bold white]Vouchers redeemed:[/bold white]    [bright_yellow]{total_vouchers}[/bright_yellow]\n\n"
            f"[dim]The file will be saved in the [bold]exports/[/bold] folder "
            f"inside your project directory.[/dim]",
            title="[bold]📤 Export History[/bold]",
            border_style="green",
            padding=(1, 2),
        )
    )

    confirm = Prompt.ask(
        "[bold cyan]Proceed with export?[/bold cyan] [dim](y/n)[/dim]",
        default="y",
    ).strip().lower()

    if confirm != "y":
        console.print("[dim]Export cancelled.[/dim]")
        return

    out_path = export_history_to_csv(account)

    # Preview table of what was exported
    history = account.get("devices_submitted", [])
    if history:
        preview = Table(
            title="[bold green]📋 Export Preview (last 5 entries)[/bold green]",
            box=box.SIMPLE_HEAVY,
            border_style="dim green",
            header_style="bold green",
            padding=(0, 1),
        )
        preview.add_column("Device",           style="bold white", min_width=20)
        preview.add_column("Qty",              style="cyan",       width=5,  justify="center")
        preview.add_column("Points",           style="bold green", width=10, justify="right")
        preview.add_column("Value (₹)",        style="yellow",     width=11, justify="right")
        preview.add_column("Code",             style="dim bright_yellow", min_width=18)
        preview.add_column("Date",             style="dim white",  min_width=16)

        for entry in history[-5:]:
            preview.add_row(
                entry.get("device", "—"),
                str(entry.get("quantity", 1)),
                f"+{entry.get('points_earned', 0):,}",
                f"₹{entry.get('value_inr', 0):,.2f}",
                entry.get("code", "—"),
                entry.get("date", "—"),
            )
        console.print()
        console.print(preview)

    console.print(
        Panel(
            f"[bold bright_green]✔  Export successful![/bold bright_green]\n\n"
            f"  [bold white]File saved to:[/bold white]\n"
            f"  [bold cyan]{out_path}[/bold cyan]\n\n"
            f"  [dim]Open in Excel, Numbers, or any spreadsheet app.[/dim]",
            title="[bold green]📁 Export Complete[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
    )

    Prompt.ask("\n[dim]Press Enter to return to main menu[/dim]", default="")
