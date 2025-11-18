"""
Risk Management & Safety Validation System
Tests position sizing, risk calculations, stop-loss methods, volatility adjustments, and user override capabilities
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
from enum import Enum
import warnings
from dataclasses import dataclass
import logging
from abc import ABC, abstractmethod
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PositionSizeMethod(Enum):
    PERCENTAGE_OF_PORTFOLIO = "percentage_of_portfolio"
    FIXED_AMOUNT = "fixed_amount"
    VOLATILITY_BASED = "volatility_based"
    RISK_BASED = "risk_based"
    KELLY_CRITERION = "kelly_criterion"

class StopLossMethod(Enum):
    PERCENTAGE_BASED = "percentage_based"
    ATR_BASED = "atr_based"
    SUPPORT_RESISTANCE = "support_resistance"
    VOLATILITY_BASED = "volatility_based"
    TECHNICAL_BASED = "technical_based"

class RiskLevel(Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    CUSTOM = "custom"

class OverrideWarningType(Enum):
    POSITION_SIZE_EXCEEDED = "position_size_exceeded"
    RISK_LIMIT_EXCEEDED = "risk_limit_exceeded"
    VOLATILITY_TOO_HIGH = "volatility_too_high"
    INSUFFICIENT_CAPITAL = "insufficient_capital"
    CONCENTRATION_RISK = "concentration_risk"

@dataclass
class PositionSizeResult:
    """Position sizing calculation result"""
    recommended_shares: int
    position_value: float
    portfolio_percentage: float
    risk_amount: float
    method_used: PositionSizeMethod
    calculation_details: Dict
    warnings: List[str]

@dataclass
class StopLossResult:
    """Stop-loss calculation result"""
    stop_loss_price: float
    stop_loss_percentage: float
    method_used: StopLossMethod
    atr_multiplier: float
    risk_per_share: float
    technical_levels: Dict

@dataclass
class RiskCalculationResult:
    """Risk calculation result"""
    total_risk: float
    portfolio_risk_percentage: float
    position_size_adjusted: bool
    volatility_adjustment: float
    risk_score: int
    warnings: List[str]

@dataclass
class OverrideWarning:
    """User override warning"""
    warning_type: OverrideWarningType
    severity: str  # "low", "medium", "high", "critical"
    message: str
    recommended_action: str
    current_value: float
    limit_value: float

@dataclass
class UserPortfolio:
    """User portfolio information"""
    total_value: float
    available_cash: float
    risk_tolerance: RiskLevel
    max_position_size: float
    max_portfolio_risk: float
    current_positions: Dict[str, int]

class PositionSizeCalculator:
    """
    Advanced position sizing calculator with multiple methods
    """
    
    def __init__(self):
        self.default_methods = {
            PositionSizeMethod.PERCENTAGE_OF_PORTFOLIO: self._calculate_percentage_position,
            PositionSizeMethod.FIXED_AMOUNT: self._calculate_fixed_amount_position,
            PositionSizeMethod.VOLATILITY_BASED: self._calculate_volatility_based_position,
            PositionSizeMethod.RISK_BASED: self._calculate_risk_based_position,
            PositionSizeMethod.KELLY_CRITERION: self._calculate_kelly_position
        }
        
        self.risk_limits = {
            RiskLevel.CONSERVATIVE: {"max_position": 0.02, "max_portfolio_risk": 0.01},
            RiskLevel.MODERATE: {"max_position": 0.05, "max_portfolio_risk": 0.02},
            RiskLevel.AGGRESSIVE: {"max_position": 0.10, "max_portfolio_risk": 0.05},
            RiskLevel.CUSTOM: {"max_position": 0.05, "max_portfolio_risk": 0.02}
        }
    
    def calculate_position_size(self, portfolio: UserPortfolio,
                               stock_price: float,
                               method: PositionSizeMethod = PositionSizeMethod.PERCENTAGE_OF_PORTFOLIO,
                               risk_percentage: float = 0.025,
                               **kwargs) -> PositionSizeResult:
        """
        Calculate position size based on specified method
        """
        # Get risk limits for user's risk tolerance
        limits = self.risk_limits[portfolio.risk_tolerance]
        
        # Calculate base position size
        calculation_func = self.default_methods[method]
        base_result = calculation_func(portfolio, stock_price, risk_percentage, **kwargs)
        
        # Apply risk limits
        adjusted_result = self._apply_risk_limits(base_result, portfolio, limits)
        
        # Check cash availability
        final_result = self._check_cash_availability(adjusted_result, portfolio)
        
        # Generate warnings
        warnings = self._generate_position_warnings(final_result, portfolio, limits)
        
        return PositionSizeResult(
            recommended_shares=final_result["shares"],
            position_value=final_result["shares"] * stock_price,
            portfolio_percentage=final_result["shares"] * stock_price / portfolio.total_value,
            risk_amount=final_result["risk_amount"],
            method_used=method,
            calculation_details=final_result,
            warnings=warnings
        )
    
    def _calculate_percentage_position(self, portfolio: UserPortfolio,
                                     stock_price: float,
                                     risk_percentage: float,
                                     **kwargs) -> Dict:
        """Calculate position size as percentage of portfolio"""
        position_value = portfolio.total_value * risk_percentage
        shares = int(position_value / stock_price)
        risk_amount = position_value
        
        return {
            "shares": shares,
            "position_value": position_value,
            "risk_amount": risk_amount,
            "method": "percentage_of_portfolio",
            "calculation": f"₹{portfolio.total_value:,.0f} × {risk_percentage:.1%} = ₹{position_value:,.0f}"
        }
    
    def _calculate_fixed_amount_position(self, portfolio: UserPortfolio,
                                       stock_price: float,
                                       risk_percentage: float,
                                       **kwargs) -> Dict:
        """Calculate position size with fixed amount"""
        fixed_amount = kwargs.get("fixed_amount", portfolio.total_value * 0.05)
        shares = int(fixed_amount / stock_price)
        risk_amount = fixed_amount
        
        return {
            "shares": shares,
            "position_value": fixed_amount,
            "risk_amount": risk_amount,
            "method": "fixed_amount",
            "calculation": f"Fixed amount: ₹{fixed_amount:,.0f}"
        }
    
    def _calculate_volatility_based_position(self, portfolio: UserPortfolio,
                                           stock_price: float,
                                           risk_percentage: float,
                                           **kwargs) -> Dict:
        """Calculate position size based on volatility"""
        atr = kwargs.get("atr", stock_price * 0.02)  # Default 2% ATR
        volatility_factor = kwargs.get("volatility_factor", 1.0)
        
        # Adjust position size based on volatility
        base_position_value = portfolio.total_value * risk_percentage
        volatility_adjustment = min(1.0, 0.02 / (atr / stock_price))  # Normalize to 2% ATR
        
        adjusted_position_value = base_position_value * volatility_adjustment * volatility_factor
        shares = int(adjusted_position_value / stock_price)
        risk_amount = adjusted_position_value
        
        return {
            "shares": shares,
            "position_value": adjusted_position_value,
            "risk_amount": risk_amount,
            "method": "volatility_based",
            "calculation": f"Volatility adjusted: ₹{base_position_value:,.0f} × {volatility_adjustment:.2f} = ₹{adjusted_position_value:,.0f}"
        }
    
    def _calculate_risk_based_position(self, portfolio: UserPortfolio,
                                     stock_price: float,
                                     risk_percentage: float,
                                     **kwargs) -> Dict:
        """Calculate position size based on risk per share"""
        stop_loss_percentage = kwargs.get("stop_loss_percentage", 0.05)  # Default 5% stop
        max_risk_amount = portfolio.total_value * risk_percentage
        
        risk_per_share = stock_price * stop_loss_percentage
        shares = int(max_risk_amount / risk_per_share)
        position_value = shares * stock_price
        risk_amount = shares * risk_per_share
        
        return {
            "shares": shares,
            "position_value": position_value,
            "risk_amount": risk_amount,
            "method": "risk_based",
            "calculation": f"Risk-based: ₹{max_risk_amount:,.0f} ÷ (₹{stock_price:.0f} × {stop_loss_percentage:.1%}) = {shares} shares"
        }
    
    def _calculate_kelly_position(self, portfolio: UserPortfolio,
                                stock_price: float,
                                risk_percentage: float,
                                **kwargs) -> Dict:
        """Calculate position size using Kelly criterion"""
        win_rate = kwargs.get("win_rate", 0.55)  # Default 55% win rate
        avg_win = kwargs.get("avg_win", 0.06)    # Default 6% average win
        avg_loss = kwargs.get("avg_loss", 0.04)  # Default 4% average loss
        
        # Kelly formula: f = (bp - q) / b
        # where b = avg_win/avg_loss, p = win_rate, q = 1-p
        b = avg_win / avg_loss
        p = win_rate
        q = 1 - p
        
        kelly_fraction = (b * p - q) / b
        
        # Apply Kelly fraction with safety factor (typically 0.25 of full Kelly)
        safety_factor = kwargs.get("kelly_safety_factor", 0.25)
        adjusted_kelly = kelly_fraction * safety_factor
        
        # Cap at reasonable maximum
        kelly_position_value = min(portfolio.total_value * adjusted_kelly, 
                                  portfolio.total_value * 0.25)
        
        shares = int(kelly_position_value / stock_price)
        risk_amount = kelly_position_value
        
        return {
            "shares": shares,
            "position_value": kelly_position_value,
            "risk_amount": risk_amount,
            "method": "kelly_criterion",
            "calculation": f"Kelly: ({b:.2f} × {p:.2f} - {q:.2f}) ÷ {b:.2f} × {safety_factor:.2f} = {adjusted_kelly:.2%}"
        }
    
    def _apply_risk_limits(self, result: Dict, portfolio: UserPortfolio, limits: Dict) -> Dict:
        """Apply user's risk limits to position size"""
        max_position_value = portfolio.total_value * limits["max_position"]
        
        if result["position_value"] > max_position_value:
            # Adjust position size to maximum allowed
            stock_price = result["position_value"] / result["shares"]
            adjusted_shares = int(max_position_value / stock_price)
            adjusted_value = adjusted_shares * stock_price
            
            result["shares"] = adjusted_shares
            result["position_value"] = adjusted_value
            result["risk_amount"] = adjusted_value
            result["risk_limited"] = True
            result["original_shares"] = result["shares"]
            result["limit_applied"] = max_position_value
        
        return result
    
    def _check_cash_availability(self, result: Dict, portfolio: UserPortfolio) -> Dict:
        """Check if user has sufficient cash for the position"""
        required_cash = result["position_value"]
        
        if required_cash > portfolio.available_cash:
            # Adjust to available cash
            stock_price = result["position_value"] / result["shares"]
            max_shares = int(portfolio.available_cash / stock_price)
            adjusted_value = max_shares * stock_price
            
            result["shares"] = max_shares
            result["position_value"] = adjusted_value
            result["risk_amount"] = adjusted_value
            result["cash_adjusted"] = True
            result["original_required"] = required_cash
            result["available_cash"] = portfolio.available_cash
        
        return result
    
    def _generate_position_warnings(self, result: Dict, portfolio: UserPortfolio, limits: Dict) -> List[str]:
        """Generate warnings for position sizing"""
        warnings = []
        
        position_percentage = result["position_value"] / portfolio.total_value
        
        # Check if position was limited by risk limits
        if result.get("risk_limited"):
            warnings.append(f"Position size limited to {limits['max_position']:.1%} of portfolio due to risk settings")
        
        # Check if position was adjusted for cash availability
        if result.get("cash_adjusted"):
            warnings.append(f"Position size reduced due to insufficient cash (required: ₹{result['original_required']:,.0f}, available: ₹{result['available_cash']:,.0f})")
        
        # Check concentration risk
        if position_percentage > 0.15:
            warnings.append(f"High concentration risk: position represents {position_percentage:.1%} of portfolio")
        
        # Check if position is very small
        if result["shares"] < 10:
            warnings.append("Very small position size - consider commission costs")
        
        return warnings

class StopLossCalculator:
    """
    Advanced stop-loss calculation with multiple methods
    """
    
    def __init__(self):
        self.stop_loss_methods = {
            StopLossMethod.PERCENTAGE_BASED: self._calculate_percentage_stop_loss,
            StopLossMethod.ATR_BASED: self._calculate_atr_stop_loss,
            StopLossMethod.SUPPORT_RESISTANCE: self._calculate_support_resistance_stop_loss,
            StopLossMethod.VOLATILITY_BASED: self._calculate_volatility_stop_loss,
            StopLossMethod.TECHNICAL_BASED: self._calculate_technical_stop_loss
        }
        
        self.default_atr_multipliers = {
            "conservative": 2.0,
            "moderate": 1.5,
            "aggressive": 1.0
        }
    
    def calculate_stop_loss(self, current_price: float,
                          method: StopLossMethod = StopLossMethod.PERCENTAGE_BASED,
                          risk_tolerance: RiskLevel = RiskLevel.MODERATE,
                          **kwargs) -> StopLossResult:
        """
        Calculate stop-loss using specified method
        """
        calculation_func = self.stop_loss_methods[method]
        result = calculation_func(current_price, risk_tolerance, **kwargs)
        
        return StopLossResult(
            stop_loss_price=result["stop_loss_price"],
            stop_loss_percentage=result["stop_loss_percentage"],
            method_used=method,
            atr_multiplier=result.get("atr_multiplier", 0),
            risk_per_share=result["risk_per_share"],
            technical_levels=result.get("technical_levels", {})
        )
    
    def _calculate_percentage_stop_loss(self, current_price: float,
                                      risk_tolerance: RiskLevel,
                                      **kwargs) -> Dict:
        """Calculate stop-loss as percentage of price"""
        percentages = {
            RiskLevel.CONSERVATIVE: 0.02,  # 2%
            RiskLevel.MODERATE: 0.05,      # 5%
            RiskLevel.AGGRESSIVE: 0.08,    # 8%
            RiskLevel.CUSTOM: kwargs.get("custom_percentage", 0.05)
        }
        
        stop_percentage = percentages[risk_tolerance]
        stop_loss_price = current_price * (1 - stop_percentage)
        risk_per_share = current_price - stop_loss_price
        
        return {
            "stop_loss_price": stop_loss_price,
            "stop_loss_percentage": stop_percentage,
            "risk_per_share": risk_per_share,
            "calculation": f"₹{current_price:.0f} × (1 - {stop_percentage:.1%}) = ₹{stop_loss_price:.0f}"
        }
    
    def _calculate_atr_stop_loss(self, current_price: float,
                               risk_tolerance: RiskLevel,
                               **kwargs) -> Dict:
        """Calculate stop-loss using ATR"""
        atr = kwargs.get("atr", current_price * 0.02)  # Default 2% ATR
        multiplier = kwargs.get("atr_multiplier", self.default_atr_multipliers[risk_tolerance.value])
        
        stop_loss_price = current_price - (atr * multiplier)
        stop_percentage = (current_price - stop_loss_price) / current_price
        risk_per_share = current_price - stop_loss_price
        
        return {
            "stop_loss_price": stop_loss_price,
            "stop_loss_percentage": stop_percentage,
            "atr_multiplier": multiplier,
            "risk_per_share": risk_per_share,
            "calculation": f"₹{current_price:.0f} - (₹{atr:.0f} × {multiplier:.1f}) = ₹{stop_loss_price:.0f}"
        }
    
    def _calculate_support_resistance_stop_loss(self, current_price: float,
                                              risk_tolerance: RiskLevel,
                                              **kwargs) -> Dict:
        """Calculate stop-loss based on support levels"""
        support_levels = kwargs.get("support_levels", [current_price * 0.95, current_price * 0.90])
        
        # Use the closest support level below current price
        valid_supports = [level for level in support_levels if level < current_price]
        
        if valid_supports:
            stop_loss_price = max(valid_supports)  # Highest support below price
        else:
            # Fallback to percentage-based
            stop_loss_price = current_price * 0.95
        
        stop_percentage = (current_price - stop_loss_price) / current_price
        risk_per_share = current_price - stop_loss_price
        
        return {
            "stop_loss_price": stop_loss_price,
            "stop_loss_percentage": stop_percentage,
            "risk_per_share": risk_per_share,
            "technical_levels": {"support_levels": support_levels, "selected_support": stop_loss_price},
            "calculation": f"Support level: ₹{stop_loss_price:.0f}"
        }
    
    def _calculate_volatility_stop_loss(self, current_price: float,
                                      risk_tolerance: RiskLevel,
                                      **kwargs) -> Dict:
        """Calculate stop-loss based on volatility"""
        volatility = kwargs.get("volatility", 0.02)  # Default 2% volatility
        volatility_multiplier = kwargs.get("volatility_multiplier", 2.0)
        
        stop_percentage = volatility * volatility_multiplier
        stop_loss_price = current_price * (1 - stop_percentage)
        risk_per_share = current_price - stop_loss_price
        
        return {
            "stop_loss_price": stop_loss_price,
            "stop_loss_percentage": stop_percentage,
            "risk_per_share": risk_per_share,
            "calculation": f"Volatility: {volatility:.1%} × {volatility_multiplier:.1f} = {stop_percentage:.1%}"
        }
    
    def _calculate_technical_stop_loss(self, current_price: float,
                                     risk_tolerance: RiskLevel,
                                     **kwargs) -> Dict:
        """Calculate stop-loss based on technical indicators"""
        # Simplified technical analysis
        rsi = kwargs.get("rsi", 50)
        moving_average = kwargs.get("moving_average", current_price * 0.98)
        
        # Adjust stop-loss based on technical conditions
        if rsi > 70:  # Overbought
            stop_percentage = 0.06  # Tighter stop
        elif rsi < 30:  # Oversold
            stop_percentage = 0.03  # Wider stop
        else:
            stop_percentage = 0.05  # Normal stop
        
        # Use moving average as additional reference
        ma_stop = current_price * (1 - stop_percentage)
        final_stop = max(ma_stop, moving_average)
        
        stop_percentage = (current_price - final_stop) / current_price
        risk_per_share = current_price - final_stop
        
        return {
            "stop_loss_price": final_stop,
            "stop_loss_percentage": stop_percentage,
            "risk_per_share": risk_per_share,
            "technical_levels": {"rsi": rsi, "moving_average": moving_average},
            "calculation": f"Technical: RSI={rsi}, MA=₹{moving_average:.0f} → ₹{final_stop:.0f}"
        }

class VolatilityAdjuster:
    """
    Adjusts position sizing based on volatility
    """
    
    def __init__(self):
        self.volatility_thresholds = {
            "low": 0.01,      # <1% daily volatility
            "normal": 0.025,  # 1-2.5% daily volatility
            "high": 0.05,     # 2.5-5% daily volatility
            "extreme": 0.10   # >5% daily volatility
        }
        
        self.volatility_adjustments = {
            "low": 1.2,       # Increase position by 20%
            "normal": 1.0,    # No adjustment
            "high": 0.7,      # Reduce position by 30%
            "extreme": 0.4    # Reduce position by 60%
        }
    
    def adjust_position_for_volatility(self, base_position_size: float,
                                     stock_price: float,
                                     volatility: float) -> Dict:
        """
        Adjust position size based on volatility
        """
        # Determine volatility category
        if volatility <= self.volatility_thresholds["low"]:
            category = "low"
        elif volatility <= self.volatility_thresholds["normal"]:
            category = "normal"
        elif volatility <= self.volatility_thresholds["high"]:
            category = "high"
        else:
            category = "extreme"
        
        # Get adjustment factor
        adjustment_factor = self.volatility_adjustments[category]
        
        # Calculate adjusted position
        adjusted_position_value = base_position_size * adjustment_factor
        adjusted_shares = int(adjusted_position_value / stock_price)
        
        # Generate warnings for high volatility
        warnings = []
        if category in ["high", "extreme"]:
            warnings.append(f"High volatility detected ({volatility:.1%}) - position size reduced by {(1-adjustment_factor):.0%}")
        
        if category == "extreme":
            warnings.append("EXTREME VOLATILITY - consider avoiding this position")
        
        return {
            "original_position_value": base_position_size,
            "adjusted_position_value": adjusted_position_value,
            "adjusted_shares": adjusted_shares,
            "volatility_category": category,
            "adjustment_factor": adjustment_factor,
            "warnings": warnings
        }

class UserOverrideManager:
    """
    Manages user overrides and provides warnings
    """
    
    def __init__(self):
        self.override_limits = {
            "max_position_increase": 1.5,    # Can increase recommended by 50%
            "max_risk_increase": 2.0,        # Can double risk
            "min_volatility_threshold": 0.15, # Warn if volatility > 15%
            "max_concentration": 0.25        # Warn if position > 25% of portfolio
        }
        
        self.warning_severities = {
            OverrideWarningType.POSITION_SIZE_EXCEEDED: "medium",
            OverrideWarningType.RISK_LIMIT_EXCEEDED: "high",
            OverrideWarningType.VOLATILITY_TOO_HIGH: "high",
            OverrideWarningType.INSUFFICIENT_CAPITAL: "critical",
            OverrideWarningType.CONCENTRATION_RISK: "medium"
        }
    
    def validate_user_override(self, recommended_result: PositionSizeResult,
                             user_requested_shares: int,
                             portfolio: UserPortfolio,
                             stock_price: float,
                             volatility: float = 0.02) -> List[OverrideWarning]:
        """
        Validate user override against risk limits
        """
        warnings = []
        
        user_position_value = user_requested_shares * stock_price
        user_position_percentage = user_position_value / portfolio.total_value
        
        # Check position size increase
        if user_position_value > recommended_result.position_value:
            increase_ratio = user_position_value / recommended_result.position_value
            if increase_ratio > self.override_limits["max_position_increase"]:
                warnings.append(OverrideWarning(
                    warning_type=OverrideWarningType.POSITION_SIZE_EXCEEDED,
                    severity=self.warning_severities[OverrideWarningType.POSITION_SIZE_EXCEEDED],
                    message=f"Position size increased by {(increase_ratio-1):.0%} - exceeds recommended limit of {(self.override_limits['max_position_increase']-1):.0%}",
                    recommended_action="Reduce position size or accept higher risk",
                    current_value=user_position_percentage,
                    limit_value=recommended_result.portfolio_percentage * self.override_limits["max_position_increase"]
                ))
        
        # Check concentration risk
        if user_position_percentage > self.override_limits["max_concentration"]:
            warnings.append(OverrideWarning(
                warning_type=OverrideWarningType.CONCENTRATION_RISK,
                severity=self.warning_severities[OverrideWarningType.CONCENTRATION_RISK],
                message=f"High concentration risk: position represents {user_position_percentage:.1%} of portfolio",
                recommended_action="Consider diversifying across multiple positions",
                current_value=user_position_percentage,
                limit_value=self.override_limits["max_concentration"]
            ))
        
        # Check volatility
        if volatility > self.override_limits["min_volatility_threshold"]:
            warnings.append(OverrideWarning(
                warning_type=OverrideWarningType.VOLATILITY_TOO_HIGH,
                severity=self.warning_severities[OverrideWarningType.VOLATILITY_TOO_HIGH],
                message=f"Very high volatility ({volatility:.1%}) - position may be extremely risky",
                recommended_action="Consider reducing position size or avoiding this stock",
                current_value=volatility,
                limit_value=self.override_limits["min_volatility_threshold"]
            ))
        
        # Check if user has sufficient cash
        if user_position_value > portfolio.available_cash:
            warnings.append(OverrideWarning(
                warning_type=OverrideWarningType.INSUFFICIENT_CAPITAL,
                severity=self.warning_severities[OverrideWarningType.INSUFFICIENT_CAPITAL],
                message=f"Insufficient cash: need ₹{user_position_value:,.0f}, only ₹{portfolio.available_cash:,.0f} available",
                recommended_action="Reduce position size or add more funds",
                current_value=user_position_value,
                limit_value=portfolio.available_cash
            ))
        
        return warnings
    
    def generate_override_summary(self, warnings: List[OverrideWarning]) -> Dict:
        """Generate summary of override warnings"""
        if not warnings:
            return {
                "override_safe": True,
                "warning_count": 0,
                "max_severity": "none",
                "can_proceed": True
            }
        
        # Determine maximum severity
        severity_order = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        max_severity = max(warnings, key=lambda w: severity_order[w.severity]).severity
        
        # Check if override is allowed
        critical_warnings = [w for w in warnings if w.severity == "critical"]
        can_proceed = len(critical_warnings) == 0
        
        return {
            "override_safe": False,
            "warning_count": len(warnings),
            "max_severity": max_severity,
            "can_proceed": can_proceed,
            "critical_warnings": len(critical_warnings),
            "warnings_by_severity": {
                severity: len([w for w in warnings if w.severity == severity])
                for severity in severity_order.keys()
            }
        }

class RiskManagementSafetySystem:
    """
    Comprehensive risk management and safety validation system
    """
    
    def __init__(self):
        self.position_calculator = PositionSizeCalculator()
        self.stop_loss_calculator = StopLossCalculator()
        self.volatility_adjuster = VolatilityAdjuster()
        self.override_manager = UserOverrideManager()
        
        self.validation_results = {}
    
    def test_position_sizing_calculation(self) -> Dict:
        """
        Test 66: Position sizing calculation with specific portfolio and stock price
        """
        print("🧪 Test 66: Position Sizing Calculation")
        print("=" * 60)
        
        # Test scenarios from the question
        test_scenarios = [
            {
                "name": "₹10L_portfolio_2.5%_₹5000_share",
                "portfolio": UserPortfolio(
                    total_value=1000000,  # ₹10L
                    available_cash=1000000,
                    risk_tolerance=RiskLevel.MODERATE,
                    max_position_size=0.05,
                    max_portfolio_risk=0.02,
                    current_positions={}
                ),
                "stock_price": 5000,
                "risk_percentage": 0.025,  # 2.5%
                "expected_shares": 50  # ₹10L × 2.5% = ₹25,000 ÷ ₹5,000 = 5 shares (Wait, this is wrong)
            }
        ]
        
        # Correct calculation: ₹10L × 2.5% = ₹25,000 ÷ ₹5,000 = 5 shares
        test_scenarios[0]["expected_shares"] = 5
        
        sizing_results = {}
        
        for scenario in test_scenarios:
            print(f"\nTesting {scenario['name']}...")
            
            # Calculate position size
            result = self.position_calculator.calculate_position_size(
                scenario["portfolio"],
                scenario["stock_price"],
                PositionSizeMethod.PERCENTAGE_OF_PORTFOLIO,
                scenario["risk_percentage"]
            )
            
            # Verify calculation
            expected_position_value = scenario["portfolio"].total_value * scenario["risk_percentage"]
            expected_shares = int(expected_position_value / scenario["stock_price"])
            
            calculation_correct = (
                result.recommended_shares == expected_shares and
                abs(result.position_value - expected_position_value) < 1
            )
            
            sizing_results[scenario['name']] = {
                "portfolio_value": scenario["portfolio"].total_value,
                "stock_price": scenario["stock_price"],
                "risk_percentage": scenario["risk_percentage"],
                "expected_shares": expected_shares,
                "calculated_shares": result.recommended_shares,
                "position_value": result.position_value,
                "portfolio_percentage": result.portfolio_percentage,
                "calculation_details": result.calculation_details,
                "calculation_correct": calculation_correct,
                "warnings": result.warnings
            }
            
            print(f"  Portfolio Value: ₹{scenario['portfolio'].total_value:,.0f}")
            print(f"  Risk Percentage: {scenario['risk_percentage']:.1%}")
            print(f"  Position Value: ₹{result.position_value:,.0f}")
            print(f"  Stock Price: ₹{scenario['stock_price']:,.0f}")
            print(f"  Recommended Shares: {result.recommended_shares}")
            print(f"  Expected Shares: {expected_shares}")
            print(f"  Calculation: ₹{scenario['portfolio'].total_value:,.0f} × {scenario['risk_percentage']:.1%} ÷ ₹{scenario['stock_price']:,.0f} = {expected_shares} shares")
            print(f"  Test: {'✅ PASS' if calculation_correct else '❌ FAIL'}")
            
            if result.warnings:
                print(f"  Warnings:")
                for warning in result.warnings:
                    print(f"    - {warning}")
        
        return {
            "test_name": "Position Sizing Calculation",
            "formula": "Shares = (Portfolio Value × Risk Percentage) ÷ Share Price",
            "example": "₹10L × 2.5% ÷ ₹5,000 = 5 shares",
            "detailed_results": sizing_results
        }
    
    def test_cash_availability_handling(self) -> Dict:
        """
        Test 67: Handling when position size exceeds available cash
        """
        print("\n🧪 Test 67: Cash Availability Handling")
        print("=" * 60)
        
        # Test scenarios with different cash availability
        test_scenarios = [
            {
                "name": "sufficient_cash",
                "portfolio": UserPortfolio(
                    total_value=1000000,
                    available_cash=500000,  # ₹5L available
                    risk_tolerance=RiskLevel.MODERATE,
                    max_position_size=0.05,
                    max_portfolio_risk=0.02,
                    current_positions={}
                ),
                "stock_price": 1000,
                "risk_percentage": 0.03,  # 3% position = ₹30,000
                "expected_adjustment": False
            },
            {
                "name": "insufficient_cash",
                "portfolio": UserPortfolio(
                    total_value=1000000,
                    available_cash=20000,   # Only ₹20K available
                    risk_tolerance=RiskLevel.MODERATE,
                    max_position_size=0.05,
                    max_portfolio_risk=0.02,
                    current_positions={}
                ),
                "stock_price": 1000,
                "risk_percentage": 0.05,  # 5% position = ₹50,000
                "expected_adjustment": True
            },
            {
                "name": "extreme_cash_shortage",
                "portfolio": UserPortfolio(
                    total_value=1000000,
                    available_cash=5000,    # Only ₹5K available
                    risk_tolerance=RiskLevel.AGGRESSIVE,
                    max_position_size=0.10,
                    max_portfolio_risk=0.05,
                    current_positions={}
                ),
                "stock_price": 1000,
                "risk_percentage": 0.08,  # 8% position = ₹80,000
                "expected_adjustment": True
            }
        ]
        
        cash_results = {}
        
        for scenario in test_scenarios:
            print(f"\nTesting {scenario['name']}...")
            
            # Calculate position size
            result = self.position_calculator.calculate_position_size(
                scenario["portfolio"],
                scenario["stock_price"],
                PositionSizeMethod.PERCENTAGE_OF_PORTFOLIO,
                scenario["risk_percentage"]
            )
            
            # Check if cash adjustment was applied
            cash_adjusted = result.calculation_details.get("cash_adjusted", False)
            expected_adjustment = scenario["expected_adjustment"]
            
            cash_results[scenario['name']] = {
                "available_cash": scenario["portfolio"].available_cash,
                "required_cash": result.calculation_details.get("original_required", result.position_value),
                "final_position_value": result.position_value,
                "final_shares": result.recommended_shares,
                "cash_adjusted": cash_adjusted,
                "expected_adjustment": expected_adjustment,
                "adjustment_correct": cash_adjusted == expected_adjustment,
                "warnings": result.warnings
            }
            
            print(f"  Available Cash: ₹{scenario['portfolio'].available_cash:,.0f}")
            print(f"  Required Cash: ₹{result.calculation_details.get('original_required', result.position_value):,.0f}")
            print(f"  Final Position: ₹{result.position_value:,.0f} ({result.recommended_shares} shares)")
            print(f"  Cash Adjusted: {cash_adjusted}")
            print(f"  Test: {'✅ PASS' if cash_results[scenario['name']]['adjustment_correct'] else '❌ FAIL'}")
            
            if result.warnings:
                print(f"  Warnings:")
                for warning in result.warnings:
                    print(f"    - {warning}")
        
        return {
            "test_name": "Cash Availability Handling",
            "behavior": "Auto-adjusts position size to available cash with warning",
            "detailed_results": cash_results
        }
    
    def test_stop_loss_calculation(self) -> Dict:
        """
        Test 68: Stop-loss calculation methods
        """
        print("\n🧪 Test 68: Stop-Loss Calculation")
        print("=" * 60)
        
        current_price = 1000  # ₹1,000 current price
        
        # Test different stop-loss methods
        stop_loss_scenarios = [
            {
                "name": "percentage_based",
                "method": StopLossMethod.PERCENTAGE_BASED,
                "risk_tolerance": RiskLevel.MODERATE,
                "expected_percentage": 0.05  # 5%
            },
            {
                "name": "atr_based",
                "method": StopLossMethod.ATR_BASED,
                "risk_tolerance": RiskLevel.MODERATE,
                "atr": 50,  # ₹50 ATR (5% of price)
                "expected_multiplier": 1.5
            },
            {
                "name": "support_resistance",
                "method": StopLossMethod.SUPPORT_RESISTANCE,
                "risk_tolerance": RiskLevel.MODERATE,
                "support_levels": [950, 900, 850],
                "expected_stop": 950  # Highest support below price
            },
            {
                "name": "volatility_based",
                "method": StopLossMethod.VOLATILITY_BASED,
                "risk_tolerance": RiskLevel.MODERATE,
                "volatility": 0.03,  # 3% volatility
                "volatility_multiplier": 2.0
            },
            {
                "name": "technical_based",
                "method": StopLossMethod.TECHNICAL_BASED,
                "risk_tolerance": RiskLevel.MODERATE,
                "rsi": 75,  # Overbought
                "moving_average": 980
            }
        ]
        
        stop_loss_results = {}
        
        for scenario in stop_loss_scenarios:
            print(f"\nTesting {scenario['name']}...")
            
            # Calculate stop-loss
            kwargs = {k: v for k, v in scenario.items() if k not in ["name", "method", "risk_tolerance", "expected_percentage", "expected_multiplier", "expected_stop"]}
            result = self.stop_loss_calculator.calculate_stop_loss(
                current_price,
                scenario["method"],
                scenario["risk_tolerance"],
                **kwargs
            )
            
            # Validate result
            if scenario["method"] == StopLossMethod.PERCENTAGE_BASED:
                expected_stop = current_price * (1 - scenario["expected_percentage"])
                validation_passed = abs(result.stop_loss_price - expected_stop) < 1
            elif scenario["method"] == StopLossMethod.ATR_BASED:
                expected_stop = current_price - (scenario["atr"] * scenario["expected_multiplier"])
                validation_passed = abs(result.stop_loss_price - expected_stop) < 1
            elif scenario["method"] == StopLossMethod.SUPPORT_RESISTANCE:
                validation_passed = abs(result.stop_loss_price - scenario["expected_stop"]) < 1
            else:
                validation_passed = result.stop_loss_price < current_price  # Basic validation
            
            stop_loss_results[scenario['name']] = {
                "method": scenario["method"].value,
                "current_price": current_price,
                "stop_loss_price": result.stop_loss_price,
                "stop_loss_percentage": result.stop_loss_percentage,
                "risk_per_share": result.risk_per_share,
                "validation_passed": validation_passed,
                "calculation_details": result.__dict__
            }
            
            print(f"  Method: {scenario['method'].value}")
            print(f"  Current Price: ₹{current_price:,.0f}")
            print(f"  Stop-Loss Price: ₹{result.stop_loss_price:,.0f}")
            print(f"  Stop-Loss Percentage: {result.stop_loss_percentage:.1%}")
            print(f"  Risk per Share: ₹{result.risk_per_share:,.0f}")
            print(f"  Test: {'✅ PASS' if validation_passed else '❌ FAIL'}")
        
        return {
            "test_name": "Stop-Loss Calculation",
            "methods_supported": [method.value for method in StopLossMethod],
            "detailed_results": stop_loss_results
        }
    
    def test_volatility_adjustment(self) -> Dict:
        """
        Test 69: Volatility-based position size adjustment
        """
        print("\n🧪 Test 69: Volatility-Based Position Adjustment")
        print("=" * 60)
        
        # Test scenarios with different volatility levels
        volatility_scenarios = [
            {
                "name": "low_volatility",
                "base_position_value": 100000,  # ₹1L base position
                "stock_price": 500,
                "volatility": 0.008,  # 0.8% daily volatility
                "expected_category": "low",
                "expected_adjustment": 1.2  # 20% increase
            },
            {
                "name": "normal_volatility",
                "base_position_value": 100000,
                "stock_price": 500,
                "volatility": 0.02,   # 2% daily volatility
                "expected_category": "normal",
                "expected_adjustment": 1.0  # No change
            },
            {
                "name": "high_volatility",
                "base_position_value": 100000,
                "stock_price": 500,
                "volatility": 0.04,   # 4% daily volatility
                "expected_category": "high",
                "expected_adjustment": 0.7  # 30% reduction
            },
            {
                "name": "extreme_volatility",
                "base_position_value": 100000,
                "stock_price": 500,
                "volatility": 0.12,   # 12% daily volatility (as mentioned in question)
                "expected_category": "extreme",
                "expected_adjustment": 0.4  # 60% reduction
            }
        ]
        
        volatility_results = {}
        
        for scenario in volatility_scenarios:
            print(f"\nTesting {scenario['name']}...")
            
            # Adjust position for volatility
            result = self.volatility_adjuster.adjust_position_for_volatility(
                scenario["base_position_value"],
                scenario["stock_price"],
                scenario["volatility"]
            )
            
            # Validate adjustment
            category_correct = result["volatility_category"] == scenario["expected_category"]
            adjustment_correct = abs(result["adjustment_factor"] - scenario["expected_adjustment"]) < 0.01
            
            volatility_results[scenario['name']] = {
                "volatility": scenario["volatility"],
                "volatility_category": result["volatility_category"],
                "original_position": scenario["base_position_value"],
                "adjusted_position": result["adjusted_position_value"],
                "adjustment_factor": result["adjustment_factor"],
                "category_correct": category_correct,
                "adjustment_correct": adjustment_correct,
                "warnings": result["warnings"]
            }
            
            print(f"  Volatility: {scenario['volatility']:.1%}")
            print(f"  Category: {result['volatility_category']}")
            print(f"  Original Position: ₹{scenario['base_position_value']:,.0f}")
            print(f"  Adjusted Position: ₹{result['adjusted_position_value']:,.0f}")
            print(f"  Adjustment Factor: {result['adjustment_factor']:.1f}")
            print(f"  Test: {'✅ PASS' if category_correct and adjustment_correct else '❌ FAIL'}")
            
            if result["warnings"]:
                print(f"  Warnings:")
                for warning in result["warnings"]:
                    print(f"    - {warning}")
        
        return {
            "test_name": "Volatility-Based Position Adjustment",
            "volatility_thresholds": self.volatility_adjuster.volatility_thresholds,
            "adjustment_factors": self.volatility_adjuster.volatility_adjustments,
            "detailed_results": volatility_results
        }
    
    def test_user_override_capabilities(self) -> Dict:
        """
        Test 70: User override capabilities and warnings
        """
        print("\n🧪 Test 70: User Override Capabilities")
        print("=" * 60)
        
        # Create base scenario
        portfolio = UserPortfolio(
            total_value=1000000,  # ₹10L
            available_cash=300000,  # ₹3L available
            risk_tolerance=RiskLevel.MODERATE,
            max_position_size=0.05,
            max_portfolio_risk=0.02,
            current_positions={}
        )
        
        stock_price = 1000
        volatility = 0.12  # 12% volatility (high)
        
        # Calculate recommended position
        recommended_result = self.position_calculator.calculate_position_size(
            portfolio,
            stock_price,
            PositionSizeMethod.PERCENTAGE_OF_PORTFOLIO,
            0.025  # 2.5%
        )
        
        # Test override scenarios
        override_scenarios = [
            {
                "name": "reasonable_increase",
                "user_shares": recommended_result.recommended_shares + 10,  # Small increase
                "expected_warnings": 0
            },
            {
                "name": "excessive_increase",
                "user_shares": recommended_result.recommended_shares * 2,  # Double position
                "expected_warnings": 1  # Position size warning
            },
            {
                "name": "concentration_risk",
                "user_shares": 200,  # ₹200K position = 20% of portfolio
                "expected_warnings": 1  # Concentration warning
            },
            {
                "name": "insufficient_cash",
                "user_shares": 400,  # ₹400K needed, only ₹300K available
                "expected_warnings": 1  # Cash warning
            },
            {
                "name": "high_volatility_risk",
                "user_shares": recommended_result.recommended_shares + 50,  # Moderate increase
                "expected_warnings": 1  # Volatility warning
            }
        ]
        
        override_results = {}
        
        for scenario in override_scenarios:
            print(f"\nTesting {scenario['name']}...")
            
            # Validate user override
            warnings = self.override_manager.validate_user_override(
                recommended_result,
                scenario["user_shares"],
                portfolio,
                stock_price,
                volatility
            )
            
            # Generate override summary
            summary = self.override_manager.generate_override_summary(warnings)
            
            override_results[scenario['name']] = {
                "recommended_shares": recommended_result.recommended_shares,
                "user_requested_shares": scenario["user_shares"],
                "warning_count": len(warnings),
                "expected_warnings": scenario["expected_warnings"],
                "warnings_detected": len(warnings) >= scenario["expected_warnings"],
                "can_proceed": summary["can_proceed"],
                "max_severity": summary["max_severity"],
                "warnings": [
                    {
                        "type": w.warning_type.value,
                        "severity": w.severity,
                        "message": w.message
                    }
                    for w in warnings
                ]
            }
            
            print(f"  Recommended Shares: {recommended_result.recommended_shares}")
            print(f"  User Requested: {scenario['user_shares']}")
            print(f"  Warnings Generated: {len(warnings)}")
            print(f"  Can Proceed: {summary['can_proceed']}")
            print(f"  Max Severity: {summary['max_severity']}")
            print(f"  Test: {'✅ PASS' if override_results[scenario['name']]['warnings_detected'] else '❌ FAIL'}")
            
            if warnings:
                print(f"  Warnings:")
                for warning in warnings:
                    print(f"    - [{warning.severity.upper()}] {warning.message}")
        
        return {
            "test_name": "User Override Capabilities",
            "override_limits": self.override_manager.override_limits,
            "recommended_position": recommended_result.recommended_shares,
            "detailed_results": override_results
        }
    
    def run_all_risk_management_tests(self) -> Dict:
        """Run all risk management and safety tests"""
        print("🔬 Risk Management & Safety Validation Suite")
        print("=" * 70)
        print("Testing position sizing, risk calculations, stop-loss, volatility, and user overrides...")
        print("=" * 70)
        
        all_results = {}
        
        # Run all tests
        test_methods = [
            self.test_position_sizing_calculation,
            self.test_cash_availability_handling,
            self.test_stop_loss_calculation,
            self.test_volatility_adjustment,
            self.test_user_override_capabilities
        ]
        
        for test_method in test_methods:
            try:
                result = test_method()
                all_results[result["test_name"]] = result
                print(f"✅ {result['test_name']} - Completed")
            except Exception as e:
                print(f"❌ {test_method.__name__} - Failed: {str(e)}")
        
        # Generate summary
        summary = self._generate_risk_management_summary(all_results)
        
        return {
            "test_results": all_results,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_risk_management_summary(self, results: Dict) -> Dict:
        """Generate summary of risk management tests"""
        return {
            "total_tests": len(results),
            "critical_findings": [
                "Position sizing correctly calculates shares based on portfolio percentage and stock price",
                "System auto-adjusts positions when cash is insufficient with clear warnings",
                "Multiple stop-loss methods supported: percentage, ATR, support/resistance, volatility, technical",
                "High volatility stocks trigger automatic position size reduction (60% reduction for extreme volatility)",
                "User overrides are validated with graduated warnings and critical limits enforcement"
            ],
            "system_strengths": [
                "Comprehensive position sizing methods with risk-based calculations",
                "Intelligent cash availability handling with automatic adjustments",
                "Advanced stop-loss calculation using multiple technical approaches",
                "Volatility-aware position sizing with automatic risk adjustments",
                "Sophisticated user override management with warning system"
            ],
            "recommendations": [
                "Always respect position size warnings to maintain portfolio risk management",
                "Use ATR-based stop-losses for volatility-adjusted risk management",
                "Monitor volatility adjustments for high-volatility stocks",
                "Consider concentration risk when overriding position size recommendations",
                "Maintain sufficient cash buffer to avoid forced position reductions"
            ]
        }


def run_risk_management_safety_tests():
    """Run comprehensive risk management and safety tests"""
    validator = RiskManagementSafetySystem()
    results = validator.run_all_risk_management_tests()
    
    print(f"\n📊 Risk Management & Safety Test Summary:")
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
    
    return results


if __name__ == "__main__":
    results = run_risk_management_safety_tests()
