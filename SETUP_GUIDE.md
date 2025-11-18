# Complete Setup Guide 🚀

## One-Command Setup

```bash
./setup_complete_system.sh
```

This single script sets up everything:
- ✅ PostgreSQL database
- ✅ Automated scheduler
- ✅ Multi-source data fetcher
- ✅ Quick start scripts

---

## What Gets Installed

### 1. Database (PostgreSQL)
- Creates `trading_framework` database
- 8 tables for predictions, learning, patterns
- Indexed for fast queries
- Replaces JSON files

### 2. Automation
- Daily evaluation (6 PM)
- Weekly retraining (Sunday 8 PM)
- Market open/close updates
- Runs automatically in background

### 3. Multi-Source Data
- TradingView API (best)
- Yahoo Finance (free)
- NSE India (official)
- BSE India (fallback)
- Automatic fallback if one fails

---

## Step-by-Step Setup

### Step 1: Run Setup Script
```bash
cd enterprise_trading_framework
./setup_complete_system.sh
```

**What it does:**
1. Checks prerequisites (Python, PostgreSQL)
2. Installs Python packages
3. Creates .env file
4. Sets up database
5. Configures automation
6. Tests data fetcher
7. Creates quick start scripts

**Time:** 5-10 minutes

---

### Step 2: Configure API Keys

Edit `.env` file:
```bash
nano .env
```

Add your keys:
```
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
TRADINGVIEW_API_KEY=your-key-here  # Optional
```

**Required:**
- OPENAI_API_KEY (for AI analysis)

**Optional:**
- ANTHROPIC_API_KEY (for Claude Vision)
- TRADINGVIEW_API_KEY (for best data)

---

### Step 3: Test the System

```bash
# Analyze a stock
./analyze.sh KPIGREEN

# View learning dashboard
./dashboard.sh

# Run evaluation manually
./evaluate.sh
```

---

## Quick Start Scripts

After setup, you get these commands:

### `./analyze.sh TICKER`
Analyze any stock with full multi-agent system
```bash
./analyze.sh KPIGREEN
./analyze.sh RELIANCE
./analyze.sh TCS
```

### `./dashboard.sh`
View learning progress and statistics
```bash
./dashboard.sh
```

### `./evaluate.sh`
Manually run prediction evaluation
```bash
./evaluate.sh
```

### `./start_daemon.sh`
Start automation daemon (runs in background)
```bash
./start_daemon.sh
```

---

## Verify Setup

### Check Database
```bash
psql -l | grep trading_framework
# Should show: trading_framework database
```

### Check Tables
```bash
psql trading_framework -c "\dt"
# Should show: 8 tables
```

### Check Automation (macOS)
```bash
launchctl list | grep trading
# Should show: com.trading.daily-evaluation
```

### Check Automation (Linux)
```bash
crontab -l
# Should show: Trading Framework jobs
```

### Check Data Fetcher
```bash
python3 multi_source_data_fetcher.py
# Should test all sources
```

---

## Troubleshooting

### PostgreSQL Not Found
```bash
# macOS
brew install postgresql
brew services start postgresql

# Linux
sudo apt install postgresql
sudo systemctl start postgresql
```

### Database Connection Error
```bash
# Check PostgreSQL is running
pg_isready

# Recreate database
dropdb trading_framework
createdb trading_framework
python3 setup_database.py
```

### Automation Not Running
```bash
# macOS - Reload jobs
launchctl unload ~/Library/LaunchAgents/com.trading.*.plist
launchctl load ~/Library/LaunchAgents/com.trading.*.plist

# Linux - Edit crontab
crontab -e
```

### Data Fetching Fails
```bash
# Test each source
python3 -c "
from multi_source_data_fetcher import MultiSourceDataFetcher
fetcher = MultiSourceDataFetcher()
data = fetcher.fetch_stock_data('RELIANCE')
print(f'Source: {data[\"source\"]}')
"
```

---

## What Happens After Setup

### Day 1: You Analyze a Stock
```bash
./analyze.sh KPIGREEN
```
**System:**
- Fetches data from best source
- Runs 4 agents + multimodal analysis
- Saves prediction to PostgreSQL
- Schedules evaluation for Day 31

### Day 31: Automatic Evaluation (6 PM)
**System automatically:**
- Checks predictions 30+ days old
- Fetches current prices
- Compares predicted vs actual
- Calculates accuracy
- Updates database

### Sunday 8 PM: Automatic Retraining
**System automatically:**
- Analyzes agent performance
- Optimizes weights
- Updates database
- Improves future predictions

### Every Day: Data Updates
**System automatically:**
- 9:30 AM: Refresh watchlist
- 3:45 PM: End of day update
- Hourly: Cache cleanup

---

## File Structure After Setup

```
enterprise_trading_framework/
├── database/
│   ├── models.py              ✅ 8 database models
│   ├── connection.py          ✅ Connection manager
│   └── __init__.py
│
├── automation/
│   ├── scheduler.py           ✅ 5 scheduled jobs
│   └── __init__.py
│
├── logs/
│   ├── evaluation.log         ✅ Daily logs
│   ├── retraining.log         ✅ Weekly logs
│   └── *.error.log
│
├── multi_source_data_fetcher.py  ✅ Data fetcher
├── setup_complete_system.sh      ✅ Master setup
├── analyze.sh                    ✅ Quick analyze
├── dashboard.sh                  ✅ Quick dashboard
├── evaluate.sh                   ✅ Quick evaluate
├── start_daemon.sh               ✅ Start daemon
└── .env                          ✅ Configuration
```

---

## Configuration Options

### `.env` File

```bash
# Database
DATABASE_URL=postgresql://localhost/trading_framework

# API Keys
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
TRADINGVIEW_API_KEY=your_key

# Trading Parameters
DEFAULT_RISK_PER_TRADE=2.0        # Risk per trade (%)
DEFAULT_POSITION_SIZE=2.5         # Default position (%)
MAX_POSITION_SIZE=10.0            # Max position (%)

# Learning Parameters
EVALUATION_PERIOD_DAYS=30         # Days before evaluation
RETRAINING_THRESHOLD=70           # Retrain if accuracy < 70%
MIN_PREDICTIONS_FOR_RETRAINING=10 # Min predictions needed
```

---

## Usage Examples

### Example 1: Analyze Stock
```bash
./analyze.sh KPIGREEN

# Output:
# 🔍 ADVANCED ANALYSIS: KPIGREEN
# ✅ Data fetched from: yahoo
# 🤖 Technical: 36/100 (SELL)
# 🤖 Fundamental: 68/100 (BUY)
# 🎯 RECOMMENDATION: HOLD
# 💾 Saved to database (ID: 123)
```

### Example 2: View Dashboard
```bash
./dashboard.sh

# Output:
# 📊 LEARNING DASHBOARD
# Total Predictions: 50
# Evaluated: 20
# Accuracy: 75%
# Agent Performance:
#   Technical: 70%
#   Fundamental: 82%
#   Risk: 75%
```

### Example 3: Manual Evaluation
```bash
./evaluate.sh

# Output:
# 🔍 EVALUATING PREDICTIONS
# Found 5 predictions ready for evaluation
# Evaluating KPIGREEN... ✅ Correct
# Evaluating RELIANCE... ❌ Incorrect
# Overall accuracy: 75%
```

---

## Next Steps

1. ✅ **Run setup**: `./setup_complete_system.sh`
2. ✅ **Add API keys**: Edit `.env`
3. ✅ **Test system**: `./analyze.sh KPIGREEN`
4. ✅ **Let it learn**: System improves automatically

---

## Support

**Check logs:**
```bash
tail -f logs/evaluation.log
tail -f logs/retraining.log
```

**Database queries:**
```bash
psql trading_framework
SELECT COUNT(*) FROM predictions;
SELECT * FROM agent_accuracy ORDER BY timestamp DESC LIMIT 5;
```

**Manual commands:**
```bash
# Analyze
python3 analyze_with_learning.py KPIGREEN

# Evaluate
python3 automation/scheduler.py --run-now evaluation

# Dashboard
python3 analyze_with_learning.py --dashboard

# Daemon
python3 automation/scheduler.py --daemon
```

---

**Everything is ready! Just run `./setup_complete_system.sh` to begin!** 🚀
