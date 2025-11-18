# Enterprise Stock Trading Framework

Multi-agent AI system for Indian stock market analysis using Smart Money Concepts and fundamental analysis.

---

## 🚀 Quick Start

### Analyze a Stock
```bash
python3 analyze_stock.py KPIGREEN
python3 analyze_stock.py RECLTD swing
python3 analyze_stock.py TCS long_term
```

### Run Streamlit UI
```bash
streamlit run streamlit_app.py
```

---

## 🏗️ Architecture

### Multi-Agent System
- **Technical Agent** (35%) - RSI, volume, Smart Money Concepts
- **Fundamental Agent** (30%) - ROE, growth, valuation, quality
- **Risk Agent** (20%) - Position sizing, stop loss, R:R
- **Market Context Agent** (15%) - Market regime, sector, timing
- **Orchestrator** - LangGraph coordination, conflict resolution

### Key Features
✅ 5 specialized agents with weighted scoring  
✅ LangGraph state machine orchestration  
✅ Automatic conflict detection & resolution  
✅ Risk-adjusted position sizing  
✅ Multi-target profit levels  
✅ Natural language query support  
✅ Real-time data from Yahoo Finance  

---

## 📁 Project Structure

```
enterprise_trading_framework/
├── analyze_stock.py              # CLI for stock analysis
├── stock_agents/                 # Multi-agent system
│   ├── base_agent.py
│   ├── technical_agent.py
│   ├── fundamental_agent.py
│   ├── risk_agent.py
│   ├── market_context_agent.py
│   └── orchestrator.py
├── market_data_fetcher.py        # Yahoo Finance data
├── fundamental_analyzer.py       # Fundamental metrics
├── smc_analyzer.py               # Smart Money Concepts
├── fvg_detector.py               # Fair Value Gaps
├── streamlit_app.py              # Web UI
├── nlp_query_handler.py          # Natural language queries
└── *_testing_system.py           # Validation systems
```

---

## 📊 Example Output

```
🎯 RECOMMENDATION: HOLD
   Composite Score: 56/100
   Confidence: 69%
   Risk Level: MEDIUM

💰 TRADING PLAN:
   Entry: ₹468.45
   Stop Loss: ₹445.03 (-5.0%)
   Target 1: ₹503.58
   Target 2: ₹527.01
   Target 3: ₹562.14
   Position Size: 3.3% of portfolio
   Risk/Reward: 1:2.7

🤖 AGENT CONSENSUS:
   • Technical: SELL (36/100)
   • Fundamental: BUY (68/100)
   • Risk: ACCEPTABLE (70/100)
   • Market_Context: NEUTRAL (60/100)

   ⚠️ CONFLICT DETECTED - Agents disagree, proceed with caution
```

---

## 🔧 Installation

```bash
# Install dependencies
pip3 install -r requirements.txt

# Verify installation
python3 verify_installation.py
```

---

## 📚 Documentation

- **[Multi-Agent Architecture](MULTI_AGENT_ARCHITECTURE.md)** - System design & flow
- **[Natural Language Queries](NATURAL_LANGUAGE_QUERIES.md)** - NLP features
- **[TradingView Setup](TRADINGVIEW_SETUP.md)** - TradingView integration

---

## 🎯 Use Cases

### Swing Trading (2-6 weeks)
```bash
python3 analyze_stock.py KPIGREEN swing
```

### Long-term Investment (2-5 years)
```bash
python3 analyze_stock.py TCS long_term
```

### Natural Language Queries
```python
# In Streamlit UI
"Find stocks with ROE > 20% and revenue growth > 30%"
"Show me undervalued stocks in IT sector"
"Which stocks are near support levels?"
```

---

## ⚙️ Configuration

Edit `.env` file:
```bash
# Data Provider
DATA_PROVIDER=yahoo
RATE_LIMIT_REQUESTS_PER_MINUTE=2000

# Risk Settings
DEFAULT_RISK_PER_TRADE=2.0
DEFAULT_POSITION_SIZE=2.5
MAX_POSITION_SIZE=10.0
```

---

## 🧪 Testing

Run validation systems:
```bash
# Test multi-agent coordination
python3 multi_agent_testing_system.py

# Test backtesting engine
python3 backtesting_validation_system.py

# Test signal generation
python3 signal_generation_logic_system.py
```

---

## 📈 Performance

- **Analysis Time:** ~2-3 seconds per stock
- **Accuracy:** Validated against historical data
- **Data Source:** Yahoo Finance (real-time)
- **Coverage:** NSE/BSE Indian stocks

---

## 🔒 Risk Disclaimer

This system is for educational and research purposes. Always:
- Do your own research
- Consult a financial advisor
- Never invest more than you can afford to lose
- Past performance ≠ future results

---

## 📝 License

MIT License - See LICENSE file

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📧 Support

For issues or questions, open a GitHub issue.

---

**Built with ❤️ for Indian stock market traders**
