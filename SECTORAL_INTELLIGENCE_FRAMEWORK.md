# Enterprise Trading Framework – Sectoral Intelligence Module

**Version:** 1.0  
**Last Updated:** November 18, 2025  
**Owner:** Market Context / Sector Intelligence Working Group

---

## 1. Executive Snapshot

| Item | Detail |
|------|--------|
| **Core Problem** | Stock calls ignore sector rotations, macro shocks, and policy shifts → winning stocks picked at losing times |
| **Objective** | Build an institutional-grade Sector Intelligence layer that feeds every agent and portfolio workflow |
| **Output** | Sector-aware recommendations answering: **Is this the right sector? Is this the right stock within it? Is this the right time?** |
| **Consumers** | Market Context Agent, Orchestrator, Portfolio Manager, Idea Engine, Risk Engine |

---

## 2. Problem Statement (Why This Matters)

1. **Sectors move in packs** – liquidity, policy, macro cycles reward/punish entire groups simultaneously.
2. **Stock-only analysis fails** – a perfect company under a sector-wide downcycle underperforms; an average company in a sector upcycle can beat.
3. **Timing is critical** – knowing *when* to rotate between Banking → Infra → Defensives is as important as *what* to own.
4. **Macro & policy shocks** – rates, inflation, crude, budget allocation, monsoon, Fed moves, China demand – each hits sectors differently.
5. **Correction types** – sideways vs price collapses vs multi-year drifts require different playbooks.
6. **Multi-agent gap** – existing agents (technical/fundamental) lack a persistent macro-sector memory to guide signals.

**Answer we must deliver:** _“Given today’s macro, sector positioning, and cycle phase, here is where capital should be deployed and why.”_

---

## 3. Multi-Layered Sector Intelligence Blueprint

| Layer | Purpose |
|-------|---------|
| **L1. Sector Taxonomy & Identity** | Precise mapping of every stock to sector/sub-sector/business model |
| **L2. Macro Drivers & Sensitivity Matrix** | Quantify rate/inflation/GDP/currency/crude/monsoon/capex impacts |
| **L3. Tailwinds & Headwinds Radar** | Ongoing qualitative + quantitative assessment (structural vs cyclical) |
| **L4. Correction Classifier** | Distinguish time, price, and time+price corrections at sector level |
| **L5. Sector Rotation Engine** | Map economic cycle to favored sectors + trigger-based rotation rules |
| **L6. Intra-Sector Stock Selection** | Rank leaders vs laggards using sector-specific scorecards |
| **L7. Sector Context Agent Workflow** | Embed intelligence into multi-agent system |
| **L8. Data Inputs & Pipelines** | Define macro/sector data feeds, frequency, APIs |
| **L9. Study Playbooks & Monitoring** | Repeatable sector study process & cadence |
| **L10. Integration & Output Format** | Standard JSON blocks for downstream agents & UI |
| **L11. Advanced Concepts** | Relative sector strength, beta, concentration risk |

---

## 4. Layer 1 – Sector Classification & Taxonomy

### 4.1 Nifty-Oriented Sector Stack

1. **Banking & Financial Services** – Private banks, PSU banks, NBFCs, Insurance, Fintechs  
2. **Information Technology** – Large-cap IT services, mid-cap IT, product/platform plays, consumer internet  
3. **Energy** – Upstream (ONGC), downstream/refining (Reliance, IOC), gas distributors (IGL), renewables (Adani Green, NTPC)  
4. **Automobile & Components** – PV, CV, 2W, EV OEMs, auto ancillaries  
5. **Pharma & Healthcare** – Domestic formulations, US generics, APIs, hospitals, diagnostics  
6. **FMCG & Retail** – Food/beverages, personal care, tobacco, modern retail, D2C hybrids  
7. **Metals & Mining** – Steel, aluminum, copper, zinc, mining majors  
8. **Infrastructure & Construction** – EPC, cement, real estate, engineering services  
9. **Telecom** – Operators, tower infra, equipment/OFC players  
10. **Capital Goods & Industrials** – Power equipment, rail/defense, heavy engineering  
11. **Consumer Durables & Electronics** – White goods, OEM/ODM, appliances  
12. **Chemicals & Petrochemicals** – Specialty, agrochem, coatings, polymer value chain  
13. **Media & Entertainment** – Broadcast, print, OTT, cinema expo, advertising IP  
14. **Hospitality & Travel** – Hotels, aviation, travel tech, QSR  

### 4.2 Market-Cap Buckets per Sector

- **Large-Cap Leaders** – Top 3-5 by market cap; “sector bellwethers”  
- **Mid-Cap Growth** – Next 5-10 names; higher beta, faster earnings CAGR  
- **Small-Cap Emerging** – Early-stage players; higher dispersion  
- **Micro-Cap Speculative** – Thin liquidity; require risk guardrails  

### 4.3 Business-Model Overlay

| Model | Examples | Notes |
|-------|----------|-------|
| **Asset Heavy** | Infra EPC, power gen, airlines | High capex, leverage sensitive |
| **Asset Light** | IT services, pharma formulations | High ROCE, low capex |
| **Working-Capital Intensive** | Retail, auto dealers, chemicals | Inventory funding risk |
| **Cash Generators** | FMCG, established IT, tobacco | Strong FCF, dividend capacity |
| **Capital Cycle Dependent** | Banks/NBFCs, PSU infra | Need recurring capital infusions |

---

## 5. Layer 2 – Macro Variables & Sensitivities

### 5.1 Core Macro Dashboard

| Macro | Current Example | Trend | Long-Term Context |
|-------|-----------------|-------|-------------------|
| RBI Repo Rate | 6.50% | Stable | Neutral vs 5-7% band |
| CPI Inflation | 5.5% | Falling | Slightly above 4% target |
| GDP Growth | 6.8% | Rising | High vs EM peers |
| USD/INR | 83.2 | Flat | Near historic lows |
| Brent Crude | $85 | Stable | Tight supply |
| Monsoon | 97% of LPA | Normal | Supports rural |
| Govt Capex | ₹10L+ Cr | Elevated | Election-year thrust |
| US Fed | 5.25-5.50% | Dovish bias forming | Impacts FII flows |

### 5.2 Sector Impact Matrix (Sample)

**Interest Rates (Rising vs Falling)**

| Sector | Rising Rates | Falling Rates |
|--------|--------------|---------------|
| Banking (private) | ✅ NIM expand | ❌ Spread compression |
| NBFCs | ⚠️ Higher CoF | ✅ Funding tailwind |
| Real Estate | ❌ EMI drag | ✅ Affordability boost |
| Auto | ❌ 70% financed | ✅ Cheaper credit |
| Infra/Capex | ❌ Debt-heavy | ✅ Lower financing |
| FMCG/Pharma | ⚠️ Neutral | ⚠️ Neutral |
| IT | ⚠️ Indirect (US) | ⚠️ Indirect |

**Inflation (High vs Low)**, **GDP (High vs Low)**, **USD/INR (Depreciating vs Appreciating)**, **Crude (>$90 vs <$70)**, **Monsoon (Good vs Poor)**, **Govt Capex (High vs Low)** with similar tables must be part of the data model (refer Appendix A for full matrices).

### 5.3 Event Watchlist & Reaction Playbook

| Event | Indicator | Reassess |
|-------|-----------|----------|
| RBI MPC | Repo change, stance | Banks, NBFCs, Real Estate |
| Union Budget | Capex allocations, taxes | Infra, Defense, FMCG, alcohol |
| IMD Monsoon Update | % of LPA | FMCG, 2W, tractors, agrochem |
| US Fed | Dot plot, QT/QE | IT, Pharma exporters |
| China PMI | >50 expansion? | Metals, chemicals |
| Brent Spike | +10% week-on-week | OMCs, airlines, paints |

---

## 6. Layer 3 – Tailwinds & Headwinds Radar (FY24-25)

Each sector keeps a **T/H card** with qualitative tags (Structural / Cyclical / Event-driven) + confidence levels. Example snapshots:

### 6.1 Banking & Financial Services
- **Tailwinds (Structural/Cyclical)**: 12-15% credit CAGR, mortgage boom, digital adoption, PSU consolidation, asset quality at decade lows.  
- **Headwinds**: RBI caps on unsecured lending, fintech competition, monsoon risk on agri portfolios, potential global risk-off.

### 6.2 IT Services
- **Tailwinds**: AI/GenAI services, GCC expansion, lower attrition, cloud modernization.  
- **Headwinds**: US discretionary cuts, INR appreciation risk, wage inflation, BFSI caution.

### 6.3 Auto
- **Tailwinds**: EV subsidies (PLI), premiumization, export opportunity, scrappage policy, chip supply normalization.  
- **Headwinds**: High EMIs, commodity volatility, EV disruption risk, fuel-price sensitivity.

*(Replicate for Pharma, FMCG, Metals, Infra, Energy, Capital Goods, Chemicals, Telecom, Hospitality – include in Appendix B.)*

### 6.4 Tailwind / Headwind Timing

| Type | Duration | Example |
|------|----------|---------|
| Structural | 3-10 yrs | Demographics favoring consumption |
| Cyclical | 6-36 months | Rate cycle, commodity super-cycle |
| Event-driven | Immediate-6 months | Budget, policy shock, USFDA action |
| Policy-driven | 1-5 yrs | EV subsidies, defense indigenization |

---

## 7. Layer 4 – Correction Pattern Engine

| Pattern | Definition | Signals | Playbook | Example |
|---------|------------|---------|----------|---------|
| **Time Correction** | Sideways 5-15% range for 3-12 months | Flat MAs, contracting ranges | Accumulate leaders on dips | Nifty IT (2022-23) |
| **Price Correction** | Sharp 15-40% drop in weeks/months | Support breaks, high volume | Wait for bottom, buy reversal | Nifty Metal (2022) |
| **Time + Price** | 30-60% drop lasting 1-3 yrs | Lower highs/lows, weak fundamentals | Avoid until structural fix | Telecom (2016-20) |

**Decision Matrix:**
- Identify correction class from relative strength + price structure
- Attach recommended tactics (accumulate, wait, avoid)

---

## 8. Layer 5 – Sector Rotation Strategy

### 8.1 Economic Cycle Mapping

1. **Early Cycle (rates falling, liquidity high)** → Banks, Autos, Real Estate  
2. **Mid Cycle (GDP accelerating)** → Capital Goods, Industrials, Consumer Discretionary  
3. **Late Cycle (inflation rising)** → Energy, Materials, Infra  
4. **Slowdown/Recession** → Defensives (FMCG, Pharma, Utilities)  

### 8.2 Rotation Triggers

| Trigger | Rotate From | Rotate To | Rationale |
|---------|-------------|-----------|-----------|
| RBI rate cuts | IT/Pharma | Banks/Auto/Realty | Credit cycle inflects |
| GDP >7% | FMCG/Def | Capital Goods/Infra | Capex restart |
| Crude >$100 | Airlines/Paints | Upstream energy | Input shock |
| Weak Monsoon | Rural plays | Export/urban sectors | Demand risk |
| US recession fears | Export-heavy | Domestic cyclicals | Diversify exposure |
| China stimulus | Domestic | Metals/Chemicals | Global demand tailwind |

### 8.3 Rotation Dashboard (Sample Columns)

- Sector 1M/3M/6M return vs Nifty
- Relative Sector Strength slope
- Macro trigger flag (binary)
- Recommended action (Overweight/Neutral/Underweight)

---

## 9. Layer 6 – Intra-Sector Stock Selection

### 9.1 Leader vs Laggard Scorecard

| Metric | Leader Profile | Laggard Warning |
|--------|----------------|-----------------|
| Market Share | Top 3, gaining share | Sub-scale, declining |
| ROE/ROCE | Consistent >15-18% | <12%, volatile |
| Debt/Equity | <0.5 (unless regulated) | >1.5 without visibility |
| Operating Margin | Stable/improving | Eroding margins |
| Revenue CAGR (3Y) | >15% (growth sectors) | <8% |
| FCF | Positive, predictable | Negative or erratic |
| Governance | Transparent, aligned | Promoter pledges, churn |
| Valuation vs peers | Premium justified | “Cheap for a reason” |

### 9.2 Use Case Example – Banks (Tailwind Phase)

| Stock | Pros | Cons | Verdict |
|-------|------|------|--------|
| HDFC Bank | Digital leader, 1% GNPA | Premium 22x P/E | ✅ Core buy |
| ICICI Bank | Corporate + retail, improving asset quality | Slightly higher beta | ✅ Accumulate |
| Axis Bank | Retail pivot, improving | Legacy issues, execution risk | ⚠️ Position-sized |
| Yes Bank | Cheap headline | Governance & NPAs | ❌ Avoid |

---

## 10. Layer 7 – Sector Context Agent Workflow

1. **Inputs:** Ticker, sector mapping, macro dashboard, sector index data, relative strength, tailwind/headwind tags, correction class.  
2. **Processing:**
   - Determine macro environment (BULL/NEUTRAL/BEAR)  
   - Fetch sector score (RSI, price trend, RSS)  
   - Identify current cycle phase + correction type  
   - Compile tailwinds/headwinds with confidence  
   - Rank stock within sector peers
3. **Outputs (JSON block):**
```json
{
  "sector": "IT Services",
  "macro_environment": "NEUTRAL_TO_POSITIVE",
  "sector_phase": "TIME_CORRECTION_ENDING",
  "relative_strength": "STABLE",
  "tailwinds": ["AI services ramp", "GCC expansion"],
  "headwinds": ["US budget caution"],
  "stock_rank": "LEADER",
  "recommendation": "SECTOR_TURNING_POSITIVE"
}
```
4. **Consumers:** Orchestrator (weight adjustments), Technical/Fundamental agents (context lines), Portfolio manager (overweight/underweight), Idea engine (sector filter).

---

## 11. Layer 8 – Data Plumbing

| Data | Source | Frequency | Access |
|------|--------|-----------|--------|
| RBI policy | RBI API / scraping | 6-8x / year | REST |
| CPI/GDP | MOSPI | Monthly/Quarterly | CSV download |
| FX, Brent | NSE/Investing.com | Real-time | API/Websocket |
| Sector indices & P/E | NSE | Daily | NSE API |
| PMI | S&P Global | Monthly | Subscription feed |
| Auto sales | SIAM/Vahan | Monthly | Reports/API |
| Bank credit | RBI | Fortnightly | DB pull |
| Capex allocation | Union Budget docs | Annual | Manual tagging |
| News sentiment | ET/BS + NLP | Daily | RSS + LLM summarizer |

Integration requirement: central **Sector Intelligence DB/table** storing daily snapshots with change deltas for quick agent access.

---

## 12. Layer 9 – Sector Study Playbook

| Cadence | Checklist |
|---------|-----------|
| **Daily (5 min)** | Track sector indices vs Nifty, read top headlines, note crude/FX moves |
| **Weekly (15 min)** | Review FII/DII sectoral flows, macro triggers, key data releases |
| **Monthly (1 hr)** | Read 1-2 sell-side sector notes, refresh macro dashboard, rebalance sector weights |
| **Quarterly (2-3 hrs)** | Analyze sector earnings, update T/H matrix, reclassify correction phases, check portfolio concentration |

Process steps: Understand structure → identify drivers → map macro sensitivity → study history → monitor leading indicators.

---

## 13. Layer 10 – Integration & Output Standards

### 13.1 Agent Contract

- `sector_signal` (FAVORABLE / NEUTRAL / UNFAVORABLE)
- `sector_phase` (EARLY_UPCYCLE / LATE / TIME_CORRECTION / PRICE_CORRECTION)
- `tailwinds`, `headwinds` arrays (each item tagged: {type, confidence, horizon})
- `relative_strength_score` (0-100) & slope trend
- `recommended_action` (Overweight / Market Weight / Underweight)
- `priority_watch_items` (macro events, data prints)

### 13.2 UI / Report Template

> **Sector View:** Banking (FAVORABLE) – Credit cycle intact, RBI stable, mortgage demand strong. Tailwinds (5) vs Headwinds (2). Sector phase: Early upcycle. Leaders: HDFCBANK, ICICIBANK. Prefer Overweight with staggered adds.

---

## 14. Layer 11 – Advanced Guardrails

1. **Relative Sector Strength (RSS)** – maintain 90-day trend to detect leadership change; rising RSS for 3+ weeks → watchlist upgrade.  
2. **Sector Beta Awareness** – categorize sectors by volatility (Metals, PSU banks high beta; FMCG, Pharma low beta) for position sizing.  
3. **Concentration Risk** – default cap: 25% per sector (conservative) / 40% (aggressive). Trigger alerts when breached.  
4. **Backtesting Hooks** – evaluate sector-rotation strategy vs baseline (e.g., 2018-2024) to quantify alpha.

---

## 15. Implementation Roadmap (High-Level)

| Phase | Milestones |
|-------|------------|
| **P1 – Data Foundation** | Build sector taxonomy table; ingest macro feeds; store daily sector index snapshots |
| **P2 – Intelligence Layer** | Tailwind/headwind tagging service; correction classifier; RSS calculator |
| **P3 – Agent Integration** | Sector Context Agent v2, orchestrator weighting, portfolio alerts |
| **P4 – UI & Automation** | Dashboards, alerting (Slack/email), auto-rotation suggestions |
| **P5 – Backtest & Optimization** | Measure rotation alpha, refine triggers, add ML signals |

---

## 16. Key Takeaways

- **Right Stock + Wrong Sector = Dead money.** Integrate sector context into every trade idea.  
- **Macro shifts hit sectors differently.** Keep a live sensitivity matrix.  
- **Detect correction types early** to choose between patience vs exit.  
- **Timely sector rotation** compounds alpha more than single-stock tweaks.  
- **Leaders vs laggards ranking** avoids value traps even in good sectors.  
- **Standardized sector outputs** let multi-agent framework reason like an institutional desk.

> **North Star:** Deliver recommendations that explicitly state _“This is the sector regime, these are the drivers, this is the stock hierarchy, and here’s how long the thesis should last.”_

---

### Appendices (To Expand Next)

- **Appendix A:** Full macro impact matrices (rates, inflation, GDP, FX, crude, monsoon, capex)  
- **Appendix B:** Detailed tailwind/headwind tables for all 14 sectors  
- **Appendix C:** Sample dashboards & JSON schemas  
- **Appendix D:** Backtesting methodology for sector rotation
