# EcoRecycle Finder Pro 🌿♻
### *Intelligent E-Waste Geolocation, Hazard Awareness & Precious Metal Recovery Portal*
*Built in alignment with the Ministry of Environment, Forest and Climate Change (MoEFCC) Safe E-Waste Directive*

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![UI-Rich](https://img.shields.io/badge/Interface-Rich%20CLI-emerald.svg)](https://github.com/Textualize/rich)
[![CPCB-Compliant](https://img.shields.io/badge/CPCB-E--Waste%20Compliant-blue.svg)](https://cpcb.nic.in/)
[![License-MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Problem Statement Alignment

> **Problem Statement:**  
> *"Website that tells you the location of the nearest e-waste collection and recycling facility. Offers educational pop-ups on the harmful components of your e-waste and their effects on the environment and human health if not disposed correctly. There could be an option to input the model of your old device and earn credit points relative to the amount of precious metals recovered from the device if disposed correctly."*  
> **Source:** Smart India Hackathon | Ministry of Environment | Smart Automation Bucket

EcoRecycle Finder implements every requirement with high-aesthetic terminal UI engineering:
1. **🗺 Certified Facility Locator:** Pan-India CPCB-verified recycling facilities with real-time **Haversine spherical distance calculation**, live **Open/Closed status**, and one-click **Google Maps navigation links**.
2. **🚨 Contextual Educational Hazard Pop-ups:** In-flow toxic component disclosures (Lead, Mercury, Cadmium, Arsenic) and organ health risks that pop up before points calculation to educate citizens.
3. **⚡ Precious Metals Credit Calculator:** Specific model input (iPhone, Samsung Galaxy, MacBook, etc.), device condition multipliers, recoverable precious metals valuation (Au, Ag, Cu, Pd, Pt), and exportable **Official Handover Certificates**.
4. **🎁 Partner Voucher Store & Impact Tracking:** Redeem points for Amazon Pay, Flipkart, Croma vouchers, or native tree planting certificates, with cumulative CO₂ and toxic waste abatement tracking.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Interactive Terminal Application
```bash
python main.py
```

### 3. CLI Shortcuts (Direct Feature Jumps)
```bash
python main.py --locate     # Open facility locator directly
python main.py --learn      # Open toxicology library & eco-quiz
python main.py --points     # Open recycling points & metal calculator
python main.py --rewards    # Open rewards dashboard & voucher store
python main.py --version    # Print version details
python main.py --help       # Display help menu
```

---

## 📂 Project Architecture

```
AD_PROJECT/
├── main.py                    # Entry point — splash banner, status bar, routing & signal handling
├── requirements.txt           # Minimal dependencies (rich)
├── README.md                  # Comprehensive project documentation
├── .gitignore                 # Excludes cache, bytecode, and system files
├── data/
│   ├── facilities.json        # 16+ authentic CPCB-registered multi-city facilities
│   ├── devices.json           # Specific consumer models & metal yield profiles
│   ├── education.json         # Toxic chemicals, biological effects & environmental stats
│   └── user_account.json      # Local profile, EcoPoints balance, and history
└── modules/
    ├── __init__.py
    ├── facility_locator.py    # Haversine distance, live operating status & directions
    ├── education.py           # Toxicology panels, hazard pop-ups & interactive eco-quiz
    ├── points_calculator.py   # Model search, hazard pop-up, condition multiplier & certificate
    └── rewards.py             # Voucher store, impact metrics & tier progression
```

---

## ✨ Feature Highlights

| Feature | Description |
|---|---|
| **🗺 Smart Facility Locator** | Dynamic distance calculation across Delhi NCR, Mumbai, Pune, Bengaluru, Hyderabad, Chennai, and Kolkata. Displays live operational status (Open/Closed) and Google Maps directions. |
| **🚨 Hazard Pop-Up Modal** | Educational modal appearing automatically during device evaluation, highlighting heavy metals, endocrine disruptors, and groundwater leaching risks. |
| **🧠 Interactive Eco-Quiz** | 3-question awareness quiz on e-waste rules that awards **+50 bonus EcoPoints** upon completion. |
| **⚡ Precious Metals Engine** | Computes exact milligram yields of Gold (Au), Silver (Ag), Copper (Cu), Palladium (Pd), and Platinum (Pt) based on working condition (Working: +20%, Cracked: Standard, Dead: -20%). |
| **📄 Digital Handover Certificate** | Exports a formatted Markdown certificate (`certificate_ECO_XXXX.md`) verifying device specs, recovered metals, and carbon offset. |
| **🎁 Partner Voucher Store** | Exchange accumulated points for Amazon Pay, Croma, Flipkart vouchers, or plant trees via SankalpTaru. |
| **🌍 Environmental Impact Stats** | Visual metric dashboard tracking cumulative CO₂ emissions prevented, freshwater preserved, and heavy metals diverted. |

---

## 🎖 Reward Tiers

| Tier | Points | Perks & Cash Equivalence |
|---|---|---|
| 🌱 **Seedling** | 0+ | Base collection points |
| 🌿 **Sprout** | 250+ | 5% bonus on metal values (₹25+ equiv.) |
| 🍃 **Green Hero** | 750+ | 10% bonus + Green Hero Profile Badge (₹75+ equiv.) |
| 🌳 **Eco Warrior** | 2,000+ | 15% bonus + Priority CPCB Pickup (₹200+ equiv.) |
| 🌍 **Planet Saver** | 5,000+ | 20% bonus + VIP Partner Vouchers (₹500+ equiv.) |

---

## 🛠 Tech Stack

- **Language:** Python 3.10+
- **Terminal UI Engine:** [Rich](https://github.com/Textualize/rich) (Tables, Panels, Progress Bars, Spinners)
- **Algorithms:** Haversine Spherical Distance, Token-Overlap Fuzzy Search
- **Data Persistence:** Local JSON storage (Offline-first, Zero-latency)
- **Signal Handling:** Clean `KeyboardInterrupt` interception

---

## 📜 License & Compliance

Distributed under the **MIT License**. Compliant with Central Pollution Control Board (CPCB) E-Waste Management Rules (2022/2023).
