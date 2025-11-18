"""
Enterprise Stock Trading Framework - Streamlit UI
7 Core Pages with Smart Money Concepts Integration
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import asyncio
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
import time
from tradingview_ta import TA_Handler, Interval, Exchange
from streamlit_autorefresh import st_autorefresh
from nifty_500_stocks import NIFTY_500_STOCKS, NIFTY_500_SECTORS
from data_provider import get_data_provider
from fvg_detector import FVGDetector, get_fvg_summary
from yahoo_provider import get_yahoo_provider
from smc_analyzer import SMCAnalyzer
from fundamental_analyzer import FundamentalAnalyzer
from volume_analyzer import VolumeAnalyzer
from market_data_fetcher import MarketDataFetcher
from nlp_query_handler import NLPQueryHandler

# Configuration
st.set_page_config(
    page_title="Enterprise Trading Framework",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# TradingView Configuration
INDIAN_STOCK_EXCHANGE = "NSE"
INDIAN_SCREENER = "india"

# Use Nifty 500 stocks (imported from nifty_500_stocks.py)
POPULAR_STOCKS = sorted(NIFTY_500_STOCKS)  # All 500 stocks, sorted alphabetically
SECTOR_STOCKS = NIFTY_500_SECTORS  # Sector-wise classification

# Initialize enhanced data provider (supports paid TradingView accounts)
try:
    data_provider = get_data_provider()
    USE_ENHANCED_PROVIDER = True
    st.sidebar.success("✅ Enhanced data provider active")
except Exception as e:
    USE_ENHANCED_PROVIDER = False
    st.sidebar.warning(f"⚠️ Using basic provider: {e}")

# Cache for price data (1 minute TTL with enhanced provider)
@st.cache_data(ttl=60, show_spinner=False)
def get_tradingview_data(symbol: str, exchange: str = INDIAN_STOCK_EXCHANGE, screener: str = INDIAN_SCREENER, interval: str = Interval.INTERVAL_1_DAY):
    """Fetch real-time data from TradingView (uses enhanced provider if available)"""
    
    # Use enhanced provider if available (paid account)
    if USE_ENHANCED_PROVIDER:
        try:
            data = data_provider.get_live_data(symbol, exchange, screener)
            if data:
                return data
        except Exception as e:
            pass  # Fallback to basic provider
    
    # Fallback to basic provider
    max_retries = 2
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                time.sleep(retry_delay * attempt)
            
            handler = TA_Handler(
                symbol=symbol,
                exchange=exchange,
                screener=screener,
                interval=interval,
                timeout=15
            )
            analysis = handler.get_analysis()
            return {
                'symbol': symbol,
                'price': analysis.indicators.get('close', 0),
                'open': analysis.indicators.get('open', 0),
                'high': analysis.indicators.get('high', 0),
                'low': analysis.indicators.get('low', 0),
                'volume': analysis.indicators.get('volume', 0),
                'change': analysis.indicators.get('change', 0),
                'change_percent': analysis.indicators.get('change', 0) / analysis.indicators.get('open', 1) * 100 if analysis.indicators.get('open') else 0,
                'rsi': analysis.indicators.get('RSI', 50),
                'sma_20': analysis.indicators.get('SMA20', 0),
                'sma_50': analysis.indicators.get('SMA50', 0),
                'recommendation': analysis.summary.get('RECOMMENDATION', 'NEUTRAL'),
                'timestamp': datetime.now().isoformat(),
                'source': 'tradingview_basic'
            }
        except Exception as e:
            error_msg = str(e)
            if '429' in error_msg and attempt < max_retries - 1:
                continue
            else:
                return None
    
    return None

@st.cache_data(ttl=60)
def get_live_price(symbol: str) -> float:
    """Get live price from TradingView"""
    data = get_tradingview_data(symbol)
    return data['price'] if data else 0.0

@st.cache_data(ttl=60, show_spinner=False)
def get_multiple_prices(symbols: List[str]) -> Dict[str, float]:
    """Fetch prices for multiple symbols (optimized with enhanced provider)"""
    prices = {}
    
    # Use batch fetching if enhanced provider available
    if USE_ENHANCED_PROVIDER:
        try:
            batch_data = data_provider.get_batch_data(symbols, INDIAN_STOCK_EXCHANGE)
            for symbol, data in batch_data.items():
                if data:
                    prices[symbol] = data['price']
            return prices
        except Exception as e:
            pass  # Fallback to sequential
    
    # Fallback: sequential fetching with rate limiting
    for i, symbol in enumerate(symbols):
        if i > 0:
            time.sleep(0.3)  # Reduced delay with better provider
        
        data = get_tradingview_data(symbol)
        if data:
            prices[symbol] = data['price']
        else:
            prices[symbol] = 0.0
    return prices

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .signal-buy {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
    }
    .signal-sell {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
    }
    .signal-hold {
        background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
    }
    .fvg-zone {
        background: rgba(255, 107, 107, 0.2);
        border: 2px dashed #ff6b6b;
        border-radius: 5px;
        padding: 0.5rem;
        margin: 0.25rem 0;
    }
    .order-block {
        background: rgba(46, 213, 115, 0.2);
        border: 2px solid #2ed573;
        border-radius: 5px;
        padding: 0.5rem;
        margin: 0.25rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'
if 'selected_symbols' not in st.session_state:
    st.session_state.selected_symbols = []
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK']
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True

# Auto-refresh every 60 seconds if enabled
if st.session_state.auto_refresh:
    count = st_autorefresh(interval=60000, key="price_refresh")

# Navigation
def navigation():
    """Main navigation sidebar"""
    st.sidebar.markdown("## 🔍 Stock Search")
    st.sidebar.markdown(f"**{len(POPULAR_STOCKS)} Nifty 500 Stocks Available**")
    
    # Stock search with autocomplete
    search_method = st.sidebar.radio("Search by:", ["Search/Filter", "By Sector", "Enter Symbol"])
    
    if search_method == "Search/Filter":
        # Text search with filtering
        search_query = st.sidebar.text_input("🔎 Type to search", placeholder="e.g., RELIANCE, TCS...", key="search_filter")
        
        if search_query:
            # Filter stocks matching the query
            filtered_stocks = [s for s in POPULAR_STOCKS if search_query.upper() in s]
            if filtered_stocks:
                selected_stock = st.sidebar.selectbox(f"Found {len(filtered_stocks)} matches", filtered_stocks, key="filtered_selector")
            else:
                st.sidebar.warning("No matches found")
                selected_stock = st.sidebar.selectbox("All Stocks", POPULAR_STOCKS, key="all_selector")
        else:
            selected_stock = st.sidebar.selectbox("All Nifty 500 Stocks", POPULAR_STOCKS, key="stock_selector")
            
    elif search_method == "By Sector":
        selected_sector = st.sidebar.selectbox("Select Sector", list(SECTOR_STOCKS.keys()))
        st.sidebar.markdown(f"*{len(SECTOR_STOCKS[selected_sector])} stocks in {selected_sector}*")
        selected_stock = st.sidebar.selectbox("Select Stock", SECTOR_STOCKS[selected_sector], key="sector_stock_selector")
    else:
        selected_stock = st.sidebar.text_input("Enter NSE Symbol", value="RELIANCE", key="manual_stock_input").upper()
    
    if st.sidebar.button("📊 Analyze Stock", use_container_width=True, type="primary"):
        if selected_stock and selected_stock not in st.session_state.watchlist:
            st.session_state.watchlist.insert(0, selected_stock)
            st.session_state.page = 'stock_analysis'
            st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("## �� Navigation")
    
    pages = {
        'dashboard': '📊 Market Dashboard',
        'screener': '🔍 Smart Screener',
        'idea_generator': '💡 AI Idea Generator',
        'stock_analysis': '📈 Stock Deep Dive',
        'portfolio': '💼 Portfolio Manager',
        'backtesting': '🧪 Backtesting Lab',
        'admin': '⚙️ Admin Panel'
    }
    
    for page_key, page_title in pages.items():
        if st.sidebar.button(page_title, key=f"nav_{page_key}", use_container_width=True):
            st.session_state.page = page_key
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Quick Stats")
    
    # Live watchlist prices
    if st.session_state.watchlist:
        watchlist_prices = get_multiple_prices(st.session_state.watchlist[:3])
        for symbol, price in watchlist_prices.items():
            st.sidebar.metric(symbol, f"₹{price:.2f}", "Live")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Settings")
    st.session_state.auto_refresh = st.sidebar.checkbox("Auto-refresh (60s)", value=st.session_state.auto_refresh)
    
    if st.sidebar.button("🔄 Refresh Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# API Helper Functions
def get_api_data(endpoint: str, params: Dict = None) -> Optional[Dict]:
    """Get data from API"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

def post_api_data(endpoint: str, data: Dict) -> Optional[Dict]:
    """Post data to API"""
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

# Chart Functions
def create_candlestick_chart(df: pd.DataFrame, title: str = "Price Chart") -> go.Figure:
    """Create candlestick chart with smart money annotations"""
    fig = go.Figure()
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name="Price",
        increasing_line_color='#00ff88',
        decreasing_line_color='#ff4444'
    ))
    
    # Volume bars
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['volume'],
        name="Volume",
        yaxis='y2',
        marker_color='rgba(158,158,158,0.5)'
    ))
    
    # Moving averages
    if 'sma_20' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['sma_20'],
            name="SMA 20",
            line=dict(color='orange', width=2)
        ))
    
    if 'sma_50' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['sma_50'],
            name="SMA 50",
            line=dict(color='blue', width=2)
        ))
    
    # Layout
    fig.update_layout(
        title=title,
        yaxis_title="Price",
        yaxis2=dict(
            title="Volume",
            overlaying='y',
            side='right'
        ),
        xaxis_rangeslider_visible=False,
        height=600,
        template="plotly_dark"
    )
    
    return fig

def create_volume_profile_chart(df: pd.DataFrame) -> go.Figure:
    """Create volume profile chart"""
    # Calculate volume profile (simplified)
    price_bins = np.linspace(df['low'].min(), df['high'].max(), 50)
    volume_profile = []
    
    for i in range(len(price_bins) - 1):
        mask = (df['close'] >= price_bins[i]) & (df['close'] < price_bins[i + 1])
        volume_profile.append(df[mask]['volume'].sum())
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=volume_profile,
        y=price_bins[:-1],
        orientation='h',
        name="Volume Profile",
        marker_color='rgba(100,149,237,0.7)'
    ))
    
    fig.update_layout(
        title="Volume Profile",
        xaxis_title="Volume",
        yaxis_title="Price",
        height=400,
        template="plotly_dark"
    )
    
    return fig

# Page 1: Market Dashboard
def market_dashboard():
    """Market overview dashboard with smart money insights"""
    st.markdown('<h1 class="main-header">📊 Market Dashboard</h1>', unsafe_allow_html=True)
    
    # Market Regime Card
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Market Regime</h3>
            <h2>🟢 Bullish</h2>
            <p>Strength: 75%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>FII Activity</h3>
            <h2>📈 Net Buyers</h2>
            <p>₹1,250 Cr</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Calculate real active FVGs from watchlist
        try:
            yahoo_prov = get_yahoo_provider()
            total_active_fvgs = 0
            for symbol in st.session_state.watchlist[:10]:
                try:
                    hist_data = yahoo_prov.get_historical_data(symbol, period="1mo", interval="1d")
                    if hist_data is not None and not hist_data.empty:
                        summary = get_fvg_summary(symbol, hist_data)
                        total_active_fvgs += summary['active_fvgs']
                except:
                    continue
        except:
            total_active_fvgs = 0
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>Active FVGs</h3>
            <h2>🎯 {total_active_fvgs}</h2>
            <p>From Watchlist</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>Volume Alert</h3>
            <h2>⚡ High</h2>
            <p>2.3x Average</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Sector Heat Map
    st.markdown("### 🔥 Sector Momentum Heat Map")
    
    # Get real sector data
    @st.cache_data(ttl=300, show_spinner=False)
    def get_sector_momentum():
        fetcher = MarketDataFetcher()
        
        # Define sector representatives
        sector_stocks = {
            'Technology': ['TCS', 'INFY', 'WIPRO', 'TECHM', 'HCLTECH'],
            'Banking': ['HDFCBANK', 'ICICIBANK', 'SBIN', 'KOTAKBANK', 'AXISBANK'],
            'Pharma': ['SUNPHARMA', 'DRREDDY', 'CIPLA', 'DIVISLAB', 'BIOCON'],
            'Energy': ['RELIANCE', 'ONGC', 'BPCL', 'IOC', 'POWERGRID'],
            'Metals': ['TATASTEEL', 'HINDALCO', 'JSWSTEEL', 'COALINDIA', 'VEDL'],
            'IT Services': ['TCS', 'INFY', 'WIPRO', 'LTIM', 'PERSISTENT']
        }
        
        return fetcher.get_sector_data(sector_stocks)
    
    with st.spinner("Loading sector data..."):
        try:
            sectors = get_sector_momentum()
        except:
            # Fallback to basic data if fetch fails
            sectors = {
                'Technology': {'score': 0.75, 'change': 1.5, 'fvg_count': 5},
                'Banking': {'score': 0.60, 'change': 0.8, 'fvg_count': 3},
                'Pharma': {'score': 0.65, 'change': 1.2, 'fvg_count': 4},
                'Energy': {'score': 0.70, 'change': 2.0, 'fvg_count': 6},
                'Metals': {'score': 0.55, 'change': -0.5, 'fvg_count': 2},
                'IT Services': {'score': 0.72, 'change': 1.3, 'fvg_count': 5}
            }
    
    sector_df = pd.DataFrame(sectors).T
    
    # Create heat map
    fig = px.imshow(
        sector_df[['score']].T,
        labels=dict(x="Sector", y="Metric", color="Score"),
        x=sector_df.index,
        y=["Momentum"],
        color_continuous_scale="RdYlGn",
        aspect="auto"
    )
    
    fig.update_layout(height=200, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent Smart Money Activity
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Recent FVG Zones")
        
        # Get real FVG data for watchlist stocks
        yahoo_prov = get_yahoo_provider()
        fvg_data = []
        
        for symbol in st.session_state.watchlist[:4]:  # Top 4 stocks
            try:
                hist_data = yahoo_prov.get_historical_data(symbol, period="3mo", interval="1d")
                if hist_data is not None and not hist_data.empty:
                    summary = get_fvg_summary(symbol, hist_data)
                    
                    # Add active FVGs to display
                    for fvg in summary['all_active_fvgs'][:1]:  # Show 1 per stock
                        fvg_data.append({
                            'symbol': symbol,
                            'type': f"{fvg['type']} FVG",
                            'range': f"₹{fvg['lower']:.2f}-{fvg['upper']:.2f}",
                            'strength': fvg['strength'],
                            'distance': f"{abs(fvg['distance_percent']):.1f}%",
                            'age': f"{fvg['days_old']}d ago"
                        })
            except Exception as e:
                continue
        
        if fvg_data:
            for fvg in fvg_data:
                with st.expander(f"**{fvg['symbol']}** - {fvg['type']}"):
                    st.markdown(f"**Range:** {fvg['range']}")
                    st.markdown(f"**Strength:** {fvg['strength']}")
                    st.markdown(f"**Distance:** {fvg['distance']}")
                    st.markdown(f"**Detected:** {fvg['age']}")
                    st.progress(0.8 if fvg['strength'] == 'Strong' else 0.5 if fvg['strength'] == 'Medium' else 0.3)
        else:
            st.info("No active FVG zones detected in watchlist stocks")
    
    with col2:
        st.markdown("### 📊 Volume Profile Analysis")
        
        # Mock volume profile data
        symbols = ['NIFTY', 'BANKNIFTY', 'RELIANCE', 'TCS']
        selected_symbol = st.selectbox("Select Index/Stock", symbols)
        
        # Create sample volume profile chart
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        sample_data = pd.DataFrame({
            'open': np.random.randn(100).cumsum() + 100,
            'high': np.random.randn(100).cumsum() + 102,
            'low': np.random.randn(100).cumsum() + 98,
            'close': np.random.randn(100).cumsum() + 100,
            'volume': np.random.randint(1000000, 5000000, 100)
        }, index=dates)
        
        fig = create_volume_profile_chart(sample_data)
        st.plotly_chart(fig, use_container_width=True)
    
    # Live Signals Feed with real prices
    st.markdown("### 📡 Live Signals Feed")
    
    # Show more stocks option
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Showing {len(st.session_state.watchlist)} stocks**")
    with col2:
        if st.button("🔄 Refresh Prices"):
            st.cache_data.clear()
            st.rerun()
    
    # Fetch live data for watchlist stocks (limit to prevent rate limiting)
    signals = []
    max_display = min(len(st.session_state.watchlist), 20)  # Limit to 20 stocks to avoid rate limits
    
    if len(st.session_state.watchlist) > 20:
        st.info(f"Showing first 20 of {len(st.session_state.watchlist)} watchlist stocks to avoid API rate limits")
    
    for i, symbol in enumerate(st.session_state.watchlist[:max_display]):
        # Add delay to avoid rate limiting
        if i > 0 and i % 5 == 0:
            time.sleep(1)  # Pause every 5 requests
        
        data = get_tradingview_data(symbol)
        if data and data['price'] > 0:
            signal_type = 'BUY' if data['recommendation'] in ['STRONG_BUY', 'BUY'] else 'SELL' if data['recommendation'] in ['STRONG_SELL', 'SELL'] else 'HOLD'
            signals.append({
                'symbol': symbol,
                'price': f"₹{data['price']:.2f}",
                'change': f"{data['change_percent']:.2f}%",
                'signal': signal_type,
                'strength': int(abs(data['rsi'] - 50) * 2),
                'rsi': f"{data['rsi']:.1f}",
                'source': 'TradingView TA',
                'time': 'Live'
            })
        else:
            # Skip stocks with unavailable data
            continue
    
    signals_df = pd.DataFrame(signals)
    
    def color_signals(val):
        if val == 'BUY':
            return 'background-color: rgba(46, 213, 115, 0.3)'
        elif val == 'SELL':
            return 'background-color: rgba(255, 71, 87, 0.3)'
        else:
            return 'background-color: rgba(255, 165, 2, 0.3)'
    
    styled_df = signals_df.style.applymap(color_signals, subset=['signal'])
    st.dataframe(styled_df, use_container_width=True)

# Page 2: Smart Screener
def smart_screener():
    """Advanced stock screener with smart money filters"""
    st.markdown('<h1 class="main-header">🔍 Smart Screener</h1>', unsafe_allow_html=True)
    
    # Filter Configuration
    st.markdown("### 🎛️ Screening Criteria")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📊 Technical Filters")
        rsi_range = st.slider("RSI Range", 0, 100, (30, 70))
        price_range = st.slider("Price Range (₹)", 0, 5000, (100, 2000))
        volume_multiplier = st.slider("Volume > Average", 1.0, 5.0, 1.5)
    
    with col2:
        st.markdown("#### 🎯 Smart Money Filters")
        fvg_filter = st.selectbox("FVG Status", ["Any", "Unmitigated FVG", "Near FVG Fill", "No FVG"])
        structure_trend = st.selectbox("Market Structure", ["Any", "Bullish", "Bearish", "Sideways"])
        order_block_proximity = st.slider("Order Block Distance (%)", 0, 10, 2)
    
    with col3:
        st.markdown("#### 💰 Fundamental Filters")
        pe_range = st.slider("P/E Ratio", 0, 50, (10, 30))
        roe_min = st.slider("Min ROE (%)", 0, 30, 15)
        debt_to_equity_max = st.slider("Max D/E Ratio", 0.0, 2.0, 1.0)
    
    # Pre-built Templates
    st.markdown("### 📋 Quick Templates")
    
    template_col1, template_col2, template_col3, template_col4 = st.columns(4)
    
    with template_col1:
        if st.button("🚀 Momentum", use_container_width=True):
            st.info("Applied: RSI > 50, Volume > 1.5x, Bullish Structure")
    
    with template_col2:
        if st.button("💎 Value Pick", use_container_width=True):
            st.info("Applied: P/E < 20, ROE > 15%, Low Debt")
    
    with template_col3:
        if st.button("🎯 FVG Plays", use_container_width=True):
            st.info("Applied: Unmitigated FVG, Volume Spike, Near Support")
    
    with template_col4:
        if st.button("⚡ Volume Breakout", use_container_width=True):
            st.info("Applied: Volume > 2x, Price Breakout, High Conviction")
    
    # Run Screener
    if st.button("🔍 Run Screener", type="primary", use_container_width=True):
        with st.spinner("Screening stocks with smart money analysis..."):
            # Fetch real data for screening
            fetcher = MarketDataFetcher()
            
            # Get stocks to screen (from watchlist or default list)
            stocks_to_screen = st.session_state.watchlist if st.session_state.watchlist else ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'WIPRO', 'ICICIBANK', 'SBIN', 'BHARTIARTL', 'ITC', 'HINDUNILVR']
            
            # Limit to prevent timeout
            stocks_to_screen = stocks_to_screen[:20]
            
            # Fetch data
            results = fetcher.fetch_multiple_stocks(stocks_to_screen, max_workers=5)
            
            if not results:
                st.error("Unable to fetch screening data. Please try again.")
                return
            
            # Convert to DataFrame
            results_df = pd.DataFrame(results)
            
            # Rename columns for display
            results_df = results_df.rename(columns={
                'change_pct': 'change',
                'fvg_status': 'FVG Status',
                'structure': 'Structure',
                'signal': 'Signal',
                'confidence': 'Confidence'
            })
            
            # Display results with styling
            st.markdown("### 📊 Screening Results")
            
            def style_results(df):
                # Color code the signals
                def color_signal(val):
                    if val == 'BUY':
                        return 'background-color: rgba(46, 213, 115, 0.3); color: white'
                    elif val == 'SELL':
                        return 'background-color: rgba(255, 71, 87, 0.3); color: white'
                    else:
                        return 'background-color: rgba(255, 165, 2, 0.3); color: white'
                
                # Color code change percentage
                def color_change(val):
                    if val > 0:
                        return 'color: #00ff88'
                    elif val < 0:
                        return 'color: #ff4444'
                    else:
                        return 'color: white'
                
                styled = df.copy()
                styled['signal'] = df['signal'].apply(color_signal)
                styled['change'] = df['change'].apply(color_change)
                
                return styled
            
            styled_results = style_results(results_df)
            st.dataframe(styled_results, use_container_width=True)
            
            # Export options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    "📥 Download CSV",
                    data=results_df.to_csv(index=False),
                    file_name="screener_results.csv",
                    mime="text/csv"
                )
            
            with col2:
                st.button("📊 Add to Watchlist", use_container_width=True)
            
            with col3:
                st.button("🔄 Run Analysis", use_container_width=True)

# Page 3: AI Idea Generator
def ai_idea_generator():
    """AI-powered trading idea generation"""
    st.markdown('<h1 class="main-header">💡 AI Idea Generator</h1>', unsafe_allow_html=True)
    
    # Strategy Selection
    st.markdown("### 🎯 Select Strategy Type")
    
    strategy_col1, strategy_col2 = st.columns(2)
    
    with strategy_col1:
        st.markdown("#### 📈 Swing Trading Ideas")
        swing_timeframe = st.selectbox("Timeframe", ["1-3 Days", "3-7 Days", "1-2 Weeks"])
        swing_risk = st.slider("Max Risk per Trade (%)", 1.0, 5.0, 2.0)
        swing_conviction = st.slider("Min Confidence (%)", 60, 95, 75)
    
    with strategy_col2:
        st.markdown("#### 💰 Long-term Investment Ideas")
        investment_horizon = st.selectbox("Horizon", ["3-6 Months", "6-12 Months", "1-3 Years"])
        fundamental_quality = st.selectbox("Min Quality Grade", ["B", "A", "A+"])
        valuation_preference = st.selectbox("Valuation", ["Value", "Growth", "Quality at Reasonable Price"])
    
    # Generate Ideas
    if st.button("🚀 Generate AI Ideas", type="primary", use_container_width=True):
        with st.spinner("AI analyzing market with smart money concepts..."):
            # Mock swing trading ideas
            swing_ideas = [
                {
                    'symbol': 'RELIANCE',
                    'entry': 2845.50,
                    'stop_loss': 2810.00,
                    'target_1': 2920.00,
                    'target_2': 2985.00,
                    'rr_ratio': 2.8,
                    'confidence': 85,
                    'reasoning': 'Bullish FVG fill at 2845 with volume confirmation. Market structure shows higher highs. Order block support at 2840.',
                    'setup_type': 'FVG Fill + Volume Spike'
                },
                {
                    'symbol': 'TCS',
                    'entry': 3450.00,
                    'stop_loss': 3410.00,
                    'target_1': 3550.00,
                    'target_2': 3620.00,
                    'rr_ratio': 2.5,
                    'confidence': 78,
                    'reasoning': 'Ascending triangle breakout with high volume. Smart money accumulation detected. RSI showing bullish momentum.',
                    'setup_type': 'Breakout + Smart Money'
                }
            ]
            
            # Mock long-term ideas
            longterm_ideas = [
                {
                    'symbol': 'HDFCBANK',
                    'current_price': 1658.20,
                    'target_price': 1950.00,
                    'upside_potential': 17.6,
                    'quality_score': 82,
                    'pe_ratio': 18.7,
                    'roe': 16.8,
                    'thesis': 'Leading private bank with strong ROE and improving asset quality. Beneficiary of economic recovery. Fair valuation with growth visibility.',
                    'holding_period': '12-18 months'
                },
                {
                    'symbol': 'INFY',
                    'current_price': 1587.90,
                    'target_price': 1850.00,
                    'upside_potential': 16.5,
                    'quality_score': 88,
                    'pe_ratio': 25.1,
                    'roe': 19.5,
                    'thesis': 'IT sector leader with strong digital capabilities. Benefiting from global digital transformation. Consistent dividend payer with strong balance sheet.',
                    'holding_period': '18-24 months'
                }
            ]
    
    # Display Swing Trading Ideas
    st.markdown("### 📈 Swing Trading Ideas")
    
    for idea in swing_ideas:
        with st.expander(f"🎯 {idea['symbol']} - Confidence: {idea['confidence']}%"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Setup Type:** {idea['setup_type']}")
                st.markdown(f"**AI Reasoning:** {idea['reasoning']}")
                
                # Entry plan
                st.markdown("**📊 Entry Plan:**")
                entry_plan = f"""
                - **Entry:** ₹{idea['entry']:.2f}
                - **Stop Loss:** ₹{idea['stop_loss']:.2f} ({((idea['entry'] - idea['stop_loss'])/idea['entry']*100):.1f}%)
                - **Target 1:** ₹{idea['target_1']:.2f}
                - **Target 2:** ₹{idea['target_2']:.2f}
                - **Risk/Reward:** {idea['rr_ratio']:.1f}
                """
                st.markdown(entry_plan)
            
            with col2:
                # Visual representation
                fig = go.Figure()
                
                # Add price levels
                fig.add_hline(y=idea['target_2'], line_dash="dash", line_color="green", annotation_text=f"T2: ₹{idea['target_2']}")
                fig.add_hline(y=idea['target_1'], line_dash="dash", line_color="lightgreen", annotation_text=f"T1: ₹{idea['target_1']}")
                fig.add_hline(y=idea['entry'], line_color="blue", line_width=3, annotation_text=f"Entry: ₹{idea['entry']}")
                fig.add_hline(y=idea['stop_loss'], line_color="red", line_width=2, annotation_text=f"SL: ₹{idea['stop_loss']}")
                
                fig.update_layout(
                    title=f"{idea['symbol']} Setup",
                    yaxis_title="Price (₹)",
                    height=250,
                    showlegend=False,
                    template="plotly_dark"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Action buttons
                st.button(f"📊 Analyze {idea['symbol']}", use_container_width=True)
                st.button(f"➕ Add to Watchlist", use_container_width=True)
    
    # Display Long-term Ideas
    st.markdown("### 💰 Long-term Investment Ideas")
    
    for idea in longterm_ideas:
        with st.expander(f"💎 {idea['symbol']} - Quality Score: {idea['quality_score']}/100"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Investment Thesis:** {idea['thesis']}")
                st.markdown(f"**Holding Period:** {idea['holding_period']}")
                
                # Fundamentals
                st.markdown("**📊 Key Fundamentals:**")
                fundamentals = f"""
                - **Current Price:** ₹{idea['current_price']:.2f}
                - **Target Price:** ₹{idea['target_price']:.2f}
                - **Upside Potential:** {idea['upside_potential']:.1f}%
                - **P/E Ratio:** {idea['pe_ratio']:.1f}
                - **ROE:** {idea['roe']:.1f}%
                - **Quality Grade:** {'A+' if idea['quality_score'] >= 85 else 'A' if idea['quality_score'] >= 75 else 'B'}
                """
                st.markdown(fundamentals)
            
            with col2:
                # Quality metrics gauge
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = idea['quality_score'],
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Quality Score"},
                    delta = {'reference': 80},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 80], 'color': "gray"},
                            {'range': [80, 100], 'color': "lightgreen"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                
                fig.update_layout(height=250, template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
                
                # Action buttons
                st.button(f"📈 Detailed Analysis", use_container_width=True)
                st.button(f"💼 Add to Portfolio", use_container_width=True)

# Page 4: Stock Deep Dive
def stock_deep_dive():
    """Individual stock comprehensive analysis"""
    st.markdown('<h1 class="main-header">📈 Stock Deep Dive</h1>', unsafe_allow_html=True)
    
    # Stock Selection with search
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Use watchlist first item if available
        default_symbol = st.session_state.watchlist[0] if st.session_state.watchlist else "RELIANCE"
        symbol = st.selectbox(
            "Select Stock",
            POPULAR_STOCKS,
            index=POPULAR_STOCKS.index(default_symbol) if default_symbol in POPULAR_STOCKS else 0
        )
    
    with col2:
        timeframe = st.selectbox(
            "Timeframe",
            ["Daily", "Weekly", "Monthly", "4-Hour", "1-Hour"],
            index=0
        )
    
    with col3:
        col3a, col3b = st.columns(2)
        with col3a:
            if st.button("➕ Add to Watchlist", use_container_width=True):
                if symbol not in st.session_state.watchlist:
                    st.session_state.watchlist.append(symbol)
                    st.success(f"{symbol} added!")
        with col3b:
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
    
    if symbol:
        # Fetch real-time data for initial check (will be updated with chart data)
        live_data = get_tradingview_data(symbol)
        
        if not live_data:
            st.error(f"Unable to fetch data for {symbol}. Please check if the symbol is correct.")
            return
        
        # Fetch real historical data based on timeframe
        yahoo_prov = get_yahoo_provider()
        
        # Map timeframe to yfinance parameters
        timeframe_map = {
            "Daily": {"period": "6mo", "interval": "1d"},
            "Weekly": {"period": "2y", "interval": "1wk"},
            "Monthly": {"period": "5y", "interval": "1mo"},
            "4-Hour": {"period": "60d", "interval": "1h"},
            "1-Hour": {"period": "30d", "interval": "1h"}
        }
        
        tf_params = timeframe_map.get(timeframe, {"period": "6mo", "interval": "1d"})
        df = yahoo_prov.get_historical_data(symbol, period=tf_params["period"], interval=tf_params["interval"])
        
        if df is None or df.empty:
            st.error(f"Unable to fetch historical data for {symbol}")
            return
        
        # Ensure lowercase column names for consistency
        df.columns = [col.lower() for col in df.columns]
        
        # Update live_data with actual latest values from chart data
        latest_candle = df.iloc[-1]
        live_data['price'] = latest_candle['close']
        live_data['open'] = latest_candle['open']
        live_data['high'] = latest_candle['high']
        live_data['low'] = latest_candle['low']
        live_data['volume'] = latest_candle['volume']
        
        # Calculate change from previous candle
        if len(df) > 1:
            prev_close = df.iloc[-2]['close']
            live_data['change'] = latest_candle['close'] - prev_close
            live_data['change_percent'] = (live_data['change'] / prev_close) * 100 if prev_close != 0 else 0
        
        # Update the price display with chart data
        st.markdown(f"### 💹 {symbol} - Live Market Data")
        st.caption(f"🕐 Last Updated: {df.index[-1].strftime('%Y-%m-%d %H:%M:%S') if hasattr(df.index[-1], 'strftime') else str(df.index[-1])} | Source: {live_data.get('source', 'yahoo_finance')}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current Price", f"₹{live_data['price']:.2f}", f"{live_data['change_percent']:.2f}%")
        with col2:
            st.metric("High", f"₹{live_data['high']:.2f}")
        with col3:
            st.metric("Low", f"₹{live_data['low']:.2f}")
        with col4:
            st.metric("Volume", f"{live_data['volume']:,.0f}")
        
        # Calculate technical indicators
        df['sma_20'] = df['close'].rolling(20).mean()
        df['sma_50'] = df['close'].rolling(50).mean()
        
        # Calculate RSI
        def calculate_rsi(data, period=14):
            delta = data.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        
        df['rsi'] = calculate_rsi(df['close'])
        
        # Main Chart
        st.markdown("### 📊 Price Action & Smart Money Annotations")
        
        # Show chart data range
        start_date = df.index[0]
        end_date = df.index[-1]
        st.caption(f"📅 Chart Period: {start_date.strftime('%Y-%m-%d') if hasattr(start_date, 'strftime') else str(start_date)} to {end_date.strftime('%Y-%m-%d') if hasattr(end_date, 'strftime') else str(end_date)} ({len(df)} {timeframe.lower()} candles)")
        
        fig = create_candlestick_chart(df, f"{symbol} - {timeframe} Chart")
        
        # Add real FVG zones from analysis
        fvg_summary = get_fvg_summary(symbol, df)
        if fvg_summary['all_active_fvgs']:
            for fvg in fvg_summary['all_active_fvgs'][:3]:  # Show top 3
                color = "rgba(0,255,0,0.2)" if fvg['type'] == 'Bullish' else "rgba(255,0,0,0.2)"
                fig.add_hrect(
                    y0=fvg['lower'], y1=fvg['upper'],
                    fillcolor=color, layer="below", line_width=0,
                    annotation_text=f"{fvg['type']} FVG",
                    annotation_position="left"
                )
        
        # Add current price line
        current_price = live_data['price']
        fig.add_hline(
            y=current_price,
            line_dash="dash",
            line_color="yellow",
            line_width=2,
            annotation_text=f"Current: ₹{current_price:.2f}",
            annotation_position="right"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Analysis Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Technical", "🎯 SMC Analysis", "📈 Volume", "💰 Fundamentals", "⚠️ Risk"])
        
        with tab1:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("RSI", f"{df['rsi'].iloc[-1]:.1f}", "Overbought" if df['rsi'].iloc[-1] > 70 else "Oversold" if df['rsi'].iloc[-1] < 30 else "Neutral")
            
            with col2:
                st.metric("Price vs SMA20", f"₹{df['close'].iloc[-1]:.2f}", "Above" if df['close'].iloc[-1] > df['sma_20'].iloc[-1] else "Below")
            
            with col3:
                st.metric("Volume Ratio", "2.3x", "Higher than average")
            
            with col4:
                st.metric("Trend", "Bullish", "📈")
            
            # Technical indicators table
            st.markdown("#### 📈 Technical Indicators")
            
            indicators = {
                'RSI (14)': f"{df['rsi'].iloc[-1]:.1f}",
                'MACD': 'Bullish Crossover',
                'Bollinger Bands': 'Middle Band',
                'SMA 20/50': 'Golden Cross',
                'ATR': f"₹{45.50:.2f}",
                'Williams %R': '-25.3'
            }
            
            indicators_df = pd.DataFrame(list(indicators.items()), columns=['Indicator', 'Value'])
            st.dataframe(indicators_df, use_container_width=True)
        
        with tab2:
            st.markdown("#### 🎯 Smart Money Concepts Analysis")
            
            # Run real SMC analysis
            with st.spinner("Analyzing Smart Money Concepts..."):
                # Create a copy with capitalized columns for SMC analyzer
                df_smc = df.copy()
                df_smc.columns = [col.capitalize() for col in df_smc.columns]
                
                smc_analyzer = SMCAnalyzer()
                smc_analysis = smc_analyzer.analyze(df_smc)
                
                # Show data freshness
                latest_date = df.index[-1]
                st.caption(f"📅 Analysis based on data up to: {latest_date.strftime('%Y-%m-%d %H:%M') if hasattr(latest_date, 'strftime') else str(latest_date)}")
            
            # Display Trading Bias prominently
            bias_data = smc_analysis['bias']
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
                <h2 style="color: white; margin: 0;">Trading Bias: {bias_data['bias']}</h2>
                <p style="color: white; font-size: 18px; margin: 10px 0;">Confidence: {bias_data['confidence']}%</p>
                <div style="background: rgba(255,255,255,0.2); border-radius: 5px; height: 10px; margin-top: 10px;">
                    <div style="background: white; height: 100%; width: {bias_data['confidence']}%; border-radius: 5px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📊 Market Structure")
                ms = smc_analysis['market_structure']
                st.markdown(f"""
                - **Structure:** {ms['structure']}
                - **Trend:** {ms['trend'].upper()} {"📈" if ms['trend'] == 'bullish' else "📉" if ms['trend'] == 'bearish' else "➡️"}
                - **Swing Highs:** {len(ms['swing_highs'])}
                - **Swing Lows:** {len(ms['swing_lows'])}
                """)
                
                if ms['last_high']:
                    st.markdown(f"- **Last High:** ₹{ms['last_high']['price']:.2f}")
                if ms['last_low']:
                    st.markdown(f"- **Last Low:** ₹{ms['last_low']['price']:.2f}")
                
                st.markdown("### 🎯 Order Blocks")
                obs = smc_analysis['order_blocks']
                st.markdown(f"""
                - **Bullish OBs:** {len(obs['bullish'])} active
                - **Bearish OBs:** {len(obs['bearish'])} active
                """)
                
                if obs['bullish']:
                    st.markdown("**Active Bullish Order Blocks:**")
                    for ob in obs['bullish'][:2]:
                        st.markdown(f"  • ₹{ob['low']:.2f}-₹{ob['high']:.2f} ({ob['strength']})")
                
                if obs['bearish']:
                    st.markdown("**Active Bearish Order Blocks:**")
                    for ob in obs['bearish'][:2]:
                        st.markdown(f"  • ₹{ob['low']:.2f}-₹{ob['high']:.2f} ({ob['strength']})")
            
            with col2:
                st.markdown("### 💧 Liquidity Zones")
                liq = smc_analysis['liquidity_zones']
                
                if liq['liquidity_above']:
                    st.markdown(f"- **Liquidity Above:** ₹{liq['liquidity_above']:.2f} 🎯")
                if liq['liquidity_below']:
                    st.markdown(f"- **Liquidity Below:** ₹{liq['liquidity_below']:.2f} 🎯")
                
                st.markdown(f"- **Equal Highs:** {len(liq['equal_highs'])}")
                st.markdown(f"- **Equal Lows:** {len(liq['equal_lows'])}")
                st.markdown(f"- **Recent Stop Hunts:** {len(liq['stop_hunts'])}")
                
                if liq['stop_hunts']:
                    st.markdown("**Recent Sweeps:**")
                    for hunt in liq['stop_hunts'][-3:]:
                        st.markdown(f"  • {hunt['type']} at ₹{hunt['price']:.2f}")
                
                st.markdown("### 🧠 Smart Money Activity")
                st.markdown(f"**{smc_analysis['smart_money_activity']}**")
                
                st.markdown("### 🔑 Key Levels")
                key_levels = smc_analysis['key_levels']
                
                if key_levels['nearest_support']:
                    st.markdown(f"- **Nearest Support:** ₹{key_levels['nearest_support'][1]:.2f}")
                    st.markdown(f"  _{key_levels['nearest_support'][0]}_")
                
                if key_levels['nearest_resistance']:
                    st.markdown(f"- **Nearest Resistance:** ₹{key_levels['nearest_resistance'][1]:.2f}")
                    st.markdown(f"  _{key_levels['nearest_resistance'][0]}_")
            
            # BOS/CHOCH Section
            st.markdown("---")
            st.markdown("### ⚡ Break of Structure (BOS) & Change of Character (CHOCH)")
            
            bos_choch = smc_analysis['bos_choch']
            col1, col2 = st.columns(2)
            
            with col1:
                if bos_choch['last_bos']:
                    bos = bos_choch['last_bos']
                    st.success(f"**Last BOS:** {bos['type']} at ₹{bos['price']:.2f}")
                else:
                    st.info("No recent BOS detected")
            
            with col2:
                if bos_choch['last_choch']:
                    choch = bos_choch['last_choch']
                    st.warning(f"**Last CHOCH:** {choch['type']} at ₹{choch['price']:.2f}")
                else:
                    st.info("No recent CHOCH detected")
            
            # Bias Reasons
            st.markdown("---")
            st.markdown("### 📋 Bias Reasoning")
            for reason in bias_data['reasons']:
                st.markdown(f"✓ {reason}")
        
        with tab3:
            st.markdown("#### 📈 Volume Profile Analysis")
            
            # Run real volume analysis
            with st.spinner("Analyzing volume patterns..."):
                vol_analyzer = VolumeAnalyzer()
                vol_analysis = vol_analyzer.analyze(df_smc)  # Use same data as SMC
            
            # Volume profile chart
            fig = create_volume_profile_chart(df)
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 📊 Volume Metrics")
                st.metric("Average Volume", f"{vol_analysis['avg_volume']:,.0f}")
                st.metric("Current Volume", f"{vol_analysis['current_volume']:,.0f}")
                st.metric("Volume Ratio", f"{vol_analysis['volume_ratio']:.2f}x", 
                         "Above Average" if vol_analysis['volume_ratio'] > 1 else "Below Average")
                st.markdown(f"**Trend:** {vol_analysis['volume_trend']}")
            
            with col2:
                st.markdown("### 🎯 Volume Profile")
                vp = vol_analysis['volume_profile']
                st.markdown(f"""
                - **Point of Control:** ₹{vp['poc']:.2f}
                - **Value Area High:** ₹{vp['vah']:.2f}
                - **Value Area Low:** ₹{vp['val']:.2f}
                - **Current Position:** {vp['current_position']}
                - **Volume Gap:** {'Yes' if vol_analysis['volume_gaps'] else 'No'}
                """)
            
            with col3:
                st.markdown("### 💪 Pressure Analysis")
                
                # Buying pressure gauge
                buying_pct = vol_analysis['buying_pressure']
                selling_pct = vol_analysis['selling_pressure']
                
                st.markdown(f"**Buying Pressure:** {buying_pct:.1f}%")
                st.progress(buying_pct / 100)
                
                st.markdown(f"**Selling Pressure:** {selling_pct:.1f}%")
                st.progress(selling_pct / 100)
                
                st.markdown(f"**Institutional Activity:** {vol_analysis['institutional_activity']}")
                
                # Determine phase
                if buying_pct > 60:
                    st.success("✅ Accumulation Phase")
                elif selling_pct > 60:
                    st.error("❌ Distribution Phase")
                else:
                    st.info("➡️ Neutral Phase")
        
        with tab4:
            st.markdown("#### 💰 Fundamental Analysis")
            
            # Create fund_analyzer instance
            fund_analyzer = FundamentalAnalyzer()
            
            # Fetch real fundamental data with caching
            @st.cache_data(ttl=300, show_spinner=False)  # 5 minute cache for fundamentals
            def get_fundamentals(symbol, exchange):
                analyzer = FundamentalAnalyzer()
                return analyzer.analyze(symbol, exchange)
            
            with st.spinner("Fetching fundamental data..."):
                try:
                    fundamentals = get_fundamentals(symbol, INDIAN_STOCK_EXCHANGE)
                except Exception as e:
                    st.error(f"Error fetching fundamentals: {e}")
                    fundamentals = {'error': True}
            
            # Display investment rating prominently
            if not fundamentals.get('error'):
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                            padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
                    <h2 style="color: white; margin: 0;">{fundamentals['company_name']}</h2>
                    <p style="color: white; font-size: 16px; margin: 5px 0;">{fundamentals['sector']} | {fundamentals['industry']}</p>
                    <h3 style="color: white; margin: 10px 0;">Investment Rating: {fundamentals['investment_rating']}</h3>
                    <p style="color: white; font-size: 18px; margin: 0;">Quality Score: {fundamentals['overall_quality']:.1f}/100</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("### 📊 Valuation Metrics")
                    st.markdown(f"""
                    - **Market Cap:** {fund_analyzer.format_market_cap(fundamentals['market_cap'])}
                    - **P/E Ratio:** {fundamentals['pe_ratio']:.2f}
                    - **Forward P/E:** {fundamentals['forward_pe']:.2f}
                    - **P/B Ratio:** {fundamentals['pb_ratio']:.2f}
                    - **P/S Ratio:** {fundamentals['ps_ratio']:.2f}
                    - **PEG Ratio:** {fundamentals['peg_ratio']:.2f}
                    """)
                
                with col2:
                    st.markdown("### 💹 Profitability Metrics")
                    st.markdown(f"""
                    - **ROE:** {fundamentals['roe']:.2f}%
                    - **ROA:** {fundamentals['roa']:.2f}%
                    - **Profit Margin:** {fundamentals['profit_margin']:.2f}%
                    - **Operating Margin:** {fundamentals['operating_margin']:.2f}%
                    - **Free Cash Flow:** {fund_analyzer.format_large_number(fundamentals['free_cashflow'])}
                    """)
                
                with col3:
                    st.markdown("### 📈 Growth & Dividend")
                    st.markdown(f"""
                    - **Revenue Growth:** {fundamentals['revenue_growth']:.2f}%
                    - **Earnings Growth:** {fundamentals['earnings_growth']:.2f}%
                    - **Dividend Yield:** {fundamentals['dividend_yield']:.2f}%
                    - **Payout Ratio:** {fundamentals['payout_ratio']:.2f}%
                    - **Beta:** {fundamentals['beta']:.2f}
                    """)
                
                # Financial Health
                st.markdown("---")
                st.markdown("### 🏥 Financial Health")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    - **Debt/Equity:** {fundamentals['debt_to_equity']:.2f}
                    - **Current Ratio:** {fundamentals['current_ratio']:.2f}
                    - **Quick Ratio:** {fundamentals['quick_ratio']:.2f}
                    """)
                    
                    # Debt health indicator
                    if fundamentals['debt_to_equity'] < 0.5:
                        st.success("✅ Low Debt - Healthy Balance Sheet")
                    elif fundamentals['debt_to_equity'] < 1.0:
                        st.info("ℹ️ Moderate Debt - Manageable")
                    else:
                        st.warning("⚠️ High Debt - Monitor Closely")
                
                with col2:
                    st.markdown(f"""
                    - **52 Week High:** ₹{fundamentals['fifty_two_week_high']:.2f}
                    - **52 Week Low:** ₹{fundamentals['fifty_two_week_low']:.2f}
                    - **Book Value:** ₹{fundamentals['book_value']:.2f}
                    """)
                    
                    # Price position
                    current_price = live_data['price']
                    high_52w = fundamentals['fifty_two_week_high']
                    low_52w = fundamentals['fifty_two_week_low']
                    
                    if high_52w > 0 and low_52w > 0:
                        position = ((current_price - low_52w) / (high_52w - low_52w)) * 100
                        st.metric("52W Position", f"{position:.1f}%", "From Low to High")
                
                # Analyst Recommendations
                if fundamentals['number_of_analyst_opinions'] > 0:
                    st.markdown("---")
                    st.markdown("### 👥 Analyst Recommendations")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Target Price", f"₹{fundamentals['target_mean_price']:.2f}")
                    with col2:
                        upside = ((fundamentals['target_mean_price'] - current_price) / current_price) * 100
                        st.metric("Potential Upside", f"{upside:.1f}%")
                    with col3:
                        st.metric("Analysts Covering", f"{fundamentals['number_of_analyst_opinions']}")
                    
                    st.markdown(f"**Consensus:** {fundamentals['recommendation'].upper()}")
                
                # Quality assessment chart
                st.markdown("---")
                st.markdown("### 📊 Quality Score Breakdown")
                
                quality_data = fundamentals['quality_scores']
                
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    name='Quality Score',
                    x=list(quality_data.keys()),
                    y=list(quality_data.values()),
                    marker_color=['#10b981' if v >= 70 else '#f59e0b' if v >= 50 else '#ef4444' for v in quality_data.values()],
                    text=[f"{v:.0f}" for v in quality_data.values()],
                    textposition='auto',
                ))
                
                fig.update_layout(
                    title=f"Overall Quality: {fundamentals['overall_quality']:.1f}/100",
                    yaxis_title="Score",
                    yaxis_range=[0, 100],
                    height=400,
                    template="plotly_dark",
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"Unable to fetch fundamental data for {symbol}. Data may not be available.")
                st.info("Try another stock from the Nifty 500 list.")
        
        with tab5:
            st.markdown("#### ⚠️ Risk Assessment")
            
            # Calculate real risk metrics
            returns = df['close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252) * 100  # Annualized
            
            # Calculate ATR (Average True Range)
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(14).mean().iloc[-1]
            
            # Calculate max drawdown
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min() * 100
            
            # Risk rating
            if volatility < 20:
                risk_rating = "Low"
            elif volatility < 35:
                risk_rating = "Medium"
            else:
                risk_rating = "High"
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📉 Volatility Metrics")
                st.metric("Historical Volatility", f"{volatility:.1f}%")
                st.metric("ATR (14)", f"₹{atr:.2f}")
                st.metric("Max Drawdown", f"{max_drawdown:.1f}%")
                
                if fundamentals.get('beta'):
                    st.metric("Beta", f"{fundamentals['beta']:.2f}")
                
                # Risk rating with color
                if risk_rating == "Low":
                    st.success(f"**Risk Rating:** {risk_rating} ✅")
                elif risk_rating == "Medium":
                    st.warning(f"**Risk Rating:** {risk_rating} ⚠️")
                else:
                    st.error(f"**Risk Rating:** {risk_rating} 🔴")
            
            with col2:
                st.markdown("### 💰 Position Sizing")
                
                # Position sizing calculator
                portfolio_size = st.number_input("Portfolio Size (₹)", value=1000000, step=100000)
                risk_per_trade = st.slider("Risk per Trade (%)", 1.0, 5.0, 2.0, 0.5)
                
                current_price = live_data['price']
                stop_loss_pct = st.slider("Stop Loss (%)", 1.0, 10.0, 2.0, 0.5)
                
                # Calculate position size
                risk_amount = portfolio_size * (risk_per_trade / 100)
                stop_loss_price = current_price * (1 - stop_loss_pct / 100)
                risk_per_share = current_price - stop_loss_price
                
                if risk_per_share > 0:
                    shares = int(risk_amount / risk_per_share)
                    position_value = shares * current_price
                    allocation_pct = (position_value / portfolio_size) * 100
                    
                    # Targets based on ATR
                    target_1 = current_price + (atr * 1.5)
                    target_2 = current_price + (atr * 2.5)
                    
                    reward_1 = target_1 - current_price
                    reward_2 = target_2 - current_price
                    rr_ratio_1 = reward_1 / risk_per_share if risk_per_share > 0 else 0
                    rr_ratio_2 = reward_2 / risk_per_share if risk_per_share > 0 else 0
                    
                    st.markdown(f"""
                    **Calculated Position:**
                    - **Shares:** {shares}
                    - **Position Value:** ₹{position_value:,.0f}
                    - **Allocation:** {allocation_pct:.1f}%
                    - **Stop Loss:** ₹{stop_loss_price:.2f}
                    - **Target 1:** ₹{target_1:.2f} (R:R {rr_ratio_1:.1f}:1)
                    - **Target 2:** ₹{target_2:.2f} (R:R {rr_ratio_2:.1f}:1)
                    - **Risk Amount:** ₹{risk_amount:,.0f}
                    """)
            
            # Risk analysis
            st.markdown("**🎯 Risk-Reward Analysis:**")
            
            risk_data = {
                'Entry': df['close'].iloc[-1],
                'Stop Loss': df['close'].iloc[-1] * 0.98,
                'Target 1': df['close'].iloc[-1] * 1.05,
                'Target 2': df['close'].iloc[-1] * 1.08
            }
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=list(risk_data.keys()),
                y=list(risk_data.values()),
                mode='lines+markers',
                name='Price Levels',
                line=dict(color='blue', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title="Risk-Reward Levels",
                yaxis_title="Price (₹)",
                height=400,
                template="plotly_dark"
            )
            
            st.plotly_chart(fig, use_container_width=True)

# Page 5: Portfolio Manager
def portfolio_manager():
    """Portfolio management and analysis"""
    st.markdown('<h1 class="main-header">💼 Portfolio Manager</h1>', unsafe_allow_html=True)
    
    # Portfolio Overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Portfolio Value", "₹25,45,890", "₹45,890 (1.8%)")
    
    with col2:
        st.metric("Total P&L", "₹1,25,890", "5.2%")
    
    with col3:
        st.metric("Win Rate", "68%", "3%")
    
    with col4:
        st.metric("Sharpe Ratio", "1.85", "0.15")
    
    # Portfolio Composition
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Portfolio Composition")
        
        # Mock portfolio data
        portfolio_data = {
            'RELIANCE': 5000,
            'TCS': 4500,
            'HDFCBANK': 3500,
            'INFY': 3000,
            'ICICIBANK': 2500
        }
        
        fig = go.Figure(data=[go.Pie(
            labels=list(portfolio_data.keys()),
            values=list(portfolio_data.values()),
            hole=0.3
        )])
        
        fig.update_layout(
            title="Portfolio Allocation",
            height=400,
            template="plotly_dark"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Performance Chart")
        
        # Mock performance data
        dates = pd.date_range(start='2023-01-01', end=datetime.now(), freq='D')
        portfolio_value = np.cumsum(np.random.randn(len(dates)) * 0.01 + 0.0005) * 100000 + 2000000
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=portfolio_value,
            mode='lines',
            name='Portfolio Value',
            line=dict(color='blue', width=2)
        ))
        
        fig.update_layout(
            title="Portfolio Performance",
            yaxis_title="Value (₹)",
            height=400,
            template="plotly_dark"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Holdings Table with live prices
    st.markdown("### 💼 Current Holdings")
    
    # Fetch live prices for holdings
    holdings_symbols = ['RELIANCE', 'TCS', 'HDFCBANK']
    live_prices = get_multiple_prices(holdings_symbols)
    
    holdings_data = [
        {
            'symbol': 'RELIANCE',
            'quantity': 100,
            'avg_cost': 2750.00,
            'current_price': live_prices.get('RELIANCE', 2850.75),
            'current_value': live_prices.get('RELIANCE', 2850.75) * 100,
            'pnl': (live_prices.get('RELIANCE', 2850.75) - 2750.00) * 100,
            'pnl_percent': ((live_prices.get('RELIANCE', 2850.75) - 2750.00) / 2750.00) * 100,
            'weight': 11.2,
            'sector': 'Energy'
        },
        {
            'symbol': 'TCS',
            'quantity': 50,
            'avg_cost': 3400.00,
            'current_price': live_prices.get('TCS', 3456.40),
            'current_value': live_prices.get('TCS', 3456.40) * 50,
            'pnl': (live_prices.get('TCS', 3456.40) - 3400.00) * 50,
            'pnl_percent': ((live_prices.get('TCS', 3456.40) - 3400.00) / 3400.00) * 100,
            'weight': 6.8,
            'sector': 'Technology'
        },
        {
            'symbol': 'HDFCBANK',
            'quantity': 200,
            'avg_cost': 1620.00,
            'current_price': live_prices.get('HDFCBANK', 1658.20),
            'current_value': live_prices.get('HDFCBANK', 1658.20) * 200,
            'pnl': (live_prices.get('HDFCBANK', 1658.20) - 1620.00) * 200,
            'pnl_percent': ((live_prices.get('HDFCBANK', 1658.20) - 1620.00) / 1620.00) * 100,
            'weight': 13.0,
            'sector': 'Banking'
        }
    ]
    
    holdings_df = pd.DataFrame(holdings_data)
    
    def color_pnl(val):
        if val > 0:
            return 'color: #00ff88'
        elif val < 0:
            return 'color: #ff4444'
        else:
            return 'color: white'
    
    styled_holdings = holdings_df.style.applymap(color_pnl, subset=['pnl', 'pnl_percent'])
    st.dataframe(styled_holdings, use_container_width=True)
    
    # Risk Analysis
    st.markdown("### ⚠️ Risk Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Portfolio Risk Metrics:**")
        st.markdown("""
        - **Portfolio Beta:** 1.05
        - **Value at Risk (95%):** ₹1,25,000
        - **Maximum Drawdown:** -12.3%
        - **Volatility (Annual):** 18.5%
        - **Correlation to Nifty:** 0.78
        """)
    
    with col2:
        st.markdown("**Sector Concentration:**")
        st.markdown("""
        - **Technology:** 35% (High)
        - **Banking:** 25% (Medium)
        - **Energy:** 20% (Medium)
        - **Pharma:** 12% (Low)
        - **Others:** 8% (Low)
        """)
        
        if st.button("🔄 Rebalance Portfolio", use_container_width=True):
            st.info("Portfolio rebalancing recommendations generated")

# Page 6: Backtesting Lab
def backtesting_lab():
    """Strategy backtesting and optimization"""
    st.markdown('<h1 class="main-header">🧪 Backtesting Lab</h1>', unsafe_allow_html=True)
    
    # Strategy Configuration
    st.markdown("### 🎛️ Strategy Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Strategy Parameters")
        
        strategy_name = st.text_input("Strategy Name", "SMC FVG Fill Strategy")
        
        # Entry conditions
        st.markdown("**Entry Conditions:**")
        fvg_required = st.checkbox("Require Unmitigated FVG")
        volume_confirmation = st.checkbox("Volume Confirmation Required")
        structure_alignment = st.checkbox("Market Structure Alignment")
        
        # Exit conditions
        st.markdown("**Exit Conditions:**")
        target_rr = st.slider("Take Profit (R Multiple)", 1.0, 5.0, 2.5)
        stop_loss_atr = st.slider("Stop Loss (ATR Multiple)", 1.0, 3.0, 2.0)
        
        # Position sizing
        position_size = st.slider("Position Size (%)", 0.5, 5.0, 2.0)
    
    with col2:
        st.markdown("#### 📈 Backtesting Parameters")
        
        # Time period
        start_date = st.date_input("Start Date", datetime(2021, 1, 1))
        end_date = st.date_input("End Date", datetime.now())
        
        # Universe selection
        universe = st.multiselect(
            "Stock Universe",
            ["NIFTY 50", "NIFTY 100", "NIFTY 200", "Custom"],
            default=["NIFTY 50"]
        )
        
        # Execution settings
        slippage = st.slider("Slippage (%)", 0.01, 0.5, 0.1)
        brokerage = st.slider("Brokerage per Trade (₹)", 0, 500, 20)
        
        # Advanced settings
        st.markdown("**Advanced Settings:**")
        walk_forward = st.checkbox("Walk-Forward Analysis")
        monte_carlo = st.checkbox("Monte Carlo Simulation")
    
    # Run Backtest
    if st.button("🚀 Run Backtest", type="primary", use_container_width=True):
        with st.spinner("Running comprehensive backtesting analysis..."):
            # Mock backtest results
            backtest_results = {
                'total_return': 45.8,
                'annualized_return': 18.3,
                'max_drawdown': -12.5,
                'sharpe_ratio': 1.85,
                'sortino_ratio': 2.45,
                'win_rate': 68.5,
                'profit_factor': 2.15,
                'total_trades': 156,
                'winning_trades': 107,
                'losing_trades': 49,
                'avg_trade_return': 2.85,
                'avg_trade_duration': 8.5,
                'var_95': 25000
            }
            
            # Show results
            st.markdown("### 📊 Backtest Results")
            
            # Performance metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Return", f"{backtest_results['total_return']:.1f}%")
                st.metric("Sharpe Ratio", f"{backtest_results['sharpe_ratio']:.2f}")
            
            with col2:
                st.metric("Max Drawdown", f"{backtest_results['max_drawdown']:.1f}%")
                st.metric("Win Rate", f"{backtest_results['win_rate']:.1f}%")
            
            with col3:
                st.metric("Total Trades", backtest_results['total_trades'])
                st.metric("Profit Factor", f"{backtest_results['profit_factor']:.2f}")
            
            with col4:
                st.metric("Avg Trade", f"{backtest_results['avg_trade_return']:.1f}%")
                st.metric("Avg Duration", f"{backtest_results['avg_trade_duration']:.1f} days")
            
            # Equity curve
            st.markdown("### 📈 Equity Curve")
            
            # Generate mock equity curve
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            initial_capital = 1000000
            
            # Simulate equity curve with realistic drawdowns
            returns = np.random.normal(0.0008, 0.02, len(dates))  # Daily returns
            equity_curve = initial_capital * np.cumprod(1 + returns)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=equity_curve,
                mode='lines',
                name='Strategy Equity',
                line=dict(color='blue', width=2)
            ))
            
            # Add benchmark (Nifty returns)
            benchmark_returns = np.random.normal(0.0006, 0.015, len(dates))
            benchmark_curve = initial_capital * np.cumprod(1 + benchmark_returns)
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=benchmark_curve,
                mode='lines',
                name='Nifty Benchmark',
                line=dict(color='orange', width=1, dash='dash')
            ))
            
            fig.update_layout(
                title="Strategy vs Benchmark Performance",
                yaxis_title="Portfolio Value (₹)",
                height=500,
                template="plotly_dark"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Trade analysis
            st.markdown("### 📋 Trade Analysis")
            
            tab1, tab2, tab3 = st.tabs(["Trade Log", "Monthly Returns", "Risk Analysis"])
            
            with tab1:
                # Mock trade log
                trade_data = []
                for i in range(20):
                    entry_price = np.random.uniform(100, 5000)
                    exit_price = entry_price * np.random.uniform(0.95, 1.08)
                    pnl_percent = (exit_price - entry_price) / entry_price * 100
                    
                    trade_data.append({
                        'date': f"2024-{np.random.randint(1,13):02d}-{np.random.randint(1,29):02d}",
                        'symbol': np.random.choice(['RELIANCE', 'TCS', 'HDFCBANK', 'INFY']),
                        'entry': f"₹{entry_price:.2f}",
                        'exit': f"₹{exit_price:.2f}",
                        'pnl_percent': f"{pnl_percent:.2f}%",
                        'duration': np.random.randint(1, 30),
                        'type': 'BUY' if pnl_percent > 0 else 'SELL'
                    })
                
                trade_df = pd.DataFrame(trade_data)
                
                def color_trade_type(val):
                    if val == 'BUY':
                        return 'background-color: rgba(46, 213, 115, 0.3)'
                    else:
                        return 'background-color: rgba(255, 71, 87, 0.3)'
                
                styled_trades = trade_df.style.applymap(color_trade_type, subset=['type'])
                st.dataframe(styled_trades, use_container_width=True)
            
            with tab2:
                # Monthly returns heatmap
                monthly_returns = np.random.normal(1.5, 4.0, 36)  # 3 years of monthly returns
                
                returns_matrix = monthly_returns.reshape(3, 12)
                
                fig = go.Figure(data=go.Heatmap(
                    z=returns_matrix,
                    x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                    y=['2024', '2023', '2022'],
                    colorscale='RdYlGn',
                    colorbar=dict(title="Return (%)")
                ))
                
                fig.update_layout(
                    title="Monthly Returns Heatmap",
                    height=400,
                    template="plotly_dark"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                # Risk metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Risk Metrics:**")
                    st.markdown(f"""
                    - **Value at Risk (95%):** ₹{backtest_results['var_95']:,.0f}
                    - **Conditional VaR:** ₹35,000
                    - **Beta:** 0.95
                    - **Correlation to Market:** 0.78
                    - **Downside Deviation:** 12.3%
                    """)
                
                with col2:
                    st.markdown("**Drawdown Analysis:**")
                    st.markdown("""
                    - **Max Drawdown:** -12.5%
                    - **Avg Drawdown:** -4.2%
                    - **Drawdown Duration:** 45 days
                    - **Recovery Time:** 28 days
                    - **Underwater Periods:** 8
                    """)
                
                # Drawdown chart
                drawdown_data = np.maximum.accumulate(equity_curve) - equity_curve
                drawdown_percent = drawdown_data / np.maximum.accumulate(equity_curve) * 100
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=drawdown_percent,
                    mode='lines',
                    name='Drawdown',
                    fill='tonexty',
                    line=dict(color='red', width=1)
                ))
                
                fig.update_layout(
                    title="Portfolio Drawdown",
                    yaxis_title="Drawdown (%)",
                    height=300,
                    template="plotly_dark"
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    # Strategy Optimization
    st.markdown("### ⚡ Strategy Optimization")
    
    if st.button("🎯 Run Parameter Optimization", use_container_width=True):
        with st.spinner("Optimizing strategy parameters..."):
            st.success("Optimization complete! Best parameters found:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Optimal Parameters:**")
                st.markdown("""
                - **FVG Strength:** Strong
                - **Volume Multiplier:** 1.8x
                - **Stop Loss:** 1.8 ATR
                - **Take Profit:** 3.2R
                - **Position Size:** 2.5%
                """)
            
            with col2:
                st.markdown("**Optimized Performance:**")
                st.markdown("""
                - **Total Return:** 52.3%
                - **Sharpe Ratio:** 2.15
                - **Max Drawdown:** -10.2%
                - **Win Rate:** 72.5%
                - **Profit Factor:** 2.85
                """)

# Page 7: Admin Panel
def admin_panel():
    """System administration and monitoring"""
    st.markdown('<h1 class="main-header">⚙️ Admin Panel</h1>', unsafe_allow_html=True)
    
    # System Status
    st.markdown("### 🖥️ System Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>API Server</h3>
            <h2>🟢 Online</h2>
            <p>Uptime: 99.8%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>Database</h3>
            <h2>🟢 Healthy</h2>
            <p>Connections: 12/20</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>Redis Cache</h3>
            <h2>🟢 Active</h2>
            <p>Memory: 45%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>Data Pipeline</h3>
            <h2>🟢 Running</h2>
            <p>Queue: 23 items</p>
        </div>
        """, unsafe_allow_html=True)
    
    # User Management
    st.markdown("### 👥 User Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Mock user data
        user_data = [
            {'email': 'admin@tradingframework.com', 'role': 'Admin', 'last_login': '2 hours ago', 'status': 'Active'},
            {'email': 'analyst1@company.com', 'role': 'Analyst', 'last_login': '1 day ago', 'status': 'Active'},
            {'email': 'trader1@company.com', 'role': 'Trader', 'last_login': '3 hours ago', 'status': 'Active'},
            {'email': 'analyst2@company.com', 'role': 'Analyst', 'last_login': '1 week ago', 'status': 'Inactive'}
        ]
        
        users_df = pd.DataFrame(user_data)
        st.dataframe(users_df, use_container_width=True)
    
    with col2:
        st.markdown("**User Actions:**")
        if st.button("➕ Add New User", use_container_width=True):
            st.info("User creation form")
        if st.button("🔄 Reset Password", use_container_width=True):
            st.info("Password reset sent")
        if st.button("🚀 Send Alert", use_container_width=True):
            st.info("System alert sent to all users")
    
    # System Metrics
    st.markdown("### 📊 System Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Performance Metrics:**")
        
        # API response times
        api_metrics = {
            'Market Data': 45,
            'Analysis': 230,
            'Backtest': 1250,
            'Portfolio': 85
        }
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Response Time (ms)',
            x=list(api_metrics.keys()),
            y=list(api_metrics.values()),
            marker_color='rgba(58, 71, 80, 0.6)',
            marker_line_color='rgba(58, 71, 80, 1.0)',
            marker_line_width=2
        ))
        
        fig.update_layout(
            title="API Response Times",
            yaxis_title="Time (ms)",
            height=400,
            template="plotly_dark"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Resource Usage:**")
        
        # Mock resource usage
        cpu_usage = np.random.randint(20, 80, 24)
        memory_usage = np.random.randint(30, 70, 24)
        hours = list(range(24))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            name='CPU Usage (%)',
            x=hours,
            y=cpu_usage,
            mode='lines+markers',
            line=dict(color='blue')
        ))
        
        fig.add_trace(go.Scatter(
            name='Memory Usage (%)',
            x=hours,
            y=memory_usage,
            mode='lines+markers',
            line=dict(color='red')
        ))
        
        fig.update_layout(
            title="Resource Usage (Last 24 Hours)",
            yaxis_title="Usage (%)",
            height=400,
            template="plotly_dark"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Data Source Status
    st.markdown("### 📡 Data Source Status")
    
    data_sources = [
        {'source': 'TradingView Webhooks', 'status': 'Active', 'last_update': '2 min ago', 'errors': 0},
        {'source': 'Yahoo Finance API', 'status': 'Active', 'last_update': '5 min ago', 'errors': 0},
        {'source': 'NSE API', 'status': 'Active', 'last_update': '1 min ago', 'errors': 2},
        {'source': 'Screener.in', 'status': 'Active', 'last_update': '10 min ago', 'errors': 0}
    ]
    
    sources_df = pd.DataFrame(data_sources)
    
    def color_status(val):
        if val == 'Active':
            return 'background-color: rgba(46, 213, 115, 0.3)'
        else:
            return 'background-color: rgba(255, 71, 87, 0.3)'
    
    styled_sources = sources_df.style.applymap(color_status, subset=['status'])
    st.dataframe(styled_sources, use_container_width=True)
    
    # System Actions
    st.markdown("### 🔧 System Actions")
    
    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
    
    with action_col1:
        if st.button("🔄 Restart Services", use_container_width=True):
            st.success("Services restarted successfully")
    
    with action_col2:
        if st.button("🧹 Clear Cache", use_container_width=True):
            st.success("Cache cleared successfully")
    
    with action_col3:
        if st.button("📦 Backup Database", use_container_width=True):
            st.success("Database backup initiated")
    
    with action_col4:
        if st.button("📊 Generate Report", use_container_width=True):
            st.success("System report generated")

# Main Application
def main():
    """Main application entry point"""
    navigation()
    
    # Natural Language Query Interface (always visible)
    st.markdown("---")
    st.markdown("### 🤖 Ask Me Anything")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_query = st.text_input(
            "Natural Language Query",
            placeholder="e.g., What is the price of RELIANCE? | Compare TCS and INFY | Show me best stocks",
            label_visibility="collapsed"
        )
    
    with col2:
        query_button = st.button("🔍 Ask", use_container_width=True, type="primary")
    
    # Process query
    if query_button and user_query:
        with st.spinner("Analyzing your query..."):
            handler = NLPQueryHandler()
            result = handler.process_query(user_query)
            
            # Display result in an expander
            with st.expander("📊 Query Result", expanded=True):
                st.markdown(result['message'])
                
                # Add quick actions based on result type
                if result['type'] in ['price', 'buy_signal', 'sell_signal', 'analysis', 'technical']:
                    if 'symbol' in result:
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"📈 Deep Dive: {result['symbol']}", key="deep_dive_btn"):
                                st.session_state.page = 'stock_analysis'
                                st.rerun()
                        with col2:
                            if st.button(f"➕ Add {result['symbol']} to Watchlist", key="add_watchlist_btn"):
                                if result['symbol'] not in st.session_state.watchlist:
                                    st.session_state.watchlist.append(result['symbol'])
                                    st.success(f"{result['symbol']} added to watchlist!")
    
    # Example queries
    with st.expander("💡 Example Queries"):
        st.markdown("""
        **Price & Basic Info:**
        - "What is the price of RELIANCE?"
        - "Show me TCS price"
        
        **Comparisons:**
        - "Compare TCS and INFY"
        - "TCS vs WIPRO"
        
        **Signals & Recommendations:**
        - "Should I buy HDFCBANK?"
        - "Is it time to sell ICICIBANK?"
        
        **Analysis:**
        - "Analyze RELIANCE"
        - "Technical analysis of TCS"
        - "Fundamentals of INFY"
        
        **Screening:**
        - "Show me best stocks"
        - "Find good opportunities"
        
        **Specific Metrics:**
        - "Volume of BHARTIARTL"
        - "Trend of ITC"
        - "Risk of HINDUNILVR"
        """)
    
    st.markdown("---")
    
    # Route to appropriate page
    if st.session_state.page == 'dashboard':
        market_dashboard()
    elif st.session_state.page == 'screener':
        smart_screener()
    elif st.session_state.page == 'idea_generator':
        ai_idea_generator()
    elif st.session_state.page == 'stock_analysis':
        stock_deep_dive()
    elif st.session_state.page == 'portfolio':
        portfolio_manager()
    elif st.session_state.page == 'backtesting':
        backtesting_lab()
    elif st.session_state.page == 'admin':
        admin_panel()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
        Enterprise Stock Trading Framework v1.0 | Powered by Smart Money Concepts & AI
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
