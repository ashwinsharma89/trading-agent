"""
Fundamental Analysis Agent
Analyzes financial metrics, ratios, growth, and quality
"""

from typing import Dict, Any
from stock_agents.base_agent import BaseAgent
from fundamental_analyzer import FundamentalAnalyzer
import logging

logger = logging.getLogger(__name__)


class FundamentalAgent(BaseAgent):
    """
    Specialized agent for fundamental analysis
    """
    
    def __init__(self, weight: float = 0.30):
        super().__init__("Fundamental Analysis Agent", weight)
        self.analyzer = FundamentalAnalyzer()
        
    def analyze(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive fundamental analysis
        """
        self.validate_state(state, ['ticker'])
        
        ticker = state['ticker']
        
        # Fetch fundamentals if not already in state
        if 'fundamental_data' not in state:
            fundamental_data = self.analyzer.analyze(ticker, "NSE")
            state['fundamental_data'] = fundamental_data
        else:
            fundamental_data = state['fundamental_data']
        
        if not fundamental_data:
            raise ValueError(f"No fundamental data available for {ticker}")
        
        # Extract metrics
        roe = fundamental_data.get('roe', 0)
        revenue_growth = fundamental_data.get('revenue_growth', 0)
        earnings_growth = fundamental_data.get('earnings_growth', 0)
        pe_ratio = fundamental_data.get('pe_ratio', 20)
        pb_ratio = fundamental_data.get('pb_ratio', 1)
        debt_to_equity = fundamental_data.get('debt_to_equity', 0)
        current_ratio = fundamental_data.get('current_ratio', 1)
        profit_margin = fundamental_data.get('profit_margin', 0)
        quality_score = fundamental_data.get('overall_quality', 50)
        dividend_yield = fundamental_data.get('dividend_yield', 0)
        payout_ratio = fundamental_data.get('payout_ratio', 0)
        free_cashflow = fundamental_data.get('free_cashflow', 0)
        peg_ratio = fundamental_data.get('peg_ratio', 0)
        fifty_two_week_high = fundamental_data.get('fifty_two_week_high', 0)
        fifty_two_week_low = fundamental_data.get('fifty_two_week_low', 0)
        quality_scores = fundamental_data.get('quality_scores', {})
        profitability_q = quality_scores.get('Profitability', 0)
        growth_q = quality_scores.get('Growth', 0)
        leverage_q = quality_scores.get('Leverage', 0)
        valuation_q = quality_scores.get('Valuation', 0)
        dividend_q = quality_scores.get('Dividend', 0)
        analyst_reco = fundamental_data.get('recommendation', 'none')
        analyst_count = fundamental_data.get('number_of_analyst_opinions', 0)
        
        # Scoring logic
        score = 0
        reasoning = []
        
        # ROE Analysis (0-20 points)
        if roe > 20:
            score += 20
            reasoning.append(f"✅ Excellent ROE at {roe:.1f}%")
        elif roe > 15:
            score += 15
            reasoning.append(f"✅ Strong ROE at {roe:.1f}%")
        elif roe > 10:
            score += 10
            reasoning.append(f"Good ROE at {roe:.1f}%")
        elif roe > 5:
            score += 5
            reasoning.append(f"⚠️ Moderate ROE at {roe:.1f}%")
        else:
            score -= 10
            reasoning.append(f"⚠️ Weak ROE at {roe:.1f}%")
        
        # Revenue Growth (0-20 points)
        if revenue_growth > 30:
            score += 20
            reasoning.append(f"✅ Exceptional revenue growth {revenue_growth:.1f}%")
        elif revenue_growth > 20:
            score += 15
            reasoning.append(f"✅ Strong revenue growth {revenue_growth:.1f}%")
        elif revenue_growth > 10:
            score += 10
            reasoning.append(f"✅ Healthy revenue growth {revenue_growth:.1f}%")
        elif revenue_growth > 0:
            score += 5
            reasoning.append(f"Positive revenue growth {revenue_growth:.1f}%")
        else:
            score -= 15
            reasoning.append(f"⚠️ Negative revenue growth {revenue_growth:.1f}%")
        
        # Earnings Growth (0-15 points)
        if earnings_growth > 25:
            score += 15
            reasoning.append(f"✅ Strong earnings growth {earnings_growth:.1f}%")
        elif earnings_growth > 15:
            score += 10
            reasoning.append(f"✅ Good earnings growth {earnings_growth:.1f}%")
        elif earnings_growth > 5:
            score += 5
            reasoning.append(f"Moderate earnings growth {earnings_growth:.1f}%")
        elif earnings_growth < 0:
            score -= 10
            reasoning.append(f"⚠️ Negative earnings growth {earnings_growth:.1f}%")
        
        # Valuation (0-15 points)
        if pe_ratio < 15:
            score += 15
            reasoning.append(f"✅ Undervalued P/E at {pe_ratio:.1f}")
        elif pe_ratio < 25:
            score += 10
            reasoning.append(f"Fair P/E at {pe_ratio:.1f}")
        elif pe_ratio < 40:
            score += 5
            reasoning.append(f"⚠️ Elevated P/E at {pe_ratio:.1f}")
        else:
            score -= 10
            reasoning.append(f"⚠️ Very high P/E at {pe_ratio:.1f}")
        
        if pb_ratio < 3:
            score += 5
            reasoning.append(f"✅ Reasonable P/B at {pb_ratio:.1f}")
        elif pb_ratio > 5:
            score -= 5
            reasoning.append(f"⚠️ High P/B at {pb_ratio:.1f}")
        
        # Financial Health (0-15 points)
        if debt_to_equity < 0.5:
            score += 10
            reasoning.append(f"✅ Low debt/equity at {debt_to_equity:.2f}")
        elif debt_to_equity < 1.0:
            score += 5
            reasoning.append(f"Manageable debt/equity at {debt_to_equity:.2f}")
        elif debt_to_equity > 2.0:
            score -= 10
            reasoning.append(f"⚠️ High debt/equity at {debt_to_equity:.2f}")
        
        if current_ratio > 1.5:
            score += 5
            reasoning.append(f"✅ Strong liquidity, current ratio {current_ratio:.2f}")
        elif current_ratio < 1.0:
            score -= 5
            reasoning.append(f"⚠️ Weak liquidity, current ratio {current_ratio:.2f}")
        
        # Profitability (0-10 points)
        if profit_margin > 15:
            score += 10
            reasoning.append(f" High profit margin {profit_margin:.1f}%")
        elif profit_margin > 10:
            score += 7
            reasoning.append(f" Good profit margin {profit_margin:.1f}%")
        elif profit_margin > 5:
            score += 5
            reasoning.append(f"Moderate profit margin {profit_margin:.1f}%")
        elif profit_margin < 0:
            score -= 10
            reasoning.append(f" Negative profit margin {profit_margin:.1f}%")

        # --- Value Investing Layer (growth- and PEG-aware) ---
        value_score = 0
        high_growth = (revenue_growth > 20) or (earnings_growth > 20)

        # Moat / resilience proxies
        if profitability_q >= 70:
            value_score += 12
            reasoning.append("\u0008\u0008 Strong profitability suggests durable moat")
        elif 0 < profitability_q <= 40:
            value_score -= 5
            reasoning.append("\u0008\u0008 Weak profitability limits competitive advantage")

        if leverage_q >= 80:
            value_score += 5
            reasoning.append("\u0008\u0008 Balance sheet strength supports resilience")
        elif leverage_q <= 60 and debt_to_equity > 1.5:
            value_score -= 5
            reasoning.append("\u0008\u0008 Higher leverage increases downside risk")

        if quality_score >= 80:
            value_score += 5
            reasoning.append("\u0008\u0008 Overall quality aligns with high-grade franchise")
        elif quality_score < 50:
            value_score -= 5
            reasoning.append("\u0008\u0008 Overall quality below value-investor comfort zone")

        # Valuation: growth-adjusted
        if pe_ratio > 0:
            if high_growth:
                # For fast-growing sectors, accept higher P/E before penalizing
                if pe_ratio < 30:
                    value_score += 4
                    reasoning.append("\u0008\u0008 Growth supports P/E premium (fast-growing franchise)")
                elif pe_ratio > 45 and (peg_ratio == 0 or peg_ratio > 2):
                    value_score -= 8
                    reasoning.append("\u0008\u0008 Very rich P/E not matched by PEG/growth")
            else:
                # Classic value thresholds for mature/slower sectors
                if pe_ratio < 15:
                    value_score += 8
                    reasoning.append("\u0008\u0008 Margin of safety: P/E below 15")
                elif pe_ratio > 35:
                    value_score -= 8
                    reasoning.append("\u0008\u0008 Rich P/E leaves little margin of safety")

        # PEG awareness (when available)
        if peg_ratio and peg_ratio > 0:
            if peg_ratio <= 1.5:
                value_score += 3
                reasoning.append("\u0008\u0008 PEG ratio reasonable relative to growth")
            elif peg_ratio > 2.5:
                value_score -= 4
                reasoning.append("\u0008\u0008 PEG ratio stretched; expectations high")

        # Price-to-book – asset-heavy vs asset-light
        if pb_ratio > 0:
            if pb_ratio < 1:
                value_score += 6
                reasoning.append("\u0008\u0008 Trading below book value suggests potential value opportunity")
            elif pb_ratio > 4:
                value_score -= 4
                reasoning.append("\u0008\u0008 High price-to-book implies elevated expectations")

        # Contrarian value: low expectations, real earnings
        if (
            pe_ratio > 0
            and pe_ratio < 12
            and revenue_growth > 0
            and earnings_growth > 0
            and quality_score >= 60
        ):
            value_score += 8
            reasoning.append("\u0008\u0008 Contrarian value: low P/E, positive growth, solid quality")

        # Story-stock risk: very high P/E without earnings support
        if pe_ratio > 45 and earnings_growth <= 0:
            value_score -= 10
            reasoning.append("\u0008\u0008 Story stock risk: very high P/E without earnings support")

        # Cash generation & capital allocation
        if free_cashflow and free_cashflow > 0:
            value_score += 4
            reasoning.append("\u0008\u0008 Positive free cash flow supports shareholder value")

        if 0 < payout_ratio < 60:
            value_score += 3
            reasoning.append("\u0008\u0008 Balanced payout ratio indicates sensible capital allocation")
        elif payout_ratio > 80:
            value_score -= 4
            reasoning.append("\u0008\u0008 Very high payout ratio may limit reinvestment capacity")
        value_score = max(-20, min(20, value_score))
        score += value_score
        
        # Quality Score (0-5 points)
        score += (quality_score / 100) * 5
        
        # Normalize score to 0-100
        score = max(0, min(100, score))
        
        # Determine signal
        if score >= 75:
            signal = 'STRONG_BUY'
        elif score >= 60:
            signal = 'BUY'
        elif score >= 40:
            signal = 'HOLD'
        elif score >= 25:
            signal = 'SELL'
        else:
            signal = 'STRONG_SELL'
        
        # Confidence based on data quality
        confidence = int(quality_score)
        
        return {
            'signal': signal,
            'strength': int(score),
            'confidence': confidence,
            'reasoning': reasoning,
            'metrics': {
                'roe': roe,
                'revenue_growth': revenue_growth,
                'earnings_growth': earnings_growth,
                'pe_ratio': pe_ratio,
                'pb_ratio': pb_ratio,
                'debt_to_equity': debt_to_equity,
                'current_ratio': current_ratio,
                'profit_margin': profit_margin,
                'quality_score': quality_score,
                'dividend_yield': dividend_yield,
                'payout_ratio': payout_ratio,
                'free_cashflow': free_cashflow,
                'value_investing_score': value_score
            }
        }
