"""
EcoRecycle Finder — Facility Locator Module
Handles searching, filtering, and displaying certified e-waste collection centres.
Features real-time Haversine distance, live operating status, and navigation routing.
"""

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich import box
from rich.columns import Columns
from rich.align import Align

console = Console()

DATA_PATH = Path(__file__).parent.parent / "data" / "facilities.json"

# Reference coordinates for major Indian tech hubs & metros
CITY_CENTERS = {
    "noida": {"name": "Noida", "lat": 28.5700, "lon": 77.3200, "state": "UP"},
    "delhi": {"name": "New Delhi", "lat": 28.6139, "lon": 77.2090, "state": "Delhi"},
    "gurugram": {"name": "Gurugram", "lat": 28.4595, "lon": 77.0266, "state": "Haryana"},
    "bengaluru": {"name": "Bengaluru", "lat": 12.9716, "lon": 77.5946, "state": "Karnataka"},
    "bangalore": {"name": "Bengaluru", "lat": 12.9716, "lon": 77.5946, "state": "Karnataka"},
    "mumbai": {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777, "state": "Maharashtra"},
    "pune": {"name": "Pune", "lat": 18.5204, "lon": 73.8567, "state": "Maharashtra"},
    "hyderabad": {"name": "Hyderabad", "lat": 17.3850, "lon": 78.4867, "state": "Telangana"},
    "chennai": {"name": "Chennai", "lat": 13.0827, "lon": 80.2707, "state": "Tamil Nadu"},
    "kolkata": {"name": "Kolkata", "lat": 22.5726, "lon": 88.3639, "state": "West Bengal"},
}


def load_facilities() -> list[dict]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two geographic points in km."""
    r_earth_km = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(r_earth_km * c, 1)


def check_facility_status(facility: dict) -> tuple[bool, str]:
    """Check live operating status against current local time."""
    now = datetime.now()
    day_abbr = now.strftime("%a")
    current_time_dec = now.hour + (now.minute / 60.0)

    allowed_days = facility.get("days", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])
    open_hour = facility.get("open_hour", 9.0)
    close_hour = facility.get("close_hour", 18.0)

    if day_abbr not in allowed_days:
        return False, "[dim red]○ Closed Today[/dim red]"

    if open_hour <= current_time_dec < close_hour:
        return True, "[bold green]● Open Now[/bold green]"
    elif current_time_dec < open_hour:
        return False, f"[yellow]○ Opens {facility.get('hours', '').split('–')[0].strip()}[/yellow]"
    else:
        return False, "[dim red]○ Closed for Day[/dim red]"


def build_facility_table(facilities: list[dict], title: str, user_city: str) -> Table:
    """Build a styled, responsive table displaying matching facilities."""
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
    table.add_column("Facility & Location", style="bold white", min_width=24)
    table.add_column("Distance", style="bold yellow", width=10, justify="center")
    table.add_column("Live Status", width=16, justify="center")
    table.add_column("Accepted Categories", style="green", min_width=24)
    table.add_column("CPCB Verified", width=13, justify="center")

    for idx, fac in enumerate(facilities, start=1):
        _, status_badge = check_facility_status(fac)
        cert_badge = "[bold green]✔ Certified[/bold green]" if fac.get("certified") else "[dim yellow]⚠ Kiosk[/dim yellow]"
        accepted = ", ".join(item.capitalize() for item in fac.get("accepted_items", [])[:4])
        if len(fac.get("accepted_items", [])) > 4:
            accepted += f" [dim](+{len(fac['accepted_items']) - 4} more)[/dim]"

        name_location = f"[bold bright_white]{fac['name']}[/bold bright_white]\n[dim]{fac['city']}, {fac['pincode']}[/dim]"
        dist_str = f"[bold yellow]{fac.get('calculated_dist', fac.get('distance_km', 0))} km[/bold yellow]"

        table.add_row(
            str(idx),
            name_location,
            dist_str,
            status_badge,
            accepted,
            cert_badge,
        )
    return table


def show_facility_detail(facility: dict, user_coords: Optional[tuple[float, float]] = None) -> None:
    """Display a comprehensive card view of the chosen facility."""
    is_open, status_str = check_facility_status(facility)
    cert_text = (
        f"[bold green]✔ Central Pollution Control Board (CPCB) Authorized[/bold green]\n"
        f"  [dim]Registration: {facility.get('cpcb_reg', 'CPCB/EW/VERIFIED')}[/dim]"
        if facility.get("certified")
        else "[dim yellow]⚠ Municipal Partner Collection Kiosk (Uncertified Secondary)[/dim yellow]"
    )

    accepted_items_list = facility.get("accepted_items", [])
    accepted_str = "\n".join(f"    [green]•[/green] {item.capitalize()}" for item in accepted_items_list)

    maps_url = f"https://www.google.com/maps/dir/?api=1&destination={facility['lat']},{facility['lon']}"
    calc_dist = facility.get("calculated_dist", facility.get("distance_km", 0))

    panel_body = (
        f"[bold bright_white]🏢 {facility['name']}[/bold bright_white]\n"
        f"  [dim white]{facility['address']}[/dim white]\n\n"
        f"  [bold]Current Status:[/bold]  {status_str}\n"
        f"  [bold]Operating Hours:[/bold] [cyan]{facility['hours']}[/cyan]\n"
        f"  [bold]Authority Status:[/bold] {cert_text}\n\n"
        f"  [bold cyan]🧭 Navigation & Distance:[/bold cyan]\n"
        f"    • Distance from your location: [bold yellow]{calc_dist} km[/bold yellow]\n"
        f"    • Landmark: [dim]{facility.get('landmark', 'City Centre')}[/dim]\n"
        f"    • Coordinates: [dim]{facility['lat']:.4f}° N, {facility['lon']:.4f}° E[/dim]\n"
        f"    • [bold bright_blue]Google Maps Directions Link:[/bold bright_blue]\n"
        f"      [underline blue]{maps_url}[/underline blue]\n\n"
        f"  [bold green]📞 Direct Contacts:[/bold green]\n"
        f"    • Phone: [bold bright_cyan]{facility.get('phone', 'N/A')}[/bold bright_cyan]\n"
        f"    • Email: [cyan]{facility.get('email', 'N/A')}[/cyan]\n\n"
        f"  [bold]♻  Accepted Items for Safe Disposal:[/bold]\n"
        f"{accepted_str}"
    )

    console.print(
        Panel(
            panel_body,
            title=f"[bold green]📋 Certified Facility Dossier — {facility['city']}[/bold green]",
            border_style="green",
            padding=(1, 2),
            expand=False,
        )
    )


def facility_locator_menu() -> None:
    """Main interactive facility locator flow with dynamic multi-city routing."""
    console.print(
        Panel(
            "[bold green]Find Certified E-Waste Collection & Recycling Centers[/bold green]\n"
            "[dim]Pan-India CPCB-authorized network • Live open/closed tracking • Haversine distance[/dim]",
            title="[bold green]🗺  Facility Locator & Directions[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
    )

    facilities = load_facilities()

    # City quick selection prompt
    console.print("[dim]Supported Metros: Noida, Delhi, Gurugram, Bengaluru, Mumbai, Pune, Hyderabad, Chennai, Kolkata[/dim]")
    user_query = Prompt.ask(
        "\n[bold cyan]Enter your city or pincode[/bold cyan]",
        default="Noida",
    ).strip().lower()

    # Determine user's base coordinates
    user_coords = None
    resolved_city = user_query.title()
    for key, cinfo in CITY_CENTERS.items():
        if key in user_query:
            user_coords = (cinfo["lat"], cinfo["lon"])
            resolved_city = cinfo["name"]
            break

    # If not recognized as a major metro, default coordinates from the closest matching facility
    matched_facilities = [
        f for f in facilities
        if user_query in f["city"].lower() or user_query in f["pincode"]
    ]

    # If no direct city match, look for pincode or partial match across all facilities
    if not matched_facilities:
        matched_facilities = [
            f for f in facilities
            if user_query in f["address"].lower()
        ]

    if not matched_facilities:
        console.print(
            Panel(
                f"[red]No collection facilities directly listed for '[bold]{user_query}[/bold]'.\n\n"
                f"[white]Try searching for nearby major hubs:[/white]\n"
                f"  • [bold green]Noida[/bold green] (201301)       • [bold green]Delhi[/bold green] (110020)\n"
                f"  • [bold green]Bengaluru[/bold green] (560100)   • [bold green]Mumbai[/bold green] (400093)\n"
                f"  • [bold green]Hyderabad[/bold green] (500081)   • [bold green]Pune[/bold green] (411057)[/red]",
                border_style="red",
                title="[bold red]Location Not Found[/bold red]",
                padding=(1, 2),
            )
        )
        Prompt.ask("\n[dim]Press Enter to return to main menu[/dim]", default="")
        return

    # Calculate real Haversine distance for each facility
    if user_coords is None:
        user_coords = (matched_facilities[0]["lat"], matched_facilities[0]["lon"])

    for fac in matched_facilities:
        fac["calculated_dist"] = haversine_distance(
            user_coords[0], user_coords[1], fac["lat"], fac["lon"]
        )

    # Sort strictly by distance
    matched_facilities.sort(key=lambda x: x["calculated_dist"])

    # Optional filter by device type
    device_filter = Prompt.ask(
        "[bold cyan]Filter by item type[/bold cyan] (e.g. laptop, battery, smartphone, tv) [dim]or Enter to skip[/dim]",
        default="",
    ).strip().lower()

    active_results = matched_facilities
    if device_filter:
        filtered = [
            f for f in matched_facilities
            if any(device_filter in item.lower() for item in f.get("accepted_items", []))
        ]
        if filtered:
            active_results = filtered
            console.print(f"\n[green]✔ Showing {len(filtered)} facilit{'y' if len(filtered)==1 else 'ies'} accepting '[bold]{device_filter}[/bold]'[/green]")
        else:
            console.print(f"\n[yellow]No facilities found specifically for '{device_filter}'. Displaying all nearby centres.[/yellow]")

    console.print()
    console.print(build_facility_table(active_results, f"Centres Near {resolved_city}", resolved_city))

    console.print(
        f"\n[dim]Found [bold green]{len(active_results)}[/bold green] verified collection point(s).[/dim]"
    )

    while True:
        choice = Prompt.ask(
            "\n[bold cyan]Select facility number for directions & contacts[/bold cyan] [dim](or 0 to exit)[/dim]",
            default="0",
        ).strip()

        if choice == "0":
            break

        try:
            idx = int(choice)
            if 1 <= idx <= len(active_results):
                console.print()
                show_facility_detail(active_results[idx - 1], user_coords)
                Prompt.ask("\n[dim]Press Enter to continue browsing facilities[/dim]", default="")
                break
            else:
                console.print(f"[red]Please enter a number between 1 and {len(active_results)}.[/red]")
        except ValueError:
            console.print("[red]Invalid input. Please enter a valid number.[/red]")
