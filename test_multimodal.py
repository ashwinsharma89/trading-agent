#!/usr/bin/env python3
"""
Test multimodal learning components
"""

import sys
from earnings_call_analyzer import EarningsCallAnalyzer
from financial_report_analyzer import FinancialReportAnalyzer
from chart_pattern_recognizer import ChartPatternRecognizer


def test_earnings_call():
    """Test earnings call analyzer"""
    print("\n📞 Testing Earnings Call Analyzer")
    print("="*60)
    
    analyzer = EarningsCallAnalyzer()
    
    # Test with sample transcript
    sample_transcript = """
    Good morning everyone. We are pleased to report strong quarterly results.
    Revenue grew 76% year-over-year to 450 crores. Our renewable energy 
    segment continues to show exceptional growth. Management is confident 
    about future prospects. We see strong demand and are expanding capacity.
    The outlook remains positive with several new opportunities in the pipeline.
    """
    
    analysis = analyzer.analyze_transcript(sample_transcript, "KPIGREEN")
    
    print(f"✅ Sentiment: {analysis['sentiment']:.2f}")
    print(f"✅ Tone: {analysis['management_tone']}")
    print(f"✅ Confidence: {analysis['confidence']:.2f}")
    
    return analysis


def test_financial_report():
    """Test financial report analyzer"""
    print("\n📄 Testing Financial Report Analyzer")
    print("="*60)
    
    analyzer = FinancialReportAnalyzer()
    
    # Test metric extraction
    sample_text = """
    Revenue for the year stood at 1200 crore, up from 700 crore last year.
    Net profit was 150 crore compared to 85 crore. Total debt is 500 crore.
    Cash and equivalents: 300 crore. The company maintains strong fundamentals.
    """
    
    metrics = analyzer._extract_metrics(sample_text, "KPIGREEN")
    
    print(f"✅ Metrics extracted: {len(metrics)}")
    for key, value in metrics.items():
        print(f"   • {key}: {value:,.0f}")
    
    return metrics


def test_chart_patterns():
    """Test chart pattern recognizer"""
    print("\n📊 Testing Chart Pattern Recognizer")
    print("="*60)
    
    recognizer = ChartPatternRecognizer()
    
    # Test with sample price data (head and shoulders pattern)
    prices = [
        100, 102, 105, 103, 101,  # Left shoulder
        103, 108, 112, 115, 113,  # Head
        110, 107, 105, 107, 103,  # Right shoulder
        101, 99, 97
    ]
    
    dates = [f"2025-01-{i+1:02d}" for i in range(len(prices))]
    
    patterns = recognizer.recognize_patterns_from_data(prices, dates)
    
    print(f"✅ Patterns found: {len(patterns)}")
    for p in patterns:
        print(f"   • {p['pattern']} ({p['direction']})")
        print(f"     Confidence: {p['confidence']:.2f}")
        print(f"     Target: ₹{p['target']:.2f}")
    
    return patterns


def main():
    print("\n🧪 MULTIMODAL LEARNING COMPONENTS TEST")
    print("="*60)
    
    try:
        # Test all components
        earnings = test_earnings_call()
        report = test_financial_report()
        patterns = test_chart_patterns()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        
        print("\n📊 Summary:")
        print(f"   • Earnings Call: {earnings['sentiment']:.2f} sentiment")
        print(f"   • Financial Report: {len(report)} metrics extracted")
        print(f"   • Chart Patterns: {len(patterns)} patterns detected")
        
        print("\n💡 Ready to use multimodal learning!")
        print("   Run: python3 analyze_with_advanced_learning.py KPIGREEN")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
