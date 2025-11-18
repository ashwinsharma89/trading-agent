"""
Natural Language Query Handler
Processes user queries and provides relevant trading insights
"""

import re
from typing import Dict, List, Tuple
from market_data_fetcher import MarketDataFetcher
from fundamental_analyzer import FundamentalAnalyzer
from smc_analyzer import SMCAnalyzer
from yahoo_provider import get_yahoo_provider


class NLPQueryHandler:
    """
    Handle natural language queries about stocks and market
    """
    
    def __init__(self):
        self.fetcher = MarketDataFetcher()
        self.fund_analyzer = FundamentalAnalyzer()
        self.yahoo_prov = get_yahoo_provider()
        
        # Query patterns
        self.patterns = {
            'price': r'(?:price|value|cost|trading at|current price) (?:of |for )?(\w+)',
            'compare': r'compare (\w+) (?:and|vs|versus|with) (\w+)',
            'best': r'(?:best|top|good) (?:stocks?|picks?|opportunities?) (?:in |for )?(\w+)?',
            'buy': r'(?:should i buy|buy signal|good to buy) (\w+)',
            'sell': r'(?:should i sell|sell signal|time to sell) (\w+)',
            'analysis': r'(?:analyze|analysis|review) (\w+)',
            'fundamentals': r'(?:fundamentals?|financial|valuation) (?:of |for )?(\w+)',
            'technical': r'(?:technical|chart|smc|smart money) (?:analysis |for )?(\w+)',
            'volume': r'(?:volume|trading volume) (?:of |for )?(\w+)',
            'trend': r'(?:trend|direction|momentum) (?:of |for )?(\w+)',
            'support': r'(?:support|resistance|key levels?) (?:of |for )?(\w+)',
            'screener': r'(?:screen|find|search|show me) (?:stocks?|opportunities?)',
            'sector': r'(?:sector|industry) (?:performance|analysis|momentum)',
            'risk': r'(?:risk|volatility|safe) (?:of |for )?(\w+)?',
        }
    
    def process_query(self, query: str) -> Dict:
        """
        Process natural language query and return structured response
        """
        query = query.lower().strip()
        
        # Detect query type and extract parameters
        query_type, params = self._detect_query_type(query)
        
        # Route to appropriate handler
        if query_type == 'price':
            return self._handle_price_query(params)
        elif query_type == 'compare':
            return self._handle_compare_query(params)
        elif query_type == 'best':
            return self._handle_best_stocks_query(params)
        elif query_type == 'buy':
            return self._handle_buy_signal_query(params)
        elif query_type == 'sell':
            return self._handle_sell_signal_query(params)
        elif query_type == 'analysis':
            return self._handle_analysis_query(params)
        elif query_type == 'fundamentals':
            return self._handle_fundamentals_query(params)
        elif query_type == 'technical':
            return self._handle_technical_query(params)
        elif query_type == 'volume':
            return self._handle_volume_query(params)
        elif query_type == 'trend':
            return self._handle_trend_query(params)
        elif query_type == 'support':
            return self._handle_support_query(params)
        elif query_type == 'screener':
            return self._handle_screener_query(params)
        elif query_type == 'sector':
            return self._handle_sector_query(params)
        elif query_type == 'risk':
            return self._handle_risk_query(params)
        else:
            return self._handle_general_query(query)
    
    def _detect_query_type(self, query: str) -> Tuple[str, Dict]:
        """
        Detect query type and extract parameters
        """
        for query_type, pattern in self.patterns.items():
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                params = {'symbols': list(match.groups())}
                return query_type, params
        
        return 'general', {'query': query}
    
    def _handle_price_query(self, params: Dict) -> Dict:
        """Handle price queries"""
        symbol = params['symbols'][0].upper() if params['symbols'][0] else None
        
        if not symbol:
            return {'type': 'error', 'message': 'Please specify a stock symbol'}
        
        data = self.fetcher.fetch_stock_data(symbol)
        
        if not data:
            return {'type': 'error', 'message': f'Unable to fetch data for {symbol}'}
        
        return {
            'type': 'price',
            'symbol': symbol,
            'price': data['price'],
            'change': data['change_pct'],
            'message': f"**{symbol}** is currently trading at **₹{data['price']:.2f}**, {data['change_pct']:+.2f}% from previous close."
        }
    
    def _handle_compare_query(self, params: Dict) -> Dict:
        """Handle comparison queries"""
        if len(params['symbols']) < 2:
            return {'type': 'error', 'message': 'Please specify two stocks to compare'}
        
        symbol1 = params['symbols'][0].upper()
        symbol2 = params['symbols'][1].upper()
        
        data1 = self.fetcher.fetch_stock_data(symbol1)
        data2 = self.fetcher.fetch_stock_data(symbol2)
        
        if not data1 or not data2:
            return {'type': 'error', 'message': 'Unable to fetch data for comparison'}
        
        comparison = {
            'symbol1': symbol1,
            'symbol2': symbol2,
            'data1': data1,
            'data2': data2,
            'winner': symbol1 if data1['confidence'] > data2['confidence'] else symbol2
        }
        
        message = f"""
### Comparison: {symbol1} vs {symbol2}

**{symbol1}:**
- Price: ₹{data1['price']:.2f} ({data1['change_pct']:+.2f}%)
- Signal: {data1['signal']} ({data1['confidence']}%)
- Structure: {data1['structure']}
- RSI: {data1['rsi']:.1f}

**{symbol2}:**
- Price: ₹{data2['price']:.2f} ({data2['change_pct']:+.2f}%)
- Signal: {data2['signal']} ({data2['confidence']}%)
- Structure: {data2['structure']}
- RSI: {data2['rsi']:.1f}

**Recommendation:** {comparison['winner']} shows stronger signals.
        """
        
        return {
            'type': 'comparison',
            'comparison': comparison,
            'message': message
        }
    
    def _handle_best_stocks_query(self, params: Dict) -> Dict:
        """Handle best stocks queries"""
        # Screen top stocks
        symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'WIPRO', 'SBIN', 'BHARTIARTL', 'ITC', 'HINDUNILVR']
        results = self.fetcher.fetch_multiple_stocks(symbols, max_workers=5)
        
        # Sort by confidence
        results.sort(key=lambda x: x['confidence'], reverse=True)
        top_5 = results[:5]
        
        message = "### 🏆 Top Stock Opportunities\n\n"
        for i, stock in enumerate(top_5, 1):
            message += f"{i}. **{stock['symbol']}** - ₹{stock['price']:.2f} ({stock['change_pct']:+.2f}%)\n"
            message += f"   - Signal: {stock['signal']} ({stock['confidence']}% confidence)\n"
            message += f"   - Structure: {stock['structure']}, RSI: {stock['rsi']:.1f}\n\n"
        
        return {
            'type': 'best_stocks',
            'stocks': top_5,
            'message': message
        }
    
    def _handle_buy_signal_query(self, params: Dict) -> Dict:
        """Handle buy signal queries"""
        symbol = params['symbols'][0].upper() if params['symbols'][0] else None
        
        if not symbol:
            return {'type': 'error', 'message': 'Please specify a stock symbol'}
        
        data = self.fetcher.fetch_stock_data(symbol)
        
        if not data:
            return {'type': 'error', 'message': f'Unable to fetch data for {symbol}'}
        
        recommendation = "✅ **BUY**" if data['signal'] == 'BUY' else "⚠️ **HOLD**" if data['signal'] == 'HOLD' else "❌ **SELL**"
        
        message = f"""
### {symbol} Buy Signal Analysis

**Current Status:** {recommendation}

**Price:** ₹{data['price']:.2f} ({data['change_pct']:+.2f}%)
**Confidence:** {data['confidence']}%
**Market Structure:** {data['structure']}
**Bias:** {data['bias']}
**RSI:** {data['rsi']:.1f}
**FVG Status:** {data['fvg_status']}

**Reasoning:**
- Structure is {data['structure']}
- RSI at {data['rsi']:.1f} ({"Overbought" if data['rsi'] > 70 else "Oversold" if data['rsi'] < 30 else "Neutral"})
- {data['active_fvgs']} active FVG zones
- Volume ratio: {data['volume_ratio']:.2f}x
        """
        
        return {
            'type': 'buy_signal',
            'symbol': symbol,
            'data': data,
            'message': message
        }
    
    def _handle_sell_signal_query(self, params: Dict) -> Dict:
        """Handle sell signal queries"""
        return self._handle_buy_signal_query(params)  # Same logic
    
    def _handle_analysis_query(self, params: Dict) -> Dict:
        """Handle comprehensive analysis queries"""
        symbol = params['symbols'][0].upper() if params['symbols'][0] else None
        
        if not symbol:
            return {'type': 'error', 'message': 'Please specify a stock symbol'}
        
        # Get comprehensive data
        market_data = self.fetcher.fetch_stock_data(symbol)
        fundamentals = self.fund_analyzer.analyze(symbol, "NSE")
        
        if not market_data:
            return {'type': 'error', 'message': f'Unable to fetch data for {symbol}'}
        
        message = f"""
### 📊 Comprehensive Analysis: {symbol}

**Technical Analysis:**
- Price: ₹{market_data['price']:.2f} ({market_data['change_pct']:+.2f}%)
- Signal: {market_data['signal']} ({market_data['confidence']}%)
- Structure: {market_data['structure']}
- RSI: {market_data['rsi']:.1f}
- Volume: {market_data['volume_ratio']:.2f}x average

**Smart Money Concepts:**
- Bias: {market_data['bias']}
- FVG Status: {market_data['fvg_status']}
- Order Blocks: {market_data['order_blocks']}

**Fundamental Analysis:**
- Market Cap: {self.fund_analyzer.format_market_cap(fundamentals.get('market_cap', 0))}
- P/E Ratio: {fundamentals.get('pe_ratio', 0):.2f}
- ROE: {fundamentals.get('roe', 0):.2f}%
- Quality Score: {fundamentals.get('overall_quality', 0):.1f}/100

**Overall Rating:** {fundamentals.get('investment_rating', 'N/A')}
        """
        
        return {
            'type': 'analysis',
            'symbol': symbol,
            'market_data': market_data,
            'fundamentals': fundamentals,
            'message': message
        }
    
    def _handle_fundamentals_query(self, params: Dict) -> Dict:
        """Handle fundamental analysis queries"""
        symbol = params['symbols'][0].upper() if params['symbols'][0] else None
        
        if not symbol:
            return {'type': 'error', 'message': 'Please specify a stock symbol'}
        
        fundamentals = self.fund_analyzer.analyze(symbol, "NSE")
        
        if fundamentals.get('error'):
            return {'type': 'error', 'message': f'Unable to fetch fundamentals for {symbol}'}
        
        message = f"""
### 💰 Fundamental Analysis: {symbol}

**Company:** {fundamentals['company_name']}
**Sector:** {fundamentals['sector']} | {fundamentals['industry']}

**Valuation:**
- Market Cap: {self.fund_analyzer.format_market_cap(fundamentals['market_cap'])}
- P/E Ratio: {fundamentals['pe_ratio']:.2f}
- P/B Ratio: {fundamentals['pb_ratio']:.2f}

**Profitability:**
- ROE: {fundamentals['roe']:.2f}%
- ROA: {fundamentals['roa']:.2f}%
- Profit Margin: {fundamentals['profit_margin']:.2f}%

**Growth:**
- Revenue Growth: {fundamentals['revenue_growth']:.2f}%
- Earnings Growth: {fundamentals['earnings_growth']:.2f}%

**Quality Score:** {fundamentals['overall_quality']:.1f}/100
**Investment Rating:** {fundamentals['investment_rating']}
        """
        
        return {
            'type': 'fundamentals',
            'symbol': symbol,
            'fundamentals': fundamentals,
            'message': message
        }
    
    def _handle_technical_query(self, params: Dict) -> Dict:
        """Handle technical analysis queries"""
        symbol = params['symbols'][0].upper() if params['symbols'][0] else None
        
        if not symbol:
            return {'type': 'error', 'message': 'Please specify a stock symbol'}
        
        data = self.fetcher.fetch_stock_data(symbol)
        
        if not data:
            return {'type': 'error', 'message': f'Unable to fetch data for {symbol}'}
        
        message = f"""
### 📈 Technical Analysis: {symbol}

**Price Action:**
- Current: ₹{data['price']:.2f}
- Change: {data['change_pct']:+.2f}%

**Indicators:**
- RSI: {data['rsi']:.1f} ({"Overbought" if data['rsi'] > 70 else "Oversold" if data['rsi'] < 30 else "Neutral"})
- Volume: {data['volume_ratio']:.2f}x average

**Smart Money Concepts:**
- Market Structure: {data['structure']}
- Bias: {data['bias']}
- FVG Status: {data['fvg_status']}
- Active Order Blocks: {data['order_blocks']}

**Signal:** {data['signal']} ({data['confidence']}% confidence)
        """
        
        return {
            'type': 'technical',
            'symbol': symbol,
            'data': data,
            'message': message
        }
    
    def _handle_volume_query(self, params: Dict) -> Dict:
        """Handle volume queries"""
        symbol = params['symbols'][0].upper() if params['symbols'][0] else None
        
        if not symbol:
            return {'type': 'error', 'message': 'Please specify a stock symbol'}
        
        data = self.fetcher.fetch_stock_data(symbol)
        
        if not data:
            return {'type': 'error', 'message': f'Unable to fetch data for {symbol}'}
        
        volume_status = "High" if data['volume_ratio'] > 1.5 else "Normal" if data['volume_ratio'] > 0.8 else "Low"
        
        message = f"""
### 📊 Volume Analysis: {symbol}

**Current Volume:** {data['volume']:,.0f}
**Volume Ratio:** {data['volume_ratio']:.2f}x average
**Status:** {volume_status}

{"⚡ **Significant volume spike detected!**" if data['volume_ratio'] > 2 else ""}
        """
        
        return {
            'type': 'volume',
            'symbol': symbol,
            'data': data,
            'message': message
        }
    
    def _handle_trend_query(self, params: Dict) -> Dict:
        """Handle trend queries"""
        symbol = params['symbols'][0].upper() if params['symbols'][0] else None
        
        if not symbol:
            return {'type': 'error', 'message': 'Please specify a stock symbol'}
        
        data = self.fetcher.fetch_stock_data(symbol)
        
        if not data:
            return {'type': 'error', 'message': f'Unable to fetch data for {symbol}'}
        
        trend_emoji = "📈" if data['structure'] == 'Bullish' else "📉" if data['structure'] == 'Bearish' else "➡️"
        
        message = f"""
### {trend_emoji} Trend Analysis: {symbol}

**Market Structure:** {data['structure']}
**Bias:** {data['bias']}
**Momentum:** {data['change_pct']:+.2f}%

**Trend Strength:** {"Strong" if abs(data['change_pct']) > 2 else "Moderate" if abs(data['change_pct']) > 1 else "Weak"}
        """
        
        return {
            'type': 'trend',
            'symbol': symbol,
            'data': data,
            'message': message
        }
    
    def _handle_support_query(self, params: Dict) -> Dict:
        """Handle support/resistance queries"""
        symbol = params['symbols'][0].upper() if params['symbols'][0] else None
        
        if not symbol:
            return {'type': 'error', 'message': 'Please specify a stock symbol'}
        
        data = self.fetcher.fetch_stock_data(symbol)
        
        if not data:
            return {'type': 'error', 'message': f'Unable to fetch data for {symbol}'}
        
        message = f"""
### 🎯 Key Levels: {symbol}

**Current Price:** ₹{data['price']:.2f}

**FVG Zones:** {data['fvg_status']}
**Order Blocks:** {data['order_blocks']} active

*For detailed support/resistance levels, please check the Stock Deep Dive tab.*
        """
        
        return {
            'type': 'support',
            'symbol': symbol,
            'data': data,
            'message': message
        }
    
    def _handle_screener_query(self, params: Dict) -> Dict:
        """Handle screener queries"""
        return self._handle_best_stocks_query(params)
    
    def _handle_sector_query(self, params: Dict) -> Dict:
        """Handle sector queries"""
        message = """
### 🔥 Sector Performance

*For detailed sector analysis, please check the Market Dashboard.*

Top performing sectors are calculated based on:
- Average price momentum
- Number of bullish signals
- Active FVG zones
- Overall market structure
        """
        
        return {
            'type': 'sector',
            'message': message
        }
    
    def _handle_risk_query(self, params: Dict) -> Dict:
        """Handle risk queries"""
        symbol = params['symbols'][0].upper() if params['symbols'][0] else None
        
        if symbol:
            data = self.fetcher.fetch_stock_data(symbol)
            
            if data:
                risk_level = "High" if data['rsi'] > 70 or data['rsi'] < 30 else "Medium" if abs(data['change_pct']) > 2 else "Low"
                
                message = f"""
### ⚠️ Risk Assessment: {symbol}

**Risk Level:** {risk_level}
**RSI:** {data['rsi']:.1f}
**Volatility:** {abs(data['change_pct']):.2f}%

*For detailed risk metrics, please check the Stock Deep Dive > Risk tab.*
                """
            else:
                message = f"Unable to fetch risk data for {symbol}"
        else:
            message = "Please specify a stock symbol for risk assessment."
        
        return {
            'type': 'risk',
            'message': message
        }
    
    def _handle_general_query(self, query: str) -> Dict:
        """Handle general queries"""
        message = """
### 🤔 I can help you with:

- **Price queries:** "What is the price of RELIANCE?"
- **Comparisons:** "Compare TCS and INFY"
- **Best stocks:** "Show me best stocks"
- **Buy/Sell signals:** "Should I buy HDFCBANK?"
- **Analysis:** "Analyze WIPRO"
- **Fundamentals:** "Fundamentals of ICICIBANK"
- **Technical:** "Technical analysis of SBIN"
- **Volume:** "Volume of BHARTIARTL"
- **Trend:** "Trend of ITC"
- **Support/Resistance:** "Support levels of HINDUNILVR"

Try asking a specific question about a stock!
        """
        
        return {
            'type': 'help',
            'message': message
        }


if __name__ == "__main__":
    # Test NLP query handler
    handler = NLPQueryHandler()
    
    test_queries = [
        "What is the price of RELIANCE?",
        "Should I buy TCS?",
        "Compare INFY and WIPRO",
        "Show me best stocks",
        "Analyze HDFCBANK"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        result = handler.process_query(query)
        print(result['message'])
