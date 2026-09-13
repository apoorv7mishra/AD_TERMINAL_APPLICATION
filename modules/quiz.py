"""
EcoRecycle Finder — Quiz Engine Module
A full 10-question interactive quiz with:
  - Randomised question selection & shuffled option order
  - Per-attempt scoring with live feedback
  - Tiered bonus EcoCredit rewards
  - Personal best & quiz history tracking in user_account.json
"""

import json
import random
from pathlib import Path
from datetime import datetime

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt
from rich import box
from rich.rule import Rule
from rich.align import Align
from rich.columns import Columns
from modules.ui import console

QUESTIONS_PATH = Path(__file__).parent.parent / "data" / "quiz_questions.json"
ACCOUNT_PATH   = Path(__file__).parent.parent / "data" / "user_account.json"

# ── Reward tiers keyed on score out of 10 ────────────────────────────────────
REWARD_TIERS = [
    {"min_score": 10, "label": "🏆 Perfect Score!",    "points": 100, "style": "bold bright_cyan"},
    {"min_score": 8,  "label": "🌍 Eco Expert",         "points": 50,  "style": "bold bright_green"},
    {"min_score": 5,  "label": "🍃 Green Aware",         "points": 30,  "style": "bold green"},
    {"min_score": 0,  "label": "🌱 Keep Learning",       "points": 0,   "style": "dim yellow"},
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_questions() -> list[dict]:
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_account() -> dict:
    with open(ACCOUNT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_account(account: dict) -> None:
    with open(ACCOUNT_PATH, "w", encoding="utf-8") as f:
        json.dump(account, f, indent=2)


def get_reward_tier(score: int, total: int) -> dict:
    """Return the reward tier dict matching the player's score."""
    for tier in REWARD_TIERS:
        if score >= tier["min_score"]:
            return tier
    return REWARD_TIERS[-1]


def shuffle_options(question: dict) -> tuple[list[str], int]:
    """
    Shuffle the answer options so the correct answer isn't always in
    the same position. Returns (shuffled_options, new_correct_index).
    """
    options = list(enumerate(question["options"]))   # [(orig_idx, text), ...]
    random.shuffle(options)
    shuffled_texts = [text for _, text in options]
    # Find where the original correct index ended up
    original_correct = question["correct"]
    new_correct = next(
        i for i, (orig_idx, _) in enumerate(options) if orig_idx == original_correct
    )
    return shuffled_texts, new_correct


# ── Quiz History display ──────────────────────────────────────────────────────

def show_quiz_history(account: dict) -> None:
    """Print a table of past quiz attempts stored in user_account.json."""
    history = account.get("quiz_history", [])

    if not history:
        console.print(
            Panel(
                "[dim]No quiz attempts yet.\nComplete a quiz to see your history here.[/dim]",
                border_style="dim green",
                padding=(1, 2),
            )
        )
        return

    table = Table(
        title=f"[bold green]📊 Quiz History ({len(history)} attempt(s))[/bold green]",
        box=box.ROUNDED,
        border_style="green",
        header_style="bold bright_green on dark_green",
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("#",          style="dim cyan",        width=4,  justify="center")
    table.add_column("Score",      style="bold white",      width=10, justify="center")
    table.add_column("Grade",      style="bold green",      min_width=18)
    table.add_column("Points Won", style="bold yellow",     width=12, justify="right")
    table.add_column("Date",       style="dim white",       min_width=18)

    personal_best = max(h["score"] for h in history)

    for idx, attempt in enumerate(reversed(history[-10:]), start=1):
        score   = attempt.get("score", 0)
        total   = attempt.get("total", 10)
        grade   = attempt.get("grade", "—")
        pts     = attempt.get("points_awarded", 0)
        date    = attempt.get("date", "—")
        is_best = "  ⭐ PB" if score == personal_best else ""
        table.add_row(
            str(idx),
            f"{score}/{total}",
            f"{grade}{is_best}",
            f"+{pts}" if pts else "—",
            date,
        )

    console.print(table)
    console.print(
        f"  [bold white]Personal Best:[/bold white] [bold bright_green]{personal_best}/10[/bold bright_green]   "
        f"[bold white]Total Quiz Points:[/bold white] [bold yellow]{sum(h.get('points_awarded', 0) for h in history):,}[/bold yellow]\n"
    )


# ── Core quiz runner ──────────────────────────────────────────────────────────

def run_quiz(num_questions: int = 10) -> None:
    """
    Interactive quiz flow:
      1. Draw `num_questions` from the pool (randomised, shuffled options)
      2. Show live Q&A with instant right/wrong feedback
      3. Display score summary panel with tier badge
      4. Award bonus EcoCredits and persist to account
    """
    all_questions = load_questions()
    selected = random.sample(all_questions, min(num_questions, len(all_questions)))
    total = len(selected)

    # ── Intro panel ───────────────────────────────────────────────────────────
    console.print(
        Panel(
            f"[bold green]🧠 EcoAwareness Quiz — {total} Questions[/bold green]\n\n"
            f"  [white]Topics covered:[/white] E-Waste Toxicology, Health Risks, Policy & Urban Mining\n"
            f"  [white]Scoring:[/white]\n"
            f"    [bold bright_cyan]10/10[/bold bright_cyan]  → +100 pts  🏆 Perfect Score!\n"
            f"    [bold bright_green] 8–9[/bold bright_green]   → +50 pts   🌍 Eco Expert\n"
            f"    [bold green] 5–7[/bold green]   → +30 pts   🍃 Green Aware\n"
            f"    [dim yellow] 0–4[/dim yellow]   →   0 pts   🌱 Keep Learning\n\n"
            f"[dim]Answer each question by typing the option number and pressing Enter.[/dim]",
            title="[bold bright_green]📋 Quiz Rules[/bold bright_green]",
            border_style="green",
            padding=(1, 2),
        )
    )
    Prompt.ask("[dim]Press Enter when ready to start[/dim]", default="")

    score       = 0
    correct_ids = []
    wrong_ids   = []

    for q_num, question in enumerate(selected, start=1):
        options, correct_idx = shuffle_options(question)

        # ── Question panel ────────────────────────────────────────────────────
        console.print(Rule(
            f"[dim green]Question {q_num} of {total}  ·  Score: {score}/{q_num - 1}[/dim green]",
            style="dim green",
        ))
        console.print(
            Panel(
                f"[bold bright_white]{question['question']}[/bold bright_white]",
                border_style="cyan",
                padding=(0, 2),
            )
        )

        # Category badge
        console.print(
            f"  [dim]Category: [italic]{question.get('category', 'General')}[/italic][/dim]\n"
        )

        # Options
        for i, opt in enumerate(options, start=1):
            console.print(f"  [bold bright_green]{i})[/bold bright_green] {opt}")

        # User input with validation
        while True:
            ans = Prompt.ask(
                f"\n[bold yellow]Your answer[/bold yellow] [dim](1–{len(options)})[/dim]",
                default="1",
            ).strip()
            try:
                ans_idx = int(ans) - 1
                if 0 <= ans_idx < len(options):
                    break
                console.print(f"[red]Enter a number between 1 and {len(options)}.[/red]")
            except ValueError:
                console.print("[red]Invalid input — please enter a number.[/red]")

        # ── Feedback ──────────────────────────────────────────────────────────
        if ans_idx == correct_idx:
            score += 1
            correct_ids.append(question["id"])
            console.print(
                Panel(
                    f"[bold green]✔  Correct![/bold green]\n"
                    f"[dim]{question['explanation']}[/dim]",
                    border_style="green",
                    padding=(0, 2),
                )
            )
        else:
            wrong_ids.append(question["id"])
            console.print(
                Panel(
                    f"[bold red]✘  Incorrect.[/bold red]  "
                    f"Correct answer: [bold bright_white]{options[correct_idx]}[/bold bright_white]\n"
                    f"[dim]{question['explanation']}[/dim]",
                    border_style="red",
                    padding=(0, 2),
                )
            )

        console.print()

    # ── Final score + tier ────────────────────────────────────────────────────
    tier = get_reward_tier(score, total)
    pct  = int((score / total) * 100)

    # Progress bar
    bar_len = 30
    filled  = int((score / total) * bar_len)
    bar = "[bold green]" + "█" * filled + "[/bold green]" + "[dim]" + "░" * (bar_len - filled) + "[/dim]"

    result_content = (
        f"  [{tier['style']}]{tier['label']}[/{tier['style']}]\n\n"
        f"  [bold white]Score:[/bold white]     [bold bright_white]{score}/{total}[/bold bright_white]  ({pct}%)\n"
        f"  [bold white]Progress:[/bold white]  {bar}\n"
        f"  [bold white]Correct:[/bold white]   [bold green]{len(correct_ids)}[/bold green]  questions\n"
        f"  [bold white]Wrong:[/bold white]     [bold red]{len(wrong_ids)}[/bold red]  questions\n\n"
    )

    if tier["points"] > 0:
        result_content += (
            f"  [bold white]🎁 Bonus Points:[/bold white] "
            f"[bold bright_yellow]+{tier['points']} EcoCredits[/bold bright_yellow] added to your account!"
        )
    else:
        result_content += (
            "  [dim]No bonus points this time. Score 5+ to earn EcoCredits![/dim]\n"
            "  [dim]Try again after reviewing the Education library.[/dim]"
        )

    console.print(
        Panel(
            result_content,
            title="[bold green]🏁 Quiz Complete — Results[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
    )

    # ── Persist to account ────────────────────────────────────────────────────
    account = load_account()
    account["total_points"] = account.get("total_points", 0) + tier["points"]

    attempt_record = {
        "score":          score,
        "total":          total,
        "percent":        pct,
        "grade":          tier["label"],
        "points_awarded": tier["points"],
        "correct_q_ids":  correct_ids,
        "wrong_q_ids":    wrong_ids,
        "date":           datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    account.setdefault("quiz_history", []).append(attempt_record)
    save_account(account)

    # Updated balance
    console.print(
        f"\n  [dim]Updated balance: [bold bright_green]{account['total_points']:,}[/bold bright_green] EcoPoints[/dim]\n"
    )

    Prompt.ask("[dim]Press Enter to return[/dim]", default="")


# ── Entry-point called from education_menu ────────────────────────────────────

def quiz_menu() -> None:
    """Top-level quiz menu: history view or start new attempt."""
    while True:
        console.print(
            Panel(
                "[bold green]Test your knowledge about e-waste hazards, health risks & recycling policy.[/bold green]\n"
                "[dim]10 randomised questions · Shuffled options · Instant feedback · EcoCredit rewards[/dim]",
                title="[bold]🧠 EcoAwareness Quiz[/bold]",
                border_style="green",
                padding=(1, 2),
            )
        )

        account = load_account()
        history = account.get("quiz_history", [])

        # Quick stats
        if history:
            best  = max(h["score"] for h in history)
            total_quiz_pts = sum(h.get("points_awarded", 0) for h in history)
            console.print(
                f"  [bold white]Attempts:[/bold white] [cyan]{len(history)}[/cyan]   "
                f"[bold white]Personal Best:[/bold white] [bright_green]{best}/10[/bright_green]   "
                f"[bold white]Quiz Points Earned:[/bold white] [yellow]{total_quiz_pts:,}[/yellow]\n"
            )

        console.print(
            "[bold white]Options:[/bold white]\n"
            "  [bold bright_green]1[/bold bright_green] — 🚀 Start New Quiz (10 questions)\n"
            "  [bold bright_green]2[/bold bright_green] — 📊 View Quiz History\n"
            "  [bold cyan]0[/bold cyan] — 🚪 Return to Education Menu"
        )

        choice = Prompt.ask(
            "\n[bold cyan]Select[/bold cyan] [dim](1, 2, or 0)[/dim]",
            default="0",
        ).strip()

        if choice == "1":
            console.print()
            run_quiz()
        elif choice == "2":
            console.print()
            show_quiz_history(account)
            Prompt.ask("[dim]Press Enter to continue[/dim]", default="")
        elif choice == "0":
            break
        else:
            console.print("[red]Invalid selection. Enter 1, 2, or 0.[/red]")
