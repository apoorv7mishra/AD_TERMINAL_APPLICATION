"""
EcoRecycle Finder — Credit Points Calculator Module
Fuzzy device search + recoverable metals estimation + redemption code generation.
"""

import json
import random
import string
import math
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, IntPrompt
from rich import box

console = Console()

DEVICES_PATH = Path(__file__).parent.parent / "data" / "devices.json"
ACCOUNT_PATH = Path(__file__).parent.parent / "data" / "user_account.json"

# Approximate metal prices (INR per gram)
METAL_PRICES_INR = {
    "gold_mg": 6.0,       # ₹6 per mg ≈ ₹6000/g (gold ~₹6000/g)
    "silver_mg": 0.07,    # ₹0.07 per mg ≈ ₹70/g
    "copper_mg": 0.00085, # ₹0.00085 per mg ≈ ₹0.85/g
    "palladium_mg": 3.0,  # ₹3 per mg ≈ ₹3000/g
    "platinum_mg": 2.7,   # ₹2.7 per mg ≈ ₹2700/g
}

POINTS_PER_RUPEE = 5  # 5 credit points per ₹1 of estimated metal value


def load_devices() -> list[dict]:
    with open(DEVICES_PATH, "r") as f:
        return json.load(f)


def load_account() -> dict:
    with open(ACCOUNT_PATH, "r") as f:
        return json.load(f)


def save_account(account: dict) -> None:
    with open(ACCOUNT_PATH, "w") as f:
        json.dump(account, f, indent=2)


def generate_redemption_code(length: int = 12) -> str:
    chars = string.ascii_uppercase + string.digits
    prefix = "ECO"
    suffix = "".join(random.choices(chars, k=length))
    return f"{prefix}-{suffix[:4]}-{suffix[4:8]}-{suffix[8:]}"


def fuzzy_match_device(query: str, devices: list[dict]) -> list[dict]:
    """Simple fuzzy matching — check if query tokens appear in device name/aliases."""
    query_lower = query.lower().strip()
    tokens = query_lower.split()

    scored = []
    for device in devices:
        # Build searchable text
        search_text = (
            device["name"].lower()
            + " "
            + " ".join(a.lower() for a in device["aliases"])
            + " "
            + device["category"].lower()
        )
        # Count how many query tokens appear
        score = sum(1 for tok in tokens if tok in search_text)
        # Bonus: exact substring match
        if query_lower in search_text:
            score += 3

        if score > 0:
            scored.append((score, device))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:5]]  # top 5 matches


def calculate_metal_value(device: dict, quantity: int) -> tuple[dict, float, int]:
    """
    Calculate recoverable metals and estimated value.
    Returns: (metals_dict, total_inr_value, earned_points)
    """
    weight_kg = (device["weight_g"] * quantity) / 1000.0
    metals_per_kg = device["metals_per_kg"]

    recovered = {}
    total_value_inr = 0.0

    for metal_key, mg_per_kg in metals_per_kg.items():
        total_mg = mg_per_kg * weight_kg
        recovered[metal_key] = round(total_mg, 2)
        price_per_mg = METAL_PRICES_INR.get(metal_key, 0)
        total_value_inr += total_mg * price_per_mg

    earned_points = device["base_points"] * quantity + int(total_value_inr * POINTS_PER_RUPEE / 10)

    return recovered, round(total_value_inr, 2), earned_points


def show_metals_table(device: dict, recovered: dict, quantity: int) -> None:
    """Show a breakdown table of recovered precious metals."""
    metal_names = {
        "gold_mg": ("Gold (Au)", "🥇"),
        "silver_mg": ("Silver (Ag)", "🥈"),
        "copper_mg": ("Copper (Cu)", "🟠"),
        "palladium_mg": ("Palladium (Pd)", "⚪"),
        "platinum_mg": ("Platinum (Pt)", "🔘"),
    }

    table = Table(
        title=f"[bold green]⚗  Recoverable Precious Metals — {device['name']} × {quantity}[/bold green]",
        box=box.ROUNDED,
        border_style="green",
        header_style="bold bright_green on dark_green",
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("Metal", style="bold white", min_width=18)
    table.add_column("Per kg (mg)", style="cyan", justify="right", min_width=14)
    table.add_column("Total Recovered (mg)", style="bold yellow", justify="right", min_width=20)
    table.add_column("Est. Value (₹)", style="bold green", justify="right", min_width=15)

    for metal_key, amount_mg in recovered.items():
        name, icon = metal_names.get(metal_key, (metal_key, ""))
        per_kg = device["metals_per_kg"][metal_key]
        value = round(amount_mg * METAL_PRICES_INR.get(metal_key, 0), 2)
        if amount_mg > 0:
            table.add_row(
                f"{icon}  {name}",
                f"{per_kg:,.1f}",
                f"{amount_mg:,.2f}",
                f"₹{value:,.2f}",
            )

    console.print(table)


def points_calculator_menu() -> None:
    """Main credit points calculator flow."""
    console.print(
        Panel(
            "[bold green]Search for your old device and discover its hidden value.[/bold green]\n"
            "[dim]We estimate recoverable precious metals and award you credit points for recycling responsibly.[/dim]",
            title="[bold]⚡ Recycling Points Calculator[/bold]",
            border_style="green",
            padding=(1, 2),
        )
    )

    devices = load_devices()
    account = load_account()

    while True:
        query = Prompt.ask(
            "\n[bold cyan]Search for your device[/bold cyan] (e.g. 'smartphone', 'old laptop', 'battery')"
        ).strip()

        if not query:
            console.print("[yellow]Please enter a device name to search.[/yellow]")
            continue

        matches = fuzzy_match_device(query, devices)

        if not matches:
            console.print(
                f"[red]No devices found for '[bold]{query}[/bold]'. Try: smartphone, laptop, battery, TV, fridge.[/red]"
            )
            retry = Prompt.ask("[bold cyan]Try another search?[/bold cyan] [dim](y/n)[/dim]", default="y").strip().lower()
            if retry != "y":
                break
            continue

        # Display matches
        console.print(f"\n[dim green]Found {len(matches)} match(es) for '[bold]{query}[/bold]':[/dim green]\n")
        match_table = Table(
            box=box.SIMPLE_HEAVY,
            border_style="dim green",
            header_style="bold green",
            padding=(0, 1),
        )
        match_table.add_column("#", style="dim cyan", width=3)
        match_table.add_column("Device Name", style="bold white", min_width=22)
        match_table.add_column("Category", style="cyan", min_width=12)
        match_table.add_column("Avg. Weight", style="yellow", justify="right", min_width=12)
        match_table.add_column("Base Points", style="green", justify="right", min_width=12)

        for idx, device in enumerate(matches, start=1):
            match_table.add_row(
                str(idx),
                device["name"],
                device["category"].title(),
                f"{device['weight_g']:,} g",
                f"{device['base_points']} pts",
            )

        console.print(match_table)

        choice = Prompt.ask(
            f"\n[bold cyan]Select device[/bold cyan] [dim](1–{len(matches)})[/dim] or [bold]0[/bold] to search again",
            default="0"
        ).strip()

        if choice == "0":
            continue

        try:
            idx = int(choice)
            if not (1 <= idx <= len(matches)):
                console.print(f"[red]Please enter a number between 1 and {len(matches)}.[/red]")
                continue
        except ValueError:
            console.print("[red]Invalid input.[/red]")
            continue

        selected_device = matches[idx - 1]

        # Get quantity
        while True:
            qty_str = Prompt.ask(
                f"[bold cyan]How many [bright_white]{selected_device['name']}[/bright_white]s are you recycling?[/bold cyan]",
                default="1"
            ).strip()
            try:
                quantity = int(qty_str)
                if quantity < 1:
                    console.print("[red]Please enter at least 1.[/red]")
                else:
                    break
            except ValueError:
                console.print("[red]Please enter a valid number.[/red]")

        # Calculate
        recovered, total_value_inr, earned_points = calculate_metal_value(selected_device, quantity)

        console.print()
        show_metals_table(selected_device, recovered, quantity)

        # Summary panel
        summary = (
            f"[bold white]Device:[/bold white] {selected_device['icon'] if 'icon' in selected_device else '♻'} "
            f"[bold bright_green]{selected_device['name']}[/bold bright_green] × {quantity}\n"
            f"[bold white]Est. Metal Value:[/bold white] [bold yellow]₹{total_value_inr:,.2f}[/bold yellow]\n"
            f"[bold white]Credit Points Earned:[/bold white] [bold bright_green]+{earned_points} points[/bold bright_green]\n"
        )

        # Generate redemption code
        code = generate_redemption_code()

        code_panel = (
            f"[bold white]🎟  Your Redemption Code:[/bold white]\n\n"
            f"[bold bright_green on dark_green]  {code}  [/bold bright_green on dark_green]\n\n"
            f"[dim]Show this code at any partnered EcoRecycle facility to claim your points.\n"
            f"Valid for 30 days from today.[/dim]"
        )

        console.print(
            Panel(
                summary,
                title="[bold green]✅ Recycling Estimate[/bold green]",
                border_style="green",
                padding=(1, 2),
            )
        )

        console.print(
            Panel(
                code_panel,
                title="[bold bright_yellow]🏷  Redemption Voucher[/bold bright_yellow]",
                border_style="bright_yellow",
                padding=(1, 3),
                expand=False,
            )
        )

        # Save to account
        confirm = Prompt.ask(
            "\n[bold cyan]Add these points to your account?[/bold cyan] [dim](y/n)[/dim]",
            default="y"
        ).strip().lower()

        if confirm == "y":
            account["total_points"] += earned_points
            account["total_devices_recycled"] += quantity
            account["devices_submitted"].append({
                "device": selected_device["name"],
                "quantity": quantity,
                "points_earned": earned_points,
                "value_inr": total_value_inr,
                "code": code,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
            save_account(account)
            console.print(
                Panel(
                    f"[bold green]✔ {earned_points} points added to your account![/bold green]\n"
                    f"[dim]Total balance: [bold bright_green]{account['total_points']} points[/bold bright_green][/dim]",
                    border_style="green",
                    padding=(0, 2),
                )
            )

        Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")

        another = Prompt.ask(
            "[bold cyan]Calculate for another device?[/bold cyan] [dim](y/n)[/dim]",
            default="n"
        ).strip().lower()

        if another != "y":
            break
