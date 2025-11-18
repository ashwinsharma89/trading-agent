"""
Weekly Close Trading System
Complete implementation for position trading based on weekly close patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class WeeklyCloseTradingSystem:
    """
    Complete weekly close based trading system with real-time analysis
    """
    
    def __init__(self):
        self.trading_config = {
            "strategy_type": "position_trading",
            "target_duration_weeks": 12,
            "weekly_patterns": {
                "strong_bullish": {"min_change": 0.03, "volume_multiplier": 2.0},
                "bullish": {"min_change": 0.015, "volume_multiplier": 1.5},
                "neutral": {"min_change": -0.005, "volume_multiplier": 1.0},
                "bearish": {"min_change": -0.015, "volume_multiplier": 1.5},
                "strong_bearish": {"min_change": -0.03, "volume_multiplier": 2.0}
            },
            "risk_management": {
                "max_position_size": 0.08,  # 8% of portfolio
                "stop_loss_pct": 0.15,      # 15% stop loss
                "target_return": 0.30,      # 30% target return
                "max_portfolio_risk": 0.20   # 20% max portfolio risk
            },
            "entry_rules": {
                "confirmation_days": 1,     # Monday entry
                "volume_confirmation": True,
                "rsi_min": 50,              # Minimum RSI for bullish
                "rsi_max": 70,              # Maximum RSI to avoid overbought
                "above_ma20": True,         # Must be above 20-week MA
                "sector_strength": True      # Sector must be strong
            },
            "exit_rules": {
                "profit_target": 0.30,      # 30% profit target
                "stop_loss": 0.15,          # 15% stop loss
                "time_exit_weeks": 16,      # Exit after 16 weeks max
                "bearish_close_exit": True, # Exit on bearish weekly close
                "trailing_stop": 0.10       # 10% trailing stop after 20% gain
            }
        }
        
        # Initialize tracking
        self.positions = []
        self.trading_journal = []
        self.weekly_analysis = {}
        
    def analyze_weekly_close(self, symbol: str, price_data: Dict) -> Dict:
        """
        Analyze weekly close pattern for a given symbol
        """
        
        try:
            current_price = price_data.get("current_price", 0)
            weekly_change = price_data.get("weekly_change", 0)
            weekly_volume = price_data.get("weekly_volume", 0)
            avg_volume_20w = price_data.get("avg_volume_20w", 1)
            weekly_high = price_data.get("weekly_high", current_price)
            weekly_low = price_data.get("weekly_low", current_price)
            rsi_weekly = price_data.get("rsi_weekly", 50)
            ma20_weekly = price_data.get("ma20_weekly", current_price)
            sector_strength = price_data.get("sector_strength", 0.5)
            
            # Calculate volume ratio
            volume_ratio = weekly_volume / avg_volume_20w if avg_volume_20w > 0 else 1
            
            # Determine weekly close pattern
            weekly_pattern = self._identify_weekly_pattern(weekly_change, volume_ratio)
            
            # Calculate weekly close position in range
            weekly_range = weekly_high - weekly_low
            close_position = (current_price - weekly_low) / weekly_range if weekly_range > 0 else 0.5
            
            # Check entry conditions
            entry_signal = self._check_entry_conditions(
                weekly_pattern, rsi_weekly, current_price, ma20_weekly, 
                sector_strength, volume_ratio, close_position
            )
            
            # Calculate position size
            recommended_size = self._calculate_position_size(entry_signal, weekly_pattern)
            
            # Determine risk level
            risk_level = self._assess_risk_level(weekly_pattern, rsi_weekly, volume_ratio)
            
            analysis_result = {
                "symbol": symbol,
                "current_price": round(current_price, 2),
                "weekly_change_percent": round(weekly_change * 100, 2),
                "weekly_pattern": weekly_pattern,
                "volume_ratio": round(volume_ratio, 2),
                "close_position_range": round(close_position * 100, 1),
                "rsi_weekly": round(rsi_weekly, 1),
                "above_ma20": current_price > ma20_weekly,
                "sector_strength": round(sector_strength * 100, 1),
                "entry_signal": entry_signal,
                "recommended_position_size": recommended_size,
                "risk_level": risk_level,
                "confidence_score": self._calculate_confidence_score(entry_signal, weekly_pattern),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            return analysis_result
            
        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e),
                "analysis_timestamp": datetime.now().isoformat()
            }
    
    def generate_trading_plan(self, weekly_analysis: Dict) -> Dict:
        """
        Generate detailed trading plan based on weekly analysis
        """
        
        if weekly_analysis.get("error"):
            return {"error": "Cannot generate plan due to analysis error"}
        
        entry_signal = weekly_analysis["entry_signal"]
        symbol = weekly_analysis["symbol"]
        
        if entry_signal == "STRONG_BUY":
            plan = self._create_strong_buy_plan(weekly_analysis)
        elif entry_signal == "BUY":
            plan = self._create_buy_plan(weekly_analysis)
        elif entry_signal == "HOLD":
            plan = self._create_hold_plan(weekly_analysis)
        elif entry_signal == "SELL":
            plan = self._create_sell_plan(weekly_analysis)
        else:  # AVOID
            plan = self._create_avoid_plan(weekly_analysis)
        
        return plan
    
    def monitor_position(self, symbol: str, current_data: Dict) -> Dict:
        """
        Monitor existing position and provide exit recommendations
        """
        
        # Find the position
        position = None
        for pos in self.positions:
            if pos["symbol"] == symbol and pos["status"] == "ACTIVE":
                position = pos
                break
        
        if not position:
            return {"error": f"No active position found for {symbol}"}
        
        current_price = current_data.get("current_price", 0)
        entry_price = position["entry_price"]
        current_return = (current_price - entry_price) / entry_price
        
        # Check exit conditions
        exit_signals = []
        
        # Profit target check
        if current_return >= self.trading_config["exit_rules"]["profit_target"]:
            exit_signals.append("PROFIT_TARGET_ACHIEVED")
        
        # Stop loss check
        if current_return <= -self.trading_config["exit_rules"]["stop_loss"]:
            exit_signals.append("STOP_LOSS_TRIGGERED")
        
        # Time exit check
        weeks_held = (datetime.now() - datetime.fromisoformat(position["entry_date"])).days / 7
        if weeks_held >= self.trading_config["exit_rules"]["time_exit_weeks"]:
            exit_signals.append("TIME_EXIT_REACHED")
        
        # Trailing stop check
        if current_return >= 0.20:  # After 20% gain
            trailing_stop = max(current_return - 0.10, -self.trading_config["exit_rules"]["stop_loss"])
            if current_return <= trailing_stop:
                exit_signals.append("TRAILING_STOP_TRIGGERED")
        
        # Weekly pattern check
        weekly_change = current_data.get("weekly_change", 0)
        weekly_volume = current_data.get("weekly_volume", 1)
        avg_volume = current_data.get("avg_volume_20w", 1)
        volume_ratio = weekly_volume / avg_volume if avg_volume > 0 else 1
        
        if weekly_change <= -0.015 and volume_ratio >= 1.5:
            exit_signals.append("BEARISH_WEEKLY_CLOSE")
        
        # Determine action
        if exit_signals:
            action = "EXIT"
            action_reason = ", ".join(exit_signals)
        else:
            action = "HOLD"
            action_reason = "No exit conditions met"
        
        monitoring_result = {
            "symbol": symbol,
            "entry_price": entry_price,
            "current_price": current_price,
            "current_return_percent": round(current_return * 100, 2),
            "weeks_held": round(weeks_held, 1),
            "exit_signals": exit_signals,
            "recommended_action": action,
            "action_reason": action_reason,
            "position_status": position["status"],
            "monitoring_timestamp": datetime.now().isoformat()
        }
        
        return monitoring_result
    
    def get_weekly_monitoring_checklist(self) -> Dict:
        """
        Get comprehensive weekly monitoring checklist
        """
        
        checklist = {
            "friday_evening_analysis": {
                "price_action": [
                    "✓ Weekly close above previous week's high?",
                    "✓ Weekly close below previous week's low?", 
                    "✓ Weekly close in upper 20% of weekly range?",
                    "✓ Weekly close forming higher highs?",
                    "✓ Weekly close breaking key resistance levels?"
                ],
                "volume_analysis": [
                    "✓ Weekly volume > 20-week average?",
                    "✓ Volume increasing on weekly close?",
                    "✓ Volume spike on Friday (weekly close day)?",
                    "✓ Volume confirming price direction?",
                    "✓ Volume distribution throughout the week?"
                ],
                "technical_indicators": [
                    "✓ Weekly RSI(14) between 50-70 for bullish?",
                    "✓ Price above 20-week moving average?",
                    "✓ MACD showing bullish crossover?",
                    "✓ Weekly candle pattern (bullish engulfing, etc.)?",
                    "✓ Bollinger Bands expansion indicating momentum?"
                ],
                "market_context": [
                    "✓ Sector showing relative strength?",
                    "✓ Market indices (Nifty, Sensex) confirming trend?",
                    "✓ FII/DII activity supportive?",
                    "✓ Global market conditions favorable?",
                    "✓ Economic data impact assessed?"
                ]
            },
            "monday_morning_execution": {
                "pre_market": [
                    "✓ Check gap up from Friday close?",
                    "✓ Verify volume in pre-market?",
                    "✓ Confirm no negative news overnight?",
                    "✓ Check global market cues?",
                    "✓ Review weekend developments?"
                ],
                "entry_execution": [
                    "✓ Enter on market open or slight dip?",
                    "✓ Use limit orders for better price?",
                    "✓ Position size according to risk rules?",
                    "✓ Set stop loss immediately?",
                    "✓ Record entry in trading journal?"
                ]
            },
            "weekly_monitoring": [
                "✓ Check weekly close pattern every Friday",
                "✓ Monitor position progress weekly",
                "✓ Review stop loss and trailing stops",
                "✓ Assess market conditions changes",
                "✓ Update trading journal with progress"
            ]
        }
        
        return checklist
    
    def get_position_sizing_calculator(self) -> Dict:
        """
        Get position sizing rules and calculator
        """
        
        sizing_rules = {
            "base_position_size": "5% of portfolio",
            "adjustments": {
                "strong_bullish_weekly_close": "+2% (total 7%)",
                "bullish_weekly_close": "+1% (total 6%)", 
                "neutral_weekly_close": "0% (total 5%)",
                "bearish_weekly_close": "-2% (total 3%)",
                "strong_bearish_weekly_close": "0% (AVOID)"
            },
            "risk_adjustments": {
                "high_volatility": "-1% position size",
                "low_volume": "-1% position size",
                "sector_weakness": "-1% position size",
                "market_uncertainty": "-1% position size"
            },
            "maximum_limits": {
                "per_position": "8% of portfolio maximum",
                "total_exposure": "20% of portfolio maximum",
                "correlated_positions": "12% of portfolio maximum"
            },
            "calculation_example": {
                "portfolio_value": "₹10,00,000",
                "strong_bullish_signal": "7% position = ₹70,000",
                "normal_bullish_signal": "6% position = ₹60,000",
                "neutral_signal": "5% position = ₹50,000"
            }
        }
        
        return sizing_rules
    
    def _identify_weekly_pattern(self, weekly_change: float, volume_ratio: float) -> str:
        """Identify weekly close pattern based on change and volume"""
        
        patterns = self.trading_config["weekly_patterns"]
        
        if weekly_change >= patterns["strong_bullish"]["min_change"] and volume_ratio >= patterns["strong_bullish"]["volume_multiplier"]:
            return "strong_bullish"
        elif weekly_change >= patterns["bullish"]["min_change"] and volume_ratio >= patterns["bullish"]["volume_multiplier"]:
            return "bullish"
        elif weekly_change >= patterns["neutral"]["min_change"]:
            return "neutral"
        elif weekly_change >= patterns["bearish"]["min_change"] and volume_ratio >= patterns["bearish"]["volume_multiplier"]:
            return "bearish"
        else:
            return "strong_bearish"
    
    def _check_entry_conditions(self, pattern: str, rsi: float, price: float, 
                                ma20: float, sector_strength: float, volume_ratio: float, 
                                close_position: float) -> str:
        """Check entry conditions based on multiple factors"""
        
        entry_rules = self.trading_config["entry_rules"]
        
        # Strong bullish conditions
        if (pattern == "strong_bullish" and 
            rsi >= entry_rules["rsi_min"] and 
            rsi <= entry_rules["rsi_max"] and
            price > ma20 and
            sector_strength > 0.6 and
            volume_ratio >= entry_rules.get("volume_multiplier", 1.5)):
            return "STRONG_BUY"
        
        # Normal bullish conditions
        elif (pattern == "bullish" and 
              rsi >= entry_rules["rsi_min"] and 
              rsi <= entry_rules["rsi_max"] and
              price > ma20 and
              sector_strength > 0.5 and
              volume_ratio >= 1.2):
            return "BUY"
        
        # Neutral/hold conditions
        elif pattern == "neutral" and rsi >= 45 and rsi <= 65:
            return "HOLD"
        
        # Bearish conditions
        elif pattern in ["bearish", "strong_bearish"]:
            return "AVOID"
        
        else:
            return "HOLD"
    
    def _calculate_position_size(self, entry_signal: str, pattern: str) -> str:
        """Calculate recommended position size"""
        
        base_size = 0.05  # 5% base
        
        if entry_signal == "STRONG_BUY":
            return "7-8%"
        elif entry_signal == "BUY":
            return "5-6%"
        elif entry_signal == "HOLD":
            return "0-3%"
        else:  # AVOID
            return "0%"
    
    def _assess_risk_level(self, pattern: str, rsi: float, volume_ratio: float) -> str:
        """Assess risk level for the trade"""
        
        if pattern == "strong_bullish" and volume_ratio >= 2.0 and rsi < 70:
            return "Medium"
        elif pattern == "bullish" and volume_ratio >= 1.5:
            return "Medium-High"
        elif pattern == "neutral":
            return "High"
        else:
            return "Very High"
    
    def _calculate_confidence_score(self, entry_signal: str, pattern: str) -> int:
        """Calculate confidence score (0-100)"""
        
        scores = {
            "STRONG_BUY": 85,
            "BUY": 75,
            "HOLD": 50,
            "AVOID": 20
        }
        
        base_score = scores.get(entry_signal, 50)
        
        # Adjust based on pattern strength
        if pattern == "strong_bullish":
            base_score += 10
        elif pattern == "bullish":
            base_score += 5
        elif pattern == "strong_bearish":
            base_score -= 10
        
        return min(100, max(0, base_score))
    
    def _create_strong_buy_plan(self, analysis: Dict) -> Dict:
        """Create trading plan for strong buy signal"""
        
        return {
            "action": "STRONG BUY",
            "symbol": analysis["symbol"],
            "entry_price": analysis["current_price"],
            "position_size": "7-8% of portfolio",
            "stop_loss": f"₹{round(analysis['current_price'] * 0.85, 2)} (15% below)",
            "target_price": f"₹{round(analysis['current_price'] * 1.30, 2)} (30% above)",
            "holding_period": "8-12 weeks",
            "entry_timing": "Monday morning on gap up confirmation",
            "risk_level": analysis["risk_level"],
            "confidence": analysis["confidence_score"],
            "monitoring": "Weekly review, exit on bearish close",
            "plan_timestamp": datetime.now().isoformat()
        }
    
    def _create_buy_plan(self, analysis: Dict) -> Dict:
        """Create trading plan for normal buy signal"""
        
        return {
            "action": "BUY",
            "symbol": analysis["symbol"],
            "entry_price": analysis["current_price"],
            "position_size": "5-6% of portfolio",
            "stop_loss": f"₹{round(analysis['current_price'] * 0.85, 2)} (15% below)",
            "target_price": f"₹{round(analysis['current_price'] * 1.25, 2)} (25% above)",
            "holding_period": "10-16 weeks",
            "entry_timing": "Monday on confirmation",
            "risk_level": analysis["risk_level"],
            "confidence": analysis["confidence_score"],
            "monitoring": "Weekly review, partial exit at 20%",
            "plan_timestamp": datetime.now().isoformat()
        }
    
    def _create_hold_plan(self, analysis: Dict) -> Dict:
        """Create trading plan for hold signal"""
        
        return {
            "action": "HOLD/WAIT",
            "symbol": analysis["symbol"],
            "recommendation": "Wait for better weekly close pattern",
            "current_status": "Neutral weekly close, no clear signal",
            "monitoring": "Watch for strong bullish weekly close",
            "confidence": analysis["confidence_score"],
            "plan_timestamp": datetime.now().isoformat()
        }
    
    def _create_sell_plan(self, analysis: Dict) -> Dict:
        """Create trading plan for sell signal"""
        
        return {
            "action": "SELL/AVOID",
            "symbol": analysis["symbol"],
            "recommendation": "Exit existing positions or avoid new entries",
            "reason": "Bearish weekly close pattern detected",
            "risk_level": "High",
            "confidence": analysis["confidence_score"],
            "plan_timestamp": datetime.now().isoformat()
        }
    
    def _create_avoid_plan(self, analysis: Dict) -> Dict:
        """Create trading plan for avoid signal"""
        
        return {
            "action": "AVOID",
            "symbol": analysis["symbol"],
            "recommendation": "Strong bearish signal - stay away from long positions",
            "reason": "Strong bearish weekly close with high volume",
            "risk_level": "Very High",
            "confidence": analysis["confidence_score"],
            "alternative": "Consider short positions if experienced",
            "plan_timestamp": datetime.now().isoformat()
        }


def demonstrate_weekly_close_system():
    """
    Demonstrate the weekly close trading system
    """
    
    system = WeeklyCloseTradingSystem()
    
    print("🚀 Weekly Close Trading System - Live Demo")
    print("=" * 55)
    
    # Example 1: Analyze a strong bullish weekly close
    print("\n📈 Example 1: Strong Bullish Weekly Close Analysis")
    print("-" * 60)
    
    sample_data_strong_bullish = {
        "current_price": 1850.50,
        "weekly_change": 0.045,  # +4.5%
        "weekly_volume": 2500000,
        "avg_volume_20w": 1000000,
        "weekly_high": 1875.00,
        "weekly_low": 1780.00,
        "rsi_weekly": 62.5,
        "ma20_weekly": 1750.00,
        "sector_strength": 0.75
    }
    
    analysis1 = system.analyze_weekly_close("HDFCBANK", sample_data_strong_bullish)
    
    print(f"Symbol: {analysis1['symbol']}")
    print(f"Current Price: ₹{analysis1['current_price']}")
    print(f"Weekly Change: {analysis1['weekly_change_percent']}%")
    print(f"Weekly Pattern: {analysis1['weekly_pattern'].upper()}")
    print(f"Volume Ratio: {analysis1['volume_ratio']}x")
    print(f"Close Position: {analysis1['close_position_range']}% of weekly range")
    print(f"RSI Weekly: {analysis1['rsi_weekly']}")
    print(f"Above 20-week MA: {analysis1['above_ma20']}")
    print(f"Sector Strength: {analysis1['sector_strength']}%")
    print(f"Entry Signal: {analysis1['entry_signal']}")
    print(f"Position Size: {analysis1['recommended_position_size']}")
    print(f"Risk Level: {analysis1['risk_level']}")
    print(f"Confidence Score: {analysis1['confidence_score']}/100")
    
    # Generate trading plan
    plan1 = system.generate_trading_plan(analysis1)
    print(f"\n📊 Trading Plan:")
    print(f"Action: {plan1['action']}")
    print(f"Position Size: {plan1['position_size']}")
    print(f"Stop Loss: {plan1['stop_loss']}")
    print(f"Target Price: {plan1['target_price']}")
    print(f"Holding Period: {plan1['holding_period']}")
    print(f"Entry Timing: {plan1['entry_timing']}")
    
    # Example 2: Analyze a bearish weekly close
    print("\n📉 Example 2: Strong Bearish Weekly Close Analysis")
    print("-" * 60)
    
    sample_data_bearish = {
        "current_price": 1680.25,
        "weekly_change": -0.042,  # -4.2%
        "weekly_volume": 3200000,
        "avg_volume_20w": 1200000,
        "weekly_high": 1780.00,
        "weekly_low": 1675.00,
        "rsi_weekly": 38.5,
        "ma20_weekly": 1720.00,
        "sector_strength": 0.35
    }
    
    analysis2 = system.analyze_weekly_close("ICICIBANK", sample_data_bearish)
    
    print(f"Symbol: {analysis2['symbol']}")
    print(f"Current Price: ₹{analysis2['current_price']}")
    print(f"Weekly Change: {analysis2['weekly_change_percent']}%")
    print(f"Weekly Pattern: {analysis2['weekly_pattern'].upper()}")
    print(f"Volume Ratio: {analysis2['volume_ratio']}x")
    print(f"Entry Signal: {analysis2['entry_signal']}")
    print(f"Position Size: {analysis2['recommended_position_size']}")
    print(f"Risk Level: {analysis2['risk_level']}")
    
    plan2 = system.generate_trading_plan(analysis2)
    print(f"\n📊 Trading Plan:")
    print(f"Action: {plan2['action']}")
    print(f"Recommendation: {plan2['recommendation']}")
    print(f"Risk Level: {plan2['risk_level']}")
    
    # Example 3: Show monitoring checklist
    print("\n📋 Weekly Monitoring Checklist")
    print("-" * 60)
    
    checklist = system.get_weekly_monitoring_checklist()
    
    print("🔍 Friday Evening Analysis:")
    for category, items in checklist["friday_evening_analysis"].items():
        print(f"\n{category.title()}:")
        for item in items[:3]:  # Show first 3 items
            print(f"  {item}")
        print(f"  ... and {len(items)-3} more")
    
    # Example 4: Show position sizing
    print("\n💰 Position Sizing Calculator")
    print("-" * 60)
    
    sizing = system.get_position_sizing_calculator()
    
    print("Base Position Size: 5% of portfolio")
    print("Adjustments:")
    for pattern, adjustment in sizing["adjustments"].items():
        print(f"  {pattern.replace('_', ' ').title()}: {adjustment}")
    
    print(f"\nCalculation Example (₹10L Portfolio):")
    for scenario, amount in sizing["calculation_example"].items():
        print(f"  {scenario.replace('_', ' ').title()}: {amount}")
    
    print(f"\n✅ System Ready for Implementation!")
    print(f"   📊 Success Rate Target: 70-82%")
    print(f"   💰 Return Target: 25-35% per position")
    print(f"   ⏰ Time Commitment: Weekly monitoring")
    print(f"   🛡️ Risk Management: 15% stop loss, 20% max portfolio risk")


if __name__ == "__main__":
    demonstrate_weekly_close_system()
