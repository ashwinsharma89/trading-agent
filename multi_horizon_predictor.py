"""
Multi-Horizon Price Target Predictor
Predicts price targets for 6 months, 1 year, 2 years, 3 years, and 5 years
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import yfinance as yf
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class MultiHorizonPredictor:
    """
    Predict price targets across multiple time horizons
    """
    
    def __init__(self):
        self.horizons = {
            '6M': {'days': 180, 'label': '6 Months'},
            '1Y': {'days': 365, 'label': '1 Year'},
            '2Y': {'days': 730, 'label': '2 Years'},
            '3Y': {'days': 1095, 'label': '3 Years'},
            '5Y': {'days': 1825, 'label': '5 Years'}
        }
    
    def predict_all_horizons(self, ticker: str, current_price: float = None) -> Dict:
        """
        Predict targets for all time horizons
        """
        # Fetch historical data
        stock = yf.Ticker(f"{ticker}.NS")
        hist = stock.history(period="5y")
        
        if hist.empty:
            raise ValueError(f"No data available for {ticker}")
        
        if current_price is None:
            current_price = hist['Close'].iloc[-1]
        
        # Get fundamental data
        info = stock.info
        
        results = {
            'ticker': ticker,
            'current_price': current_price,
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'horizons': {},
            'summary': {}
        }
        
        # Predict for each horizon
        for horizon_key, horizon_info in self.horizons.items():
            prediction = self._predict_horizon(
                ticker, hist, info, current_price, 
                horizon_info['days'], horizon_info['label']
            )
            results['horizons'][horizon_key] = prediction
        
        # Generate summary
        results['summary'] = self._generate_summary(results['horizons'])
        
        return results
    
    def _predict_horizon(self, ticker: str, hist: pd.DataFrame, info: Dict,
                        current_price: float, days: int, label: str) -> Dict:
        """
        Predict target for a specific horizon using multiple methods
        """
        prediction = {
            'horizon': label,
            'days': days,
            'methods': {},
            'consensus': {}
        }
        
        # Method 1: Historical Growth Rate
        historical = self._historical_growth_method(hist, current_price, days)
        prediction['methods']['historical_growth'] = historical
        
        # Method 2: Fundamental Valuation
        fundamental = self._fundamental_valuation_method(info, current_price, days)
        prediction['methods']['fundamental'] = fundamental
        
        # Method 3: Technical Projection
        technical = self._technical_projection_method(hist, current_price, days)
        prediction['methods']['technical'] = technical
        
        # Method 4: Regression Analysis
        regression = self._regression_method(hist, current_price, days)
        prediction['methods']['regression'] = regression
        
        # Method 5: Monte Carlo Simulation
        monte_carlo = self._monte_carlo_method(hist, current_price, days)
        prediction['methods']['monte_carlo'] = monte_carlo
        
        # Build consensus
        prediction['consensus'] = self._build_consensus(prediction['methods'], current_price)
        
        return prediction
    
    def _historical_growth_method(self, hist: pd.DataFrame, current_price: float, days: int) -> Dict:
        """
        Project based on historical growth rate
        """
        # Calculate CAGR from available data
        years_of_data = len(hist) / 252  # Trading days per year
        
        if years_of_data < 1:
            return {'target': None, 'confidence': 0, 'note': 'Insufficient data'}
        
        start_price = hist['Close'].iloc[0]
        end_price = hist['Close'].iloc[-1]
        
        # CAGR = (End/Start)^(1/years) - 1
        cagr = (end_price / start_price) ** (1 / years_of_data) - 1
        
        # Project forward
        years_forward = days / 365
        target = current_price * ((1 + cagr) ** years_forward)
        
        # Calculate confidence based on consistency
        returns = hist['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)  # Annualized
        confidence = max(0, min(100, 100 - (volatility * 100)))
        
        return {
            'target': float(target),
            'cagr': float(cagr * 100),
            'confidence': float(confidence),
            'upside': float((target - current_price) / current_price * 100)
        }
    
    def _fundamental_valuation_method(self, info: Dict, current_price: float, days: int) -> Dict:
        """
        Project based on fundamental growth expectations
        """
        try:
            # Get growth metrics
            revenue_growth = info.get('revenueGrowth', 0) or 0
            earnings_growth = info.get('earningsGrowth', 0) or 0
            
            # Average growth rate
            avg_growth = (revenue_growth + earnings_growth) / 2
            
            # Adjust for time horizon (growth typically slows over time)
            years = days / 365
            if years <= 1:
                adjusted_growth = avg_growth
            elif years <= 2:
                adjusted_growth = avg_growth * 0.9
            elif years <= 3:
                adjusted_growth = avg_growth * 0.8
            else:
                adjusted_growth = avg_growth * 0.7
            
            # Project target
            target = current_price * ((1 + adjusted_growth) ** years)
            
            # Confidence based on profitability
            roe = info.get('returnOnEquity', 0) or 0
            profit_margin = info.get('profitMargins', 0) or 0
            confidence = min(100, (roe * 100 + profit_margin * 100) / 2)
            
            return {
                'target': float(target),
                'growth_rate': float(adjusted_growth * 100),
                'confidence': float(confidence),
                'upside': float((target - current_price) / current_price * 100)
            }
        except Exception as e:
            return {'target': None, 'confidence': 0, 'note': str(e)}
    
    def _technical_projection_method(self, hist: pd.DataFrame, current_price: float, days: int) -> Dict:
        """
        Project based on technical analysis
        """
        # Calculate support and resistance levels
        highs = hist['High'].rolling(window=20).max()
        lows = hist['Low'].rolling(window=20).min()
        
        # Calculate average range expansion
        ranges = highs - lows
        avg_range = ranges.mean()
        
        # Project based on trend
        prices = hist['Close'].values
        
        # Linear trend
        x = np.arange(len(prices))
        slope, intercept, r_value, _, _ = stats.linregress(x, prices)
        
        # Project forward
        future_x = len(prices) + days
        target = slope * future_x + intercept
        
        # Adjust for volatility
        volatility = hist['Close'].pct_change().std()
        confidence = max(0, min(100, abs(r_value) * 100))
        
        return {
            'target': float(max(0, target)),
            'trend_strength': float(r_value),
            'confidence': float(confidence),
            'upside': float((target - current_price) / current_price * 100)
        }
    
    def _regression_method(self, hist: pd.DataFrame, current_price: float, days: int) -> Dict:
        """
        Polynomial regression projection
        """
        prices = hist['Close'].values
        x = np.arange(len(prices))
        
        # Fit polynomial (degree 2)
        coeffs = np.polyfit(x, prices, 2)
        poly = np.poly1d(coeffs)
        
        # Project forward
        future_x = len(prices) + days
        target = poly(future_x)
        
        # Calculate R-squared
        fitted = poly(x)
        ss_res = np.sum((prices - fitted) ** 2)
        ss_tot = np.sum((prices - np.mean(prices)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        
        confidence = max(0, min(100, r_squared * 100))
        
        return {
            'target': float(max(0, target)),
            'r_squared': float(r_squared),
            'confidence': float(confidence),
            'upside': float((target - current_price) / current_price * 100)
        }
    
    def _monte_carlo_method(self, hist: pd.DataFrame, current_price: float, days: int) -> Dict:
        """
        Monte Carlo simulation
        """
        returns = hist['Close'].pct_change().dropna()
        
        # Calculate statistics
        mean_return = returns.mean()
        std_return = returns.std()
        
        # Run simulations
        num_simulations = 1000
        final_prices = []
        
        for _ in range(num_simulations):
            price = current_price
            for _ in range(days):
                daily_return = np.random.normal(mean_return, std_return)
                price *= (1 + daily_return)
            final_prices.append(price)
        
        # Calculate statistics
        final_prices = np.array(final_prices)
        target = np.median(final_prices)
        confidence_interval = np.percentile(final_prices, [25, 75])
        
        # Confidence based on distribution width
        spread = (confidence_interval[1] - confidence_interval[0]) / target
        confidence = max(0, min(100, 100 - (spread * 100)))
        
        return {
            'target': float(target),
            'median': float(target),
            'lower_bound': float(confidence_interval[0]),
            'upper_bound': float(confidence_interval[1]),
            'confidence': float(confidence),
            'upside': float((target - current_price) / current_price * 100)
        }
    
    def _build_consensus(self, methods: Dict, current_price: float) -> Dict:
        """
        Build consensus from all methods with improved confidence calculation
        """
        targets = []
        confidences = []
        
        for method_name, method_data in methods.items():
            if method_data.get('target') and method_data['target'] > 0:
                targets.append(method_data['target'])
                confidences.append(method_data.get('confidence', 50))
        
        if not targets:
            return {'target': None, 'confidence': 0}
        
        # Weighted average by confidence
        weights = np.array(confidences) / sum(confidences)
        consensus_target = np.average(targets, weights=weights)
        
        # Calculate range
        min_target = min(targets)
        max_target = max(targets)
        
        # IMPROVED CONFIDENCE CALCULATION
        # Factor 1: Average method confidence (40% weight)
        avg_confidence = np.mean(confidences)
        
        # Factor 2: Agreement between methods (40% weight)
        # Lower variance = higher agreement = higher confidence
        target_std = np.std(targets)
        target_mean = np.mean(targets)
        coefficient_of_variation = target_std / target_mean if target_mean > 0 else 1
        agreement_score = max(0, 100 - (coefficient_of_variation * 100))
        
        # Factor 3: Number of methods agreeing (20% weight)
        method_score = (len(targets) / 5) * 100  # Max 5 methods
        
        # Combined confidence
        consensus_confidence = (
            avg_confidence * 0.4 + 
            agreement_score * 0.4 + 
            method_score * 0.2
        )
        
        # Ensure reasonable bounds
        consensus_confidence = max(30, min(95, consensus_confidence))
        
        return {
            'target': float(consensus_target),
            'min_target': float(min_target),
            'max_target': float(max_target),
            'confidence': float(consensus_confidence),
            'upside': float((consensus_target - current_price) / current_price * 100),
            'num_methods': len(targets),
            'agreement_score': float(agreement_score),
            'method_confidence': float(avg_confidence)
        }
    
    def _generate_summary(self, horizons: Dict) -> Dict:
        """
        Generate overall summary
        """
        summary = {
            'investment_outlook': None,
            'best_horizon': None,
            'expected_cagr': None,
            'risk_level': None
        }
        
        # Calculate expected CAGR
        if '5Y' in horizons and horizons['5Y']['consensus']['target']:
            five_year_target = horizons['5Y']['consensus']['target']
            current = horizons['5Y']['consensus'].get('current_price', 100)
            cagr = ((five_year_target / current) ** (1/5) - 1) * 100
            summary['expected_cagr'] = float(cagr)
        
        # Determine best horizon (highest risk-adjusted return)
        best_score = 0
        for horizon_key, horizon_data in horizons.items():
            consensus = horizon_data['consensus']
            if consensus['target']:
                # Risk-adjusted score
                score = consensus['upside'] * (consensus['confidence'] / 100)
                if score > best_score:
                    best_score = score
                    summary['best_horizon'] = horizon_data['horizon']
        
        # Determine outlook
        if summary['expected_cagr']:
            if summary['expected_cagr'] > 20:
                summary['investment_outlook'] = 'VERY BULLISH'
                summary['risk_level'] = 'HIGH'
            elif summary['expected_cagr'] > 15:
                summary['investment_outlook'] = 'BULLISH'
                summary['risk_level'] = 'MEDIUM-HIGH'
            elif summary['expected_cagr'] > 10:
                summary['investment_outlook'] = 'MODERATELY BULLISH'
                summary['risk_level'] = 'MEDIUM'
            elif summary['expected_cagr'] > 5:
                summary['investment_outlook'] = 'NEUTRAL'
                summary['risk_level'] = 'MEDIUM-LOW'
            else:
                summary['investment_outlook'] = 'BEARISH'
                summary['risk_level'] = 'LOW'
        
        return summary
    
    def print_report(self, results: Dict):
        """
        Print formatted report
        """
        print("\n" + "="*70)
        print(f"📊 MULTI-HORIZON PRICE TARGET ANALYSIS: {results['ticker']}")
        print("="*70)
        
        print(f"\n💰 Current Price: ₹{results['current_price']:.2f}")
        print(f"📅 Analysis Date: {results['analysis_date']}")
        
        print("\n" + "="*70)
        print("🎯 PRICE TARGETS BY HORIZON")
        print("="*70)
        
        for horizon_key in ['6M', '1Y', '2Y', '3Y', '5Y']:
            if horizon_key in results['horizons']:
                horizon = results['horizons'][horizon_key]
                consensus = horizon['consensus']
                
                if consensus['target']:
                    print(f"\n📈 {horizon['horizon']}:")
                    print(f"   Target: ₹{consensus['target']:.2f}")
                    print(f"   Range: ₹{consensus['min_target']:.2f} - ₹{consensus['max_target']:.2f}")
                    print(f"   Upside: {consensus['upside']:.1f}%")
                    print(f"   Confidence: {consensus['confidence']:.0f}% (Methods: {consensus['method_confidence']:.0f}%, Agreement: {consensus['agreement_score']:.0f}%)")
        
        print("\n" + "="*70)
        print("📊 SUMMARY")
        print("="*70)
        
        summary = results['summary']
        print(f"\n🎯 Investment Outlook: {summary['investment_outlook']}")
        print(f"⚡ Expected CAGR (5Y): {summary['expected_cagr']:.1f}%")
        print(f"🎲 Risk Level: {summary['risk_level']}")
        print(f"⭐ Best Horizon: {summary['best_horizon']}")


if __name__ == "__main__":
    import sys
    
    ticker = sys.argv[1] if len(sys.argv) > 1 else "KPIGREEN"
    
    print(f"\n🔮 Predicting multi-horizon targets for {ticker}...")
    
    predictor = MultiHorizonPredictor()
    results = predictor.predict_all_horizons(ticker)
    predictor.print_report(results)
    
    print("\n" + "="*70)
    print("✅ Analysis Complete!")
    print("="*70)
