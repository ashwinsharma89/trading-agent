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
            reasoning.append(f"✅ High profit margin {profit_margin:.1f}%")
        elif profit_margin > 10:
            score += 7
            reasoning.append(f"✅ Good profit margin {profit_margin:.1f}%")
        elif profit_margin > 5:
            score += 5
            reasoning.append(f"Moderate profit margin {profit_margin:.1f}%")
        elif profit_margin < 0:
            score -= 10
            reasoning.append(f"⚠️ Negative profit margin {profit_margin:.1f}%")
        
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
                'quality_score': quality_score
            }
        }
