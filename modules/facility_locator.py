"""
EcoRecycle Finder — Facility Locator Module
Handles searching, filtering, and displaying e-waste collection centers.
"""

import json
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, IntPrompt
from rich import box
from rich.columns import Columns
from rich.align import Align

console = Console()

DATA_PATH = Path(__file__).parent.parent / "data" / "facilities.json"


def load_facilities() -> list[dict]:
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def build_facility_table(facilities: list[dict], title: str = "Nearby E-Waste Collection Centres") -> Table:
    table = Table(
        title=f"[bold green]🗺  {title}[/bold green]",
        box=box.ROUNDED,
        border_style="green",
        header_style="bold bright_green on dark_green",
        show_lines=True,
        padding=(0, 1),
        expand=True,
    )
    table.add_column("#", style="dim cyan", width=3, justify="center")
    table.add_column("Facility Name", style="bold white", min_width=22)
    table.add_column("Address", style="dim white", min_width=28)
    table.add_column("Distance", style="bold yellow", width=10, justify="center")
    table.add_column("Accepted Items", style="green", min_width=28)
    table.add_column("Hours", style="cyan", min_width=22)
    table.add_column("Certified", width=9, justify="center")

    for idx, fac in enumerate(facilities, start=1):
        accepted = ", ".join(item.capitalize() for item in fac["accepted_items"])
        certified_badge = "[bold green]✔ Yes[/bold green]" if fac["certified"] else "[dim red]✘ No[/dim red]"
        dist_str = f"[bold yellow]{fac['distance_km']} km[/bold yellow]"
        table.add_row(
            str(idx),
            fac["name"],
            fac["address"],
            dist_str,
            accepted,
            fac["hours"],
            certified_badge,
        )
    return table


def show_facility_detail(facility: dict) -> None:
    """Display a rich detail panel for a selected facility."""
    cert = "[bold green]✔ CPCB Certified[/bold green]" if facility["certified"] else "[dim red]✘ Not CPCB Certified[/dim red]"

    accepted_items = "\n".join(f"  [green]•[/green] {item.capitalize()}" for item in facility["accepted_items"])

    directions_text = (
        f"[bold cyan]🧭 Directions:[/bold cyan]\n"
        f"  Head [bold yellow]{facility['direction']}[/bold yellow] from your current location.\n"
        f"  Distance: [bold yellow]{facility['distance_km']} km[/bold yellow]\n"
        f"  📍 Landmark: {facility['landmark']}"
    )

    detail = (
        f"[bold bright_white]📍 {facility['name']}[/bold bright_white]\n"
        f"[dim]{facility['address']}[/dim]\n\n"
        f"[bold]Certification:[/bold] {cert}\n\n"
        f"[bold]🕐 Hours:[/bold] [cyan]{facility['hours']}[/cyan]\n"
        f"[bold]📞 Phone:[/bold] [cyan]{facility['phone']}[/cyan]\n"
        f"[bold]📧 Email:[/bold] [cyan]{facility['email']}[/cyan]\n\n"
        f"[bold]♻  Accepted Items:[/bold]\n{accepted_items}\n\n"
        f"{directions_text}"
    )

    console.print(
        Panel(
            detail,
            title="[bold green]📋 Facility Details[/bold green]",
            border_style="green",
            padding=(1, 2),
            expand=False,
        )
    )


def facility_locator_menu() -> None:
    """Main facility locator flow."""
    console.print(
        Panel(
            "[bold green]Find a nearby e-waste collection facility[/bold green]\n"
            "[dim]Search by city/pincode and optionally filter by device type.[/dim]",
            title="[bold]🗺  Facility Locator[/bold]",
            border_style="green",
            padding=(1, 2),
        )
    )

    facilities = load_facilities()

    city_input = Prompt.ask(
        "\n[bold cyan]Enter your city or pincode[/bold cyan]",
        default="Noida"
    ).strip().lower()

    # Filter by city/pincode
    filtered = [
        f for f in facilities
        if city_input in f["city"].lower() or city_input in f["pincode"]
    ]

    if not filtered:
        console.print(
            Panel(
                f"[red]No facilities found for '[bold]{city_input}[/bold]'.\n"
                "Try 'Noida' or pincode '201301'.[/red]",
                border_style="red",
            )
        )
        Prompt.ask("\n[dim]Press Enter to return to main menu[/dim]", default="")
        return

    # Sort by distance
    filtered.sort(key=lambda x: x["distance_km"])

    # Optional device-type filter
    device_filter = Prompt.ask(
        "[bold cyan]Filter by device type[/bold cyan] (e.g. battery, laptop) — or press Enter to skip",
        default=""
    ).strip().lower()

    if device_filter:
        filtered_by_device = [
            f for f in filtered
            if any(device_filter in item.lower() for item in f["accepted_items"])
        ]
        if filtered_by_device:
            filtered = filtered_by_device
            console.print(f"\n[dim green]Showing facilities that accept '[bold]{device_filter}[/bold]'[/dim green]")
        else:
            console.print(f"\n[yellow]No facilities found accepting '[bold]{device_filter}[/bold]'. Showing all results.[/yellow]")

    console.print()
    console.print(build_facility_table(filtered))

    console.print(
        f"\n[dim]Found [bold green]{len(filtered)}[/bold green] facilit{'y' if len(filtered)==1 else 'ies'} near [bold]{city_input.title()}[/bold].[/dim]"
    )

    # Facility selection
    while True:
        choice = Prompt.ask(
            "\n[bold cyan]Enter facility number for details[/bold cyan] (or [bold]0[/bold] to go back)",
            default="0"
        ).strip()

        if choice == "0":
            break

        try:
            idx = int(choice)
            if 1 <= idx <= len(filtered):
                console.print()
                show_facility_detail(filtered[idx - 1])
                Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")
                break
            else:
                console.print(f"[red]Please enter a number between 1 and {len(filtered)}.[/red]")
        except ValueError:
            console.print("[red]Invalid input. Please enter a number.[/red]")
