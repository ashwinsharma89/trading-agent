"""
False Breakout Detection - Enterprise Stock Trading Framework
How the system identifies false breakouts and breakdowns using Smart Money Concepts
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

class FalseBreakoutDetector:
    """
    Advanced false breakout detection using Smart Money Concepts
    """
    
    def __init__(self):
        self.confidence_threshold = 0.7
        self.volume_multiplier = 1.5
        self.price_tolerance = 0.01  # 1%
    
    def analyze_false_breakout_potential(self, df: pd.DataFrame, breakout_level: float, direction: str = "bullish") -> Dict:
        """
        Comprehensive analysis to determine if a breakout is likely false
        
        Args:
            df: OHLCV data
            breakout_level: Price level that was broken
            direction: "bullish" for upside breakout, "bearish" for downside breakdown
        
        Returns:
            Dict with false breakout probability and reasoning
        """
        
        analysis = {
            "false_breakout_probability": 0.0,
            "confidence": 0.0,
            "warning_signals": [],
            "smart_money_indicators": {},
            "volume_analysis": {},
            "price_action_analysis": {},
            "recommendation": "WAIT_FOR_CONFIRMATION"
        }
        
        # 1. Volume Analysis (Critical for false breakout detection)
        volume_signals = self._analyze_breakout_volume(df, breakout_level, direction)
        analysis["volume_analysis"] = volume_signals
        
        # 2. Price Action Analysis
        price_signals = self._analyze_price_action(df, breakout_level, direction)
        analysis["price_action_analysis"] = price_signals
        
        # 3. Smart Money Concepts Analysis
        smc_signals = self._analyze_smart_money_concepts(df, breakout_level, direction)
        analysis["smart_money_indicators"] = smc_signals
        
        # 4. Liquidity Analysis
        liquidity_signals = self._analyze_liquidity_grab(df, breakout_level, direction)
        analysis["liquidity_analysis"] = liquidity_signals
        
        # 5. Market Structure Analysis
        structure_signals = self._analyze_market_structure(df, breakout_level, direction)
        analysis["structure_analysis"] = structure_signals
        
        # Calculate overall false breakout probability
        analysis = self._calculate_false_breakout_probability(analysis)
        
        return analysis
    
    def _analyze_breakout_volume(self, df: pd.DataFrame, breakout_level: float, direction: str) -> Dict:
        """Analyze volume characteristics of the breakout"""
        
        if len(df) < 10:
            return {"signal": "INSUFFICIENT_DATA", "confidence": 0.0}
        
        # Recent volume analysis
        recent_volume = df['volume'].tail(5)
        avg_volume = df['volume'].tail(20).mean()
        volume_ratio = recent_volume.iloc[-1] / avg_volume
        
        # Volume trend
        volume_trend = "increasing" if recent_volume.is_monotonic_increasing else "decreasing"
        
        signals = []
        false_breakout_score = 0
        
        # Signal 1: Low volume breakout (high probability of being false)
        if volume_ratio < 1.2:  # Less than 20% above average
            signals.append("LOW_VOLUME_BREAKOUT")
            false_breakout_score += 0.3
        
        # Signal 2: Volume drying up after breakout
        if len(recent_volume) >= 3:
            if recent_volume.iloc[-1] < recent_volume.iloc[-2] < recent_volume.iloc[-3]:
                signals.append("VOLUME_DRYING_UP")
                false_breakout_score += 0.25
        
        # Signal 3: Exhaustive volume (climax top/bottom)
        if volume_ratio > 3.0:  # Extremely high volume
            signals.append("EXHAUSTIVE_VOLUME")
            false_breakout_score += 0.2
        
        # Signal 4: Volume divergence
        if direction == "bullish":
            price_increasing = df['close'].tail(3).is_monotonic_increasing
            volume_decreasing = recent_volume.tail(3).is_monotonic_decreasing
            if price_increasing and volume_decreasing:
                signals.append("VOLUME_DIVERGENCE")
                false_breakout_score += 0.25
        
        return {
            "volume_ratio": volume_ratio,
            "volume_trend": volume_trend,
            "signals": signals,
            "false_breakout_score": min(1.0, false_breakout_score),
            "confidence": len(signals) / 4.0
        }
    
    def _analyze_price_action(self, df: pd.DataFrame, breakout_level: float, direction: str) -> Dict:
        """Analyze price action patterns for false breakout signals"""
        
        if len(df) < 5:
            return {"signal": "INSUFFICIENT_DATA", "confidence": 0.0}
        
        signals = []
        false_breakout_score = 0
        
        # Recent candles
        last_candle = df.iloc[-1]
        second_last = df.iloc[-2]
        third_last = df.iloc[-3]
        
        # Signal 1: Immediate rejection after breakout
        if direction == "bullish":
            if (last_candle['high'] > breakout_level and 
                last_candle['close'] < breakout_level * 0.995):
                signals.append("IMMEDIATE_REJECTION")
                false_breakout_score += 0.35
        else:  # bearish
            if (last_candle['low'] < breakout_level and 
                last_candle['close'] > breakout_level * 1.005):
                signals.append("IMMEDIATE_REJECTION")
                false_breakout_score += 0.35
        
        # Signal 2: Long wicks at breakout level
        if direction == "bullish":
            wick_ratio = (last_candle['high'] - last_candle['close']) / (last_candle['high'] - last_candle['low'])
            if wick_ratio > 0.6:  # More than 60% upper wick
                signals.append("UPPER_WICK_REJECTION")
                false_breakout_score += 0.25
        else:
            wick_ratio = (last_candle['close'] - last_candle['low']) / (last_candle['high'] - last_candle['low'])
            if wick_ratio > 0.6:  # More than 60% lower wick
                signals.append("LOWER_WICK_REJECTION")
                false_breakout_score += 0.25
        
        # Signal 3: Failed follow-through
        if len(df) >= 3:
            if direction == "bullish":
                if (second_last['close'] > breakout_level and 
                    last_candle['close'] < second_last['close']):
                    signals.append("FAILED_FOLLOW_THROUGH")
                    false_breakout_score += 0.2
            else:
                if (second_last['close'] < breakout_level and 
                    last_candle['close'] > second_last['close']):
                    signals.append("FAILED_FOLLOW_THROUGH")
                    false_breakout_score += 0.2
        
        # Signal 4: Quick reversal pattern
        if len(df) >= 3:
            if direction == "bullish":
                if (third_last['close'] < breakout_level and
                    second_last['close'] > breakout_level and
                    last_candle['close'] < breakout_level):
                    signals.append("QUICK_REVERSAL")
                    false_breakout_score += 0.3
            else:
                if (third_last['close'] > breakout_level and
                    second_last['close'] < breakout_level and
                    last_candle['close'] > breakout_level):
                    signals.append("QUICK_REVERSAL")
                    false_breakout_score += 0.3
        
        return {
            "signals": signals,
            "false_breakout_score": min(1.0, false_breakout_score),
            "confidence": len(signals) / 4.0
        }
    
    def _analyze_smart_money_concepts(self, df: pd.DataFrame, breakout_level: float, direction: str) -> Dict:
        """Analyze Smart Money Concepts for false breakout detection"""
        
        signals = []
        false_breakout_score = 0
        
        # 1. Fair Value Gap Analysis
        fvg_signals = self._analyze_fvg_at_breakout(df, breakout_level, direction)
        if fvg_signals["is_false_breakout_likely"]:
            signals.extend(fvg_signals["signals"])
            false_breakout_score += fvg_signals["score"]
        
        # 2. Order Block Analysis
        ob_signals = self._analyze_order_blocks_at_breakout(df, breakout_level, direction)
        if ob_signals["is_false_breakout_likely"]:
            signals.extend(ob_signals["signals"])
            false_breakout_score += ob_signals["score"]
        
        # 3. Market Structure Analysis
        structure_signals = self._analyze_structure_at_breakout(df, breakout_level, direction)
        if structure_signals["is_false_breakout_likely"]:
            signals.extend(structure_signals["signals"])
            false_breakout_score += structure_signals["score"]
        
        return {
            "signals": signals,
            "false_breakout_score": min(1.0, false_breakout_score),
            "confidence": len(signals) / 6.0  # Max 6 signals possible
        }
    
    def _analyze_fvg_at_breakout(self, df: pd.DataFrame, breakout_level: float, direction: str) -> Dict:
        """Analyze Fair Value Gaps around breakout level"""
        
        signals = []
        score = 0
        
        # Look for FVGs that might indicate false breakout
        for i in range(2, len(df)):
            candle_1 = df.iloc[i-2]
            candle_2 = df.iloc[i-1]
            
            # Check for FVG near breakout level
            if direction == "bullish":
                # Bullish FVG above breakout level (could be filled and reverse)
                if (candle_1['high'] < candle_2['low'] and
                    candle_2['low'] > breakout_level and
                    candle_2['low'] < breakout_level * 1.02):
                    signals.append("FVG_RESISTANCE_ABOVE")
                    score += 0.2
            else:
                # Bearish FVG below breakout level
                if (candle_1['low'] > candle_2['high'] and
                    candle_2['high'] < breakout_level and
                    candle_2['high'] > breakout_level * 0.98):
                    signals.append("FVG_SUPPORT_BELOW")
                    score += 0.2
        
        return {
            "signals": signals,
            "score": score,
            "is_false_breakout_likely": len(signals) > 0
        }
    
    def _analyze_order_blocks_at_breakout(self, df: pd.DataFrame, breakout_level: float, direction: str) -> Dict:
        """Analyze Order Blocks around breakout level"""
        
        signals = []
        score = 0
        
        # Look for order blocks near breakout level
        for i in range(1, len(df)):
            prev_candle = df.iloc[i-1]
            curr_candle = df.iloc[i]
            
            if direction == "bullish":
                # Sell order block above breakout level (resistance)
                if (prev_candle['close'] > prev_candle['open'] and  # Green candle
                    curr_candle['close'] < curr_candle['open'] and  # Red candle
                    prev_candle['high'] > breakout_level and
                    prev_candle['high'] < breakout_level * 1.02):
                    signals.append("SELL_ORDER_BLOCK_RESISTANCE")
                    score += 0.25
            else:
                # Buy order block below breakout level (support)
                if (prev_candle['close'] < prev_candle['open'] and  # Red candle
                    curr_candle['close'] > curr_candle['open'] and  # Green candle
                    prev_candle['low'] < breakout_level and
                    prev_candle['low'] > breakout_level * 0.98):
                    signals.append("BUY_ORDER_BLOCK_SUPPORT")
                    score += 0.25
        
        return {
            "signals": signals,
            "score": score,
            "is_false_breakout_likely": len(signals) > 0
        }
    
    def _analyze_structure_at_breakout(self, df: pd.DataFrame, breakout_level: float, direction: str) -> Dict:
        """Analyze Market Structure at breakout"""
        
        signals = []
        score = 0
        
        # Check for CHOCH (Change of Character) - potential false breakout
        if len(df) >= 5:
            recent_lows = df['low'].rolling(3, center=True).min()
            recent_highs = df['high'].rolling(3, center=True).max()
            
            if direction == "bullish":
                # Look for CHOCH pattern (lower low then higher high)
                for i in range(3, len(df) - 2):
                    if (recent_lows.iloc[i] == df.iloc[i]['low'] and
                        df.iloc[i+2]['high'] > df.iloc[i-2]['high'] and
                        df.iloc[i+2]['close'] < df.iloc[i+2]['high'] * 0.98):  # Rejection
                        signals.append("CHOCH_REJECTION")
                        score += 0.3
            else:
                # Bearish CHOCH
                for i in range(3, len(df) - 2):
                    if (recent_highs.iloc[i] == df.iloc[i]['high'] and
                        df.iloc[i+2]['low'] < df.iloc[i-2]['low'] and
                        df.iloc[i+2]['close'] > df.iloc[i+2]['low'] * 1.02):  # Rejection
                        signals.append("CHOCH_REJECTION")
                        score += 0.3
        
        return {
            "signals": signals,
            "score": score,
            "is_false_breakout_likely": len(signals) > 0
        }
    
    def _analyze_liquidity_grab(self, df: pd.DataFrame, breakout_level: float, direction: str) -> Dict:
        """Analyze if breakout is a liquidity grab"""
        
        signals = []
        score = 0
        
        if len(df) < 5:
            return {"signals": signals, "score": score, "is_false_breakout_likely": False}
        
        # Look for equal highs/lows being taken
        recent_highs = []
        recent_lows = []
        
        for i in range(len(df) - 3, len(df)):
            recent_highs.append(df.iloc[i]['high'])
            recent_lows.append(df.iloc[i]['low'])
        
        # Check for liquidity grab pattern
        if direction == "bullish":
            # Take out equal highs then reverse
            if len(recent_highs) >= 3:
                high_range = max(recent_highs) - min(recent_highs)
                if high_range < breakout_level * 0.005:  # Within 0.5%
                    last_candle = df.iloc[-1]
                    if (last_candle['high'] > max(recent_highs) and
                        last_candle['close'] < last_candle['open']):
                        signals.append("LIQUIDITY_GRAB_HIGHS")
                        score += 0.4
        else:
            # Take out equal lows then reverse
            if len(recent_lows) >= 3:
                low_range = max(recent_lows) - min(recent_lows)
                if low_range < breakout_level * 0.005:  # Within 0.5%
                    last_candle = df.iloc[-1]
                    if (last_candle['low'] < min(recent_lows) and
                        last_candle['close'] > last_candle['open']):
                        signals.append("LIQUIDITY_GRAB_LOWS")
                        score += 0.4
        
        return {
            "signals": signals,
            "score": score,
            "is_false_breakout_likely": len(signals) > 0
        }
    
    def _analyze_market_structure(self, df: pd.DataFrame, breakout_level: float, direction: str) -> Dict:
        """Analyze overall market structure context"""
        
        signals = []
        score = 0
        
        if len(df) < 20:
            return {"signals": signals, "score": score, "is_false_breakout_likely": False}
        
        # Determine trend
        sma_20 = df['close'].rolling(20).mean().iloc[-1]
        sma_50 = df['close'].rolling(50).mean().iloc[-1]
        current_price = df['close'].iloc[-1]
        
        # Signal 1: Breakout against major trend
        if direction == "bullish" and current_price < sma_50:
            signals.append("BREAKOUT_AGAINST_DOWNTREND")
            score += 0.2
        elif direction == "bearish" and current_price > sma_50:
            signals.append("BREAKOUT_AGAINST_UPTREND")
            score += 0.2
        
        # Signal 2: Breakout at overbought/oversold levels
        rsi = self._calculate_rsi(df['close'])
        if direction == "bullish" and rsi > 70:
            signals.append("BREAKOUT_AT_OVERBOUGHT")
            score += 0.15
        elif direction == "bearish" and rsi < 30:
            signals.append("BREAKOUT_AT_OVERSOLD")
            score += 0.15
        
        return {
            "signals": signals,
            "score": score,
            "is_false_breakout_likely": len(signals) > 0
        }
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs.iloc[-1]))
    
    def _calculate_false_breakout_probability(self, analysis: Dict) -> Dict:
        """Calculate overall false breakout probability"""
        
        # Weight different analysis components
        weights = {
            "volume_analysis": 0.25,
            "price_action_analysis": 0.25,
            "smart_money_indicators": 0.30,
            "liquidity_analysis": 0.10,
            "structure_analysis": 0.10
        }
        
        total_score = 0
        total_weight = 0
        all_signals = []
        
        for component, weight in weights.items():
            if component in analysis:
                component_score = analysis[component].get("false_breakout_score", 0)
                component_confidence = analysis[component].get("confidence", 0)
                
                # Weight by confidence
                weighted_score = component_score * component_confidence * weight
                total_score += weighted_score
                total_weight += component_confidence * weight
                
                # Collect all warning signals
                signals = analysis[component].get("signals", [])
                all_signals.extend(signals)
        
        # Calculate final probability
        if total_weight > 0:
            false_breakout_probability = total_score / total_weight
        else:
            false_breakout_probability = 0
        
        # Generate recommendation
        if false_breakout_probability > 0.7:
            recommendation = "HIGH_RISK_FALSE_BREAKOUT"
        elif false_breakout_probability > 0.5:
            recommendation = "WAIT_FOR_CONFIRMATION"
        elif false_breakout_probability > 0.3:
            recommendation = "CAUTIOUS_PARTIAL_ENTRY"
        else:
            recommendation = "LEGITIMATE_BREAKOUT"
        
        analysis.update({
            "false_breakout_probability": false_breakout_probability,
            "confidence": total_weight / sum(weights.values()),
            "warning_signals": all_signals,
            "recommendation": recommendation
        })
        
        return analysis


# Example Usage and Demonstration
def demonstrate_false_breakout_detection():
    """Demonstrate false breakout detection with sample scenarios"""
    
    detector = FalseBreakoutDetector()
    
    print("🎯 False Breakout Detection - Enterprise Trading Framework")
    print("=" * 60)
    
    # Scenario 1: Bullish false breakout with low volume
    print("\n📈 Scenario 1: Bullish False Breakout (Low Volume)")
    print("-" * 50)
    
    # Create sample data for false breakout
    dates = pd.date_range(start='2024-01-01', periods=20, freq='D')
    np.random.seed(42)
    
    # Price data that breaks resistance then fails
    base_price = 100
    prices = []
    volumes = []
    
    for i in range(20):
        if i < 15:
            # Accumulation phase
            price = base_price + np.random.normal(0, 1)
            volume = 100000 + np.random.normal(0, 20000)
        else:
            # False breakout attempt
            if i == 15:
                price = 105.5  # Breakout above 105 resistance
                volume = 80000  # Low volume breakout
            elif i == 16:
                price = 104.8  # Slight rejection
                volume = 70000  # Volume drying up
            else:
                price = 103.2  # Failed breakout
                volume = 60000
        
        prices.append(price)
        volumes.append(max(volume, 10000))
    
    # Create OHLCV data
    data = []
    for i, (price, volume) in enumerate(zip(prices, volumes)):
        high = price * (1 + abs(np.random.normal(0, 0.01)))
        low = price * (1 - abs(np.random.normal(0, 0.01)))
        open_price = np.random.uniform(low, high)
        
        data.append({
            'open': open_price,
            'high': high,
            'low': low,
            'close': price,
            'volume': int(volume)
        })
    
    df = pd.DataFrame(data, index=dates)
    
    # Analyze the false breakout
    breakout_level = 105.0
    analysis = detector.analyze_false_breakout_potential(df, breakout_level, "bullish")
    
    print(f"Breakout Level: ₹{breakout_level:.2f}")
    print(f"False Breakout Probability: {analysis['false_breakout_probability']:.1%}")
    print(f"Confidence: {analysis['confidence']:.1%}")
    print(f"Recommendation: {analysis['recommendation']}")
    print(f"Warning Signals: {', '.join(analysis['warning_signals'])}")
    
    # Detailed breakdown
    print("\n📊 Detailed Analysis:")
    for component, data in analysis.items():
        if component.endswith("_analysis") and isinstance(data, dict):
            print(f"  {component.replace('_', ' ').title()}:")
            print(f"    Score: {data.get('false_breakout_score', 0):.1%}")
            if data.get('signals'):
                print(f"    Signals: {', '.join(data['signals'])}")
    
    # Scenario 2: Legitimate breakout with high volume
    print("\n\n📈 Scenario 2: Legitimate Bullish Breakout (High Volume)")
    print("-" * 50)
    
    # Create sample data for legitimate breakout
    prices_legit = []
    volumes_legit = []
    
    for i in range(20):
        if i < 15:
            # Accumulation phase
            price = base_price + np.random.normal(0, 1)
            volume = 100000 + np.random.normal(0, 20000)
        else:
            # Legitimate breakout
            if i == 15:
                price = 105.8  # Strong breakout
                volume = 300000  # High volume confirmation
            elif i == 16:
                price = 106.5  # Follow through
                volume = 250000  # Sustained volume
            else:
                price = 107.2 + (i-17) * 0.3  # Continued move
                volume = 200000 + np.random.normal(0, 30000)
        
        prices_legit.append(price)
        volumes_legit.append(max(volume, 10000))
    
    # Create OHLCV data for legitimate breakout
    data_legit = []
    for i, (price, volume) in enumerate(zip(prices_legit, volumes_legit)):
        high = price * (1 + abs(np.random.normal(0, 0.01)))
        low = price * (1 - abs(np.random.normal(0, 0.01)))
        open_price = np.random.uniform(low, high)
        
        data_legit.append({
            'open': open_price,
            'high': high,
            'low': low,
            'close': price,
            'volume': int(volume)
        })
    
    df_legit = pd.DataFrame(data_legit, index=dates)
    
    # Analyze the legitimate breakout
    analysis_legit = detector.analyze_false_breakout_potential(df_legit, breakout_level, "bullish")
    
    print(f"Breakout Level: ₹{breakout_level:.2f}")
    print(f"False Breakout Probability: {analysis_legit['false_breakout_probability']:.1%}")
    print(f"Confidence: {analysis_legit['confidence']:.1%}")
    print(f"Recommendation: {analysis_legit['recommendation']}")
    print(f"Warning Signals: {', '.join(analysis_legit['warning_signals']) if analysis_legit['warning_signals'] else 'None'}")
    
    print("\n🎯 Key Takeaways:")
    print("✅ False breakouts typically have:")
    print("   • Low volume (< 1.2x average)")
    print("   • Immediate price rejection")
    print("   • Long wicks at breakout level")
    print("   • Volume drying up after breakout")
    print("   • Liquidity grab patterns")
    print("   • Breakout against major trend")
    
    print("\n✅ Legitimate breakouts typically have:")
    print("   • High volume (> 1.5x average)")
    print("   • Sustained price movement")
    print("   • Follow-through buying/selling")
    print("   • Volume confirmation")
    print("   • Alignment with market structure")


if __name__ == "__main__":
    demonstrate_false_breakout_detection()
