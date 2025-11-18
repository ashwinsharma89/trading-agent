"""
Market Data Fetcher for Dashboard and Screener
Fetches real market data for multiple stocks efficiently
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from yahoo_provider import get_yahoo_provider
from fvg_detector import get_fvg_summary
from smc_analyzer import SMCAnalyzer


class MarketDataFetcher:
    """
    Efficiently fetch market data for multiple stocks
    """
    
    def __init__(self):
        self.yahoo_prov = get_yahoo_provider()
        self.smc_analyzer = SMCAnalyzer()
    
    def fetch_stock_data(self, symbol: str, period: str = "3mo", interval: str = "1d") -> Dict:
        """
        Fetch comprehensive data for a single stock
        """
        try:
            # Get historical data
            df = self.yahoo_prov.get_historical_data(symbol, period=period, interval=interval)
            
            if df is None or df.empty:
                return None
            
            # Ensure proper column names
            df.columns = [col.lower() for col in df.columns]
            
            # Get latest data
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            # Calculate metrics
            change = latest['close'] - prev['close']
            change_pct = (change / prev['close']) * 100 if prev['close'] != 0 else 0
            
            # Volume analysis
            avg_volume = df['volume'].mean()
            volume_ratio = latest['volume'] / avg_volume if avg_volume > 0 else 1
            
            # RSI calculation
            returns = df['close'].pct_change()
            gain = returns.where(returns > 0, 0).rolling(14).mean()
            loss = -returns.where(returns < 0, 0).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1] if not rsi.empty else 50
            
            # FVG analysis
            fvg_summary = get_fvg_summary(symbol, df)
            
            # SMC analysis
            df_smc = df.copy()
            df_smc.columns = [col.capitalize() for col in df_smc.columns]
            smc_analysis = self.smc_analyzer.analyze(df_smc)
            
            # Determine signal
            signal = "HOLD"
            confidence = 50
            
            if smc_analysis['bias']['bias'] == "BULLISH" and current_rsi < 70:
                signal = "BUY"
                confidence = smc_analysis['bias']['confidence']
            elif smc_analysis['bias']['bias'] == "BEARISH" and current_rsi > 30:
                signal = "SELL"
                confidence = smc_analysis['bias']['confidence']
            
            return {
                'symbol': symbol,
                'price': latest['close'],
                'change': change,
                'change_pct': change_pct,
                'volume': latest['volume'],
                'volume_ratio': volume_ratio,
                'rsi': current_rsi,
                'fvg_status': self._get_fvg_status(fvg_summary),
                'active_fvgs': fvg_summary['active_fvgs'],
                'structure': smc_analysis['market_structure']['trend'].capitalize(),
                'signal': signal,
                'confidence': confidence,
                'bias': smc_analysis['bias']['bias'],
                'order_blocks': len(smc_analysis['order_blocks']['bullish']) + len(smc_analysis['order_blocks']['bearish'])
            }
            
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def _get_fvg_status(self, fvg_summary: Dict) -> str:
        """
        Get human-readable FVG status
        """
        if fvg_summary['active_fvgs'] == 0:
            return "No Active FVG"
        
        # Get the strongest FVG
        if fvg_summary['all_active_fvgs']:
            strongest = fvg_summary['all_active_fvgs'][0]
            fvg_type = strongest['type']
            strength = strongest['strength']
            distance = abs(strongest['distance_percent'])
            
            if distance < 2:
                return f"Near {fvg_type} FVG ({strength})"
            else:
                return f"{fvg_type} FVG ({strength})"
        
        return "Active FVG"
    
    def fetch_multiple_stocks(self, symbols: List[str], max_workers: int = 5) -> List[Dict]:
        """
        Fetch data for multiple stocks in parallel
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_symbol = {
                executor.submit(self.fetch_stock_data, symbol): symbol 
                for symbol in symbols
            }
            
            for future in as_completed(future_to_symbol):
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    symbol = future_to_symbol[future]
                    print(f"Error processing {symbol}: {e}")
        
        return results
    
    def get_sector_data(self, sector_stocks: Dict[str, List[str]]) -> Dict:
        """
        Get aggregated data by sector
        """
        sector_data = {}
        
        for sector, stocks in sector_stocks.items():
            # Fetch data for stocks in this sector
            stock_data = self.fetch_multiple_stocks(stocks[:5], max_workers=3)  # Limit to 5 per sector
            
            if stock_data:
                # Calculate sector metrics
                avg_change = np.mean([s['change_pct'] for s in stock_data])
                total_fvgs = sum([s['active_fvgs'] for s in stock_data])
                bullish_count = sum([1 for s in stock_data if s['signal'] == 'BUY'])
                
                # Sector score (0-1)
                score = (bullish_count / len(stock_data)) if stock_data else 0.5
                
                sector_data[sector] = {
                    'score': score,
                    'change': avg_change,
                    'fvg_count': total_fvgs,
                    'bullish_stocks': bullish_count,
                    'total_stocks': len(stock_data)
                }
        
        return sector_data


if __name__ == "__main__":
    # Test market data fetcher
    print("\n📊 Testing Market Data Fetcher\n")
    
    fetcher = MarketDataFetcher()
    
    # Test single stock
    print("Fetching RELIANCE...")
    data = fetcher.fetch_stock_data("RELIANCE", period="3mo", interval="1d")
    
    if data:
        print(f"\nSymbol: {data['symbol']}")
        print(f"Price: ₹{data['price']:.2f}")
        print(f"Change: {data['change_pct']:.2f}%")
        print(f"Volume Ratio: {data['volume_ratio']:.2f}x")
        print(f"RSI: {data['rsi']:.1f}")
        print(f"FVG Status: {data['fvg_status']}")
        print(f"Structure: {data['structure']}")
        print(f"Signal: {data['signal']} ({data['confidence']}%)")
    
    # Test multiple stocks
    print("\n\nFetching multiple stocks...")
    symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK']
    results = fetcher.fetch_multiple_stocks(symbols, max_workers=4)
    
    print(f"\nFetched {len(results)} stocks:")
    for r in results:
        print(f"  {r['symbol']}: ₹{r['price']:.2f} ({r['change_pct']:+.2f}%) - {r['signal']}")
