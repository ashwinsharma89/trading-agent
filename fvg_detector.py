"""
Fair Value Gap (FVG) Detection
Detects and analyzes FVG zones from price data
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class FVGDetector:
    """
    Detects Fair Value Gaps in price data
    """
    
    def __init__(self, min_gap_percent: float = 0.5):
        """
        Initialize FVG detector
        
        Args:
            min_gap_percent: Minimum gap size as percentage of price
        """
        self.min_gap_percent = min_gap_percent
    
    def detect_fvg(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect FVG zones in OHLC data
        
        FVG occurs when:
        - Bullish FVG: candle[i-1].low > candle[i+1].high (gap up)
        - Bearish FVG: candle[i-1].high < candle[i+1].low (gap down)
        
        Args:
            df: DataFrame with OHLC data (columns: Open, High, Low, Close)
        
        Returns:
            List of FVG zones with details
        """
        fvg_zones = []
        
        if len(df) < 3:
            return fvg_zones
        
        # Ensure column names are capitalized
        df = df.copy()
        df.columns = [col.capitalize() for col in df.columns]
        
        for i in range(1, len(df) - 1):
            # Bullish FVG: Previous candle low > Next candle high
            if df.iloc[i-1]['Low'] > df.iloc[i+1]['High']:
                gap_size = df.iloc[i-1]['Low'] - df.iloc[i+1]['High']
                gap_percent = (gap_size / df.iloc[i]['Close']) * 100
                
                if gap_percent >= self.min_gap_percent:
                    fvg_zones.append({
                        'type': 'Bullish',
                        'date': df.index[i],
                        'upper': df.iloc[i-1]['Low'],
                        'lower': df.iloc[i+1]['High'],
                        'gap_size': gap_size,
                        'gap_percent': gap_percent,
                        'filled': False,
                        'fill_date': None,
                        'strength': self._calculate_strength(gap_percent, df.iloc[i]['Volume'], df['Volume'].mean())
                    })
            
            # Bearish FVG: Previous candle high < Next candle low
            elif df.iloc[i-1]['High'] < df.iloc[i+1]['Low']:
                gap_size = df.iloc[i+1]['Low'] - df.iloc[i-1]['High']
                gap_percent = (gap_size / df.iloc[i]['Close']) * 100
                
                if gap_percent >= self.min_gap_percent:
                    fvg_zones.append({
                        'type': 'Bearish',
                        'date': df.index[i],
                        'upper': df.iloc[i+1]['Low'],
                        'lower': df.iloc[i-1]['High'],
                        'gap_size': gap_size,
                        'gap_percent': gap_percent,
                        'filled': False,
                        'fill_date': None,
                        'strength': self._calculate_strength(gap_percent, df.iloc[i]['Volume'], df['Volume'].mean())
                    })
        
        # Check which FVGs have been filled
        for fvg in fvg_zones:
            fvg_index = df.index.get_loc(fvg['date'])
            
            # Check subsequent candles for fill
            for j in range(fvg_index + 1, len(df)):
                if fvg['type'] == 'Bullish':
                    # Filled if price goes back into the gap
                    if df.iloc[j]['Low'] <= fvg['upper']:
                        fvg['filled'] = True
                        fvg['fill_date'] = df.index[j]
                        break
                else:  # Bearish
                    if df.iloc[j]['High'] >= fvg['lower']:
                        fvg['filled'] = True
                        fvg['fill_date'] = df.index[j]
                        break
        
        return fvg_zones
    
    def _calculate_strength(self, gap_percent: float, volume: float, avg_volume: float) -> str:
        """
        Calculate FVG strength based on gap size and volume
        """
        volume_ratio = volume / avg_volume if avg_volume > 0 else 1
        
        # Strong: Large gap + high volume
        if gap_percent > 2.0 and volume_ratio > 1.5:
            return 'Strong'
        # Medium: Moderate gap or volume
        elif gap_percent > 1.0 or volume_ratio > 1.2:
            return 'Medium'
        # Weak: Small gap and normal volume
        else:
            return 'Weak'
    
    def get_active_fvgs(self, fvg_zones: List[Dict], current_price: float, lookback_days: int = 30) -> List[Dict]:
        """
        Get unfilled FVGs within lookback period
        
        Args:
            fvg_zones: List of all detected FVGs
            current_price: Current market price
            lookback_days: Only consider FVGs from last N days
        
        Returns:
            List of active (unfilled) FVGs
        """
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        
        active_fvgs = []
        for fvg in fvg_zones:
            # Skip if filled
            if fvg['filled']:
                continue
            
            # Skip if too old
            if pd.Timestamp(fvg['date']) < cutoff_date:
                continue
            
            # Calculate distance from current price
            if fvg['type'] == 'Bullish':
                distance = ((fvg['lower'] - current_price) / current_price) * 100
            else:
                distance = ((current_price - fvg['upper']) / current_price) * 100
            
            fvg['distance_percent'] = distance
            fvg['days_old'] = (datetime.now() - pd.Timestamp(fvg['date'])).days
            
            active_fvgs.append(fvg)
        
        # Sort by proximity to current price
        active_fvgs.sort(key=lambda x: abs(x['distance_percent']))
        
        return active_fvgs
    
    def get_nearest_fvg(self, fvg_zones: List[Dict], current_price: float) -> Optional[Dict]:
        """
        Get the nearest unfilled FVG to current price
        """
        active_fvgs = self.get_active_fvgs(fvg_zones, current_price)
        
        if active_fvgs:
            return active_fvgs[0]
        return None
    
    def format_fvg_for_display(self, fvg: Dict) -> str:
        """
        Format FVG data for display
        """
        return f"{fvg['type']} FVG: ₹{fvg['lower']:.2f}-{fvg['upper']:.2f} ({fvg['strength']})"


def get_fvg_summary(symbol: str, df: pd.DataFrame) -> Dict:
    """
    Get comprehensive FVG summary for a symbol
    
    Args:
        symbol: Stock symbol
        df: OHLC DataFrame
    
    Returns:
        Dictionary with FVG analysis
    """
    detector = FVGDetector(min_gap_percent=0.3)
    
    # Detect all FVGs
    all_fvgs = detector.detect_fvg(df)
    
    # Get current price
    current_price = df['Close'].iloc[-1] if 'Close' in df.columns else df['close'].iloc[-1]
    
    # Get active FVGs
    active_fvgs = detector.get_active_fvgs(all_fvgs, current_price, lookback_days=30)
    
    # Get nearest FVG
    nearest_fvg = detector.get_nearest_fvg(all_fvgs, current_price)
    
    # Calculate statistics
    total_fvgs = len(all_fvgs)
    filled_fvgs = len([fvg for fvg in all_fvgs if fvg['filled']])
    fill_rate = (filled_fvgs / total_fvgs * 100) if total_fvgs > 0 else 0
    
    bullish_fvgs = len([fvg for fvg in active_fvgs if fvg['type'] == 'Bullish'])
    bearish_fvgs = len([fvg for fvg in active_fvgs if fvg['type'] == 'Bearish'])
    
    return {
        'symbol': symbol,
        'total_fvgs': total_fvgs,
        'active_fvgs': len(active_fvgs),
        'filled_fvgs': filled_fvgs,
        'fill_rate': fill_rate,
        'bullish_active': bullish_fvgs,
        'bearish_active': bearish_fvgs,
        'nearest_fvg': nearest_fvg,
        'all_active_fvgs': active_fvgs[:5],  # Top 5 nearest
        'current_price': current_price
    }


if __name__ == "__main__":
    # Test FVG detection
    import yfinance as yf
    
    print("\n🎯 Testing FVG Detection\n")
    
    # Fetch data
    ticker = yf.Ticker("RELIANCE.NS")
    df = ticker.history(period="3mo", interval="1d")
    
    # Get FVG summary
    summary = get_fvg_summary("RELIANCE", df)
    
    print(f"Symbol: {summary['symbol']}")
    print(f"Total FVGs detected: {summary['total_fvgs']}")
    print(f"Active FVGs: {summary['active_fvgs']}")
    print(f"Fill rate: {summary['fill_rate']:.1f}%")
    print(f"Bullish active: {summary['bullish_active']}")
    print(f"Bearish active: {summary['bearish_active']}")
    
    if summary['nearest_fvg']:
        fvg = summary['nearest_fvg']
        print(f"\nNearest FVG:")
        print(f"  Type: {fvg['type']}")
        print(f"  Range: ₹{fvg['lower']:.2f} - ₹{fvg['upper']:.2f}")
        print(f"  Strength: {fvg['strength']}")
        print(f"  Distance: {fvg['distance_percent']:.2f}%")
        print(f"  Age: {fvg['days_old']} days")
