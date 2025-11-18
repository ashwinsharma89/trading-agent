"""
Enhanced Pattern Recognition
Advanced algorithms for better chart pattern detection
"""

import numpy as np
from scipy.signal import find_peaks, savgol_filter
from scipy.stats import linregress
from typing import List, Dict, Tuple
import cv2


class EnhancedPatternRecognizer:
    """
    Advanced pattern recognition using multiple techniques
    """
    
    def __init__(self):
        self.min_pattern_length = 10
        self.confidence_threshold = 0.6
    
    def detect_all_patterns(self, prices: np.ndarray) -> List[Dict]:
        """
        Detect all patterns using advanced algorithms
        """
        # Smooth data
        smoothed = self._smooth_prices(prices)
        
        patterns = []
        
        # Detect each pattern type
        patterns.extend(self._detect_head_shoulders_advanced(smoothed))
        patterns.extend(self._detect_triangles_advanced(smoothed))
        patterns.extend(self._detect_double_patterns_advanced(smoothed))
        patterns.extend(self._detect_cup_handle_advanced(smoothed))
        patterns.extend(self._detect_channels(smoothed))
        patterns.extend(self._detect_wedges_advanced(smoothed))
        
        return sorted(patterns, key=lambda x: x['confidence'], reverse=True)
    
    def _smooth_prices(self, prices: np.ndarray) -> np.ndarray:
        """Smooth price data using Savitzky-Golay filter"""
        if len(prices) < 11:
            return prices
        window = min(11, len(prices) if len(prices) % 2 == 1 else len(prices) - 1)
        return savgol_filter(prices, window, 3)
    
    def _find_peaks_advanced(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Find peaks and troughs using scipy"""
        peaks, _ = find_peaks(data, distance=5)
        troughs, _ = find_peaks(-data, distance=5)
        return peaks, troughs
    
    def _detect_head_shoulders_advanced(self, prices: np.ndarray) -> List[Dict]:
        """Advanced head & shoulders detection"""
        patterns = []
        peaks, troughs = self._find_peaks_advanced(prices)
        
        if len(peaks) < 3 or len(troughs) < 2:
            return patterns
        
        for i in range(len(peaks) - 2):
            left_shoulder = peaks[i]
            head = peaks[i + 1]
            right_shoulder = peaks[i + 2]
            
            # Check pattern validity
            if (prices[head] > prices[left_shoulder] and 
                prices[head] > prices[right_shoulder]):
                
                # Shoulders should be similar height
                shoulder_diff = abs(prices[left_shoulder] - prices[right_shoulder])
                avg_shoulder = (prices[left_shoulder] + prices[right_shoulder]) / 2
                
                if shoulder_diff / avg_shoulder < 0.05:  # Within 5%
                    # Calculate neckline
                    neckline_slope = (prices[right_shoulder] - prices[left_shoulder]) / (right_shoulder - left_shoulder)
                    
                    confidence = 0.85 - (shoulder_diff / avg_shoulder)
                    
                    patterns.append({
                        'name': 'head_and_shoulders',
                        'direction': 'bearish',
                        'confidence': confidence,
                        'start_idx': left_shoulder,
                        'end_idx': right_shoulder,
                        'target': prices[head] - (prices[head] - avg_shoulder),
                        'neckline_slope': neckline_slope
                    })
        
        return patterns
    
    def _detect_triangles_advanced(self, prices: np.ndarray) -> List[Dict]:
        """Advanced triangle detection using trendlines"""
        patterns = []
        peaks, troughs = self._find_peaks_advanced(prices)
        
        if len(peaks) < 2 or len(troughs) < 2:
            return patterns
        
        # Calculate trendlines
        if len(peaks) >= 2:
            peak_slope, peak_intercept, peak_r, _, _ = linregress(peaks, prices[peaks])
        else:
            return patterns
            
        if len(troughs) >= 2:
            trough_slope, trough_intercept, trough_r, _, _ = linregress(troughs, prices[troughs])
        else:
            return patterns
        
        # Ascending triangle: flat top, rising bottom
        if abs(peak_slope) < 0.01 and trough_slope > 0.01:
            confidence = min(abs(peak_r), abs(trough_r))
            patterns.append({
                'name': 'ascending_triangle',
                'direction': 'bullish',
                'confidence': confidence,
                'breakout_target': prices[peaks[-1]] * 1.05
            })
        
        # Descending triangle: declining top, flat bottom
        elif peak_slope < -0.01 and abs(trough_slope) < 0.01:
            confidence = min(abs(peak_r), abs(trough_r))
            patterns.append({
                'name': 'descending_triangle',
                'direction': 'bearish',
                'confidence': confidence,
                'breakout_target': prices[troughs[-1]] * 0.95
            })
        
        # Symmetrical triangle: converging lines
        elif peak_slope < -0.01 and trough_slope > 0.01:
            confidence = min(abs(peak_r), abs(trough_r)) * 0.9
            patterns.append({
                'name': 'symmetrical_triangle',
                'direction': 'neutral',
                'confidence': confidence
            })
        
        return patterns
    
    def _detect_double_patterns_advanced(self, prices: np.ndarray) -> List[Dict]:
        """Advanced double top/bottom detection"""
        patterns = []
        peaks, troughs = self._find_peaks_advanced(prices)
        
        # Double top
        for i in range(len(peaks) - 1):
            p1, p2 = peaks[i], peaks[i + 1]
            height_diff = abs(prices[p1] - prices[p2])
            avg_height = (prices[p1] + prices[p2]) / 2
            
            if height_diff / avg_height < 0.03:  # Within 3%
                # Find trough between peaks
                between_troughs = troughs[(troughs > p1) & (troughs < p2)]
                
                if len(between_troughs) > 0:
                    valley = prices[between_troughs[0]]
                    depth = avg_height - valley
                    
                    if depth / avg_height > 0.02:  # At least 2% depth
                        confidence = 0.80 - (height_diff / avg_height)
                        
                        patterns.append({
                            'name': 'double_top',
                            'direction': 'bearish',
                            'confidence': confidence,
                            'target': valley - depth
                        })
        
        # Double bottom
        for i in range(len(troughs) - 1):
            t1, t2 = troughs[i], troughs[i + 1]
            depth_diff = abs(prices[t1] - prices[t2])
            avg_depth = (prices[t1] + prices[t2]) / 2
            
            if depth_diff / avg_depth < 0.03:
                between_peaks = peaks[(peaks > t1) & (peaks < t2)]
                
                if len(between_peaks) > 0:
                    peak = prices[between_peaks[0]]
                    height = peak - avg_depth
                    
                    if height / avg_depth > 0.02:
                        confidence = 0.80 - (depth_diff / avg_depth)
                        
                        patterns.append({
                            'name': 'double_bottom',
                            'direction': 'bullish',
                            'confidence': confidence,
                            'target': peak + height
                        })
        
        return patterns
    
    def _detect_cup_handle_advanced(self, prices: np.ndarray) -> List[Dict]:
        """Advanced cup and handle detection"""
        patterns = []
        
        if len(prices) < 40:
            return patterns
        
        # Look for U-shaped cup
        for i in range(len(prices) - 40):
            segment = prices[i:i+40]
            
            # Cup: start and end should be similar, middle should be lower
            start, end = segment[0], segment[-1]
            mid_idx = len(segment) // 2
            mid = segment[mid_idx]
            
            if (abs(start - end) / start < 0.05 and  # Similar heights
                mid < start * 0.90):  # At least 10% drop
                
                # Check for handle (small pullback at end)
                handle_start = int(len(segment) * 0.75)
                handle = segment[handle_start:]
                
                if len(handle) > 5 and handle[-1] < handle[0]:
                    confidence = 0.75
                    
                    patterns.append({
                        'name': 'cup_and_handle',
                        'direction': 'bullish',
                        'confidence': confidence,
                        'target': start * 1.10
                    })
        
        return patterns
    
    def _detect_channels(self, prices: np.ndarray) -> List[Dict]:
        """Detect price channels"""
        patterns = []
        peaks, troughs = self._find_peaks_advanced(prices)
        
        if len(peaks) >= 3 and len(troughs) >= 3:
            # Fit lines to peaks and troughs
            peak_slope, _, peak_r, _, _ = linregress(peaks, prices[peaks])
            trough_slope, _, trough_r, _, _ = linregress(troughs, prices[troughs])
            
            # Parallel lines indicate channel
            slope_diff = abs(peak_slope - trough_slope)
            
            if slope_diff < 0.01 and abs(peak_r) > 0.7 and abs(trough_r) > 0.7:
                if peak_slope > 0.01:
                    direction = 'bullish'
                    name = 'ascending_channel'
                elif peak_slope < -0.01:
                    direction = 'bearish'
                    name = 'descending_channel'
                else:
                    direction = 'neutral'
                    name = 'horizontal_channel'
                
                confidence = min(abs(peak_r), abs(trough_r))
                
                patterns.append({
                    'name': name,
                    'direction': direction,
                    'confidence': confidence
                })
        
        return patterns
    
    def _detect_wedges_advanced(self, prices: np.ndarray) -> List[Dict]:
        """Advanced wedge detection"""
        patterns = []
        peaks, troughs = self._find_peaks_advanced(prices)
        
        if len(peaks) >= 2 and len(troughs) >= 2:
            peak_slope, _, _, _, _ = linregress(peaks, prices[peaks])
            trough_slope, _, _, _, _ = linregress(troughs, prices[troughs])
            
            # Rising wedge: both lines rising, converging
            if peak_slope > 0 and trough_slope > 0 and peak_slope < trough_slope:
                patterns.append({
                    'name': 'rising_wedge',
                    'direction': 'bearish',
                    'confidence': 0.70
                })
            
            # Falling wedge: both lines falling, converging
            elif peak_slope < 0 and trough_slope < 0 and peak_slope > trough_slope:
                patterns.append({
                    'name': 'falling_wedge',
                    'direction': 'bullish',
                    'confidence': 0.70
                })
        
        return patterns


if __name__ == "__main__":
    # Test
    recognizer = EnhancedPatternRecognizer()
    
    # Generate test data with head & shoulders
    prices = np.array([100, 102, 105, 103, 101, 103, 108, 112, 115, 113, 
                      110, 107, 105, 107, 103, 101, 99, 97])
    
    patterns = recognizer.detect_all_patterns(prices)
    
    print(f"Found {len(patterns)} patterns:")
    for p in patterns:
        print(f"  • {p['name']} ({p['direction']}) - {p['confidence']:.0%}")
