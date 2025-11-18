"""
Real Fundamental Analysis using Yahoo Finance
Fetches actual company fundamentals
"""

import yfinance as yf
from typing import Dict, Optional
import pandas as pd


class FundamentalAnalyzer:
    """
    Fetch and analyze real fundamental data
    """
    
    def __init__(self):
        self.cache = {}
    
    def analyze(self, symbol: str, exchange: str = "NSE") -> Dict:
        """
        Get comprehensive fundamental analysis
        
        Args:
            symbol: Stock symbol
            exchange: Exchange (NSE/BSE)
        
        Returns:
            Dictionary with fundamental metrics
        """
        # Convert to Yahoo Finance format
        yf_symbol = f"{symbol}.NS" if exchange == "NSE" else f"{symbol}.BO"
        
        try:
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            
            # Extract key metrics
            fundamentals = {
                'symbol': symbol,
                'company_name': info.get('longName', symbol),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                
                # Valuation metrics
                'market_cap': info.get('marketCap', 0),
                'enterprise_value': info.get('enterpriseValue', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'pb_ratio': info.get('priceToBook', 0),
                'ps_ratio': info.get('priceToSalesTrailing12Months', 0),
                'peg_ratio': info.get('pegRatio', 0),
                
                # Profitability metrics
                'profit_margin': info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0,
                'operating_margin': info.get('operatingMargins', 0) * 100 if info.get('operatingMargins') else 0,
                'roe': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0,
                'roa': info.get('returnOnAssets', 0) * 100 if info.get('returnOnAssets') else 0,
                
                # Growth metrics
                'revenue_growth': info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else 0,
                'earnings_growth': info.get('earningsGrowth', 0) * 100 if info.get('earningsGrowth') else 0,
                'earnings_quarterly_growth': info.get('earningsQuarterlyGrowth', 0) * 100 if info.get('earningsQuarterlyGrowth') else 0,
                
                # Financial health
                'debt_to_equity': info.get('debtToEquity', 0),
                'current_ratio': info.get('currentRatio', 0),
                'quick_ratio': info.get('quickRatio', 0),
                'free_cashflow': info.get('freeCashflow', 0),
                
                # Dividend metrics
                'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                'payout_ratio': info.get('payoutRatio', 0) * 100 if info.get('payoutRatio') else 0,
                
                # Trading metrics
                'beta': info.get('beta', 0),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
                
                # Analyst recommendations
                'target_mean_price': info.get('targetMeanPrice', 0),
                'target_high_price': info.get('targetHighPrice', 0),
                'target_low_price': info.get('targetLowPrice', 0),
                'recommendation': info.get('recommendationKey', 'none'),
                'number_of_analyst_opinions': info.get('numberOfAnalystOpinions', 0),
                
                # Additional info
                'book_value': info.get('bookValue', 0),
                'price_to_book': info.get('priceToBook', 0),
                'shares_outstanding': info.get('sharesOutstanding', 0),
                'float_shares': info.get('floatShares', 0),
                'shares_short': info.get('sharesShort', 0),
            }
            
            # Calculate quality scores
            quality_scores = self._calculate_quality_scores(fundamentals)
            fundamentals['quality_scores'] = quality_scores
            fundamentals['overall_quality'] = sum(quality_scores.values()) / len(quality_scores)
            
            # Investment rating
            fundamentals['investment_rating'] = self._determine_investment_rating(fundamentals)
            
            return fundamentals
            
        except Exception as e:
            print(f"Error fetching fundamentals for {symbol}: {e}")
            return self._get_default_fundamentals(symbol)
    
    def _calculate_quality_scores(self, fundamentals: Dict) -> Dict[str, float]:
        """
        Calculate quality scores for different aspects
        """
        scores = {}
        
        # Profitability Score (0-100)
        profit_score = 0
        if fundamentals['roe'] > 20:
            profit_score += 40
        elif fundamentals['roe'] > 15:
            profit_score += 30
        elif fundamentals['roe'] > 10:
            profit_score += 20
        
        if fundamentals['profit_margin'] > 15:
            profit_score += 30
        elif fundamentals['profit_margin'] > 10:
            profit_score += 20
        elif fundamentals['profit_margin'] > 5:
            profit_score += 10
        
        if fundamentals['operating_margin'] > 15:
            profit_score += 30
        elif fundamentals['operating_margin'] > 10:
            profit_score += 20
        
        scores['Profitability'] = min(100, profit_score)
        
        # Growth Score (0-100)
        growth_score = 0
        if fundamentals['revenue_growth'] > 20:
            growth_score += 50
        elif fundamentals['revenue_growth'] > 10:
            growth_score += 35
        elif fundamentals['revenue_growth'] > 5:
            growth_score += 20
        
        if fundamentals['earnings_growth'] > 20:
            growth_score += 50
        elif fundamentals['earnings_growth'] > 10:
            growth_score += 35
        elif fundamentals['earnings_growth'] > 5:
            growth_score += 20
        
        scores['Growth'] = min(100, growth_score)
        
        # Leverage Score (0-100) - Lower debt is better
        leverage_score = 100
        if fundamentals['debt_to_equity'] > 2:
            leverage_score = 40
        elif fundamentals['debt_to_equity'] > 1:
            leverage_score = 60
        elif fundamentals['debt_to_equity'] > 0.5:
            leverage_score = 80
        
        scores['Leverage'] = leverage_score
        
        # Valuation Score (0-100) - Lower P/E is better
        valuation_score = 50  # Neutral
        if fundamentals['pe_ratio'] > 0:
            if fundamentals['pe_ratio'] < 15:
                valuation_score = 90
            elif fundamentals['pe_ratio'] < 25:
                valuation_score = 70
            elif fundamentals['pe_ratio'] < 35:
                valuation_score = 50
            else:
                valuation_score = 30
        
        scores['Valuation'] = valuation_score
        
        # Dividend Score (0-100)
        dividend_score = 0
        if fundamentals['dividend_yield'] > 3:
            dividend_score = 90
        elif fundamentals['dividend_yield'] > 2:
            dividend_score = 70
        elif fundamentals['dividend_yield'] > 1:
            dividend_score = 50
        elif fundamentals['dividend_yield'] > 0:
            dividend_score = 30
        
        scores['Dividend'] = dividend_score
        
        return scores
    
    def _determine_investment_rating(self, fundamentals: Dict) -> str:
        """
        Determine overall investment rating
        """
        quality = fundamentals['overall_quality']
        
        if quality >= 80:
            return "Strong Buy 🟢"
        elif quality >= 70:
            return "Buy 🟢"
        elif quality >= 60:
            return "Hold ⚪"
        elif quality >= 50:
            return "Weak Hold ⚪"
        else:
            return "Sell 🔴"
    
    def _get_default_fundamentals(self, symbol: str) -> Dict:
        """
        Return default structure when data unavailable
        """
        return {
            'symbol': symbol,
            'company_name': symbol,
            'sector': 'N/A',
            'industry': 'N/A',
            'market_cap': 0,
            'pe_ratio': 0,
            'pb_ratio': 0,
            'roe': 0,
            'debt_to_equity': 0,
            'dividend_yield': 0,
            'quality_scores': {
                'Profitability': 0,
                'Growth': 0,
                'Leverage': 0,
                'Valuation': 0,
                'Dividend': 0
            },
            'overall_quality': 0,
            'investment_rating': 'No Data Available',
            'error': True
        }
    
    def format_market_cap(self, market_cap: float) -> str:
        """Format market cap in Indian format"""
        if market_cap >= 1e12:
            return f"₹{market_cap/1e12:.2f}L Cr"
        elif market_cap >= 1e10:
            return f"₹{market_cap/1e10:.2f}K Cr"
        elif market_cap >= 1e7:
            return f"₹{market_cap/1e7:.2f} Cr"
        else:
            return f"₹{market_cap:.2f}"
    
    def format_large_number(self, number: float) -> str:
        """Format large numbers"""
        if number >= 1e9:
            return f"₹{number/1e9:.2f}B"
        elif number >= 1e7:
            return f"₹{number/1e7:.2f}Cr"
        elif number >= 1e5:
            return f"₹{number/1e5:.2f}L"
        else:
            return f"₹{number:.2f}"


if __name__ == "__main__":
    # Test fundamental analyzer
    print("\n💰 Testing Fundamental Analyzer\n")
    
    analyzer = FundamentalAnalyzer()
    
    # Test with RELIANCE
    print("Analyzing RELIANCE...")
    fundamentals = analyzer.analyze("RELIANCE", "NSE")
    
    print(f"\nCompany: {fundamentals['company_name']}")
    print(f"Sector: {fundamentals['sector']}")
    print(f"Industry: {fundamentals['industry']}")
    print(f"\nMarket Cap: {analyzer.format_market_cap(fundamentals['market_cap'])}")
    print(f"P/E Ratio: {fundamentals['pe_ratio']:.2f}")
    print(f"P/B Ratio: {fundamentals['pb_ratio']:.2f}")
    print(f"ROE: {fundamentals['roe']:.2f}%")
    print(f"Debt/Equity: {fundamentals['debt_to_equity']:.2f}")
    print(f"Dividend Yield: {fundamentals['dividend_yield']:.2f}%")
    print(f"\nOverall Quality: {fundamentals['overall_quality']:.1f}/100")
    print(f"Investment Rating: {fundamentals['investment_rating']}")
    print(f"\nQuality Scores:")
    for metric, score in fundamentals['quality_scores'].items():
        print(f"  {metric}: {score:.1f}/100")
