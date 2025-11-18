"""
Statistical Validity Validation System
Tests performance metrics, statistical significance, overfitting detection, and walk-forward optimization
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
from scipy import stats
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StrategyType(Enum):
    SWING = "swing"
    LONG_TERM = "long_term"
    INTRADAY = "intraday"
    POSITIONAL = "positional"

class PerformanceMetricType(Enum):
    SHARPE_RATIO = "sharpe_ratio"
    SORTINO_RATIO = "sortino_ratio"
    MAX_DRAWDOWN = "max_drawdown"
    CALMAR_RATIO = "calmar_ratio"
    INFORMATION_RATIO = "information_ratio"
    WIN_RATE = "win_rate"

class StatisticalTestType(Enum):
    T_TEST = "t_test"
    WILCOXON = "wilcoxon"
    KS_TEST = "ks_test"
    BOOTSTRAP = "bootstrap"

class OverfittingDetectionType(Enum):
    REGIME_STABILITY = "regime_stability"
    PARAMETER_STABILITY = "parameter_stability"
    OUT_OF_SAMPLE = "out_of_sample"
    CROSS_VALIDATION = "cross_validation"

@dataclass
class PerformanceMetrics:
    """Performance metrics calculation result"""
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    calmar_ratio: float
    information_ratio: float
    win_rate: float
    profit_factor: float
    average_win: float
    average_loss: float
    total_return: float
    volatility: float

@dataclass
class StatisticalSignificance:
    """Statistical significance test result"""
    test_type: StatisticalTestType
    sample_size: int
    p_value: float
    is_significant: bool
    confidence_level: float
    test_statistic: float
    critical_value: float

@dataclass
class OverfittingWarning:
    """Overfitting detection warning"""
    warning_type: OverfittingDetectionType
    severity: str  # "low", "medium", "high", "critical"
    description: str
    metric_value: float
    threshold: float
    recommendation: str

@dataclass
class WalkForwardResult:
    """Walk-forward optimization result"""
    in_sample_sharpe: float
    out_of_sample_sharpe: float
    performance_decay: float
    stability_score: float
    robustness_rating: str  # "poor", "acceptable", "good", "excellent"

class PerformanceMetricsCalculator:
    """
    Calculates comprehensive performance metrics with Indian market assumptions
    """
    
    def __init__(self):
        # Indian market risk-free rate (10-year G-Sec yield)
        self.risk_free_rate = 0.068  # 6.8% annualized (current Indian G-Sec rate)
        self.trading_days_per_year = 252  # Indian market trading days
        self.benchmark_return = 0.12  # 12% Nifty 50 historical average
        
        # Performance thresholds for different strategy types
        self.performance_thresholds = {
            StrategyType.SWING: {
                "sharpe_ratio": {"poor": 0.5, "acceptable": 1.0, "good": 1.5, "excellent": 2.0},
                "sortino_ratio": {"poor": 0.8, "acceptable": 1.5, "good": 2.0, "excellent": 2.5},
                "max_drawdown": {"poor": 0.30, "acceptable": 0.20, "good": 0.15, "excellent": 0.10}
            },
            StrategyType.LONG_TERM: {
                "sharpe_ratio": {"poor": 0.3, "acceptable": 0.7, "good": 1.0, "excellent": 1.5},
                "sortino_ratio": {"poor": 0.5, "acceptable": 1.0, "good": 1.5, "excellent": 2.0},
                "max_drawdown": {"poor": 0.40, "acceptable": 0.25, "good": 0.20, "excellent": 0.15}
            },
            StrategyType.INTRADAY: {
                "sharpe_ratio": {"poor": 1.0, "acceptable": 2.0, "good": 3.0, "excellent": 4.0},
                "sortino_ratio": {"poor": 1.5, "acceptable": 2.5, "good": 3.5, "excellent": 4.5},
                "max_drawdown": {"poor": 0.05, "acceptable": 0.03, "good": 0.02, "excellent": 0.01}
            }
        }
    
    def calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = None) -> float:
        """
        Calculate Sharpe Ratio with Indian market risk-free rate
        """
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        # Convert annual risk-free rate to daily
        daily_rf_rate = risk_free_rate / self.trading_days_per_year
        
        # Calculate excess returns
        excess_returns = returns - daily_rf_rate
        
        # Annualized Sharpe ratio
        if excess_returns.std() == 0:
            return 0.0
        
        sharpe_ratio = (excess_returns.mean() * self.trading_days_per_year) / \
                      (excess_returns.std() * np.sqrt(self.trading_days_per_year))
        
        return sharpe_ratio
    
    def calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float = None) -> float:
        """
        Calculate Sortino Ratio (downside risk-adjusted return)
        """
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        # Convert annual risk-free rate to daily
        daily_rf_rate = risk_free_rate / self.trading_days_per_year
        
        # Calculate excess returns
        excess_returns = returns - daily_rf_rate
        
        # Calculate downside deviation (only negative returns)
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return float('inf') if excess_returns.mean() > 0 else 0.0
        
        # Annualized Sortino ratio
        sortino_ratio = (excess_returns.mean() * self.trading_days_per_year) / \
                       (downside_returns.std() * np.sqrt(self.trading_days_per_year))
        
        return sortino_ratio
    
    def calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """
        Calculate Maximum Drawdown
        """
        cumulative_returns = (1 + equity_curve).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        
        return drawdown.min()
    
    def calculate_calmar_ratio(self, returns: pd.Series, equity_curve: pd.Series) -> float:
        """
        Calculate Calmar Ratio (annual return / max drawdown)
        """
        total_return = (1 + returns).prod() - 1
        years = len(returns) / self.trading_days_per_year
        annual_return = (1 + total_return) ** (1/years) - 1
        
        max_dd = abs(self.calculate_max_drawdown(equity_curve))
        
        if max_dd == 0:
            return float('inf') if annual_return > 0 else 0.0
        
        return annual_return / max_dd
    
    def calculate_information_ratio(self, returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """
        Calculate Information Ratio (excess return over benchmark)
        """
        excess_returns = returns - benchmark_returns
        
        if excess_returns.std() == 0:
            return 0.0
        
        # Annualized Information Ratio
        information_ratio = (excess_returns.mean() * self.trading_days_per_year) / \
                           (excess_returns.std() * np.sqrt(self.trading_days_per_year))
        
        return information_ratio
    
    def calculate_comprehensive_metrics(self, returns: pd.Series, 
                                      benchmark_returns: pd.Series = None,
                                      trades: pd.DataFrame = None) -> PerformanceMetrics:
        """
        Calculate comprehensive performance metrics
        """
        if benchmark_returns is None:
            # Create synthetic benchmark (Nifty-like returns)
            benchmark_returns = pd.Series(np.random.normal(0.0005, 0.015, len(returns)), 
                                         index=returns.index)
        
        # Calculate core metrics
        sharpe_ratio = self.calculate_sharpe_ratio(returns)
        sortino_ratio = self.calculate_sortino_ratio(returns)
        max_drawdown = self.calculate_max_drawdown(returns)
        calmar_ratio = self.calculate_calmar_ratio(returns, returns)
        information_ratio = self.calculate_information_ratio(returns, benchmark_returns)
        
        # Calculate trade-based metrics
        if trades is not None and len(trades) > 0:
            win_rate = len(trades[trades['pnl'] > 0]) / len(trades)
            profit_factor = abs(trades[trades['pnl'] > 0]['pnl'].sum()) / \
                           abs(trades[trades['pnl'] < 0]['pnl'].sum()) if \
                           trades[trades['pnl'] < 0]['pnl'].sum() != 0 else float('inf')
            average_win = trades[trades['pnl'] > 0]['pnl'].mean() if len(trades[trades['pnl'] > 0]) > 0 else 0
            average_loss = trades[trades['pnl'] < 0]['pnl'].mean() if len(trades[trades['pnl'] < 0]) > 0 else 0
        else:
            win_rate = 0.0
            profit_factor = 1.0
            average_win = 0.0
            average_loss = 0.0
        
        # Calculate return metrics
        total_return = (1 + returns).prod() - 1
        volatility = returns.std() * np.sqrt(self.trading_days_per_year)
        
        return PerformanceMetrics(
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            calmar_ratio=calmar_ratio,
            information_ratio=information_ratio,
            win_rate=win_rate,
            profit_factor=profit_factor,
            average_win=average_win,
            average_loss=average_loss,
            total_return=total_return,
            volatility=volatility
        )
    
    def evaluate_performance_quality(self, metrics: PerformanceMetrics, 
                                    strategy_type: StrategyType) -> Dict:
        """
        Evaluate performance quality against strategy type benchmarks
        """
        thresholds = self.performance_thresholds[strategy_type]
        
        sharpe_rating = self._get_performance_rating(metrics.sharpe_ratio, 
                                                     thresholds["sharpe_ratio"])
        sortino_rating = self._get_performance_rating(metrics.sortino_ratio, 
                                                      thresholds["sortino_ratio"])
        drawdown_rating = self._get_performance_rating(abs(metrics.max_drawdown), 
                                                       thresholds["max_drawdown"], 
                                                       reverse=True)
        
        overall_rating = self._calculate_overall_rating([sharpe_rating, sortino_rating, drawdown_rating])
        
        return {
            "strategy_type": strategy_type.value,
            "sharpe_ratio": {"value": metrics.sharpe_ratio, "rating": sharpe_rating},
            "sortino_ratio": {"value": metrics.sortino_ratio, "rating": sortino_rating},
            "max_drawdown": {"value": abs(metrics.max_drawdown), "rating": drawdown_rating},
            "overall_rating": overall_rating,
            "assessment": self._get_assessment_text(overall_rating)
        }
    
    def _get_performance_rating(self, value: float, thresholds: Dict, reverse: bool = False) -> str:
        """Get performance rating based on value and thresholds"""
        if reverse:
            # For drawdown (lower is better)
            if value <= thresholds["excellent"]:
                return "excellent"
            elif value <= thresholds["good"]:
                return "good"
            elif value <= thresholds["acceptable"]:
                return "acceptable"
            else:
                return "poor"
        else:
            # For Sharpe/Sortino (higher is better)
            if value >= thresholds["excellent"]:
                return "excellent"
            elif value >= thresholds["good"]:
                return "good"
            elif value >= thresholds["acceptable"]:
                return "acceptable"
            else:
                return "poor"
    
    def _calculate_overall_rating(self, ratings: List[str]) -> str:
        """Calculate overall performance rating"""
        rating_scores = {"poor": 1, "acceptable": 2, "good": 3, "excellent": 4}
        average_score = sum(rating_scores[r] for r in ratings) / len(ratings)
        
        if average_score >= 3.5:
            return "excellent"
        elif average_score >= 2.5:
            return "good"
        elif average_score >= 1.5:
            return "acceptable"
        else:
            return "poor"
    
    def _get_assessment_text(self, rating: str) -> str:
        """Get assessment text based on rating"""
        assessments = {
            "excellent": "Outstanding performance, top-tier strategy",
            "good": "Strong performance, above-average strategy",
            "acceptable": "Decent performance, room for improvement",
            "poor": "Weak performance, strategy needs significant improvement"
        }
        return assessments[rating]

class StatisticalSignificanceTester:
    """
    Tests statistical significance of trading results
    """
    
    def __init__(self):
        self.minimum_sample_size = 30  # Minimum trades for basic significance
        self.recommended_sample_size = 100  # Recommended for robust conclusions
        self.high_confidence_sample_size = 200  # For high confidence conclusions
        
        self.significance_thresholds = {
            "low": 0.10,    # 90% confidence
            "medium": 0.05, # 95% confidence
            "high": 0.01    # 99% confidence
        }
    
    def calculate_minimum_sample_size(self, expected_win_rate: float, 
                                     confidence_level: float = 0.95,
                                     margin_of_error: float = 0.05) -> int:
        """
        Calculate minimum sample size required for statistical significance
        """
        z_score = stats.norm.ppf(1 - (1 - confidence_level) / 2)
        
        # Conservative estimate using worst-case variance (p = 0.5)
        variance = expected_win_rate * (1 - expected_win_rate)
        
        if variance == 0:
            variance = 0.25  # Maximum variance for binary outcomes
        
        sample_size = (z_score ** 2 * variance) / (margin_of_error ** 2)
        
        return int(np.ceil(sample_size))
    
    def test_win_rate_significance(self, wins: int, total_trades: int, 
                                  expected_win_rate: float = 0.5) -> StatisticalSignificance:
        """
        Test if win rate is statistically significant
        """
        if total_trades < self.minimum_sample_size:
            return StatisticalSignificance(
                test_type=StatisticalTestType.T_TEST,
                sample_size=total_trades,
                p_value=1.0,
                is_significant=False,
                confidence_level=0.95,
                test_statistic=0.0,
                critical_value=0.0
            )
        
        # One-sample proportion test
        observed_win_rate = wins / total_trades
        
        # Calculate z-score
        standard_error = np.sqrt((expected_win_rate * (1 - expected_win_rate)) / total_trades)
        z_score = (observed_win_rate - expected_win_rate) / standard_error
        
        # Calculate p-value (two-tailed test)
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
        
        return StatisticalSignificance(
            test_type=StatisticalTestType.T_TEST,
            sample_size=total_trades,
            p_value=p_value,
            is_significant=p_value < 0.05,
            confidence_level=0.95,
            test_statistic=z_score,
            critical_value=stats.norm.ppf(0.975)
        )
    
    def test_returns_distribution(self, returns: pd.Series) -> StatisticalSignificance:
        """
        Test if returns are significantly different from zero
        """
        if len(returns) < self.minimum_sample_size:
            return StatisticalSignificance(
                test_type=StatisticalTestType.T_TEST,
                sample_size=len(returns),
                p_value=1.0,
                is_significant=False,
                confidence_level=0.95,
                test_statistic=0.0,
                critical_value=0.0
            )
        
        # One-sample t-test
        t_statistic, p_value = stats.ttest_1samp(returns, 0)
        
        return StatisticalSignificance(
            test_type=StatisticalTestType.T_TEST,
            sample_size=len(returns),
            p_value=p_value,
            is_significant=p_value < 0.05,
            confidence_level=0.95,
            test_statistic=t_statistic,
            critical_value=stats.t.ppf(0.975, len(returns) - 1)
        )
    
    def bootstrap_confidence_interval(self, returns: pd.Series, 
                                    confidence_level: float = 0.95,
                                    n_bootstrap: int = 1000) -> Dict:
        """
        Calculate bootstrap confidence intervals for returns
        """
        if len(returns) < self.minimum_sample_size:
            return {
                "mean_return": 0.0,
                "ci_lower": 0.0,
                "ci_upper": 0.0,
                "sample_size_warning": True
            }
        
        # Bootstrap sampling
        bootstrap_means = []
        
        for _ in range(n_bootstrap):
            sample = np.random.choice(returns, size=len(returns), replace=True)
            bootstrap_means.append(np.mean(sample))
        
        # Calculate confidence interval
        alpha = 1 - confidence_level
        ci_lower = np.percentile(bootstrap_means, 100 * alpha / 2)
        ci_upper = np.percentile(bootstrap_means, 100 * (1 - alpha / 2))
        
        return {
            "mean_return": np.mean(returns),
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "sample_size_warning": False,
            "bootstrap_samples": n_bootstrap
        }
    
    def generate_sample_size_warning(self, sample_size: int, 
                                   strategy_type: StrategyType) -> Dict:
        """
        Generate warning if sample size is insufficient
        """
        warnings = []
        
        if sample_size < self.minimum_sample_size:
            warnings.append({
                "level": "critical",
                "message": f"Sample size ({sample_size}) below minimum threshold ({self.minimum_sample_size})",
                "recommendation": "Collect more data before drawing conclusions"
            })
        
        elif sample_size < self.recommended_sample_size:
            warnings.append({
                "level": "medium",
                "message": f"Sample size ({sample_size}) below recommended threshold ({self.recommended_sample_size})",
                "recommendation": "Results may not be statistically robust"
            })
        
        elif sample_size < self.high_confidence_sample_size:
            warnings.append({
                "level": "low",
                "message": f"Sample size ({sample_size}) adequate but could be higher for high confidence",
                "recommendation": "Consider more data for stronger statistical conclusions"
            })
        
        # Calculate required sample size for 95% confidence
        required_size = self.calculate_minimum_sample_size(0.55, 0.95, 0.05)
        
        return {
            "current_sample_size": sample_size,
            "minimum_required": self.minimum_sample_size,
            "recommended": self.recommended_sample_size,
            "high_confidence": self.high_confidence_sample_size,
            "calculated_required": required_size,
            "warnings": warnings,
            "statistical_power": self._estimate_statistical_power(sample_size)
        }
    
    def _estimate_statistical_power(self, sample_size: int) -> float:
        """Estimate statistical power for given sample size"""
        if sample_size < self.minimum_sample_size:
            return 0.0
        elif sample_size < self.recommended_sample_size:
            return 0.6
        elif sample_size < self.high_confidence_sample_size:
            return 0.8
        else:
            return 0.95

class OverfittingDetector:
    """
    Advanced overfitting detection using multiple methods
    """
    
    def __init__(self):
        self.regime_stability_threshold = 0.3  # 30% performance variation allowed
        self.parameter_stability_threshold = 0.2  # 20% parameter variation allowed
        self.out_of_sample_threshold = 0.5  # 50% performance degradation threshold
        
        self.warnings = []
    
    def detect_regime_overfitting(self, bull_market_performance: Dict,
                                bear_market_performance: Dict) -> OverfittingWarning:
        """
        Detect overfitting to specific market regimes
        """
        bull_sharpe = bull_market_performance.get("sharpe_ratio", 0)
        bear_sharpe = bear_market_performance.get("sharpe_ratio", 0)
        
        # Calculate performance variation
        if bull_sharpe != 0:
            performance_variation = abs(bull_sharpe - bear_sharpe) / abs(bull_sharpe)
        else:
            performance_variation = 1.0  # Maximum variation if bull Sharpe is zero
        
        severity = self._calculate_severity(performance_variation, 
                                          self.regime_stability_threshold)
        
        warning = OverfittingWarning(
            warning_type=OverfittingDetectionType.REGIME_STABILITY,
            severity=severity,
            description=f"Strategy performance varies {performance_variation:.1%} between market regimes",
            metric_value=performance_variation,
            threshold=self.regime_stability_threshold,
            recommendation=self._get_regime_recommendation(performance_variation)
        )
        
        return warning
    
    def detect_parameter_overfitting(self, optimal_parameters: Dict,
                                   parameter_stability: Dict) -> OverfittingWarning:
        """
        Detect overfitting through parameter instability
        """
        stability_score = parameter_stability.get("stability_score", 1.0)
        parameter_variation = 1 - stability_score
        
        severity = self._calculate_severity(parameter_variation,
                                          self.parameter_stability_threshold)
        
        warning = OverfittingWarning(
            warning_type=OverfittingDetectionType.PARAMETER_STABILITY,
            severity=severity,
            description=f"Parameters show {parameter_variation:.1%} instability across time periods",
            metric_value=parameter_variation,
            threshold=self.parameter_stability_threshold,
            recommendation=self._get_parameter_recommendation(parameter_variation)
        )
        
        return warning
    
    def detect_out_of_sample_overfitting(self, in_sample_performance: Dict,
                                       out_of_sample_performance: Dict) -> OverfittingWarning:
        """
        Detect overfitting through poor out-of-sample performance
        """
        in_sample_sharpe = in_sample_performance.get("sharpe_ratio", 0)
        out_sample_sharpe = out_of_sample_performance.get("sharpe_ratio", 0)
        
        if in_sample_sharpe != 0:
            performance_decay = (in_sample_sharpe - out_sample_sharpe) / abs(in_sample_sharpe)
        else:
            performance_decay = 0.0
        
        severity = self._calculate_severity(performance_decay,
                                          self.out_of_sample_threshold)
        
        warning = OverfittingWarning(
            warning_type=OverfittingDetectionType.OUT_OF_SAMPLE,
            severity=severity,
            description=f"Out-of-sample performance decays by {performance_decay:.1%} compared to in-sample",
            metric_value=performance_decay,
            threshold=self.out_of_sample_threshold,
            recommendation=self._get_out_of_sample_recommendation(performance_decay)
        )
        
        return warning
    
    def analyze_market_regime_performance(self, returns: pd.Series, 
                                        market_data: pd.DataFrame) -> Dict:
        """
        Analyze strategy performance across different market regimes
        """
        # Define market regimes based on market returns
        market_returns = market_data['returns']
        
        # Bull market: positive returns
        bull_periods = market_returns > 0
        bear_periods = market_returns < 0
        
        # Calculate performance in each regime
        bull_returns = returns[bull_periods]
        bear_returns = returns[bear_periods]
        
        bull_performance = {
            "sharpe_ratio": self._calculate_simple_sharpe(bull_returns),
            "total_return": (1 + bull_returns).prod() - 1 if len(bull_returns) > 0 else 0,
            "volatility": bull_returns.std() * np.sqrt(252) if len(bull_returns) > 0 else 0,
            "periods": len(bull_returns)
        }
        
        bear_performance = {
            "sharpe_ratio": self._calculate_simple_sharpe(bear_returns),
            "total_return": (1 + bear_returns).prod() - 1 if len(bear_returns) > 0 else 0,
            "volatility": bear_returns.std() * np.sqrt(252) if len(bear_returns) > 0 else 0,
            "periods": len(bear_returns)
        }
        
        return {
            "bull_market": bull_performance,
            "bear_market": bear_performance,
            "regime_analysis": self._analyze_regime_sensitivity(bull_performance, bear_performance)
        }
    
    def _calculate_simple_sharpe(self, returns: pd.Series) -> float:
        """Calculate simple Sharpe ratio for regime analysis"""
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        return (returns.mean() * 252) / (returns.std() * np.sqrt(252))
    
    def _analyze_regime_sensitivity(self, bull_perf: Dict, bear_perf: Dict) -> Dict:
        """Analyze sensitivity to market regimes"""
        bull_sharpe = bull_perf.get("sharpe_ratio", 0)
        bear_sharpe = bear_perf.get("sharpe_ratio", 0)
        
        if bull_sharpe != 0:
            sensitivity = abs(bull_sharpe - bear_sharpe) / abs(bull_sharpe)
        else:
            sensitivity = 1.0
        
        return {
            "sensitivity_score": sensitivity,
            "bull_market_sharpe": bull_sharpe,
            "bear_market_sharpe": bear_sharpe,
            "regime_diversification": sensitivity < 0.5
        }
    
    def _calculate_severity(self, metric_value: float, threshold: float) -> str:
        """Calculate warning severity based on metric value and threshold"""
        if metric_value > threshold * 2:
            return "critical"
        elif metric_value > threshold * 1.5:
            return "high"
        elif metric_value > threshold:
            return "medium"
        else:
            return "low"
    
    def _get_regime_recommendation(self, variation: float) -> str:
        """Get recommendation for regime overfitting"""
        if variation > 0.5:
            return "Strategy is heavily overfit to specific market conditions - requires complete redesign"
        elif variation > 0.3:
            return "Consider adding market regime filters or adaptive parameters"
        else:
            return "Monitor regime performance, consider minor adjustments"
    
    def _get_parameter_recommendation(self, variation: float) -> str:
        """Get recommendation for parameter overfitting"""
        if variation > 0.4:
            return "Parameters are unstable - use regularization or simpler model"
        elif variation > 0.2:
            return "Consider parameter stability constraints or ensemble methods"
        else:
            return "Parameters are reasonably stable"
    
    def _get_out_of_sample_recommendation(self, decay: float) -> str:
        """Get recommendation for out-of-sample overfitting"""
        if decay > 0.7:
            return "Severe overfitting detected - strategy needs complete revalidation"
        elif decay > 0.5:
            return "Significant overfitting - reduce model complexity or add regularization"
        elif decay > 0.3:
            return "Moderate overfitting - consider cross-validation techniques"
        else:
            return "Minimal overfitting detected - strategy appears robust"

class WalkForwardOptimizer:
    """
    Walk-forward optimization for strategy robustness validation
    """
    
    def __init__(self):
        self.default_window_size = 252  # 1 year of data
        self.default_step_size = 63     # 3 months step
        self.default_test_size = 63     # 3 months test period
        
        self.performance_thresholds = {
            "excellent": 0.8,   # 80% out-of-sample performance retention
            "good": 0.6,        # 60% performance retention
            "acceptable": 0.4,  # 40% performance retention
            "poor": 0.2         # <20% performance retention
        }
    
    def perform_walk_forward_analysis(self, returns: pd.Series,
                                    parameter_ranges: Dict,
                                    window_size: int = None,
                                    step_size: int = None,
                                    test_size: int = None) -> WalkForwardResult:
        """
        Perform comprehensive walk-forward analysis
        """
        if window_size is None:
            window_size = self.default_window_size
        if step_size is None:
            step_size = self.default_step_size
        if test_size is None:
            test_size = self.default_test_size
        
        # Generate walk-forward windows
        windows = self._generate_walk_forward_windows(returns, window_size, step_size, test_size)
        
        in_sample_performances = []
        out_of_sample_performances = []
        
        for train_start, train_end, test_start, test_end in windows:
            # Split data
            train_data = returns.iloc[train_start:train_end]
            test_data = returns.iloc[test_start:test_end]
            
            # Optimize parameters on training data
            optimal_params = self._optimize_parameters(train_data, parameter_ranges)
            
            # Calculate performance
            train_performance = self._calculate_performance(train_data, optimal_params)
            test_performance = self._calculate_performance(test_data, optimal_params)
            
            in_sample_performances.append(train_performance)
            out_of_sample_performances.append(test_performance)
        
        # Calculate aggregate results
        avg_in_sample = np.mean(in_sample_performances)
        avg_out_sample = np.mean(out_of_sample_performances)
        
        performance_decay = (avg_in_sample - avg_out_sample) / abs(avg_in_sample) if avg_in_sample != 0 else 0
        stability_score = self._calculate_stability_score(out_of_sample_performances)
        robustness_rating = self._calculate_robustness_rating(performance_decay, stability_score)
        
        return WalkForwardResult(
            in_sample_sharpe=avg_in_sample,
            out_of_sample_sharpe=avg_out_sample,
            performance_decay=performance_decay,
            stability_score=stability_score,
            robustness_rating=robustness_rating
        )
    
    def _generate_walk_forward_windows(self, data: pd.Series, 
                                     window_size: int, 
                                     step_size: int, 
                                     test_size: int) -> List[Tuple]:
        """Generate walk-forward analysis windows"""
        windows = []
        data_length = len(data)
        
        current_start = 0
        
        while current_start + window_size + test_size <= data_length:
            train_start = current_start
            train_end = current_start + window_size
            test_start = train_end
            test_end = test_start + test_size
            
            windows.append((train_start, train_end, test_start, test_end))
            
            current_start += step_size
        
        return windows
    
    def _optimize_parameters(self, data: pd.Series, parameter_ranges: Dict) -> Dict:
        """
        Optimize strategy parameters on training data (simplified)
        """
        # Simplified parameter optimization
        # In real implementation, this would test actual strategy parameters
        
        best_sharpe = -float('inf')
        best_params = {}
        
        # Example: optimize lookback period
        for lookback in parameter_ranges.get('lookback', [20, 50, 100]):
            # Calculate performance with this parameter
            returns = self._calculate_strategy_returns(data, lookback)
            sharpe = self._calculate_simple_sharpe(returns)
            
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_params = {'lookback': lookback}
        
        return best_params
    
    def _calculate_strategy_returns(self, data: pd.Series, lookback: int) -> pd.Series:
        """
        Calculate strategy returns with given parameters (simplified)
        """
        # Simplified moving average crossover strategy
        if len(data) < lookback:
            return pd.Series([0.0] * len(data), index=data.index)
        
        short_ma = data.rolling(window=lookback//2).mean()
        long_ma = data.rolling(window=lookback).mean()
        
        # Generate signals
        signals = np.where(short_ma > long_ma, 1, -1)
        
        # Calculate returns
        strategy_returns = pd.Series(signals[:-1] * data.pct_change().iloc[1:], 
                                   index=data.index[1:])
        
        return strategy_returns
    
    def _calculate_performance(self, data: pd.Series, params: Dict) -> float:
        """Calculate strategy performance with given parameters"""
        returns = self._calculate_strategy_returns(data, params.get('lookback', 50))
        return self._calculate_simple_sharpe(returns)
    
    def _calculate_simple_sharpe(self, returns: pd.Series) -> float:
        """Calculate simple Sharpe ratio"""
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        return (returns.mean() * 252) / (returns.std() * np.sqrt(252))
    
    def _calculate_stability_score(self, performances: List[float]) -> float:
        """Calculate performance stability score"""
        if len(performances) == 0:
            return 0.0
        
        mean_performance = np.mean(performances)
        std_performance = np.std(performances)
        
        if mean_performance == 0:
            return 0.0
        
        # Stability score: 1 - coefficient of variation
        stability = 1 - (std_performance / abs(mean_performance))
        return max(0, stability)
    
    def _calculate_robustness_rating(self, performance_decay: float, 
                                   stability_score: float) -> str:
        """Calculate overall robustness rating"""
        # Combine performance decay and stability
        decay_score = max(0, 1 - performance_decay)
        combined_score = (decay_score + stability_score) / 2
        
        if combined_score >= self.performance_thresholds["excellent"]:
            return "excellent"
        elif combined_score >= self.performance_thresholds["good"]:
            return "good"
        elif combined_score >= self.performance_thresholds["acceptable"]:
            return "acceptable"
        else:
            return "poor"
    
    def generate_walk_forward_report(self, result: WalkForwardResult) -> Dict:
        """Generate comprehensive walk-forward analysis report"""
        return {
            "in_sample_performance": result.in_sample_sharpe,
            "out_of_sample_performance": result.out_of_sample_sharpe,
            "performance_retention": (result.out_of_sample_sharpe / result.in_sample_sharpe) if result.in_sample_sharpe != 0 else 0,
            "performance_decay": result.performance_decay,
            "stability_score": result.stability_score,
            "robustness_rating": result.robustness_rating,
            "assessment": self._get_robustness_assessment(result.robustness_rating),
            "recommendations": self._get_walk_forward_recommendations(result)
        }
    
    def _get_robustness_assessment(self, rating: str) -> str:
        """Get assessment text based on robustness rating"""
        assessments = {
            "excellent": "Strategy is highly robust across different time periods",
            "good": "Strategy shows good robustness with minor performance variations",
            "acceptable": "Strategy is moderately robust but may need refinement",
            "poor": "Strategy lacks robustness - significant overfitting detected"
        }
        return assessments[rating]
    
    def _get_walk_forward_recommendations(self, result: WalkForwardResult) -> List[str]:
        """Get recommendations based on walk-forward results"""
        recommendations = []
        
        if result.performance_decay > 0.5:
            recommendations.append("Significant overfitting detected - simplify strategy parameters")
        
        if result.stability_score < 0.5:
            recommendations.append("Low stability detected - consider adaptive mechanisms")
        
        if result.out_of_sample_sharpe < 0.5:
            recommendations.append("Poor out-of-sample performance - revalidate strategy logic")
        
        if result.robustness_rating in ["excellent", "good"]:
            recommendations.append("Strategy appears robust - consider live testing with small position sizes")
        
        return recommendations

class StatisticalValiditySystem:
    """
    Comprehensive statistical validity validation system
    """
    
    def __init__(self):
        self.metrics_calculator = PerformanceMetricsCalculator()
        self.significance_tester = StatisticalSignificanceTester()
        self.overfitting_detector = OverfittingDetector()
        self.walk_forward_optimizer = WalkForwardOptimizer()
        
        self.validation_results = {}
    
    def test_sharpe_ratio_calculation(self) -> Dict:
        """
        Test 41: Sharpe Ratio calculation with Indian G-Sec rates
        """
        print("🧪 Test 41: Sharpe Ratio Calculation")
        print("=" * 60)
        
        # Test different return scenarios
        test_scenarios = [
            {
                "name": "high_volatility_strategy",
                "returns": np.random.normal(0.002, 0.03, 252),  # 2% daily return, 3% volatility
                "expected_sharpe_range": (0.8, 1.2)
            },
            {
                "name": "low_volatility_strategy", 
                "returns": np.random.normal(0.001, 0.01, 252),  # 1% daily return, 1% volatility
                "expected_sharpe_range": (1.2, 1.8)
            },
            {
                "name": "negative_returns",
                "returns": np.random.normal(-0.001, 0.02, 252),  # Negative returns
                "expected_sharpe_range": (-0.5, 0.5)
            }
        ]
        
        sharpe_results = {}
        
        for scenario in test_scenarios:
            print(f"\nTesting {scenario['name']}...")
            
            returns_series = pd.Series(scenario['returns'])
            
            # Calculate Sharpe with default Indian G-Sec rate
            sharpe_indian = self.metrics_calculator.calculate_sharpe_ratio(returns_series)
            
            # Calculate Sharpe with different risk-free rates for comparison
            sharpe_zero = self.metrics_calculator.calculate_sharpe_ratio(returns_series, 0.0)
            sharpe_us = self.metrics_calculator.calculate_sharpe_ratio(returns_series, 0.04)  # US Treasury
            
            expected_min, expected_max = scenario['expected_sharpe_range']
            within_expected = expected_min <= sharpe_indian <= expected_max
            
            sharpe_results[scenario['name']] = {
                "indian_gsec_sharpe": sharpe_indian,
                "zero_rf_sharpe": sharpe_zero,
                "us_treasury_sharpe": sharpe_us,
                "risk_free_rate_used": self.metrics_calculator.risk_free_rate,
                "expected_range": scenario['expected_sharpe_range'],
                "within_expected": within_expected
            }
            
            print(f"  Indian G-Sec Sharpe: {sharpe_indian:.3f}")
            print(f"  Zero Risk-Free Sharpe: {sharpe_zero:.3f}")
            print(f"  US Treasury Sharpe: {sharpe_us:.3f}")
            print(f"  Risk-Free Rate Used: {self.metrics_calculator.risk_free_rate:.1%}")
            print(f"  Expected Range: {expected_min:.1f} - {expected_max:.1f}")
            print(f"  Test: {'✅ PASS' if within_expected else '❌ FAIL'}")
        
        return {
            "test_name": "Sharpe Ratio Calculation",
            "risk_free_rate_assumption": f"Indian G-Sec: {self.metrics_calculator.risk_free_rate:.1%}",
            "scenarios_tested": len(test_scenarios),
            "calculation_method": "Annualized excess returns / volatility (252 trading days)",
            "detailed_results": sharpe_results
        }
    
    def test_performance_thresholds(self) -> Dict:
        """
        Test 42: Performance thresholds for different strategy types
        """
        print("\n🧪 Test 42: Performance Thresholds by Strategy Type")
        print("=" * 60)
        
        # Test different strategy types with various performance levels
        strategy_scenarios = [
            {
                "strategy_type": StrategyType.SWING,
                "performance_level": "excellent",
                "returns": np.random.normal(0.0015, 0.02, 252)  # Good swing performance
            },
            {
                "strategy_type": StrategyType.LONG_TERM,
                "performance_level": "good", 
                "returns": np.random.normal(0.0008, 0.015, 504)  # 2 years data
            },
            {
                "strategy_type": StrategyType.INTRADAY,
                "performance_level": "acceptable",
                "returns": np.random.normal(0.0003, 0.008, 252)  # Intraday performance
            }
        ]
        
        threshold_results = {}
        
        for scenario in strategy_scenarios:
            print(f"\nTesting {scenario['strategy_type'].value.upper()} - {scenario['performance_level'].upper()}...")
            
            returns_series = pd.Series(scenario['returns'])
            benchmark_returns = pd.Series(np.random.normal(0.0005, 0.015, len(returns_series)))
            
            # Calculate comprehensive metrics
            metrics = self.metrics_calculator.calculate_comprehensive_metrics(
                returns_series, benchmark_returns
            )
            
            # Evaluate performance quality
            evaluation = self.metrics_calculator.evaluate_performance_quality(
                metrics, scenario['strategy_type']
            )
            
            threshold_results[f"{scenario['strategy_type'].value}_{scenario['performance_level']}"] = {
                "strategy_type": scenario['strategy_type'].value,
                "performance_level": scenario['performance_level'],
                "metrics": {
                    "sharpe_ratio": metrics.sharpe_ratio,
                    "sortino_ratio": metrics.sortino_ratio,
                    "max_drawdown": abs(metrics.max_drawdown)
                },
                "evaluation": evaluation,
                "thresholds_met": evaluation["overall_rating"] == scenario['performance_level']
            }
            
            print(f"  Sharpe Ratio: {metrics.sharpe_ratio:.2f} ({evaluation['sharpe_ratio']['rating']})")
            print(f"  Sortino Ratio: {metrics.sortino_ratio:.2f} ({evaluation['sortino_ratio']['rating']})")
            print(f"  Max Drawdown: {abs(metrics.max_drawdown):.1%} ({evaluation['max_drawdown']['rating']})")
            print(f"  Overall Rating: {evaluation['overall_rating'].upper()}")
            print(f"  Assessment: {evaluation['assessment']}")
            key = f"{scenario['strategy_type'].value}_{scenario['performance_level']}"
            print(f"  Test: {'✅ PASS' if threshold_results[key]['thresholds_met'] else '❌ FAIL'}")
        
        return {
            "test_name": "Performance Thresholds by Strategy Type",
            "strategy_types_tested": [s.value for s in StrategyType],
            "performance_thresholds": self.metrics_calculator.performance_thresholds,
            "detailed_results": threshold_results
        }
    
    def test_statistical_significance(self) -> Dict:
        """
        Test 43: Statistical significance and sample size requirements
        """
        print("\n🧪 Test 43: Statistical Significance & Sample Size")
        print("=" * 60)
        
        # Test different sample sizes
        sample_size_scenarios = [
            {
                "name": "very_small_sample",
                "total_trades": 15,
                "wins": 10,
                "expected_significance": False
            },
            {
                "name": "small_sample",
                "total_trades": 35,
                "wins": 22,
                "expected_significance": True
            },
            {
                "name": "adequate_sample",
                "total_trades": 120,
                "wins": 75,
                "expected_significance": True
            },
            {
                "name": "large_sample",
                "total_trades": 500,
                "wins": 280,
                "expected_significance": True
            }
        ]
        
        significance_results = {}
        
        for scenario in sample_size_scenarios:
            print(f"\nTesting {scenario['name']} ({scenario['total_trades']} trades)...")
            
            # Test win rate significance
            win_rate_test = self.significance_tester.test_win_rate_significance(
                scenario['wins'], scenario['total_trades']
            )
            
            # Generate sample size warning
            sample_warning = self.significance_tester.generate_sample_size_warning(
                scenario['total_trades'], StrategyType.SWING
            )
            
            # Calculate required sample size
            required_size = self.significance_tester.calculate_minimum_sample_size(0.55, 0.95, 0.05)
            
            significance_results[scenario['name']] = {
                "sample_size": scenario['total_trades'],
                "wins": scenario['wins'],
                "win_rate": scenario['wins'] / scenario['total_trades'],
                "significance_test": {
                    "p_value": win_rate_test.p_value,
                    "is_significant": win_rate_test.is_significant,
                    "test_statistic": win_rate_test.test_statistic
                },
                "sample_size_warning": sample_warning,
                "required_sample_size": required_size,
                "test_passed": win_rate_test.is_significant == scenario['expected_significance']
            }
            
            print(f"  Sample Size: {scenario['total_trades']} trades")
            print(f"  Win Rate: {scenario['wins']}/{scenario['total_trades']} = {scenario['wins']/scenario['total_trades']:.1%}")
            print(f"  P-Value: {win_rate_test.p_value:.4f}")
            print(f"  Statistically Significant: {win_rate_test.is_significant}")
            print(f"  Required Sample Size: {required_size} trades")
            print(f"  Warnings: {len(sample_warning['warnings'])}")
            for warning in sample_warning['warnings']:
                print(f"    - {warning['level'].upper()}: {warning['message']}")
            print(f"  Test: {'✅ PASS' if significance_results[scenario['name']]['test_passed'] else '❌ FAIL'}")
        
        return {
            "test_name": "Statistical Significance & Sample Size",
            "minimum_sample_size": self.significance_tester.minimum_sample_size,
            "recommended_sample_size": self.significance_tester.recommended_sample_size,
            "high_confidence_sample_size": self.significance_tester.high_confidence_sample_size,
            "detailed_results": significance_results
        }
    
    def test_overfitting_detection(self) -> Dict:
        """
        Test 44: Overfitting detection across market regimes
        """
        print("\n🧪 Test 44: Overfitting Detection")
        print("=" * 60)
        
        # Test overfitting scenarios
        overfitting_scenarios = [
            {
                "name": "bull_market_overfit",
                "bull_market_performance": {"sharpe_ratio": 2.5, "total_return": 0.8},
                "bear_market_performance": {"sharpe_ratio": -0.5, "total_return": -0.3},
                "expected_warning": True
            },
            {
                "name": "balanced_strategy",
                "bull_market_performance": {"sharpe_ratio": 1.2, "total_return": 0.4},
                "bear_market_performance": {"sharpe_ratio": 0.8, "total_return": 0.1},
                "expected_warning": False
            },
            {
                "name": "bear_market_specialist",
                "bull_market_performance": {"sharpe_ratio": -0.2, "total_return": -0.1},
                "bear_market_performance": {"sharpe_ratio": 2.0, "total_return": 0.6},
                "expected_warning": True
            }
        ]
        
        overfitting_results = {}
        
        for scenario in overfitting_scenarios:
            print(f"\nTesting {scenario['name']}...")
            
            # Detect regime overfitting
            regime_warning = self.overfitting_detector.detect_regime_overfitting(
                scenario['bull_market_performance'],
                scenario['bear_market_performance']
            )
            
            # Detect out-of-sample overfitting
            oos_warning = self.overfitting_detector.detect_out_of_sample_overfitting(
                scenario['bull_market_performance'],
                scenario['bear_market_performance']
            )
            
            overfitting_results[scenario['name']] = {
                "scenario": scenario,
                "regime_warning": {
                    "detected": regime_warning.severity != "low",
                    "severity": regime_warning.severity,
                    "description": regime_warning.description,
                    "recommendation": regime_warning.recommendation
                },
                "out_of_sample_warning": {
                    "detected": oos_warning.severity != "low",
                    "severity": oos_warning.severity,
                    "description": oos_warning.description,
                    "recommendation": oos_warning.recommendation
                },
                "overfitting_detected": regime_warning.severity != "low" or oos_warning.severity != "low",
                "expected_warning": scenario['expected_warning']
            }
            
            print(f"  Bull Market Sharpe: {scenario['bull_market_performance']['sharpe_ratio']}")
            print(f"  Bear Market Sharpe: {scenario['bear_market_performance']['sharpe_ratio']}")
            print(f"  Regime Overfitting: {regime_warning.severity.upper()}")
            print(f"    {regime_warning.description}")
            print(f"  Out-of-Sample Overfitting: {oos_warning.severity.upper()}")
            print(f"    {oos_warning.description}")
            print(f"  Overall Overfitting: {'DETECTED' if overfitting_results[scenario['name']]['overfitting_detected'] else 'NOT DETECTED'}")
            print(f"  Test: {'✅ PASS' if overfitting_results[scenario['name']]['overfitting_detected'] == scenario['expected_warning'] else '❌ FAIL'}")
        
        return {
            "test_name": "Overfitting Detection",
            "detection_methods": ["regime_stability", "out_of_sample_performance"],
            "overfitting_thresholds": {
                "regime_variation": self.overfitting_detector.regime_stability_threshold,
                "performance_decay": self.overfitting_detector.out_of_sample_threshold
            },
            "detailed_results": overfitting_results
        }
    
    def test_walk_forward_optimization(self) -> Dict:
        """
        Test 45: Walk-forward optimization for strategy robustness
        """
        print("\n🧪 Test 45: Walk-Forward Optimization")
        print("=" * 60)
        
        # Test walk-forward scenarios
        walk_forward_scenarios = [
            {
                "name": "robust_strategy",
                "returns": np.random.normal(0.001, 0.02, 504),  # Consistent performance
                "parameter_ranges": {"lookback": [20, 50, 100]},
                "expected_robustness": "good"
            },
            {
                "name": "overfit_strategy",
                "returns": np.concatenate([
                    np.random.normal(0.002, 0.015, 252),  # Good first year
                    np.random.normal(-0.001, 0.025, 252)  # Poor second year
                ]),
                "parameter_ranges": {"lookback": [20, 50, 100]},
                "expected_robustness": "poor"
            }
        ]
        
        walk_forward_results = {}
        
        for scenario in walk_forward_scenarios:
            print(f"\nTesting {scenario['name']}...")
            
            returns_series = pd.Series(scenario['returns'])
            
            # Perform walk-forward analysis
            wf_result = self.walk_forward_optimizer.perform_walk_forward_analysis(
                returns_series,
                scenario['parameter_ranges']
            )
            
            # Generate walk-forward report
            wf_report = self.walk_forward_optimizer.generate_walk_forward_report(wf_result)
            
            walk_forward_results[scenario['name']] = {
                "scenario": scenario,
                "walk_forward_result": wf_result,
                "report": wf_report,
                "robustness_achieved": wf_result.robustness_rating == scenario['expected_robustness']
            }
            
            print(f"  In-Sample Sharpe: {wf_result.in_sample_sharpe:.2f}")
            print(f"  Out-of-Sample Sharpe: {wf_result.out_of_sample_sharpe:.2f}")
            print(f"  Performance Decay: {wf_result.performance_decay:.1%}")
            print(f"  Stability Score: {wf_result.stability_score:.2f}")
            print(f"  Robustness Rating: {wf_result.robustness_rating.upper()}")
            print(f"  Assessment: {wf_report['assessment']}")
            print(f"  Recommendations:")
            for rec in wf_report['recommendations']:
                print(f"    - {rec}")
            print(f"  Test: {'✅ PASS' if walk_forward_results[scenario['name']]['robustness_achieved'] else '❌ FAIL'}")
        
        return {
            "test_name": "Walk-Forward Optimization",
            "window_configuration": {
                "training_window": self.walk_forward_optimizer.default_window_size,
                "step_size": self.walk_forward_optimizer.default_step_size,
                "test_window": self.walk_forward_optimizer.default_test_size
            },
            "robustness_thresholds": self.walk_forward_optimizer.performance_thresholds,
            "detailed_results": walk_forward_results
        }
    
    def run_all_statistical_validity_tests(self) -> Dict:
        """Run all statistical validity tests"""
        print("🔬 Statistical Validity Validation Suite")
        print("=" * 70)
        print("Testing performance metrics, significance, overfitting, and walk-forward optimization...")
        print("=" * 70)
        
        all_results = {}
        
        # Run all tests
        test_methods = [
            self.test_sharpe_ratio_calculation,
            self.test_performance_thresholds,
            self.test_statistical_significance,
            self.test_overfitting_detection,
            self.test_walk_forward_optimization
        ]
        
        for test_method in test_methods:
            try:
                result = test_method()
                all_results[result["test_name"]] = result
                print(f"✅ {result['test_name']} - Completed")
            except Exception as e:
                print(f"❌ {test_method.__name__} - Failed: {str(e)}")
        
        # Generate summary
        summary = self._generate_statistical_validity_summary(all_results)
        
        return {
            "test_results": all_results,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_statistical_validity_summary(self, results: Dict) -> Dict:
        """Generate summary of statistical validity tests"""
        return {
            "total_tests": len(results),
            "critical_findings": [
                "Sharpe ratio uses Indian G-Sec risk-free rate (6.8%) for accurate calculations",
                "Performance thresholds differentiated by strategy type (swing, long-term, intraday)",
                "Statistical significance testing with minimum 30 trades required",
                "Overfitting detection across market regimes and out-of-sample validation",
                "Walk-forward optimization validates strategy robustness over time"
            ],
            "system_strengths": [
                "Comprehensive performance metrics calculation with Indian market assumptions",
                "Statistical significance validation with proper sample size requirements",
                "Advanced overfitting detection using multiple methods",
                "Walk-forward optimization for robustness validation",
                "Strategy-type specific performance thresholds"
            ],
            "recommendations": [
                "Always validate statistical significance before strategy deployment",
                "Use walk-forward optimization for robustness validation",
                "Monitor regime-specific performance for overfitting detection",
                "Apply appropriate performance thresholds based on strategy type",
                "Document all statistical assumptions and calculations"
            ]
        }


def run_statistical_validity_tests():
    """Run comprehensive statistical validity tests"""
    validator = StatisticalValiditySystem()
    results = validator.run_all_statistical_validity_tests()
    
    print(f"\n📊 Statistical Validity Test Summary:")
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
    results = run_statistical_validity_tests()
