"""
Technical Analysis Agent
Analyzes price action, indicators, patterns, and Smart Money Concepts
"""

from typing import Dict, Any
from stock_agents.base_agent import BaseAgent
from market_data_fetcher import MarketDataFetcher
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class TechnicalAgent(BaseAgent):
    """
    Specialized agent for technical analysis
    """
    
    def __init__(self, weight: float = 0.35):
        super().__init__("Technical Analysis Agent", weight)
        self.fetcher = MarketDataFetcher()
        
    def analyze(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive technical analysis
        """
        self.validate_state(state, ['ticker', 'strategy'])
        
        ticker = state['ticker']
        strategy = state.get('strategy', 'swing')
        
        # Fetch market data if not already in state
        if 'market_data' not in state:
            market_data = self.fetcher.fetch_stock_data(ticker, period="1y", interval="1d")
            state['market_data'] = market_data
        else:
            market_data = state['market_data']
        
        if not market_data:
            raise ValueError(f"No market data available for {ticker}")

        # Pull recent historical data for advanced diagnostics
        history_df = self.fetcher.yahoo_prov.get_historical_data(ticker, period="6mo", interval="1d")
        if history_df is None or history_df.empty:
            raise ValueError(f"Unable to fetch historical data for {ticker}")
        history_df.columns = [col.lower() for col in history_df.columns]

        false_breakout, false_breakdown = self._detect_false_break_moves(history_df)
        bullish_div, bearish_div = self._detect_rsi_divergence(history_df)
        
        # Extract technical metrics
        current_price = market_data['price']
        rsi = market_data['rsi']
        volume_ratio = market_data['volume_ratio']
        structure = market_data['structure']
        bias = market_data['bias']
        confidence_smc = market_data['confidence']
        active_fvgs = market_data['active_fvgs']
        order_blocks = market_data['order_blocks']
        
        # Scoring logic
        score = 0
        reasoning = []
        
        # RSI Analysis (0-20 points)
        if rsi < 30:
            score += 20
            reasoning.append(f"✅ RSI oversold at {rsi:.1f} - strong buy signal")
        elif rsi < 40:
            score += 15
            reasoning.append(f"✅ RSI at {rsi:.1f} - bullish")
        elif rsi > 70:
            score -= 20
            reasoning.append(f"⚠️ RSI overbought at {rsi:.1f} - caution")
        elif rsi > 60:
            score += 5
            reasoning.append(f"RSI at {rsi:.1f} - neutral to bullish")
        else:
            score += 10
            reasoning.append(f"RSI at {rsi:.1f} - neutral")

        if bullish_div:
            score += 8
            reasoning.append("✅ Bullish RSI divergence detected")
        if bearish_div:
            score -= 8
            reasoning.append("⚠️ Bearish RSI divergence detected")
        
        # Volume Analysis (0-15 points)
        if volume_ratio > 2.0:
            score += 15
            reasoning.append(f"✅ High volume {volume_ratio:.1f}x - strong conviction")
        elif volume_ratio > 1.5:
            score += 10
            reasoning.append(f"✅ Above average volume {volume_ratio:.1f}x")
        elif volume_ratio < 0.5:
            score -= 10
            reasoning.append(f"⚠️ Low volume {volume_ratio:.1f}x - weak signal")
        else:
            score += 5
            reasoning.append(f"Volume at {volume_ratio:.1f}x average")
        
        # Smart Money Concepts (0-30 points)
        if structure == 'Bullish':
            score += 15
            reasoning.append(f"✅ Bullish market structure")
        elif structure == 'Bearish':
            score -= 15
            reasoning.append(f"⚠️ Bearish market structure")
        
        if bias == 'BULLISH':
            score += 10
            reasoning.append(f"✅ Bullish bias detected")
        elif bias == 'BEARISH':
            score -= 10
            reasoning.append(f"⚠️ Bearish bias detected")
        
        score += min(confidence_smc / 10, 5)  # Max 5 points from SMC confidence
        
        # FVG Analysis (0-10 points)
        if active_fvgs > 0:
            score += min(active_fvgs * 3, 10)
            reasoning.append(f"✅ {active_fvgs} active Fair Value Gaps")
        
        # Order Blocks (0-10 points)
        if order_blocks > 0:
            score += min(order_blocks * 2, 10)
            reasoning.append(f"✅ {order_blocks} order blocks identified")

        if false_breakout:
            score -= 10
            reasoning.append("⚠️ Possible bull trap (false breakout above resistance)")
        if false_breakdown:
            score += 10
            reasoning.append("✅ Bear trap (false breakdown) – potential short-cover rally")
        
        # Price momentum (0-15 points)
        price_change = market_data['change_pct']
        if price_change > 5:
            score += 15
            reasoning.append(f"✅ Strong upward momentum +{price_change:.1f}%")
        elif price_change > 2:
            score += 10
            reasoning.append(f"✅ Positive momentum +{price_change:.1f}%")
        elif price_change < -5:
            score -= 15
            reasoning.append(f"⚠️ Strong downward momentum {price_change:.1f}%")
        elif price_change < -2:
            score -= 10
            reasoning.append(f"⚠️ Negative momentum {price_change:.1f}%")
        
        # Normalize score to 0-100
        score = max(0, min(100, score))
        
        # Determine signal
        if score >= 75:
            signal = 'STRONG_BUY'
        elif score >= 60:
            signal = 'BUY'
        elif score >= 40:
            signal = 'HOLD'
        elif score >= 25:
            signal = 'SELL'
        else:
            signal = 'STRONG_SELL'
        
        # Calculate confidence based on data quality
        confidence = min(100, score + confidence_smc / 2)
        
        return {
            'signal': signal,
            'strength': score,
            'confidence': int(confidence),
            'reasoning': reasoning,
            'metrics': {
                'rsi': rsi,
                'volume_ratio': volume_ratio,
                'structure': structure,
                'bias': bias,
                'price_change': price_change,
                'active_fvgs': active_fvgs,
                'order_blocks': order_blocks,
                'false_breakout': false_breakout,
                'false_breakdown': false_breakdown,
                'bullish_rsi_divergence': bullish_div,
                'bearish_rsi_divergence': bearish_div
            }
        }

    def _detect_false_break_moves(self, df: pd.DataFrame) -> (bool, bool):
        """Identify recent false breakout/breakdown events."""
        window = min(30, len(df))
        if window < 10:
            return False, False
        recent = df.tail(window)
        close = recent['close'].values
        highs = recent['high'].values
        lows = recent['low'].values

        prior_high = np.max(highs[:-2])
        prior_low = np.min(lows[:-2])
        prev_close = close[-2]
        last_close = close[-1]

        false_breakout = prev_close > prior_high and last_close < prior_high
        false_breakdown = prev_close < prior_low and last_close > prior_low
        return bool(false_breakout), bool(false_breakdown)

    def _detect_rsi_divergence(self, df: pd.DataFrame) -> (bool, bool):
        """Detect simple RSI divergences using recent swings."""
        closes = df['close']
        if len(closes) < 20:
            return False, False

        returns = closes.pct_change()
        gain = returns.where(returns > 0, 0).rolling(14).mean()
        loss = -returns.where(returns < 0, 0).rolling(14).mean()
        rs = gain / loss
        rsi_series = 100 - (100 / (1 + rs))

        recent_window = 10
        prior_window = 10
        recent_prices = closes.iloc[-recent_window:]
        prior_prices = closes.iloc[-(recent_window + prior_window):-recent_window]
        recent_rsi = rsi_series.iloc[-recent_window:]
        prior_rsi = rsi_series.iloc[-(recent_window + prior_window):-recent_window]

        if prior_prices.empty or prior_rsi.empty:
            return False, False

        bullish_div = (
            recent_prices.min() < prior_prices.min() and
            recent_rsi.min() > prior_rsi.min()
        )
        bearish_div = (
            recent_prices.max() > prior_prices.max() and
            recent_rsi.max() < prior_rsi.max()
        )
        return bool(bullish_div), bool(bearish_div)
