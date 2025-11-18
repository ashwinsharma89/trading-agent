# Learning System Architecture

## 🧠 How the System Learns

The multi-agent system learns through **continuous feedback loops** that track predictions vs actual outcomes and automatically improve over time.

---

## 🔄 Learning Flow

```
Make Prediction → Track → Wait 30+ Days → Evaluate → Learn → Improve
     ↓              ↓           ↓            ↓         ↓        ↓
  Save to DB    Monitor     Check Price   Compare   Retrain  Better
                            Movement      Accuracy   Models   Predictions
```

---

## 📊 3-Stage Learning Process

### **Stage 1: Prediction Tracking**

Every time the system analyzes a stock, it saves:

```python
{
    "prediction_id": "uuid",
    "timestamp": "2025-11-17T12:00:00",
    "ticker": "KPIGREEN",
    "recommendation": "BUY",
    "entry_price": 468.45,
    "predicted_targets": [503.58, 527.01, 562.14],
    "stop_loss": 445.03,
    "composite_score": 56,
    "confidence": 69,
    "agent_scores": {
        "technical": 36,
        "fundamental": 68,
        "risk": 70,
        "market_context": 60
    },
    "features": {
        "rsi": 19.7,
        "roe": 17.3,
        "revenue_growth": 76.4,
        # ... 20+ features
    },
    "evaluation_date": "2025-12-17",  # 30 days later
    "evaluated": false
}
```

**Stored in:** PostgreSQL `predictions` table

---

### **Stage 2: Outcome Evaluation**

After 30+ days, the system automatically:

1. **Fetches Current Price**
   ```python
   current_price = fetch_price("KPIGREEN")  # e.g., 520
   entry_price = 468.45
   actual_return = (520 - 468.45) / 468.45 * 100  # +11%
   ```

2. **Compares vs Prediction**
   ```python
   predicted_return = 7.5%  # Based on composite score
   actual_return = 11%
   error = abs(11 - 7.5) / 7.5 = 47%  # Error margin
   ```

3. **Evaluates Each Agent**
   ```python
   # Technical Agent predicted SELL (36/100)
   # But stock went UP 11%
   # → Technical Agent was WRONG
   
   # Fundamental Agent predicted BUY (68/100)
   # Stock went UP 11%
   # → Fundamental Agent was RIGHT
   ```

4. **Calculates Accuracy**
   ```python
   if error < 20%:
       prediction_correct = True
   else:
       prediction_correct = False
   
   # Track per-agent accuracy
   technical_accuracy = correct / total
   fundamental_accuracy = correct / total
   ```

---

### **Stage 3: Model Retraining**

When accuracy drops below 70%, the system automatically retrains:

#### **A. Update Agent Weights**

```python
# Current weights
weights = {
    'technical': 0.35,
    'fundamental': 0.30,
    'risk': 0.20,
    'market_context': 0.15
}

# If fundamental agent is more accurate:
# Increase its weight, decrease technical weight

new_weights = optimize_weights(historical_accuracy)
# Result:
# {
#     'technical': 0.30,      # Decreased
#     'fundamental': 0.35,    # Increased
#     'risk': 0.20,
#     'market_context': 0.15
# }
```

#### **B. Retrain ML Models**

For each agent that uses ML (Technical, Fundamental):

```python
# Collect training data from evaluated predictions
training_data = []
for prediction in evaluated_predictions:
    features = prediction['features']
    actual_outcome = prediction['actual_return']
    training_data.append((features, actual_outcome))

# Retrain Gradient Boosting model
model.fit(X_train, y_train)

# Validate improvement
new_accuracy = model.score(X_test, y_test)
if new_accuracy > old_accuracy:
    save_model()  # Keep improved model
else:
    rollback()    # Revert to old model
```

#### **C. Update Scoring Logic**

```python
# If RSI < 30 predictions were often wrong:
# Reduce RSI weight in technical scoring

# Before
rsi_weight = 20  # Out of 100

# After learning
if rsi_predictions_accuracy < 60%:
    rsi_weight = 10  # Reduce weight
    volume_weight = 25  # Increase other factors
```

---

## 🎯 What Gets Learned

### 1. **Agent Weight Optimization**
- Which agent is most accurate?
- Automatically adjust weights
- Example: If fundamental > technical, increase fundamental weight

### 2. **Feature Importance**
- Which metrics matter most?
- RSI vs Volume vs ROE?
- Automatically prioritize accurate features

### 3. **Market Regime Patterns**
- Bull market: Technical signals work better
- Bear market: Fundamental signals work better
- Sideways: Risk management matters most

### 4. **Sector-Specific Learning**
- IT stocks: Technical analysis more reliable
- Banking: Fundamental analysis more reliable
- Auto: Market context matters more

### 5. **Timeframe Optimization**
- Short-term (swing): Technical weight ↑
- Long-term (investment): Fundamental weight ↑

### 6. **Error Pattern Recognition**
- Consistently overestimate growth? → Reduce growth multiplier
- Underestimate risk? → Increase stop loss %
- Miss breakouts? → Adjust volume thresholds

---

## 📈 Learning Metrics Tracked

### Per-Agent Accuracy
```python
{
    "technical_agent": {
        "total_predictions": 100,
        "correct": 65,
        "accuracy": 65%,
        "avg_error": 15%,
        "best_conditions": "high_volume_breakouts",
        "worst_conditions": "low_volume_sideways"
    },
    "fundamental_agent": {
        "total_predictions": 100,
        "correct": 78,
        "accuracy": 78%,
        "avg_error": 12%,
        "best_conditions": "quality_stocks",
        "worst_conditions": "high_debt_companies"
    }
}
```

### Overall System Accuracy
```python
{
    "total_predictions": 500,
    "evaluated": 200,
    "correct": 145,
    "accuracy": 72.5%,
    "improvement_over_time": +5%,  # vs initial
    "learning_iterations": 3
}
```

### Feature Importance Evolution
```python
# Iteration 1 (Initial)
feature_importance = {
    "revenue_growth": 52%,
    "quality_score": 46%,
    "rsi": 2%
}

# Iteration 3 (After learning)
feature_importance = {
    "revenue_growth": 45%,  # Decreased (overweighted)
    "quality_score": 38%,   # Decreased
    "rsi": 8%,              # Increased (underweighted)
    "volume_ratio": 9%      # New important feature
}
```

---

## 🔧 Implementation

### 1. **Prediction Tracking** (Already Built)

```python
from stock_agents.orchestrator import MultiAgentOrchestrator

orchestrator = MultiAgentOrchestrator()

# Analyze and track
analysis = orchestrator.analyze('KPIGREEN')

# Save to database
save_prediction(
    ticker='KPIGREEN',
    analysis=analysis,
    evaluation_date=datetime.now() + timedelta(days=30)
)
```

### 2. **Automated Evaluation** (Cron Job)

```python
# Run daily
def evaluate_predictions():
    """
    Check all predictions that are 30+ days old
    """
    predictions = get_unevaluated_predictions()
    
    for pred in predictions:
        if days_since(pred.timestamp) >= 30:
            # Fetch current price
            current = fetch_price(pred.ticker)
            
            # Calculate accuracy
            accuracy = calculate_accuracy(pred, current)
            
            # Update database
            update_prediction(pred.id, {
                'evaluated': True,
                'actual_price': current,
                'accuracy': accuracy
            })
    
    # Check if retraining needed
    overall_accuracy = calculate_overall_accuracy()
    if overall_accuracy < 70%:
        trigger_retraining()
```

### 3. **Automatic Retraining**

```python
def trigger_retraining():
    """
    Retrain models when accuracy drops
    """
    # Get evaluated predictions
    training_data = get_evaluated_predictions()
    
    # Optimize agent weights
    new_weights = optimize_weights(training_data)
    
    # Retrain ML models
    for agent in ['technical', 'fundamental']:
        retrain_agent_model(agent, training_data)
    
    # Update orchestrator
    orchestrator.update_weights(new_weights)
    
    # Log improvement
    log_learning_iteration({
        'timestamp': datetime.now(),
        'new_weights': new_weights,
        'accuracy_before': old_accuracy,
        'accuracy_after': new_accuracy
    })
```

---

## 📊 Learning Dashboard

Track learning progress in real-time:

```
╔════════════════════════════════════════════════════════╗
║           LEARNING SYSTEM DASHBOARD                    ║
╚════════════════════════════════════════════════════════╝

📈 Overall Performance
   Accuracy: 72.5% (↑ 5% from initial)
   Total Predictions: 500
   Evaluated: 200
   Learning Iterations: 3

🤖 Agent Performance
   Technical:     65% accuracy (↓ weight to 30%)
   Fundamental:   78% accuracy (↑ weight to 35%)
   Risk:          70% accuracy (→ weight 20%)
   Market:        68% accuracy (→ weight 15%)

🎯 Recent Improvements
   ✅ Reduced overestimation of growth stocks
   ✅ Better risk assessment for high-debt companies
   ✅ Improved volume breakout detection
   ⚠️  Still struggling with sideways markets

📊 Feature Importance Changes
   Revenue Growth: 52% → 45% (overweighted)
   Quality Score:  46% → 38% (overweighted)
   RSI:            2% → 8%   (underweighted)
   Volume:         0% → 9%   (newly important)

🔄 Next Evaluation: 15 predictions in 5 days
```

---

## 🚀 Advanced Learning Features

### 1. **Market Regime Detection**
```python
# Learn which agent works best in different markets
if market_regime == 'BULL':
    weights = {'technical': 0.40, 'fundamental': 0.25, ...}
elif market_regime == 'BEAR':
    weights = {'technical': 0.25, 'fundamental': 0.40, ...}
```

### 2. **Sector-Specific Models**
```python
# Train separate models per sector
models = {
    'IT': TechnicalAgent(weight=0.40),
    'Banking': FundamentalAgent(weight=0.40),
    'Auto': MarketContextAgent(weight=0.25)
}
```

### 3. **Confidence Calibration**
```python
# Learn to be more/less confident
if overconfident:
    reduce_confidence_scores()
if underconfident:
    increase_confidence_scores()
```

### 4. **Human Feedback Loop**
```python
# User can mark predictions as correct/incorrect
user_feedback = get_user_feedback()
incorporate_feedback(user_feedback)
```

---

## ⏱️ Learning Timeline

```
Day 1:     Make 10 predictions
Day 30:    Evaluate first 10 predictions
           Accuracy: 60% (baseline)

Day 60:    Evaluate next 20 predictions
           Accuracy: 65% (↑5%)
           Trigger retraining

Day 90:    Evaluate next 30 predictions
           Accuracy: 72% (↑7%)
           Weights optimized

Day 180:   Evaluate 100+ predictions
           Accuracy: 78% (↑18%)
           Models significantly improved
```

---

## 🎯 Expected Improvements

| Metric | Initial | After 6 Months | Improvement |
|--------|---------|----------------|-------------|
| **Accuracy** | 60% | 78% | +30% |
| **Avg Error** | 25% | 12% | -52% |
| **Confidence Calibration** | Poor | Good | ✅ |
| **Agent Weights** | Generic | Optimized | ✅ |
| **Feature Importance** | Guessed | Data-driven | ✅ |

---

## ✅ Summary

**The system learns by:**

1. ✅ **Tracking** every prediction with timestamp
2. ✅ **Evaluating** outcomes after 30+ days
3. ✅ **Calculating** accuracy per agent
4. ✅ **Retraining** models when accuracy drops
5. ✅ **Optimizing** agent weights based on performance
6. ✅ **Updating** feature importance
7. ✅ **Adapting** to market regimes
8. ✅ **Improving** continuously over time

**Result:** A self-improving system that gets smarter with every prediction! 🧠✨
