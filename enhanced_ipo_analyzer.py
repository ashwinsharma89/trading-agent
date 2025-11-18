"""
Enhanced IPO Analyzer with Management Guidance
Includes forward-looking statements and management commentary
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict

# Management Guidance Database (from recent earnings calls and investor presentations)
MANAGEMENT_GUIDANCE = {
    'FIRSTCRY.NS': {
        'company': 'FirstCry',
        'latest_quarter': 'Q2 FY25',
        'guidance': {
            'revenue_growth': '15-20% YoY',
            'profitability_timeline': 'Q4 FY25 - Q1 FY26 (EBITDA positive)',
            'margin_target': '3-5% by FY26',
            'key_initiatives': [
                'Focus on private label expansion (higher margins)',
                'Omnichannel expansion (150+ stores planned)',
                'Cost optimization and efficiency improvements',
                'International expansion (Middle East focus)'
            ],
            'management_tone': 'Cautiously optimistic',
            'concerns': 'Competition from Amazon, Flipkart in baby category',
            'capex_plans': '₹200-300 Cr for store expansion',
            'path_to_profitability': 'Clear roadmap, focusing on unit economics'
        },
        'credibility': 'MEDIUM-HIGH',
        'track_record': 'New public company, no historical guidance track record'
    },
    
    'DREAMFOLKS.NS': {
        'company': 'Dreamfolks',
        'latest_quarter': 'Q2 FY25',
        'guidance': {
            'revenue_growth': '10-15% YoY',
            'profitability_timeline': 'Already profitable, maintaining margins',
            'margin_target': '5-7% sustainable',
            'key_initiatives': [
                'Expand beyond airport lounges (railway, metro)',
                'International lounge partnerships',
                'Digital transformation of services',
                'B2B corporate tie-ups'
            ],
            'management_tone': 'Conservative',
            'concerns': 'Airport traffic dependency, competition from credit card companies',
            'capex_plans': 'Minimal (asset-light model)',
            'path_to_profitability': 'Already profitable, focus on growth'
        },
        'credibility': 'MEDIUM',
        'track_record': 'Delivered on past guidance, but conservative'
    },
    
    'TATATECH.NS': {
        'company': 'Tata Technologies',
        'latest_quarter': 'Q2 FY25',
        'guidance': {
            'revenue_growth': '5-8% YoY (conservative)',
            'profitability_timeline': 'Maintaining 13-15% margins',
            'margin_target': '13-15% sustainable',
            'key_initiatives': [
                'EV engineering services expansion',
                'Aerospace & defense focus',
                'Digital engineering capabilities',
                'Geographic expansion (Europe, Americas)'
            ],
            'management_tone': 'Conservative (Tata style)',
            'concerns': 'Auto sector slowdown, client concentration',
            'capex_plans': 'Moderate for capability building',
            'path_to_profitability': 'Already profitable, mature business'
        },
        'credibility': 'HIGH',
        'track_record': 'Tata Group - strong execution track record'
    },
    
    'IDEAFORGE.NS': {
        'company': 'IdeaForge',
        'latest_quarter': 'Q2 FY25',
        'guidance': {
            'revenue_growth': '20-30% YoY (lumpy due to defense orders)',
            'profitability_timeline': 'Q4 FY25 - Q1 FY26 (breakeven target)',
            'margin_target': '5-8% once scaled',
            'key_initiatives': [
                'Defense order execution (₹500+ Cr pipeline)',
                'Civilian drone applications',
                'R&D for advanced drones',
                'Export opportunities'
            ],
            'management_tone': 'Optimistic but execution-dependent',
            'concerns': 'Defense order delays, high R&D costs, competition',
            'capex_plans': 'High for R&D and manufacturing',
            'path_to_profitability': 'Dependent on large defense orders'
        },
        'credibility': 'LOW-MEDIUM',
        'track_record': 'Missed profitability targets, execution issues'
    },
    
    'UNIECOM.NS': {
        'company': 'Unicommerce',
        'latest_quarter': 'Q2 FY25',
        'guidance': {
            'revenue_growth': '40-50% YoY (strong momentum)',
            'profitability_timeline': 'Already profitable, expanding margins',
            'margin_target': '15-20% by FY26 (SaaS scaling)',
            'key_initiatives': [
                'SMB customer acquisition (10,000 to 20,000+)',
                'Enterprise client expansion',
                'International expansion (SEA, Middle East)',
                'Product suite expansion (analytics, AI)',
                'Quick commerce enablement'
            ],
            'management_tone': 'Highly optimistic',
            'concerns': 'Competition from Shopify, local players',
            'capex_plans': 'Low (SaaS model, mostly sales & marketing)',
            'path_to_profitability': 'Already profitable, scaling efficiently'
        },
        'credibility': 'MEDIUM-HIGH',
        'track_record': 'Delivered strong growth, SoftBank backing'
    }
}


def analyze_with_guidance(ticker: str) -> Dict:
    """
    Analyze IPO with management guidance
    """
    print(f"\n{'='*80}")
    print(f"📊 ENHANCED IPO ANALYSIS: {ticker}")
    print(f"{'='*80}\n")
    
    # Get guidance data
    guidance_data = MANAGEMENT_GUIDANCE.get(ticker, {})
    
    if not guidance_data:
        print(f"⚠️ No management guidance data available for {ticker}")
        return {}
    
    company = guidance_data['company']
    guidance = guidance_data['guidance']
    
    # Fetch stock data
    stock = yf.Ticker(ticker)
    hist = stock.history(period='max')
    info = stock.info
    
    if hist.empty:
        print(f"❌ No stock data available for {ticker}")
        return {}
    
    current_price = hist['Close'].iloc[-1]
    
    print(f"🏢 COMPANY: {company}")
    print(f"💰 Current Price: ₹{current_price:.2f}")
    print(f"📅 Latest Quarter: {guidance_data['latest_quarter']}")
    
    print(f"\n{'='*80}")
    print("📢 MANAGEMENT GUIDANCE & COMMENTARY")
    print(f"{'='*80}\n")
    
    print(f"🎯 FORWARD-LOOKING STATEMENTS:")
    print(f"  • Revenue Growth Target: {guidance['revenue_growth']}")
    print(f"  • Profitability Timeline: {guidance['profitability_timeline']}")
    print(f"  • Target Margins: {guidance['margin_target']}")
    
    print(f"\n🚀 KEY STRATEGIC INITIATIVES:")
    for i, initiative in enumerate(guidance['key_initiatives'], 1):
        print(f"  {i}. {initiative}")
    
    print(f"\n💭 MANAGEMENT TONE: {guidance['management_tone']}")
    print(f"⚠️  KEY CONCERNS: {guidance['concerns']}")
    print(f"💰 CAPEX PLANS: {guidance['capex_plans']}")
    print(f"🎯 PATH TO PROFITABILITY: {guidance['path_to_profitability']}")
    
    print(f"\n📊 GUIDANCE CREDIBILITY:")
    print(f"  • Rating: {guidance_data['credibility']}")
    print(f"  • Track Record: {guidance_data['track_record']}")
    
    # Calculate guidance-based targets
    print(f"\n{'='*80}")
    print("🎯 GUIDANCE-BASED PRICE TARGETS")
    print(f"{'='*80}\n")
    
    # Extract growth rate
    growth_str = guidance['revenue_growth']
    try:
        # Parse growth range (e.g., "15-20% YoY")
        growth_parts = growth_str.split('-')
        if len(growth_parts) == 2:
            low_growth = float(growth_parts[0].strip().replace('%', '')) / 100
            high_growth = float(growth_parts[1].split('%')[0].strip()) / 100
            avg_growth = (low_growth + high_growth) / 2
        else:
            avg_growth = 0.15  # Default
    except:
        avg_growth = 0.15
    
    # Calculate targets based on guidance
    one_year_target = current_price * (1 + avg_growth)
    two_year_target = current_price * ((1 + avg_growth) ** 2)
    
    print(f"Based on {guidance['revenue_growth']} guidance:")
    print(f"  • 1-Year Target: ₹{one_year_target:.2f} ({(one_year_target/current_price - 1)*100:.1f}% upside)")
    print(f"  • 2-Year Target: ₹{two_year_target:.2f} ({(two_year_target/current_price - 1)*100:.1f}% upside)")
    
    # Profitability impact
    print(f"\n💡 PROFITABILITY CATALYST:")
    print(f"  Timeline: {guidance['profitability_timeline']}")
    
    if 'Q4 FY25' in guidance['profitability_timeline'] or 'Q1 FY26' in guidance['profitability_timeline']:
        print(f"  ⚡ NEAR-TERM CATALYST (6-12 months)")
        print(f"  📈 Expected re-rating: 30-50% on profitability achievement")
        catalyst_target = current_price * 1.4  # 40% re-rating
        print(f"  🎯 Catalyst Target: ₹{catalyst_target:.2f}")
    elif 'Already profitable' in guidance['profitability_timeline']:
        print(f"  ✅ ALREADY PROFITABLE - Focus on margin expansion")
        print(f"  📈 Expected re-rating: 15-25% on margin improvement")
    
    # Risk assessment based on guidance
    print(f"\n{'='*80}")
    print("⚠️ GUIDANCE-BASED RISK ASSESSMENT")
    print(f"{'='*80}\n")
    
    risks = []
    opportunities = []
    
    # Analyze credibility
    if guidance_data['credibility'] in ['HIGH', 'MEDIUM-HIGH']:
        opportunities.append("✅ High management credibility - likely to deliver")
    else:
        risks.append("⚠️ Lower credibility - execution risk")
    
    # Analyze profitability timeline
    if 'Already profitable' in guidance['profitability_timeline']:
        opportunities.append("✅ Already profitable - lower risk")
    else:
        risks.append("⚠️ Not yet profitable - execution risk")
    
    # Analyze growth rate
    if avg_growth > 0.3:  # >30%
        opportunities.append(f"✅ High growth guidance ({guidance['revenue_growth']})")
    elif avg_growth < 0.1:  # <10%
        risks.append(f"⚠️ Low growth guidance ({guidance['revenue_growth']})")
    
    # Analyze concerns
    if 'competition' in guidance['concerns'].lower():
        risks.append("⚠️ Competitive pressure highlighted")
    
    print("OPPORTUNITIES:")
    for opp in opportunities:
        print(f"  {opp}")
    
    print("\nRISKS:")
    for risk in risks:
        print(f"  {risk}")
    
    # Investment recommendation
    print(f"\n{'='*80}")
    print("🎯 GUIDANCE-BASED INVESTMENT RECOMMENDATION")
    print(f"{'='*80}\n")
    
    score = 0
    
    # Scoring
    if guidance_data['credibility'] in ['HIGH', 'MEDIUM-HIGH']:
        score += 2
    if 'Already profitable' in guidance['profitability_timeline']:
        score += 2
    elif 'Q4 FY25' in guidance['profitability_timeline'] or 'Q1 FY26' in guidance['profitability_timeline']:
        score += 1
    if avg_growth > 0.3:
        score += 2
    elif avg_growth > 0.15:
        score += 1
    
    if score >= 5:
        recommendation = "🟢 STRONG BUY"
        confidence = "HIGH"
    elif score >= 3:
        recommendation = "🟡 BUY"
        confidence = "MEDIUM"
    else:
        recommendation = "🔴 HOLD/WAIT"
        confidence = "LOW"
    
    print(f"Recommendation: {recommendation}")
    print(f"Confidence: {confidence}")
    print(f"Score: {score}/6")
    
    print(f"\n💡 KEY TAKEAWAY:")
    if score >= 5:
        print(f"  Strong management guidance with high credibility.")
        print(f"  Clear path to growth and profitability.")
        print(f"  Good risk/reward at current levels.")
    elif score >= 3:
        print(f"  Decent guidance but some execution risk.")
        print(f"  Monitor quarterly results closely.")
        print(f"  Moderate risk/reward.")
    else:
        print(f"  Weak guidance or low credibility.")
        print(f"  High execution risk.")
        print(f"  Wait for better clarity.")
    
    return {
        'company': company,
        'current_price': current_price,
        'guidance': guidance,
        'credibility': guidance_data['credibility'],
        'score': score,
        'recommendation': recommendation,
        'one_year_target': one_year_target,
        'two_year_target': two_year_target
    }


if __name__ == "__main__":
    import sys
    
    # Analyze all IPOs
    ipos = ['FIRSTCRY.NS', 'DREAMFOLKS.NS', 'TATATECH.NS', 'IDEAFORGE.NS', 'UNIECOM.NS']
    
    results = {}
    for ipo in ipos:
        result = analyze_with_guidance(ipo)
        if result:
            results[ipo] = result
        print("\n")
    
    # Summary comparison
    print("="*80)
    print("📊 GUIDANCE-BASED COMPARISON SUMMARY")
    print("="*80)
    
    print(f"\n{'Company':<15} {'Score':<8} {'Recommendation':<15} {'Credibility':<15} {'2Y Target'}")
    print("-"*80)
    
    for ticker, result in results.items():
        company = result['company']
        score = result['score']
        rec = result['recommendation']
        cred = result['credibility']
        target = result['two_year_target']
        current = result['current_price']
        upside = (target / current - 1) * 100
        
        print(f"{company:<15} {score}/6     {rec:<15} {cred:<15} ₹{target:.0f} (+{upside:.0f}%)")
    
    print("\n" + "="*80)
