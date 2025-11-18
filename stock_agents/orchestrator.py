"""
Orchestrator Agent using LangGraph
Coordinates all agents and aggregates their outputs
"""

from typing import Dict, Any, TypedDict, Annotated
from typing_extensions import TypedDict
import operator
from langgraph.graph import StateGraph, END
from stock_agents.technical_agent import TechnicalAgent
from stock_agents.fundamental_agent import FundamentalAgent
from stock_agents.risk_agent import RiskAgent
from stock_agents.market_context_agent import MarketContextAgent
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class AnalysisState(TypedDict):
    """
    Shared state passed between agents
    """
    # Input
    ticker: str
    strategy: str  # 'swing' or 'long_term'
    
    # Data
    market_data: Dict[str, Any]
    fundamental_data: Dict[str, Any]
    
    # Agent outputs
    technical_output: Dict[str, Any]
    fundamental_output: Dict[str, Any]
    risk_output: Dict[str, Any]
    market_context_output: Dict[str, Any]
    
    # Final result
    final_recommendation: Dict[str, Any]
    composite_score: int
    confidence: int
    
    # Metadata
    execution_log: Annotated[list, operator.add]
    evaluation_metrics: Dict[str, Any]
    trace: Dict[str, Any]


class MultiAgentOrchestrator:
    """
    Orchestrates multiple specialized agents using LangGraph
    """
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize orchestrator with agent weights
        
        Args:
            weights: Dict of agent weights, defaults to balanced
        """
        if weights is None:
            weights = {
                'technical': 0.35,
                'fundamental': 0.30,
                'risk': 0.20,
                'market_context': 0.15
            }
        
        self.weights = weights
        
        # Initialize agents
        self.technical_agent = TechnicalAgent(weight=weights['technical'])
        self.fundamental_agent = FundamentalAgent(weight=weights['fundamental'])
        self.risk_agent = RiskAgent(weight=weights['risk'])
        self.market_context_agent = MarketContextAgent(weight=weights['market_context'])
        
        # Build workflow
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        """
        Build LangGraph workflow
        """
        workflow = StateGraph(AnalysisState)
        
        # Add nodes
        workflow.add_node("technical", self._run_technical)
        workflow.add_node("fundamental", self._run_fundamental)
        workflow.add_node("market_context", self._run_market_context)
        workflow.add_node("risk", self._run_risk)
        workflow.add_node("aggregate", self._aggregate_results)
        
        # Define edges
        workflow.set_entry_point("technical")
        workflow.add_edge("technical", "fundamental")
        workflow.add_edge("fundamental", "market_context")
        workflow.add_edge("market_context", "risk")
        workflow.add_edge("risk", "aggregate")
        workflow.add_edge("aggregate", END)
        
        return workflow.compile()
    
    def _run_technical(self, state: AnalysisState) -> AnalysisState:
        """Run technical analysis agent"""
        result = self.technical_agent.execute(state)
        state['technical_output'] = result
        logs = state.get('execution_log', [])
        logs.append(f"✅ Technical Agent: {result['signal']} ({result['strength']}/100)")
        state['execution_log'] = logs
        return state
    
    def _run_fundamental(self, state: AnalysisState) -> AnalysisState:
        """Run fundamental analysis agent"""
        result = self.fundamental_agent.execute(state)
        state['fundamental_output'] = result
        logs = state.get('execution_log', [])
        logs.append(f"✅ Fundamental Agent: {result['signal']} ({result['strength']}/100)")
        state['execution_log'] = logs
        return state
    
    def _run_market_context(self, state: AnalysisState) -> AnalysisState:
        """Run market context agent"""
        result = self.market_context_agent.execute(state)
        state['market_context_output'] = result
        logs = state.get('execution_log', [])
        logs.append(f"✅ Market Context Agent: {result['signal']} ({result['strength']}/100)")
        state['execution_log'] = logs
        return state
    
    def _run_risk(self, state: AnalysisState) -> AnalysisState:
        """Run risk assessment agent"""
        result = self.risk_agent.execute(state)
        state['risk_output'] = result
        logs = state.get('execution_log', [])
        logs.append(f"✅ Risk Agent: {result['signal']} ({result['strength']}/100)")
        state['execution_log'] = logs
        return state
    
    def _aggregate_results(self, state: AnalysisState) -> AnalysisState:
        """
        Aggregate all agent outputs and make final recommendation
        """
        tech = state['technical_output']
        fund = state['fundamental_output']
        risk = state['risk_output']
        market = state['market_context_output']
        
        # Calculate weighted composite score
        composite_score = (
            tech['strength'] * self.weights['technical'] +
            fund['strength'] * self.weights['fundamental'] +
            risk['strength'] * self.weights['risk'] +
            market['strength'] * self.weights['market_context']
        )
        
        # Calculate confidence (weighted average)
        confidence = (
            tech['confidence'] * self.weights['technical'] +
            fund['confidence'] * self.weights['fundamental'] +
            risk['confidence'] * self.weights['risk'] +
            market['confidence'] * self.weights['market_context']
        )
        
        # Conflict resolution
        signals = [tech['signal'], fund['signal'], risk['signal'], market['signal']]
        signal_counts = {}
        for sig in signals:
            signal_counts[sig] = signal_counts.get(sig, 0) + 1
        
        # Check for conflicts
        buy_signals = sum(1 for s in signals if 'BUY' in s)
        sell_signals = sum(1 for s in signals if 'SELL' in s)
        
        conflict_detected = False
        if buy_signals > 0 and sell_signals > 0:
            conflict_detected = True
            logger.warning(f"⚠️ Conflict detected: {buy_signals} BUY vs {sell_signals} SELL signals")
        
        # Determine final recommendation
        if composite_score >= 75 and not conflict_detected:
            recommendation = 'STRONG_BUY'
        elif composite_score >= 65:
            recommendation = 'BUY'
        elif composite_score >= 45 or conflict_detected:
            recommendation = 'HOLD'
        elif composite_score >= 35:
            recommendation = 'SELL'
        else:
            recommendation = 'STRONG_SELL'
        
        # If confidence is low, downgrade to HOLD
        if confidence < 60 and recommendation in ['STRONG_BUY', 'BUY']:
            recommendation = 'HOLD'
            logger.warning(f"⚠️ Low confidence ({confidence:.0f}%), downgrading to HOLD")
        
        # Evaluation metrics
        risk_level = risk.get('risk_level', 'UNKNOWN')
        if risk_level == 'LOW':
            risk_factor = 1.0
        elif risk_level == 'MEDIUM':
            risk_factor = 0.9
        elif risk_level == 'HIGH':
            risk_factor = 0.75
        elif risk_level == 'VERY_HIGH':
            risk_factor = 0.5
        else:
            risk_factor = 0.8
        risk_adjusted_score = composite_score * risk_factor
        evaluation_metrics = {
            'technical_strength': tech['strength'],
            'fundamental_strength': fund['strength'],
            'risk_strength': risk['strength'],
            'market_context_strength': market['strength'],
            'composite_score': int(composite_score),
            'confidence': int(confidence),
            'risk_adjusted_score': int(risk_adjusted_score),
            'risk_level': risk_level,
            'risk_reward': risk['risk_reward'],
            'position_size_pct': risk['position_size'],
            'stop_loss_pct': risk['stop_loss_pct'],
            'conflict_detected': conflict_detected,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals
        }
        state['evaluation_metrics'] = evaluation_metrics
        
        # Trace block
        timestamp = datetime.now().isoformat()
        trace_id = f"{state['ticker']}-{timestamp}"
        trace = {
            'trace_id': trace_id,
            'ticker': state['ticker'],
            'strategy': state['strategy'],
            'timestamp': timestamp,
            'weights': self.weights,
            'agent_outputs': {
                'technical': tech,
                'fundamental': fund,
                'risk': risk,
                'market_context': market
            }
        }
        state['trace'] = trace
        
        # Build final recommendation
        state['final_recommendation'] = {
            'recommendation': recommendation,
            'composite_score': int(composite_score),
            'confidence': int(confidence),
            'conflict_detected': conflict_detected,
            'agent_consensus': {
                'technical': tech['signal'],
                'fundamental': fund['signal'],
                'risk': risk['signal'],
                'market_context': market['signal']
            },
            'entry_price': state['market_data']['price'],
            'stop_loss': risk['stop_loss'],
            'targets': risk['targets'],
            'position_size': risk['position_size'],
            'risk_reward': risk['risk_reward'],
            'risk_level': risk_level,
            'timestamp': timestamp,
            'trace_id': trace_id,
            'evaluation_metrics': evaluation_metrics,
            'trace': trace
        }
        
        state['composite_score'] = int(composite_score)
        state['confidence'] = int(confidence)
        logs = state.get('execution_log', [])
        logs.extend([
            f"🎯 Final Recommendation: {recommendation}",
            f"📊 Composite Score: {composite_score:.0f}/100",
            f"🎲 Confidence: {confidence:.0f}%"
        ])
        state['execution_log'] = logs
        
        return state
    
    def analyze(self, ticker: str, strategy: str = 'swing') -> Dict[str, Any]:
        """
        Analyze a stock using multi-agent system
        
        Args:
            ticker: Stock ticker symbol
            strategy: Trading strategy ('swing' or 'long_term')
            
        Returns:
            Complete analysis with recommendation
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"🤖 MULTI-AGENT ANALYSIS: {ticker}")
        logger.info(f"{'='*80}\n")
        
        # Initialize state
        initial_state = {
            'ticker': ticker,
            'strategy': strategy,
            'execution_log': []
        }
        
        # Run workflow
        try:
            final_state = self.workflow.invoke(initial_state)
            
            # Log execution
            for log in final_state.get('execution_log', []):
                logger.info(log)
            
            return final_state
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            raise
    
    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """
        Generate human-readable report from analysis
        """
        rec = analysis['final_recommendation']
        tech = analysis['technical_output']
        fund = analysis['fundamental_output']
        risk = analysis['risk_output']
        market = analysis['market_context_output']
        
        report = f"\n{'='*80}\n"
        report += f"📊 {analysis['ticker']} - MULTI-AGENT ANALYSIS REPORT\n"
        report += f"{'='*80}\n\n"
        
        # Recommendation
        report += f"🎯 RECOMMENDATION: {rec['recommendation']}\n"
        report += f"   Composite Score: {rec['composite_score']}/100\n"
        report += f"   Confidence: {rec['confidence']}%\n"
        report += f"   Risk Level: {rec['risk_level']}\n\n"
        
        # Trading Plan
        report += f"💰 TRADING PLAN:\n"
        report += f"   Entry: ₹{rec['entry_price']:.2f}\n"
        report += f"   Stop Loss: ₹{rec['stop_loss']:.2f} (-{risk['stop_loss_pct']:.1f}%)\n"
        report += f"   Target 1: ₹{rec['targets']['target1']:.2f}\n"
        report += f"   Target 2: ₹{rec['targets']['target2']:.2f}\n"
        report += f"   Target 3: ₹{rec['targets']['target3']:.2f}\n"
        report += f"   Position Size: {rec['position_size']}% of portfolio\n"
        report += f"   Risk/Reward: 1:{rec['risk_reward']:.1f}\n\n"
        
        # Agent Consensus
        report += f"🤖 AGENT CONSENSUS:\n"
        for agent, signal in rec['agent_consensus'].items():
            output = analysis[f'{agent}_output']
            report += f"   • {agent.title()}: {signal} ({output['strength']}/100)\n"
        
        if rec['conflict_detected']:
            report += f"\n   ⚠️ CONFLICT DETECTED - Agents disagree, proceed with caution\n"
        
        report += f"\n"
        
        # Key Reasons
        report += f"✅ KEY REASONS:\n"
        all_reasoning = []
        for output in [tech, fund, risk, market]:
            all_reasoning.extend(output['reasoning'][:2])  # Top 2 from each
        
        for reason in all_reasoning[:8]:  # Top 8 overall
            report += f"   {reason}\n"
        
        report += f"\n{'='*80}\n"
        
        return report


if __name__ == "__main__":
    # Test the orchestrator
    orchestrator = MultiAgentOrchestrator()
    
    test_stocks = ['KPIGREEN', 'RECLTD', 'SUZLON']
    
    for ticker in test_stocks:
        try:
            analysis = orchestrator.analyze(ticker, strategy='swing')
            report = orchestrator.generate_report(analysis)
            print(report)
        except Exception as e:
            print(f"❌ Failed to analyze {ticker}: {e}")
