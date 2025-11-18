"""
Enterprise Stock Trading Framework - Backtesting Engine
Walk-forward analysis, optimization, and Monte Carlo simulation
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import asyncio
import json
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradeSignal(Enum):
    """Trade signal types"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class PositionType(Enum):
    """Position types"""
    LONG = "LONG"
    SHORT = "SHORT"
    FLAT = "FLAT"


@dataclass
class Trade:
    """Individual trade representation"""
    symbol: str
    entry_date: datetime
    exit_date: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    quantity: int
    position_type: PositionType
    entry_signal: Dict[str, Any]
    exit_signal: Optional[Dict[str, Any]]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    
    def calculate_pnl(self) -> float:
        """Calculate trade P&L"""
        if self.exit_price is None:
            return 0.0
        
        if self.position_type == PositionType.LONG:
            return (self.exit_price - self.entry_price) * self.quantity
        else:
            return (self.entry_price - self.exit_price) * self.quantity
    
    def calculate_pnl_percent(self) -> float:
        """Calculate trade P&L percentage"""
        if self.exit_price is None:
            return 0.0
        
        if self.position_type == PositionType.LONG:
            return ((self.exit_price - self.entry_price) / self.entry_price) * 100
        else:
            return ((self.entry_price - self.exit_price) / self.entry_price) * 100
    
    def calculate_duration(self) -> int:
        """Calculate trade duration in days"""
        if self.exit_date is None:
            return 0
        return (self.exit_date - self.entry_date).days


@dataclass
class BacktestConfig:
    """Backtesting configuration"""
    initial_capital: float
    commission_per_trade: float
    slippage_percent: float
    position_sizing_method: str  # fixed, kelly, percentage
    position_size_percent: float
    max_position_size: float
    risk_per_trade: float
    benchmark_symbol: str


@dataclass
class BacktestResult:
    """Backtesting results"""
    total_return: float
    annualized_return: float
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_trade_return: float
    avg_trade_duration: float
    var_95: float
    calmar_ratio: float
    beta: float
    alpha: float
    trades: List[Trade]
    equity_curve: pd.Series
    benchmark_returns: pd.Series
    monthly_returns: pd.Series
    drawdown_series: pd.Series


class Strategy(ABC):
    """Abstract base class for trading strategies"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get('name', 'DefaultStrategy')
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate trading signals from data"""
        pass
    
    @abstractmethod
    def calculate_position_size(self, signal: Dict[str, Any], portfolio_value: float, risk_params: Dict) -> int:
        """Calculate position size based on signal and risk parameters"""
        pass


class SMCFVGStrategy(Strategy):
    """Smart Money Concepts FVG-based strategy"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.fvg_strength_required = config.get('fvg_strength', 'medium')
        self.volume_multiplier = config.get('volume_multiplier', 1.5)
        self.structure_alignment = config.get('structure_alignment', True)
        self.rr_ratio = config.get('risk_reward_ratio', 2.5)
    
    def generate_signals(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate SMC-based signals"""
        signals = []
        
        if len(data) < 50:
            return signals
        
        # Calculate indicators
        data = self._calculate_indicators(data)
        
        # Detect FVG zones
        fvg_zones = self._detect_fvg_zones(data)
        
        # Analyze market structure
        structure = self._analyze_market_structure(data)
        
        # Volume analysis
        volume_signals = self._analyze_volume(data)
        
        for i in range(20, len(data)):
            current_candle = data.iloc[i]
            
            # Check for FVG fill setup
            fvg_signal = self._check_fvg_fill_setup(current_candle, fvg_zones, i)
            if fvg_signal:
                # Additional confirmations
                volume_confirm = self._check_volume_confirmation(current_candle, volume_signals, i)
                structure_confirm = self._check_structure_confirmation(structure, i)
                
                if volume_confirm and (not self.structure_alignment or structure_confirm):
                    signals.append(fvg_signal)
        
        return signals
    
    def _calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        # Moving averages
        data['sma_20'] = data['close'].rolling(20).mean()
        data['sma_50'] = data['close'].rolling(50).mean()
        data['ema_12'] = data['close'].ewm(span=12).mean()
        data['ema_26'] = data['close'].ewm(span=26).mean()
        
        # RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        data['macd'] = data['ema_12'] - data['ema_26']
        data['macd_signal'] = data['macd'].ewm(span=9).mean()
        data['macd_histogram'] = data['macd'] - data['macd_signal']
        
        # ATR
        high_low = data['high'] - data['low']
        high_close = abs(data['high'] - data['close'].shift())
        low_close = abs(data['low'] - data['close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        data['atr'] = true_range.rolling(14).mean()
        
        # Volume indicators
        data['volume_sma'] = data['volume'].rolling(20).mean()
        data['volume_ratio'] = data['volume'] / data['volume_sma']
        
        return data
    
    def _detect_fvg_zones(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Fair Value Gaps"""
        fvg_zones = []
        
        for i in range(2, len(data)):
            candle_1 = data.iloc[i-2]
            candle_2 = data.iloc[i-1]
            
            # Bullish FVG
            if candle_1['high'] < candle_2['low']:
                fvg_zones.append({
                    'type': 'bullish',
                    'high': candle_2['low'],
                    'low': candle_1['high'],
                    'midpoint': (candle_2['low'] + candle_1['high']) / 2,
                    'candle_index': i-1,
                    'strength': self._calculate_fvg_strength(candle_1, candle_2)
                })
            
            # Bearish FVG
            elif candle_1['low'] > candle_2['high']:
                fvg_zones.append({
                    'type': 'bearish',
                    'high': candle_1['low'],
                    'low': candle_2['high'],
                    'midpoint': (candle_1['low'] + candle_2['high']) / 2,
                    'candle_index': i-1,
                    'strength': self._calculate_fvg_strength(candle_1, candle_2)
                })
        
        return fvg_zones
    
    def _calculate_fvg_strength(self, candle_1: pd.Series, candle_2: pd.Series) -> str:
        """Calculate FVG strength"""
        avg_volume = (candle_1['volume'] + candle_2['volume']) / 2
        gap_size = abs(candle_1['high'] - candle_2['low']) / candle_1['close']
        
        if avg_volume > 1000000 and gap_size > 0.02:
            return 'strong'
        elif avg_volume > 500000 and gap_size > 0.01:
            return 'medium'
        else:
            return 'weak'
    
    def _analyze_market_structure(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market structure"""
        swing_highs = []
        swing_lows = []
        
        for i in range(2, len(data) - 2):
            candle = data.iloc[i]
            
            # Swing high
            if (candle['high'] > data.iloc[i-1]['high'] and 
                candle['high'] > data.iloc[i-2]['high'] and
                candle['high'] > data.iloc[i+1]['high'] and 
                candle['high'] > data.iloc[i+2]['high']):
                swing_highs.append((i, candle['high']))
            
            # Swing low
            if (candle['low'] < data.iloc[i-1]['low'] and 
                candle['low'] < data.iloc[i-2]['low'] and
                candle['low'] < data.iloc[i+1]['low'] and 
                candle['low'] < data.iloc[i+2]['low']):
                swing_lows.append((i, candle['low']))
        
        # Determine trend
        trend = "sideways"
        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            if swing_highs[-1][1] > swing_highs[-2][1] and swing_lows[-1][1] > swing_lows[-2][1]:
                trend = "bullish"
            elif swing_highs[-1][1] < swing_highs[-2][1] and swing_lows[-1][1] < swing_lows[-2][1]:
                trend = "bearish"
        
        return {
            'trend': trend,
            'swing_highs': swing_highs,
            'swing_lows': swing_lows
        }
    
    def _analyze_volume(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volume patterns"""
        volume_spikes = []
        
        for i in range(20, len(data)):
            if data.iloc[i]['volume_ratio'] > self.volume_multiplier:
                volume_spikes.append(i)
        
        return {
            'volume_spikes': volume_spikes,
            'avg_volume_ratio': data['volume_ratio'].mean()
        }
    
    def _check_fvg_fill_setup(self, candle: pd.Series, fvg_zones: List[Dict], current_index: int) -> Optional[Dict[str, Any]]:
        """Check for FVG fill setup"""
        current_price = candle['close']
        
        for fvg in fvg_zones:
            # Check if price is near FVG zone
            if (fvg['type'] == 'bullish' and 
                current_price > fvg['low'] and current_price < fvg['high'] * 1.02 and
                fvg['candle_index'] < current_index and
                current_index - fvg['candle_index'] < 10):  # Recent FVG
                
                if fvg['strength'] == self.fvg_strength_required or self.fvg_strength_required == 'any':
                    return {
                        'signal': TradeSignal.BUY,
                        'price': current_price,
                        'strength': 85 if fvg['strength'] == 'strong' else 70,
                        'fvg_zone': fvg,
                        'reason': f"FVG fill setup - {fvg['strength']} FVG"
                    }
        
        return None
    
    def _check_volume_confirmation(self, candle: pd.Series, volume_signals: Dict, current_index: int) -> bool:
        """Check volume confirmation"""
        return candle['volume_ratio'] > self.volume_multiplier
    
    def _check_structure_confirmation(self, structure: Dict, current_index: int) -> bool:
        """Check market structure confirmation"""
        return structure['trend'] == 'bullish'
    
    def calculate_position_size(self, signal: Dict[str, Any], portfolio_value: float, risk_params: Dict) -> int:
        """Calculate position size using Kelly Criterion"""
        if self.config.get('position_sizing_method') == 'kelly':
            win_rate = 0.65  # Historical win rate
            avg_win = self.rr_ratio
            avg_loss = 1.0
            
            kelly_fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
            kelly_fraction = max(0, min(0.25, kelly_fraction))  # Cap at 25%
            
            position_value = portfolio_value * kelly_fraction
        else:
            position_value = portfolio_value * (self.config.get('position_size_percent', 2.0) / 100)
        
        # Limit to max position size
        position_value = min(position_value, self.config.get('max_position_size', portfolio_value * 0.1))
        
        return int(position_value / signal['price'])


class BacktestEngine:
    """Main backtesting engine"""
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = []
        self.current_capital = config.initial_capital
        self.current_position = None
    
    async def run_backtest(self, strategy: Strategy, data: pd.DataFrame, benchmark_data: Optional[pd.DataFrame] = None) -> BacktestResult:
        """Run backtest with given strategy and data"""
        logger.info(f"Starting backtest for strategy: {strategy.name}")
        
        # Initialize
        self.trades = []
        self.equity_curve = [self.config.initial_capital]
        self.current_capital = self.config.initial_capital
        self.current_position = None
        
        # Generate signals
        signals = strategy.generate_signals(data)
        
        # Process signals chronologically
        for i, signal in enumerate(signals):
            signal_date = data.index[min(signal.get('candle_index', i), len(data) - 1)]
            
            if signal['signal'] == TradeSignal.BUY and self.current_position is None:
                await self._enter_position(signal, signal_date, data)
            elif signal['signal'] == TradeSignal.SELL and self.current_position is not None:
                await self._exit_position(signal, signal_date, data)
        
        # Close any open position at the end
        if self.current_position is not None:
            await self._close_position(data.index[-1], data.iloc[-1]['close'], "End of backtest")
        
        # Calculate results
        return self._calculate_results(data, benchmark_data)
    
    async def _enter_position(self, signal: Dict[str, Any], entry_date: datetime, data: pd.DataFrame):
        """Enter a position"""
        entry_price = signal['price']
        
        # Calculate position size
        position_size = self._calculate_position_size(signal, entry_price)
        
        # Apply slippage
        entry_price *= (1 + self.config.slippage_percent / 100)
        
        # Calculate commission
        commission = self.config.commission_per_trade
        
        # Create trade
        trade = Trade(
            symbol=data.iloc[0].get('symbol', 'UNKNOWN'),
            entry_date=entry_date,
            exit_date=None,
            entry_price=entry_price,
            exit_price=None,
            quantity=position_size,
            position_type=PositionType.LONG,
            entry_signal=signal,
            exit_signal=None,
            stop_loss=self._calculate_stop_loss(entry_price, data),
            take_profit=self._calculate_take_profit(entry_price, data)
        )
        
        self.current_position = trade
        self.current_capital -= (position_size * entry_price) + commission
        
        logger.info(f"Entered position: {position_size} shares at ₹{entry_price:.2f}")
    
    async def _exit_position(self, signal: Dict[str, Any], exit_date: datetime, data: pd.DataFrame):
        """Exit current position"""
        if self.current_position is None:
            return
        
        exit_price = signal['price']
        
        # Apply slippage
        exit_price *= (1 - self.config.slippage_percent / 100)
        
        # Calculate commission
        commission = self.config.commission_per_trade
        
        # Update trade
        self.current_position.exit_date = exit_date
        self.current_position.exit_price = exit_price
        self.current_position.exit_signal = signal
        
        # Update capital
        self.current_capital += (self.current_position.quantity * exit_price) - commission
        
        # Add to trades list
        self.trades.append(self.current_position)
        
        logger.info(f"Exited position at ₹{exit_price:.2f}, P&L: ₹{self.current_position.calculate_pnl():.2f}")
        
        self.current_position = None
    
    async def _close_position(self, exit_date: datetime, exit_price: float, reason: str):
        """Close position at end of backtest"""
        if self.current_position is None:
            return
        
        # Apply slippage
        exit_price *= (1 - self.config.slippage_percent / 100)
        
        # Calculate commission
        commission = self.config.commission_per_trade
        
        # Update trade
        self.current_position.exit_date = exit_date
        self.current_position.exit_price = exit_price
        self.current_position.exit_signal = {'reason': reason}
        
        # Update capital
        self.current_capital += (self.current_position.quantity * exit_price) - commission
        
        # Add to trades list
        self.trades.append(self.current_position)
        
        self.current_position = None
    
    def _calculate_position_size(self, signal: Dict[str, Any], entry_price: float) -> int:
        """Calculate position size"""
        risk_amount = self.config.initial_capital * (self.config.risk_per_trade / 100)
        
        # Estimate stop loss distance (2% of price as default)
        stop_loss_distance = entry_price * 0.02
        
        position_value = risk_amount * 2.5  # Risk/reward of 2.5:1
        position_size = int(position_value / entry_price)
        
        return min(position_size, int(self.config.max_position_size))
    
    def _calculate_stop_loss(self, entry_price: float, data: pd.DataFrame) -> float:
        """Calculate stop loss price"""
        # ATR-based stop loss (2 ATR below entry)
        if 'atr' in data.columns:
            latest_atr = data['atr'].iloc[-1]
            return entry_price - (2 * latest_atr)
        else:
            return entry_price * 0.98  # 2% below entry
    
    def _calculate_take_profit(self, entry_price: float, data: pd.DataFrame) -> float:
        """Calculate take profit price"""
        # Risk/reward based take profit
        stop_loss = self._calculate_stop_loss(entry_price, data)
        risk = entry_price - stop_loss
        return entry_price + (risk * 2.5)  # 2.5:1 risk/reward
    
    def _calculate_results(self, data: pd.DataFrame, benchmark_data: Optional[pd.DataFrame] = None) -> BacktestResult:
        """Calculate comprehensive backtest results"""
        if not self.trades:
            raise ValueError("No trades executed")
        
        # Calculate returns
        total_return = (self.current_capital - self.config.initial_capital) / self.config.initial_capital * 100
        
        # Annualized return (assuming daily data)
        days = (data.index[-1] - data.index[0]).days
        annualized_return = ((self.current_capital / self.config.initial_capital) ** (365 / days) - 1) * 100
        
        # Calculate equity curve
        equity_curve = self._calculate_equity_curve(data)
        
        # Calculate drawdown
        drawdown_series = self._calculate_drawdown(equity_curve)
        max_drawdown = drawdown_series.min()
        
        # Calculate risk metrics
        returns = equity_curve.pct_change().dropna()
        sharpe_ratio = self._calculate_sharpe_ratio(returns)
        sortino_ratio = self._calculate_sortino_ratio(returns)
        
        # Calculate trade statistics
        winning_trades = [t for t in self.trades if t.calculate_pnl() > 0]
        losing_trades = [t for t in self.trades if t.calculate_pnl() <= 0]
        
        win_rate = len(winning_trades) / len(self.trades) * 100
        
        avg_win = np.mean([t.calculate_pnl() for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([abs(t.calculate_pnl()) for t in losing_trades]) if losing_trades else 0
        profit_factor = avg_win / avg_loss if avg_loss > 0 else float('inf')
        
        avg_trade_return = np.mean([t.calculate_pnl_percent() for t in self.trades])
        avg_trade_duration = np.mean([t.calculate_duration() for t in self.trades])
        
        # Calculate VaR
        var_95 = np.percentile(returns, 5) * self.config.initial_capital
        
        # Calculate Calmar ratio
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Calculate beta and alpha (if benchmark provided)
        beta, alpha = 0, 0
        if benchmark_data is not None:
            beta, alpha = self._calculate_beta_alpha(returns, benchmark_data)
        
        # Calculate monthly returns
        monthly_returns = equity_curve.resample('M').last().pct_change().dropna() * 100
        
        return BacktestResult(
            total_return=total_return,
            annualized_return=annualized_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=len(self.trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            avg_trade_return=avg_trade_return,
            avg_trade_duration=avg_trade_duration,
            var_95=var_95,
            calmar_ratio=calmar_ratio,
            beta=beta,
            alpha=alpha,
            trades=self.trades,
            equity_curve=equity_curve,
            benchmark_returns=benchmark_data if benchmark_data else pd.Series(),
            monthly_returns=monthly_returns,
            drawdown_series=drawdown_series
        )
    
    def _calculate_equity_curve(self, data: pd.DataFrame) -> pd.Series:
        """Calculate equity curve throughout backtest"""
        equity = [self.config.initial_capital]
        current_equity = self.config.initial_capital
        
        for i in range(1, len(data)):
            # Check if any trade closed on this day
            for trade in self.trades:
                if trade.exit_date == data.index[i]:
                    current_equity += trade.calculate_pnl()
            
            # Update open position value
            if self.current_position is not None:
                position_value = self.current_position.quantity * data.iloc[i]['close']
                current_equity = self.config.initial_capital - sum([t.quantity * t.entry_price for t in self.trades]) + position_value
            
            equity.append(current_equity)
        
        return pd.Series(equity, index=data.index)
    
    def _calculate_drawdown(self, equity_curve: pd.Series) -> pd.Series:
        """Calculate drawdown series"""
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak * 100
        return drawdown
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.06) -> float:
        """Calculate Sharpe ratio"""
        excess_returns = returns - risk_free_rate / 252
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std() if excess_returns.std() != 0 else 0
    
    def _calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float = 0.06) -> float:
        """Calculate Sortino ratio"""
        excess_returns = returns - risk_free_rate / 252
        downside_returns = excess_returns[excess_returns < 0]
        return np.sqrt(252) * excess_returns.mean() / downside_returns.std() if len(downside_returns) > 0 and downside_returns.std() != 0 else 0
    
    def _calculate_beta_alpha(self, returns: pd.Series, benchmark_returns: pd.Series) -> Tuple[float, float]:
        """Calculate beta and alpha against benchmark"""
        if len(returns) != len(benchmark_returns):
            returns = returns[:len(benchmark_returns)]
        
        # Align the series
        aligned_returns = returns.align(benchmark_returns, join='inner')
        strategy_returns = aligned_returns[0]
        benchmark_aligned = aligned_returns[1]
        
        # Calculate beta
        covariance = np.cov(strategy_returns, benchmark_aligned)[0, 1]
        benchmark_variance = np.var(benchmark_aligned)
        beta = covariance / benchmark_variance if benchmark_variance != 0 else 0
        
        # Calculate alpha
        alpha = (strategy_returns.mean() - 0.06/252) - beta * (benchmark_aligned.mean() - 0.06/252)
        alpha *= 252  # Annualized alpha
        
        return beta, alpha


class WalkForwardOptimizer:
    """Walk-forward optimization engine"""
    
    def __init__(self, config: BacktestConfig):
        self.config = config
    
    async def optimize_strategy(self, strategy_class: type, parameter_grid: Dict[str, List], data: pd.DataFrame, 
                               in_sample_periods: int = 12, out_sample_periods: int = 3) -> Dict[str, Any]:
        """Perform walk-forward optimization"""
        logger.info("Starting walk-forward optimization")
        
        # Split data into walk-forward windows
        windows = self._create_walk_forward_windows(data, in_sample_periods, out_sample_periods)
        
        optimization_results = []
        
        for i, (train_data, test_data) in enumerate(windows):
            logger.info(f"Optimizing window {i+1}/{len(windows)}")
            
            # Optimize parameters on training data
            best_params = await self._optimize_parameters(strategy_class, parameter_grid, train_data)
            
            # Test on out-of-sample data
            strategy = strategy_class({**strategy_class.__init__.__self__.__dict__, **best_params})
            engine = BacktestEngine(self.config)
            
            result = await engine.run_backtest(strategy, test_data)
            
            optimization_results.append({
                'window': i+1,
                'train_period': (train_data.index[0], train_data.index[-1]),
                'test_period': (test_data.index[0], test_data.index[-1]),
                'best_parameters': best_params,
                'test_result': asdict(result)
            })
        
        # Aggregate results
        return self._aggregate_walk_forward_results(optimization_results)
    
    def _create_walk_forward_windows(self, data: pd.DataFrame, in_sample_periods: int, out_sample_periods: int) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
        """Create walk-forward windows"""
        windows = []
        total_periods = in_sample_periods + out_sample_periods
        
        # Assuming daily data, create monthly windows
        data_sorted = data.sort_index()
        
        start_idx = 0
        while start_idx + total_periods < len(data_sorted):
            train_start = start_idx
            train_end = start_idx + in_sample_periods * 20  # Approximate trading days per month
            test_start = train_end
            test_end = test_start + out_sample_periods * 20
            
            if test_end < len(data_sorted):
                train_data = data_sorted.iloc[train_start:train_end]
                test_data = data_sorted.iloc[test_start:test_end]
                windows.append((train_data, test_data))
            
            start_idx = test_start
        
        return windows
    
    async def _optimize_parameters(self, strategy_class: type, parameter_grid: Dict[str, List], train_data: pd.DataFrame) -> Dict[str, Any]:
        """Optimize strategy parameters on training data"""
        best_score = -float('inf')
        best_params = {}
        
        # Generate all parameter combinations
        param_combinations = self._generate_parameter_combinations(parameter_grid)
        
        for params in param_combinations:
            # Create strategy with parameters
            strategy = strategy_class(params)
            engine = BacktestEngine(self.config)
            
            try:
                result = await engine.run_backtest(strategy, train_data)
                
                # Score based on Sharpe ratio and total return
                score = result.sharpe_ratio + (result.total_return / 100)
                
                if score > best_score:
                    best_score = score
                    best_params = params
                    
            except Exception as e:
                logger.warning(f"Parameter optimization failed for {params}: {e}")
                continue
        
        return best_params
    
    def _generate_parameter_combinations(self, parameter_grid: Dict[str, List]) -> List[Dict[str, Any]]:
        """Generate all parameter combinations from grid"""
        import itertools
        
        keys = list(parameter_grid.keys())
        values = list(parameter_grid.values())
        
        combinations = []
        for combination in itertools.product(*values):
            combinations.append(dict(zip(keys, combination)))
        
        return combinations
    
    def _aggregate_walk_forward_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate walk-forward optimization results"""
        if not results:
            return {}
        
        # Calculate average metrics across all windows
        total_return = np.mean([r['test_result']['total_return'] for r in results])
        sharpe_ratio = np.mean([r['test_result']['sharpe_ratio'] for r in results])
        max_drawdown = np.mean([r['test_result']['max_drawdown'] for r in results])
        win_rate = np.mean([r['test_result']['win_rate'] for r in results])
        
        # Parameter stability analysis
        param_stability = self._analyze_parameter_stability(results)
        
        return {
            'walk_forward_return': total_return,
            'walk_forward_sharpe': sharpe_ratio,
            'walk_forward_max_drawdown': max_drawdown,
            'walk_forward_win_rate': win_rate,
            'parameter_stability': param_stability,
            'detailed_results': results
        }
    
    def _analyze_parameter_stability(self, results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze stability of optimized parameters"""
        if not results:
            return {}
        
        # Get all parameter names
        param_names = list(results[0]['best_parameters'].keys())
        stability = {}
        
        for param in param_names:
            values = [r['best_parameters'].get(param) for r in results]
            # Calculate coefficient of variation
            if len(set(values)) > 1:
                cv = np.std(values) / np.mean(values) if np.mean(values) != 0 else float('inf')
                stability[param] = 1 / (1 + cv)  # Higher stability for lower CV
            else:
                stability[param] = 1.0  # Perfect stability
        
        return stability


class MonteCarloSimulator:
    """Monte Carlo simulation for strategy robustness"""
    
    def __init__(self, config: BacktestConfig):
        self.config = config
    
    async def run_simulation(self, backtest_result: BacktestResult, num_simulations: int = 1000) -> Dict[str, Any]:
        """Run Monte Carlo simulation on backtest results"""
        logger.info(f"Running Monte Carlo simulation with {num_simulations} iterations")
        
        # Extract trade returns
        trade_returns = [t.calculate_pnl_percent() for t in backtest_result.trades]
        
        if not trade_returns:
            return {}
        
        # Run simulations
        simulation_results = []
        
        for i in range(num_simulations):
            # Resample trades with replacement
            sampled_returns = np.random.choice(trade_returns, size=len(trade_returns), replace=True)
            
            # Calculate portfolio metrics
            total_return = np.sum(sampled_returns)
            win_rate = len([r for r in sampled_returns if r > 0]) / len(sampled_returns) * 100
            
            simulation_results.append({
                'total_return': total_return,
                'win_rate': win_rate
            })
        
        # Calculate statistics
        returns_dist = [r['total_return'] for r in simulation_results]
        win_rates = [r['win_rate'] for r in simulation_results]
        
        return {
            'num_simulations': num_simulations,
            'return_statistics': {
                'mean': np.mean(returns_dist),
                'std': np.std(returns_dist),
                'min': np.min(returns_dist),
                'max': np.max(returns_dist),
                'percentile_5': np.percentile(returns_dist, 5),
                'percentile_95': np.percentile(returns_dist, 95)
            },
            'win_rate_statistics': {
                'mean': np.mean(win_rates),
                'std': np.std(win_rates),
                'min': np.min(win_rates),
                'max': np.max(win_rates),
                'percentile_5': np.percentile(win_rates, 5),
                'percentile_95': np.percentile(win_rates, 95)
            },
            'probability_of_profit': len([r for r in returns_dist if r > 0]) / len(returns_dist) * 100,
            'simulation_results': simulation_results
        }


# Example usage and testing functions
async def run_example_backtest():
    """Run example backtest"""
    # Configuration
    config = BacktestConfig(
        initial_capital=1000000,
        commission_per_trade=20,
        slippage_percent=0.1,
        position_sizing_method='kelly',
        position_size_percent=2.0,
        max_position_size=100000,
        risk_per_trade=2.0,
        benchmark_symbol='NIFTY'
    )
    
    # Generate sample data
    dates = pd.date_range(start='2022-01-01', end='2024-01-01', freq='D')
    np.random.seed(42)
    
    # Simulate price data with some trends
    price_data = []
    price = 1000
    
    for i in range(len(dates)):
        change = np.random.normal(0.001, 0.02)  # Daily returns
        price *= (1 + change)
        
        high = price * (1 + abs(np.random.normal(0, 0.01)))
        low = price * (1 - abs(np.random.normal(0, 0.01)))
        volume = int(np.random.normal(1000000, 300000))
        
        price_data.append({
            'open': price,
            'high': high,
            'low': low,
            'close': price,
            'volume': max(volume, 100000)
        })
    
    data = pd.DataFrame(price_data, index=dates)
    
    # Strategy configuration
    strategy_config = {
        'name': 'SMC FVG Strategy',
        'fvg_strength': 'medium',
        'volume_multiplier': 1.5,
        'structure_alignment': True,
        'risk_reward_ratio': 2.5,
        'position_sizing_method': 'kelly',
        'position_size_percent': 2.0
    }
    
    # Create strategy and run backtest
    strategy = SMCFVGStrategy(strategy_config)
    engine = BacktestEngine(config)
    
    result = await engine.run_backtest(strategy, data)
    
    # Print results
    print("Backtest Results:")
    print(f"Total Return: {result.total_return:.2f}%")
    print(f"Annualized Return: {result.annualized_return:.2f}%")
    print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
    print(f"Max Drawdown: {result.max_drawdown:.2f}%")
    print(f"Win Rate: {result.win_rate:.2f}%")
    print(f"Total Trades: {result.total_trades}")
    print(f"Profit Factor: {result.profit_factor:.2f}")
    
    # Run Monte Carlo simulation
    simulator = MonteCarloSimulator(config)
    mc_results = await simulator.run_simulation(result, num_simulations=1000)
    
    print("\nMonte Carlo Results:")
    print(f"Probability of Profit: {mc_results['probability_of_profit']:.2f}%")
    print(f"Return 5th Percentile: {mc_results['return_statistics']['percentile_5']:.2f}%")
    print(f"Return 95th Percentile: {mc_results['return_statistics']['percentile_95']:.2f}%")
    
    return result, mc_results


if __name__ == "__main__":
    # Run example backtest
    asyncio.run(run_example_backtest())
