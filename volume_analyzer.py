"""
Real Volume Analysis
Calculates actual volume metrics from price data
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


class VolumeAnalyzer:
    """
    Analyze volume patterns and calculate volume profile
    """
    
    def __init__(self):
        pass
    
    def analyze(self, df: pd.DataFrame) -> Dict:
        """
        Comprehensive volume analysis
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            Dictionary with volume metrics
        """
        # Ensure proper column names
        df = df.copy()
        df.columns = [col.capitalize() for col in df.columns]
        
        # Calculate volume metrics
        avg_volume = df['Volume'].mean()
        current_volume = df['Volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # Volume trend
        recent_avg = df['Volume'].iloc[-10:].mean()
        older_avg = df['Volume'].iloc[-30:-10].mean() if len(df) > 30 else avg_volume
        volume_trend = "Increasing" if recent_avg > older_avg else "Decreasing"
        
        # Calculate volume profile (price levels with most volume)
        volume_profile = self._calculate_volume_profile(df)
        
        # Buying vs selling pressure
        buying_pressure, selling_pressure = self._calculate_pressure(df)
        
        # Volume gaps
        volume_gaps = self._detect_volume_gaps(df)
        
        # Institutional activity indicator
        institutional_activity = self._detect_institutional_activity(df)
        
        return {
            'avg_volume': avg_volume,
            'current_volume': current_volume,
            'volume_ratio': volume_ratio,
            'volume_trend': volume_trend,
            'volume_profile': volume_profile,
            'buying_pressure': buying_pressure,
            'selling_pressure': selling_pressure,
            'volume_gaps': volume_gaps,
            'institutional_activity': institutional_activity
        }
    
    def _calculate_volume_profile(self, df: pd.DataFrame) -> Dict:
        """
        Calculate volume profile (POC, VAH, VAL)
        """
        # Create price bins
        price_min = df['Low'].min()
        price_max = df['High'].max()
        num_bins = 20
        
        bins = np.linspace(price_min, price_max, num_bins)
        volume_at_price = np.zeros(num_bins - 1)
        
        # Distribute volume across price levels
        for idx, row in df.iterrows():
            candle_range = row['High'] - row['Low']
            if candle_range > 0:
                # Find which bins this candle touches
                for i in range(len(bins) - 1):
                    bin_low = bins[i]
                    bin_high = bins[i + 1]
                    
                    # Check if candle overlaps with this bin
                    if row['Low'] <= bin_high and row['High'] >= bin_low:
                        # Calculate overlap
                        overlap_low = max(row['Low'], bin_low)
                        overlap_high = min(row['High'], bin_high)
                        overlap_ratio = (overlap_high - overlap_low) / candle_range
                        
                        # Add proportional volume
                        volume_at_price[i] += row['Volume'] * overlap_ratio
        
        # Find Point of Control (price with most volume)
        poc_idx = np.argmax(volume_at_price)
        poc_price = (bins[poc_idx] + bins[poc_idx + 1]) / 2
        
        # Calculate Value Area (70% of volume)
        total_volume = volume_at_price.sum()
        target_volume = total_volume * 0.70
        
        # Start from POC and expand
        accumulated_volume = volume_at_price[poc_idx]
        lower_idx = poc_idx
        upper_idx = poc_idx
        
        while accumulated_volume < target_volume and (lower_idx > 0 or upper_idx < len(volume_at_price) - 1):
            # Expand to side with more volume
            lower_vol = volume_at_price[lower_idx - 1] if lower_idx > 0 else 0
            upper_vol = volume_at_price[upper_idx + 1] if upper_idx < len(volume_at_price) - 1 else 0
            
            if lower_vol > upper_vol and lower_idx > 0:
                lower_idx -= 1
                accumulated_volume += lower_vol
            elif upper_idx < len(volume_at_price) - 1:
                upper_idx += 1
                accumulated_volume += upper_vol
            else:
                break
        
        vah = bins[upper_idx + 1]  # Value Area High
        val = bins[lower_idx]      # Value Area Low
        
        # Current price position
        current_price = df['Close'].iloc[-1]
        if current_price > vah:
            position = "Above VA"
        elif current_price < val:
            position = "Below VA"
        else:
            position = "Within VA"
        
        return {
            'poc': poc_price,
            'vah': vah,
            'val': val,
            'current_position': position,
            'volume_distribution': volume_at_price.tolist(),
            'price_bins': bins.tolist()
        }
    
    def _calculate_pressure(self, df: pd.DataFrame) -> Tuple[float, float]:
        """
        Calculate buying vs selling pressure
        """
        # Use candle body and volume
        buying_volume = 0
        selling_volume = 0
        
        for idx, row in df.iterrows():
            if row['Close'] > row['Open']:  # Bullish candle
                buying_volume += row['Volume']
            elif row['Close'] < row['Open']:  # Bearish candle
                selling_volume += row['Volume']
            else:  # Doji
                # Split volume
                buying_volume += row['Volume'] / 2
                selling_volume += row['Volume'] / 2
        
        total_volume = buying_volume + selling_volume
        
        if total_volume > 0:
            buying_pressure = (buying_volume / total_volume) * 100
            selling_pressure = (selling_volume / total_volume) * 100
        else:
            buying_pressure = 50
            selling_pressure = 50
        
        return buying_pressure, selling_pressure
    
    def _detect_volume_gaps(self, df: pd.DataFrame) -> bool:
        """
        Detect if there are significant volume gaps
        """
        avg_volume = df['Volume'].mean()
        
        # Check for candles with very low volume (< 30% of average)
        low_volume_candles = df[df['Volume'] < avg_volume * 0.3]
        
        return len(low_volume_candles) > len(df) * 0.1  # More than 10% of candles
    
    def _detect_institutional_activity(self, df: pd.DataFrame) -> str:
        """
        Detect institutional activity based on volume patterns
        """
        avg_volume = df['Volume'].mean()
        recent_volumes = df['Volume'].iloc[-10:]
        
        # Count high volume days (> 1.5x average)
        high_volume_days = (recent_volumes > avg_volume * 1.5).sum()
        
        # Check for volume spikes with price movement
        recent_df = df.iloc[-10:]
        volume_spikes_with_movement = 0
        
        for idx, row in recent_df.iterrows():
            if row['Volume'] > avg_volume * 1.5:
                price_change = abs(row['Close'] - row['Open']) / row['Open']
                if price_change > 0.02:  # > 2% move
                    volume_spikes_with_movement += 1
        
        if volume_spikes_with_movement >= 3:
            return "High"
        elif high_volume_days >= 4:
            return "Medium"
        else:
            return "Low"


if __name__ == "__main__":
    # Test volume analyzer
    import yfinance as yf
    
    print("\n📊 Testing Volume Analyzer\n")
    
    ticker = yf.Ticker("RELIANCE.NS")
    df = ticker.history(period="3mo", interval="1d")
    
    analyzer = VolumeAnalyzer()
    analysis = analyzer.analyze(df)
    
    print(f"Average Volume: {analysis['avg_volume']:,.0f}")
    print(f"Current Volume: {analysis['current_volume']:,.0f}")
    print(f"Volume Ratio: {analysis['volume_ratio']:.2f}x")
    print(f"Volume Trend: {analysis['volume_trend']}")
    print(f"\nVolume Profile:")
    print(f"  POC: ₹{analysis['volume_profile']['poc']:.2f}")
    print(f"  VAH: ₹{analysis['volume_profile']['vah']:.2f}")
    print(f"  VAL: ₹{analysis['volume_profile']['val']:.2f}")
    print(f"  Position: {analysis['volume_profile']['current_position']}")
    print(f"\nBuying Pressure: {analysis['buying_pressure']:.1f}%")
    print(f"Selling Pressure: {analysis['selling_pressure']:.1f}%")
    print(f"Institutional Activity: {analysis['institutional_activity']}")
