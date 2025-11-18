"""
Enhanced Data Provider with TradingView Paid Account Support
Supports multiple data sources with fallback
"""

import os
from typing import Dict, Optional, List
from datetime import datetime
import time
from tradingview_ta import TA_Handler, Interval, Exchange
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DataProvider:
    """
    Multi-source data provider with paid TradingView support
    """
    
    def __init__(self):
        self.provider = os.getenv("DATA_PROVIDER", "yahoo")
        self.tv_username = os.getenv("TRADINGVIEW_USERNAME")
        self.tv_password = os.getenv("TRADINGVIEW_PASSWORD")
        self.tv_token = os.getenv("TRADINGVIEW_API_TOKEN")
        self.rate_limit = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "2000"))
        self.cache_ttl = int(os.getenv("CACHE_TTL_SECONDS", "60"))
        
        # Request tracking for rate limiting
        self.request_times = []
        self.cache = {}
        
        # Initialize providers (Yahoo Finance always, TradingView as fallback)
        self.yahoo_provider = None
        self.ws_client = None
        
        # Always initialize Yahoo Finance as primary
        try:
            from yahoo_provider import get_yahoo_provider
            self.yahoo_provider = get_yahoo_provider()
            print("✅ Yahoo Finance provider initialized (primary)")
        except Exception as e:
            print(f"⚠️ Yahoo Finance init failed: {e}")
        
        # Initialize TradingView as fallback if configured
        if self.provider == "tradingview" or (self.tv_username and self.tv_password):
            try:
                from tradingview_websocket import get_tradingview_ws
                self.ws_client = get_tradingview_ws(self.tv_username, self.tv_password)
                print("✅ TradingView WebSocket initialized (fallback)")
            except Exception as e:
                print(f"⚠️ TradingView WebSocket init failed: {e}")
    
    def _check_rate_limit(self):
        """Check if we're within rate limits"""
        now = time.time()
        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        if len(self.request_times) >= self.rate_limit:
            # Wait until we can make another request
            sleep_time = 60 - (now - self.request_times[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
                self.request_times = []
        
        self.request_times.append(now)
    
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
    
    def get_live_data(self, symbol: str, exchange: str = "NSE", screener: str = "india") -> Optional[Dict]:
        """
        Get live data for symbol with automatic fallback
        Priority: Yahoo Finance -> TradingView WebSocket -> TradingView REST API
        """
        cache_key = f"{exchange}:{symbol}"
        
        # Check cache first
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        # Try Yahoo Finance first (always, regardless of config)
        if self.yahoo_provider:
            try:
                data = self.yahoo_provider.get_live_data(symbol, exchange)
                if data and data.get('price', 0) > 0:
                    self._set_cache(cache_key, data)
                    return data
            except Exception as e:
                print(f"Yahoo Finance unavailable for {symbol}, trying TradingView...")
        
        # Fallback 1: Try TradingView WebSocket (if available)
        if self.ws_client and self.ws_client.connected:
            try:
                ws_data = self.ws_client.get_price(symbol, exchange)
                if ws_data:
                    formatted_data = self._format_ws_data(symbol, ws_data)
                    self._set_cache(cache_key, formatted_data)
                    return formatted_data
            except Exception as e:
                print(f"TradingView WebSocket unavailable for {symbol}, trying REST API...")
        
        # Fallback 2: TradingView REST API with rate limiting
        self._check_rate_limit()
        
        try:
            handler = TA_Handler(
                symbol=symbol,
                exchange=exchange,
                screener=screener,
                interval=Interval.INTERVAL_1_DAY,
                timeout=15
            )
            analysis = handler.get_analysis()
            
            data = {
                'symbol': symbol,
                'exchange': exchange,
                'price': analysis.indicators.get('close', 0),
                'open': analysis.indicators.get('open', 0),
                'high': analysis.indicators.get('high', 0),
                'low': analysis.indicators.get('low', 0),
                'volume': analysis.indicators.get('volume', 0),
                'change': analysis.indicators.get('change', 0),
                'change_percent': self._calculate_change_percent(
                    analysis.indicators.get('close', 0),
                    analysis.indicators.get('open', 1)
                ),
                'rsi': analysis.indicators.get('RSI', 50),
                'sma_20': analysis.indicators.get('SMA20', 0),
                'sma_50': analysis.indicators.get('SMA50', 0),
                'ema_20': analysis.indicators.get('EMA20', 0),
                'macd': analysis.indicators.get('MACD.macd', 0),
                'macd_signal': analysis.indicators.get('MACD.signal', 0),
                'recommendation': analysis.summary.get('RECOMMENDATION', 'NEUTRAL'),
                'buy_signals': analysis.summary.get('BUY', 0),
                'sell_signals': analysis.summary.get('SELL', 0),
                'neutral_signals': analysis.summary.get('NEUTRAL', 0),
                'timestamp': datetime.now().isoformat(),
                'source': 'tradingview_rest'
            }
            
            self._set_cache(cache_key, data)
            return data
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def _format_ws_data(self, symbol: str, ws_data: Dict) -> Dict:
        """Format WebSocket data to standard format"""
        return {
            'symbol': symbol,
            'price': ws_data.get('lp', 0),  # Last price
            'open': ws_data.get('open_price', 0),
            'high': ws_data.get('high_price', 0),
            'low': ws_data.get('low_price', 0),
            'volume': ws_data.get('volume', 0),
            'change': ws_data.get('ch', 0),
            'change_percent': ws_data.get('chp', 0),
            'timestamp': datetime.now().isoformat(),
            'source': 'tradingview_websocket'
        }
    
    def _calculate_change_percent(self, current: float, previous: float) -> float:
        """Calculate percentage change"""
        if previous and previous != 0:
            return ((current - previous) / previous) * 100
        return 0.0
    
    def get_batch_data(self, symbols: List[str], exchange: str = "NSE") -> Dict[str, Dict]:
        """
        Get data for multiple symbols with automatic fallback
        Priority: Yahoo Finance batch -> Individual fetch with fallback
        """
        # Try Yahoo Finance batch method first
        if self.yahoo_provider:
            try:
                results = self.yahoo_provider.get_batch_data(symbols, exchange)
                # Check if we got data for all symbols
                if len(results) == len(symbols):
                    return results
                # If some symbols missing, fetch them individually with fallback
                missing_symbols = [s for s in symbols if s not in results]
                print(f"Yahoo batch incomplete, fetching {len(missing_symbols)} symbols individually...")
                for symbol in missing_symbols:
                    data = self.get_live_data(symbol, exchange)
                    if data:
                        results[symbol] = data
                return results
            except Exception as e:
                print(f"Yahoo batch fetch error, trying individual fetch: {e}")
        
        # Fallback: Sequential fetching with automatic provider fallback
        results = {}
        for symbol in symbols:
            data = self.get_live_data(symbol, exchange)  # This will try Yahoo -> TradingView
            if data:
                results[symbol] = data
            time.sleep(0.1)
        
        return results
    
    def subscribe_realtime(self, symbols: List[str], exchange: str = "NSE", callback=None):
        """
        Subscribe to real-time updates via WebSocket
        Only available with paid account
        """
        if not self.ws_client:
            print("⚠️ Real-time subscription requires TradingView credentials")
            return False
        
        for symbol in symbols:
            self.ws_client.subscribe(symbol, exchange, callback)
        
        return True
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache = {}
        print("✅ Cache cleared")


# Singleton instance
_provider_instance = None

def get_data_provider() -> DataProvider:
    """Get or create DataProvider instance"""
    global _provider_instance
    
    if _provider_instance is None:
        _provider_instance = DataProvider()
    
    return _provider_instance


if __name__ == "__main__":
    # Test the data provider
    provider = get_data_provider()
    
    print("\n📊 Testing Data Provider\n")
    
    # Test single stock
    data = provider.get_live_data("RELIANCE", "NSE")
    if data:
        print(f"✅ RELIANCE: ₹{data['price']:.2f} ({data['change_percent']:+.2f}%)")
        print(f"   Source: {data['source']}")
    
    # Test batch
    print("\n📦 Batch test:")
    batch = provider.get_batch_data(["TCS", "INFY", "HDFCBANK"])
    for symbol, data in batch.items():
        if data:
            print(f"✅ {symbol}: ₹{data['price']:.2f}")
