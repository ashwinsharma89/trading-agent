"""
Chart Pattern Recognizer
Uses computer vision to recognize patterns in stock charts
"""

import os
import numpy as np
from typing import Dict, Any, List, Tuple
import json
from datetime import datetime


class ChartPatternRecognizer:
    """
    Recognize chart patterns from price data or images
    """
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.cache_dir = 'data/chart_patterns'
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Pattern definitions
        self.patterns = {
            'head_and_shoulders': {'reliability': 0.85, 'direction': 'bearish'},
            'inverse_head_and_shoulders': {'reliability': 0.85, 'direction': 'bullish'},
            'double_top': {'reliability': 0.80, 'direction': 'bearish'},
            'double_bottom': {'reliability': 0.80, 'direction': 'bullish'},
            'ascending_triangle': {'reliability': 0.75, 'direction': 'bullish'},
            'descending_triangle': {'reliability': 0.75, 'direction': 'bearish'},
            'symmetrical_triangle': {'reliability': 0.70, 'direction': 'neutral'},
            'cup_and_handle': {'reliability': 0.80, 'direction': 'bullish'},
            'flag': {'reliability': 0.75, 'direction': 'continuation'},
            'pennant': {'reliability': 0.75, 'direction': 'continuation'},
            'wedge_rising': {'reliability': 0.70, 'direction': 'bearish'},
            'wedge_falling': {'reliability': 0.70, 'direction': 'bullish'},
        }
    
    def recognize_patterns_from_data(self, prices: List[float], 
                                     dates: List[str]) -> List[Dict[str, Any]]:
        """
        Recognize patterns from price data
        """
        patterns_found = []
        
        # Convert to numpy array
        price_array = np.array(prices)
        
        # Detect each pattern type
        patterns_found.extend(self._detect_head_and_shoulders(price_array, dates))
        patterns_found.extend(self._detect_double_top_bottom(price_array, dates))
        patterns_found.extend(self._detect_triangles(price_array, dates))
        patterns_found.extend(self._detect_cup_and_handle(price_array, dates))
        patterns_found.extend(self._detect_flags_pennants(price_array, dates))
        patterns_found.extend(self._detect_wedges(price_array, dates))
        
        # Sort by confidence
        patterns_found.sort(key=lambda x: x['confidence'], reverse=True)
        
        return patterns_found
    
    def _detect_head_and_shoulders(self, prices: np.ndarray, 
                                   dates: List[str]) -> List[Dict]:
        """
        Detect head and shoulders pattern
        """
        patterns = []
        window = 30  # Look at 30-day windows
        
        if len(prices) < window:
            return patterns
        
        for i in range(len(prices) - window):
            segment = prices[i:i+window]
            
            # Find peaks
            peaks = self._find_peaks(segment)
            
            if len(peaks) >= 3:
                # Check if middle peak is highest (head)
                # and side peaks are similar (shoulders)
                left_shoulder = peaks[0]
                head = peaks[1]
                right_shoulder = peaks[2]
                
                if (segment[head] > segment[left_shoulder] and 
                    segment[head] > segment[right_shoulder] and
                    abs(segment[left_shoulder] - segment[right_shoulder]) < segment[head] * 0.05):
                    
                    patterns.append({
                        'pattern': 'head_and_shoulders',
                        'direction': 'bearish',
                        'confidence': 0.75,
                        'start_date': dates[i],
                        'end_date': dates[i+window-1],
                        'target': segment[head] * 0.90,  # 10% drop expected
                        'reliability': 0.85
                    })
        
        return patterns
    
    def _detect_double_top_bottom(self, prices: np.ndarray, 
                                  dates: List[str]) -> List[Dict]:
        """
        Detect double top/bottom patterns
        """
        patterns = []
        window = 20
        
        if len(prices) < window:
            return patterns
        
        for i in range(len(prices) - window):
            segment = prices[i:i+window]
            
            # Find peaks and troughs
            peaks = self._find_peaks(segment)
            troughs = self._find_troughs(segment)
            
            # Double top: two similar peaks
            if len(peaks) >= 2:
                if abs(segment[peaks[0]] - segment[peaks[1]]) < segment[peaks[0]] * 0.03:
                    patterns.append({
                        'pattern': 'double_top',
                        'direction': 'bearish',
                        'confidence': 0.70,
                        'start_date': dates[i],
                        'end_date': dates[i+window-1],
                        'target': segment[peaks[0]] * 0.93,
                        'reliability': 0.80
                    })
            
            # Double bottom: two similar troughs
            if len(troughs) >= 2:
                if abs(segment[troughs[0]] - segment[troughs[1]]) < segment[troughs[0]] * 0.03:
                    patterns.append({
                        'pattern': 'double_bottom',
                        'direction': 'bullish',
                        'confidence': 0.70,
                        'start_date': dates[i],
                        'end_date': dates[i+window-1],
                        'target': segment[troughs[0]] * 1.07,
                        'reliability': 0.80
                    })
        
        return patterns
    
    def _detect_triangles(self, prices: np.ndarray, dates: List[str]) -> List[Dict]:
        """
        Detect triangle patterns (ascending, descending, symmetrical)
        """
        patterns = []
        window = 25
        
        if len(prices) < window:
            return patterns
        
        for i in range(len(prices) - window):
            segment = prices[i:i+window]
            
            # Find highs and lows
            highs = self._find_peaks(segment)
            lows = self._find_troughs(segment)
            
            if len(highs) >= 2 and len(lows) >= 2:
                # Calculate trendlines
                high_slope = self._calculate_slope([segment[h] for h in highs])
                low_slope = self._calculate_slope([segment[l] for l in lows])
                
                # Ascending triangle: flat top, rising bottom
                if abs(high_slope) < 0.01 and low_slope > 0.01:
                    patterns.append({
                        'pattern': 'ascending_triangle',
                        'direction': 'bullish',
                        'confidence': 0.65,
                        'start_date': dates[i],
                        'end_date': dates[i+window-1],
                        'target': segment[-1] * 1.05,
                        'reliability': 0.75
                    })
                
                # Descending triangle: declining top, flat bottom
                elif high_slope < -0.01 and abs(low_slope) < 0.01:
                    patterns.append({
                        'pattern': 'descending_triangle',
                        'direction': 'bearish',
                        'confidence': 0.65,
                        'start_date': dates[i],
                        'end_date': dates[i+window-1],
                        'target': segment[-1] * 0.95,
                        'reliability': 0.75
                    })
                
                # Symmetrical triangle: converging lines
                elif high_slope < -0.01 and low_slope > 0.01:
                    patterns.append({
                        'pattern': 'symmetrical_triangle',
                        'direction': 'neutral',
                        'confidence': 0.60,
                        'start_date': dates[i],
                        'end_date': dates[i+window-1],
                        'target': segment[-1],
                        'reliability': 0.70
                    })
        
        return patterns
    
    def _detect_cup_and_handle(self, prices: np.ndarray, 
                               dates: List[str]) -> List[Dict]:
        """
        Detect cup and handle pattern
        """
        patterns = []
        window = 40  # Longer pattern
        
        if len(prices) < window:
            return patterns
        
        for i in range(len(prices) - window):
            segment = prices[i:i+window]
            
            # Cup: U-shaped bottom
            mid = len(segment) // 2
            if (segment[0] > segment[mid] and 
                segment[-1] > segment[mid] and
                abs(segment[0] - segment[-1]) < segment[0] * 0.05):
                
                # Handle: small pullback at end
                handle_start = int(window * 0.75)
                if segment[-1] < segment[handle_start]:
                    patterns.append({
                        'pattern': 'cup_and_handle',
                        'direction': 'bullish',
                        'confidence': 0.70,
                        'start_date': dates[i],
                        'end_date': dates[i+window-1],
                        'target': segment[0] * 1.10,
                        'reliability': 0.80
                    })
        
        return patterns
    
    def _detect_flags_pennants(self, prices: np.ndarray, 
                               dates: List[str]) -> List[Dict]:
        """
        Detect flag and pennant patterns (continuation)
        """
        patterns = []
        # Implementation similar to triangles but shorter timeframe
        return patterns
    
    def _detect_wedges(self, prices: np.ndarray, dates: List[str]) -> List[Dict]:
        """
        Detect rising and falling wedges
        """
        patterns = []
        # Implementation similar to triangles but both lines sloping same direction
        return patterns
    
    def _find_peaks(self, data: np.ndarray, threshold: float = 0.02) -> List[int]:
        """
        Find local peaks in price data
        """
        peaks = []
        for i in range(1, len(data) - 1):
            if data[i] > data[i-1] and data[i] > data[i+1]:
                if data[i] > data[i-1] * (1 + threshold):
                    peaks.append(i)
        return peaks
    
    def _find_troughs(self, data: np.ndarray, threshold: float = 0.02) -> List[int]:
        """
        Find local troughs in price data
        """
        troughs = []
        for i in range(1, len(data) - 1):
            if data[i] < data[i-1] and data[i] < data[i+1]:
                if data[i] < data[i-1] * (1 - threshold):
                    troughs.append(i)
        return troughs
    
    def _calculate_slope(self, values: List[float]) -> float:
        """
        Calculate slope of trendline
        """
        if len(values) < 2:
            return 0
        
        x = np.arange(len(values))
        y = np.array(values)
        
        # Linear regression
        slope = np.polyfit(x, y, 1)[0]
        return slope / np.mean(y)  # Normalize by average value
    
    def recognize_from_image(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Recognize patterns from chart image using AI vision
        """
        try:
            import openai
            import base64
            
            # Read image
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # Use GPT-4 Vision
            response = openai.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this stock chart and identify any chart patterns (head and shoulders, double top/bottom, triangles, cup and handle, flags, wedges). Return as JSON with pattern name, direction (bullish/bearish), and confidence (0-1)."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('patterns', [])
            
        except Exception as e:
            print(f"Image recognition failed: {e}")
            return []
    
    def get_pattern_statistics(self, ticker: str) -> Dict[str, Any]:
        """
        Get historical accuracy of pattern predictions
        """
        stats_file = f"{self.cache_dir}/{ticker}_pattern_stats.json"
        
        if os.path.exists(stats_file):
            with open(stats_file, 'r') as f:
                return json.load(f)
        
        return {
            'patterns_detected': 0,
            'patterns_successful': 0,
            'accuracy': 0.0,
            'best_pattern': None
        }


if __name__ == "__main__":
    # Test
    recognizer = ChartPatternRecognizer()
    
    # Example: recognize from price data
    prices = [100, 102, 105, 103, 108, 110, 107, 105, 103, 101]
    dates = ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', 
             '2025-01-05', '2025-01-06', '2025-01-07', '2025-01-08',
             '2025-01-09', '2025-01-10']
    
    patterns = recognizer.recognize_patterns_from_data(prices, dates)
    
    for pattern in patterns:
        print(f"Pattern: {pattern['pattern']}")
        print(f"Direction: {pattern['direction']}")
        print(f"Confidence: {pattern['confidence']}")
        print(f"Target: {pattern['target']}")
        print()
