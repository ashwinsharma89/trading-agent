"""
Learning Engine for Multi-Agent System
Tracks predictions, evaluates accuracy, and retrains models
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import numpy as np
from collections import defaultdict

from stock_agents.orchestrator import MultiAgentOrchestrator
from market_data_fetcher import MarketDataFetcher


class LearningEngine:
    """
    Manages the learning loop for the multi-agent system
    """
    
    def __init__(self, data_dir='data/learning'):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.predictions_file = f'{data_dir}/predictions.json'
        self.accuracy_file = f'{data_dir}/accuracy_history.json'
        self.weights_file = f'{data_dir}/agent_weights.json'
        
        self.predictions = self._load_predictions()
        self.accuracy_history = self._load_accuracy_history()
        self.fetcher = MarketDataFetcher()
        
    def _load_predictions(self) -> List[Dict]:
        """Load saved predictions"""
        if os.path.exists(self.predictions_file):
            with open(self.predictions_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_predictions(self):
        """Save predictions to disk"""
        with open(self.predictions_file, 'w') as f:
            json.dump(self.predictions, f, indent=2, default=str)
    
    def _load_accuracy_history(self) -> List[Dict]:
        """Load accuracy history"""
        if os.path.exists(self.accuracy_file):
            with open(self.accuracy_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_accuracy_history(self):
        """Save accuracy history"""
        with open(self.accuracy_file, 'w') as f:
            json.dump(self.accuracy_history, f, indent=2, default=str)
    
    def track_prediction(self, ticker: str, analysis: Dict[str, Any]):
        """
        Track a prediction for future evaluation
        
        Args:
            ticker: Stock ticker
            analysis: Complete analysis from orchestrator
        """
        prediction = {
            'id': len(self.predictions) + 1,
            'timestamp': datetime.now().isoformat(),
            'ticker': ticker,
            'entry_price': analysis['final_recommendation']['entry_price'],
            'recommendation': analysis['final_recommendation']['recommendation'],
            'composite_score': analysis['composite_score'],
            'confidence': analysis['confidence'],
            'agent_scores': {
                'technical': analysis['technical_output']['strength'],
                'fundamental': analysis['fundamental_output']['strength'],
                'risk': analysis['risk_output']['strength'],
                'market_context': analysis['market_context_output']['strength']
            },
            'agent_signals': {
                'technical': analysis['technical_output']['signal'],
                'fundamental': analysis['fundamental_output']['signal'],
                'risk': analysis['risk_output']['signal'],
                'market_context': analysis['market_context_output']['signal']
            },
            'targets': analysis['final_recommendation']['targets'],
            'stop_loss': analysis['final_recommendation']['stop_loss'],
            'evaluation_date': (datetime.now() + timedelta(days=30)).isoformat(),
            'evaluated': False
        }
        
        self.predictions.append(prediction)
        self._save_predictions()
        
        print(f"✅ Tracked prediction #{prediction['id']} for {ticker}")
        return prediction['id']
    
    def evaluate_predictions(self, min_days: int = 30) -> Dict[str, Any]:
        """
        Evaluate predictions that are old enough
        
        Args:
            min_days: Minimum days before evaluation
            
        Returns:
            Evaluation summary
        """
        print(f"\n🔍 EVALUATING PREDICTIONS (min {min_days} days old)")
        print("="*80)
        
        evaluated_count = 0
        correct_count = 0
        agent_performance = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        for pred in self.predictions:
            if pred['evaluated']:
                continue
            
            # Check if old enough
            pred_date = datetime.fromisoformat(pred['timestamp'])
            days_elapsed = (datetime.now() - pred_date).days
            
            if days_elapsed < min_days:
                continue
            
            ticker = pred['ticker']
            print(f"\n📊 Evaluating {ticker} (Day {days_elapsed})...")
            
            try:
                # Fetch current price
                current_data = self.fetcher.fetch_stock_data(ticker, period="1d", interval="1d")
                if not current_data:
                    print(f"   ❌ No data available")
                    continue
                
                current_price = current_data['price']
                entry_price = pred['entry_price']
                
                # Calculate actual return
                actual_return = ((current_price - entry_price) / entry_price) * 100
                
                # Calculate expected return based on composite score
                # Score 50 = 0%, Score 75 = 15%, Score 100 = 30%
                expected_return = (pred['composite_score'] - 50) * 0.6
                
                # Calculate error
                error_margin = abs(actual_return - expected_return) / max(abs(expected_return), 1)
                
                # Determine if correct (within 30% margin)
                is_correct = error_margin < 0.3
                
                if is_correct:
                    correct_count += 1
                
                # Evaluate each agent
                for agent_name, signal in pred['agent_signals'].items():
                    agent_performance[agent_name]['total'] += 1
                    
                    # Agent was correct if:
                    # - Predicted BUY and stock went up
                    # - Predicted SELL and stock went down
                    # - Predicted HOLD and stock stayed flat
                    
                    agent_correct = False
                    if 'BUY' in signal and actual_return > 5:
                        agent_correct = True
                    elif 'SELL' in signal and actual_return < -5:
                        agent_correct = True
                    elif signal == 'HOLD' and -5 <= actual_return <= 5:
                        agent_correct = True
                    elif signal in ['ACCEPTABLE', 'NEUTRAL', 'FAVORABLE']:
                        agent_correct = True  # Risk/Market agents are harder to judge
                    
                    if agent_correct:
                        agent_performance[agent_name]['correct'] += 1
                
                # Update prediction
                pred['evaluated'] = True
                pred['evaluation_date'] = datetime.now().isoformat()
                pred['current_price'] = current_price
                pred['actual_return'] = actual_return
                pred['expected_return'] = expected_return
                pred['error_margin'] = error_margin
                pred['is_correct'] = is_correct
                
                evaluated_count += 1
                
                # Print result
                status = "✅" if is_correct else "❌"
                print(f"   {status} Expected: {expected_return:+.1f}%, Actual: {actual_return:+.1f}%, Error: {error_margin*100:.1f}%")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Save updated predictions
        self._save_predictions()
        
        # Calculate overall accuracy
        if evaluated_count > 0:
            overall_accuracy = (correct_count / evaluated_count) * 100
        else:
            overall_accuracy = 0
        
        # Calculate per-agent accuracy
        agent_accuracy = {}
        for agent, perf in agent_performance.items():
            if perf['total'] > 0:
                agent_accuracy[agent] = (perf['correct'] / perf['total']) * 100
            else:
                agent_accuracy[agent] = 0
        
        # Save to history
        evaluation_summary = {
            'timestamp': datetime.now().isoformat(),
            'evaluated_count': evaluated_count,
            'correct_count': correct_count,
            'overall_accuracy': overall_accuracy,
            'agent_accuracy': agent_accuracy
        }
        
        self.accuracy_history.append(evaluation_summary)
        self._save_accuracy_history()
        
        # Print summary
        print(f"\n{'='*80}")
        print(f"📊 EVALUATION SUMMARY")
        print(f"{'='*80}")
        print(f"Evaluated: {evaluated_count} predictions")
        print(f"Correct: {correct_count}")
        print(f"Overall Accuracy: {overall_accuracy:.1f}%")
        print(f"\n🤖 Agent Accuracy:")
        for agent, acc in sorted(agent_accuracy.items(), key=lambda x: x[1], reverse=True):
            print(f"   {agent:20} {acc:.1f}%")
        
        # Check if retraining needed
        if overall_accuracy < 70 and evaluated_count >= 10:
            print(f"\n⚠️  Accuracy below 70% - Retraining recommended!")
            self.optimize_weights(agent_accuracy)
        
        return evaluation_summary
    
    def optimize_weights(self, agent_accuracy: Dict[str, float]):
        """
        Optimize agent weights based on accuracy
        
        Args:
            agent_accuracy: Dict of agent accuracies
        """
        print(f"\n🔄 OPTIMIZING AGENT WEIGHTS")
        print("="*80)
        
        # Load current weights
        orchestrator = MultiAgentOrchestrator()
        current_weights = orchestrator.weights
        
        print(f"\nCurrent weights:")
        for agent, weight in current_weights.items():
            print(f"   {agent:20} {weight:.2f}")
        
        # Calculate new weights based on accuracy
        # Higher accuracy = higher weight
        total_accuracy = sum(agent_accuracy.values())
        
        if total_accuracy == 0:
            print("⚠️  No accuracy data, keeping current weights")
            return current_weights
        
        new_weights = {}
        for agent in current_weights.keys():
            if agent in agent_accuracy:
                # Proportional to accuracy
                new_weights[agent] = agent_accuracy[agent] / total_accuracy
            else:
                new_weights[agent] = current_weights[agent]
        
        # Normalize to sum to 1.0
        total = sum(new_weights.values())
        new_weights = {k: v/total for k, v in new_weights.items()}
        
        print(f"\nOptimized weights:")
        for agent, weight in new_weights.items():
            change = weight - current_weights[agent]
            arrow = "↑" if change > 0 else "↓" if change < 0 else "→"
            print(f"   {agent:20} {weight:.2f} ({arrow} {abs(change):.2f})")
        
        # Save new weights
        with open(self.weights_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'weights': new_weights,
                'agent_accuracy': agent_accuracy
            }, f, indent=2)
        
        print(f"\n✅ New weights saved to {self.weights_file}")
        print(f"💡 Update orchestrator to use new weights:")
        print(f"   orchestrator = MultiAgentOrchestrator(weights={new_weights})")
        
        return new_weights
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        total = len(self.predictions)
        evaluated = sum(1 for p in self.predictions if p['evaluated'])
        correct = sum(1 for p in self.predictions if p.get('is_correct', False))
        
        if evaluated > 0:
            accuracy = (correct / evaluated) * 100
        else:
            accuracy = 0
        
        # Get accuracy trend
        if len(self.accuracy_history) >= 2:
            first_acc = self.accuracy_history[0]['overall_accuracy']
            latest_acc = self.accuracy_history[-1]['overall_accuracy']
            improvement = latest_acc - first_acc
        else:
            improvement = 0
        
        return {
            'total_predictions': total,
            'evaluated': evaluated,
            'correct': correct,
            'accuracy': accuracy,
            'improvement': improvement,
            'learning_iterations': len(self.accuracy_history)
        }
    
    def print_dashboard(self):
        """Print learning dashboard"""
        stats = self.get_learning_stats()
        
        print(f"\n{'='*80}")
        print(f"🧠 LEARNING SYSTEM DASHBOARD")
        print(f"{'='*80}\n")
        
        print(f"📊 Overall Performance:")
        print(f"   Total Predictions: {stats['total_predictions']}")
        print(f"   Evaluated: {stats['evaluated']}")
        print(f"   Correct: {stats['correct']}")
        print(f"   Accuracy: {stats['accuracy']:.1f}%")
        print(f"   Improvement: {stats['improvement']:+.1f}%")
        print(f"   Learning Iterations: {stats['learning_iterations']}")
        
        if self.accuracy_history:
            latest = self.accuracy_history[-1]
            print(f"\n🤖 Latest Agent Performance:")
            for agent, acc in sorted(latest['agent_accuracy'].items(), key=lambda x: x[1], reverse=True):
                print(f"   {agent:20} {acc:.1f}%")
        
        # Pending evaluations
        pending = sum(1 for p in self.predictions if not p['evaluated'])
        if pending > 0:
            print(f"\n⏳ Pending Evaluations: {pending}")
            
            # Show next evaluation date
            next_eval = None
            for p in self.predictions:
                if not p['evaluated']:
                    eval_date = datetime.fromisoformat(p['evaluation_date'])
                    if next_eval is None or eval_date < next_eval:
                        next_eval = eval_date
            
            if next_eval:
                days_until = (next_eval - datetime.now()).days
                print(f"   Next evaluation in: {days_until} days")


if __name__ == "__main__":
    # Example usage
    engine = LearningEngine()
    
    # Show dashboard
    engine.print_dashboard()
    
    # Evaluate predictions
    if len(engine.predictions) > 0:
        print("\n" + "="*80)
        engine.evaluate_predictions(min_days=1)  # Use 1 day for testing
