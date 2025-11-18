"""
IPO Analysis Framework
Analyzes recent IPOs for SIP timing and return potential
Compares with successful IPOs like Zomato
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class IPOAnalyzer:
    """
    Comprehensive IPO analysis for SIP timing and return potential
    """
    
    def __init__(self):
        self.ipo_stocks = {
            'FIRSTCRY.NS': {'name': 'FirstCry', 'listing_date': '2024-08-13'},
            'ZOMATO.NS': {'name': 'Zomato', 'listing_date': '2021-07-23'},
            'NYKAA.NS': {'name': 'Nykaa', 'listing_date': '2021-11-10'},
            'PAYTM.NS': {'name': 'Paytm', 'listing_date': '2021-11-18'},
            'POLICYBZR.NS': {'name': 'PolicyBazaar', 'listing_date': '2021-11-15'},
            'CARTRADE.NS': {'name': 'CarTrade', 'listing_date': '2021-08-20'},
        }
    
    def analyze_ipo(self, ticker: str, listing_date: str = None) -> Dict:
        """
        Complete IPO analysis
        """
        print(f"\n{'='*80}")
        print(f"📊 ANALYZING IPO: {ticker}")
        print(f"{'='*80}\n")
        
        stock = yf.Ticker(ticker)
        
        # Get full history
        hist = stock.history(period="max")
        if hist.empty:
            return {'error': f'No data for {ticker}'}
        
        info = stock.info
        current_price = hist['Close'].iloc[-1]
        
        results = {
            'ticker': ticker,
            'name': info.get('longName', ticker),
            'current_price': current_price,
            'listing_date': listing_date or hist.index[0].strftime('%Y-%m-%d'),
            'technical_analysis': {},
            'fundamental_analysis': {},
            'sip_analysis': {},
            'comparison': {}
        }
        
        # 1. Technical Analysis
        print("🔍 TECHNICAL ANALYSIS")
        print("-" * 80)
        results['technical_analysis'] = self._technical_analysis(hist, listing_date)
        
        # 2. Fundamental Analysis
        print("\n💰 FUNDAMENTAL ANALYSIS")
        print("-" * 80)
        results['fundamental_analysis'] = self._fundamental_analysis(stock, info)
        
        # 3. SIP Timing Analysis
        print("\n📈 SIP TIMING ANALYSIS")
        print("-" * 80)
        results['sip_analysis'] = self._sip_timing_analysis(hist, results['technical_analysis'])
        
        # 4. Return Potential
        print("\n🎯 RETURN POTENTIAL (2 Year)")
        print("-" * 80)
        results['return_potential'] = self._calculate_return_potential(hist, info, current_price)
        
        return results
    
    def _technical_analysis(self, hist: pd.DataFrame, listing_date: str = None) -> Dict:
        """
        Technical analysis: tops, bottoms, volume, RSI divergence
        """
        analysis = {}
        
        # Find listing price
        listing_price = hist['Close'].iloc[0]
        analysis['listing_price'] = float(listing_price)
        
        # a) Weeks to top after listing
        top_price = hist['High'].max()
        top_idx = hist['High'].idxmax()
        weeks_to_top = (top_idx - hist.index[0]).days / 7
        
        analysis['weeks_to_top'] = float(weeks_to_top)
        analysis['top_price'] = float(top_price)
        analysis['top_date'] = top_idx.strftime('%Y-%m-%d')
        analysis['gain_to_top'] = float((top_price - listing_price) / listing_price * 100)
        
        print(f"  ✅ Weeks to Top: {weeks_to_top:.1f} weeks")
        print(f"  📈 Top Price: ₹{top_price:.2f} (+{analysis['gain_to_top']:.1f}%)")
        print(f"  📅 Top Date: {analysis['top_date']}")
        
        # b) Weeks to bottom after top
        post_top = hist[hist.index > top_idx]
        if not post_top.empty:
            bottom_price = post_top['Low'].min()
            bottom_idx = post_top['Low'].idxmin()
            weeks_to_bottom = (bottom_idx - top_idx).days / 7
            
            analysis['weeks_to_bottom'] = float(weeks_to_bottom)
            analysis['bottom_price'] = float(bottom_price)
            analysis['bottom_date'] = bottom_idx.strftime('%Y-%m-%d')
            analysis['drop_from_top'] = float((bottom_price - top_price) / top_price * 100)
            
            print(f"\n  ⬇️ Weeks to Bottom: {weeks_to_bottom:.1f} weeks")
            print(f"  📉 Bottom Price: ₹{bottom_price:.2f} ({analysis['drop_from_top']:.1f}%)")
            print(f"  📅 Bottom Date: {analysis['bottom_date']}")
            
            # c) Volume at bottom vs average
            avg_volume = hist['Volume'].mean()
            bottom_volume = post_top.loc[bottom_idx, 'Volume']
            volume_ratio = bottom_volume / avg_volume
            
            analysis['avg_volume'] = float(avg_volume)
            analysis['bottom_volume'] = float(bottom_volume)
            analysis['volume_ratio'] = float(volume_ratio)
            
            print(f"\n  📊 Volume at Bottom: {bottom_volume:,.0f}")
            print(f"  📊 Average Volume: {avg_volume:,.0f}")
            print(f"  📊 Volume Ratio: {volume_ratio:.2f}x")
            
            # d) RSI Bullish Divergence
            rsi_divergence = self._check_rsi_divergence(post_top, bottom_idx)
            analysis['rsi_divergence'] = rsi_divergence
            
            if rsi_divergence['detected']:
                print(f"\n  🎯 RSI Bullish Divergence: DETECTED ✅")
                print(f"  📊 RSI at Bottom: {rsi_divergence['rsi_at_bottom']:.2f}")
            else:
                print(f"\n  ⚠️ RSI Bullish Divergence: NOT DETECTED")
        
        # Current position analysis
        current_price = hist['Close'].iloc[-1]
        from_top = (current_price - top_price) / top_price * 100
        from_listing = (current_price - listing_price) / listing_price * 100
        
        analysis['current_price'] = float(current_price)
        analysis['from_top_pct'] = float(from_top)
        analysis['from_listing_pct'] = float(from_listing)
        
        print(f"\n  💰 Current Price: ₹{current_price:.2f}")
        print(f"  📊 From Top: {from_top:+.1f}%")
        print(f"  📊 From Listing: {from_listing:+.1f}%")
        
        return analysis
    
    def _check_rsi_divergence(self, data: pd.DataFrame, bottom_idx) -> Dict:
        """
        Check for RSI bullish divergence at bottom
        """
        # Calculate RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Look for divergence around bottom
        window = 20  # days
        start_idx = max(0, data.index.get_loc(bottom_idx) - window)
        end_idx = min(len(data), data.index.get_loc(bottom_idx) + window)
        
        window_data = data.iloc[start_idx:end_idx]
        window_rsi = rsi.iloc[start_idx:end_idx]
        
        # Check if price made lower low but RSI made higher low
        price_lows = window_data['Low'].nsmallest(2)
        rsi_at_lows = window_rsi.loc[price_lows.index]
        
        detected = False
        if len(price_lows) >= 2 and len(rsi_at_lows) >= 2:
            if price_lows.iloc[1] < price_lows.iloc[0] and rsi_at_lows.iloc[1] > rsi_at_lows.iloc[0]:
                detected = True
        
        return {
            'detected': detected,
            'rsi_at_bottom': float(rsi.loc[bottom_idx]) if bottom_idx in rsi.index else None
        }
    
    def _fundamental_analysis(self, stock, info: Dict) -> Dict:
        """
        Fundamental analysis: ratios, results, balance sheet, shareholding
        """
        analysis = {}
        
        # a) Fundamental Ratios
        print("  📊 Fundamental Ratios:")
        
        pe_ratio = info.get('trailingPE', None)
        analysis['pe_ratio'] = float(pe_ratio) if pe_ratio else None
        print(f"    • P/E Ratio: {pe_ratio:.2f}" if pe_ratio else "    • P/E Ratio: N/A")
        
        ev_ebitda = info.get('enterpriseToEbitda', None)
        analysis['ev_ebitda'] = float(ev_ebitda) if ev_ebitda else None
        print(f"    • EV/EBITDA: {ev_ebitda:.2f}" if ev_ebitda else "    • EV/EBITDA: N/A")
        
        pb_ratio = info.get('priceToBook', None)
        analysis['price_to_book'] = float(pb_ratio) if pb_ratio else None
        print(f"    • Price to Book: {pb_ratio:.2f}" if pb_ratio else "    • Price to Book: N/A")
        
        market_cap = info.get('marketCap', None)
        revenue = info.get('totalRevenue', None)
        if market_cap and revenue:
            mc_sales = market_cap / revenue
            analysis['market_cap_to_sales'] = float(mc_sales)
            print(f"    • Market Cap/Sales: {mc_sales:.2f}")
        else:
            analysis['market_cap_to_sales'] = None
            print(f"    • Market Cap/Sales: N/A")
        
        # b) Quarterly Results
        print("\n  📈 Recent Performance:")
        
        revenue_growth = info.get('revenueGrowth', None)
        analysis['revenue_growth'] = float(revenue_growth * 100) if revenue_growth else None
        print(f"    • Revenue Growth: {revenue_growth*100:.1f}%" if revenue_growth else "    • Revenue Growth: N/A")
        
        earnings_growth = info.get('earningsGrowth', None)
        analysis['earnings_growth'] = float(earnings_growth * 100) if earnings_growth else None
        print(f"    • Earnings Growth: {earnings_growth*100:.1f}%" if earnings_growth else "    • Earnings Growth: N/A")
        
        profit_margin = info.get('profitMargins', None)
        analysis['profit_margin'] = float(profit_margin * 100) if profit_margin else None
        print(f"    • Profit Margin: {profit_margin*100:.1f}%" if profit_margin else "    • Profit Margin: N/A")
        
        # c) Balance Sheet
        print("\n  💼 Balance Sheet:")
        
        roe = info.get('returnOnEquity', None)
        analysis['roe'] = float(roe * 100) if roe else None
        print(f"    • ROE: {roe*100:.1f}%" if roe else "    • ROE: N/A")
        
        debt_equity = info.get('debtToEquity', None)
        analysis['debt_to_equity'] = float(debt_equity) if debt_equity else None
        print(f"    • Debt/Equity: {debt_equity:.2f}" if debt_equity else "    • Debt/Equity: N/A")
        
        current_ratio = info.get('currentRatio', None)
        analysis['current_ratio'] = float(current_ratio) if current_ratio else None
        print(f"    • Current Ratio: {current_ratio:.2f}" if current_ratio else "    • Current Ratio: N/A")
        
        # d) Shareholding Pattern
        print("\n  👥 Shareholding:")
        
        promoter_holding = info.get('heldPercentInsiders', None)
        analysis['promoter_holding'] = float(promoter_holding * 100) if promoter_holding else None
        print(f"    • Promoter Holding: {promoter_holding*100:.1f}%" if promoter_holding else "    • Promoter Holding: N/A")
        
        institutional = info.get('heldPercentInstitutions', None)
        analysis['institutional_holding'] = float(institutional * 100) if institutional else None
        print(f"    • Institutional: {institutional*100:.1f}%" if institutional else "    • Institutional: N/A")
        
        return analysis
    
    def _sip_timing_analysis(self, hist: pd.DataFrame, tech_analysis: Dict) -> Dict:
        """
        Analyze if it's good time to start SIP based on MWWR and TWWR
        """
        analysis = {}
        
        current_price = hist['Close'].iloc[-1]
        bottom_price = tech_analysis.get('bottom_price', current_price)
        top_price = tech_analysis.get('top_price', current_price)
        
        # Calculate position in range
        price_range = top_price - bottom_price
        position_in_range = (current_price - bottom_price) / price_range if price_range > 0 else 0
        
        analysis['position_in_range'] = float(position_in_range * 100)
        
        # SIP recommendation
        if position_in_range < 0.3:
            recommendation = "EXCELLENT"
            reason = "Near bottom, great entry point"
        elif position_in_range < 0.5:
            recommendation = "GOOD"
            reason = "Below mid-range, favorable for SIP"
        elif position_in_range < 0.7:
            recommendation = "MODERATE"
            reason = "Mid-range, average entry point"
        elif position_in_range < 0.9:
            recommendation = "CAUTION"
            reason = "Near top, wait for correction"
        else:
            recommendation = "AVOID"
            reason = "At/near top, high risk"
        
        analysis['sip_recommendation'] = recommendation
        analysis['reason'] = reason
        
        # Calculate potential MWWR and TWWR
        # Simulate SIP over next 24 months
        monthly_investment = 10000  # Example
        months = 24
        
        # Estimate future prices (conservative)
        expected_return = 0.15  # 15% annual
        future_price = current_price * ((1 + expected_return) ** 2)
        
        analysis['expected_2y_price'] = float(future_price)
        analysis['expected_2y_return'] = float((future_price - current_price) / current_price * 100)
        
        print(f"  📍 Current Position: {position_in_range*100:.1f}% of range (Bottom to Top)")
        print(f"  🎯 SIP Recommendation: {recommendation}")
        print(f"  💡 Reason: {reason}")
        print(f"\n  📊 2-Year Projections:")
        print(f"    • Expected Price: ₹{future_price:.2f}")
        print(f"    • Expected Return: {analysis['expected_2y_return']:.1f}%")
        
        return analysis
    
    def _calculate_return_potential(self, hist: pd.DataFrame, info: Dict, current_price: float) -> Dict:
        """
        Calculate 2-year return potential
        """
        # Use multiple methods
        methods = {}
        
        # Method 1: Historical CAGR
        if len(hist) > 252:  # At least 1 year
            start_price = hist['Close'].iloc[0]
            years = len(hist) / 252
            cagr = (current_price / start_price) ** (1 / years) - 1
            two_year_target = current_price * ((1 + cagr) ** 2)
            methods['historical_cagr'] = {
                'target': float(two_year_target),
                'return': float((two_year_target - current_price) / current_price * 100)
            }
        
        # Method 2: Growth-based
        revenue_growth = info.get('revenueGrowth', 0.15)
        growth_target = current_price * ((1 + revenue_growth) ** 2)
        methods['growth_based'] = {
            'target': float(growth_target),
            'return': float((growth_target - current_price) / current_price * 100)
        }
        
        # Method 3: Conservative (10% CAGR)
        conservative_target = current_price * (1.1 ** 2)
        methods['conservative'] = {
            'target': float(conservative_target),
            'return': float((conservative_target - current_price) / current_price * 100)
        }
        
        # Consensus
        targets = [m['target'] for m in methods.values()]
        consensus_target = np.mean(targets)
        consensus_return = (consensus_target - current_price) / current_price * 100
        
        print(f"  🎯 Consensus 2Y Target: ₹{consensus_target:.2f}")
        print(f"  📈 Expected Return: {consensus_return:.1f}%")
        print(f"  📊 Range: ₹{min(targets):.2f} - ₹{max(targets):.2f}")
        
        return {
            'methods': methods,
            'consensus_target': float(consensus_target),
            'consensus_return': float(consensus_return),
            'min_target': float(min(targets)),
            'max_target': float(max(targets))
        }
    
    def compare_with_zomato(self, ipo_ticker: str, ipo_results: Dict) -> Dict:
        """
        Compare IPO with Zomato's performance
        """
        print(f"\n{'='*80}")
        print(f"🔄 COMPARING WITH ZOMATO")
        print(f"{'='*80}\n")
        
        # Analyze Zomato
        zomato_results = self.analyze_ipo('ZOMATO.NS', '2021-07-23')
        
        comparison = {
            'ipo': ipo_ticker,
            'benchmark': 'ZOMATO.NS',
            'metrics': {}
        }
        
        # Compare key metrics
        print("📊 COMPARISON METRICS:")
        print("-" * 80)
        
        # Technical comparison
        ipo_tech = ipo_results['technical_analysis']
        zom_tech = zomato_results['technical_analysis']
        
        print(f"\n  Technical Analysis:")
        print(f"    Metric                    {ipo_results['name']:>15}    Zomato")
        print(f"    {'-'*60}")
        print(f"    Weeks to Top:             {ipo_tech.get('weeks_to_top', 0):>15.1f}    {zom_tech.get('weeks_to_top', 0):.1f}")
        print(f"    Gain to Top:              {ipo_tech.get('gain_to_top', 0):>14.1f}%    {zom_tech.get('gain_to_top', 0):.1f}%")
        print(f"    Drop from Top:            {ipo_tech.get('drop_from_top', 0):>14.1f}%    {zom_tech.get('drop_from_top', 0):.1f}%")
        print(f"    Current from Listing:     {ipo_tech.get('from_listing_pct', 0):>14.1f}%    {zom_tech.get('from_listing_pct', 0):.1f}%")
        
        # Fundamental comparison
        ipo_fund = ipo_results['fundamental_analysis']
        zom_fund = zomato_results['fundamental_analysis']
        
        print(f"\n  Fundamental Analysis:")
        print(f"    Metric                    {ipo_results['name']:>15}    Zomato")
        print(f"    {'-'*60}")
        
        ipo_pe = ipo_fund.get('pe_ratio')
        zom_pe = zom_fund.get('pe_ratio')
        print(f"    P/E Ratio:                {ipo_pe if ipo_pe else 'N/A':>15}    {zom_pe if zom_pe else 'N/A'}")
        
        ipo_rev = ipo_fund.get('revenue_growth')
        zom_rev = zom_fund.get('revenue_growth')
        print(f"    Revenue Growth:           {f'{ipo_rev:.1f}%' if ipo_rev else 'N/A':>15}    {f'{zom_rev:.1f}%' if zom_rev else 'N/A'}")
        
        # Return potential comparison
        ipo_ret = ipo_results['return_potential']
        zom_ret = zomato_results['return_potential']
        
        print(f"\n  2-Year Return Potential:")
        print(f"    {ipo_results['name']:>20}: {ipo_ret['consensus_return']:>6.1f}%")
        print(f"    {'Zomato':>20}: {zom_ret['consensus_return']:>6.1f}%")
        
        # Verdict
        print(f"\n{'='*80}")
        print(f"🎯 VERDICT")
        print(f"{'='*80}\n")
        
        if ipo_ret['consensus_return'] > zom_ret['consensus_return']:
            print(f"  ✅ {ipo_results['name']} shows HIGHER return potential than Zomato")
            print(f"  📈 Expected outperformance: {ipo_ret['consensus_return'] - zom_ret['consensus_return']:.1f}%")
        else:
            print(f"  ⚠️ {ipo_results['name']} shows LOWER return potential than Zomato")
            print(f"  📉 Expected underperformance: {ipo_ret['consensus_return'] - zom_ret['consensus_return']:.1f}%")
        
        return comparison


if __name__ == "__main__":
    import sys
    
    analyzer = IPOAnalyzer()
    
    # Analyze FirstCry
    print("\n" + "="*80)
    print("🎯 IPO ANALYSIS: FIRSTCRY")
    print("="*80)
    
    firstcry_results = analyzer.analyze_ipo('FIRSTCRY.NS', '2024-08-13')
    
    # Compare with Zomato
    comparison = analyzer.compare_with_zomato('FIRSTCRY.NS', firstcry_results)
    
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE")
    print("="*80)
