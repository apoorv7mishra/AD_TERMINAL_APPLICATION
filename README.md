# EcoRecycle Finder 🌿♻

A terminal-based CLI application to help users locate nearby e-waste collection facilities, learn about e-waste hazards, and earn credit points for responsible recycling.

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the application

```bash
python main.py
```

---

## 📂 Project Structure

```
AD_PROJECT/
├── main.py                    # Entry point — main menu loop
├── requirements.txt
├── README.md
├── data/
│   ├── facilities.json        # E-waste collection centres dataset
│   ├── devices.json           # Device-to-metals lookup table
│   ├── education.json         # Hazard info per device category
│   └── user_account.json      # Local user account & points storage
└── modules/
    ├── __init__.py
    ├── facility_locator.py    # Feature 1: Find nearby facilities
    ├── education.py           # Feature 2: E-waste education panels
    ├── points_calculator.py   # Feature 3: Recycling credit calculator
    └── rewards.py             # Feature 4: Rewards & points dashboard
```

---

## ✨ Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **🗺 Facility Locator** | Search by city/pincode, filter by device type, view detailed directions |
| 2 | **📚 Learn About E-Waste** | Hazardous components, health effects, and environmental stats by category |
| 3 | **⚡ Points Calculator** | Fuzzy device search, precious metals estimation, redemption code generation |
| 4 | **🏆 My Rewards** | Total points, tier badge, history table, redemption guide |
| 5 | **ℹ About** | App info, India e-waste statistics |

---

## ⚡ CLI Flags (Jump Directly to a Feature)

```bash
python main.py --locate     # Open facility locator
python main.py --learn      # Open education module
python main.py --points     # Open points calculator
python main.py --rewards    # Open rewards dashboard
python main.py --version    # Print version
python main.py --help       # Show help
```

---

## 🎖 Reward Tiers

| Tier | Points | Cash Equivalent |
|------|--------|----------------|
| 🌱 Seedling | 0+ | — |
| 🌿 Sprout | 250+ | ₹25+ |
| 🍃 Green Hero | 750+ | ₹75+ |
| 🌳 Eco Warrior | 2000+ | ₹200+ |
| 🌍 Planet Saver | 5000+ | ₹500+ |

---

## 📦 Data Sources (Fictional / Demo)

All data is fictional but realistic, bundled locally for fully offline operation:
- **facilities.json** — 8 sample e-waste centres in Noida, UP
- **devices.json** — 15 common consumer electronics with precious metal content
- **education.json** — 6 device categories with hazard profiles
- **user_account.json** — Local account file (auto-created / persisted)

---

## 🛠 Tech Stack

- **Python 3.10+**
- **[rich](https://github.com/Textualize/rich)** — Tables, panels, spinners, styled text
- **argparse** — CLI flag handling
- **JSON** — Local data storage (no external DB)

---

*Made with 💚 for a cleaner planet.*
