"""
Enterprise Trading Framework - Simple Dashboard
Real-time stock analysis with multi-agent system
"""

import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import our analysis system
from multi_horizon_predictor import MultiHorizonPredictor

# Page config
st.set_page_config(
    page_title="Trading Framework Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📊 Enterprise Trading Framework</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("🎯 Stock Analysis")
    
    # Stock input
    ticker = st.text_input("Enter Stock Symbol", "KPIGREEN", help="NSE stock symbol (without .NS)")
    
    # Popular stocks
    st.subheader("Popular Stocks")
    popular = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "BHARTIARTL", "ITC", "KOTAKBANK", "LT"]
    selected_popular = st.selectbox("Quick Select", [""] + popular)
    if selected_popular:
        ticker = selected_popular
    
    analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.subheader("📈 Features")
    st.write("✅ Multi-Agent Analysis")
    st.write("✅ 6M-5Y Price Targets")
    st.write("✅ Technical Indicators")
    st.write("✅ Risk Assessment")

# Main content
if analyze_btn or ticker:
    try:
        with st.spinner(f"🔮 Analyzing {ticker}..."):
            # Fetch data
            stock = yf.Ticker(f"{ticker}.NS")
            hist = stock.history(period="1y")
            info = stock.info
            
            if hist.empty:
                st.error(f"❌ No data found for {ticker}")
                st.stop()
            
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100
            
            # Top metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Current Price",
                    f"₹{current_price:.2f}",
                    f"{change_pct:+.2f}%"
                )
            
            with col2:
                high_52w = hist['High'].max()
                st.metric("52W High", f"₹{high_52w:.2f}")
            
            with col3:
                low_52w = hist['Low'].min()
                st.metric("52W Low", f"₹{low_52w:.2f}")
            
            with col4:
                volume = hist['Volume'].iloc[-1]
                st.metric("Volume", f"{volume:,.0f}")
            
            st.markdown("---")
            
            # Two columns layout
            col_left, col_right = st.columns([2, 1])
            
            with col_left:
                # Price chart
                st.subheader("📈 Price Chart")
                
                fig = go.Figure()
                
                # Candlestick
                fig.add_trace(go.Candlestick(
                    x=hist.index,
                    open=hist['Open'],
                    high=hist['High'],
                    low=hist['Low'],
                    close=hist['Close'],
                    name='Price'
                ))
                
                # Volume bar
                fig.add_trace(go.Bar(
                    x=hist.index,
                    y=hist['Volume'],
                    name='Volume',
                    yaxis='y2',
                    marker_color='rgba(100, 100, 100, 0.3)'
                ))
                
                fig.update_layout(
                    title=f"{ticker} - Last 1 Year",
                    yaxis_title="Price (₹)",
                    yaxis2=dict(title="Volume", overlaying='y', side='right'),
                    xaxis_rangeslider_visible=False,
                    height=500,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col_right:
                # Company info
                st.subheader("🏢 Company Info")
                
                company_name = info.get('longName', ticker)
                sector = info.get('sector', 'N/A')
                industry = info.get('industry', 'N/A')
                
                st.write(f"**Name:** {company_name}")
                st.write(f"**Sector:** {sector}")
                st.write(f"**Industry:** {industry}")
                
                st.markdown("---")
                
                # Key metrics
                st.subheader("📊 Key Metrics")
                
                market_cap = info.get('marketCap', 0)
                if market_cap:
                    st.write(f"**Market Cap:** ₹{market_cap/10000000:.2f} Cr")
                
                pe_ratio = info.get('trailingPE', 0)
                if pe_ratio:
                    st.write(f"**P/E Ratio:** {pe_ratio:.2f}")
                
                roe = info.get('returnOnEquity', 0)
                if roe:
                    st.write(f"**ROE:** {roe*100:.2f}%")
                
                debt_equity = info.get('debtToEquity', 0)
                if debt_equity:
                    st.write(f"**Debt/Equity:** {debt_equity:.2f}")
            
            st.markdown("---")
            
            # Multi-horizon predictions
            st.subheader("🎯 Multi-Horizon Price Targets")
            
            with st.spinner("Calculating targets..."):
                predictor = MultiHorizonPredictor()
                results = predictor.predict_all_horizons(ticker, current_price)
                
                # Display targets
                cols = st.columns(5)
                
                horizons = ['6M', '1Y', '2Y', '3Y', '5Y']
                for i, horizon_key in enumerate(horizons):
                    if horizon_key in results['horizons']:
                        horizon = results['horizons'][horizon_key]
                        consensus = horizon['consensus']
                        
                        if consensus['target']:
                            with cols[i]:
                                st.metric(
                                    horizon['horizon'],
                                    f"₹{consensus['target']:.2f}",
                                    f"{consensus['upside']:.1f}%",
                                    help=f"Confidence: {consensus['confidence']:.0f}%"
                                )
                                st.caption(f"Confidence: {consensus['confidence']:.0f}%")
                
                # Summary
                st.markdown("---")
                summary = results['summary']
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    outlook = summary['investment_outlook']
                    color = "🟢" if "BULLISH" in outlook else "🔴" if "BEARISH" in outlook else "🟡"
                    st.info(f"{color} **Outlook:** {outlook}")
                
                with col2:
                    cagr = summary['expected_cagr']
                    st.info(f"📈 **Expected CAGR:** {cagr:.1f}%")
                
                with col3:
                    risk = summary['risk_level']
                    st.info(f"⚠️ **Risk Level:** {risk}")
                
                with col4:
                    best = summary['best_horizon']
                    st.info(f"⭐ **Best Horizon:** {best}")
                
                # Detailed table
                st.subheader("📋 Detailed Targets")
                
                table_data = []
                for horizon_key in horizons:
                    if horizon_key in results['horizons']:
                        horizon = results['horizons'][horizon_key]
                        consensus = horizon['consensus']
                        
                        if consensus['target']:
                            table_data.append({
                                'Horizon': horizon['horizon'],
                                'Target': f"₹{consensus['target']:.2f}",
                                'Min': f"₹{consensus['min_target']:.2f}",
                                'Max': f"₹{consensus['max_target']:.2f}",
                                'Upside': f"{consensus['upside']:.1f}%",
                                'Confidence': f"{consensus['confidence']:.0f}%"
                            })
                
                if table_data:
                    df = pd.DataFrame(table_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Technical indicators
            st.markdown("---")
            st.subheader("📊 Technical Indicators")
            
            col1, col2, col3 = st.columns(3)
            
            # Calculate RSI
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            with col1:
                rsi_color = "🔴" if current_rsi > 70 else "🟢" if current_rsi < 30 else "🟡"
                st.metric("RSI (14)", f"{current_rsi:.2f}", help="Relative Strength Index")
                st.caption(f"{rsi_color} {'Overbought' if current_rsi > 70 else 'Oversold' if current_rsi < 30 else 'Neutral'}")
            
            # Moving averages
            ma20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            ma50 = hist['Close'].rolling(window=50).mean().iloc[-1]
            
            with col2:
                st.metric("MA(20)", f"₹{ma20:.2f}")
                trend = "🟢 Above" if current_price > ma20 else "🔴 Below"
                st.caption(f"Price {trend}")
            
            with col3:
                st.metric("MA(50)", f"₹{ma50:.2f}")
                trend = "🟢 Above" if current_price > ma50 else "🔴 Below"
                st.caption(f"Price {trend}")
            
    except Exception as e:
        st.error(f"❌ Error analyzing {ticker}: {str(e)}")
        st.exception(e)

else:
    # Welcome screen
    st.info("👈 Enter a stock symbol in the sidebar to begin analysis")
    
    st.subheader("🚀 Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📊 Analysis Features
        - **Multi-Agent System** - 4 specialized AI agents
        - **Multi-Horizon Targets** - 6M to 5Y predictions
        - **Technical Analysis** - RSI, Moving Averages, Trends
        - **Fundamental Metrics** - P/E, ROE, Debt/Equity
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 Prediction Methods
        - **Historical Growth** - CAGR analysis
        - **Fundamental Valuation** - Growth projections
        - **Technical Projection** - Trend analysis
        - **Regression Analysis** - Statistical modeling
        - **Monte Carlo** - 1000 simulations
        """)
    
    st.markdown("---")
    st.success("✅ System is ready! Enter a stock symbol to start.")

# Footer
st.markdown("---")
st.caption("🤖 Powered by Enterprise Trading Framework | Multi-Agent AI System")
