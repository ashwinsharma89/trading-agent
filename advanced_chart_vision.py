"""
Advanced Chart Image Analysis
Uses multiple computer vision techniques to analyze chart images
"""

import os
import base64
import json
import numpy as np
from typing import Dict, Any, List, Tuple
from PIL import Image
import io


class AdvancedChartVision:
    """
    Advanced chart image analysis using multiple approaches
    """
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.cache_dir = 'data/chart_images'
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def analyze_chart_image(self, image_path: str, ticker: str = None) -> Dict[str, Any]:
        """
        Complete chart image analysis using multiple methods
        """
        results = {
            'ticker': ticker,
            'image_path': image_path,
            'methods_used': []
        }
        
        # Method 1: AI Vision (GPT-4 Vision)
        ai_analysis = self._ai_vision_analysis(image_path)
        results['ai_vision'] = ai_analysis
        results['methods_used'].append('ai_vision')
        
        # Method 2: Traditional CV (if we can extract price data)
        cv_analysis = self._traditional_cv_analysis(image_path)
        if cv_analysis:
            results['computer_vision'] = cv_analysis
            results['methods_used'].append('computer_vision')
        
        # Method 3: OCR + Pattern matching
        ocr_analysis = self._ocr_analysis(image_path)
        if ocr_analysis:
            results['ocr'] = ocr_analysis
            results['methods_used'].append('ocr')
        
        # Combine all results
        results['combined_analysis'] = self._combine_analyses(
            ai_analysis, cv_analysis, ocr_analysis
        )
        
        return results
    
    def _ai_vision_analysis(self, image_path: str) -> Dict[str, Any]:
        """
        Method 1: Use GPT-4 Vision to analyze chart
        Most accurate but requires API calls
        """
        try:
            import openai
            
            # Read and encode image
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # Detailed prompt for comprehensive analysis
            prompt = """
            Analyze this stock chart image in detail:
            
            1. PATTERNS: Identify any chart patterns (head & shoulders, triangles, flags, etc.)
            2. TREND: Overall trend (uptrend, downtrend, sideways)
            3. SUPPORT/RESISTANCE: Key price levels
            4. INDICATORS: Any visible indicators (RSI, MACD, volume)
            5. CANDLESTICK PATTERNS: Any notable candlestick formations
            6. VOLUME: Volume analysis if visible
            7. TIMEFRAME: Estimated timeframe (daily, weekly, etc.)
            8. RECOMMENDATION: Buy/Sell/Hold based on the chart
            9. CONFIDENCE: Your confidence level (0-1)
            10. KEY OBSERVATIONS: Top 3-5 observations
            
            Return as JSON with these exact keys:
            {
                "patterns": [{"name": "...", "direction": "bullish/bearish", "confidence": 0.8}],
                "trend": "uptrend/downtrend/sideways",
                "support_levels": [450, 440],
                "resistance_levels": [480, 490],
                "indicators": {"rsi": "oversold", "macd": "bullish_crossover"},
                "candlestick_patterns": ["hammer", "engulfing"],
                "volume_analysis": "increasing/decreasing/normal",
                "timeframe": "daily/weekly/monthly",
                "recommendation": "buy/sell/hold",
                "confidence": 0.75,
                "key_observations": ["...", "...", "..."]
            }
            """
            
            response = openai.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            result['method'] = 'ai_vision'
            result['available'] = True
            
            return result
            
        except Exception as e:
            print(f"AI Vision analysis failed: {e}")
            return {'available': False, 'error': str(e)}
    
    def _traditional_cv_analysis(self, image_path: str) -> Dict[str, Any]:
        """
        Method 2: Traditional computer vision
        Extract price data from chart and analyze
        """
        try:
            from PIL import Image
            import cv2
            
            # Load image
            img = Image.open(image_path)
            img_array = np.array(img)
            
            # Convert to grayscale
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Detect chart area (remove axes, labels)
            chart_area = self._detect_chart_area(gray)
            
            # Extract price line
            price_line = self._extract_price_line(chart_area)
            
            if price_line is not None:
                # Analyze the extracted price line
                patterns = self._analyze_price_line(price_line)
                
                return {
                    'available': True,
                    'method': 'computer_vision',
                    'patterns': patterns,
                    'price_points': len(price_line)
                }
            
            return None
            
        except Exception as e:
            print(f"Traditional CV analysis failed: {e}")
            return None
    
    def _detect_chart_area(self, gray_image: np.ndarray) -> np.ndarray:
        """
        Detect the main chart area (remove axes, labels)
        """
        # Simple approach: assume chart is in center 80%
        h, w = gray_image.shape
        margin_h = int(h * 0.1)
        margin_w = int(w * 0.1)
        
        chart_area = gray_image[margin_h:h-margin_h, margin_w:w-margin_w]
        return chart_area
    
    def _extract_price_line(self, chart_area: np.ndarray) -> np.ndarray:
        """
        Extract the price line from chart area
        """
        try:
            import cv2
            
            # Edge detection
            edges = cv2.Canny(chart_area, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, 
                                          cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Get the longest contour (likely the price line)
                longest = max(contours, key=cv2.contourArea)
                
                # Convert to price points
                points = longest.squeeze()
                if len(points.shape) == 2:
                    # Extract y-coordinates (prices)
                    prices = points[:, 1]
                    # Invert (image coords are top-down)
                    prices = chart_area.shape[0] - prices
                    return prices
            
            return None
            
        except Exception as e:
            print(f"Price line extraction failed: {e}")
            return None
    
    def _analyze_price_line(self, price_line: np.ndarray) -> List[Dict]:
        """
        Analyze extracted price line for patterns
        """
        patterns = []
        
        # Normalize prices
        normalized = (price_line - price_line.min()) / (price_line.max() - price_line.min())
        
        # Detect trend
        if normalized[-1] > normalized[0] + 0.1:
            patterns.append({
                'name': 'uptrend',
                'direction': 'bullish',
                'confidence': 0.7
            })
        elif normalized[-1] < normalized[0] - 0.1:
            patterns.append({
                'name': 'downtrend',
                'direction': 'bearish',
                'confidence': 0.7
            })
        
        # Detect peaks and troughs
        peaks = self._find_peaks_cv(normalized)
        troughs = self._find_troughs_cv(normalized)
        
        # Double top/bottom
        if len(peaks) >= 2:
            if abs(normalized[peaks[-1]] - normalized[peaks[-2]]) < 0.05:
                patterns.append({
                    'name': 'double_top',
                    'direction': 'bearish',
                    'confidence': 0.65
                })
        
        if len(troughs) >= 2:
            if abs(normalized[troughs[-1]] - normalized[troughs[-2]]) < 0.05:
                patterns.append({
                    'name': 'double_bottom',
                    'direction': 'bullish',
                    'confidence': 0.65
                })
        
        return patterns
    
    def _find_peaks_cv(self, data: np.ndarray) -> List[int]:
        """Find peaks in normalized price data"""
        peaks = []
        for i in range(1, len(data) - 1):
            if data[i] > data[i-1] and data[i] > data[i+1]:
                peaks.append(i)
        return peaks
    
    def _find_troughs_cv(self, data: np.ndarray) -> List[int]:
        """Find troughs in normalized price data"""
        troughs = []
        for i in range(1, len(data) - 1):
            if data[i] < data[i-1] and data[i] < data[i+1]:
                troughs.append(i)
        return troughs
    
    def _ocr_analysis(self, image_path: str) -> Dict[str, Any]:
        """
        Method 3: OCR to extract text (prices, dates, indicators)
        """
        try:
            import pytesseract
            from PIL import Image
            
            img = Image.open(image_path)
            
            # Extract text
            text = pytesseract.image_to_string(img)
            
            # Parse for useful info
            analysis = {
                'available': True,
                'method': 'ocr',
                'extracted_text': text,
                'prices': self._extract_prices_from_text(text),
                'dates': self._extract_dates_from_text(text),
                'indicators': self._extract_indicators_from_text(text)
            }
            
            return analysis
            
        except Exception as e:
            print(f"OCR analysis failed: {e}")
            return None
    
    def _extract_prices_from_text(self, text: str) -> List[float]:
        """Extract price values from OCR text"""
        import re
        
        # Find numbers that look like prices
        price_pattern = r'\d+\.?\d*'
        matches = re.findall(price_pattern, text)
        
        prices = []
        for match in matches:
            try:
                price = float(match)
                if 10 < price < 100000:  # Reasonable price range
                    prices.append(price)
            except:
                pass
        
        return prices
    
    def _extract_dates_from_text(self, text: str) -> List[str]:
        """Extract dates from OCR text"""
        import re
        
        # Common date patterns
        date_patterns = [
            r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
            r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',
            r'[A-Z][a-z]{2}\s+\d{1,2}'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)
        
        return dates
    
    def _extract_indicators_from_text(self, text: str) -> Dict[str, str]:
        """Extract indicator values from OCR text"""
        indicators = {}
        
        text_lower = text.lower()
        
        # Look for common indicators
        if 'rsi' in text_lower:
            indicators['rsi'] = 'present'
        if 'macd' in text_lower:
            indicators['macd'] = 'present'
        if 'volume' in text_lower:
            indicators['volume'] = 'present'
        
        return indicators
    
    def _combine_analyses(self, ai: Dict, cv: Dict, ocr: Dict) -> Dict[str, Any]:
        """
        Combine results from all methods
        """
        combined = {
            'patterns': [],
            'confidence': 0.0,
            'recommendation': 'HOLD',
            'consensus': {}
        }
        
        # Collect all patterns
        all_patterns = []
        
        if ai and ai.get('available'):
            all_patterns.extend(ai.get('patterns', []))
            combined['ai_recommendation'] = ai.get('recommendation', 'hold')
            combined['ai_confidence'] = ai.get('confidence', 0.5)
        
        if cv and cv.get('available'):
            all_patterns.extend(cv.get('patterns', []))
        
        # Count pattern occurrences
        pattern_counts = {}
        for p in all_patterns:
            name = p['name']
            if name not in pattern_counts:
                pattern_counts[name] = {
                    'count': 0,
                    'direction': p['direction'],
                    'avg_confidence': 0
                }
            pattern_counts[name]['count'] += 1
            pattern_counts[name]['avg_confidence'] += p.get('confidence', 0.5)
        
        # Calculate average confidence
        for name in pattern_counts:
            pattern_counts[name]['avg_confidence'] /= pattern_counts[name]['count']
        
        # Patterns detected by multiple methods are more reliable
        for name, data in pattern_counts.items():
            combined['patterns'].append({
                'name': name,
                'direction': data['direction'],
                'confidence': data['avg_confidence'],
                'detected_by': data['count']
            })
        
        # Sort by confidence
        combined['patterns'].sort(key=lambda x: x['confidence'], reverse=True)
        
        # Overall recommendation
        if combined['patterns']:
            bullish = sum(1 for p in combined['patterns'] if p['direction'] == 'bullish')
            bearish = sum(1 for p in combined['patterns'] if p['direction'] == 'bearish')
            
            if bullish > bearish:
                combined['recommendation'] = 'BUY'
                combined['confidence'] = 0.7
            elif bearish > bullish:
                combined['recommendation'] = 'SELL'
                combined['confidence'] = 0.7
            else:
                combined['recommendation'] = 'HOLD'
                combined['confidence'] = 0.5
        
        return combined


if __name__ == "__main__":
    # Test
    analyzer = AdvancedChartVision()
    
    print("Advanced Chart Vision Analyzer Ready!")
    print("\nUsage:")
    print("  analyzer = AdvancedChartVision()")
    print("  result = analyzer.analyze_chart_image('chart.png', 'KPIGREEN')")
    print("\nMethods used:")
    print("  1. AI Vision (GPT-4 Vision) - Most accurate")
    print("  2. Computer Vision (OpenCV) - Extract price line")
    print("  3. OCR (Tesseract) - Extract text/prices")
