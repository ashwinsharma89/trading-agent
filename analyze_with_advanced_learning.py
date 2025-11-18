#!/usr/bin/env python3
"""
Advanced Stock Analysis with Multimodal Learning
Includes: Earnings calls, Financial reports, Chart patterns
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stock_agents.orchestrator import MultiAgentOrchestrator
from learning_engine import LearningEngine
from earnings_call_analyzer import EarningsCallAnalyzer
from financial_report_analyzer import FinancialReportAnalyzer
from chart_pattern_recognizer import ChartPatternRecognizer
from market_data_fetcher import MarketDataFetcher


def main():
    if len(sys.argv) < 2:
        print("\n🧠 Advanced Stock Analysis with Multimodal Learning")
        print("="*80)
        print("\nUsage:")
        print("  python3 analyze_with_advanced_learning.py <TICKER>")
        print("\nExample:")
        print("  python3 analyze_with_advanced_learning.py KPIGREEN")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    
    print(f"\n🔍 ADVANCED ANALYSIS: {ticker}")
    print("="*80)
    
    # Initialize all engines
    orchestrator = MultiAgentOrchestrator()
    learning = LearningEngine()
    earnings_analyzer = EarningsCallAnalyzer()
    report_analyzer = FinancialReportAnalyzer()
    pattern_recognizer = ChartPatternRecognizer()
    data_fetcher = MarketDataFetcher()
    
    try:
        # 1. Traditional multi-agent analysis
        print("\n📊 Running multi-agent analysis...")
        analysis = orchestrator.analyze(ticker)
        
        # 2. Earnings call analysis
        print("\n📞 Analyzing earnings calls...")
        transcript = earnings_analyzer.fetch_transcript(ticker)
        earnings_analysis = earnings_analyzer.analyze_transcript(transcript, ticker)
        
        if earnings_analysis['available']:
            print(f"   ✅ Sentiment: {earnings_analysis['sentiment']:.2f}")
            print(f"   ✅ Tone: {earnings_analysis['management_tone']}")
            print(f"   ✅ Confidence: {earnings_analysis['confidence']:.2f}")
        else:
            print(f"   ⚠️  No earnings call transcript available")
        
        # 3. Financial report analysis
        print("\n📄 Analyzing financial reports...")
        report_analysis = report_analyzer.analyze_report(ticker)
        
        if report_analysis['available']:
            print(f"   ✅ Quality Score: {report_analysis['quality_score']}/100")
            print(f"   ✅ Metrics extracted: {len(report_analysis['metrics'])}")
        else:
            print(f"   ⚠️  No financial report available")
        
        # 4. Chart pattern recognition
        print("\n📊 Recognizing chart patterns...")
        market_data = data_fetcher.fetch_stock_data(ticker, period="6mo")
        
        if market_data:
            prices = market_data['historical']['Close'].tolist()
            dates = market_data['historical'].index.strftime('%Y-%m-%d').tolist()
            
            patterns = pattern_recognizer.recognize_patterns_from_data(prices, dates)
            
            if patterns:
                print(f"   ✅ Found {len(patterns)} patterns:")
                for p in patterns[:3]:  # Top 3
                    print(f"      • {p['pattern']} ({p['direction']}) - Confidence: {p['confidence']:.2f}")
            else:
                print(f"   ⚠️  No significant patterns detected")
        
        # 5. Combine all analyses
        print("\n🤖 Combining all insights...")
        
        combined_analysis = {
            **analysis,
            'earnings_call': earnings_analysis,
            'financial_report': report_analysis,
            'chart_patterns': patterns if market_data else []
        }
        
        # Calculate enhanced score
        enhanced_score = analysis['composite_score']
        
        # Adjust based on earnings sentiment
        if earnings_analysis['available']:
            sentiment_adjustment = (earnings_analysis['sentiment'] - 0.5) * 10
            enhanced_score += sentiment_adjustment
            print(f"   Earnings sentiment adjustment: {sentiment_adjustment:+.1f}")
        
        # Adjust based on report quality
        if report_analysis['available']:
            quality_adjustment = (report_analysis['quality_score'] - 50) * 0.2
            enhanced_score += quality_adjustment
            print(f"   Report quality adjustment: {quality_adjustment:+.1f}")
        
        # Adjust based on patterns
        if patterns:
            bullish_patterns = sum(1 for p in patterns if p['direction'] == 'bullish')
            bearish_patterns = sum(1 for p in patterns if p['direction'] == 'bearish')
            pattern_adjustment = (bullish_patterns - bearish_patterns) * 2
            enhanced_score += pattern_adjustment
            print(f"   Pattern adjustment: {pattern_adjustment:+.1f}")
        
        enhanced_score = max(0, min(100, enhanced_score))
        
        # Update recommendation based on enhanced score
        if enhanced_score >= 75:
            enhanced_recommendation = 'STRONG_BUY'
        elif enhanced_score >= 65:
            enhanced_recommendation = 'BUY'
        elif enhanced_score >= 45:
            enhanced_recommendation = 'HOLD'
        elif enhanced_score >= 35:
            enhanced_recommendation = 'SELL'
        else:
            enhanced_recommendation = 'STRONG_SELL'
        
        # 6. Generate enhanced report
        print("\n" + "="*80)
        print(f"📊 {ticker} - ENHANCED MULTI-MODAL ANALYSIS")
        print("="*80)
        
        print(f"\n🎯 ENHANCED RECOMMENDATION: {enhanced_recommendation}")
        print(f"   Original Score: {analysis['composite_score']}/100")
        print(f"   Enhanced Score: {enhanced_score:.0f}/100")
        print(f"   Confidence: {analysis['confidence']}%")
        
        print(f"\n💰 TRADING PLAN:")
        rec = analysis['final_recommendation']
        print(f"   Entry: ₹{rec['entry_price']:.2f}")
        print(f"   Stop Loss: ₹{rec['stop_loss']:.2f}")
        print(f"   Targets: ₹{rec['targets']['target1']:.2f}, ₹{rec['targets']['target2']:.2f}, ₹{rec['targets']['target3']:.2f}")
        print(f"   Position Size: {rec['position_size']:.1f}%")
        
        print(f"\n🤖 AGENT CONSENSUS:")
        for agent, output in [
            ('Technical', analysis['technical_output']),
            ('Fundamental', analysis['fundamental_output']),
            ('Risk', analysis['risk_output']),
            ('Market_Context', analysis['market_context_output'])
        ]:
            print(f"   • {agent}: {output['signal']} ({output['strength']}/100)")
        
        print(f"\n📊 ADDITIONAL INSIGHTS:")
        
        if earnings_analysis['available']:
            print(f"   📞 Earnings Call:")
            print(f"      Sentiment: {earnings_analysis['sentiment']:.2f} ({earnings_analysis['management_tone']})")
        
        if report_analysis['available']:
            print(f"   📄 Financial Report:")
            print(f"      Quality Score: {report_analysis['quality_score']}/100")
        
        if patterns:
            print(f"   📊 Chart Patterns:")
            for p in patterns[:2]:
                print(f"      • {p['pattern']} ({p['direction']}) - Target: ₹{p['target']:.2f}")
        
        # 7. Track prediction
        pred_id = learning.track_prediction(ticker, combined_analysis)
        
        print(f"\n{'='*80}")
        print(f"🧠 LEARNING STATUS")
        print(f"{'='*80}")
        stats = learning.get_learning_stats()
        print(f"Total Predictions: {stats['total_predictions']}")
        print(f"Evaluated: {stats['evaluated']}")
        print(f"Accuracy: {stats['accuracy']:.1f}%")
        print(f"\n💡 This prediction will be evaluated in 30 days")
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
