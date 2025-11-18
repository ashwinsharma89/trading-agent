# TradingView Paid Account Integration Setup

## 🎯 Benefits of Paid Account Integration

### **Free vs Paid Account**
| Feature | Free (tradingview-ta) | Paid Account |
|---------|----------------------|--------------|
| Rate Limit | ~5-10 req/min | 60+ req/min |
| Real-time Data | No (5min delay) | Yes (WebSocket) |
| Historical Data | Limited | Full access |
| Concurrent Symbols | Limited | Unlimited |
| API Stability | Rate limited | Stable |

## 📋 Setup Instructions

### **Step 1: Create `.env` File**

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### **Step 2: Add Your Credentials**

Edit `.env` and add your TradingView credentials:

```env
# TradingView Account Credentials
TRADINGVIEW_USERNAME=your_email@example.com
TRADINGVIEW_PASSWORD=your_password

# Or use API token if available
TRADINGVIEW_API_TOKEN=your_api_token_here

# Settings (adjust based on your plan)
DATA_PROVIDER=tradingview
RATE_LIMIT_REQUESTS_PER_MINUTE=60
CACHE_TTL_SECONDS=60

# Exchange Settings
DEFAULT_EXCHANGE=NSE
DEFAULT_SCREENER=india
```

### **Step 3: Verify Setup**

Test the connection:
```bash
python data_provider.py
```

Expected output:
```
✅ TradingView WebSocket initialized with paid account
📊 Testing Data Provider
✅ RELIANCE: ₹2850.75 (+1.23%)
   Source: tradingview_websocket
```

### **Step 4: Restart Streamlit**

```bash
streamlit run streamlit_app.py
```

## 🔧 Configuration Options

### **Data Provider Options**

1. **TradingView WebSocket** (Recommended for paid accounts)
   - Real-time streaming data
   - No rate limits
   - Lowest latency
   - Requires credentials

2. **TradingView REST API** (Fallback)
   - Higher rate limits with paid account
   - Cached responses
   - Works without WebSocket

3. **Yahoo Finance** (Alternative)
   - Free, no authentication
   - Good for historical data
   - Limited real-time features

### **Rate Limit Settings**

Adjust based on your TradingView plan:

| Plan | Recommended Setting |
|------|---------------------|
| Free | 5 req/min |
| Essential | 30 req/min |
| Plus | 60 req/min |
| Premium | 120 req/min |

## 🚀 Features Enabled with Paid Account

### **1. Real-time WebSocket Streaming**
```python
from data_provider import get_data_provider

provider = get_data_provider()

# Subscribe to real-time updates
def on_price_update(data):
    print(f"Live update: {data}")

provider.subscribe_realtime(['RELIANCE', 'TCS'], callback=on_price_update)
```

### **2. Batch Data Fetching**
```python
# Fetch multiple stocks efficiently
batch_data = provider.get_batch_data(['RELIANCE', 'TCS', 'INFY', 'HDFCBANK'])
```

### **3. Extended Technical Indicators**
- RSI, MACD, EMA, SMA
- Volume Profile
- Support/Resistance levels
- TradingView recommendations

### **4. No Rate Limit Warnings**
- Smooth operation with 500+ stocks
- No 429 errors
- Faster refresh rates

## 🔒 Security Best Practices

1. **Never commit `.env` file**
   - Already in `.gitignore`
   - Keep credentials private

2. **Use environment variables in production**
   ```bash
   export TRADINGVIEW_USERNAME="your_email"
   export TRADINGVIEW_PASSWORD="your_password"
   ```

3. **Rotate credentials regularly**
   - Change password every 90 days
   - Use strong, unique passwords

## 🐛 Troubleshooting

### **WebSocket Connection Failed**
```
⚠️ WebSocket init failed, using REST API
```
**Solution**: Check credentials in `.env` file

### **Rate Limit Still Hit**
```
HTTP 429: Too Many Requests
```
**Solution**: Increase `RATE_LIMIT_REQUESTS_PER_MINUTE` or reduce watchlist size

### **No Data Returned**
```
Error fetching data for SYMBOL
```
**Solution**: 
- Verify symbol exists on NSE
- Check exchange setting (NSE vs BSE)
- Clear cache: `provider.clear_cache()`

## 📊 Performance Comparison

### **Before (Free API)**
- ❌ Rate limited to 5-10 stocks/min
- ❌ 5-minute delayed data
- ❌ Frequent 429 errors
- ❌ Max 20 stocks in watchlist

### **After (Paid Account)**
- ✅ 60+ stocks/min
- ✅ Real-time streaming data
- ✅ No rate limit errors
- ✅ Unlimited watchlist size
- ✅ WebSocket for instant updates

## 🔗 Additional Resources

- [TradingView API Documentation](https://www.tradingview.com/support/solutions/43000529348-i-want-to-use-the-tradingview-api/)
- [WebSocket Protocol](https://www.tradingview.com/HTML5-stock-forex-bitcoin-charting-library/)
- [Rate Limits by Plan](https://www.tradingview.com/gopro/)

## 📞 Support

If you encounter issues:
1. Check `.env` configuration
2. Test with `python data_provider.py`
3. Review logs in terminal
4. Verify TradingView account is active

---

**Note**: This integration uses unofficial TradingView APIs. For production use, consider TradingView's official charting library or data feed API.
