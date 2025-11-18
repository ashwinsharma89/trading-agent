"""
Advanced Double Top/Bottom Detector
Works across multiple timeframes (daily, weekly, monthly)
"""

import numpy as np
from scipy.signal import find_peaks, argrelextrema
from scipy.stats import pearsonr
from typing import List, Dict, Tuple, Optional
import pandas as pd
from datetime import datetime, timedelta


class DoublePatternDetector:
    """
    Specialized detector for double tops and double bottoms
    Optimized for daily, weekly, and monthly timeframes
    """
    
    def __init__(self):
        # Timeframe-specific parameters
        self.params = {
            'daily': {
                'min_distance': 5,      # Days between peaks
                'max_distance': 60,     # Max 2 months
                'height_tolerance': 0.02,  # 2% difference
                'valley_depth': 0.03,   # 3% minimum depth
                'confirmation_days': 3   # Days to confirm breakdown
            },
            'weekly': {
                'min_distance': 2,      # Weeks
                'max_distance': 26,     # Max 6 months
                'height_tolerance': 0.025,
                'valley_depth': 0.04,
                'confirmation_days': 1
            },
            'monthly': {
                'min_distance': 1,      # Months
                'max_distance': 12,     # Max 1 year
                'height_tolerance': 0.03,
                'valley_depth': 0.05,
                'confirmation_days': 1
            }
        }
    
    def detect_double_tops(self, prices: np.ndarray, dates: List[str], 
                          timeframe: str = 'daily') -> List[Dict]:
        """
        Detect double top patterns
        
        Args:
            prices: Price array
            dates: Date array
            timeframe: 'daily', 'weekly', or 'monthly'
        """
        if timeframe not in self.params:
            raise ValueError(f"Invalid timeframe: {timeframe}")
        
        params = self.params[timeframe]
        patterns = []
        
        # Find peaks
        peaks, properties = find_peaks(
            prices,
            distance=params['min_distance'],
            prominence=prices.std() * 0.5
        )
        
        if len(peaks) < 2:
            return patterns
        
        # Check each pair of peaks
        for i in range(len(peaks) - 1):
            for j in range(i + 1, len(peaks)):
                peak1_idx = peaks[i]
                peak2_idx = peaks[j]
                
                # Check distance constraint
                distance = peak2_idx - peak1_idx
                if distance < params['min_distance'] or distance > params['max_distance']:
                    continue
                
                peak1_price = prices[peak1_idx]
                peak2_price = prices[peak2_idx]
                
                # Check if peaks are at similar heights
                height_diff = abs(peak1_price - peak2_price)
                avg_height = (peak1_price + peak2_price) / 2
                
                if height_diff / avg_height > params['height_tolerance']:
                    continue
                
                # Find valley between peaks
                valley_segment = prices[peak1_idx:peak2_idx+1]
                valley_idx = peak1_idx + np.argmin(valley_segment)
                valley_price = prices[valley_idx]
                
                # Check valley depth
                valley_depth = (avg_height - valley_price) / avg_height
                
                if valley_depth < params['valley_depth']:
                    continue
                
                # Check for breakdown confirmation
                breakdown_confirmed = self._check_breakdown_confirmation(
                    prices, peak2_idx, valley_price, params['confirmation_days']
                )
                
                # Calculate confidence
                confidence = self._calculate_double_top_confidence(
                    peak1_price, peak2_price, valley_price, 
                    distance, params, breakdown_confirmed
                )
                
                # Calculate target price (measured move)
                target_price = valley_price - (avg_height - valley_price)
                
                # Calculate neckline
                neckline = valley_price
                
                pattern = {
                    'type': 'double_top',
                    'timeframe': timeframe,
                    'direction': 'bearish',
                    'confidence': confidence,
                    
                    # Peak details
                    'peak1_idx': int(peak1_idx),
                    'peak1_date': dates[peak1_idx],
                    'peak1_price': float(peak1_price),
                    
                    'peak2_idx': int(peak2_idx),
                    'peak2_date': dates[peak2_idx],
                    'peak2_price': float(peak2_price),
                    
                    # Valley details
                    'valley_idx': int(valley_idx),
                    'valley_date': dates[valley_idx],
                    'valley_price': float(valley_price),
                    'neckline': float(neckline),
                    
                    # Pattern metrics
                    'height_diff_pct': float(height_diff / avg_height * 100),
                    'valley_depth_pct': float(valley_depth * 100),
                    'distance_periods': int(distance),
                    
                    # Trading levels
                    'target_price': float(target_price),
                    'stop_loss': float(avg_height * 1.02),  # 2% above peaks
                    'risk_reward': float((avg_height - target_price) / (avg_height * 0.02)),
                    
                    # Confirmation
                    'breakdown_confirmed': breakdown_confirmed,
                    'status': 'confirmed' if breakdown_confirmed else 'forming'
                }
                
                patterns.append(pattern)
        
        # Sort by confidence
        patterns.sort(key=lambda x: x['confidence'], reverse=True)
        
        return patterns
    
    def detect_double_bottoms(self, prices: np.ndarray, dates: List[str],
                             timeframe: str = 'daily') -> List[Dict]:
        """
        Detect double bottom patterns
        """
        if timeframe not in self.params:
            raise ValueError(f"Invalid timeframe: {timeframe}")
        
        params = self.params[timeframe]
        patterns = []
        
        # Find troughs (invert prices to find peaks)
        troughs, properties = find_peaks(
            -prices,
            distance=params['min_distance'],
            prominence=prices.std() * 0.5
        )
        
        if len(troughs) < 2:
            return patterns
        
        # Check each pair of troughs
        for i in range(len(troughs) - 1):
            for j in range(i + 1, len(troughs)):
                trough1_idx = troughs[i]
                trough2_idx = troughs[j]
                
                # Check distance
                distance = trough2_idx - trough1_idx
                if distance < params['min_distance'] or distance > params['max_distance']:
                    continue
                
                trough1_price = prices[trough1_idx]
                trough2_price = prices[trough2_idx]
                
                # Check if troughs are at similar depths
                depth_diff = abs(trough1_price - trough2_price)
                avg_depth = (trough1_price + trough2_price) / 2
                
                if depth_diff / avg_depth > params['height_tolerance']:
                    continue
                
                # Find peak between troughs
                peak_segment = prices[trough1_idx:trough2_idx+1]
                peak_idx = trough1_idx + np.argmax(peak_segment)
                peak_price = prices[peak_idx]
                
                # Check peak height
                peak_height = (peak_price - avg_depth) / avg_depth
                
                if peak_height < params['valley_depth']:
                    continue
                
                # Check for breakout confirmation
                breakout_confirmed = self._check_breakout_confirmation(
                    prices, trough2_idx, peak_price, params['confirmation_days']
                )
                
                # Calculate confidence
                confidence = self._calculate_double_bottom_confidence(
                    trough1_price, trough2_price, peak_price,
                    distance, params, breakout_confirmed
                )
                
                # Calculate target price
                target_price = peak_price + (peak_price - avg_depth)
                
                # Calculate neckline
                neckline = peak_price
                
                pattern = {
                    'type': 'double_bottom',
                    'timeframe': timeframe,
                    'direction': 'bullish',
                    'confidence': confidence,
                    
                    # Trough details
                    'trough1_idx': int(trough1_idx),
                    'trough1_date': dates[trough1_idx],
                    'trough1_price': float(trough1_price),
                    
                    'trough2_idx': int(trough2_idx),
                    'trough2_date': dates[trough2_idx],
                    'trough2_price': float(trough2_price),
                    
                    # Peak details
                    'peak_idx': int(peak_idx),
                    'peak_date': dates[peak_idx],
                    'peak_price': float(peak_price),
                    'neckline': float(neckline),
                    
                    # Pattern metrics
                    'depth_diff_pct': float(depth_diff / avg_depth * 100),
                    'peak_height_pct': float(peak_height * 100),
                    'distance_periods': int(distance),
                    
                    # Trading levels
                    'target_price': float(target_price),
                    'stop_loss': float(avg_depth * 0.98),  # 2% below troughs
                    'risk_reward': float((target_price - avg_depth) / (avg_depth * 0.02)),
                    
                    # Confirmation
                    'breakout_confirmed': breakout_confirmed,
                    'status': 'confirmed' if breakout_confirmed else 'forming'
                }
                
                patterns.append(pattern)
        
        # Sort by confidence
        patterns.sort(key=lambda x: x['confidence'], reverse=True)
        
        return patterns
    
    def _check_breakdown_confirmation(self, prices: np.ndarray, peak_idx: int,
                                     neckline: float, confirmation_days: int) -> bool:
        """Check if price broke down below neckline"""
        if peak_idx + confirmation_days >= len(prices):
            return False
        
        # Check if price closed below neckline for confirmation days
        after_peak = prices[peak_idx+1:peak_idx+1+confirmation_days]
        return np.all(after_peak < neckline)
    
    def _check_breakout_confirmation(self, prices: np.ndarray, trough_idx: int,
                                    neckline: float, confirmation_days: int) -> bool:
        """Check if price broke out above neckline"""
        if trough_idx + confirmation_days >= len(prices):
            return False
        
        # Check if price closed above neckline for confirmation days
        after_trough = prices[trough_idx+1:trough_idx+1+confirmation_days]
        return np.all(after_trough > neckline)
    
    def _calculate_double_top_confidence(self, peak1: float, peak2: float,
                                        valley: float, distance: int,
                                        params: Dict, confirmed: bool) -> float:
        """Calculate confidence score for double top"""
        confidence = 0.0
        
        # Base confidence
        confidence += 0.50
        
        # Height similarity (max 0.20)
        height_diff = abs(peak1 - peak2) / ((peak1 + peak2) / 2)
        height_score = max(0, 0.20 - height_diff * 10)
        confidence += height_score
        
        # Valley depth (max 0.15)
        avg_peak = (peak1 + peak2) / 2
        valley_depth = (avg_peak - valley) / avg_peak
        depth_score = min(0.15, valley_depth * 3)
        confidence += depth_score
        
        # Distance (max 0.10)
        ideal_distance = (params['min_distance'] + params['max_distance']) / 2
        distance_score = 0.10 * (1 - abs(distance - ideal_distance) / ideal_distance)
        confidence += max(0, distance_score)
        
        # Confirmation bonus (0.05)
        if confirmed:
            confidence += 0.05
        
        return min(1.0, confidence)
    
    def _calculate_double_bottom_confidence(self, trough1: float, trough2: float,
                                           peak: float, distance: int,
                                           params: Dict, confirmed: bool) -> float:
        """Calculate confidence score for double bottom"""
        confidence = 0.0
        
        # Base confidence
        confidence += 0.50
        
        # Depth similarity (max 0.20)
        depth_diff = abs(trough1 - trough2) / ((trough1 + trough2) / 2)
        depth_score = max(0, 0.20 - depth_diff * 10)
        confidence += depth_score
        
        # Peak height (max 0.15)
        avg_trough = (trough1 + trough2) / 2
        peak_height = (peak - avg_trough) / avg_trough
        height_score = min(0.15, peak_height * 3)
        confidence += height_score
        
        # Distance (max 0.10)
        ideal_distance = (params['min_distance'] + params['max_distance']) / 2
        distance_score = 0.10 * (1 - abs(distance - ideal_distance) / ideal_distance)
        confidence += max(0, distance_score)
        
        # Confirmation bonus (0.05)
        if confirmed:
            confidence += 0.05
        
        return min(1.0, confidence)
    
    def analyze_multi_timeframe(self, daily_prices: pd.DataFrame) -> Dict:
        """
        Analyze double patterns across all timeframes
        
        Args:
            daily_prices: DataFrame with DatetimeIndex and 'Close' column
        """
        results = {
            'daily': {},
            'weekly': {},
            'monthly': {},
            'consensus': {}
        }
        
        # Daily analysis
        daily_dates = daily_prices.index.astype(str).tolist()
        daily_close = daily_prices['Close'].values
        
        results['daily']['double_tops'] = self.detect_double_tops(
            daily_close, daily_dates, 'daily'
        )
        results['daily']['double_bottoms'] = self.detect_double_bottoms(
            daily_close, daily_dates, 'daily'
        )
        
        # Weekly analysis
        weekly_prices = daily_prices.resample('W').agg({
            'Close': 'last'
        }).dropna()
        
        if len(weekly_prices) > 10:
            weekly_dates = weekly_prices.index.astype(str).tolist()
            weekly_close = weekly_prices['Close'].values
            
            results['weekly']['double_tops'] = self.detect_double_tops(
                weekly_close, weekly_dates, 'weekly'
            )
            results['weekly']['double_bottoms'] = self.detect_double_bottoms(
                weekly_close, weekly_dates, 'weekly'
            )
        
        # Monthly analysis
        monthly_prices = daily_prices.resample('M').agg({
            'Close': 'last'
        }).dropna()
        
        if len(monthly_prices) > 6:
            monthly_dates = monthly_prices.index.astype(str).tolist()
            monthly_close = monthly_prices['Close'].values
            
            results['monthly']['double_tops'] = self.detect_double_tops(
                monthly_close, monthly_dates, 'monthly'
            )
            results['monthly']['double_bottoms'] = self.detect_double_bottoms(
                monthly_close, monthly_dates, 'monthly'
            )
        
        # Build consensus
        results['consensus'] = self._build_timeframe_consensus(results)
        
        return results
    
    def _build_timeframe_consensus(self, results: Dict) -> Dict:
        """Build consensus across timeframes"""
        consensus = {
            'double_tops': [],
            'double_bottoms': [],
            'recommendation': None,
            'strength': 0
        }
        
        # Count patterns across timeframes
        top_count = 0
        bottom_count = 0
        
        for tf in ['daily', 'weekly', 'monthly']:
            if tf in results and results[tf]:
                top_count += len(results[tf].get('double_tops', []))
                bottom_count += len(results[tf].get('double_bottoms', []))
        
        # Determine recommendation
        if top_count > bottom_count:
            consensus['recommendation'] = 'BEARISH'
            consensus['strength'] = min(100, top_count * 30)
        elif bottom_count > top_count:
            consensus['recommendation'] = 'BULLISH'
            consensus['strength'] = min(100, bottom_count * 30)
        else:
            consensus['recommendation'] = 'NEUTRAL'
            consensus['strength'] = 50
        
        return consensus


if __name__ == "__main__":
    # Test
    detector = DoublePatternDetector()
    
    # Generate test data
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    prices = np.array([100 + np.sin(i/10)*10 + np.random.randn()*2 for i in range(100)])
    
    df = pd.DataFrame({'Date': dates, 'Close': prices})
    df.set_index('Date', inplace=True)
    
    # Detect patterns
    results = detector.analyze_multi_timeframe(df)
    
    print("Double Top/Bottom Detector Test")
    print("="*60)
    print(f"Daily double tops: {len(results['daily'].get('double_tops', []))}")
    print(f"Daily double bottoms: {len(results['daily'].get('double_bottoms', []))}")
    print(f"Consensus: {results['consensus']['recommendation']}")
