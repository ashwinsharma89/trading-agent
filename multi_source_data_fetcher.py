"""
Multi-Source Data Fetcher
Fetches data from multiple sources with automatic fallback
Priority: TradingView > Yahoo Finance > NSE > BSE
"""

import os
import requests
import yfinance as yf
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class MultiSourceDataFetcher:
    """
    Fetch stock data from multiple sources with automatic fallback
    """
    
    def __init__(self):
        self.tradingview_enabled = bool(os.getenv('TRADINGVIEW_API_KEY'))
        self.sources = ['tradingview', 'yahoo', 'nse', 'bse']
        self.cache = {}
    
    def fetch_stock_data(self, ticker: str, period: str = "1y") -> Optional[Dict[str, Any]]:
        """
        Fetch stock data trying all sources in priority order
        """
        errors = []
        
        for source in self.sources:
            try:
                logger.info(f"Trying {source} for {ticker}")
                
                if source == 'tradingview' and self.tradingview_enabled:
                    data = self._fetch_from_tradingview(ticker, period)
                elif source == 'yahoo':
                    data = self._fetch_from_yahoo(ticker, period)
                elif source == 'nse':
                    data = self._fetch_from_nse(ticker)
                elif source == 'bse':
                    data = self._fetch_from_bse(ticker)
                else:
                    continue
                
                if data:
                    logger.info(f"✅ Successfully fetched from {source}")
                    data['source'] = source
                    data['fetch_time'] = datetime.now()
                    return data
                    
            except Exception as e:
                error_msg = f"{source}: {str(e)}"
                errors.append(error_msg)
                logger.warning(f"Failed to fetch from {source}: {e}")
                continue
        
        logger.error(f"All sources failed for {ticker}: {errors}")
        return None
    
    def _fetch_from_tradingview(self, ticker: str, period: str) -> Optional[Dict[str, Any]]:
        """
        Fetch from TradingView API
        """
        api_key = os.getenv('TRADINGVIEW_API_KEY')
        if not api_key:
            return None
        
        # TradingView API endpoint (example - adjust based on actual API)
        url = f"https://api.tradingview.com/v1/quotes"
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Convert ticker to TradingView format
        tv_ticker = f"NSE:{ticker}"
        
        payload = {
            'symbols': [tv_ticker],
            'fields': ['close', 'high', 'low', 'open', 'volume']
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return self._parse_tradingview_data(data, ticker)
        
        return None
    
    def _parse_tradingview_data(self, raw_data: Dict, ticker: str) -> Dict[str, Any]:
        """
        Parse TradingView API response
        """
        # This is a placeholder - adjust based on actual API response format
        return {
            'ticker': ticker,
            'current_price': raw_data.get('close'),
            'historical': pd.DataFrame(raw_data.get('history', [])),
            'volume': raw_data.get('volume'),
            'source': 'tradingview'
        }
    
    def _fetch_from_yahoo(self, ticker: str, period: str) -> Optional[Dict[str, Any]]:
        """
        Fetch from Yahoo Finance (current implementation)
        """
        try:
            # Add .NS suffix for NSE stocks
            yahoo_ticker = f"{ticker}.NS" if not ticker.endswith('.NS') else ticker
            
            stock = yf.Ticker(yahoo_ticker)
            
            # Get historical data
            hist = stock.history(period=period)
            
            if hist.empty:
                return None
            
            # Get current info
            info = stock.info
            
            return {
                'ticker': ticker,
                'current_price': hist['Close'].iloc[-1],
                'historical': hist,
                'info': info,
                'volume': hist['Volume'].iloc[-1],
                'source': 'yahoo'
            }
            
        except Exception as e:
            logger.error(f"Yahoo Finance error: {e}")
            return None
    
    def _fetch_from_nse(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch from NSE India website
        """
        try:
            # NSE API endpoint
            url = f"https://www.nseindia.com/api/quote-equity?symbol={ticker}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            # NSE requires session with cookies
            session = requests.Session()
            session.get('https://www.nseindia.com', headers=headers)
            
            response = session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_nse_data(data, ticker)
            
            return None
            
        except Exception as e:
            logger.error(f"NSE error: {e}")
            return None
    
    def _parse_nse_data(self, raw_data: Dict, ticker: str) -> Dict[str, Any]:
        """
        Parse NSE API response
        """
        try:
            price_info = raw_data.get('priceInfo', {})
            
            return {
                'ticker': ticker,
                'current_price': price_info.get('lastPrice'),
                'open': price_info.get('open'),
                'high': price_info.get('intraDayHighLow', {}).get('max'),
                'low': price_info.get('intraDayHighLow', {}).get('min'),
                'volume': raw_data.get('totalTradedVolume'),
                'change': price_info.get('change'),
                'change_percent': price_info.get('pChange'),
                'source': 'nse'
            }
        except Exception as e:
            logger.error(f"NSE parsing error: {e}")
            return None
    
    def _fetch_from_bse(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch from BSE India website
        """
        try:
            # BSE API endpoint (example - adjust based on actual API)
            url = f"https://api.bseindia.com/BseIndiaAPI/api/StockReachGraph/w"
            
            params = {
                'scripcode': ticker,
                'flag': '0',
                'fromdate': (datetime.now() - timedelta(days=365)).strftime('%Y%m%d'),
                'todate': datetime.now().strftime('%Y%m%d'),
                'seriesid': ''
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_bse_data(data, ticker)
            
            return None
            
        except Exception as e:
            logger.error(f"BSE error: {e}")
            return None
    
    def _parse_bse_data(self, raw_data: Dict, ticker: str) -> Dict[str, Any]:
        """
        Parse BSE API response
        """
        # Placeholder - adjust based on actual API response
        return {
            'ticker': ticker,
            'current_price': raw_data.get('currentvalue'),
            'source': 'bse'
        }
    
    def fetch_fundamental_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch fundamental data from multiple sources
        """
        # Try Yahoo Finance first (has good fundamental data)
        try:
            yahoo_ticker = f"{ticker}.NS"
            stock = yf.Ticker(yahoo_ticker)
            info = stock.info
            
            if info:
                return {
                    'ticker': ticker,
                    'market_cap': info.get('marketCap'),
                    'pe_ratio': info.get('trailingPE'),
                    'pb_ratio': info.get('priceToBook'),
                    'dividend_yield': info.get('dividendYield'),
                    'roe': info.get('returnOnEquity'),
                    'debt_to_equity': info.get('debtToEquity'),
                    'revenue': info.get('totalRevenue'),
                    'profit_margin': info.get('profitMargins'),
                    'source': 'yahoo'
                }
        except Exception as e:
            logger.error(f"Fundamental data error: {e}")
        
        # Try NSE/BSE as fallback
        # ... implement NSE/BSE fundamental data fetching
        
        return None
    
    def get_data_quality_score(self, data: Dict[str, Any]) -> float:
        """
        Calculate quality score for fetched data
        """
        score = 0.0
        
        # Check completeness
        required_fields = ['ticker', 'current_price']
        optional_fields = ['historical', 'volume', 'info']
        
        for field in required_fields:
            if field in data and data[field] is not None:
                score += 0.3
        
        for field in optional_fields:
            if field in data and data[field] is not None:
                score += 0.1
        
        # Bonus for certain sources
        source_bonus = {
            'tradingview': 0.2,
            'yahoo': 0.15,
            'nse': 0.1,
            'bse': 0.05
        }
        
        score += source_bonus.get(data.get('source', ''), 0)
        
        return min(1.0, score)


if __name__ == "__main__":
    # Test multi-source fetcher
    fetcher = MultiSourceDataFetcher()
    
    print("🔍 Testing Multi-Source Data Fetcher")
    print("="*60)
    
    ticker = "KPIGREEN"
    
    print(f"\nFetching data for {ticker}...")
    data = fetcher.fetch_stock_data(ticker)
    
    if data:
        print(f"✅ Successfully fetched from: {data['source']}")
        print(f"   Current Price: ₹{data['current_price']:.2f}")
        print(f"   Data Quality: {fetcher.get_data_quality_score(data)*100:.0f}%")
    else:
        print("❌ Failed to fetch data from all sources")
