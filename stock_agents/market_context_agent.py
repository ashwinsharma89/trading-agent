"""
Market Context Agent
Analyzes overall market conditions, sector trends, and timing
"""

from typing import Dict, Any
from stock_agents.base_agent import BaseAgent
from market_data_fetcher import MarketDataFetcher
from commodity_data_fetcher import (
    fetch_commodity_snapshot,
    evaluate_sector_pressure,
)
import logging

logger = logging.getLogger(__name__)


class MarketContextAgent(BaseAgent):
    """
    Specialized agent for market context and timing analysis
    """
    
    def __init__(self, weight: float = 0.15):
        super().__init__("Market Context Agent", weight)
        self.fetcher = MarketDataFetcher()
        # Default sector basket for signal generation
        self.sector_watchlist = {
            "Information Technology": ["TCS.NS", "INFY.NS", "HCLTECH.NS"],
            "Banking & Financial Services": ["HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS"],
            "Energy": ["RELIANCE.NS", "ONGC.NS", "COALINDIA.NS"],
            "Automobile & Auto Components": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS"],
            "Pharmaceuticals": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS"],
            "Infrastructure": ["LT.NS", "ABB.NS", "SIEMENS.NS"],
            "FMCG": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS"],
            "Metals & Mining": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS"],
        }
        
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
        
        # Sector analysis using live basket data
        sector_strength = 'NEUTRAL'
        sector_metrics = self.fetcher.get_sector_data(self.sector_watchlist)
        if sector_metrics:
            # Find best match key
            selected_key = None
            for key in sector_metrics.keys():
                if key.lower() in sector.lower():
                    selected_key = key
                    break
            selected_key = selected_key or next(iter(sector_metrics.keys()))
            metrics = sector_metrics.get(selected_key)
            if metrics:
                change = metrics['change']
                score_adjust = metrics['score'] * 20 - 10  # map 0-1 to -10..+10
                score += score_adjust
                if change > 0:
                    sector_strength = 'STRONG'
                    reasoning.append(
                        f"✅ Sector momentum positive - {selected_key} avg change {change:+.2f}%"
                    )
                elif change < 0:
                    sector_strength = 'WEAK'
                    reasoning.append(
                        f"⚠️ Sector underperforming - {selected_key} avg change {change:+.2f}%"
                    )
                else:
                    sector_strength = 'NEUTRAL'
                    reasoning.append(f"Neutral sector - {selected_key}")
        else:
            reasoning.append("⚠️ Unable to compute sector metrics")

        # Commodity overlay for the sector
        commodity_pressure = {}
        try:
            commodity_snapshots = fetch_commodity_snapshot()
            commodity_pressure = evaluate_sector_pressure(sector, commodity_snapshots)
            headwinds = [name for name, status in commodity_pressure.items() if status == 'HEADWIND']
            tailwinds = [name for name, status in commodity_pressure.items() if status == 'TAILWIND']
            if headwinds:
                score -= 5 * len(headwinds)
                reasoning.append(
                    f"⚠️ Commodity headwinds: {', '.join(headwinds)} elevated for {sector}"
                )
            if tailwinds:
                score += 5 * len(tailwinds)
                reasoning.append(
                    f"✅ Commodity tailwinds: {', '.join(tailwinds)} supportive for {sector}"
                )
        except Exception as exc:
            reasoning.append(f"⚠️ Commodity feed unavailable: {exc}")
            commodity_pressure = {}
        
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
            'commodity_pressure': commodity_pressure,
            'metrics': {
                'nifty_change': nifty_data['change_pct'] if nifty_data else None,
                'nifty_rsi': nifty_data['rsi'] if nifty_data else None,
                'sector': sector
            }
        }
