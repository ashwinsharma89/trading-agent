"""
Market Context Agent
Analyzes overall market conditions, sector trends, and timing
"""

from typing import Dict, Any
from stock_agents.base_agent import BaseAgent
from market_data_fetcher import MarketDataFetcher
import logging

logger = logging.getLogger(__name__)


class MarketContextAgent(BaseAgent):
    """
    Specialized agent for market context and timing analysis
    """
    
    def __init__(self, weight: float = 0.15):
        super().__init__("Market Context Agent", weight)
        self.fetcher = MarketDataFetcher()
        
    def analyze(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market context and timing
        """
        self.validate_state(state, ['ticker'])
        
        ticker = state['ticker']
        fundamental_data = state.get('fundamental_data', {})
        sector = fundamental_data.get('sector', 'Unknown')
        
        # Fetch Nifty 50 data for market context
        try:
            nifty_data = self.fetcher.fetch_stock_data('^NSEI', period="3mo", interval="1d")
        except:
            nifty_data = None
        
        score = 60  # Start neutral
        reasoning = []
        
        # Market regime analysis
        if nifty_data:
            nifty_change = nifty_data['change_pct']
            nifty_rsi = nifty_data['rsi']
            nifty_structure = nifty_data['structure']
            
            if nifty_structure == 'Bullish':
                score += 15
                reasoning.append(f"✅ Bullish market regime - Nifty structure positive")
                regime = 'BULL'
            elif nifty_structure == 'Bearish':
                score -= 15
                reasoning.append(f"⚠️ Bearish market regime - Nifty structure negative")
                regime = 'BEAR'
            else:
                score += 5
                reasoning.append(f"Neutral market regime")
                regime = 'NEUTRAL'
            
            if nifty_rsi > 70:
                score -= 10
                reasoning.append(f"⚠️ Market overbought - Nifty RSI {nifty_rsi:.1f}")
            elif nifty_rsi < 30:
                score += 10
                reasoning.append(f"✅ Market oversold - Nifty RSI {nifty_rsi:.1f}")
            
            if abs(nifty_change) > 2:
                score -= 5
                reasoning.append(f"⚠️ High market volatility - Nifty {nifty_change:+.1f}%")
        else:
            regime = 'UNKNOWN'
            reasoning.append("⚠️ Unable to fetch market data")
        
        # Sector analysis (simplified - would fetch sector index in production)
        sector_strength = 'NEUTRAL'
        
        if sector in ['Information Technology', 'Renewable Energy', 'Electric Vehicles']:
            score += 10
            reasoning.append(f"✅ Strong sector momentum - {sector}")
            sector_strength = 'STRONG'
        elif sector in ['Banking', 'Infrastructure', 'Pharmaceuticals']:
            score += 5
            reasoning.append(f"Favorable sector - {sector}")
            sector_strength = 'FAVORABLE'
        elif sector in ['Real Estate', 'Telecom']:
            score -= 5
            reasoning.append(f"⚠️ Weak sector - {sector}")
            sector_strength = 'WEAK'
        else:
            reasoning.append(f"Neutral sector - {sector}")
        
        # Timing analysis
        # In production, would check:
        # - FII/DII flows
        # - VIX levels
        # - Earnings season
        # - Economic calendar
        
        timing_score = 'GOOD'
        if score >= 70:
            timing_score = 'EXCELLENT'
        elif score < 50:
            timing_score = 'POOR'
        
        reasoning.append(f"Market timing: {timing_score}")
        
        # Normalize score
        score = max(0, min(100, score))
        
        # Determine signal
        if score >= 70:
            signal = 'FAVORABLE'
        elif score >= 50:
            signal = 'NEUTRAL'
        else:
            signal = 'UNFAVORABLE'
        
        return {
            'signal': signal,
            'strength': int(score),
            'confidence': 70,  # Market context is less certain
            'reasoning': reasoning,
            'market_regime': regime,
            'sector_strength': sector_strength,
            'timing': timing_score,
            'metrics': {
                'nifty_change': nifty_data['change_pct'] if nifty_data else None,
                'nifty_rsi': nifty_data['rsi'] if nifty_data else None,
                'sector': sector
            }
        }
