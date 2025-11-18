# Quick Start Guide

## 🚀 3 Ways to Use the System

### 1. Command Line (Fastest)
```bash
python3 analyze_stock.py KPIGREEN
```

**Output:** Complete analysis in 2-3 seconds

---

### 2. Streamlit UI (Best UX)
```bash
streamlit run streamlit_app.py
```

**Features:**
- Visual charts
- Natural language queries
- Portfolio tracking
- Backtesting

---

### 3. Python API (For Integration)
```python
from stock_agents.orchestrator import MultiAgentOrchestrator

orchestrator = MultiAgentOrchestrator()
analysis = orchestrator.analyze('KPIGREEN', strategy='swing')
print(orchestrator.generate_report(analysis))
```

---

## 📊 What You Get

Every analysis includes:

✅ **Recommendation** - STRONG_BUY / BUY / HOLD / SELL  
✅ **Composite Score** - 0-100 weighted score  
✅ **Confidence** - How certain the system is  
✅ **Entry Price** - Where to buy  
✅ **Stop Loss** - Where to exit if wrong  
✅ **3 Targets** - Profit levels (1.5:1, 2.5:1, 4:1 R:R)  
✅ **Position Size** - % of portfolio (1-5%)  
✅ **Risk Level** - LOW / MEDIUM / HIGH  
✅ **Agent Consensus** - What each agent thinks  
✅ **Key Reasons** - Why this recommendation  

---

## 🤖 The 4 Agents

1. **Technical** (35%) - Price action, RSI, volume, Smart Money Concepts
2. **Fundamental** (30%) - ROE, growth, valuation, financial health
3. **Risk** (20%) - Position sizing, stop loss, risk/reward
4. **Market Context** (15%) - Market regime, sector strength, timing

**Orchestrator** coordinates all agents and resolves conflicts.

---

## 💡 Example Queries (Streamlit)

```
"Find stocks with ROE > 20%"
"Show undervalued stocks in IT sector"
"Which stocks are near support levels?"
"Stocks with high volume breakout"
"Best swing trading opportunities"
```

---

## ⚙️ Customize Agent Weights

```python
orchestrator = MultiAgentOrchestrator(weights={
    'technical': 0.40,      # More weight to technical
    'fundamental': 0.25,
    'risk': 0.20,
    'market_context': 0.15
})
```

---

## 🎯 Trading Strategies

### Swing Trading (Default)
- Holding period: 2-6 weeks
- Focus: Technical + momentum
- Risk: Medium

```bash
python3 analyze_stock.py KPIGREEN swing
```

### Long-term Investment
- Holding period: 2-5 years
- Focus: Fundamentals + quality
- Risk: Lower

```bash
python3 analyze_stock.py TCS long_term
```

---

## 📈 Understanding the Output

### Composite Score
- **75-100:** Strong opportunity
- **60-74:** Good opportunity
- **45-59:** Neutral / Hold
- **25-44:** Weak / Consider selling
- **0-24:** Avoid

### Confidence
- **80-100%:** High confidence, trust the signal
- **60-79%:** Moderate confidence, do additional research
- **<60%:** Low confidence, system downgrades to HOLD

### Conflict Detection
If agents disagree (e.g., Technical says SELL, Fundamental says BUY):
- System flags: ⚠️ CONFLICT DETECTED
- Automatically downgrades to HOLD
- Suggests proceeding with caution

---

## 🔧 Troubleshooting

### "No data found"
- Stock might be delisted
- Check ticker symbol (use .NS for NSE)
- Try alternative symbol

### "Rate limit exceeded"
- Wait 60 seconds
- Reduce query frequency
- Consider upgrading data source

### Slow performance
- First run is slower (downloads data)
- Subsequent runs use cache
- Average: 2-3 seconds per stock

---

## 📚 Learn More

- **[Multi-Agent Architecture](MULTI_AGENT_ARCHITECTURE.md)** - How it works
- **[README](README.md)** - Full documentation
- **[Natural Language Queries](NATURAL_LANGUAGE_QUERIES.md)** - NLP features

---

**Ready to analyze stocks? Start with:**
```bash
python3 analyze_stock.py KPIGREEN
```
