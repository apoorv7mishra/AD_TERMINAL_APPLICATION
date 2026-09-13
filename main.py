#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                   EcoRecycle Finder — main.py                             ║
║      Intelligent E-Waste Collection, Hazard Awareness & Recovery CLI      ║
║           Ministry of Environment Safe Recycling Solution                 ║
╚═══════════════════════════════════════════════════════════════════════════╝

Usage:
    python main.py              # Launch interactive terminal UI
    python main.py --locate     # Jump directly to facility locator
    python main.py --learn      # Jump directly to toxicology library
    python main.py --points     # Jump directly to points & metal calculator
    python main.py --rewards    # Jump directly to rewards dashboard
    python main.py --version    # Print version details
"""

import os
import sys
import argparse
import time
import json
from pathlib import Path

from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich import box
from rich.align import Align
from rich.table import Table
from rich.live import Live
from rich.spinner import Spinner
from rich.columns import Columns
import rich.traceback

# Install rich tracebacks
rich.traceback.install(show_locals=False)

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent))

from modules.facility_locator import facility_locator_menu
from modules.education import education_menu
from modules.points_calculator import points_calculator_menu
from modules.rewards import rewards_dashboard_menu, get_tier
from modules.exporter import export_menu
from modules.ui import console

ACCOUNT_PATH = Path(__file__).parent / "data" / "user_account.json"


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


# ── Modern Unicode Banner ───────────────────────────────────────────────────

BANNER = r"""
 █▀▀ █▀▀ █▀█ █▀█ █▀▀ █▀▀ █▄█ █▀▀ █   █▀▀
 █▀▀ █▄▄ █▄█ █▀▄ █▀▀ █▄▄  █  █▄▄ █▄▄ █▀▀
  F I N D E R  •  L O C A T E  •  L E A R N  •  E A R N
"""


def get_user_quick_stats() -> tuple[str, str, int, int]:
    """Fetch quick stats for the banner status bar."""
    try:
        with open(ACCOUNT_PATH, "r", encoding="utf-8") as f:
            acc = json.load(f)
            username = acc.get("username", "EcoUser")
            points = acc.get("total_points", 0)
            devices = acc.get("total_devices_recycled", 0)
            tier_name, _ = get_tier(points)
            return username, tier_name, points, devices
    except Exception:
        return "EcoUser", "🌱 Seedling", 0, 0


def show_splash() -> None:
    """Display modern aesthetic splash header with live user badge."""
    clear_screen()
    username, tier_name, points, devices = get_user_quick_stats()

    header_text = (
        f"[brand]{BANNER.strip()}[/brand]\n"
        f"[brand.dim]NATIONAL E-WASTE RECOVERY NETWORK  /  MOEFCC INDIA[/brand.dim]\n"
    )

    console.print(
        Panel(
            Align.center(header_text),
            border_style="#2f6f68",
            padding=(1, 2),
        )
    )

    # Status Bar
    status_bar = Table(box=box.SIMPLE, show_header=False, padding=(0, 2), expand=True)
    status_bar.add_column("User", style="white", justify="left")
    status_bar.add_column("Tier", style="info", justify="center")
    status_bar.add_column("Points", style="accent", justify="center")
    status_bar.add_column("Items", style="success", justify="right")

    status_bar.add_row(
        f"PROFILE  [bold]{username}[/bold]",
        f"TIER  [bold]{tier_name}[/bold]",
        f"BALANCE  [bold accent]{points:,}[/bold accent] pts",
        f"DIVERTED  [bold success]{devices}[/bold success] devices",
    )
    console.print(Panel(status_bar, border_style="#263f43", padding=(0, 1)))


def show_loading(message: str = "Loading", duration: float = 0.5) -> None:
    """Polished micro-animation."""
    with Live(
        Spinner("dots", text=f"[brand]{message}...[/brand]", style="brand"),
        console=console,
        transient=True,
    ):
        time.sleep(duration)


# ── About & Problem Statement Alignment Screen ──────────────────────────────

def show_about() -> None:
    clear_screen()
    show_splash()

    about_content = (
        "[bold green]EcoRecycle Finder[/bold green] is an intelligent software solution built for the\n"
        "[bold bright_white]Ministry of Environment, Forest and Climate Change (MoEFCC)[/bold bright_white] Problem Statement.\n\n"
        "[bold white]🎯 Problem Statement Alignment:[/bold white]\n"
        "  [green]1. 🗺 Facility Locator:[/green] Real-time geolocation using the Haversine formula to\n"
        "     pinpoint nearest CPCB-certified collection hubs across major Indian metros.\n"
        "  [green]2. 🚨 Educational Pop-ups:[/green] Contextual toxic hazard disclosures (lead, cadmium,\n"
        "     mercury) before recycling to promote environmental awareness.\n"
        "  [green]3. ⚡ Precious Metals Calculator:[/green] Input device brand & model to compute salvable\n"
        "     Gold, Silver, Copper, Palladium & Platinum, earning redeemable EcoCredits.\n\n"
        "[bold white]📊 Key India E-Waste Facts:[/bold white]\n"
        "  [red]•[/red]  India generates [bold]~3.2 million tonnes[/bold] of e-waste annually (3rd globally)\n"
        "  [red]•[/red]  Only [bold]~5%[/bold] reaches formal, environmentally sound recyclers\n"
        "  [green]•[/green]  Proper recycling recovers finite precious metals with [bold]95% less energy[/bold]\n\n"
        "[dim]Version 2.0.0-PRO  •  CPCB Registered Partner Network  •  Open Source MIT[/dim]"
    )

    console.print(
        Panel(
            about_content,
            title="[bold green]ℹ  About & Ministry Directive Alignment[/bold green]",
            border_style="green",
            padding=(1, 3),
        )
    )

    # Quick stats grid
    stat_panels = [
        Panel(
            Align.center(
                Text("3.2 MT\n", style="bold bright_green")
                + Text("Annual E-waste\nin India", style="dim white")
            ),
            border_style="green",
            padding=(1, 1),
        ),
        Panel(
            Align.center(
                Text("~5%\n", style="bold yellow")
                + Text("Formally\nRecycled", style="dim white")
            ),
            border_style="yellow",
            padding=(1, 1),
        ),
        Panel(
            Align.center(
                Text("62+\n", style="bold cyan")
                + Text("Metals per\nSmartphone", style="dim white")
            ),
            border_style="cyan",
            padding=(1, 1),
        ),
        Panel(
            Align.center(
                Text("14.5 kg\n", style="bold bright_green")
                + Text("CO₂ Offset per\nRecycled kg", style="dim white")
            ),
            border_style="bright_green",
            padding=(1, 1),
        ),
    ]
    console.print(Columns(stat_panels, equal=True))
    Prompt.ask("\n[dim]Press Enter to return to main menu[/dim]", default="")


# ── Main Menu ────────────────────────────────────────────────────────────────

MENU_ITEMS = [
    ("1", "🗺 ", "Find Nearby Facility",       "Locate certified CPCB collection hubs with live status"),
    ("2", "📚 ", "Learn & Take Eco-Quiz",       "Hazard toxicology library + interactive quiz (+50 pts)"),
    ("3", "⚡ ", "Calculate Recycling Points",   "Fuzzy model search, hazard alert & precious metals yield"),
    ("4", "🏆 ", "My Rewards & Voucher Store",  "View points, redeem Amazon/Flipkart vouchers & certificates"),
    ("5", "📤 ", "Export History",               "Save recycling & voucher history to a CSV file"),
    ("6", "ℹ  ", "About & Problem Statement",    "Architecture details & India e-waste directive alignment"),
    ("7", "🚪 ", "Exit Application",            "Close the application safely"),
]


def show_main_menu() -> None:
    """Render the high-aesthetic main menu."""
    show_splash()

    menu_table = Table(
        box=box.ROUNDED,
        border_style="green",
        show_header=False,
        padding=(0, 2),
        expand=True,
    )
    menu_table.add_column("Num", style="bold bright_green", width=4, justify="center", no_wrap=True)
    menu_table.add_column("Icon", width=4, no_wrap=True)
    menu_table.add_column("Option", style="bold white", ratio=2, no_wrap=True)
    menu_table.add_column("Description", style="dim white", ratio=3)

    for num, icon, option, desc in MENU_ITEMS:
        menu_table.add_row(
            f"[bold bright_green]{num}[/bold bright_green]",
            icon,
            option,
            f"[dim]{desc}[/dim]",
        )

    console.print(
        Panel(
            Align.center(menu_table),
            title="[brand]ECORECYCLE  /  COMMAND CENTER[/brand]",
            subtitle="[muted]Choose a destination  [1-7]  and press Enter[/muted]",
            border_style="#2f6f68",
            padding=(1, 2),
        )
    )


def main_loop() -> None:
    """Run the interactive main menu loop with graceful exit handling."""
    show_loading("Connecting to EcoRecycle Central Hub", duration=0.6)

    while True:
        try:
            show_main_menu()

            choice = Prompt.ask(
                "\n[bold bright_green]Select an option[/bold bright_green] [dim](1–7)[/dim]",
                default="1",
            ).strip()

            if choice == "1":
                clear_screen()
                show_loading("Loading Facility Geolocation Engine")
                facility_locator_menu()

            elif choice == "2":
                clear_screen()
                show_loading("Loading Toxicology Library")
                education_menu()

            elif choice == "3":
                clear_screen()
                show_loading("Loading Metal Valuation Engine")
                points_calculator_menu()

            elif choice == "4":
                clear_screen()
                show_loading("Loading Rewards & Voucher Store")
                rewards_dashboard_menu()

            elif choice == "5":
                clear_screen()
                show_loading("Preparing Export")
                export_menu()

            elif choice == "6":
                show_about()

            elif choice == "7":
                clear_screen()
                console.print(
                    Panel(
                        Align.center(
                            Text(
                                "\n  🌿  Thank you for choosing to recycle responsibly!  🌿\n\n"
                                "  Every circuit board safely recycled protects\n"
                                "  India's groundwater and human health.\n\n"
                                "  — EcoRecycle India Initiative  •  Ministry of Environment Partner\n",
                                style="bold green",
                            )
                        ),
                        border_style="green",
                        padding=(1, 4),
                    )
                )
                sys.exit(0)

            else:
                console.print("[red]Invalid option. Please enter a number between 1 and 7.[/red]")
                time.sleep(0.8)

        except KeyboardInterrupt:
            console.print("\n\n")
            console.print(
                Panel(
                    Align.center(
                        Text(
                            "🌿 Thank you for championing responsible e-waste recycling! 🌿\n"
                            "Session cleanly ended.",
                            style="bold green",
                        )
                    ),
                    border_style="green",
                    padding=(1, 3),
                )
            )
            sys.exit(0)


# ── CLI argument parsing ─────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ecorecycle",
        description=(
            "EcoRecycle Finder — High-Aesthetic E-Waste Recycling CLI.\n"
            "Locate CPCB facilities, review toxic hazards, and earn precious metal credits."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python main.py              # Launch interactive UI\n"
            "  python main.py --locate     # Jump straight to facility locator\n"
            "  python main.py --learn      # Jump straight to education & quiz\n"
            "  python main.py --points     # Jump straight to points calculator\n"
            "  python main.py --rewards    # Jump straight to rewards & vouchers\n"
        ),
    )
    parser.add_argument(
        "--locate", action="store_true",
        help="Open facility locator directly"
    )
    parser.add_argument(
        "--learn", action="store_true",
        help="Open education module directly"
    )
    parser.add_argument(
        "--points", action="store_true",
        help="Open recycling points calculator directly"
    )
    parser.add_argument(
        "--rewards", action="store_true",
        help="Open rewards dashboard directly"
    )
    parser.add_argument(
        "--export", action="store_true",
        help="Export recycling history to a CSV file and exit"
    )
    parser.add_argument(
        "--version", action="version", version="EcoRecycle Finder v2.0.0-PRO"
    )
    return parser.parse_args()


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = parse_args()
    try:
        if args.locate:
            show_splash()
            facility_locator_menu()
        elif args.learn:
            show_splash()
            education_menu()
        elif args.points:
            show_splash()
            points_calculator_menu()
        elif args.rewards:
            show_splash()
            rewards_dashboard_menu()
        elif args.export:
            show_splash()
            export_menu()
        else:
            main_loop()
    except KeyboardInterrupt:
        console.print("\n[bold green]🌿 Safe recycling saves lives. Goodbye![/bold green]")
        sys.exit(0)
