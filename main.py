#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════╗
║           EcoRecycle Finder — main.py                     ║
║   A CLI tool for responsible e-waste recycling in India   ║
╚═══════════════════════════════════════════════════════════╝

Usage:
    python main.py          # launch interactive menu
    python main.py --help   # show help
"""

import os
import sys
import argparse
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich import box
from rich.rule import Rule
from rich.align import Align
from rich.table import Table
from rich.live import Live
from rich.spinner import Spinner
from rich.columns import Columns
import rich.traceback

# Install rich tracebacks for nicer error output
rich.traceback.install(show_locals=False)

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent))

from modules.facility_locator import facility_locator_menu
from modules.education import education_menu
from modules.points_calculator import points_calculator_menu
from modules.rewards import rewards_dashboard_menu

console = Console()

# ── ANSI / terminal helpers ──────────────────────────────────────────────────

def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


# ── Splash / Banner ──────────────────────────────────────────────────────────

BANNER = r"""
  ___           ___                         _       
 | __|__ ___   | _ \___ __ _  _ ____ __ __| |___   
 | _|/ _/ _ \  |   / -_) _| || / _| | V  V / -_)  
 |___\__\___/  |_|_\___\__|\_,_\__|  \_/\_/\___|  
                                                    
  ███████╗██╗███╗   ██╗██████╗ ███████╗██████╗    
  ██╔════╝██║████╗  ██║██╔══██╗██╔════╝██╔══██╗   
  █████╗  ██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝   
  ██╔══╝  ██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗   
  ██║     ██║██║ ╚████║██████╔╝███████╗██║  ██║   
  ╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝  
"""

def show_splash() -> None:
    """Display animated splash screen."""
    clear_screen()
    console.print(
        Panel(
            Align.center(
                Text(BANNER, style="bold green")
            ),
            border_style="green",
            padding=(0, 2),
        )
    )
    console.print(
        Align.center(
            Text(
                "♻  Locate • Learn • Earn — Responsible E-Waste Recycling",
                style="italic dim green",
            )
        )
    )
    console.print(
        Align.center(
            Text("Powered by EcoRecycle India Initiative  🌿", style="dim")
        )
    )
    console.print()


def show_loading(message: str = "Loading", duration: float = 0.8) -> None:
    """Brief loading animation."""
    with Live(
        Spinner("dots", text=f"[green]{message}...[/green]", style="green"),
        console=console,
        transient=True,
    ):
        time.sleep(duration)


# ── About Screen ─────────────────────────────────────────────────────────────

def show_about() -> None:
    clear_screen()
    show_splash()

    about_content = (
        "[bold green]EcoRecycle Finder[/bold green] is a terminal-based tool that helps\n"
        "Indian citizens responsibly dispose of their electronic waste.\n\n"
        "[bold white]What we do:[/bold white]\n"
        "  [green]🗺[/green]  Connect you to CPCB-certified collection centres\n"
        "  [green]📚[/green]  Educate about hazardous materials in electronics\n"
        "  [green]⚡[/green]  Estimate recoverable precious metals in your device\n"
        "  [green]🏆[/green]  Reward responsible recycling with credit points\n\n"
        "[bold white]E-Waste in India — Key Facts:[/bold white]\n"
        "  [red]•[/red]  India generates [bold]~3.2 million tonnes[/bold] of e-waste per year\n"
        "  [red]•[/red]  Only [bold]~5%[/bold] is formally recycled\n"
        "  [red]•[/red]  ~[bold]1.5 crore[/bold] informal workers handle e-waste unsafely\n"
        "  [green]•[/green]  Proper recycling conserves [bold]finite natural resources[/bold]\n"
        "  [green]•[/green]  You can earn real rewards for doing the right thing!\n\n"
        "[bold white]Version:[/bold white]  1.0.0\n"
        "[bold white]Author:[/bold white]   EcoRecycle India Dev Team\n"
        "[bold white]License:[/bold white]  MIT Open Source\n"
        "[bold white]Contact:[/bold white]  hello@ecorecycle.in"
    )

    console.print(
        Panel(
            about_content,
            title="[bold green]ℹ  About EcoRecycle Finder[/bold green]",
            border_style="green",
            padding=(1, 3),
        )
    )

    # Quick stats grid
    stat_panels = [
        Panel(
            Align.center(
                Text("3.2 MT\n", style="bold bright_green")
                + Text("E-waste/year\nin India", style="dim white")
            ),
            border_style="green",
            padding=(1, 2),
        ),
        Panel(
            Align.center(
                Text("~5%\n", style="bold yellow")
                + Text("Formally\nrecycled", style="dim white")
            ),
            border_style="yellow",
            padding=(1, 2),
        ),
        Panel(
            Align.center(
                Text("62+\n", style="bold cyan")
                + Text("Metals in\n1 smartphone", style="dim white")
            ),
            border_style="cyan",
            padding=(1, 2),
        ),
        Panel(
            Align.center(
                Text("₹∞\n", style="bold bright_green")
                + Text("Value of\nrecoverable metals", style="dim white")
            ),
            border_style="bright_green",
            padding=(1, 2),
        ),
    ]
    console.print(Columns(stat_panels, equal=True))

    Prompt.ask("\n[dim]Press Enter to return to main menu[/dim]", default="")


# ── Main Menu ────────────────────────────────────────────────────────────────

MENU_ITEMS = [
    ("1", "🗺 ", "Find Nearby Facility",       "Locate certified e-waste drop-off centres near you"),
    ("2", "📚 ", "Learn About E-Waste",          "Health & environmental risks by device category"),
    ("3", "⚡ ", "Calculate Recycling Points",   "Discover your device's hidden metal value & earn credits"),
    ("4", "🏆 ", "My Rewards",                   "View points balance, tier, and redemption history"),
    ("5", "ℹ  ", "About",                         "About EcoRecycle Finder & India e-waste facts"),
    ("6", "🚪 ", "Exit",                           "Exit the application"),
]


def show_main_menu() -> None:
    """Render the styled main menu."""
    clear_screen()
    show_splash()

    menu_table = Table(
        box=box.ROUNDED,
        border_style="green",
        show_header=False,
        padding=(0, 2),
        expand=False,
        min_width=64,
    )
    menu_table.add_column("Num", style="bold bright_green", width=4, justify="center")
    menu_table.add_column("Icon", width=4)
    menu_table.add_column("Option", style="bold white", min_width=28)
    menu_table.add_column("Description", style="dim white", min_width=44)

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
            title="[bold green]♻  EcoRecycle Finder — Main Menu[/bold green]",
            subtitle="[dim italic]Type a number and press Enter[/dim italic]",
            border_style="green",
            padding=(1, 2),
        )
    )


def main_loop() -> None:
    """Run the interactive main menu loop."""
    show_splash()
    show_loading("Initialising EcoRecycle Finder", duration=1.0)

    while True:
        show_main_menu()

        choice = Prompt.ask(
            "\n[bold bright_green]Select an option[/bold bright_green] [dim](1–6)[/dim]",
            default="1"
        ).strip()

        if choice == "1":
            clear_screen()
            show_loading("Loading Facility Locator")
            facility_locator_menu()

        elif choice == "2":
            clear_screen()
            show_loading("Loading Education Library")
            education_menu()

        elif choice == "3":
            clear_screen()
            show_loading("Loading Points Calculator")
            points_calculator_menu()

        elif choice == "4":
            clear_screen()
            show_loading("Loading Rewards Dashboard")
            rewards_dashboard_menu()

        elif choice == "5":
            show_about()

        elif choice == "6":
            clear_screen()
            console.print(
                Panel(
                    Align.center(
                        Text(
                            "\n  🌿  Thank you for choosing to recycle responsibly!  🌿\n\n"
                            "  Every device you recycle today protects\n"
                            "  a child's future tomorrow.\n\n"
                            "  — The EcoRecycle India Team\n",
                            style="bold green",
                        )
                    ),
                    border_style="green",
                    padding=(1, 4),
                )
            )
            sys.exit(0)

        else:
            console.print("[red]Invalid option. Please enter a number between 1 and 6.[/red]")
            time.sleep(1.0)


# ── CLI argument parsing ─────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ecorecycle",
        description=(
            "EcoRecycle Finder — A CLI tool for responsible e-waste recycling.\n"
            "Locate facilities, learn about e-waste hazards, and earn credit points."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python main.py              # Launch interactive menu\n"
            "  python main.py --locate     # Jump straight to facility locator\n"
            "  python main.py --learn      # Jump straight to education module\n"
            "  python main.py --points     # Jump straight to points calculator\n"
            "  python main.py --rewards    # Jump straight to rewards dashboard\n"
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
        "--version", action="version", version="EcoRecycle Finder v1.0.0"
    )
    return parser.parse_args()


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = parse_args()

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
    else:
        main_loop()
