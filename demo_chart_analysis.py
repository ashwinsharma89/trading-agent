#!/usr/bin/env python3
"""
Demo: Analyze Chart Images
Shows how to analyze stock chart screenshots
"""

import sys
import os
from advanced_chart_vision import AdvancedChartVision


def demo_chart_analysis():
    """
    Demo chart image analysis
    """
    print("\n📊 CHART IMAGE ANALYSIS DEMO")
    print("="*80)
    
    analyzer = AdvancedChartVision()
    
    print("\n🎯 How It Works:")
    print("-"*80)
    print("\n1️⃣  AI VISION (GPT-4 Vision)")
    print("   • Sends chart image to GPT-4 Vision")
    print("   • AI analyzes patterns, trends, support/resistance")
    print("   • Returns detailed analysis with confidence scores")
    print("   • Most accurate method")
    
    print("\n2️⃣  COMPUTER VISION (OpenCV)")
    print("   • Extracts price line from chart image")
    print("   • Detects edges and contours")
    print("   • Analyzes price movements algorithmically")
    print("   • Works offline, no API needed")
    
    print("\n3️⃣  OCR (Optical Character Recognition)")
    print("   • Extracts text from chart (prices, dates)")
    print("   • Identifies indicator values")
    print("   • Supplements other methods")
    
    print("\n" + "="*80)
    print("📸 EXAMPLE USAGE")
    print("="*80)
    
    print("\n# Method 1: Analyze screenshot from TradingView")
    print("```python")
    print("from advanced_chart_vision import AdvancedChartVision")
    print("")
    print("analyzer = AdvancedChartVision()")
    print("result = analyzer.analyze_chart_image('kpigreen_chart.png', 'KPIGREEN')")
    print("")
    print("# AI Vision Analysis")
    print("print(result['ai_vision']['patterns'])")
    print("# Output: [")
    print("#   {'name': 'ascending_triangle', 'direction': 'bullish', 'confidence': 0.85},")
    print("#   {'name': 'cup_and_handle', 'direction': 'bullish', 'confidence': 0.75}")
    print("# ]")
    print("")
    print("print(result['ai_vision']['recommendation'])  # 'buy'")
    print("print(result['ai_vision']['support_levels'])  # [450, 440]")
    print("print(result['ai_vision']['resistance_levels'])  # [480, 490]")
    print("```")
    
    print("\n" + "="*80)
    print("🎨 WHAT AI VISION DETECTS")
    print("="*80)
    
    print("\n✅ Chart Patterns:")
    print("   • Head & Shoulders")
    print("   • Double Top/Bottom")
    print("   • Triangles (Ascending, Descending, Symmetrical)")
    print("   • Cup & Handle")
    print("   • Flags & Pennants")
    print("   • Wedges")
    
    print("\n✅ Technical Analysis:")
    print("   • Trend direction (up/down/sideways)")
    print("   • Support & resistance levels")
    print("   • Volume analysis")
    print("   • Indicator readings (RSI, MACD if visible)")
    
    print("\n✅ Candlestick Patterns:")
    print("   • Hammer, Shooting Star")
    print("   • Engulfing patterns")
    print("   • Doji, Spinning Top")
    
    print("\n" + "="*80)
    print("📊 EXAMPLE OUTPUT")
    print("="*80)
    
    example_output = """
{
  "ai_vision": {
    "patterns": [
      {
        "name": "ascending_triangle",
        "direction": "bullish",
        "confidence": 0.85
      },
      {
        "name": "bullish_flag",
        "direction": "bullish",
        "confidence": 0.75
      }
    ],
    "trend": "uptrend",
    "support_levels": [450, 440, 430],
    "resistance_levels": [480, 490],
    "indicators": {
      "rsi": "neutral (55)",
      "macd": "bullish_crossover",
      "volume": "increasing"
    },
    "candlestick_patterns": ["hammer", "bullish_engulfing"],
    "volume_analysis": "increasing",
    "timeframe": "daily",
    "recommendation": "buy",
    "confidence": 0.82,
    "key_observations": [
      "Strong uptrend with higher highs and higher lows",
      "Ascending triangle pattern forming - bullish breakout likely",
      "Volume increasing on up days - confirms strength",
      "RSI not overbought - room to run",
      "MACD bullish crossover - momentum positive"
    ]
  },
  "computer_vision": {
    "patterns": [
      {"name": "uptrend", "direction": "bullish", "confidence": 0.7}
    ],
    "price_points": 120
  },
  "combined_analysis": {
    "patterns": [
      {
        "name": "ascending_triangle",
        "direction": "bullish",
        "confidence": 0.85,
        "detected_by": 1
      }
    ],
    "recommendation": "BUY",
    "confidence": 0.82
  }
}
"""
    
    print(example_output)
    
    print("\n" + "="*80)
    print("🚀 HOW TO USE")
    print("="*80)
    
    print("\n1. Take screenshot of chart from TradingView/Zerodha/etc.")
    print("2. Save as PNG/JPG")
    print("3. Run analysis:")
    print("\n```bash")
    print("python3 demo_chart_analysis.py /path/to/chart.png KPIGREEN")
    print("```")
    
    print("\n4. Get instant analysis:")
    print("   ✅ Patterns detected")
    print("   ✅ Buy/Sell recommendation")
    print("   ✅ Support/Resistance levels")
    print("   ✅ Confidence score")
    
    print("\n" + "="*80)
    print("💡 INTEGRATION WITH MULTI-AGENT SYSTEM")
    print("="*80)
    
    print("\nChart analysis enhances the multi-agent system:")
    print("")
    print("Traditional Analysis:")
    print("  Technical Agent: 36/100 (RSI oversold)")
    print("  Fundamental Agent: 68/100 (strong growth)")
    print("  → Composite: 56/100 (HOLD)")
    print("")
    print("+ Chart Image Analysis:")
    print("  AI Vision: Ascending triangle (bullish, 0.85 confidence)")
    print("  Pattern adjustment: +8 points")
    print("  → Enhanced: 64/100 (BUY)")
    
    print("\n" + "="*80)
    print("⚡ ADVANTAGES")
    print("="*80)
    
    print("\n✅ Visual Confirmation")
    print("   See what the AI sees - transparent analysis")
    
    print("\n✅ Works with Any Chart")
    print("   TradingView, Zerodha, NSE, BSE - any screenshot")
    
    print("\n✅ Multiple Methods")
    print("   AI Vision + Computer Vision + OCR = robust analysis")
    
    print("\n✅ Learning Capability")
    print("   Track which patterns actually work")
    print("   Improve accuracy over time")
    
    print("\n" + "="*80)
    print("📝 REQUIREMENTS")
    print("="*80)
    
    print("\n```bash")
    print("pip install openai pillow opencv-python pytesseract")
    print("```")
    
    print("\nSet OpenAI API key in .env:")
    print("```")
    print("OPENAI_API_KEY=your_key_here")
    print("```")
    
    print("\n" + "="*80)
    print("✅ READY TO USE!")
    print("="*80)
    
    print("\nThe chart image analyzer is built and ready.")
    print("Just provide a chart screenshot and get instant analysis!")


def analyze_image_file(image_path: str, ticker: str):
    """
    Analyze a specific chart image
    """
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    print(f"\n🔍 Analyzing chart: {image_path}")
    print(f"📊 Ticker: {ticker}")
    print("="*80)
    
    analyzer = AdvancedChartVision()
    
    print("\n⏳ Running analysis (this may take 10-15 seconds)...")
    
    result = analyzer.analyze_chart_image(image_path, ticker)
    
    print("\n✅ Analysis Complete!")
    print("="*80)
    
    # Display AI Vision results
    if result.get('ai_vision', {}).get('available'):
        ai = result['ai_vision']
        
        print(f"\n🤖 AI VISION ANALYSIS")
        print("-"*80)
        
        print(f"\n📊 Patterns Detected:")
        for p in ai.get('patterns', []):
            print(f"   • {p['name']} ({p['direction']}) - Confidence: {p['confidence']:.0%}")
        
        print(f"\n📈 Trend: {ai.get('trend', 'unknown')}")
        
        if ai.get('support_levels'):
            print(f"📉 Support: {', '.join([f'₹{s}' for s in ai['support_levels']])}")
        
        if ai.get('resistance_levels'):
            print(f"📈 Resistance: {', '.join([f'₹{r}' for r in ai['resistance_levels']])}")
        
        print(f"\n🎯 Recommendation: {ai.get('recommendation', 'HOLD').upper()}")
        print(f"💯 Confidence: {ai.get('confidence', 0)*100:.0f}%")
        
        if ai.get('key_observations'):
            print(f"\n💡 Key Observations:")
            for obs in ai['key_observations']:
                print(f"   • {obs}")
    
    # Display combined analysis
    if result.get('combined_analysis'):
        combined = result['combined_analysis']
        
        print(f"\n🔄 COMBINED ANALYSIS")
        print("-"*80)
        print(f"Recommendation: {combined['recommendation']}")
        print(f"Confidence: {combined['confidence']*100:.0f}%")


if __name__ == "__main__":
    if len(sys.argv) > 2:
        # Analyze specific image
        image_path = sys.argv[1]
        ticker = sys.argv[2]
        analyze_image_file(image_path, ticker)
    else:
        # Show demo
        demo_chart_analysis()
