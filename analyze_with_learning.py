#!/usr/bin/env python3
"""
Stock Analysis with Learning
Analyzes stocks and tracks predictions for continuous learning
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stock_agents.orchestrator import MultiAgentOrchestrator
from learning_engine import LearningEngine


def main():
    if len(sys.argv) < 2:
        print("\n🧠 Stock Analysis with Learning")
        print("="*80)
        print("\nUsage:")
        print("  python3 analyze_with_learning.py <TICKER> [strategy]")
        print("  python3 analyze_with_learning.py --evaluate")
        print("  python3 analyze_with_learning.py --dashboard")
        print("\nExamples:")
        print("  python3 analyze_with_learning.py KPIGREEN")
        print("  python3 analyze_with_learning.py --evaluate")
        print("  python3 analyze_with_learning.py --dashboard")
        sys.exit(1)
    
    # Initialize learning engine
    engine = LearningEngine()
    
    # Handle commands
    command = sys.argv[1]
    
    if command == '--evaluate':
        # Evaluate past predictions
        engine.evaluate_predictions(min_days=30)
        
    elif command == '--dashboard':
        # Show learning dashboard
        engine.print_dashboard()
        
    elif command == '--test-evaluate':
        # Test evaluation with 1 day (for testing)
        engine.evaluate_predictions(min_days=1)
        
    else:
        # Analyze stock
        ticker = sys.argv[1].upper()
        strategy = sys.argv[2] if len(sys.argv) > 2 else 'swing'
        
        # Load optimized weights if available
        weights_file = 'data/learning/agent_weights.json'
        if os.path.exists(weights_file):
            import json
            with open(weights_file, 'r') as f:
                weights_data = json.load(f)
                weights = weights_data['weights']
                print(f"\n✅ Using optimized weights from learning")
                orchestrator = MultiAgentOrchestrator(weights=weights)
        else:
            print(f"\n📊 Using default weights (no learning data yet)")
            orchestrator = MultiAgentOrchestrator()
        
        try:
            # Analyze
            print(f"\n🤖 Analyzing {ticker}...")
            analysis = orchestrator.analyze(ticker, strategy)
            
            # Track prediction
            pred_id = engine.track_prediction(ticker, analysis)
            
            # Generate and print report
            report = orchestrator.generate_report(analysis)
            print(report)
            
            # Show learning stats
            print(f"\n{'='*80}")
            print(f"🧠 LEARNING STATUS")
            print(f"{'='*80}")
            stats = engine.get_learning_stats()
            print(f"Total Predictions Tracked: {stats['total_predictions']}")
            print(f"Evaluated: {stats['evaluated']}")
            print(f"Current Accuracy: {stats['accuracy']:.1f}%")
            if stats['improvement'] != 0:
                print(f"Improvement: {stats['improvement']:+.1f}%")
            print(f"\n💡 This prediction will be evaluated in 30 days")
            print(f"   Run: python3 analyze_with_learning.py --evaluate")
            
        except Exception as e:
            print(f"\n❌ Analysis failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
