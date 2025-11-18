# Hedging Playbook & Templates

**Purpose:** Provide plug-and-play hedging blueprints for key commodity exposures across the Enterprise Trading Framework. Each template includes instruments, sizing math, and automation hooks so portfolio managers can react when alerts fire.

---

## 1. Fuel & Energy Hedge (Airlines / Logistics / Autos)

| Item | Details |
|------|---------|
| **Exposure** | Jet fuel / diesel linked to Brent crude ($/bbl) |
| **Trigger** | Brent > $95 (from alert manager) OR 10% rally in 5 days |
| **Objective** | Lock cost ceiling for next 3 months |
| **Instruments** | ICE Brent futures, OTC swaps, options (3M call spread) |
| **Template Sizing** | `Hedge barrels = (Projected fuel usage * Hedge ratio)`<br>`Hedge ratio = Desired protection % / Pass-through ability` |
| **Example** | 1M liters jet fuel ≈ 6,290 bbl. Protect 70%: hedge 0.7 * 6,290 ≈ 4,403 bbl via long Brent call spread (strike $95/$110). |
| **Automation Hook** | `python automation/hedge_executor.py --strategy fuel --notional 4403 --expiry 2025-03-31` |

### Notes
- Airlines can finance premium using higher strike call sale (collar).  
- For logistics companies, combine diesel swaps + surcharge schedules.  
- Autos should coordinate with pricing team before hedging (pass-through windows).

---

## 2. Agricultural Input Hedge (FMCG / QSR / Breweries)

| Item | Details |
|------|---------|
| **Exposure** | Wheat, sugar, palm oil, cocoa |
| **Trigger** | Alert manager flags `✅ commodity benign` (low prices) → accumulate inventory; `⚠️ elevated` → hedge/fix price |
| **Objective** | Smooth gross margin over 6-12 months |
| **Instruments** | CBOT futures (wheat, corn), ICE (sugar, cocoa), Bursa Malaysia (palm), OTC swaps |
| **Template Sizing** | `Hedge lots = (Quarterly consumption / Contract size) * Hedge ratio` |
| **Example** | Biscuit maker uses 10,000 MT wheat/quarter. CBOT wheat contract 136 MT. Hedge 50%: `10,000 * 0.5 / 136 ≈ 37` contracts |
| **Automation Hook** | `python automation/hedge_executor.py --strategy agri --commodity wheat --lots 37 --tenor 2025-06` |

### Notes
- Pair hedges with recipe flexibility (switch oils) when spreads widen.  
- Cocoa and sugar volatility high; consider option collars vs straight futures.  
- Maintain inventory ledger to avoid double hedging physical + derivatives.

---

## 3. FX Overlay (Exporters / Importers)

| Item | Details |
|------|---------|
| **Exposure** | USD/INR, EUR/INR, USD/BRL, USD/CAD (commodities impact FX) |
| **Trigger** | Commodity move combined with FX technical break (e.g., copper rally + AUD/USD breakout) |
| **Objective** | Neutralize FX volatility tied to commodity exposure |
| **Instruments** | FX forwards, options (seagulls), cross-currency swaps |
| **Template Sizing** | `Notional = Forecast FX receivable/payable * Hedge ratio` |
| **Example** | IT exporter with $20M receivables hedges 60%: sell $12M 6M forward when USD/INR > 84 or risk of INR strength |
| **Automation Hook** | `python automation/hedge_executor.py --strategy fx --pair USDINR --notional 12000000 --tenor 6M --type forward` |

### Notes
- Combine with natural hedges (imports vs exports).  
- Use options when expecting large commodity-driven FX swings (e.g., crude crash → INR strengthens).  
- Coordinate with treasury to align with working capital cycles.

---

## 4. Metals & EV Supply Chain Hedge

| Item | Details |
|------|---------|
| **Exposure** | Copper, aluminum, lithium, nickel |
| **Trigger** | Sector rotation model recommends overweight OR alerts show headwind |
| **Objective** | Lock costs for CAPEX-heavy or EV programs |
| **Instruments** | LME futures, CME copper options, long-term offtake agreements |
| **Template Sizing** | `Hedge ratio = (Project requirement / Contract size)` |
| **Example** | EV OEM needs 5,000 MT copper. Hedge 40% via LME 25-tonne lots → `5,000 * 0.4 / 25 = 80` lots |
| **Automation Hook** | `python automation/hedge_executor.py --strategy metals --commodity copper --lots 80 --tenor 2025-12` |

### Notes
- Align hedges with CAPEX schedule; mis-timed hedges become speculation.  
- For lithium, consider long-term supply agreements with price caps.  
- Evaluate carbon exposure (EU ETS) simultaneously for European plants.

---

## 5. Carbon Permit & Renewable Hedge

| Item | Details |
|------|---------|
| **Exposure** | EU ETS, California CCA, REC prices |
| **Trigger** | EUA price > €100 or < €70, policy announcements |
| **Objective** | Stabilize compliance costs, monetize green premium |
| **Instruments** | EUA futures/options, REC forwards |
| **Template Sizing** | `Allowances = Forecast emissions (tonnes CO₂e)` |
| **Example** | Utility expects 1M tonnes CO₂e; buy EUA futures on 70% to lock cost |
| **Automation Hook** | `python automation/hedge_executor.py --strategy carbon --notional 700000 --tenor 2025-09` |

### Notes
- Combine with renewable PPAs to reduce required allowances.  
- Use options when expecting political volatility (elections, policy reform).  
- Track alert manager outputs for EUA status.

---

## 6. Automation & Governance Checklist

1. **Trigger Ingestion:** Alert manager posts Slack notification; run hedging script with context payload.  
2. **Trade Ticket Logging:** `automation/hedge_executor.py` writes JSON ticket + timestamp to `/logs/hedges`.  
3. **Approval Workflow:** Minimum two-step approval for notional > threshold (configurable).  
4. **Mark-to-Market Tracking:** Daily MTM via treasury system (link to `data_pipeline`).  
5. **Reporting:** Weekly hedge coverage report (actual vs policy range) auto-generated via `dashboard.sh hedges`.  

---

## 7. Sample Automation Command Cheat Sheet

```bash
# Fuel hedge (Brent call spread)
python automation/hedge_executor.py --strategy fuel --notional 5000 --instrument brent_call_spread --expiry 2025-03-31

# Sugar futures hedge
python automation/hedge_executor.py --strategy agri --commodity sugar --lots 25 --tenor 2025-07

# USD/INR forward sell
python automation/hedge_executor.py --strategy fx --pair USDINR --notional 15000000 --tenor 3M --type forward

# Copper futures hedge
python automation/hedge_executor.py --strategy metals --commodity copper --lots 60 --tenor 2025-12

# EUA compliance purchase
python automation/hedge_executor.py --strategy carbon --notional 500000 --tenor 2025-10
```

---

**Reminder:** Every hedge must reference the alert ID, underlying exposure, hedge ratio justification, and approval trail to remain audit compliant.
