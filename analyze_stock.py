#!/usr/bin/env python3
"""
Simple CLI to use the Multi-Agent Stock Analysis System
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stock_agents.orchestrator import MultiAgentOrchestrator


def main():
    if len(sys.argv) < 2:
        print("\n🤖 Multi-Agent Stock Analysis System")
        print("="*80)
        print("\nUsage:")
        print("  python3 analyze_stock.py <TICKER> [strategy]")
        print("\nExamples:")
        print("  python3 analyze_stock.py KPIGREEN")
        print("  python3 analyze_stock.py RECLTD swing")
        print("  python3 analyze_stock.py TCS long_term")
        print("\nStrategies: swing (default), long_term")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    strategy = sys.argv[2] if len(sys.argv) > 2 else 'swing'
    
    # Initialize orchestrator
    orchestrator = MultiAgentOrchestrator()
    
    try:
        # Analyze
        analysis = orchestrator.analyze(ticker, strategy)
        
        # Generate and print report
        report = orchestrator.generate_report(analysis)
        print(report)
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
