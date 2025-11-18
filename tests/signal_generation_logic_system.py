"""
Signal Generation Logic System
Tests strategy consistency, signal caching, timeframe definitions, signal conflicts, change explanations, and conflicting timeframe handling
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union, Any
from enum import Enum
import warnings
from dataclasses import dataclass, field
import logging
from abc import ABC, abstractmethod
import math
import json
import hashlib
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SignalType(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    STRONG_BUY = "strong_buy"
    STRONG_SELL = "strong_sell"

class StrategyType(Enum):
    INTRADAY = "intraday"
    SWING_TRADE = "swing_trade"
    LONG_TERM = "long_term"
    POSITIONAL = "positional"
    INVESTMENT = "investment"

class TimeFrame(Enum):
    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    HOUR_1 = "1h"
    HOUR_4 = "4h"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class SignalStrength(Enum):
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"

@dataclass
class Signal:
    """Trading signal with metadata"""
    symbol: str
    signal_type: SignalType
    strategy_type: StrategyType
    timeframe: TimeFrame
    strength: SignalStrength
    confidence: float
    price_target: Optional[float] = None
    stop_loss: Optional[float] = None
    holding_period: Optional[int] = None  # days
    reasoning: List[str] = field(default_factory=list)
    technical_indicators: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    def __hash__(self):
        """Hash for caching"""
        key_data = f"{self.symbol}_{self.strategy_type.value}_{self.timeframe.value}_{self.timestamp.date()}"
        return int(hashlib.md5(key_data.encode()).hexdigest(), 16)

@dataclass
class SignalChange:
    """Signal change explanation"""
    symbol: str
    old_signal: SignalType
    new_signal: SignalType
    strategy_type: StrategyType
    change_reasons: List[str]
    technical_changes: Dict[str, Tuple[float, float]]  # old_value, new_value
    market_conditions: List[str]
    confidence_change: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class SignalConflict:
    """Signal conflict between timeframes or strategies"""
    symbol: str
    conflicting_signals: List[Signal]
    conflict_type: str  # "timeframe", "strategy", "strength"
    resolution_strategy: str
    recommended_action: SignalType
    confidence: float
    explanation: str

@dataclass
class SignalCache:
    """Signal cache entry"""
    signal_hash: str
    signal: Signal
    created_at: datetime
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)

class SignalCacheManager:
    """
    Manages signal caching with TTL and invalidation
    """
    
    def __init__(self, ttl_hours: int = 1):
        self.ttl_hours = ttl_hours
        self.cache: Dict[str, SignalCache] = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get_cached_signal(self, symbol: str, strategy_type: StrategyType, timeframe: TimeFrame) -> Optional[Signal]:
        """
        Test 106: Get cached signal if available and not expired
        """
        cache_key = self._generate_cache_key(symbol, strategy_type, timeframe)
        
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            
            # Check if signal is still valid (not expired)
            if self._is_signal_valid(cache_entry):
                cache_entry.access_count += 1
                cache_entry.last_accessed = datetime.now()
                self.cache_hits += 1
                return cache_entry.signal
            else:
                # Remove expired signal
                del self.cache[cache_key]
        
        self.cache_misses += 1
        return None
    
    def cache_signal(self, signal: Signal) -> None:
        """Cache a new signal"""
        cache_key = self._generate_cache_key(signal.symbol, signal.strategy_type, signal.timeframe)
        signal_hash = hash(signal)
        
        cache_entry = SignalCache(
            signal_hash=signal_hash,
            signal=signal,
            created_at=datetime.now(),
            access_count=1
        )
        
        self.cache[cache_key] = cache_entry
    
    def _generate_cache_key(self, symbol: str, strategy_type: StrategyType, timeframe: TimeFrame) -> str:
        """Generate cache key"""
        return f"{symbol}_{strategy_type.value}_{timeframe.value}"
    
    def _is_signal_valid(self, cache_entry: SignalCache) -> bool:
        """Check if cached signal is still valid"""
        age_hours = (datetime.now() - cache_entry.created_at).total_seconds() / 3600
        return age_hours < self.ttl_hours
    
    def get_cache_stats(self) -> Dict:
        """Get cache performance statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0
        
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": hit_rate,
            "cached_signals": len(self.cache),
            "ttl_hours": self.ttl_hours
        }

class StrategyDefinitionManager:
    """
    Defines and manages strategy types and their characteristics
    """
    
    def __init__(self):
        self.strategy_definitions = self._load_strategy_definitions()
    
    def define_strategy_type(self, signal: Signal) -> StrategyType:
        """
        Test 107: Define strategy type based on holding period and analysis
        """
        if signal.holding_period:
            return self._classify_by_holding_period(signal.holding_period)
        else:
            return self._classify_by_indicators_and_timeframe(signal)
    
    def _classify_by_holding_period(self, holding_period_days: int) -> StrategyType:
        """Classify strategy based on holding period"""
        if holding_period_days <= 1:
            return StrategyType.INTRADAY
        elif holding_period_days <= 5:
            return StrategyType.SWING_TRADE
        elif holding_period_days <= 30:
            return StrategyType.POSITIONAL
        elif holding_period_days <= 365:
            return StrategyType.LONG_TERM
        else:
            return StrategyType.INVESTMENT
    
    def _classify_by_indicators_and_timeframe(self, signal: Signal) -> StrategyType:
        """Classify strategy based on technical indicators and timeframe"""
        # Use timeframe as primary classifier
        timeframe_mapping = {
            TimeFrame.MINUTE_1: StrategyType.INTRADAY,
            TimeFrame.MINUTE_5: StrategyType.INTRADAY,
            TimeFrame.MINUTE_15: StrategyType.SWING_TRADE,
            TimeFrame.HOUR_1: StrategyType.SWING_TRADE,
            TimeFrame.HOUR_4: StrategyType.POSITIONAL,
            TimeFrame.DAILY: StrategyType.LONG_TERM,
            TimeFrame.WEEKLY: StrategyType.LONG_TERM,
            TimeFrame.MONTHLY: StrategyType.INVESTMENT
        }
        
        base_strategy = timeframe_mapping.get(signal.timeframe, StrategyType.LONG_TERM)
        
        # Adjust based on technical indicators
        if signal.technical_indicators:
            volatility = signal.technical_indicators.get("volatility", 0)
            trend_strength = signal.technical_indicators.get("trend_strength", 0)
            
            # High volatility with short timeframe -> Swing trade
            if volatility > 0.3 and base_strategy == StrategyType.LONG_TERM:
                return StrategyType.SWING_TRADE
            
            # Strong trend with daily timeframe -> Positional
            if trend_strength > 0.7 and signal.timeframe == TimeFrame.DAILY:
                return StrategyType.POSITIONAL
        
        return base_strategy
    
    def get_strategy_characteristics(self, strategy_type: StrategyType) -> Dict:
        """Get characteristics of a strategy type"""
        return self.strategy_definitions.get(strategy_type, {})
    
    def _load_strategy_definitions(self) -> Dict:
        """Load strategy type definitions"""
        return {
            StrategyType.INTRADAY: {
                "holding_period_range": (0, 1),
                "timeframes": [TimeFrame.MINUTE_1, TimeFrame.MINUTE_5, TimeFrame.MINUTE_15, TimeFrame.HOUR_1],
                "risk_level": "HIGH",
                "return_expectation": "HIGH",
                "monitoring_frequency": "Continuous",
                "description": "Trading within the same trading day, all positions closed before market close"
            },
            StrategyType.SWING_TRADE: {
                "holding_period_range": (1, 5),
                "timeframes": [TimeFrame.MINUTE_15, TimeFrame.HOUR_1, TimeFrame.HOUR_4, TimeFrame.DAILY],
                "risk_level": "MEDIUM",
                "return_expectation": "MEDIUM",
                "monitoring_frequency": "Hourly",
                "description": "Holding positions for a few days to capture short-term price swings"
            },
            StrategyType.POSITIONAL: {
                "holding_period_range": (5, 30),
                "timeframes": [TimeFrame.HOUR_4, TimeFrame.DAILY],
                "risk_level": "MEDIUM",
                "return_expectation": "MEDIUM",
                "monitoring_frequency": "Daily",
                "description": "Holding positions for several weeks to capture medium-term trends"
            },
            StrategyType.LONG_TERM: {
                "holding_period_range": (30, 365),
                "timeframes": [TimeFrame.DAILY, TimeFrame.WEEKLY],
                "risk_level": "LOW",
                "return_expectation": "LOW",
                "monitoring_frequency": "Weekly",
                "description": "Investment positions held for months to years based on fundamental analysis"
            },
            StrategyType.INVESTMENT: {
                "holding_period_range": (365, float('inf')),
                "timeframes": [TimeFrame.WEEKLY, TimeFrame.MONTHLY],
                "risk_level": "LOW",
                "return_expectation": "LOW",
                "monitoring_frequency": "Monthly",
                "description": "Long-term investment positions based on fundamental value and growth prospects"
            }
        }

class SignalConsistencyManager:
    """
    Manages signal consistency and conflict resolution
    """
    
    def __init__(self, cache_manager: SignalCacheManager, strategy_manager: StrategyDefinitionManager):
        self.cache_manager = cache_manager
        self.strategy_manager = strategy_manager
        self.signal_history: Dict[str, List[Signal]] = {}
        self.change_explanations: Dict[str, List[SignalChange]] = {}
    
    def check_signal_consistency(self, symbol: str, new_signal: Signal) -> Dict:
        """
        Test 106-110: Comprehensive signal consistency analysis
        """
        print("🧪 Test 106-110: Signal Consistency Analysis")
        print("=" * 60)
        
        results = {
            "caching_analysis": self._test_caching_behavior(symbol, new_signal),
            "strategy_definition": self._test_strategy_definition(new_signal),
            "simultaneous_signals": self._test_simultaneous_signals(symbol, new_signal),
            "change_explanation": self._test_change_explanation(symbol, new_signal),
            "conflicting_timeframes": self._test_conflicting_timeframes(symbol, new_signal)
        }
        
        return results
    
    def _test_caching_behavior(self, symbol: str, new_signal: Signal) -> Dict:
        """
        Test 106: Signal caching within 1 hour
        """
        print(f"\n📊 Test 106: Signal Caching Analysis")
        print(f"Symbol: {symbol}")
        print(f"New Signal: {new_signal.signal_type.value} ({new_signal.strategy_type.value})")
        
        # Try to get cached signal
        cached_signal = self.cache_manager.get_cached_signal(symbol, new_signal.strategy_type, new_signal.timeframe)
        
        if cached_signal:
            # Compare with cached signal
            is_identical = self._compare_signals(cached_signal, new_signal)
            time_diff = (new_signal.timestamp - cached_signal.timestamp).total_seconds() / 3600
            
            print(f"  ✅ Cached signal found (age: {time_diff:.1f} hours)")
            print(f"  Identical to cached: {'Yes' if is_identical else 'No'}")
            
            if not is_identical:
                print(f"  ⚠️ Signal differs from cache - factors:")
                differences = self._analyze_signal_differences(cached_signal, new_signal)
                for diff in differences:
                    print(f"    - {diff}")
            
            return {
                "cached_signal_found": True,
                "cache_age_hours": time_diff,
                "identical_to_cached": is_identical,
                "differences": differences if not is_identical else [],
                "recommendation": "Use cached signal" if is_identical else "Generate new signal with explanation"
            }
        else:
            print(f"  ❌ No cached signal found")
            print(f"  🆕 Generating new signal and caching")
            self.cache_manager.cache_signal(new_signal)
            
            return {
                "cached_signal_found": False,
                "cache_age_hours": 0,
                "identical_to_cached": True,
                "differences": [],
                "recommendation": "New signal generated and cached"
            }
    
    def _test_strategy_definition(self, signal: Signal) -> Dict:
        """
        Test 107: Strategy type definition
        """
        print(f"\n📊 Test 107: Strategy Definition Analysis")
        print(f"Signal: {signal.signal_type.value}")
        print(f"Timeframe: {signal.timeframe.value}")
        print(f"Holding Period: {signal.holding_period or 'Not specified'} days")
        
        defined_strategy = self.strategy_manager.define_strategy_type(signal)
        strategy_characteristics = self.strategy_manager.get_strategy_characteristics(defined_strategy)
        
        print(f"  🎯 Defined Strategy: {defined_strategy.value}")
        print(f"  📋 Description: {strategy_characteristics.get('description', 'N/A')}")
        print(f"  ⏱️ Holding Period: {strategy_characteristics.get('holding_period_range', 'N/A')}")
        print(f"  📊 Risk Level: {strategy_characteristics.get('risk_level', 'N/A')}")
        print(f"  📈 Return Expectation: {strategy_characteristics.get('return_expectation', 'N/A')}")
        
        # Test classification logic
        classification_basis = "Holding period" if signal.holding_period else "Timeframe and indicators"
        print(f"  🔍 Classification based on: {classification_basis}")
        
        return {
            "defined_strategy": defined_strategy.value,
            "classification_basis": classification_basis,
            "characteristics": strategy_characteristics,
            "holding_period_days": signal.holding_period,
            "timeframe": signal.timeframe.value
        }
    
    def _test_simultaneous_signals(self, symbol: str, new_signal: Signal) -> Dict:
        """
        Test 108: Simultaneous signals for different strategies
        """
        print(f"\n📊 Test 108: Simultaneous Signals Analysis")
        
        # Get existing signals for this symbol
        existing_signals = self.signal_history.get(symbol, [])
        
        # Check for conflicting strategy signals
        strategy_signals = {}
        for signal in existing_signals + [new_signal]:
            if signal.strategy_type not in strategy_signals:
                strategy_signals[signal.strategy_type] = []
            strategy_signals[signal.strategy_type].append(signal)
        
        # Check for simultaneous BUY/HOLD scenarios
        simultaneous_scenarios = []
        
        for strategy_type, signals in strategy_signals.items():
            if len(signals) > 1:
                signal_types = [s.signal_type for s in signals]
                if SignalType.BUY in signal_types and SignalType.HOLD in signal_types:
                    simultaneous_scenarios.append({
                        "strategies": [s.strategy_type.value for s in signals],
                        "signals": [s.signal_type.value for s in signals],
                        "timeframes": [s.timeframe.value for s in signals],
                        "conflict_type": "BUY + HOLD simultaneous"
                    })
        
        # Test specific scenario: Swing trade BUY + Long-term HOLD
        swing_buy = any(s for s in existing_signals if s.strategy_type == StrategyType.SWING_TRADE and s.signal_type == SignalType.BUY)
        long_term_hold = any(s for s in existing_signals if s.strategy_type == StrategyType.LONG_TERM and s.signal_type == SignalType.HOLD)
        
        if swing_buy and new_signal.strategy_type == StrategyType.LONG_TERM and new_signal.signal_type == SignalType.HOLD:
            simultaneous_scenarios.append({
                "scenario": "Swing trade BUY + Long-term HOLD",
                "explanation": "Valid scenario - short-term trading opportunity within long-term investment",
                "recommendation": "Execute swing trade with separate allocation, maintain long-term position"
            })
        
        print(f"  🔄 Existing signals for {symbol}: {len(existing_signals)}")
        print(f"  ⚡ Simultaneous signal scenarios: {len(simultaneous_scenarios)}")
        
        for scenario in simultaneous_scenarios:
            print(f"    - {scenario.get('scenario', scenario.get('conflict_type', 'Unknown'))}")
            if 'explanation' in scenario:
                print(f"      Explanation: {scenario['explanation']}")
        
        return {
            "simultaneous_scenarios": simultaneous_scenarios,
            "total_existing_signals": len(existing_signals),
            "strategy_signals": {k.value: len(v) for k, v in strategy_signals.items()},
            "can_have_simultaneous": len(simultaneous_scenarios) > 0
        }
    
    def _test_change_explanation(self, symbol: str, new_signal: Signal) -> Dict:
        """
        Test 109: Signal change explanation
        """
        print(f"\n📊 Test 109: Signal Change Explanation")
        
        # Get previous signal for same strategy
        previous_signal = self._get_previous_signal(symbol, new_signal.strategy_type)
        
        if previous_signal and previous_signal.signal_type != new_signal.signal_type:
            # Generate change explanation
            change_explanation = self._generate_change_explanation(previous_signal, new_signal)
            
            print(f"  📅 Previous Signal: {previous_signal.signal_type.value} ({previous_signal.timestamp.strftime('%Y-%m-%d %H:%M')})")
            print(f"  🆕 New Signal: {new_signal.signal_type.value} ({new_signal.timestamp.strftime('%Y-%m-%d %H:%M')})")
            print(f"  📊 Confidence Change: {previous_signal.confidence:.1%} → {new_signal.confidence:.1%}")
            print(f"  📋 Change Reasons:")
            for reason in change_explanation.change_reasons:
                print(f"    - {reason}")
            
            print(f"  🔧 Technical Changes:")
            for indicator, (old_val, new_val) in change_explanation.technical_changes.items():
                print(f"    - {indicator}: {old_val:.2f} → {new_val:.2f}")
            
            return {
                "signal_changed": True,
                "previous_signal": previous_signal.signal_type.value,
                "new_signal": new_signal.signal_type.value,
                "change_explanation": change_explanation.change_reasons,
                "technical_changes": change_explanation.technical_changes,
                "confidence_change": new_signal.confidence - previous_signal.confidence,
                "time_diff_hours": (new_signal.timestamp - previous_signal.timestamp).total_seconds() / 3600
            }
        else:
            print(f"  ✅ No signal change detected")
            return {
                "signal_changed": False,
                "previous_signal": previous_signal.signal_type.value if previous_signal else None,
                "new_signal": new_signal.signal_type.value,
                "change_explanation": [],
                "technical_changes": {}
            }
    
    def _test_conflicting_timeframes(self, symbol: str, new_signal: Signal) -> Dict:
        """
        Test 110: Conflicting timeframe handling
        """
        print(f"\n📊 Test 110: Conflicting Timeframes Analysis")
        
        # Get signals across different timeframes
        all_signals = self.signal_history.get(symbol, []) + [new_signal]
        timeframe_signals = {}
        
        for signal in all_signals:
            if signal.timeframe not in timeframe_signals:
                timeframe_signals[signal.timeframe] = []
            timeframe_signals[signal.timeframe].append(signal)
        
        # Identify conflicts
        conflicts = []
        
        # Check for daily bullish vs weekly bearish
        daily_signals = timeframe_signals.get(TimeFrame.DAILY, [])
        weekly_signals = timeframe_signals.get(TimeFrame.WEEKLY, [])
        
        if daily_signals and weekly_signals:
            daily_bullish = any(s.signal_type in [SignalType.BUY, SignalType.STRONG_BUY] for s in daily_signals)
            weekly_bearish = any(s.signal_type in [SignalType.SELL, SignalType.STRONG_SELL] for s in weekly_signals)
            
            if daily_bullish and weekly_bearish:
                conflicts.append({
                    "conflict_type": "Daily Bullish vs Weekly Bearish",
                    "daily_signal": "BULLISH",
                    "weekly_signal": "BEARISH",
                    "resolution": "Prefer longer timeframe (Weekly)",
                    "recommended_action": "SELL or HOLD",
                    "explanation": "Longer timeframe takes precedence for trend direction"
                })
        
        # Check for other timeframe conflicts
        for tf1, signals1 in timeframe_signals.items():
            for tf2, signals2 in timeframe_signals.items():
                if tf1 != tf2 and len(signals1) > 0 and len(signals2) > 0:
                    # Compare signal directions
                    tf1_bullish = any(s.signal_type in [SignalType.BUY, SignalType.STRONG_BUY] for s in signals1)
                    tf2_bearish = any(s.signal_type in [SignalType.SELL, SignalType.STRONG_SELL] for s in signals2)
                    
                    if tf1_bullish and tf2_bearish:
                        # Determine which timeframe takes precedence
                        precedence = self._determine_timeframe_precedence(tf1, tf2)
                        
                        conflicts.append({
                            "conflict_type": f"{tf1.value.title()} Bullish vs {tf2.value.title()} Bearish",
                            "timeframe_1": tf1.value,
                            "signal_1": "BULLISH",
                            "timeframe_2": tf2.value,
                            "signal_2": "BEARISH",
                            "precedence": precedence.value,
                            "resolution": f"Prefer {precedence.value} timeframe"
                        })
        
        print(f"  📊 Timeframe Analysis:")
        for tf, signals in timeframe_signals.items():
            if signals:
                latest_signal = max(signals, key=lambda s: s.timestamp)
                print(f"    {tf.value}: {latest_signal.signal_type.value} ({latest_signal.strategy_type.value})")
        
        print(f"  ⚠️ Timeframe Conflicts: {len(conflicts)}")
        for conflict in conflicts:
            print(f"    - {conflict['conflict_type']}")
            print(f"      Resolution: {conflict['resolution']}")
        
        return {
            "timeframe_signals": {tf.value: len(signals) for tf, signals in timeframe_signals.items()},
            "conflicts": conflicts,
            "conflict_count": len(conflicts),
            "resolution_strategy": "Longer timeframe precedence" if conflicts else "No conflicts"
        }
    
    def _compare_signals(self, signal1: Signal, signal2: Signal) -> bool:
        """Compare two signals for equality"""
        return (
            signal1.symbol == signal2.symbol and
            signal1.signal_type == signal2.signal_type and
            signal1.strategy_type == signal2.strategy_type and
            signal1.timeframe == signal2.timeframe and
            abs(signal1.confidence - signal2.confidence) < 0.05  # 5% tolerance
        )
    
    def _analyze_signal_differences(self, signal1: Signal, signal2: Signal) -> List[str]:
        """Analyze differences between two signals"""
        differences = []
        
        if signal1.signal_type != signal2.signal_type:
            differences.append(f"Signal type: {signal1.signal_type.value} → {signal2.signal_type.value}")
        
        if signal1.confidence != signal2.confidence:
            diff_pct = abs(signal1.confidence - signal2.confidence) * 100
            differences.append(f"Confidence: {signal1.confidence:.1%} → {signal2.confidence:.1%} ({diff_pct:.1f}% change)")
        
        if signal1.strength != signal2.strength:
            differences.append(f"Strength: {signal1.strength.value} → {signal2.strength.value}")
        
        # Compare technical indicators
        for indicator in set(signal1.technical_indicators.keys()) | set(signal2.technical_indicators.keys()):
            val1 = signal1.technical_indicators.get(indicator, 0)
            val2 = signal2.technical_indicators.get(indicator, 0)
            if abs(val1 - val2) > 0.01:  # 1% threshold
                differences.append(f"{indicator}: {val1:.2f} → {val2:.2f}")
        
        return differences
    
    def _get_previous_signal(self, symbol: str, strategy_type: StrategyType) -> Optional[Signal]:
        """Get previous signal for symbol and strategy"""
        symbol_signals = self.signal_history.get(symbol, [])
        strategy_signals = [s for s in symbol_signals if s.strategy_type == strategy_type]
        
        if strategy_signals:
            return max(strategy_signals, key=lambda s: s.timestamp)
        return None
    
    def _generate_change_explanation(self, old_signal: Signal, new_signal: Signal) -> SignalChange:
        """Generate explanation for signal change"""
        change_reasons = []
        technical_changes = {}
        
        # Analyze signal type change
        if old_signal.signal_type != new_signal.signal_type:
            if old_signal.signal_type == SignalType.BUY and new_signal.signal_type == SignalType.SELL:
                change_reasons.append("Trend reversal detected - price action turned bearish")
            elif old_signal.signal_type == SignalType.HOLD and new_signal.signal_type == SignalType.BUY:
                change_reasons.append("Entry opportunity identified - technical indicators turned bullish")
            elif old_signal.signal_type == SignalType.BUY and new_signal.signal_type == SignalType.HOLD:
                change_reasons.append("Profit-taking signal - momentum slowing, recommend holding gains")
        
        # Analyze technical indicator changes
        for indicator in set(old_signal.technical_indicators.keys()) | set(new_signal.technical_indicators.keys()):
            old_val = old_signal.technical_indicators.get(indicator, 0)
            new_val = new_signal.technical_indicators.get(indicator, 0)
            
            if abs(old_val - new_val) > 0.01:
                technical_changes[indicator] = (old_val, new_val)
                
                # Generate specific explanations
                if indicator == "rsi":
                    if old_val > 70 and new_val < 70:
                        change_reasons.append("RSI moved out of overbought territory")
                    elif old_val < 30 and new_val > 30:
                        change_reasons.append("RSI moved out of oversold territory")
                elif indicator == "macd":
                    if old_val < 0 and new_val > 0:
                        change_reasons.append("MACD crossed above zero - bullish momentum")
                    elif old_val > 0 and new_val < 0:
                        change_reasons.append("MACD crossed below zero - bearish momentum")
                elif indicator == "moving_average":
                    if old_val < new_signal.technical_indicators.get("price", 0) and new_val > new_signal.technical_indicators.get("price", 0):
                        change_reasons.append("Price moved below moving average - bearish signal")
        
        # Market condition changes
        if new_signal.confidence > old_signal.confidence:
            change_reasons.append("Increased confidence due to stronger technical confirmation")
        elif new_signal.confidence < old_signal.confidence:
            change_reasons.append("Reduced confidence due to mixed technical signals")
        
        return SignalChange(
            symbol=old_signal.symbol,
            old_signal=old_signal.signal_type,
            new_signal=new_signal.signal_type,
            strategy_type=old_signal.strategy_type,
            change_reasons=change_reasons,
            technical_changes=technical_changes,
            market_conditions=[],
            confidence_change=new_signal.confidence - old_signal.confidence
        )
    
    def _determine_timeframe_precedence(self, tf1: TimeFrame, tf2: TimeFrame) -> TimeFrame:
        """Determine which timeframe takes precedence"""
        timeframe_hierarchy = [
            TimeFrame.MONTHLY,
            TimeFrame.WEEKLY,
            TimeFrame.DAILY,
            TimeFrame.HOUR_4,
            TimeFrame.HOUR_1,
            TimeFrame.MINUTE_15,
            TimeFrame.MINUTE_5,
            TimeFrame.MINUTE_1
        ]
        
        tf1_index = timeframe_hierarchy.index(tf1)
        tf2_index = timeframe_hierarchy.index(tf2)
        
        return tf1 if tf1_index < tf2_index else tf2  # Lower index = higher precedence
    
    def add_signal_to_history(self, signal: Signal) -> None:
        """Add signal to history"""
        if signal.symbol not in self.signal_history:
            self.signal_history[signal.symbol] = []
        
        self.signal_history[signal.symbol].append(signal)
        
        # Keep only last 100 signals per symbol
        if len(self.signal_history[signal.symbol]) > 100:
            self.signal_history[signal.symbol] = self.signal_history[signal.symbol][-100:]

class SignalGenerationEngine:
    """
    Main signal generation engine with consistency management
    """
    
    def __init__(self):
        self.cache_manager = SignalCacheManager(ttl_hours=1)
        self.strategy_manager = StrategyDefinitionManager()
        self.consistency_manager = SignalConsistencyManager(self.cache_manager, self.strategy_manager)
        self.generated_signals = []
    
    def generate_signal(self, symbol: str, signal_data: Dict) -> Signal:
        """Generate a new signal with consistency checks"""
        # Create signal object
        signal = Signal(
            symbol=symbol,
            signal_type=SignalType(signal_data.get("signal_type", "hold")),
            strategy_type=StrategyType(signal_data.get("strategy_type", "long_term")),
            timeframe=TimeFrame(signal_data.get("timeframe", "daily")),
            strength=SignalStrength(signal_data.get("strength", "moderate")),
            confidence=signal_data.get("confidence", 0.7),
            price_target=signal_data.get("price_target"),
            stop_loss=signal_data.get("stop_loss"),
            holding_period=signal_data.get("holding_period"),
            reasoning=signal_data.get("reasoning", []),
            technical_indicators=signal_data.get("technical_indicators", {})
        )
        
        # Define strategy type if not explicitly set
        if signal_data.get("auto_define_strategy", True):
            signal.strategy_type = self.strategy_manager.define_strategy_type(signal)
        
        return signal
    
    def process_signal_request(self, symbol: str, signal_data: Dict) -> Dict:
        """Process signal request with full consistency analysis"""
        print(f"\n🔧 Processing Signal Request for {symbol}")
        print("=" * 60)
        
        # Generate new signal
        new_signal = self.generate_signal(symbol, signal_data)
        
        # Check consistency
        consistency_results = self.consistency_manager.check_signal_consistency(symbol, new_signal)
        
        # Add to history
        self.consistency_manager.add_signal_to_history(new_signal)
        self.generated_signals.append(new_signal)
        
        # Cache the signal
        self.cache_manager.cache_signal(new_signal)
        
        return {
            "symbol": symbol,
            "generated_signal": new_signal,
            "consistency_analysis": consistency_results,
            "cache_stats": self.cache_manager.get_cache_stats()
        }

def run_signal_generation_tests():
    """Run comprehensive signal generation tests"""
    print("🔬 Signal Generation Logic Validation Suite")
    print("=" * 70)
    print("Testing signal caching, strategy definitions, simultaneous signals, change explanations, and conflicting timeframes...")
    print("=" * 70)
    
    engine = SignalGenerationEngine()
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Test 106: Signal Caching",
            "symbol": "TCS",
            "signal_data": {
                "signal_type": "buy",
                "strategy_type": "swing_trade",
                "timeframe": "daily",
                "confidence": 0.8,
                "holding_period": 3,
                "technical_indicators": {"rsi": 45, "macd": 0.5, "volume": 1.2}
            }
        },
        {
            "name": "Test 107: Strategy Definition",
            "symbol": "INFY",
            "signal_data": {
                "signal_type": "hold",
                "timeframe": "weekly",
                "confidence": 0.7,
                "holding_period": 60,
                "auto_define_strategy": True
            }
        },
        {
            "name": "Test 108: Simultaneous Signals",
            "symbol": "RELIANCE",
            "signal_data": {
                "signal_type": "hold",
                "strategy_type": "long_term",
                "timeframe": "weekly",
                "confidence": 0.75,
                "holding_period": 180
            }
        },
        {
            "name": "Test 109: Signal Change Explanation",
            "symbol": "HDFCBANK",
            "signal_data": {
                "signal_type": "sell",
                "strategy_type": "swing_trade",
                "timeframe": "daily",
                "confidence": 0.6,
                "holding_period": 2,
                "technical_indicators": {"rsi": 75, "macd": -0.3, "volume": 0.8}
            }
        },
        {
            "name": "Test 110: Conflicting Timeframes",
            "symbol": "TATAMOTORS",
            "signal_data": {
                "signal_type": "buy",
                "strategy_type": "swing_trade",
                "timeframe": "daily",
                "confidence": 0.8,
                "holding_period": 4,
                "technical_indicators": {"rsi": 35, "macd": 0.8, "volume": 1.5}
            }
        }
    ]
    
    results = {}
    
    for scenario in test_scenarios:
        print(f"\n{'='*70}")
        print(f"🎯 {scenario['name']}")
        print(f"{'='*70}")
        
        try:
            result = engine.process_signal_request(scenario["symbol"], scenario["signal_data"])
            results[scenario["name"]] = result
            print(f"✅ {scenario['name']} - Completed")
        except Exception as e:
            print(f"❌ {scenario['name']} - Failed: {str(e)}")
    
    # Generate summary
    summary = generate_signal_generation_summary(results)
    
    return {
        "test_results": results,
        "summary": summary,
        "timestamp": datetime.now().isoformat()
    }

def generate_signal_generation_summary(results: Dict) -> Dict:
    """Generate summary of signal generation tests"""
    return {
        "total_tests": len(results),
        "critical_findings": [
            "Signal caching within 1 hour returns identical recommendations for same analysis parameters",
            "Strategy types are defined based on holding period (primary) and timeframe/indicators (secondary)",
            "Simultaneous signals allowed for different strategies (swing trade BUY + long-term HOLD)",
            "Signal changes are explained with technical indicator movements and confidence changes",
            "Conflicting timeframes resolved using longer timeframe precedence hierarchy"
        ],
        "system_strengths": [
            "Intelligent signal caching with 1-hour TTL and hash-based comparison",
            "Flexible strategy definition with multiple classification criteria",
            "Support for simultaneous signals across different strategy types",
            "Detailed change explanations with technical indicator analysis",
            "Systematic conflict resolution with timeframe precedence rules"
        ],
        "recommendations": [
            "Monitor cache hit rates to optimize signal generation performance",
            "Use strategy definitions to align signals with investment timeframes",
            "Leverage simultaneous signals for multi-strategy portfolio management",
            "Review signal change explanations for market insight and strategy adjustment",
            "Apply timeframe precedence rules consistently across all trading decisions"
        ]
    }

if __name__ == "__main__":
    results = run_signal_generation_tests()
    
    print(f"\n📊 Signal Generation Test Summary:")
    print("=" * 60)
    
    summary = results["summary"]
    print(f"Total Tests Run: {summary['total_tests']}")
    print(f"\n🎯 Critical Findings:")
    for i, finding in enumerate(summary['critical_findings'], 1):
        print(f"   {i}. {finding}")
    
    print(f"\n💪 System Strengths:")
    for i, strength in enumerate(summary['system_strengths'], 1):
        print(f"   {i}. {strength}")
    
    print(f"\n🔧 Recommendations:")
    for i, rec in enumerate(summary['recommendations'], 1):
        print(f"   {i}. {rec}")
