# Quick Reference Cheat Sheet

## 🚀 Most Common Commands

```bash
# Analyze a stock (with learning)
python3 analyze_with_learning.py KPIGREEN

# Analyze without learning
python3 analyze_stock.py KPIGREEN

# Start web interface
streamlit run streamlit_app.py

# Evaluate past predictions
python3 analyze_with_learning.py --evaluate

# View learning dashboard
python3 analyze_with_learning.py --dashboard
```

---

## 🤖 What Each Agent Does

| Agent | Focus | Weight | Key Metrics |
|-------|-------|--------|-------------|
| **Technical** | Price action | 35% | RSI, Volume, SMC |
| **Fundamental** | Company quality | 30% | ROE, Growth, Ratios |
| **Risk** | Position sizing | 20% | Stop loss, R:R |
| **Market Context** | Timing | 15% | Regime, Sector |

---

## 📊 Understanding Scores

| Score | Meaning | Action |
|-------|---------|--------|
| **75-100** | Strong opportunity | Consider buying |
| **60-74** | Good opportunity | Research more |
| **45-59** | Neutral | Hold or wait |
| **25-44** | Weak | Consider selling |
| **0-24** | Very weak | Avoid |

---

## 🎯 Confidence Levels

| Confidence | Meaning | What to Do |
|------------|---------|------------|
| **80-100%** | High confidence | Trust the signal |
| **60-79%** | Moderate | Do extra research |
| **<60%** | Low | System downgrades to HOLD |

---

## ⚠️ Conflict Detection

```
⚠️ CONFLICT DETECTED

What it means:
- Agents disagree (e.g., Technical says SELL, Fundamental says BUY)
- System automatically downgrades to HOLD
- Proceed with extra caution

What to do:
- Review each agent's reasoning
- Understand why they disagree
- Consider waiting for clarity
```

---

## 🔄 Learning Timeline

| Day | Action | Result |
|-----|--------|--------|
| **1** | Make prediction | Tracked automatically |
| **30** | Evaluate | Compare vs actual |
| **31** | Learn | Weights optimized |
| **60+** | Improve | Better predictions |

---

## 📈 Expected Accuracy

| Timeline | Accuracy | Status |
|----------|----------|--------|
| Day 1 | 60% | Baseline |
| Month 1 | 65% | Learning |
| Month 3 | 70% | Improving |
| Month 6 | 78% | Mature |

---

## 💡 Quick Tips

### ✅ Do This
- Use `analyze_with_learning.py` for all queries
- Wait 30 days before evaluating
- Trust high confidence predictions (>70%)
- Follow position sizing recommendations
- Review agent consensus

### ❌ Don't Do This
- Create new .py files for each query
- Manually adjust weights
- Evaluate before 30 days
- Ignore risk management
- Skip conflict warnings

---

## 🎯 Trading Plan Components

Every analysis includes:

```
Entry: ₹468        → Where to buy
Stop Loss: ₹445    → Where to exit if wrong (-5%)
Target 1: ₹503     → First profit level (+7.5%)
Target 2: ₹527     → Second profit level (+12.5%)
Target 3: ₹562     → Third profit level (+20%)
Position: 3.3%     → % of portfolio to allocate
Risk/Reward: 1:2.7 → Risk 1 to make 2.7
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `analyze_with_learning.py` | Main CLI with learning |
| `analyze_stock.py` | Simple CLI without learning |
| `learning_engine.py` | Learning logic |
| `stock_agents/orchestrator.py` | Multi-agent coordination |
| `streamlit_app.py` | Web UI |

---

## 💾 Data Files

| File | Contains |
|------|----------|
| `data/learning/predictions.json` | All predictions |
| `data/learning/accuracy_history.json` | Accuracy over time |
| `data/learning/agent_weights.json` | Optimized weights |

---

## 🔧 Customization

### Change Agent Weights
```python
orchestrator = MultiAgentOrchestrator(weights={
    'technical': 0.40,      # Increase technical
    'fundamental': 0.25,    # Decrease fundamental
    'risk': 0.20,
    'market_context': 0.15
})
```

### Adjust Risk Parameters
```python
# In .env file
DEFAULT_RISK_PER_TRADE=2.0
DEFAULT_POSITION_SIZE=2.5
MAX_POSITION_SIZE=10.0
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "No data found" | Check ticker symbol, add .NS for NSE |
| "Rate limit" | Wait 60 seconds, reduce frequency |
| "Low confidence" | System downgrades to HOLD, do more research |
| "Conflict detected" | Agents disagree, proceed with caution |

---

## 📚 Documentation

| Doc | Purpose |
|-----|---------|
| `README.md` | Main documentation |
| `QUICK_START.md` | Quick guide |
| `SYSTEM_OVERVIEW.md` | Complete overview |
| `LEARNING_SYSTEM.md` | How learning works |
| `FEEDBACK_LOOP.md` | Feedback loop details |

---

## 🎯 One-Liners

```bash
# Analyze
python3 analyze_with_learning.py KPIGREEN

# Evaluate
python3 analyze_with_learning.py --evaluate

# Dashboard
python3 analyze_with_learning.py --dashboard

# Web UI
streamlit run streamlit_app.py
```

---

## ✅ Daily Workflow

```
Morning:
1. Check dashboard
2. Analyze new stocks
3. Review predictions

Monthly:
1. Run evaluation
2. Check accuracy
3. Review learning progress

Quarterly:
1. Review agent weights
2. Check feature importance
3. Validate improvements
```

---

**Keep this handy for quick reference!** 📋✨
