"""
Enhanced Smart Money Concepts (SMC) Analyzer
Sharp, impactful, and efficient analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class SMCAnalyzer:
    """
    Advanced Smart Money Concepts analyzer
    Detects market structure, order blocks, liquidity zones, and FVGs
    """
    
    def __init__(self):
        self.swing_lookback = 5  # Candles to look for swing points
        
    def analyze(self, df: pd.DataFrame) -> Dict:
        """
        Comprehensive SMC analysis
        
        Returns:
            Dictionary with all SMC components
        """
        # Ensure proper column names
        df = df.copy()
        df.columns = [col.capitalize() for col in df.columns]
        
        # Core SMC components
        market_structure = self._detect_market_structure(df)
        order_blocks = self._detect_order_blocks(df)
        liquidity_zones = self._detect_liquidity_zones(df)
        fvg_zones = self._detect_fvg_zones(df)
        bos_choch = self._detect_bos_choch(df, market_structure)
        
        # Smart Money activity
        smart_money_activity = self._analyze_smart_money_activity(
            df, order_blocks, liquidity_zones
        )
        
        # Trading bias and key levels
        bias = self._determine_bias(market_structure, order_blocks, fvg_zones)
        key_levels = self._identify_key_levels(df, order_blocks, liquidity_zones)
        
        return {
            'market_structure': market_structure,
            'order_blocks': order_blocks,
            'liquidity_zones': liquidity_zones,
            'fvg_zones': fvg_zones,
            'bos_choch': bos_choch,
            'smart_money_activity': smart_money_activity,
            'bias': bias,
            'key_levels': key_levels,
            'timestamp': datetime.now().isoformat()
        }
    
    def _detect_market_structure(self, df: pd.DataFrame) -> Dict:
        """
        Detect market structure (HH, HL, LH, LL)
        """
        highs = []
        lows = []
        
        # Find swing highs and lows
        for i in range(self.swing_lookback, len(df) - self.swing_lookback):
            # Swing high
            if df.iloc[i]['High'] == df['High'].iloc[i-self.swing_lookback:i+self.swing_lookback+1].max():
                highs.append({'index': i, 'price': df.iloc[i]['High'], 'date': df.index[i]})
            
            # Swing low
            if df.iloc[i]['Low'] == df['Low'].iloc[i-self.swing_lookback:i+self.swing_lookback+1].min():
                lows.append({'index': i, 'price': df.iloc[i]['Low'], 'date': df.index[i]})
        
        # Determine structure
        if len(highs) >= 2 and len(lows) >= 2:
            recent_highs = highs[-2:]
            recent_lows = lows[-2:]
            
            # Higher Highs and Higher Lows = Bullish
            if (recent_highs[1]['price'] > recent_highs[0]['price'] and 
                recent_lows[1]['price'] > recent_lows[0]['price']):
                structure = 'Bullish (HH, HL)'
                trend = 'bullish'
            # Lower Highs and Lower Lows = Bearish
            elif (recent_highs[1]['price'] < recent_highs[0]['price'] and 
                  recent_lows[1]['price'] < recent_lows[0]['price']):
                structure = 'Bearish (LH, LL)'
                trend = 'bearish'
            # Mixed = Range/Consolidation
            else:
                structure = 'Ranging/Consolidation'
                trend = 'neutral'
        else:
            structure = 'Insufficient Data'
            trend = 'neutral'
        
        return {
            'structure': structure,
            'trend': trend,
            'swing_highs': highs[-3:] if len(highs) >= 3 else highs,
            'swing_lows': lows[-3:] if len(lows) >= 3 else lows,
            'last_high': highs[-1] if highs else None,
            'last_low': lows[-1] if lows else None
        }
    
    def _detect_order_blocks(self, df: pd.DataFrame) -> Dict:
        """
        Detect bullish and bearish order blocks
        Order Block = Last down candle before strong up move (bullish)
                     Last up candle before strong down move (bearish)
        """
        bullish_obs = []
        bearish_obs = []
        
        for i in range(1, len(df) - 1):
            # Bullish Order Block
            # Last red candle before strong green candle
            if (df.iloc[i]['Close'] < df.iloc[i]['Open'] and  # Red candle
                df.iloc[i+1]['Close'] > df.iloc[i+1]['Open'] and  # Next is green
                (df.iloc[i+1]['Close'] - df.iloc[i+1]['Open']) > 
                abs(df.iloc[i]['Close'] - df.iloc[i]['Open']) * 1.5):  # Strong move
                
                bullish_obs.append({
                    'type': 'Bullish OB',
                    'date': df.index[i],
                    'high': df.iloc[i]['High'],
                    'low': df.iloc[i]['Low'],
                    'strength': self._calculate_ob_strength(df, i, 'bullish'),
                    'tested': self._is_ob_tested(df, i, 'bullish')
                })
            
            # Bearish Order Block
            # Last green candle before strong red candle
            if (df.iloc[i]['Close'] > df.iloc[i]['Open'] and  # Green candle
                df.iloc[i+1]['Close'] < df.iloc[i+1]['Open'] and  # Next is red
                abs(df.iloc[i+1]['Close'] - df.iloc[i+1]['Open']) > 
                (df.iloc[i]['Close'] - df.iloc[i]['Open']) * 1.5):  # Strong move
                
                bearish_obs.append({
                    'type': 'Bearish OB',
                    'date': df.index[i],
                    'high': df.iloc[i]['High'],
                    'low': df.iloc[i]['Low'],
                    'strength': self._calculate_ob_strength(df, i, 'bearish'),
                    'tested': self._is_ob_tested(df, i, 'bearish')
                })
        
        # Get most recent untested order blocks
        active_bullish = [ob for ob in bullish_obs if not ob['tested']][-3:]
        active_bearish = [ob for ob in bearish_obs if not ob['tested']][-3:]
        
        return {
            'bullish': active_bullish,
            'bearish': active_bearish,
            'total_bullish': len(bullish_obs),
            'total_bearish': len(bearish_obs)
        }
    
    def _calculate_ob_strength(self, df: pd.DataFrame, index: int, ob_type: str) -> str:
        """Calculate order block strength based on volume and move size"""
        avg_volume = df['Volume'].mean()
        ob_volume = df.iloc[index]['Volume']
        
        volume_ratio = ob_volume / avg_volume if avg_volume > 0 else 1
        
        if volume_ratio > 2.0:
            return 'Strong'
        elif volume_ratio > 1.3:
            return 'Medium'
        else:
            return 'Weak'
    
    def _is_ob_tested(self, df: pd.DataFrame, ob_index: int, ob_type: str) -> bool:
        """Check if order block has been tested (price returned to it)"""
        ob_high = df.iloc[ob_index]['High']
        ob_low = df.iloc[ob_index]['Low']
        
        # Check subsequent candles
        for i in range(ob_index + 2, len(df)):
            if ob_type == 'bullish':
                # Tested if price comes back down to OB
                if df.iloc[i]['Low'] <= ob_high:
                    return True
            else:  # bearish
                # Tested if price comes back up to OB
                if df.iloc[i]['High'] >= ob_low:
                    return True
        
        return False
    
    def _detect_liquidity_zones(self, df: pd.DataFrame) -> Dict:
        """
        Detect liquidity zones (equal highs/lows, stop hunts)
        """
        equal_highs = []
        equal_lows = []
        
        # Find equal highs (within 0.5% of each other)
        highs = df['High'].values
        for i in range(len(highs) - 1):
            for j in range(i + 1, min(i + 20, len(highs))):  # Look ahead 20 candles
                if abs(highs[i] - highs[j]) / highs[i] < 0.005:  # Within 0.5%
                    equal_highs.append({
                        'price': (highs[i] + highs[j]) / 2,
                        'count': 2,
                        'first_date': df.index[i],
                        'last_date': df.index[j]
                    })
        
        # Find equal lows
        lows = df['Low'].values
        for i in range(len(lows) - 1):
            for j in range(i + 1, min(i + 20, len(lows))):
                if abs(lows[i] - lows[j]) / lows[i] < 0.005:
                    equal_lows.append({
                        'price': (lows[i] + lows[j]) / 2,
                        'count': 2,
                        'first_date': df.index[i],
                        'last_date': df.index[j]
                    })
        
        # Detect stop hunts (wicks that quickly reverse)
        stop_hunts = []
        for i in range(1, len(df)):
            # Bullish stop hunt (sweep lows then reverse up)
            if (df.iloc[i]['Low'] < df.iloc[i-1]['Low'] and
                df.iloc[i]['Close'] > df.iloc[i]['Open'] and
                df.iloc[i]['Close'] > df.iloc[i-1]['Close']):
                stop_hunts.append({
                    'type': 'Bullish Sweep',
                    'date': df.index[i],
                    'price': df.iloc[i]['Low']
                })
            
            # Bearish stop hunt (sweep highs then reverse down)
            if (df.iloc[i]['High'] > df.iloc[i-1]['High'] and
                df.iloc[i]['Close'] < df.iloc[i]['Open'] and
                df.iloc[i]['Close'] < df.iloc[i-1]['Close']):
                stop_hunts.append({
                    'type': 'Bearish Sweep',
                    'date': df.index[i],
                    'price': df.iloc[i]['High']
                })
        
        return {
            'equal_highs': equal_highs[-3:] if equal_highs else [],
            'equal_lows': equal_lows[-3:] if equal_lows else [],
            'stop_hunts': stop_hunts[-5:] if stop_hunts else [],
            'liquidity_above': equal_highs[-1]['price'] if equal_highs else None,
            'liquidity_below': equal_lows[-1]['price'] if equal_lows else None
        }
    
    def _detect_fvg_zones(self, df: pd.DataFrame) -> List[Dict]:
        """Detect Fair Value Gaps"""
        fvgs = []
        
        for i in range(1, len(df) - 1):
            # Bullish FVG
            if df.iloc[i-1]['Low'] > df.iloc[i+1]['High']:
                fvgs.append({
                    'type': 'Bullish FVG',
                    'date': df.index[i],
                    'upper': df.iloc[i-1]['Low'],
                    'lower': df.iloc[i+1]['High'],
                    'filled': False
                })
            
            # Bearish FVG
            elif df.iloc[i-1]['High'] < df.iloc[i+1]['Low']:
                fvgs.append({
                    'type': 'Bearish FVG',
                    'date': df.index[i],
                    'upper': df.iloc[i+1]['Low'],
                    'lower': df.iloc[i-1]['High'],
                    'filled': False
                })
        
        return fvgs[-5:] if fvgs else []
    
    def _detect_bos_choch(self, df: pd.DataFrame, market_structure: Dict) -> Dict:
        """
        Detect Break of Structure (BOS) and Change of Character (CHOCH)
        """
        swing_highs = market_structure['swing_highs']
        swing_lows = market_structure['swing_lows']
        
        bos_events = []
        choch_events = []
        
        if len(swing_highs) >= 2:
            last_high = swing_highs[-1]
            prev_high = swing_highs[-2]
            
            # BOS: Breaking previous high in uptrend
            if last_high['price'] > prev_high['price']:
                bos_events.append({
                    'type': 'Bullish BOS',
                    'price': last_high['price'],
                    'date': last_high['date']
                })
        
        if len(swing_lows) >= 2:
            last_low = swing_lows[-1]
            prev_low = swing_lows[-2]
            
            # BOS: Breaking previous low in downtrend
            if last_low['price'] < prev_low['price']:
                bos_events.append({
                    'type': 'Bearish BOS',
                    'price': last_low['price'],
                    'date': last_low['date']
                })
        
        return {
            'last_bos': bos_events[-1] if bos_events else None,
            'last_choch': choch_events[-1] if choch_events else None,
            'bos_count': len(bos_events),
            'choch_count': len(choch_events)
        }
    
    def _analyze_smart_money_activity(self, df: pd.DataFrame, 
                                     order_blocks: Dict, 
                                     liquidity_zones: Dict) -> str:
        """
        Determine smart money activity (Accumulation/Distribution/Manipulation)
        """
        recent_volume = df['Volume'].iloc[-10:].mean()
        avg_volume = df['Volume'].mean()
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
        
        recent_range = df['High'].iloc[-10:].max() - df['Low'].iloc[-10:].min()
        avg_range = (df['High'] - df['Low']).mean()
        range_ratio = recent_range / avg_range if avg_range > 0 else 1
        
        # High volume + low range = Accumulation
        if volume_ratio > 1.3 and range_ratio < 0.8:
            return 'Accumulation 📊'
        
        # High volume + high range = Distribution
        elif volume_ratio > 1.3 and range_ratio > 1.2:
            return 'Distribution 📉'
        
        # Stop hunts detected = Manipulation
        elif len(liquidity_zones['stop_hunts']) > 2:
            return 'Manipulation 🎯'
        
        # Normal activity
        else:
            return 'Neutral Activity ➡️'
    
    def _determine_bias(self, market_structure: Dict, 
                       order_blocks: Dict, 
                       fvg_zones: List[Dict]) -> Dict:
        """
        Determine overall trading bias
        """
        score = 0
        reasons = []
        
        # Market structure
        if market_structure['trend'] == 'bullish':
            score += 3
            reasons.append('Bullish market structure')
        elif market_structure['trend'] == 'bearish':
            score -= 3
            reasons.append('Bearish market structure')
        
        # Order blocks
        if len(order_blocks['bullish']) > len(order_blocks['bearish']):
            score += 2
            reasons.append('More bullish order blocks')
        elif len(order_blocks['bearish']) > len(order_blocks['bullish']):
            score -= 2
            reasons.append('More bearish order blocks')
        
        # FVG zones
        bullish_fvgs = len([f for f in fvg_zones if f['type'] == 'Bullish FVG'])
        bearish_fvgs = len([f for f in fvg_zones if f['type'] == 'Bearish FVG'])
        
        if bullish_fvgs > bearish_fvgs:
            score += 1
            reasons.append('Bullish FVG dominance')
        elif bearish_fvgs > bullish_fvgs:
            score -= 1
            reasons.append('Bearish FVG dominance')
        
        # Determine bias
        if score >= 3:
            bias = 'BULLISH 🟢'
            confidence = min(95, 60 + (score * 5))
        elif score <= -3:
            bias = 'BEARISH 🔴'
            confidence = min(95, 60 + (abs(score) * 5))
        else:
            bias = 'NEUTRAL ⚪'
            confidence = 50
        
        return {
            'bias': bias,
            'confidence': confidence,
            'score': score,
            'reasons': reasons
        }
    
    def _identify_key_levels(self, df: pd.DataFrame, 
                            order_blocks: Dict, 
                            liquidity_zones: Dict) -> Dict:
        """
        Identify key support and resistance levels
        """
        current_price = df['Close'].iloc[-1]
        
        # Collect all potential levels
        levels = []
        
        # From order blocks
        for ob in order_blocks['bullish']:
            levels.append(('Support (OB)', (ob['high'] + ob['low']) / 2))
        
        for ob in order_blocks['bearish']:
            levels.append(('Resistance (OB)', (ob['high'] + ob['low']) / 2))
        
        # From liquidity zones
        if liquidity_zones['liquidity_above']:
            levels.append(('Liquidity Above', liquidity_zones['liquidity_above']))
        
        if liquidity_zones['liquidity_below']:
            levels.append(('Liquidity Below', liquidity_zones['liquidity_below']))
        
        # Find nearest support and resistance
        supports = [l for l in levels if l[1] < current_price]
        resistances = [l for l in levels if l[1] > current_price]
        
        nearest_support = max(supports, key=lambda x: x[1]) if supports else None
        nearest_resistance = min(resistances, key=lambda x: x[1]) if resistances else None
        
        return {
            'current_price': current_price,
            'nearest_support': nearest_support,
            'nearest_resistance': nearest_resistance,
            'all_supports': sorted(supports, key=lambda x: x[1], reverse=True)[:3],
            'all_resistances': sorted(resistances, key=lambda x: x[1])[:3]
        }


if __name__ == "__main__":
    # Test SMC analyzer
    import yfinance as yf
    
    print("\n🎯 Testing Enhanced SMC Analyzer\n")
    
    ticker = yf.Ticker("RELIANCE.NS")
    df = ticker.history(period="3mo", interval="1d")
    
    analyzer = SMCAnalyzer()
    analysis = analyzer.analyze(df)
    
    print(f"Market Structure: {analysis['market_structure']['structure']}")
    print(f"Trend: {analysis['market_structure']['trend']}")
    print(f"\nBullish Order Blocks: {len(analysis['order_blocks']['bullish'])}")
    print(f"Bearish Order Blocks: {len(analysis['order_blocks']['bearish'])}")
    print(f"\nSmart Money Activity: {analysis['smart_money_activity']}")
    print(f"\nBias: {analysis['bias']['bias']}")
    print(f"Confidence: {analysis['bias']['confidence']}%")
    print(f"\nKey Levels:")
    if analysis['key_levels']['nearest_support']:
        print(f"  Support: ₹{analysis['key_levels']['nearest_support'][1]:.2f}")
    if analysis['key_levels']['nearest_resistance']:
        print(f"  Resistance: ₹{analysis['key_levels']['nearest_resistance'][1]:.2f}")
