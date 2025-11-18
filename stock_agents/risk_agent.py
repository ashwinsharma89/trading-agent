"""
Risk Assessment Agent
Calculates position sizing, stop-loss, risk-reward, and portfolio correlation
"""

from typing import Dict, Any
from stock_agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)


class RiskAgent(BaseAgent):
    """
    Specialized agent for risk assessment and position sizing
    """
    
    def __init__(self, weight: float = 0.20):
        super().__init__("Risk Assessment Agent", weight)
        
    def analyze(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform risk assessment and calculate position sizing
        """
        self.validate_state(state, ['ticker', 'market_data'])
        
        market_data = state['market_data']
        fundamental_data = state.get('fundamental_data', {})
        
        current_price = market_data['price']
        rsi = market_data['rsi']
        volume_ratio = market_data['volume_ratio']
        price_change = market_data['change_pct']
        
        quality_score = fundamental_data.get('overall_quality', 50)
        debt_to_equity = fundamental_data.get('debt_to_equity', 0)
        
        # Calculate ATR-based stop loss (simplified - using price volatility)
        # In production, calculate actual ATR from historical data
        volatility = abs(price_change) / 100
        atr_multiplier = 1.5
        stop_loss_pct = max(5, min(15, volatility * 100 * atr_multiplier))
        stop_loss_price = current_price * (1 - stop_loss_pct / 100)
        
        # Calculate targets (risk-reward based)
        target1_pct = stop_loss_pct * 1.5  # 1.5:1 R:R
        target2_pct = stop_loss_pct * 2.5  # 2.5:1 R:R
        target3_pct = stop_loss_pct * 4.0  # 4:1 R:R
        
        target1 = current_price * (1 + target1_pct / 100)
        target2 = current_price * (1 + target2_pct / 100)
        target3 = current_price * (1 + target3_pct / 100)
        
        # Position sizing based on risk
        base_position = 2.5  # Default 2.5% of portfolio
        
        # Adjust based on quality
        if quality_score > 75:
            position_size = base_position * 1.2  # Increase for high quality
        elif quality_score < 50:
            position_size = base_position * 0.7  # Reduce for low quality
        else:
            position_size = base_position
        
        # Adjust based on volatility
        if volatility > 0.05:  # High volatility
            position_size *= 0.8
        elif volatility < 0.02:  # Low volatility
            position_size *= 1.1
        
        # Cap position size
        position_size = min(position_size, 5.0)  # Max 5%
        position_size = max(position_size, 1.0)  # Min 1%
        
        # Risk scoring
        score = 70  # Start neutral
        reasoning = []
        
        # Quality-based risk
        if quality_score > 75:
            score += 15
            reasoning.append(f"✅ Low risk - High quality score {quality_score}/100")
        elif quality_score < 50:
            score -= 20
            reasoning.append(f"⚠️ High risk - Low quality score {quality_score}/100")
        
        # Debt risk
        if debt_to_equity < 0.5:
            score += 10
            reasoning.append(f"✅ Low debt risk {debt_to_equity:.2f}")
        elif debt_to_equity > 2.0:
            score -= 15
            reasoning.append(f"⚠️ High debt risk {debt_to_equity:.2f}")
        
        # Volatility risk
        if volatility > 0.05:
            score -= 10
            reasoning.append(f"⚠️ High volatility {volatility*100:.1f}%")
        elif volatility < 0.02:
            score += 5
            reasoning.append(f"✅ Low volatility {volatility*100:.1f}%")
        
        # Volume risk
        if volume_ratio < 0.5:
            score -= 10
            reasoning.append(f"⚠️ Low liquidity risk - volume {volume_ratio:.2f}x")
        elif volume_ratio > 1.5:
            score += 5
            reasoning.append(f"✅ Good liquidity - volume {volume_ratio:.2f}x")
        
        # RSI extremes (reversal risk)
        if rsi > 80 or rsi < 20:
            score -= 5
            reasoning.append(f"⚠️ Reversal risk - RSI at extreme {rsi:.1f}")
        
        # Normalize score
        score = max(0, min(100, score))
        
        # Determine risk level
        if score >= 75:
            risk_level = 'LOW'
            signal = 'ACCEPTABLE'
        elif score >= 60:
            risk_level = 'MEDIUM'
            signal = 'ACCEPTABLE'
        elif score >= 40:
            risk_level = 'HIGH'
            signal = 'CAUTION'
        else:
            risk_level = 'VERY_HIGH'
            signal = 'AVOID'
        
        # Risk-reward ratio
        avg_target = (target1 + target2 + target3) / 3
        risk_reward = (avg_target - current_price) / (current_price - stop_loss_price)
        
        return {
            'signal': signal,
            'strength': int(score),
            'confidence': int(score),
            'reasoning': reasoning,
            'risk_level': risk_level,
            'position_size': round(position_size, 2),
            'stop_loss': round(stop_loss_price, 2),
            'stop_loss_pct': round(stop_loss_pct, 2),
            'targets': {
                'target1': round(target1, 2),
                'target2': round(target2, 2),
                'target3': round(target3, 2)
            },
            'risk_reward': round(risk_reward, 2),
            'metrics': {
                'volatility': round(volatility * 100, 2),
                'quality_score': quality_score,
                'debt_to_equity': debt_to_equity
            }
        }
