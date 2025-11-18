"""
Deep Chart Analyzer
Uses multiple AI models for superior chart analysis
"""

import os
import base64
import json
import numpy as np
from typing import Dict, List
from PIL import Image
import cv2


class DeepChartAnalyzer:
    """
    Multi-model chart analysis for maximum accuracy
    """
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.models = ['gpt4_vision', 'claude_vision', 'gemini_vision']
    
    def analyze_chart_comprehensive(self, image_path: str) -> Dict:
        """
        Comprehensive analysis using multiple AI models
        """
        results = {
            'image_path': image_path,
            'analyses': {},
            'consensus': {}
        }
        
        # 1. GPT-4 Vision (OpenAI)
        gpt4_result = self._analyze_with_gpt4_vision(image_path)
        if gpt4_result:
            results['analyses']['gpt4'] = gpt4_result
        
        # 2. Claude Vision (Anthropic)
        claude_result = self._analyze_with_claude_vision(image_path)
        if claude_result:
            results['analyses']['claude'] = claude_result
        
        # 3. Computer Vision (OpenCV)
        cv_result = self._analyze_with_opencv(image_path)
        if cv_result:
            results['analyses']['opencv'] = cv_result
        
        # 4. Build consensus
        results['consensus'] = self._build_consensus(results['analyses'])
        
        return results
    
    def _analyze_with_gpt4_vision(self, image_path: str) -> Dict:
        """GPT-4 Vision analysis"""
        try:
            import openai
            
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode()
            
            prompt = """Analyze this stock chart with expert precision:

1. PATTERNS: List ALL chart patterns visible (head & shoulders, triangles, flags, wedges, etc.)
2. TREND: Current trend (strong uptrend/uptrend/sideways/downtrend/strong downtrend)
3. SUPPORT/RESISTANCE: Exact price levels
4. VOLUME: Volume pattern analysis
5. INDICATORS: Any visible indicators (RSI, MACD, moving averages)
6. CANDLESTICKS: Notable candlestick patterns
7. MOMENTUM: Price momentum (accelerating/steady/decelerating)
8. BREAKOUT: Any breakout or breakdown signals
9. RECOMMENDATION: BUY/SELL/HOLD with reasoning
10. CONFIDENCE: 0-100 score

Return detailed JSON."""
            
            response = openai.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                    ]
                }],
                max_tokens=1500,
                temperature=0.2
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"GPT-4 Vision error: {e}")
            return None
    
    def _analyze_with_claude_vision(self, image_path: str) -> Dict:
        """Claude Vision analysis"""
        try:
            import anthropic
            
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode()
            
            client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            
            message = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1500,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data
                            }
                        },
                        {
                            "type": "text",
                            "text": "Analyze this stock chart. Identify patterns, trend, support/resistance, and provide trading recommendation. Return as JSON."
                        }
                    ]
                }]
            )
            
            return json.loads(message.content[0].text)
        except Exception as e:
            print(f"Claude Vision error: {e}")
            return None
    
    def _analyze_with_opencv(self, image_path: str) -> Dict:
        """Computer vision analysis"""
        try:
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Extract features
            features = {
                'edges': self._detect_edges(gray),
                'lines': self._detect_lines(gray),
                'contours': self._detect_contours(gray),
                'trend': self._detect_trend_cv(gray)
            }
            
            return features
        except Exception as e:
            print(f"OpenCV error: {e}")
            return None
    
    def _detect_edges(self, gray_img: np.ndarray) -> int:
        """Count edges (indicates volatility)"""
        edges = cv2.Canny(gray_img, 50, 150)
        return np.sum(edges > 0)
    
    def _detect_lines(self, gray_img: np.ndarray) -> List:
        """Detect trendlines"""
        edges = cv2.Canny(gray_img, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        return lines.tolist() if lines is not None else []
    
    def _detect_contours(self, gray_img: np.ndarray) -> int:
        """Count contours (patterns)"""
        _, thresh = cv2.threshold(gray_img, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return len(contours)
    
    def _detect_trend_cv(self, gray_img: np.ndarray) -> str:
        """Detect trend from image"""
        # Simple: check if right side is higher than left
        h, w = gray_img.shape
        left_avg = np.mean(gray_img[:, :w//3])
        right_avg = np.mean(gray_img[:, 2*w//3:])
        
        if right_avg < left_avg - 10:
            return 'uptrend'
        elif right_avg > left_avg + 10:
            return 'downtrend'
        return 'sideways'
    
    def _build_consensus(self, analyses: Dict) -> Dict:
        """Build consensus from multiple analyses"""
        consensus = {
            'patterns': [],
            'trend': None,
            'recommendation': None,
            'confidence': 0
        }
        
        # Collect all patterns
        all_patterns = []
        for model, analysis in analyses.items():
            if isinstance(analysis, dict) and 'patterns' in analysis:
                all_patterns.extend(analysis.get('patterns', []))
        
        # Count pattern occurrences
        pattern_counts = {}
        for pattern in all_patterns:
            name = pattern.get('name', '')
            if name:
                pattern_counts[name] = pattern_counts.get(name, 0) + 1
        
        # Patterns seen by multiple models are more reliable
        for pattern, count in pattern_counts.items():
            if count >= 2:  # Seen by at least 2 models
                consensus['patterns'].append({
                    'name': pattern,
                    'confidence': count / len(analyses),
                    'verified_by': count
                })
        
        # Trend consensus
        trends = []
        for analysis in analyses.values():
            if isinstance(analysis, dict) and 'trend' in analysis:
                trends.append(analysis['trend'])
        
        if trends:
            consensus['trend'] = max(set(trends), key=trends.count)
        
        # Recommendation consensus
        recommendations = []
        for analysis in analyses.values():
            if isinstance(analysis, dict) and 'recommendation' in analysis:
                recommendations.append(analysis['recommendation'])
        
        if recommendations:
            consensus['recommendation'] = max(set(recommendations), key=recommendations.count)
            consensus['confidence'] = recommendations.count(consensus['recommendation']) / len(recommendations) * 100
        
        return consensus


if __name__ == "__main__":
    analyzer = DeepChartAnalyzer()
    print("Deep Chart Analyzer ready!")
    print("Uses: GPT-4 Vision + Claude Vision + OpenCV")
    print("Provides consensus analysis for maximum accuracy")
