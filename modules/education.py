"""
EcoRecycle Finder — Educational Module
Provides e-waste education panels by device category.
"""

import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, IntPrompt
from rich import box
from rich.columns import Columns

console = Console()

DATA_PATH = Path(__file__).parent.parent / "data" / "education.json"


def load_education_data() -> list[dict]:
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def show_category_menu(categories: list[dict]) -> None:
    """Display available education categories in a styled table."""
    table = Table(
        title="[bold green]📚 E-Waste Education Library[/bold green]",
        box=box.ROUNDED,
        border_style="green",
        header_style="bold bright_green on dark_green",
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("#", style="dim cyan", width=3, justify="center")
    table.add_column("Category", style="bold white", min_width=20)
    table.add_column("Icon", width=5, justify="center")

    for idx, cat in enumerate(categories, start=1):
        table.add_row(str(idx), cat["category"], cat["icon"])

    console.print(table)


def display_category_panel(category: dict) -> None:
    """Show detailed educational info for a single device category."""
    icon = category["icon"]
    name = category["category"]

    # Harmful Components
    harm_lines = "\n".join(
        f"  [red]⚠[/red]  {c}" for c in category["harmful_components"]
    )

    # Health Effects
    health_lines = "\n".join(
        f"  [yellow]💔[/yellow]  {h}" for h in category["health_effects"]
    )

    # Environmental Stats
    env_lines = "\n".join(
        f"  [green]🌍[/green]  {e}" for e in category["environmental_stats"]
    )

    content = (
        f"[bold red]☣  Harmful Components[/bold red]\n"
        f"{harm_lines}\n\n"
        f"[bold yellow]🏥  Health Effects of Improper Disposal[/bold yellow]\n"
        f"{health_lines}\n\n"
        f"[bold green]🌿  Environmental Impact[/bold green]\n"
        f"{env_lines}"
    )

    console.print(
        Panel(
            content,
            title=f"[bold bright_white]{icon}  {name} — E-Waste Hazard Profile[/bold bright_white]",
            subtitle="[dim italic]Source: E-Waste Alliance / WHO / UNEP Data[/dim italic]",
            border_style="green",
            padding=(1, 2),
        )
    )

    # Call-to-action footer
    console.print(
        Panel(
            "[bold green]♻  Never throw this device in a regular dustbin![/bold green]\n"
            "[dim]Use the [bold]Facility Locator[/bold] to find a certified drop-off point near you.[/dim]",
            border_style="dim green",
            padding=(0, 2),
        )
    )


def education_menu() -> None:
    """Main education module flow."""
    console.print(
        Panel(
            "[bold green]Understand the dangers hidden inside your old electronics.[/bold green]\n"
            "[dim]Select a device category to learn about harmful materials & disposal impact.[/dim]",
            title="[bold]📖 Learn About E-Waste[/bold]",
            border_style="green",
            padding=(1, 2),
        )
    )

    categories = load_education_data()
    show_category_menu(categories)

    while True:
        choice = Prompt.ask(
            f"\n[bold cyan]Select a category[/bold cyan] [dim](1–{len(categories)})[/dim] or [bold]0[/bold] to go back",
            default="0"
        ).strip()

        if choice == "0":
            break

        try:
            idx = int(choice)
            if 1 <= idx <= len(categories):
                console.print()
                display_category_panel(categories[idx - 1])
                Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")

                # Ask if user wants to view another
                again = Prompt.ask(
                    "[bold cyan]View another category?[/bold cyan] [dim](y/n)[/dim]",
                    default="n"
                ).strip().lower()

                if again == "y":
                    console.clear()
                    show_category_menu(categories)
                    continue
                else:
                    break
            else:
                console.print(f"[red]Please enter a number between 1 and {len(categories)}.[/red]")
        except ValueError:
            console.print("[red]Invalid input. Please enter a number.[/red]")
