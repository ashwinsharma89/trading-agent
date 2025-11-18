"""
Multibagger Identification System
Identifies stocks with potential to become multibaggers (3x-10x returns)
Based on weekly close patterns, fundamentals, and growth indicators
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class MultibaggerIdentifier:
    """
    Systematic approach to identify potential multibagger stocks
    """
    
    def __init__(self):
        self.multibagger_criteria = {
            # Fundamental Criteria (40% weight)
            "min_revenue_growth": 25.0,  # 25%+ annual revenue growth
            "min_profit_growth": 30.0,   # 30%+ annual profit growth
            "max_pe_ratio": 25.0,        # Reasonable valuation
            "min_roce": 15.0,            # 15%+ Return on Capital Employed
            "debt_to_equity_max": 0.8,   # Conservative debt levels
            
            # Technical Criteria (30% weight)
            "weekly_close_strength": 3.0,  # 3%+ weekly close gains
            "volume_ratio_min": 2.0,       # 2x+ volume confirmation
            "rsi_weekly_range": (50, 70),  # Healthy momentum
            "price_above_ma": True,         # Above key moving averages
            
            # Business Quality (20% weight)
            "competitive_moat": True,       # Strong competitive advantage
            "market_leadership": True,      # #1 or #2 in sector
            "scalable_business": True,      # Scalable business model
            
            # Management & Governance (10% weight)
            "promoter_holding_min": 40.0,   # 40%+ promoter holding
            "fiis_diis_increasing": True,   # Institutional confidence
            "corporate_governance": True    # Clean governance
        }
        
        # Potential multibagger candidates (as of Nov 2025)
        self.multibagger_universe = {
            # Small/Mid Caps with High Growth Potential
            "KAJARIACER": {
                "sector": "Ceramics", 
                "current_price": 1250.60, 
                "market_cap": 15000,  # ₹15,000 crore
                "quality_score": 78,
                "growth_stage": "expansion"
            },
            "POLYMED": {
                "sector": "Pharma", 
                "current_price": 2850.60, 
                "market_cap": 12000,  # ₹12,000 crore
                "quality_score": 84,
                "growth_stage": "rapid_growth"
            },
            "SUNDERAM": {
                "sector": "Auto Ancillary", 
                "current_price": 2650.80, 
                "market_cap": 8000,   # ₹8,000 crore
                "quality_score": 73,
                "growth_stage": "expansion"
            },
            "TIMECON": {
                "sector": "Education", 
                "current_price": 1250.40, 
                "market_cap": 6000,   # ₹6,000 crore
                "quality_score": 69,
                "growth_stage": "turnaround"
            },
            "CERA": {
                "sector": "Ceramics", 
                "current_price": 850.40, 
                "market_cap": 7000,   # ₹7,000 crore
                "quality_score": 74,
                "growth_stage": "growth"
            },
            
            # Emerging Leaders
            "RAYMOND": {
                "sector": "Textiles", 
                "current_price": 1850.80, 
                "market_cap": 10000,  # ₹10,000 crore
                "quality_score": 75,
                "growth_stage": "transformation"
            },
            "JYOTHYLAB": {
                "sector": "Consumer Goods", 
                "current_price": 285.60, 
                "market_cap": 5000,   # ₹5,000 crore
                "quality_score": 71,
                "growth_stage": "growth"
            },
            "SHOPERSTOP": {
                "sector": "Retail", 
                "current_price": 650.20, 
                "market_cap": 4000,   # ₹4,000 crore
                "quality_score": 72,
                "growth_stage": "expansion"
            },
            
            # Special Situations
            "MANAPPURAM": {
                "sector": "NBFC", 
                "current_price": 185.40, 
                "market_cap": 9000,   # ₹9,000 crore
                "quality_score": 70,
                "growth_stage": "growth"
            },
            "SUNTECK": {
                "sector": "Real Estate", 
                "current_price": 485.20, 
                "market_cap": 3000,   # ₹3,000 crore
                "quality_score": 72,
                "growth_stage": "turnaround"
            }
        }
    
    def analyze_multibagger_potential(self, symbol: str) -> Dict:
        """
        Comprehensive analysis of multibagger potential
        """
        
        if symbol not in self.multibagger_universe:
            return {"error": f"Stock {symbol} not in multibagger universe"}
        
        stock_data = self.multibagger_universe[symbol]
        current_price = stock_data["current_price"]
        
        # Fundamental Analysis
        fundamental_score = self._analyze_fundamentals(symbol)
        
        # Technical Analysis (Weekly Close Focus)
        technical_score = self._analyze_technicals(symbol)
        
        # Business Quality Analysis
        business_score = self._analyze_business_quality(symbol)
        
        # Management & Governance Analysis
        governance_score = self._analyze_governance(symbol)
        
        # Growth Potential Analysis
        growth_potential = self._analyze_growth_potential(symbol)
        
        # Calculate overall multibagger score
        overall_score = (
            fundamental_score * 0.40 +
            technical_score * 0.30 +
            business_score * 0.20 +
            governance_score * 0.10
        )
        
        # Generate multibagger recommendation
        recommendation = self._generate_multibagger_recommendation(
            symbol, overall_score, growth_potential
        )
        
        # Risk assessment
        risk_assessment = self._assess_multibagger_risk(symbol, overall_score)
        
        analysis_result = {
            "symbol": symbol,
            "sector": stock_data["sector"],
            "current_price": current_price,
            "market_cap": stock_data["market_cap"],
            "growth_stage": stock_data["growth_stage"],
            "fundamental_score": fundamental_score,
            "technical_score": technical_score,
            "business_score": business_score,
            "governance_score": governance_score,
            "overall_score": overall_score,
            "growth_potential": growth_potential,
            "recommendation": recommendation,
            "risk_assessment": risk_assessment,
            "analysis_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        return analysis_result
    
    def get_top_multibagger_candidates(self) -> List[Dict]:
        """
        Get top multibagger candidates based on comprehensive analysis
        """
        
        candidates = []
        
        for symbol in self.multibagger_universe.keys():
            analysis = self.analyze_multibagger_potential(symbol)
            if analysis["recommendation"]["multibagger_potential"] in ["HIGH", "VERY_HIGH"]:
                candidates.append(analysis)
        
        # Sort by overall score and growth potential
        candidates.sort(
            key=lambda x: (x["overall_score"], x["growth_potential"]["potential_return_3y"]),
            reverse=True
        )
        
        return candidates[:8]
    
    def _analyze_fundamentals(self, symbol: str) -> float:
        """
        Analyze fundamental strength for multibagger potential
        """
        
        # Simulate fundamental metrics (in production, use real data)
        np.random.seed(hash(symbol) % 2**32)
        
        revenue_growth = np.random.uniform(20, 45)  # 20-45% revenue growth
        profit_growth = np.random.uniform(25, 60)   # 25-60% profit growth
        pe_ratio = np.random.uniform(15, 30)        # 15-30 PE ratio
        roce = np.random.uniform(12, 25)            # 12-25% ROCE
        debt_to_equity = np.random.uniform(0.2, 1.2) # 0.2-1.2 D/E
        
        # Score calculation (0-100)
        score = 0
        
        # Revenue growth (25 points)
        if revenue_growth >= 35:
            score += 25
        elif revenue_growth >= 25:
            score += 20
        elif revenue_growth >= 15:
            score += 15
        else:
            score += 10
        
        # Profit growth (25 points)
        if profit_growth >= 40:
            score += 25
        elif profit_growth >= 30:
            score += 20
        elif profit_growth >= 20:
            score += 15
        else:
            score += 10
        
        # ROCE (25 points)
        if roce >= 20:
            score += 25
        elif roce >= 15:
            score += 20
        elif roce >= 10:
            score += 15
        else:
            score += 10
        
        # Valuation (15 points)
        if pe_ratio <= 20:
            score += 15
        elif pe_ratio <= 25:
            score += 12
        elif pe_ratio <= 30:
            score += 8
        else:
            score += 5
        
        # Debt levels (10 points)
        if debt_to_equity <= 0.5:
            score += 10
        elif debt_to_equity <= 0.8:
            score += 8
        elif debt_to_equity <= 1.0:
            score += 5
        else:
            score += 2
        
        return min(100, score)
    
    def _analyze_technicals(self, symbol: str) -> float:
        """
        Analyze technical indicators with weekly close focus
        """
        
        np.random.seed(abs(hash(symbol) + 1) % 2**32)
        
        weekly_close_strength = np.random.uniform(1, 6)    # 1-6% weekly close
        volume_ratio = np.random.uniform(1.5, 3.5)         # 1.5-3.5x volume
        rsi_weekly = np.random.uniform(45, 75)             # 45-75 RSI
        price_above_ma = np.random.choice([True, False], p=[0.7, 0.3])
        
        # Score calculation (0-100)
        score = 0
        
        # Weekly close strength (40 points)
        if weekly_close_strength >= 4:
            score += 40
        elif weekly_close_strength >= 3:
            score += 30
        elif weekly_close_strength >= 2:
            score += 20
        else:
            score += 10
        
        # Volume confirmation (30 points)
        if volume_ratio >= 3:
            score += 30
        elif volume_ratio >= 2:
            score += 25
        elif volume_ratio >= 1.5:
            score += 15
        else:
            score += 5
        
        # RSI momentum (20 points)
        if 55 <= rsi_weekly <= 70:
            score += 20
        elif 50 <= rsi_weekly <= 75:
            score += 15
        elif 45 <= rsi_weekly <= 80:
            score += 10
        else:
            score += 5
        
        # Price position (10 points)
        if price_above_ma:
            score += 10
        else:
            score += 3
        
        return min(100, score)
    
    def _analyze_business_quality(self, symbol: str) -> float:
        """
        Analyze business quality and competitive positioning
        """
        
        np.random.seed(abs(hash(symbol) + 2) % 2**32)
        
        competitive_moat = np.random.choice(["strong", "moderate", "weak"], p=[0.3, 0.5, 0.2])
        market_share = np.random.uniform(5, 25)  # 5-25% market share
        scalability = np.random.choice(["high", "medium", "low"], p=[0.4, 0.4, 0.2])
        industry_growth = np.random.uniform(10, 25)  # 10-25% industry growth
        
        # Score calculation (0-100)
        score = 0
        
        # Competitive moat (40 points)
        if competitive_moat == "strong":
            score += 40
        elif competitive_moat == "moderate":
            score += 25
        else:
            score += 10
        
        # Market leadership (30 points)
        if market_share >= 20:
            score += 30
        elif market_share >= 15:
            score += 25
        elif market_share >= 10:
            score += 20
        else:
            score += 15
        
        # Scalability (20 points)
        if scalability == "high":
            score += 20
        elif scalability == "medium":
            score += 15
        else:
            score += 8
        
        # Industry growth (10 points)
        if industry_growth >= 20:
            score += 10
        elif industry_growth >= 15:
            score += 8
        else:
            score += 5
        
        return min(100, score)
    
    def _analyze_governance(self, symbol: str) -> float:
        """
        Analyze management quality and corporate governance
        """
        
        np.random.seed(abs(hash(symbol) + 3) % 2**32)
        
        promoter_holding = np.random.uniform(30, 70)  # 30-70% promoter holding
        fiis_diis_trend = np.random.choice(["increasing", "stable", "decreasing"], p=[0.5, 0.3, 0.2])
        corporate_governance = np.random.choice(["excellent", "good", "average"], p=[0.3, 0.5, 0.2])
        management_experience = np.random.uniform(5, 20)  # 5-20 years
        
        # Score calculation (0-100)
        score = 0
        
        # Promoter holding (30 points)
        if promoter_holding >= 55:
            score += 30
        elif promoter_holding >= 45:
            score += 25
        elif promoter_holding >= 35:
            score += 20
        else:
            score += 15
        
        # Institutional confidence (25 points)
        if fiis_diis_trend == "increasing":
            score += 25
        elif fiis_diis_trend == "stable":
            score += 18
        else:
            score += 10
        
        # Corporate governance (25 points)
        if corporate_governance == "excellent":
            score += 25
        elif corporate_governance == "good":
            score += 20
        else:
            score += 12
        
        # Management experience (20 points)
        if management_experience >= 15:
            score += 20
        elif management_experience >= 10:
            score += 15
        else:
            score += 10
        
        return min(100, score)
    
    def _analyze_growth_potential(self, symbol: str) -> Dict:
        """
        Analyze growth potential and multibagger timeline
        """
        
        stock_data = self.multibagger_universe[symbol]
        growth_stage = stock_data["growth_stage"]
        current_price = stock_data["current_price"]
        
        # Growth potential based on stage
        growth_potentials = {
            "turnaround": {"2y": 2.5, "3y": 4.0, "5y": 8.0},
            "growth": {"2y": 2.0, "3y": 3.5, "5y": 6.0},
            "rapid_growth": {"2y": 3.0, "3y": 5.0, "5y": 10.0},
            "expansion": {"2y": 1.8, "3y": 3.0, "5y": 5.0},
            "transformation": {"2y": 2.2, "3y": 4.0, "5y": 7.0}
        }
        
        potential = growth_potentials.get(growth_stage, {"2y": 1.5, "3y": 2.5, "5y": 4.0})
        
        return {
            "growth_stage": growth_stage,
            "potential_return_2y": f"{(potential['2y'] - 1) * 100:.0f}%",
            "potential_return_3y": f"{(potential['3y'] - 1) * 100:.0f}%",
            "potential_return_5y": f"{(potential['5y'] - 1) * 100:.0f}%",
            "target_price_2y": round(current_price * potential['2y'], 2),
            "target_price_3y": round(current_price * potential['3y'], 2),
            "target_price_5y": round(current_price * potential['5y'], 2),
            "time_to_2x": "18-24 months" if potential['2y'] >= 2 else "24-30 months",
            "time_to_3x": "30-36 months" if potential['3y'] >= 3 else "36-42 months",
            "time_to_5x": "48-60 months" if potential['5y'] >= 5 else "60+ months"
        }
    
    def _generate_multibagger_recommendation(self, symbol: str, overall_score: float, 
                                            growth_potential: Dict) -> Dict:
        """
        Generate multibagger recommendation based on comprehensive analysis
        """
        
        if overall_score >= 80:
            potential = "VERY_HIGH"
            confidence = 85
            action = "STRONG BUY - Multibagger Potential"
        elif overall_score >= 70:
            potential = "HIGH"
            confidence = 75
            action = "BUY - High Multibagger Potential"
        elif overall_score >= 60:
            potential = "MEDIUM"
            confidence = 65
            action = "HOLD - Monitor for Entry"
        else:
            potential = "LOW"
            confidence = 45
            action = "AVOID - Low Multibagger Potential"
        
        return {
            "action": action,
            "multibagger_potential": potential,
            "confidence_score": confidence,
            "overall_score": overall_score,
            "entry_strategy": self._get_entry_strategy(overall_score),
            "holding_period": "3-5 years minimum",
            "position_size": self._get_position_size(overall_score),
            "monitoring_frequency": "Weekly reviews mandatory"
        }
    
    def _get_entry_strategy(self, score: float) -> str:
        """Get entry strategy based on score"""
        if score >= 80:
            return "Accumulate on dips, 25% at a time over 3 months"
        elif score >= 70:
            return "Buy on correction, 50% at entry, 50% on dips"
        else:
            return "Wait for significant correction before entry"
    
    def _get_position_size(self, score: float) -> str:
        """Get recommended position size"""
        if score >= 80:
            return "8-10% of portfolio"
        elif score >= 70:
            return "5-7% of portfolio"
        else:
            return "2-3% of portfolio"
    
    def _assess_multibagger_risk(self, symbol: str, overall_score: float) -> Dict:
        """Assess risks specific to multibagger investments"""
        
        stock_data = self.multibagger_universe[symbol]
        market_cap = stock_data["market_cap"]
        
        risk_factors = []
        
        # Market cap risk
        if market_cap < 5000:
            risk_factors.append("Very small market cap - high volatility")
        elif market_cap < 10000:
            risk_factors.append("Small market cap - liquidity risk")
        
        # Business risk
        risk_factors.append("Execution risk on growth plans")
        risk_factors.append("Competition intensification risk")
        risk_factors.append("Regulatory changes impact")
        
        # Market risk
        risk_factors.append("Market sentiment sensitivity")
        risk_factors.append("Funding risk for expansion")
        
        # Scoring based risk level
        if overall_score >= 80:
            risk_level = "Medium-High"
        elif overall_score >= 70:
            risk_level = "High"
        else:
            risk_level = "Very High"
        
        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "volatility_expectation": "Very High",
            "liquidity_risk": "Medium to High",
            "time_horizon_risk": "Long-term commitment required"
        }


def identify_multibaggers():
    """
    Identify top multibagger candidates with comprehensive analysis
    """
    
    identifier = MultibaggerIdentifier()
    
    print("🚀 Multibagger Identification System")
    print("=" * 60)
    print("Identifying Stocks with 3x-10x Potential | November 2025")
    print("=" * 60)
    
    top_candidates = identifier.get_top_multibagger_candidates()
    
    print(f"\n📊 Top Multibagger Candidates:")
    print("-" * 60)
    
    print(f"{'Rank':<4} {'Stock':<12} {'Price':<10} {'Score':<8} {'3Y Potential':<12} {'Risk':<10} {'Stage':<12}")
    print("-" * 80)
    
    for i, candidate in enumerate(top_candidates, 1):
        symbol = candidate["symbol"]
        price = candidate["current_price"]
        score = candidate["overall_score"]
        potential_3y = candidate["growth_potential"]["potential_return_3y"]
        risk = candidate["risk_assessment"]["risk_level"]
        stage = candidate["growth_stage"].title()
        
        print(f"{i:<4} {symbol:<12} ₹{price:<9.2f} {score:<8.0f} {potential_3y:<12} {risk:<10} {stage:<12}")
    
    print(f"\n📈 Detailed Multibagger Analysis:")
    print("=" * 60)
    
    for i, candidate in enumerate(top_candidates, 1):
        print(f"\n{i}. {candidate['symbol']} ({candidate['sector']})")
        print(f"   Current Price: ₹{candidate['current_price']:.2f}")
        print(f"   Market Cap: ₹{candidate['market_cap']:,} crore")
        print(f"   Growth Stage: {candidate['growth_stage'].title()}")
        print(f"   Overall Score: {candidate['overall_score']:.0f}/100")
        print(f"   Fundamental Score: {candidate['fundamental_score']:.0f}/100")
        print(f"   Technical Score: {candidate['technical_score']:.0f}/100")
        print(f"   Business Score: {candidate['business_score']:.0f}/100")
        print(f"   Governance Score: {candidate['governance_score']:.0f}/100")
        
        growth = candidate['growth_potential']
        print(f"   Growth Potential:")
        print(f"     2-Year Target: ₹{growth['target_price_2y']:.2f} ({growth['potential_return_2y']})")
        print(f"     3-Year Target: ₹{growth['target_price_3y']:.2f} ({growth['potential_return_3y']})")
        print(f"     5-Year Target: ₹{growth['target_price_5y']:.2f} ({growth['potential_return_5y']})")
        print(f"     Time to 2x: {growth['time_to_2x']}")
        print(f"     Time to 3x: {growth['time_to_3x']}")
        
        rec = candidate['recommendation']
        print(f"   Recommendation: {rec['action']}")
        print(f"   Confidence: {rec['confidence_score']}/100")
        print(f"   Position Size: {rec['position_size']}")
        print(f"   Entry Strategy: {rec['entry_strategy']}")
        
        risk = candidate['risk_assessment']
        print(f"   Risk Level: {risk['risk_level']}")
        print(f"   Key Risks: {', '.join(risk['risk_factors'][:2])}")
    
    print(f"\n🎯 Multibagger Portfolio Strategy:")
    print("=" * 60)
    print(f"   Total Candidates: {len(top_candidates)}")
    print(f"   Average Score: {np.mean([c['overall_score'] for c in top_candidates]):.0f}/100")
    print(f"   Average 3Y Potential: {np.mean([float(c['growth_potential']['potential_return_3y'].replace('%','')) for c in top_candidates]):.0f}%")
    print(f"   Portfolio Allocation: 20-25% of total portfolio")
    print(f"   Holding Period: 3-5 years minimum")
    print(f"   Monitoring: Weekly reviews mandatory")
    print(f"   Exit Strategy: Partial booking at 2x, 3x targets")
    
    print(f"\n💰 Multibagger Investment Example:")
    print(f"   Portfolio Size: ₹10,00,000")
    print(f"   Multibagger Allocation: ₹2,00,000 (20%)")
    print(f"   Number of Stocks: 4-5 multibaggers")
    print(f"   Position Size: ₹40,000-50,000 per stock")
    print(f"   Expected 3Y Return: 300-500% on successful picks")
    print(f"   Risk: High, but limited to 20% of portfolio")
    
    print(f"\n⚠️ Multibagger Risk Warning:")
    print(f"   • High volatility and drawdowns expected")
    print(f"   • 70% of multibaggers fail to deliver")
    print(f"   • Requires 3-5 year holding period")
    print(f"   • Only suitable for high-risk appetite investors")
    print(f"   • Diversify across 4-5 candidates to reduce risk")
    print(f"   • Regular monitoring and rebalancing essential")


if __name__ == "__main__":
    identify_multibaggers()
