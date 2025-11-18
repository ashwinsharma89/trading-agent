"""
Earnings Call Analyzer
Extracts insights from earnings call transcripts
"""

import os
import requests
from typing import Dict, Any, List
from datetime import datetime
import json


class EarningsCallAnalyzer:
    """
    Analyze earnings call transcripts for sentiment and insights
    """
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.cache_dir = 'data/earnings_calls'
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def fetch_transcript(self, ticker: str) -> str:
        """
        Fetch latest earnings call transcript
        Uses: Seeking Alpha, Yahoo Finance, or company IR page
        """
        # Check cache first
        cache_file = f"{self.cache_dir}/{ticker}_latest.txt"
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return f.read()
        
        # Try multiple sources
        transcript = None
        
        # Source 1: Seeking Alpha (requires scraping or API)
        # Source 2: Yahoo Finance
        # Source 3: Company IR page
        
        # For now, placeholder - you'd implement actual fetching
        transcript = self._fetch_from_sources(ticker)
        
        if transcript:
            # Cache it
            with open(cache_file, 'w') as f:
                f.write(transcript)
        
        return transcript
    
    def _fetch_from_sources(self, ticker: str) -> str:
        """
        Try multiple sources to get transcript
        """
        # Placeholder - implement actual fetching
        # This would use web scraping or APIs
        return None
    
    def analyze_transcript(self, transcript: str, ticker: str) -> Dict[str, Any]:
        """
        Analyze earnings call using AI
        """
        if not transcript:
            return {
                'available': False,
                'sentiment': 0.5,
                'confidence': 0,
                'insights': []
            }
        
        # Use OpenAI to analyze
        analysis = self._ai_analysis(transcript, ticker)
        
        return {
            'available': True,
            'sentiment': analysis['sentiment'],
            'confidence': analysis['confidence'],
            'management_tone': analysis['tone'],
            'key_points': analysis['key_points'],
            'guidance': analysis['guidance'],
            'concerns': analysis['concerns'],
            'opportunities': analysis['opportunities']
        }
    
    def _ai_analysis(self, transcript: str, ticker: str) -> Dict[str, Any]:
        """
        Use AI to extract insights from transcript
        """
        try:
            import openai
            
            prompt = f"""
            Analyze this earnings call transcript for {ticker}.
            
            Extract:
            1. Overall sentiment (0-1 scale, 0=very negative, 1=very positive)
            2. Management tone (confident/cautious/defensive/optimistic)
            3. Key points mentioned (top 5)
            4. Forward guidance (bullish/neutral/bearish)
            5. Main concerns raised
            6. Growth opportunities mentioned
            7. Confidence level in the analysis (0-1)
            
            Transcript (first 3000 chars):
            {transcript[:3000]}
            
            Return as JSON with keys: sentiment, tone, key_points, guidance, concerns, opportunities, confidence
            """
            
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial analyst expert at analyzing earnings calls."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"AI analysis failed: {e}")
            # Fallback to simple sentiment analysis
            return self._simple_sentiment_analysis(transcript)
    
    def _simple_sentiment_analysis(self, transcript: str) -> Dict[str, Any]:
        """
        Simple keyword-based sentiment analysis (fallback)
        """
        positive_words = ['growth', 'strong', 'increase', 'positive', 'opportunity', 
                         'expansion', 'success', 'improve', 'optimistic', 'confident']
        negative_words = ['decline', 'weak', 'decrease', 'negative', 'concern',
                         'challenge', 'difficult', 'loss', 'cautious', 'uncertain']
        
        text_lower = transcript.lower()
        
        pos_count = sum(text_lower.count(word) for word in positive_words)
        neg_count = sum(text_lower.count(word) for word in negative_words)
        
        total = pos_count + neg_count
        sentiment = pos_count / total if total > 0 else 0.5
        
        return {
            'sentiment': sentiment,
            'tone': 'optimistic' if sentiment > 0.6 else 'cautious' if sentiment < 0.4 else 'neutral',
            'key_points': [],
            'guidance': 'neutral',
            'concerns': [],
            'opportunities': [],
            'confidence': 0.5
        }
    
    def get_historical_accuracy(self, ticker: str) -> float:
        """
        Get historical accuracy of earnings call sentiment predictions
        """
        history_file = f"{self.cache_dir}/{ticker}_history.json"
        
        if not os.path.exists(history_file):
            return 0.5  # Default
        
        with open(history_file, 'r') as f:
            history = json.load(f)
        
        if not history:
            return 0.5
        
        correct = sum(1 for h in history if h.get('correct', False))
        total = len(history)
        
        return correct / total if total > 0 else 0.5
    
    def track_prediction(self, ticker: str, analysis: Dict[str, Any], 
                        current_price: float):
        """
        Track earnings call prediction for future evaluation
        """
        history_file = f"{self.cache_dir}/{ticker}_history.json"
        
        # Load existing history
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        # Add new prediction
        prediction = {
            'date': datetime.now().isoformat(),
            'sentiment': analysis['sentiment'],
            'tone': analysis['management_tone'],
            'current_price': current_price,
            'evaluated': False
        }
        
        history.append(prediction)
        
        # Save
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)


if __name__ == "__main__":
    # Test
    analyzer = EarningsCallAnalyzer()
    
    # Example usage
    ticker = "KPIGREEN"
    transcript = analyzer.fetch_transcript(ticker)
    
    if transcript:
        analysis = analyzer.analyze_transcript(transcript, ticker)
        print(f"Sentiment: {analysis['sentiment']}")
        print(f"Tone: {analysis['management_tone']}")
        print(f"Confidence: {analysis['confidence']}")
    else:
        print("No transcript available")
