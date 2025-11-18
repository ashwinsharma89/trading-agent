"""
Yahoo Finance Data Provider
Free, reliable data source for Indian stocks
"""

import yfinance as yf
from yahooquery import Ticker
from typing import Dict, Optional, List
from datetime import datetime
import time
import pandas as pd


class YahooFinanceProvider:
    """
    Yahoo Finance data provider for NSE/BSE stocks
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 60  # 60 seconds
    
    def _get_nse_symbol(self, symbol: str) -> str:
        """Convert symbol to Yahoo Finance NSE format"""
        # Yahoo Finance uses .NS suffix for NSE stocks
        if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
            return f"{symbol}.NS"
        return symbol
    
    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get data from cache if not expired"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return data
        return None
    
    def _set_cache(self, key: str, data: Dict):
        """Store data in cache"""
        self.cache[key] = (data, time.time())
    
    def get_live_data(self, symbol: str, exchange: str = "NSE") -> Optional[Dict]:
        """
        Get live data for symbol using Yahoo Finance
        """
        cache_key = f"{exchange}:{symbol}"
        
        # Check cache first
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        try:
            # Convert to Yahoo Finance format
            yf_symbol = self._get_nse_symbol(symbol)
            
            # Fetch data using yfinance
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            hist = ticker.history(period="5d")
            
            if hist.empty:
                return None
            
            # Get latest data
            latest = hist.iloc[-1]
            previous = hist.iloc[-2] if len(hist) > 1 else latest
            
            # Calculate technical indicators
            rsi = self._calculate_rsi(hist['Close'])
            sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1] if len(hist) >= 20 else latest['Close']
            sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1] if len(hist) >= 50 else latest['Close']
            
            # Format data
            current_price = latest['Close']
            open_price = latest['Open']
            change = current_price - previous['Close']
            change_percent = (change / previous['Close']) * 100 if previous['Close'] != 0 else 0
            
            data = {
                'symbol': symbol,
                'exchange': exchange,
                'price': float(current_price),
                'open': float(open_price),
                'high': float(latest['High']),
                'low': float(latest['Low']),
                'volume': int(latest['Volume']),
                'change': float(change),
                'change_percent': float(change_percent),
                'rsi': float(rsi),
                'sma_20': float(sma_20),
                'sma_50': float(sma_50),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'recommendation': self._get_recommendation(rsi, current_price, sma_20, sma_50),
                'timestamp': datetime.now().isoformat(),
                'source': 'yahoo_finance'
            }
            
            self._set_cache(cache_key, data)
            return data
            
        except Exception as e:
            print(f"Error fetching Yahoo Finance data for {symbol}: {e}")
            return None
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI indicator"""
        try:
            if len(prices) < period + 1:
                return 50.0
            
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
        except:
            return 50.0
    
    def _get_recommendation(self, rsi: float, price: float, sma_20: float, sma_50: float) -> str:
        """Generate recommendation based on indicators"""
        signals = []
        
        # RSI signals
        if rsi < 30:
            signals.append('BUY')
        elif rsi > 70:
            signals.append('SELL')
        else:
            signals.append('NEUTRAL')
        
        # Moving average signals
        if price > sma_20 and price > sma_50:
            signals.append('BUY')
        elif price < sma_20 and price < sma_50:
            signals.append('SELL')
        else:
            signals.append('NEUTRAL')
        
        # Aggregate signals
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')
        
        if buy_count > sell_count:
            return 'BUY' if buy_count >= 2 else 'NEUTRAL'
        elif sell_count > buy_count:
            return 'SELL' if sell_count >= 2 else 'NEUTRAL'
        else:
            return 'NEUTRAL'
    
    def get_batch_data(self, symbols: List[str], exchange: str = "NSE") -> Dict[str, Dict]:
        """
        Get data for multiple symbols
        """
        results = {}
        
        for symbol in symbols:
            data = self.get_live_data(symbol, exchange)
            if data:
                results[symbol] = data
            
            # Small delay to be respectful
            time.sleep(0.1)
        
        return results
    
    def get_historical_data(self, symbol: str, period: str = "1mo", interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Get historical data for symbol
        """
        try:
            yf_symbol = self._get_nse_symbol(symbol)
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period=period, interval=interval)
            return hist
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache = {}
        print("✅ Yahoo Finance cache cleared")


# Singleton instance
_yahoo_provider = None

def get_yahoo_provider() -> YahooFinanceProvider:
    """Get or create Yahoo Finance provider instance"""
    global _yahoo_provider
    
    if _yahoo_provider is None:
        _yahoo_provider = YahooFinanceProvider()
    
    return _yahoo_provider


if __name__ == "__main__":
    # Test Yahoo Finance provider
    provider = get_yahoo_provider()
    
    print("\n📊 Testing Yahoo Finance Provider\n")
    
    # Test single stock
    data = provider.get_live_data("RELIANCE", "NSE")
    if data:
        print(f"✅ RELIANCE: ₹{data['price']:.2f} ({data['change_percent']:+.2f}%)")
        print(f"   RSI: {data['rsi']:.1f}")
        print(f"   Recommendation: {data['recommendation']}")
        print(f"   Source: {data['source']}")
    
    # Test batch
    print("\n📦 Batch test:")
    batch = provider.get_batch_data(["TCS", "INFY", "HDFCBANK"])
    for symbol, data in batch.items():
        if data:
            print(f"✅ {symbol}: ₹{data['price']:.2f} ({data['change_percent']:+.2f}%)")
