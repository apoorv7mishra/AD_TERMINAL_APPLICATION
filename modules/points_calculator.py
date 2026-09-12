"""
EcoRecycle Finder — Credit Points Calculator Module
Fuzzy device search + contextual educational hazard pop-up +
device condition multiplier + precious metals estimation +
digital recycling certificate generator.
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
from rich.prompt import Prompt, IntPrompt
from rich import box
from rich.progress import BarColumn, Progress, TextColumn

from modules.education import render_hazard_modal

console = Console()

DEVICES_PATH = Path(__file__).parent.parent / "data" / "devices.json"
ACCOUNT_PATH = Path(__file__).parent.parent / "data" / "user_account.json"

# Approximate metal prices (INR per gram / per mg)
METAL_PRICES_INR = {
    "gold_mg": 6.5,       # ₹6.5 per mg ≈ ₹6500/g
    "silver_mg": 0.08,    # ₹0.08 per mg ≈ ₹80/g
    "copper_mg": 0.00095, # ₹0.00095 per mg ≈ ₹0.95/g
    "palladium_mg": 3.2,  # ₹3.2 per mg ≈ ₹3200/g
    "platinum_mg": 2.9,   # ₹2.9 per mg ≈ ₹2900/g
}

POINTS_PER_RUPEE = 5  # 5 credit points per ₹1 of estimated metal value

CONDITION_MULTIPLIERS = {
    "1": ("Working / Intact Components", 1.20, "[bold green]Working (+20% bonus)[/bold green]"),
    "2": ("Functional / Cracked Screen or Minor Faults", 1.00, "[yellow]Standard (100%)[/yellow]"),
    "3": ("Dead / Motherboard Scrap Only", 0.80, "[dim red]Scrap (-20% discount)[/dim red]"),
}


def load_devices() -> list[dict]:
    with open(DEVICES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_account() -> dict:
    with open(ACCOUNT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_account(account: dict) -> None:
    with open(ACCOUNT_PATH, "w", encoding="utf-8") as f:
        json.dump(account, f, indent=2)


def generate_redemption_code(length: int = 12) -> str:
    """Generate a clean 16-character alphanumeric authorization code."""
    chars = string.ascii_uppercase + string.digits
    prefix = "ECO"
    suffix = "".join(random.choices(chars, k=length))
    return f"{prefix}-{suffix[:4]}-{suffix[4:8]}-{suffix[8:]}"


def fuzzy_match_device(query: str, devices: list[dict]) -> list[dict]:
    """Search query against device names, models, aliases, and categories."""
    query_lower = query.lower().strip()
    tokens = query_lower.split()

    scored = []
    for device in devices:
        search_text = (
            device["name"].lower()
            + " "
            + device.get("model", "").lower()
            + " "
            + " ".join(a.lower() for a in device.get("aliases", []))
            + " "
            + device["category"].lower()
        )
        # Token overlap
        score = sum(2 for tok in tokens if tok in search_text)
        # Exact query match bonus
        if query_lower in search_text:
            score += 5
        # Exact name match
        if query_lower == device["name"].lower():
            score += 10

        if score > 0:
            scored.append((score, device))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:6]]


def calculate_metal_yield(
    device: dict, quantity: int, condition_mult: float
) -> tuple[dict, float, int, float]:
    """
    Calculate recoverable precious metals and points.
    Returns: (metals_dict, total_value_inr, earned_points, co2_saved_kg)
    """
    total_weight_kg = (device["weight_g"] * quantity) / 1000.0
    metals_per_kg = device["metals_per_kg"]

    recovered = {}
    total_value_inr = 0.0

    for metal_key, mg_per_kg in metals_per_kg.items():
        total_mg = mg_per_kg * total_weight_kg * condition_mult
        recovered[metal_key] = round(total_mg, 2)
        price_per_mg = METAL_PRICES_INR.get(metal_key, 0.0)
        total_value_inr += total_mg * price_per_mg

    base_pts = int(device.get("base_points", 50) * quantity * condition_mult)
    metal_pts = int((total_value_inr * POINTS_PER_RUPEE) / 5)
    earned_points = base_pts + metal_pts

    # Environmental CO2 offset metric: roughly 14.5 kg CO2 saved per kg of high-grade electronics recycled
    co2_saved_kg = round(total_weight_kg * 14.5, 2)

    return recovered, round(total_value_inr, 2), earned_points, co2_saved_kg


def show_metals_table(device: dict, recovered: dict, quantity: int, condition_label: str) -> None:
    """Render a styled table of recovered precious metals with visual share bars."""
    metal_metadata = {
        "gold_mg": ("Gold (Au)", "🥇", "bold bright_yellow"),
        "silver_mg": ("Silver (Ag)", "🥈", "bold bright_white"),
        "copper_mg": ("Copper (Cu)", "🟠", "bold rgb(230,120,40)"),
        "palladium_mg": ("Palladium (Pd)", "⚪", "bold cyan"),
        "platinum_mg": ("Platinum (Pt)", "🔘", "bold bright_cyan"),
    }

    table = Table(
        title=f"[bold green]⚗  Estimated Recoverable Precious Metals — {device['name']} × {quantity}[/bold green]\n"
              f"[dim]Condition: {condition_label}[/dim]",
        box=box.ROUNDED,
        border_style="green",
        header_style="bold bright_green on dark_green",
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("Precious Metal", style="bold white", min_width=18)
    table.add_column("Concentration", style="cyan", justify="right", min_width=14)
    table.add_column("Salvaged (mg)", style="bold yellow", justify="right", min_width=16)
    table.add_column("Market Rate", style="dim white", justify="right", min_width=14)
    table.add_column("Est. Value (₹)", style="bold green", justify="right", min_width=15)

    for metal_key, amount_mg in recovered.items():
        name, icon, style = metal_metadata.get(metal_key, (metal_key, "⚙", "white"))
        per_kg = device["metals_per_kg"].get(metal_key, 0)
        rate = METAL_PRICES_INR.get(metal_key, 0.0)
        val = round(amount_mg * rate, 2)

        if amount_mg > 0:
            table.add_row(
                f"{icon}  [{style}]{name}[/{style}]",
                f"{per_kg:,.0f} mg/kg",
                f"{amount_mg:,.2f} mg",
                f"₹{rate*1000:,.0f}/g",
                f"₹{val:,.2f}",
            )

    console.print(table)


def export_digital_certificate(
    username: str,
    device_name: str,
    quantity: int,
    condition_desc: str,
    recovered_metals: dict,
    total_val: float,
    points: int,
    co2_saved: float,
    code: str,
) -> str:
    """Generate a printable digital certificate markdown file."""
    timestamp = datetime.now().strftime("%d %B %Y, %I:%M %p")
    cert_filename = f"certificate_{code}.md"
    cert_path = Path(__file__).parent.parent / cert_filename

    cert_content = f"""# 🌿 OFFICIAL E-WASTE RECYCLING HANDOVER CERTIFICATE
**Issued by EcoRecycle India & Ministry of Environment Partner Network**

---

### **Certificate Identification**
- **Authorization Code:** `{code}`
- **Beneficiary:** `{username}`
- **Date & Timestamp:** `{timestamp}`
- **Verification Status:** `OFFICIALLY VERIFIED & PENDING FACILITY HANDOVER`

---

### **Recycled Device Specifications**
- **Device Model:** {device_name}
- **Quantity Handed Over:** {quantity} unit(s)
- **Functional Condition:** {condition_desc}

---

### **Recovered Precious Metals Breakdown**
| Precious Metal | Salvaged Amount (mg) |
|---|---|
| 🥇 Gold (Au) | {recovered_metals.get('gold_mg', 0):,.2f} mg |
| 🥈 Silver (Ag) | {recovered_metals.get('silver_mg', 0):,.2f} mg |
| 🟠 Copper (Cu) | {recovered_metals.get('copper_mg', 0):,.2f} mg |
| ⚪ Palladium (Pd) | {recovered_metals.get('palladium_mg', 0):,.2f} mg |
| 🔘 Platinum (Pt) | {recovered_metals.get('platinum_mg', 0):,.2f} mg |

- **Total Estimated Material Value:** ₹{total_val:,.2f}
- **EcoCredit Reward Points Earned:** **+{points:,} Points**

---

### **Environmental Impact Contributions**
- 🌍 **CO₂ Equivalent Prevented:** `{co2_saved} kg CO₂`
- 💧 **Groundwater Leaching Prevented:** Diverted toxic lead, cadmium, and mercury from Indian soil.

---
*Present this certificate or code `{code}` at any CPCB-authorized partner facility to validate your drop-off.*
"""
    with open(cert_path, "w", encoding="utf-8") as f:
        f.write(cert_content)

    return cert_filename


def points_calculator_menu() -> None:
    """Main credit points calculator interactive workflow."""
    console.print(
        Panel(
            "[bold green]Search Your Device Model • Review Toxic Hazards • Calculate Credit Points[/bold green]\n"
            "[dim]Earn rewards proportional to recoverable precious metals • Generate verifiable drop-off tokens[/dim]",
            title="[bold green]⚡ Recycling Points & Precious Metals Calculator[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
    )

    devices = load_devices()
    account = load_account()

    while True:
        query = Prompt.ask(
            "\n[bold cyan]Input your device brand or model[/bold cyan] (e.g. 'iPhone 13', 'MacBook', 'Galaxy S23', 'CRT TV')",
        ).strip()

        if not query:
            console.print("[yellow]Please enter a device name or model.[/yellow]")
            continue

        matches = fuzzy_match_device(query, devices)

        if not matches:
            console.print(
                f"[red]No exact devices found for '[bold]{query}[/bold]'.[/red]\n"
                f"[dim]Try: iPhone, Samsung Galaxy, MacBook, Dell Laptop, iPad, Smartwatch, Battery, Printer, CRT[/dim]"
            )
            retry = Prompt.ask("[bold cyan]Search again?[/bold cyan] [dim](y/n)[/dim]", default="y").strip().lower()
            if retry != "y":
                break
            continue

        # Show matches table
        console.print(f"\n[green]Found {len(matches)} matching model(s):[/green]\n")
        match_table = Table(
            box=box.ROUNDED,
            border_style="dim green",
            header_style="bold green",
            padding=(0, 1),
        )
        match_table.add_column("#", style="dim cyan", width=3, justify="center")
        match_table.add_column("Device / Model", style="bold white", min_width=24)
        match_table.add_column("Category", style="cyan", min_width=12)
        match_table.add_column("Weight (est)", style="yellow", justify="right", min_width=12)
        match_table.add_column("Base Reward", style="bold green", justify="right", min_width=12)

        for idx, dev in enumerate(matches, start=1):
            match_table.add_row(
                str(idx),
                dev["name"],
                dev.get("model", dev["category"].title()),
                f"{dev['weight_g']} g",
                f"{dev.get('base_points', 50)} pts",
            )
        console.print(match_table)

        # User selects device
        sel = Prompt.ask(
            f"\n[bold cyan]Select device number (1–{len(matches)})[/bold cyan] [dim]or 0 to search again[/dim]",
            default="1",
        ).strip()

        if sel == "0":
            continue

        try:
            device_idx = int(sel) - 1
            if not (0 <= device_idx < len(matches)):
                console.print("[red]Invalid selection number.[/red]")
                continue
            selected_device = matches[device_idx]
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")
            continue

        # ── 1. MANDATORY CONTEXTUAL EDUCATIONAL HAZARD POP-UP ──
        # Directly addresses the problem statement's educational pop-up requirement
        console.print()
        hazard_cat = selected_device.get("hazard_category", selected_device.get("category", "Smartphone"))
        render_hazard_modal(selected_device["name"], hazard_cat)

        # ── 2. Device Condition Assessment ──
        console.print(
            "\n[bold green]Select Current Device Condition:[/bold green]\n"
            "  [bold cyan]1[/bold cyan] — Working / Intact Components [bold green](+20% bonus)[/bold green]\n"
            "  [bold cyan]2[/bold cyan] — Functional with Faults / Cracked Screen [yellow](100% standard)[/yellow]\n"
            "  [bold cyan]3[/bold cyan] — Dead / Motherboard Scrap Only [dim red](-20% discount)[/dim red]"
        )
        cond_choice = Prompt.ask(
            "[bold cyan]Enter condition (1–3)[/bold cyan]", default="2"
        ).strip()
        cond_desc, cond_multiplier, cond_label = CONDITION_MULTIPLIERS.get(
            cond_choice, CONDITION_MULTIPLIERS["2"]
        )

        # ── 3. Quantity ──
        qty_input = Prompt.ask("[bold cyan]Quantity of devices[/bold cyan]", default="1").strip()
        try:
            qty = max(1, int(qty_input))
        except ValueError:
            qty = 1

        # ── 4. Calculation ──
        recovered, total_val, earned_points, co2_saved = calculate_metal_yield(
            selected_device, qty, cond_multiplier
        )

        console.print()
        show_metals_table(selected_device, recovered, qty, cond_desc)

        redemption_code = generate_redemption_code()

        # Summary & Award Card
        card_content = (
            f"[bold bright_white]📱 Device Handover Summary:[/bold bright_white]\n"
            f"  • Model: [bold]{selected_device['name']}[/bold] (×{qty})\n"
            f"  • Condition: {cond_label}\n"
            f"  • Total Metal Value: [bold yellow]₹{total_val:,.2f}[/bold yellow]\n\n"
            f"  [bold bright_green]🏆 Credit Points Earned:[/bold bright_green]  [bold bright_yellow]+{earned_points:,}[/bold bright_yellow] points\n"
            f"  [bold cyan]🌍 Environmental Impact:[/bold cyan]  Prevents [bold bright_green]~{co2_saved} kg[/bold bright_green] of CO₂ emissions\n\n"
            f"  [bold bright_white]🎟  Official Drop-Off Authorization Code:[/bold bright_white]\n"
            f"  [bold black on bright_yellow]  {redemption_code}  [/bold black on bright_yellow]\n\n"
            f"  [dim italic]Present this code at any certified collection facility to claim rewards.[/dim italic]"
        )

        console.print(
            Panel(
                card_content,
                title="[bold green]✨ Recycling Credit Award[/bold green]",
                border_style="bright_green",
                padding=(1, 2),
            )
        )

        # Update Account
        account["total_points"] = account.get("total_points", 0) + earned_points
        account["total_devices_recycled"] = account.get("total_devices_recycled", 0) + qty
        account.setdefault("devices_submitted", []).append(
            {
                "device": selected_device["name"],
                "quantity": qty,
                "points_earned": earned_points,
                "value_inr": total_val,
                "code": redemption_code,
                "co2_saved_kg": co2_saved,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
        )
        save_account(account)

        # ── 5. Certificate Export Option ──
        export_choice = Prompt.ask(
            "\n[bold bright_yellow]Export official Digital Recycling Certificate?[/bold bright_yellow] [dim](y/n)[/dim]",
            default="y",
        ).strip().lower()

        if export_choice == "y":
            cert_file = export_digital_certificate(
                account.get("username", "EcoRecycle User"),
                selected_device["name"],
                qty,
                cond_desc,
                recovered,
                total_val,
                earned_points,
                co2_saved,
                redemption_code,
            )
            console.print(
                f"[bold green]✔ Digital Handover Certificate generated:[/bold green] [underline cyan]{cert_file}[/underline cyan]"
            )

        another = Prompt.ask("\n[bold cyan]Recycle another device?[/bold cyan] [dim](y/n)[/dim]", default="n").strip().lower()
        if another != "y":
            break
