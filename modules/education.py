"""
EcoRecycle Finder — Educational & Awareness Module
Provides e-waste hazard profiles, contextual pop-up alerts, and interactive eco-quizzes.
"""

import json
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt
from rich import box
from rich.columns import Columns
from rich.align import Align

console = Console()

DATA_PATH = Path(__file__).parent.parent / "data" / "education.json"
ACCOUNT_PATH = Path(__file__).parent.parent / "data" / "user_account.json"


def load_education_data() -> list[dict]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_hazard_profile(category_name: str) -> Optional[dict]:
    """Retrieve hazard profile dictionary by category name."""
    data = load_education_data()
    category_lower = category_name.lower().strip()
    for cat in data:
        if cat["category"].lower() in category_lower or category_lower in cat["category"].lower():
            return cat
    return data[0] if data else None


def render_hazard_modal(device_name: str, category_name: str) -> None:
    """
    Renders an in-flow educational alert pop-up panel.
    Directly satisfies the problem statement requirement:
    'Offers educational pop-ups on the harmful components of your e-waste
     and their effects on the environment and human health if not disposed correctly.'
    """
    profile = get_hazard_profile(category_name)
    if not profile:
        return

    harm_lines = "\n".join(f"  [bold red]☣[/bold red]  [white]{item}[/white]" for item in profile["harmful_components"][:5])
    health_lines = "\n".join(f"  [bold yellow]💔[/bold yellow] [dim white]{item}[/dim white]" for item in profile["health_effects"][:4])
    env_lines = "\n".join(f"  [bold cyan]🌍[/bold cyan] [dim white]{item}[/dim white]" for item in profile["environmental_stats"][:3])

    content = (
        f"[bold red]⚠  MANDATORY HAZARD & TOXICITY DISCLOSURE[/bold red]\n"
        f"[dim white]Device Model:[/dim white] [bold bright_white]{device_name}[/bold bright_white] "
        f"[dim](Classification: {profile['category']})[/dim]\n\n"
        f"[bold red]Dangerous Toxic Components Found Inside This Device:[/bold red]\n"
        f"{harm_lines}\n\n"
        f"[bold yellow]Direct Human Health Risks (If informally dismantled/burned):[/bold yellow]\n"
        f"{health_lines}\n\n"
        f"[bold cyan]Environmental & Groundwater Consequences:[/bold cyan]\n"
        f"{env_lines}\n\n"
        f"[bold bright_green]💡 Safe Recycling Fact:[/bold bright_green] "
        f"[italic green]Disposing via certified CPCB recyclers prevents these toxins from entering India's soil & food chain.[/italic green]"
    )

    console.print(
        Panel(
            content,
            title="[bold yellow]🚨 EDUCATIONAL HAZARD POP-UP[/bold yellow]",
            subtitle="[dim italic]Ministry of Environment Safe E-Waste Directive[/dim italic]",
            border_style="yellow",
            padding=(1, 2),
            expand=False,
        )
    )
    Prompt.ask("[dim]Press Enter to acknowledge hazard warning & proceed to rewards calculation[/dim]", default="")


def show_category_menu(categories: list[dict]) -> None:
    """Display available education categories in a styled table."""
    table = Table(
        title="[bold green]📚 E-Waste Education & Toxicology Library[/bold green]",
        box=box.ROUNDED,
        border_style="green",
        header_style="bold bright_green on dark_green",
        show_lines=True,
        padding=(0, 2),
    )
    table.add_column("#", style="dim cyan", width=4, justify="center")
    table.add_column("Icon", width=6, justify="center")
    table.add_column("Device Category", style="bold white", min_width=22)
    table.add_column("Primary Toxic Threats", style="dim red", min_width=32)

    for idx, cat in enumerate(categories, start=1):
        threats = ", ".join(item.split("—")[0].strip() for item in cat.get("harmful_components", [])[:3])
        table.add_row(str(idx), cat.get("icon", "📦"), cat["category"], threats)

    console.print(table)


def display_category_panel(category: dict) -> None:
    """Show detailed educational toxicology report for a single device category."""
    icon = category.get("icon", "📦")
    name = category["category"]

    harm_lines = "\n".join(f"  [red]⚠[/red]  [bold]{c.split('—')[0]}[/bold] — [dim]{c.split('—')[1] if '—' in c else ''}[/dim]" for c in category["harmful_components"])
    health_lines = "\n".join(f"  [yellow]💔[/yellow]  {h}" for h in category["health_effects"])
    env_lines = "\n".join(f"  [cyan]🌱[/cyan]  {s}" for s in category["environmental_stats"])

    left_panel = Panel(
        harm_lines,
        title="[bold red]☣ Toxic Components[/bold red]",
        border_style="red",
        padding=(1, 2),
    )
    right_panel = Panel(
        health_lines,
        title="[bold yellow]💔 Human Health Impacts[/bold yellow]",
        border_style="yellow",
        padding=(1, 2),
    )

    console.print(
        Panel(
            f"[bold bright_white]{icon}  {name.upper()} — ENVIRONMENTAL & TOXIC PROFILE[/bold bright_white]\n"
            f"[dim]Detailed hazard assessment according to CPCB & Basel Convention guidelines[/dim]",
            border_style="green",
            padding=(0, 2),
        )
    )
    console.print(Columns([left_panel, right_panel], equal=True))
    console.print(
        Panel(
            env_lines,
            title="[bold cyan]🌍 Environmental Impact & Resource Conservation[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        )
    )


def run_eco_quiz() -> None:
    """Run an interactive 3-question awareness quiz awarding bonus points."""
    console.print(
        Panel(
            "[bold green]🧠 Welcome to the EcoAwareness Quiz![/bold green]\n"
            "[dim]Answer 3 quick questions about safe e-waste disposal and earn +50 EcoCredit points.[/dim]",
            title="[bold green]🌱 Interactive Eco-Quiz[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
    )

    questions = [
        {
            "q": "Which toxic heavy metal found in CRT monitors & solder leads to severe brain & kidney damage?",
            "options": ["Lead (Pb)", "Silicon (Si)", "Iron (Fe)", "Gold (Au)"],
            "correct": 1,
            "explanation": "CRT monitors can contain up to 4 kg of toxic Lead, which severely contaminates soil and groundwater."
        },
        {
            "q": "What is the primary danger of dumping Lithium-ion batteries into regular municipal trash?",
            "options": ["They dissolve into water", "They can ignite runaway chemical fires & explode", "They attract insects", "They freeze landfill waste"],
            "correct": 2,
            "explanation": "Compacting or puncturing lithium batteries causes thermal runaway, releasing toxic gases and persistent fires."
        },
        {
            "q": "Roughly how much gold can be recovered from recycling 1 ton of discarded smartphones?",
            "options": ["Less than 1 gram", "Around 10 grams", "Over 300 grams (far more than gold ore)", "Zero gold"],
            "correct": 3,
            "explanation": "High-grade circuit boards contain over 300g of gold per ton — nearly 50x richer in gold than typical virgin gold mines!"
        }
    ]

    score = 0
    for i, q in enumerate(questions, start=1):
        console.print(f"\n[bold bright_white]Question {i}/3:[/bold bright_white] [cyan]{q['q']}[/cyan]")
        for opt_idx, opt in enumerate(q["options"], start=1):
            console.print(f"  [bold green]{opt_idx})[/bold green] {opt}")

        user_ans = Prompt.ask("\n[bold yellow]Your answer (1–4)[/bold yellow]", default="1").strip()
        try:
            if int(user_ans) == q["correct"]:
                score += 1
                console.print(f"[bold green]✔ Correct![/bold green] [dim]{q['explanation']}[/dim]")
            else:
                correct_text = q["options"][q["correct"] - 1]
                console.print(f"[bold red]✘ Incorrect.[/bold red] Correct answer: [bold]{correct_text}[/bold]. [dim]{q['explanation']}[/dim]")
        except ValueError:
            console.print(f"[bold red]Invalid option.[/bold red] The correct answer was {q['options'][q['correct'] - 1]}.")

    console.print()
    if score >= 2:
        bonus_pts = 50
        try:
            with open(ACCOUNT_PATH, "r+", encoding="utf-8") as f:
                acc = json.load(f)
                acc["total_points"] = acc.get("total_points", 0) + bonus_pts
                f.seek(0)
                json.dump(acc, f, indent=2)
                f.truncate()
            award_msg = f"[bold green]🎉 Fantastic Job! Score: {score}/3.[/bold green]\nYou earned [bold bright_yellow]+{bonus_pts} EcoCredit Bonus Points[/bold bright_yellow] credited to your account!"
        except Exception:
            award_msg = f"[bold green]🎉 Great job! Score: {score}/3.[/bold green]"
    else:
        award_msg = f"[bold yellow]Nice try! Score: {score}/3.[/bold yellow] Review the education library to boost your knowledge."

    console.print(
        Panel(award_msg, title="[bold green]Quiz Results[/bold green]", border_style="green", padding=(1, 2))
    )
    Prompt.ask("\n[dim]Press Enter to return to Education Menu[/dim]", default="")


def education_menu() -> None:
    """Main educational knowledge base menu."""
    categories = load_education_data()

    while True:
        console.print(
            Panel(
                "[bold green]Explore Hazardous Materials, Biological Impacts & Safe Recycling[/bold green]\n"
                "[dim]Knowledge empowers responsible disposal • Take the quiz to earn bonus rewards[/dim]",
                title="[bold green]📚 E-Waste Toxicology & Awareness Hub[/bold green]",
                border_style="green",
                padding=(1, 2),
            )
        )

        show_category_menu(categories)

        console.print(
            "\n[bold white]Additional Options:[/bold white]\n"
            "  [bold bright_yellow]Q[/bold bright_yellow] — 🧠 [bold]Take Interactive Eco-Awareness Quiz (+50 Points)[/bold]\n"
            "  [bold cyan]0[/bold cyan] — 🚪 Return to Main Menu"
        )

        choice = Prompt.ask(
            "\n[bold cyan]Select category number (1–6), 'Q' for Quiz, or '0' to exit[/bold cyan]",
            default="0",
        ).strip().upper()

        if choice == "0":
            break
        elif choice == "Q":
            run_eco_quiz()
        else:
            try:
                idx = int(choice)
                if 1 <= idx <= len(categories):
                    console.print()
                    display_category_panel(categories[idx - 1])
                    Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")
                else:
                    console.print(f"[red]Please enter a number between 1 and {len(categories)}.[/red]")
            except ValueError:
                console.print("[red]Invalid selection. Enter 1–6, Q, or 0.[/red]")
