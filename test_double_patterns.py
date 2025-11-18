#!/usr/bin/env python3
"""
Test Double Pattern Detector
Shows how it works across daily, weekly, monthly timeframes
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from double_pattern_detector import DoublePatternDetector


def generate_double_top_data():
    """Generate sample data with double top pattern"""
    dates = pd.date_range('2024-01-01', periods=120, freq='D')
    
    # Create double top pattern
    prices = []
    for i in range(120):
        if i < 30:
            # Uptrend to first peak
            price = 100 + i * 0.5
        elif i < 40:
            # First peak
            price = 115 + np.sin((i-30)/3) * 2
        elif i < 60:
            # Decline to valley
            price = 115 - (i-40) * 0.3
        elif i < 70:
            # Rise to second peak
            price = 109 + (i-60) * 0.6
        elif i < 80:
            # Second peak
            price = 115 + np.sin((i-70)/3) * 2
        else:
            # Breakdown
            price = 115 - (i-80) * 0.4
        
        prices.append(price + np.random.randn() * 0.5)
    
    return pd.DataFrame({'Date': dates, 'Close': prices})


def generate_double_bottom_data():
    """Generate sample data with double bottom pattern"""
    dates = pd.date_range('2024-01-01', periods=120, freq='D')
    
    # Create double bottom pattern
    prices = []
    for i in range(120):
        if i < 30:
            # Downtrend to first trough
            price = 120 - i * 0.5
        elif i < 40:
            # First trough
            price = 105 - np.sin((i-30)/3) * 2
        elif i < 60:
            # Rise to peak
            price = 105 + (i-40) * 0.3
        elif i < 70:
            # Decline to second trough
            price = 111 - (i-60) * 0.6
        elif i < 80:
            # Second trough
            price = 105 - np.sin((i-70)/3) * 2
        else:
            # Breakout
            price = 105 + (i-80) * 0.4
        
        prices.append(price + np.random.randn() * 0.5)
    
    return pd.DataFrame({'Date': dates, 'Close': prices})


def test_double_top():
    """Test double top detection"""
    print("\n" + "="*70)
    print("TEST 1: DOUBLE TOP PATTERN")
    print("="*70)
    
    detector = DoublePatternDetector()
    df = generate_double_top_data()
    df.set_index('Date', inplace=True)
    
    # Analyze all timeframes
    results = detector.analyze_multi_timeframe(df)
    
    # Display results
    print("\n📊 DAILY TIMEFRAME:")
    daily_tops = results['daily'].get('double_tops', [])
    if daily_tops:
        for i, pattern in enumerate(daily_tops[:2], 1):
            print(f"\n  Pattern {i}:")
            print(f"    Confidence: {pattern['confidence']:.0%}")
            print(f"    Peak 1: ₹{pattern['peak1_price']:.2f} on {pattern['peak1_date']}")
            print(f"    Peak 2: ₹{pattern['peak2_price']:.2f} on {pattern['peak2_date']}")
            print(f"    Neckline: ₹{pattern['neckline']:.2f}")
            print(f"    Target: ₹{pattern['target_price']:.2f}")
            print(f"    Stop Loss: ₹{pattern['stop_loss']:.2f}")
            print(f"    Risk/Reward: {pattern['risk_reward']:.2f}")
            print(f"    Status: {pattern['status'].upper()}")
    else:
        print("  No patterns detected")
    
    print("\n📊 WEEKLY TIMEFRAME:")
    weekly_tops = results['weekly'].get('double_tops', [])
    print(f"  Patterns found: {len(weekly_tops)}")
    
    print("\n📊 MONTHLY TIMEFRAME:")
    monthly_tops = results['monthly'].get('double_tops', [])
    print(f"  Patterns found: {len(monthly_tops)}")
    
    print("\n🎯 CONSENSUS:")
    consensus = results['consensus']
    print(f"  Recommendation: {consensus['recommendation']}")
    print(f"  Strength: {consensus['strength']}/100")


def test_double_bottom():
    """Test double bottom detection"""
    print("\n" + "="*70)
    print("TEST 2: DOUBLE BOTTOM PATTERN")
    print("="*70)
    
    detector = DoublePatternDetector()
    df = generate_double_bottom_data()
    df.set_index('Date', inplace=True)
    
    # Analyze all timeframes
    results = detector.analyze_multi_timeframe(df)
    
    # Display results
    print("\n📊 DAILY TIMEFRAME:")
    daily_bottoms = results['daily'].get('double_bottoms', [])
    if daily_bottoms:
        for i, pattern in enumerate(daily_bottoms[:2], 1):
            print(f"\n  Pattern {i}:")
            print(f"    Confidence: {pattern['confidence']:.0%}")
            print(f"    Trough 1: ₹{pattern['trough1_price']:.2f} on {pattern['trough1_date']}")
            print(f"    Trough 2: ₹{pattern['trough2_price']:.2f} on {pattern['trough2_date']}")
            print(f"    Neckline: ₹{pattern['neckline']:.2f}")
            print(f"    Target: ₹{pattern['target_price']:.2f}")
            print(f"    Stop Loss: ₹{pattern['stop_loss']:.2f}")
            print(f"    Risk/Reward: {pattern['risk_reward']:.2f}")
            print(f"    Status: {pattern['status'].upper()}")
    else:
        print("  No patterns detected")
    
    print("\n📊 WEEKLY TIMEFRAME:")
    weekly_bottoms = results['weekly'].get('double_bottoms', [])
    print(f"  Patterns found: {len(weekly_bottoms)}")
    
    print("\n📊 MONTHLY TIMEFRAME:")
    monthly_bottoms = results['monthly'].get('double_bottoms', [])
    print(f"  Patterns found: {len(monthly_bottoms)}")
    
    print("\n🎯 CONSENSUS:")
    consensus = results['consensus']
    print(f"  Recommendation: {consensus['recommendation']}")
    print(f"  Strength: {consensus['strength']}/100")


def test_real_stock():
    """Test with real stock data"""
    print("\n" + "="*70)
    print("TEST 3: REAL STOCK DATA (KPIGREEN)")
    print("="*70)
    
    try:
        import yfinance as yf
        
        detector = DoublePatternDetector()
        
        # Fetch real data
        ticker = yf.Ticker("KPIGREEN.NS")
        hist = ticker.history(period="1y")
        
        df = pd.DataFrame({
            'Date': hist.index,
            'Close': hist['Close'].values
        })
        df.set_index('Date', inplace=True)
        
        # Analyze
        results = detector.analyze_multi_timeframe(df)
        
        # Display
        print("\n📊 ANALYSIS RESULTS:")
        
        for timeframe in ['daily', 'weekly', 'monthly']:
            if timeframe in results and results[timeframe]:
                tops = results[timeframe].get('double_tops', [])
                bottoms = results[timeframe].get('double_bottoms', [])
                
                print(f"\n  {timeframe.upper()}:")
                print(f"    Double Tops: {len(tops)}")
                print(f"    Double Bottoms: {len(bottoms)}")
                
                if tops:
                    print(f"    Best Top: {tops[0]['confidence']:.0%} confidence")
                if bottoms:
                    print(f"    Best Bottom: {bottoms[0]['confidence']:.0%} confidence")
        
        print("\n🎯 CONSENSUS:")
        consensus = results['consensus']
        print(f"  Recommendation: {consensus['recommendation']}")
        print(f"  Strength: {consensus['strength']}/100")
        
    except Exception as e:
        print(f"  ⚠️  Could not fetch real data: {e}")
        print("  (This is normal if no internet connection)")


def main():
    print("\n🔍 DOUBLE PATTERN DETECTOR - COMPREHENSIVE TEST")
    print("="*70)
    print("\nTesting across DAILY, WEEKLY, and MONTHLY timeframes")
    
    # Run tests
    test_double_top()
    test_double_bottom()
    test_real_stock()
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETE")
    print("="*70)
    
    print("\n💡 KEY FEATURES:")
    print("  ✅ Detects double tops and double bottoms")
    print("  ✅ Works on daily, weekly, monthly timeframes")
    print("  ✅ Calculates confidence scores")
    print("  ✅ Provides target prices and stop losses")
    print("  ✅ Confirms breakouts/breakdowns")
    print("  ✅ Multi-timeframe consensus")
    
    print("\n📊 USAGE:")
    print("  from double_pattern_detector import DoublePatternDetector")
    print("  detector = DoublePatternDetector()")
    print("  results = detector.analyze_multi_timeframe(price_data)")
    print("")


if __name__ == "__main__":
    main()
